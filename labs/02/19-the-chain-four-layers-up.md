<a id="the-chain-four-layers-up"></a>
# One compaction, four layers, and the relist at the top

**Artifact** — the causal chain **etcd compaction → watcher eviction (`ErrCompacted`) → apiserver `410 Gone` → client-go relist**, written out with a `file:line` or a documented error string at each arrow, in a form you can then state from memory. **[Gate condition 1](../../phases/02-etcd.md#gate) is this artifact recited without notes**, and the phase does not end until you can.

**Rests on** — [exercise 17](17-synced-unsynced-victim.md) for the first arrow and [exercise 18](18-compact-under-a-live-watcher.md) for the second. The third and fourth arrows are **not observable in this phase** — there is no Kubernetes on [`etcd-only`](../../strands/lab-topologies.md#etcd-only) and there will not be. They are established from source and from the error string you already met in [P1](../01/06-resourceversion-moves.md), where a `resourceVersion` too old returned `410 Gone` on a cluster you had running at the time.

**Topology** — none required. This is written work, and it is deliberately placed at the end of [module 2.3](../../phases/02-etcd.md#m2-3) rather than at the end of the phase, because the two arrows you *can* demonstrate are fresh right now.

**Do**

1. Write arrow 1 — **compaction → eviction**. One sentence on what compaction removes, one on why a behind watcher cannot be served without it, and the `watchable_store.go` `file:line` from [exercise 18](18-compact-under-a-live-watcher.md).

2. Write arrow 2 — **eviction → what the etcd client sees**. The exact error text you captured, and the fact that the stream ends rather than degrades.

3. Establish arrow 3 — **`ErrCompacted` → `410 Gone`**. You have no apiserver here, so this is a citation, not a measurement. Search the k8s tree if you have it, or state it from the API conventions and the `410` you produced in [P1](../01/06-resourceversion-moves.md) with a deliberately old `resourceVersion`. Name the HTTP status, the `Reason` on the `Status` object, and the message text. **Mark this arrow as cited-not-observed in your write-up** — [P3](../../phases/03-api-machinery.md) opens the apiserver's storage layer and the `cacher` that sits between these two arrows, and it is where you replace the citation with a trace.

4. Establish arrow 4 — **`410` → relist**. What does a client-go reflector do when its watch returns that status? Name the two calls it makes and in which order, and say what happens to the informer's cache in between. [P4](../../phases/04-controllers.md) builds this from the other side.

5. Now find the two places the chain is **not** a straight line, because a chain you can only recite forwards is not yet a model:

   - The apiserver does not put every watch straight through to etcd. Name what sits in between, and say whether it can serve a request etcd would have refused.
   - Not every `410` a client sees comes from a compaction. Name one other cause.

6. Recite it. Close the notes, say the four arrows out loud, then check. Repeat until it comes out whole. This is the only exercise in the curriculum whose success condition is recall, and it is here because two later phases assume this chain as a primitive and neither re-teaches it.

**Expect** — the chain is four arrows and about six sentences, and the compression is the value. Written long it is a paragraph anyone could produce; written short it is the sentence that makes an unexplained controller resync at 3am immediately legible as *someone compacted, or something was slow enough to fall behind*.

Step 5's first answer is the one most people miss, and it is the reason [P3](../../phases/03-api-machinery.md) exists as a separate phase.

**Write down** — the chain itself, in your journal, with the two demonstrated arrows carrying their `file:line` and the two cited arrows marked as cited. Then add the one-line operational form: *what an operator sees when this happens to a real cluster, and which metric would have warned them.*

**Teardown** — nothing was created. If the topology is still up from [exercise 18](18-compact-under-a-live-watcher.md), **it stays** — [module 2.4](../../phases/02-etcd.md#m2-4) starts on the same cluster and wants the `/sync/` keys still in it.
