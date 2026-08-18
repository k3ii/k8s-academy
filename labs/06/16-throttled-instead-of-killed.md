<a id="throttled-instead-of-killed"></a>
# Write one number into a cgroup by hand and turn an OOMKill into a slowdown

**Claim** — cgroup v2 has a throttle for memory as well as a wall, and the difference is one file: `memory.high` makes a process stall under reclaim pressure while `memory.max` has it killed. Kubernetes sets only the second by default, and you can demonstrate what the first would do before deciding whether you want the feature gate that sets it for you.

**Rests on** — [the cgroup tree](15-the-cgroup-tree-under-one-pod.md); you need the pod's directory path and the `cgroups` namespace still up.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued. Worker `.131`.

**Read** — KEP-2570, Memory QoS with cgroups v2, for two answers: what formula does it use to derive `memory.high` from a pod's requests and limits, and what is the argument for a *throttle* over a *kill* for a workload that briefly overshoots? Then find whether this node would do it for you:

```sh
grep -rn 'MemoryQoS' ~/src/kubernetes/pkg/features/kube_features.go
kubectl get --raw "/api/v1/nodes/pair-worker/proxy/configz" | jq '.kubeletconfig.featureGates'
```

**Do**

1. Replace the Burstable pod from the previous exercise with one that actually allocates, keeping the same 128Mi limit:

   ```sh
   kubectl -n cgroups delete pod b --now
   kubectl -n cgroups apply -f - <<'EOF2'
   apiVersion: v1
   kind: Pod
   metadata: {name: b}
   spec:
     nodeName: pair-worker
     containers:
     - name: c
       image: busybox:1.36
       command: ["sh","-c","i=0; while true; do dd if=/dev/zero of=/fill/$i bs=1M count=8 2>/dev/null; i=$((i+1)); sleep 2; done"]
       volumeMounts: [{name: fill, mountPath: /fill}]
       resources: {requests: {memory: 32Mi}, limits: {memory: 128Mi}}
     volumes: [{name: fill, emptyDir: {medium: Memory}}]
   EOF2
   ```

2. Find its cgroup directory (the method is [exercise 15's](15-the-cgroup-tree-under-one-pod.md)), then set the throttle by hand, well under the limit:

   ```sh
   ssh zain@10.10.10.131 'CG=<the pod cgroup path>; \
     echo 64M | sudo tee $CG/memory.high; \
     while :; do printf "cur=%-10s high=%-10s max=%-10s\n" \
       "$(cat $CG/memory.current)" "$(cat $CG/memory.high)" "$(cat $CG/memory.max)"; \
       cat $CG/memory.events | tr "\n" " "; echo; sleep 2; done'
   ```

3. Watch `kubectl -n cgroups get pod b -w` at the same time.

4. Now remove the throttle and let it run into the wall:

   ```sh
   ssh zain@10.10.10.131 'CG=<the pod cgroup path>; echo max | sudo tee $CG/memory.high'
   ```

**Observe** — the `memory.events` counters specifically, one line at a time. There are separate counters for `high`, `max`, `oom` and `oom_kill`, and the whole exercise is visible in which of them moves.

**Expect** — with `memory.high` set: `memory.current` hovering at or just above the throttle, the `high` counter climbing steadily, the `dd` loop visibly slower, and **the pod still `Running` with `restartCount` at zero**. The process is being made to wait for reclaim on every allocation — a workload that is slow rather than dead, which for a cache or a JVM heap is usually the outcome you would have chosen.

With `memory.high` back to `max`: `memory.current` climbs to the limit, `max` and `oom_kill` move, the container restarts. Same pod, same spec, same limit — the difference is one file that Kubernetes did not write.

Expect the kubelet to eventually restore `memory.high` to its own idea of the value when it next syncs the pod's cgroup. If it does, note when: it is the clearest demonstration in the phase that these directories are **reconciled state**, not configuration you own — and it is [P4's level-triggered loop](../../phases/04-controllers.md) reaching all the way down to a file in `/sys`.

**Write down** — the `memory.events` deltas for both halves, the observed behaviour of each, the KEP's formula, and whether the gate is on for this node. Add one sentence on when you would want the throttle and when you would not.

**Footprint note** — capped at 128Mi by the pod's own limit; nothing reaches the node. This is deliberately the *contained* counterpart to [exercise 14](14-evicted-or-oomkilled.md).

**Teardown** — `kubectl -n cgroups delete pod b --now`. **Keep the `cgroups` namespace** for [exercise 18](18-cpu-max-and-the-throttle-counter.md). **The topology stays.**
