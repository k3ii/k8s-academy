<a id="one-owner-may-be-the-controller"></a>
# Three things an owner reference will not do for you

**Claim** — an owner reference is checked by three different components with three different rules, and you can produce a distinct, visible failure from each: the API server refuses two controlling owners, the garbage collector refuses a cross-namespace parent and *says so in an event*, and neither of them will adopt an existing object on your behalf. The third is your controller's job and nobody else's.

**Rests on** — [module 4.4's](../../phases/04-controllers.md#m4-4) `controller-ref.md` reading question, and [the registry entry](14-generate-the-clientset.md) whose whole existence is justified by the second failure below.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Do**

1. **Two controllers.** Take one of `alpha`'s children and add a second owner reference with `controller: true`, pointing at anything:

   ```sh
   kubectl -n academy-lab get configmap alpha-voice-1 -o yaml > /tmp/cm.yaml
   # add a second ownerReference with controller: true, then:
   kubectl -n academy-lab replace -f /tmp/cm.yaml
   ```

2. **A parent in another namespace.** Create a ConfigMap in `academy-registry` whose only owner reference points at `alpha`, which lives in `academy-lab`:

   ```sh
   kubectl -n academy-registry create configmap stray --from-literal=x=1
   # patch in an ownerReference to alpha, with its real UID, then:
   kubectl -n academy-lab delete ensemble alpha
   kubectl -n academy-registry get configmap stray
   kubectl -n academy-registry get events --field-selector involvedObject.name=stray
   ```

3. **An object that should have been adopted.** Recreate `alpha`, but first create `alpha-voice-1` yourself, by hand, with no owner reference at all. Start the operator and watch.

**Observe** — the API server's rejection message in step 1, the event and the survival in step 2, and the operator's behaviour in step 3.

**Expect** — step 1 is refused by validation, naming the field. The rule is not a convention the controllers agree to honour; it is enforced where objects are written, which is why "who owns this" always has one answer.

Step 2 leaves `stray` alive after its parent is gone, and the garbage collector emits an event saying the reference is invalid because it crosses a namespace. **This is the fact your finalizer exists to work around**, and it is worth having seen rather than accepted: the GC does not silently skip the object and it does not delete it either — it complains, forever, into an event stream nobody reads. A design that relies on cross-namespace ownership does not fail loudly; it accumulates.

Step 3 is the one where your operator's behaviour is a choice. With deterministic names it will try to create, get `AlreadyExists`, and — depending on what you wrote in [exercise 15](15-the-hand-wired-loop.md) — either error forever or treat the existing object as satisfying the desired state without touching it. Neither is adoption. **Adoption means taking ownership of an object you did not create**, and it is a deliberate act: check that the object has no controlling owner, then patch one in. `replica_set.go` does this, and the reason is that a ReplicaSet must be able to take over pods from the Deployment revision before it.

Decide what your operator does, implement it, and defend it. Both answers are defensible and they are not the same operator: **an adopting controller can absorb objects it did not make, which is powerful and is also how one controller ends up fighting another.**

**Write down** — the three failure messages verbatim, and your adoption decision with its argument. The cross-namespace event is the one to keep for [the finalizer drill](25-4c2-a-finalizer-that-never-completes.md), which breaks the code that exists because of it.

**Footprint note** — nothing new.

**Teardown**

```sh
kubectl -n academy-registry delete configmap stray
```

Recreate `alpha` with `voices: 3` if you deleted it, and confirm the operator rebuilds its children and its registry key. **The topology stays.**
