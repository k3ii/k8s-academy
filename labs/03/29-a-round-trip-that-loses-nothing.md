<a id="a-round-trip-that-loses-nothing"></a>
# Prove the round trip, then break it on purpose

**Claim** — a Widget written as `v2`, stored as `v1` and read back as `v2` is byte-identical in `spec` to what you sent, for every input your webhook accepts; and a single-line change to the conversion makes that false in a way no error message reports.

**Rests on** — [the conversion webhook](28-the-conversion-webhook.md), whose lossy-direction strategy this is the test of. [KEP-598's requirement](../../phases/03-api-machinery.md#m3-4) is what "loses nothing" means precisely.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Do**

1. Write four Widgets through `v2`, chosen to sit at the edges of your mapping: an exact match (`10x10`), a non-match (`7x3`), the smallest legal (`1x1`), and one large enough to be obviously not an enum value (`400x1`).

2. Read each back as `v2` and diff `spec` against what you sent:

   ```sh
   for w in exact odd tiny wide; do
     kubectl -n tenant get widgets.v2.academy.k3ii.dev $w -o json \
       | jq -S '.spec' > /tmp/rt-$w.out
     jq -S '.spec' /tmp/rt-$w.in > /tmp/rt-$w.want
     diff /tmp/rt-$w.want /tmp/rt-$w.out && echo "$w OK" || echo "$w LOST DATA"
   done
   ```

3. Now break it. In `convert.go`, in the **v2→v1** direction only, drop whatever you carry the extra information in — the annotation, or the rounding tolerance. Rebuild, push, `kubectl rollout restart`.

4. Repeat step 2. Then, and this is the part that matters, go looking for a complaint:

   ```sh
   kubectl -n tenant get events --field-selector involvedObject.kind=Widget
   kubectl get crd widgets.academy.k3ii.dev -o jsonpath='{.status.conditions}' | jq
   kubectl -n academy-build logs deploy/academy-converter --tail=50
   ```

5. Recover the objects, or discover you cannot. Try re-applying the original `v2` manifests and diffing again.

**Observe**

```sh
kubectl -n tenant get widgets.v1.academy.k3ii.dev -o yaml    # what is actually stored
kubectl -n tenant get widgets.v2.academy.k3ii.dev -o yaml    # what you are shown
```

Watch the difference between those two commands. One is the truth and one is a rendering of it, and after step 3 they disagree about objects that were already correct before you changed anything.

**Expect** — before the break: four `OK`. After it: `exact` and `tiny` still pass (they land on enum values), `odd` and `wide` return `10x10` or whatever your rounding produces. **No event, no condition, no error log, no non-zero exit anywhere.** The apiserver's contract is that conversion is total and lossless; nothing checks that it is, because nothing can — a conversion webhook is the only authority on its own correctness.

Then the sharper half: the damage is not in the *reading*. Every object written **while the broken code was deployed** was stored with its extra information already discarded, so restoring `convert.go` restores the four you wrote earlier and does not restore anything written in between. Re-applying the original manifests works, which makes this recoverable here and not recoverable in a system where the manifests are not the source of truth.

**Write down** — the four diff results before and after, the empty search for a complaint in step 4 (list what you checked, since the negative result is the finding), and one sentence on what a real system would have to do to detect this — the answer is a round-trip test in CI, which is why [the property test](28-the-conversion-webhook.md) is where it is.

**Teardown** — restore `convert.go`, rebuild, redeploy, re-verify the four. Delete the Widgets. **Keep the CRD and the webhook** — [the storage question](30-how-a-crd-gets-its-storage.md) reads the code path all of this ran through. **The topology stays.**
