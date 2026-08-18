<a id="relist-and-the-threshold-it-checks"></a>
# The one loop in the kubelet that fits in your head, and the deadline it holds itself to

**Claim** — `relist` is a single periodic loop that diffs the runtime's whole pod list against its own last snapshot, and the health check every operator has met is nothing more than "how long since that loop last finished" — a number you can read live from the node's own metrics and compare against the constant in the source.

**Rests on** — [the CRI call sequence](02-one-pod-is-how-many-cri-calls.md): relist is the consumer of `ListPodSandbox`/`ListContainers`, so the calls you counted starting one pod are the calls this loop makes about *every* pod, forever.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued. Reading happens on [`forge`](../../strands/lab-topologies.md#build-guest); the measurement comes from the worker's kubelet.

**Read** — the doc before the code, per [Area 7's rule](../../strands/source-reading.md#area-7-kubelet):

1. `~/src/design-proposals-archive/node/pod-lifecycle-event-generator.md` (item 4). Answer [module 6.1's PLEG question](../../phases/06-kubelet-node.md#m6-1): what did per-pod polling cost, and what does relist emit instead of a per-pod status?
2. `pkg/kubelet/pleg/pleg.go` (2.7 KB) — the interface, four event types, one channel. Read it whole; it is the frame.
3. `pkg/kubelet/pleg/generic.go` (⭐, 20.8 KB) — `Start`, `relist`, `Healthy`, and the `podRecords` cache. Three questions to answer with `file:line`:
   - which two constants set the relist **period** and the health **threshold**, and what is the ratio between them?
   - where does the loop decide that a container transition is worth emitting an event, and what happens to a container that changed twice between two relists?
   - what does `Healthy()` actually compare, and against which timestamp field?

**Do** — measure the same numbers from the running node rather than trusting the constants:

```sh
kubectl get --raw /api/v1/nodes/pair-worker/proxy/metrics | grep -E '^kubelet_pleg' 
```

Then, with a churn generator running, take the measurement again and compare:

```sh
kubectl create ns pleg-lab
kubectl -n pleg-lab create deployment churn --image=registry.k8s.io/pause:3.10 --replicas=12
kubectl -n pleg-lab scale deployment churn --replicas=0
kubectl -n pleg-lab scale deployment churn --replicas=12
kubectl get --raw /api/v1/nodes/pair-worker/proxy/metrics | grep -E 'kubelet_pleg_relist_duration_seconds_(sum|count)|kubelet_pleg_relist_interval'
```

Substitute your worker's real node name from `kubectl get nodes` for `pair-worker`.

**Observe** — `relist_duration_seconds_sum / relist_duration_seconds_count` before and after the churn, and `kubelet_pleg_last_seen_seconds` in relation to the clock.

**Expect** — a mean relist duration in the low milliseconds on an idle two-node lab, rising by a visible multiple during the scale-up, and a health threshold that is **two orders of magnitude larger** than either the period or the duration you measured. That ratio is the finding: the check is not a latency SLO, it is a liveness test for a loop that has stopped entirely, which is why `PLEG is not healthy` almost never means "slow" and almost always means "the runtime is not answering".

`kubelet_pleg_last_seen_seconds` should track within one period of now. Watch it once with `watch -n1` and the loop becomes a thing you have seen rather than read.

**Write down** — the phase's [6.1 write-down](../../phases/06-kubelet-node.md#checklist): the relist loop in one paragraph, with the `generic.go:line` of the health threshold, plus the measured mean duration and the ratio between it and that threshold. [The next exercise](04-pleg-is-not-healthy.md) makes the ratio matter.

**Footprint note** — twelve `pause` pods are a few MB each and are the cheapest churn available; the reason to use `pause` and not `nginx` is that this exercise measures the *kubelet's* loop, and 12 real workloads on a 2048MB worker would measure memory pressure instead. Keep the pattern for the rest of the phase: `pause` unless the exercise is about memory.

**Teardown** — `kubectl delete ns pleg-lab`. **The topology stays.**
