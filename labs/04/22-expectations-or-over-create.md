<a id="expectations-or-over-create"></a>
# Make your own operator over-create, then name the two defences against it

**Claim** — a diff-driven reconcile that counts children in a cache it has just written to will create them twice, and you can produce that on demand. **There are exactly two defences and your operator is already using one of them by accident**: deterministic child names, or `ControllerExpectations`. You can say which one applies to which kind of controller and why ReplicaSet cannot use the first.

**Rests on** — [the read-your-own-write gap](12-4c4-act-before-the-cache-is-synced.md), which established that the cache does not contain your write yet, and [module 4.4's](../../phases/04-controllers.md#m4-4) `Expectations` reading question. This is [objective 5](../../phases/04-controllers.md#objectives).

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued, operator running as `go run` on [`forge`](../../strands/lab-topologies.md#build-guest).

**Do**

1. Add `--double-enqueue`: after a successful reconcile, re-add the key immediately rather than only on error. This is not a contrivance — **it is what a second event arriving during the first reconcile does**, which under load is the normal case rather than the exception.

2. Run with it, on an `Ensemble` with `voices: 4`. Count the ConfigMaps. Then change one line — children created with `GenerateName: "beta-voice-"` instead of `Name: fmt.Sprintf("beta-voice-%d", i)` — and run it again.

   ```sh
   kubectl -n academy-lab apply -f - <<'EOF'
   apiVersion: academy.k3ii.dev/v1alpha1
   kind: Ensemble
   metadata: {name: beta}
   spec: {voices: 4, registryNamespace: academy-registry}
   EOF
   kubectl -n academy-lab get configmaps | grep beta-voice | wc -l
   ```

3. Read what the tree does instead, and find the three places it has to appear:

   ```sh
   cd ~/src/kubernetes
   git grep -n 'type ControllerExpectations\|func (r \*ControllerExpectations) SatisfiedExpectations\|ExpectCreations\|CreationObserved' \
     -- pkg/controller/controller_utils.go
   git grep -n 'expectations\.' -- pkg/controller/replicaset/replica_set.go
   ```

   Answer: **where is the expectation set, where is it satisfied, and what happens on the reconcile that finds it unsatisfied?** The third is the interesting one — it does not block, and it does not retry immediately.

4. Reproduce the same pressure against a ReplicaSet and confirm it does not over-create: scale one to 10 and delete its pods repeatedly while it works.

**Observe** — the ConfigMap count in both naming schemes, and the pod count on the ReplicaSet.

**Expect** — deterministic names give four ConfigMaps and a stream of `AlreadyExists` errors, which are noise but not damage. `GenerateName` gives eight, or twelve, and **nothing ever cleans them up**: the next reconcile counts twelve, wants four, and if your reconcile deletes surplus children it will now oscillate, and if it does not, the surplus is permanent.

The mechanism the tree uses is a counter per controller key, decremented by the informer event for each child it created. A reconcile that finds its expectations unsatisfied **returns without acting** and waits for its own writes to come back through the watch — with a timeout, so a create that produced no event does not wedge the controller forever. That timeout is not a detail: it is the admission that the cache may never deliver, and it is what stops the mechanism from being a distributed lock.

The comparison to write down:

| | Deterministic names | `ControllerExpectations` |
|---|---|---|
| makes creates | idempotent | counted |
| costs | you must be able to name every child | a counter, a timeout, and three call sites to keep correct |
| fails when | two children are genuinely identical and both needed | the informer misses an event and the timeout is what saves you |
| available to ReplicaSet | **no** — pod names are generated, precisely so two identical pods can coexist | yes, and this is why it exists |

**Your operator's immunity is a consequence of its API**, not of care taken in its reconcile. An `Ensemble` with four voices has four *named* children; a ReplicaSet with four replicas has four *interchangeable* ones, and interchangeability is exactly what makes them uncountable by name. Say which kind of controller yours is, in one sentence, in the write-up.

**Write down** — the counts under both naming schemes, the three `Expectations` call sites with `file:line`, and the table above with your operator's row filled in. This is [the checklist's](../../phases/04-controllers.md#checklist) claim about over-creation, and it is one of [the capstone's](../../phases/04-controllers.md#capstone) four citations.

**Footprint note** — a dozen ConfigMaps and ten `pause` pods, briefly.

**Teardown**

```sh
kubectl -n academy-lab delete ensemble beta
kubectl -n academy-lab delete configmap -l academy.k3ii.dev/ensemble=beta --ignore-not-found
```

The second line is the one that matters: the orphans from the `GenerateName` run have owner references and *should* go with the parent — check that they did, and if any survived, you have found a second bug worth a line in the journal. Restore deterministic naming before continuing. **The topology stays.**
