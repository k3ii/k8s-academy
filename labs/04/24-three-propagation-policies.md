<a id="three-propagation-policies"></a>
# The same delete, three times, with three different meanings

**Claim** — `Orphan`, `Background` and `Foreground` differ in *what is deleted first*, and only one of them makes the parent's disappearance mean anything about the children. You can predict, for each, whether the parent is gone the instant `kubectl delete` returns, what the children look like a second later, and which finalizer the API server adds to make it work.

**Rests on** — [module 4.4's](../../phases/04-controllers.md#m4-4) `garbage-collection.md` reading question, and [the owner references](23-one-owner-may-be-the-controller.md) whose behaviour these policies govern.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Setup** — three identical `Ensemble` objects, so the three runs are comparable:

```sh
for n in orphan background foreground; do
  kubectl -n academy-lab apply -f - <<EOF
apiVersion: academy.k3ii.dev/v1alpha1
kind: Ensemble
metadata: {name: $n}
spec: {voices: 3, registryNamespace: academy-registry}
EOF
done
kubectl -n academy-lab get configmaps | grep voice | wc -l    # expect 9 plus alpha's
```

**Do**

1. Predict all nine cells before running anything:

   | Policy | Parent gone when the command returns? | Children a second later | Finalizer added to the parent |
   |---|---|---|---|
   | `--cascade=orphan` | | | |
   | `--cascade=background` | | | |
   | `--cascade=foreground` | | | |

2. Run them, watching the parent in a second terminal so you can catch the intermediate state:

   ```sh
   kubectl -n academy-lab get ensemble -w &
   kubectl -n academy-lab delete ensemble orphan     --cascade=orphan
   kubectl -n academy-lab delete ensemble background --cascade=background
   kubectl -n academy-lab delete ensemble foreground --cascade=foreground
   kubectl -n academy-lab get configmaps
   ```

3. For `foreground`, catch the parent mid-delete and read its metadata before it disappears:

   ```sh
   kubectl -n academy-lab get ensemble foreground -o jsonpath='{.metadata.finalizers}{"\n"}{.metadata.deletionTimestamp}'
   ```

4. Look at the orphaned children's owner references afterwards.

**Observe** — the child count after each, and the parent's metadata during `foreground`.

**Expect** — `background` returns immediately, the parent is gone, and the children vanish shortly after, deleted by the garbage collector on its own schedule. `orphan` also returns immediately and the children stay — with their owner reference **removed**, which is the detail worth checking: they are not children of a missing parent, they are not children at all, and nothing will ever clean them up.

`foreground` is the interesting one, and it is the only one that is not fire-and-forget. The API server adds the `foregroundDeletion` finalizer to the parent, so the parent **stays visible with a `deletionTimestamp`** while its children are deleted, and only then goes. That is the same three-step dance your own finalizer performs in [exercise 15](15-the-hand-wired-loop.md) — set, do the work, remove — implemented for you by the cluster, and seeing it here is what makes the pattern read as a convention rather than an invention.

Your operator's own finalizer runs in all three cases, because it is triggered by the `deletionTimestamp` and not by the policy. Confirm that: the registry entry is gone in all three runs, including `orphan`, where the ConfigMap children survived. **Your cleanup and the cluster's cascade are independent mechanisms that happen to fire at the same moment**, and conflating them is how people write a finalizer that deletes children the GC was going to delete anyway — doing the work twice and racing itself.

**Write down** — [the checklist's](../../phases/04-controllers.md#checklist) propagation half: the nine-cell table with predictions and outcomes, and one sentence on the difference between `foregroundDeletion` and your own finalizer, given that they are the same mechanism.

**Footprint note** — nothing new; a handful of ConfigMaps, most of which delete themselves.

**Teardown**

```sh
kubectl -n academy-lab delete configmap -l academy.k3ii.dev/ensemble --ignore-not-found
kubectl -n academy-lab get configmaps
```

The orphans from the first run are the only litter this exercise leaves, and they are litter precisely because nothing owns them. **The topology stays.**
