<a id="the-conversion-webhook"></a>
# The third webhook: a different request shape entirely

**Artifact** — the phase's third webhook and third build-track artifact: a CRD conversion webhook in `build/03-conversion-webhook/`, attached to `widgets.academy.k3ii.dev`, converting between `v1`'s `size` and `v2`'s `dimensions` in both directions — including the half of that mapping which cannot be lossless without help.

**Rests on** — [the pruning you observed](27-a-two-version-crd.md) with `conversion: None`, which is the problem this solves, and [the `cert-manager` path](22-the-mutating-webhook-cert-manager-signs.md), whose certificate machinery this reuses rather than re-deriving.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued from [the two-version CRD](27-a-two-version-crd.md).

**Build**

```
build/03-conversion-webhook/
  go.mod
  main.go          TLS server, one route: /convert
  convert.go       v1 <-> v2, both directions
  convert_test.go  round-trip property test
```

What it must implement, and where it differs from the two admission webhooks you have already written:

1. **A different request type.** The body is an `apiextensions.k8s.io/v1.ConversionReview`, not an `AdmissionReview`. It carries `request.objects` — **a list**, not one object — and `request.desiredAPIVersion`. Every object in the list must appear in `response.convertedObjects`, in order, or the response is invalid.
2. **No admit/deny.** There is no allowed field. The response carries `result` with a `Status`, and a failure is a failure of the *read*, not a rejection of a write. [The chaos drill](32-3c2-garbage-from-the-conversion-webhook.md) is built on exactly this difference.
3. **The mapping**: `small` ↔ 1×1, `medium` ↔ 5×5, `large` ↔ 10×10.
4. **The lossy direction, handled explicitly.** A `v2` Widget with `width: 7, height: 3` has no `v1` `size`. Choose a strategy and defend it in the write-up:
   - round to the nearest enumerated size and lose the exact values;
   - stash the original `dimensions` in an annotation on the way down and restore them on the way up;
   - refuse the conversion.
   The second is what real CRDs do and it is what [KEP-598's round-trip requirement](../../phases/03-api-machinery.md#m3-4) is asking for. The third is honest and produces an object nobody can store. Pick one, implement it, and say what the other two would have cost.
5. **`convert_test.go` as a property test**, not an example test: for a generated set of v2 objects, `to_v1(to_v2(x)) == x` must hold. This is the only place in the phase where a test is a genuine specification, and it is worth writing it that way.

Attach it to the CRD — the `caBundle` comes from `cert-manager` again, via the annotation on the **CRD**:

```yaml
spec:
  conversion:
    strategy: Webhook
    webhook:
      conversionReviewVersions: ["v1"]
      clientConfig:
        service:
          name: academy-converter
          namespace: academy-build
          path: /convert
          port: 443
```

**Gate** — [tier 2](../../strands/build-mechanics.md#gates), plus the property test, which is real evidence but is *your* test and therefore [not the gate](../../strands/build-mechanics.md#gates). The claim to write: **"a conversion webhook is invoked on ⟨which operations⟩ and not on ⟨which⟩, cited to ⟨`file:function`⟩ in `apiextensions-apiserver`"** — and the surprising half of that answer is what makes it worth claiming. Find out whether a *write* in the storage version invokes it at all.

**Expect** — a `v1` Widget now reads as a `v2` Widget with `dimensions: {width: 10, height: 10}` and no `size` field, and back again. The pruning from [the previous exercise](27-a-two-version-crd.md) is gone.

Two things to expect that the design does not advertise:

- **The webhook is called on `LIST` too**, once per object, in one request. A `kubectl get widgets` across a hundred objects is one `ConversionReview` with a hundred entries. Your handler's loop is a hot path in a way an admission handler's is not.
- **It is called on reads from `etcd` during the apiserver's own operations**, not only on user requests — which is why a broken conversion webhook takes down more than `kubectl get`, and why [the drill](32-3c2-garbage-from-the-conversion-webhook.md) is scoped the way it is.

The likeliest bug is the object list: returning one converted object for a list of three produces an error naming a count mismatch, which is at least a clear message. The second likeliest is dropping `metadata` — the conversion must preserve everything it does not deliberately change, including `resourceVersion`, and a handler that constructs a fresh object rather than editing the given one loses it and produces a conflict on every write.

**Write down** — the lossy-direction strategy and its defence, the citation with the operations answer, and the property test's failure output the first time it failed (it will).

**Footprint note** — a third small Go Deployment in `academy-build`. Same shape and same sizing rule as [the others](../../strands/build-mechanics.md#sizing); no change to the phase's arithmetic.

**Teardown** — delete the test Widgets. **Keep the webhook and the CRD** — [the round trip](29-a-round-trip-that-loses-nothing.md) is the next exercise and [the drill](32-3c2-garbage-from-the-conversion-webhook.md) breaks this same webhook. **The topology stays.**
