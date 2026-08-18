<a id="4c4-act-before-the-cache-is-synced"></a>
# 4.C4 — a controller with an empty cache concludes nothing should exist

**Claim** — the dangerous shape is not "the cache is stale" but "the cache is *empty and believed*". A reconcile that deletes what it cannot find, run before `WaitForCacheSync`, deletes everything — and it does so with no error, no retry and no metric, because from inside the process the run was a complete success.

**Rests on** — [what `HasSynced` promises](11-what-hassynced-actually-promises.md), and the 50 seed ConfigMaps left in place there.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued. Everything destroyed here lives in `academy-lab` and nowhere else.

**Setup — the escape hatch, before anything else.** This drill deletes objects on purpose, so make the restore one line and test it now:

```sh
seed() { for i in $(seq 1 50); do kubectl -n academy-lab create configmap seed-$i --from-literal=n=$i >/dev/null; done; }
kubectl -n academy-lab get configmap --no-headers | wc -l     # expect 50
```

Nothing outside `academy-lab` is touched by anything below. Confirm that by reading your own reconcile's namespace argument before you run it, not after.

**Do**

1. Write a ten-line reconcile with the shape half the operators in the world have — *the API is truth, the cache is the desired set, delete the difference*:

   ```go
   informer := factory.Core().V1().ConfigMaps()
   lister := informer.Lister()
   factory.Start(stop)
   // NO WaitForCacheSync here. That is the drill.

   live, _ := cs.CoreV1().ConfigMaps("academy-lab").List(ctx, metav1.ListOptions{})
   for _, cm := range live.Items {
       if _, err := lister.ConfigMaps("academy-lab").Get(cm.Name); apierrors.IsNotFound(err) {
           fmt.Println("DELETE (not in cache)", cm.Name)
           _ = cs.CoreV1().ConfigMaps("academy-lab").Delete(ctx, cm.Name, metav1.DeleteOptions{})
       }
   }
   ```

2. Run it. Count what is left.

3. Re-seed, insert `cache.WaitForCacheSync(stop, informer.Informer().HasSynced)` immediately after `factory.Start`, and run it again.

4. Now the subtler half, with the sync in place. Have the reconcile **create** `seed-99`, then immediately re-read it from the lister and, if absent, create it again. Run it once.

**Observe** — the count of `DELETE` lines in step 2, of `DELETE` lines in step 3, and the error returned by the second create in step 4.

**Expect** — step 2 deletes all fifty. The process exits zero. The only trace is your own print, and if you had not printed you would have nothing at all: no API error, no event on any object, nothing in the apiserver audit that distinguishes this from an intentional cleanup. Step 3 deletes none.

Step 4 fails with `AlreadyExists` — and that failure is the good outcome. **The cache does not contain your own write yet**, so a reconcile that verifies its work by re-reading the cache concludes the work did not happen. Deterministic names turn that into a harmless `AlreadyExists`; generated names turn it into a duplicate. The mechanism the tree uses to avoid both is `ControllerExpectations`, and it is [exercise 22](22-expectations-or-over-create.md) — the reason it exists is this exact three-line experiment.

The rule to take into your own operator: **`WaitForCacheSync` before the first reconcile, and never treat "absent from the cache" as "absent from the cluster" for a destructive decision.** The first is one line. The second is a design rule with no compiler behind it, which is why [module 4.4's](../../phases/04-controllers.md#m4-4) exemplar reconciles against owner references rather than against absence.

**Write down** — the two counts, and one sentence answering [module 4.2's](../../phases/04-controllers.md#m4-2) question about why acting before sync is wrong, phrased as the incident it causes rather than as the rule it breaks.

**Footprint note** — nothing new; 50 tiny ConfigMaps, created and destroyed twice.

**Teardown**

```sh
kubectl -n academy-lab delete configmap --all
```

**The topology stays.** The cluster is idle for [the next exercise](13-the-same-drawing-corrected.md), which needs no cluster at all, and busy again from [the generated clientset](14-generate-the-clientset.md) onward.
