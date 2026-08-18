<a id="what-hassynced-actually-promises"></a>
# `HasSynced` is a promise about one moment, not about being current

**Claim** — `HasSynced` becomes true when the objects from the *initial* list have been popped from the queue and put in the store. It does not promise that your handlers have finished with them, and it does not promise the store is current with the server at any later instant. You can state which of those three things it covers, cite the two functions that implement it, and time the flip against your own log.

**Rests on** — [the probe](10-the-410-under-your-own-informer.md) and [module 4.2's](../../phases/04-controllers.md#m4-2) `shared_informer.go` reading question.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued, `academy-lab` now empty.

**Setup** — seed the namespace so the initial list is not trivial:

```sh
for i in $(seq 1 50); do kubectl -n academy-lab create configmap seed-$i --from-literal=n=$i >/dev/null; done
```

**Do**

1. Read both halves. The informer's `HasSynced` delegates, and the delegate counts something specific:

   ```sh
   cd ~/src/kubernetes
   git grep -n 'func (s \*sharedIndexInformer) HasSynced\|WaitForCacheSync' -- staging/src/k8s.io/client-go/tools/cache/shared_informer.go
   git grep -n 'func (f \*DeltaFIFO) HasSynced\|initialPopulationCount\|populated' -- staging/src/k8s.io/client-go/tools/cache/delta_fifo.go
   ```

   Answer in writing, from those functions: **what is being counted down to zero**, and at what moment it reaches zero relative to (a) the list returning, (b) your handler being called for the last listed object, and (c) that handler *finishing*.

2. Add two lines to the probe: a goroutine polling `fifo.HasSynced()` every 10ms and printing the first `true`, and a print of `isInInitialList` inside the `Pop` handler.

3. Keep the four-second sleep in the `Pop` loop, restart the probe, and watch.

**Observe** — where the `SYNCED` line falls in the stream of `POP` lines.

**Expect** — it does not fall at the end of the initial burst; it falls when the last initially-listed key is *popped*, which with a four-second consumer is many seconds before the last handler returns. A controller that waits for `HasSynced` and then reconciles is therefore working from a store that is complete but whose handlers are still catching up — which is fine, because the store is what the reconcile reads, and the handlers only enqueue keys.

The second half of the claim is the one worth constructing: after `HasSynced` is true, create a ConfigMap and read the indexer 50 milliseconds later. It is not there. `HasSynced` said nothing about *now* and never will; **the only freshness guarantee an informer offers is "everything the server told me, in order"**, and the distance between that and the server's present state is your watch latency plus your consumer's backlog. This is exactly why a reconcile is allowed to be wrong once and required to be right eventually, and why [exercise 22](22-expectations-or-over-create.md)'s over-creation is a real bug rather than a theoretical one.

**Write down** — the three-part answer from step 1, the timing of the flip, and one sentence stating what a controller may assume the instant `WaitForCacheSync` returns.

**Footprint note** — 50 ConfigMaps, deleted below.

**Teardown** — stop the probe. **Keep the 50 ConfigMaps** — [the drill](12-4c4-act-before-the-cache-is-synced.md) needs a populated namespace and an empty one is the trivial case where the bug hides. **The topology stays.**
