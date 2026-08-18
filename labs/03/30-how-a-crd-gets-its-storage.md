<a id="how-a-crd-gets-its-storage"></a>
# Where a CRD's REST storage comes from at runtime

**Claim** — a built-in resource's storage is wired at apiserver startup and a CRD's is constructed on demand, cached, and torn down when the CRD changes; you can name the type that holds that cache, the key it is keyed by, and the event that invalidates an entry, each with a `file:line`.

**Rests on** — [the strategy exercise](12-what-a-strategy-decides.md), which read the built-in side of exactly this: `registry/generic/registry/store.go` reached through a hand-written strategy. The question here is what plays the strategy's part when nobody hand-wrote one.

**Topology** — none for the reading. Use the instrumented tree on [`forge`](../../strands/lab-topologies.md#build-guest) from [the flag exercise](02-every-flag-located-in-source.md); the [`pair`](../../strands/lab-topologies.md#pair) cluster stays up and is used only for the check in step 5.

**Do**

1. Read `staging/src/k8s.io/apiextensions-apiserver/pkg/apiserver/customresource_handler.go`. It is long. Read it for three things and skip the rest:
   - the `ServeHTTP` method — how a request for `/apis/academy.k3ii.dev/v1/widgets` finds anything at all, given that no route for it was registered at startup;
   - `getOrCreateServingInfoFor` — the construction path, and the lock around it;
   - the informer event handlers at the bottom of the file — what happens to a cached entry when the CRD object is updated.

2. Answer, each with a `file:line` from your clone at [the sha you recorded](02-every-flag-located-in-source.md):

   | Question | Where the answer is |
   |---|---|
   | What type holds the per-CRD storage, and what is it keyed by? | the field, not the accessor |
   | What is constructed per version, and what is shared across versions? | the construction path |
   | Which struct plays `pkg/registry/core/pod/strategy.go`'s part for a CRD? | name it, and say what it reads its behaviour from instead of Go code |
   | What invalidates an entry, and what does *not*? | the event handlers |
   | Where is the conversion webhook you built called from? | follow it from the storage, not from the handler |

3. Follow one question further than the table asks: from the type in row 3, find where `x-kubernetes-validations` is evaluated. It is not in that struct. Name the package it is in and how it is reached.

4. Now compare against the built-in path. In `pkg/registry/core/pod/storage/storage.go`, find where `NewStorage` is called from, and follow it up to `cmd/kube-apiserver/app/server.go`. Write one sentence contrasting *when* the two happen.

5. Check the claim on the running cluster. Change the CRD in a way that must invalidate the cache — add a printer column to `v1` — and watch whether the change is served immediately:

   ```sh
   kubectl get widgets -o wide          # before
   kubectl patch crd widgets.academy.k3ii.dev --type=json \
     -p '[{"op":"add","path":"/spec/versions/0/additionalPrinterColumns","value":[{"name":"Size","type":"string","jsonPath":".spec.size"}]}]'
   kubectl get widgets -o wide          # after
   ```

**Expect** — the storage is per-CRD **and per-version**, keyed by UID rather than by name, which is the detail worth stopping on: a CRD deleted and recreated with the same name is a different key, and that is deliberate. The strategy's part is played by a struct that reads its behaviour from the CRD's schema at runtime rather than from compiled Go — which is the whole difference between the two paths stated as one sentence.

The invalidation answer has a trap in it: not every update to the CRD tears the entry down, and the ones that do not are the ones where nothing about serving changed. Name which is which.

The printer column appears with no restart and no perceptible delay. Contrast that with what adding a field to a built-in type costs.

**Write down** — the five `file:line` answers, the row-3 struct's name, the sentence from step 4, and the UID-keying detail with why it is not a bug.

**Teardown** — revert the printer column patch. Nothing else was created. **The topology stays** — [the aggregation exercise](31-an-apiservice-routes-out-of-process.md) needs it.
