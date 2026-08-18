<a id="evicted-or-oomkilled"></a>
# The same node, the same pod spec, two different killers — decided by allocation speed

**Claim** — whether a pod is evicted by the kubelet or killed by the kernel is not a property of the pod, the QoS class or the threshold: it is a race between how fast the memory is taken and how fast the eviction manager can act. Change only the allocation rate and you change the killer.

**Rests on** — [exercise 12](12-an-eviction-you-configured.md) for the configured threshold, [exercise 13](13-faster-than-housekeeping.md) for the reaction latency you measured, and [drill 6.C3](09-6c3-who-killed-the-pod.md) for what a kernel kill looks like from the outside. **This is [objective 4](../../phases/06-kubelet-node.md#objectives)** and it is the phase's one exercise that is purely about telling two things apart.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued, worker only, with the aggressive `evictionHard` still in place.

**Setup** — keep the forensic commands from [6.C3](09-6c3-who-killed-the-pod.md) in a shell on the worker; you will run them against both outcomes.

**Do — run A, slow: give the kubelet time**

```sh
kubectl create ns killer
kubectl -n killer apply -f - <<'EOF2'
apiVersion: v1
kind: Pod
metadata: {name: slow, labels: {rate: slow}}
spec:
  nodeName: pair-worker
  containers:
  - name: c
    image: busybox:1.36
    command: ["sh","-c","i=0; while true; do dd if=/dev/zero of=/fill/$i bs=1M count=16 2>/dev/null; i=$((i+1)); sleep 5; done"]
    volumeMounts: [{name: fill, mountPath: /fill}]
  volumes: [{name: fill, emptyDir: {medium: Memory}}]
EOF2
```

**Do — run B, fast: do not**

```sh
kubectl -n killer delete pod slow --now
kubectl -n killer apply -f - <<'EOF2'
apiVersion: v1
kind: Pod
metadata: {name: fast, labels: {rate: fast}}
spec:
  nodeName: pair-worker
  containers:
  - name: c
    image: busybox:1.36
    command: ["sh","-c","i=0; while true; do dd if=/dev/zero of=/fill/$i bs=1M count=64 2>/dev/null; i=$((i+1)); done"]
    volumeMounts: [{name: fill, mountPath: /fill}]
  volumes: [{name: fill, emptyDir: {medium: Memory}}]
EOF2
```

For each run, answer the same six questions from evidence:

| Question | Where the answer is |
|---|---|
| Is the pod object still there? | `kubectl -n killer get pods` |
| What is `status.reason`? | `kubectl -n killer get pod <n> -o jsonpath='{.status.reason}'` |
| What is in `lastState.terminated`? | the same object's `containerStatuses` |
| Did `restartCount` move? | the same |
| Is there an `Evicted` event, and who is the source? | `kubectl -n killer get events` |
| Did the kernel log an OOM? | `ssh zain@10.10.10.131 'sudo dmesg | tail -30'` |

And the one that names the killer: `ssh zain@10.10.10.131 'sudo journalctl -u kubelet --since "-3 min" | grep -i -e eviction -e oom'`.

**Observe** — the kubelet log for run B specifically. It very likely contains an OOM *observation* — the kubelet watches for kernel kills and reports them — with no eviction decision anywhere. **Reporting a kill and performing one produce log lines that look alike and mean opposite things**; separating them is the skill this exercise exists to build.

**Expect** — run A: `Failed` / `Evicted`, pod object retained, no restart, a node condition that flipped, an eviction decision in the log, nothing in `dmesg`.

Run B: no `Evicted` reason, `lastState.terminated.reason: OOMKilled` with exit code 137 **or** a kernel OOM report naming a different victim entirely, `restartCount` moving, no eviction decision, and a `dmesg` report. If the kernel picked a *neighbour* rather than your hog, that is not a failed run — it is the badness arithmetic from [exercise 7](07-oom-score-adj-from-the-formula.md) doing its job on a node with no per-pod limit to contain the damage, and it is worth writing down as the strongest argument for setting limits you will meet in this phase.

Expect the kubelet itself to survive both. Check why, and get the number: `ssh zain@10.10.10.131 'cat /proc/$(pidof kubelet)/oom_score_adj'` — the node's most important process protects itself with the same one-integer mechanism your pods use.

**Write down** — the six-row comparison table for both runs, the deciding factor in one sentence, and the discrimination procedure itself: **given a dead pod and no context, the ordered checks that name the killer.** That procedure is [the checklist's 6.3 item](../../phases/06-kubelet-node.md#checklist) and it is what you will actually use at work.

**Footprint note — this is the phase's deliberate cascade and it is sized to produce one.** Run B takes memory faster than the manager can respond on a 2048MB node; that is the experiment, not an accident. It is contained to the worker guest: the control plane keeps the API server, so even a fully wedged worker leaves you a working `kubectl`. If the worker becomes unresponsive rather than recovering, `ssh hopper` and reset that guest alone — do **not** destroy the topology, which would cost a re-provision and lose the Chaos Mesh install from [exercise 8](08-chaos-mesh-at-582mi.md).

**Teardown**

```sh
kubectl delete ns killer
```

Confirm the node came back: `kubectl get node pair-worker -o jsonpath='{range .status.conditions[*]}{.type}={.status}{"\n"}{end}'` — all pressures `False` after the transition period. **Leave the kubelet configuration in place** for now. **The topology stays.**
