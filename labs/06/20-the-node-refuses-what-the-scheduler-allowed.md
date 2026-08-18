<a id="the-node-refuses-what-the-scheduler-allowed"></a>
# Bypass the scheduler entirely and meet the node's own admission check

**Claim** — the scheduler's decision is not the last word: the kubelet runs its own admission over every pod assigned to it, against the node's *current* allocatable, and it can refuse a pod the scheduler would have accepted. The failure has its own reason string and its own code path, and neither of them is the scheduler's.

**Rests on** — [the allocatable arithmetic](17-where-the-ram-went.md), which is the number the check compares against, and [P5's scheduling](../../phases/05-scheduler.md#m5-3), which is the decision being bypassed.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued, with the worker's aggressive `evictionHard` still in place — it is what makes allocatable small enough to hit deliberately.

**Read** — `pkg/kubelet/lifecycle/predicate.go` (item 17): which predicates run at the node, what reason each produces, and — the question worth the read — **why does the same check exist in two places?** Then find the caller in `kubelet.go`'s sync loop, so you can name the point in a pod's life at which the node gets its veto.

**Do**

1. Read the current allocatable, and pick a request just above it:

   ```sh
   kubectl get node pair-worker -o jsonpath='{.status.allocatable.memory}{"\n"}'
   ```

2. Assign a pod past the scheduler with `nodeName` — the scheduler never sees it:

   ```sh
   kubectl create ns admit
   kubectl -n admit apply -f - <<'EOF2'
   apiVersion: v1
   kind: Pod
   metadata: {name: too-big}
   spec:
     nodeName: pair-worker
     containers:
     - name: c
       image: registry.k8s.io/pause:3.10
       resources: {requests: {memory: 4Gi}}
   EOF2
   ```

3. Read the refusal from three places:

   ```sh
   kubectl -n admit get pod too-big -o jsonpath='{.status.phase}{"\t"}{.status.reason}{"\t"}{.status.message}{"\n"}'
   kubectl -n admit get events --field-selector involvedObject.name=too-big
   ssh zain@10.10.10.131 'sudo journalctl -u kubelet --since "-2 min" | grep -i -e admit -e "predicate"'
   ```

4. **The control:** submit the identical pod *without* `nodeName` and see what a different component does with the same impossible request:

   ```sh
   kubectl -n admit run too-big-2 --image=registry.k8s.io/pause:3.10 --restart=Never \
     --overrides='{"spec":{"containers":[{"name":"c","image":"registry.k8s.io/pause:3.10","resources":{"requests":{"memory":"4Gi"}}}]}}'
   kubectl -n admit get pod too-big-2 -o jsonpath='{.status.phase}{"\t"}{.status.conditions[0].reason}{"\t"}{.status.conditions[0].message}{"\n"}'
   ```

**Expect** — the `nodeName` pod to reach `Failed` with `status.reason: OutOfmemory` and a message naming the node's capacity, produced by the kubelet. The scheduled pod stays **`Pending`** forever with an `Unschedulable` condition and a message naming how many nodes did not fit, produced by the scheduler.

Two rejections of the same request, in different phases, with different reasons, from different components — and only one of them leaves a corpse. That difference is the exercise: a `Pending` pod is a cluster that has not decided, a `Failed`/`OutOfmemory` pod is a node that has decided against you, and the two are diagnosed in completely different places.

Expect the kubelet's refusal to be immediate — no image pull, no sandbox, no container. Confirm on the node with `sudo crictl pods | grep too-big` returning nothing: admission runs before the runtime is asked for anything, which is the whole reason it is worth having twice.

**Write down** — the two reasons with the code that produced each (`predicate.go:line` for one, [P5's plugin](../../phases/05-scheduler.md#m5-3) for the other), and one sentence on when the node's copy is the *only* one that can be right — the race the doubled check exists for.

**Footprint note** — nothing runs; both pods are refused. Zero cost, which is a pleasant property for an exercise about resource limits.

**Teardown** — delete the namespace, then **restore the worker's kubelet to its original configuration** — the aggressive threshold has done its work and every remaining exercise wants a normal node:

```sh
kubectl delete ns admit
ssh zain@10.10.10.131 'sudo cp /var/lib/kubelet/config.yaml.orig /var/lib/kubelet/config.yaml && sudo systemctl restart kubelet'
sleep 20; kubectl get node pair-worker -o jsonpath='{.status.allocatable.memory}{"\n"}'
```

That last line should show allocatable back up by the difference you computed in [exercise 17](17-where-the-ram-went.md) — the arithmetic, confirmed a third time and in the other direction. **The topology stays.**
