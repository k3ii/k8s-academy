<a id="the-line-that-writes-insufficient-cpu"></a>
# `Insufficient cpu` — the exact line that formats it, and what it counted

**Claim** — the message a learner sees on a `Pending` pod is produced by one `fmt` call in `noderesources/fit.go`, the number it compares against is **allocatable minus the requests of pods already assigned to the node**, and neither term is what most people assume: it is not the node's capacity, and it is not what the pods are actually using.

**Rests on** — [the three rejection strings](06-three-rejections-three-plugins.md), which established that events name plugins, and [`CycleState`](14-state-without-globals.md), which is where this plugin's precomputed half lives.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Do**

1. Produce the message, with a request that no node could satisfy:

   ```sh
   kubectl -n sched-lab run greedy --image=registry.k8s.io/pause:3.9 --restart=Never \
     --overrides='{"spec":{"containers":[{"name":"pause","image":"registry.k8s.io/pause:3.9","resources":{"requests":{"cpu":"8"}}}]}}'
   kubectl -n sched-lab describe pod greedy | sed -n '/Events/,$p'
   ```

2. Find the line that wrote it. `fit.go` is 37.8 KB, so do not read it front to back — [the area is explicit](../../strands/source-reading.md#area-3-scheduler) that this file is entered from a message:

   ```sh
   grep -n 'Insufficient' pkg/scheduler/framework/plugins/noderesources/fit.go
   ```

3. Read outward from that line until you have all three of: the function it is in, what supplies the "available" number, and what supplies the "requested" number. Then chase the available number to its source:

   ```sh
   grep -rn 'Allocatable\|NodeInfo{' pkg/scheduler/framework/types.go | head
   ```

   `types.go` is 64.3 KB and [reference-only by design](../../strands/source-reading.md#area-3-scheduler) — look up `NodeInfo` and its `Requested` and `Allocatable` fields, and get out.

4. Prove that "requested" is not "used". Put a pod on a node that requests a lot and uses nothing, then ask both the scheduler and the node:

   ```sh
   kubectl -n sched-lab run hoarder --image=registry.k8s.io/pause:3.9 \
     --overrides='{"spec":{"containers":[{"name":"pause","image":"registry.k8s.io/pause:3.9","resources":{"requests":{"cpu":"1500m"}}}]}}'
   kubectl describe node <worker-node> | sed -n '/Allocated resources/,/^Events/p'
   ssh zain@10.10.10.131 'uptime; cat /proc/loadavg'
   ```

5. Prove that "allocatable" is not "capacity", and find the gap:

   ```sh
   kubectl get node <worker-node> -o jsonpath='{.status.capacity}{"\n"}{.status.allocatable}{"\n"}'
   ssh zain@10.10.10.131 'sudo cat /var/lib/kubelet/config.yaml | grep -A4 -iE "reserved|evictionHard"'
   ```

6. Answer the module's question: which extension points does this one plugin register at, and what does each do? You have [the mapping](04-what-actually-runs-by-default.md); confirm it against the file and note what the `Score` half computes, because [module 5.6](34-placement-that-differs-measurably.md) will change exactly that.

**Observe** — the message from step 1 verbatim, the two numbers in step 5, and the node's actual load in step 4 while it is "full".

**Expect** — a node reported as having no CPU left while its load average is approximately zero. The scheduler is a bookkeeper of *promises*, and this is the single most consequential fact about it: it never looks at utilisation, and a cluster can be simultaneously 100% scheduled and 3% busy. Every capacity conversation in the rest of the curriculum starts here.

Expect `allocatable` to be smaller than `capacity` by the kubelet's reservations, and expect the gap to be visible in the kubelet config rather than anywhere in the scheduler. The scheduler never subtracts anything for the system; the node reports a number that already has.

Expect the `Insufficient` string to be assembled from the resource name, so the same line produces `Insufficient memory` and `Insufficient nvidia.com/gpu` without carrying a special case for either — which is why extended resources need no scheduler change at all.

**Write down** — the `file:line` of the format call, the definitions of both terms in your own words, and the capacity/allocatable numbers with the reservation that explains the gap.

**Footprint note** — two pause pods, one of which reserves 1.5 CPU on `pair`'s worker. Delete it in the teardown or the next module's pods will not fit and you will misread the reason. 7.5GB total.

**Teardown** — `kubectl -n sched-lab delete pod greedy hoarder --ignore-not-found`, then confirm the worker is empty of your reservations: `kubectl describe node <worker-node> | sed -n '/Allocated resources/,/^Events/p'`. **The topology stays.**
