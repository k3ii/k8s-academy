<a id="the-diff-is-the-easy-half"></a>
# `manageReplicas`: the subtraction, and the two policies wrapped around it

**Claim** — the desired-minus-actual arithmetic in `replica_set.go` is four lines. The controller around it is two policies you can predict before running anything: **creates go out in doubling batches, and deletes are ranked rather than arbitrary.** You can state both from source, predict which pods a scale-down kills, and be right.

**Rests on** — [module 4.4's](../../phases/04-controllers.md#m4-4) `replica_set.go` reading question, and [your own `syncHandler`](15-the-hand-wired-loop.md), which currently has the subtraction and neither policy.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Do**

1. Read the three functions and answer from them, in writing:

   ```sh
   cd ~/src/kubernetes
   git grep -n 'func (rsc \*ReplicaSetController) manageReplicas' -A 40 -- pkg/controller/replicaset/replica_set.go
   git grep -n 'slowStartBatch\|SlowStartInitialBatchSize' -- pkg/controller/replicaset/replica_set.go
   git grep -n 'getPodsToDelete\|ActivePodsWithRanks\|func (s ActivePods) Less' -- pkg/controller/replicaset/ pkg/controller/controller_utils.go
   ```

   - What is the batch sequence for a create of 20, and **why is it batched at all** — what failure is it protecting against?
   - List the tie-breaks in the delete ranking, in order, from the comparison function.

2. Predict, then measure the create side:

   ```sh
   kubectl -n academy-lab create deployment burst --image=registry.k8s.io/pause:3.10 --replicas=20
   kubectl -n academy-lab get pods -l app=burst \
     -o custom-columns=NAME:.metadata.name,T:.metadata.creationTimestamp --sort-by=.metadata.creationTimestamp
   ```

3. Predict, then measure the delete side. Build a set of pods that differ in the ways the ranking cares about — some unschedulable, some newer — then scale down and name the victims *before* you look:

   ```sh
   kubectl -n academy-lab scale deployment burst --replicas=25
   kubectl -n academy-lab patch deployment burst --type=json \
     -p '[{"op":"add","path":"/spec/template/spec/nodeSelector","value":{"disktype":"nonexistent"}}]'
   # some pods now Pending on a node that cannot exist
   kubectl -n academy-lab scale deployment burst --replicas=5
   ```

**Observe** — the creation timestamps grouped into batches, and which pods survive the scale-down.

**Expect** — creation timestamps cluster: one, then two, then four, and so on, each batch waiting for the previous to be accepted. The reason is worth writing down in full because it recurs: **a controller that fires 20 creates at an API server that will reject all 20 has wasted 20 requests and will do it again on the next reconcile.** Batching turns a quota rejection or an admission webhook denial into one wasted request instead of `n`, and the failure of the first batch short-circuits the rest.

The scale-down kills the pods you can rank without asking any node anything: unassigned before assigned, `Pending` before `Running`, not-ready before ready, and newer before older among equals. **Every tie-break is computable from objects the controller already has in its cache**, which is the constraint that shaped the list — a ranking needing a live query would put a network call inside a reconcile that must be cheap.

Now turn it on your own operator: your children are ConfigMaps and cannot be pending, unready or newer in any meaningful sense, so **neither policy applies to you, and that is a defensible answer rather than an omission**. Write the sentence that says so. A controller whose children are pods needs both; one whose children are configuration needs neither, and deciding which of those you are is the design question this exercise asks.

**Write down** — the batch sequence with its rationale, the ordered tie-break list, your predicted-versus-actual victims, and the one-sentence verdict on your own operator.

**Footprint note** — 25 `pause` pods on the [`pair`](../../strands/lab-topologies.md#pair) worker, at a few MB each; they exist for minutes and several are deliberately `Pending`, which costs nothing at all. Delete the Deployment before moving on — [the next exercise](22-expectations-or-over-create.md) counts objects and a stray ReplicaSet makes the count ambiguous.

**Teardown**

```sh
kubectl -n academy-lab delete deployment burst
```

**The topology stays.**
