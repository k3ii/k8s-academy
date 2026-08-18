<a id="6c3-who-killed-the-pod"></a>
# 6.C3 — Two OOM kills that look the same from `kubectl` and were done by different machines

**Claim** — a cgroup OOM kill and an `OOMKilled` container status are **not the same event**: the kernel kills the fattest process in the cgroup, and the pod is only marked `OOMKilled` when that process happens to be the container's init. You can produce both on the same pod spec and tell them apart in under a minute, from `memory.events`, `dmesg` and the container's `lastState`.

**Rests on** — [Chaos Mesh](08-chaos-mesh-at-582mi.md) for the first kill and [the oom_score_adj values](07-oom-score-adj-from-the-formula.md) for the *why this victim* half. This is [drill 6.C3](../../phases/06-kubelet-node.md#chaos), and its method is the talk the phase cites.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued. Everything runs on the worker `.131`; keep a second shell open on it for `dmesg -w`.

**Setup**

```sh
kubectl create ns oomkill
kubectl -n oomkill apply -f - <<'EOF2'
apiVersion: v1
kind: Pod
metadata: {name: victim, labels: {app: victim}}
spec:
  nodeName: pair-worker
  containers:
  - name: c
    image: registry.k8s.io/pause:3.10
    resources: {requests: {memory: 64Mi}, limits: {memory: 128Mi}}
EOF2
```

Find its cgroup and watch the counter that will move:

```sh
ssh zain@10.10.10.131 'p=$(sudo crictl ps --name c --pod $(sudo crictl pods --name victim -q) -q); \
  pid=$(sudo crictl inspect $p | jq -r .info.pid); \
  cg=/sys/fs/cgroup$(awk -F: "{print \$3}" /proc/$pid/cgroup); \
  echo "$cg"; cat $cg/memory.max; cat $cg/memory.events'
```

**Do — kill one: the injector**

```sh
kubectl apply -f - <<'EOF2'
apiVersion: chaos-mesh.org/v1alpha1
kind: StressChaos
metadata: {name: oom-the-victim, namespace: oomkill}
spec:
  mode: one
  selector:
    namespaces: [oomkill]
    labelSelectors: {app: victim}
  stressors:
    memory: {workers: 1, size: 400MB}
  duration: 60s
EOF2
```

While it runs, on the worker: `sudo dmesg -w`, and re-read `memory.events` and `memory.current`. From the cluster: `kubectl -n oomkill get pod victim -o jsonpath='{.status.containerStatuses[0].restartCount}{"\t"}{.status.containerStatuses[0].state}{"\n"}'`.

**Do — kill two: the container's own process**

```sh
kubectl -n oomkill delete pod victim --now
kubectl -n oomkill apply -f - <<'EOF2'
apiVersion: v1
kind: Pod
metadata: {name: victim, labels: {app: victim}}
spec:
  nodeName: pair-worker
  containers:
  - name: c
    image: busybox:1.36
    command: ["sh","-c","tail /dev/zero"]
    resources: {requests: {memory: 64Mi}, limits: {memory: 128Mi}}
EOF2
kubectl -n oomkill get pod victim -w
```

Then the forensics, in the order the talk's method runs them:

```sh
kubectl -n oomkill get pod victim -o jsonpath='{.status.containerStatuses[0].lastState.terminated}{"\n"}' | jq
kubectl -n oomkill get events --field-selector involvedObject.name=victim
ssh zain@10.10.10.131 'sudo journalctl -u kubelet --since "-3 min" | grep -i -e oom -e killing'
ssh zain@10.10.10.131 'sudo dmesg | tail -40'
```

**Observe** — in the `dmesg` OOM report, the task table that precedes the kill line. It lists every task in the cgroup with its `oom_score_adj` and its RSS. Map each row back to the value you computed in [exercise 7](07-oom-score-adj-from-the-formula.md), and read the kernel's chosen victim as the arithmetic it is: badness is RSS scaled by the adjustment, so the class order the phase claims is a *consequence* of the constants, not a rule written down anywhere in the kernel. The kernel has never heard of QoS.

**Expect** — from kill one: `memory.events` `oom_kill` increments, `dmesg` names the pod's cgroup path, **and `kubectl` shows the pod still `Running` with `restartCount` unchanged and no event at all.** The kernel killed `stress-ng`, which was the fattest task in the cgroup, and the `pause` process it was sharing the cgroup with never noticed. This is the drill's finding and it is the reason "the pod was OOMKilled" is a claim to check rather than to accept: *a container can absorb a fatal OOM kill and report nothing*.

From kill two: `lastState.terminated.reason: OOMKilled`, `exitCode: 137`, `restartCount` climbing, a `BackOff` event once the restarts back off — and in `dmesg`, the same kind of report naming the same cgroup. **Identical kernel event, different `kubectl` output**, because this time the dead task was the container's PID 1 and the runtime reported its exit status.

Expect the kubelet's log to contain no decision in either case — no ranking, no threshold, no grace period. Nothing here is an eviction, and the absence is the evidence: [when the kubelet does the killing](14-evicted-or-oomkilled.md) it says so at length beforehand.

**Write down** — the two-column comparison (kernel signal, cgroup counter, `kubectl` state, restart count, event, who chose the victim), the `dmesg` task table with the adjustments mapped to the QoS classes, and one sentence naming the killer in each case. [The phase's chaos table](../../phases/06-kubelet-node.md#chaos) asks for exactly this pair.

**Footprint note — the pressure is contained and deliberately small.** `StressChaos` joins the target's existing cgroup, so 400MB of stressor is capped at the pod's own 128Mi limit and never reaches the node; `tail /dev/zero` is bounded by the same limit. **This drill cannot cause node-level pressure and is not meant to** — that is [exercise 14](14-evicted-or-oomkilled.md), which is sized for it on purpose.

**Teardown**

```sh
kubectl -n oomkill delete stresschaos oom-the-victim --ignore-not-found
kubectl delete ns oomkill
```

Confirm no `stress-ng` survived on the worker: `ssh zain@10.10.10.131 'pgrep -a stress-ng'` should print nothing. **The topology stays**, and so does Chaos Mesh.
