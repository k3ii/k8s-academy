<a id="the-uid-is-the-edge"></a>
# The garbage collector matches on UID, and it checks before it deletes

**Claim** — the edge in the garbage collector's graph is the owner's **UID**, not its name; a child whose owner reference names a live object with the wrong UID is deleted within seconds. And the collector does not trust its own cache for that decision — it goes and asks the API server first, which is the same rule [you were taught by breaking it](12-4c4-act-before-the-cache-is-synced.md), followed by the tree.

**Rests on** — [module 4.4's](../../phases/04-controllers.md#m4-4) `garbagecollector/graph.go` reading question, and [the owner-reference failures](23-one-owner-may-be-the-controller.md).

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Do**

1. Read the node identity and the check, and answer both:

   ```sh
   cd ~/src/kubernetes
   git grep -n 'type node struct\|identity\|owners \[\]metav1.OwnerReference' -- pkg/controller/garbagecollector/graph.go
   git grep -n 'virtual\|attemptToDelete\|classifyReferences\|isDangling' -- pkg/controller/garbagecollector/garbagecollector.go
   ```

   - **What three fields identify a node**, and which one is the edge?
   - When the collector meets a dependent whose owner it has never seen, what does it do *before* deciding the reference is dangling? Name the call.

2. Predict, then run. Take a live child of `alpha` and corrupt only the UID in its owner reference — same name, same kind, same API version:

   ```sh
   kubectl -n academy-lab get configmap alpha-voice-1 -o jsonpath='{.metadata.ownerReferences[0].uid}{"\n"}'
   kubectl -n academy-lab get ensemble alpha -o jsonpath='{.metadata.uid}{"\n"}'
   # patch the ConfigMap's ownerReference uid to a made-up but well-formed UUID
   kubectl -n academy-lab get configmap alpha-voice-1 -w
   ```

3. Predict, then run the second case. Delete `alpha` with `--cascade=orphan`, then recreate an `Ensemble` with the same name, and look at what the orphans' owner references say and whether the new object claims them.

**Observe** — how long `alpha-voice-1` survives in step 2, and whether the operator recreates it. In step 3, whether anything at all connects the new `alpha` to the old children.

**Expect** — step 2's ConfigMap is deleted, promptly, by a component you did not ask. A live `Ensemble` named `alpha` exists the entire time; **the name was never what mattered.** Your operator then recreates the child on its next reconcile, which makes the whole thing look like a blip — run it with the operator stopped once, so you can see the deletion without the repair.

Step 3 recreates nothing. The orphans have had their owner references stripped, and even if they had not, the new object's UID is different. **A name is reusable and a UID is not, which is exactly why the graph is built on the one that cannot be recycled** — otherwise deleting and recreating a parent would silently transfer custody of objects the new parent never asked for.

The pre-delete check from step 1 is the detail to keep. The collector holds a graph built from watches on every resource in the cluster, and it still refuses to delete a dependent on the strength of an absence in that graph — it does a live read first, because an object missing from a cache and an object missing from the cluster are different claims. That is the same rule as [4.C4](12-4c4-act-before-the-cache-is-synced.md), applied by the component with the most destructive power in the control plane, and it is the strongest available argument for applying it in your own reconcile.

**Write down** — the three identity fields with the edge named, the live-read call site with its `file:line`, and one sentence on why re-using a name does not re-adopt.

**Footprint note** — nothing new.

**Teardown** — restart the operator if you stopped it, confirm `alpha` has its three children and one registry key, and delete any orphans from step 3. **The topology stays** — [leader election](28-two-replicas-one-lease.md) needs the operator running.
