<a id="synchronize-and-the-ranking"></a>
# One function decides who dies, and the order is not the one people quote

**Claim** — the eviction victim order is fully determined by three comparators applied in a fixed sequence inside `eviction_manager.go`, and QoS class enters only through one of them — so "BestEffort goes first" is a consequence you can derive, not a rule the code contains.

**Rests on** — [the prediction table](10-the-signals-before-the-code.md). Answer 3 in that table gets scored here.

**Topology** — **none.** Reading on [`forge`](../../strands/lab-topologies.md#build-guest) or on any clone of k/k.

**Read** — in this order, and stop at each boundary:

| Item | Answer from it |
|---|---|
| `pkg/kubelet/eviction/api/types.go`, then `pkg/kubelet/eviction/types.go` (item 11) | The `Signal`, `Threshold` and `ThresholdValue` types. How is a percentage threshold represented differently from an absolute one, and what does that force `synchronize()` to do with node capacity? |
| `pkg/kubelet/eviction/eviction_manager.go`, `synchronize()` only (item 11) | The loop: observe → threshold-cross → rank → evict one. How many pods does one pass evict, and what happens to the rest? |
| The ranking functions the same file selects between (`rankMemoryPressure`, and the disk equivalents) | The comparator sequence. Where does QoS class enter it, and where does *usage above request* enter it? **This is [objective 3](../../phases/06-kubelet-node.md#objectives).** |
| `pkg/kubelet/eviction/defaults_linux.go` (item 12) | The shipped defaults, against your two guesses. |

For the last row: locate the file and read the values yourself. **They are not repeated here**, and [the phase does not repeat them either](../../phases/06-kubelet-node.md#m6-3) — a default that changes upstream and is stale in your notes is worse than one you can locate on demand.

**Do** — write the comparator sequence out as pseudocode, in order, with a `file:line` for each step. Then hand-rank these four pods for a `memory.available` eviction, using only your pseudocode:

| Pod | QoS | memory request | current usage | Priority |
|---|---|---|---|---|
| `alpha` | Burstable | 100Mi | 500Mi | 0 |
| `beta` | Burstable | 400Mi | 500Mi | 0 |
| `gamma` | BestEffort | — | 300Mi | 0 |
| `delta` | Burstable | 100Mi | 500Mi | 1000 |

Now check the defaults question that decides half of it: is pod priority compared *before* or *after* usage-above-request, and does that ordering depend on a feature gate? Find the answer in the code, not in a blog.

**Expect** — the ranking to be a `sort.Sort` over a slice of comparators, so the whole ordering is readable in one screen. Expect `gamma` to rank first — and expect your reason to be "its usage exceeds its request by the largest margin, because its request is zero", not "it is BestEffort". The two reasons give the same answer here and different answers for `alpha` versus `beta`, which is exactly why the exercise includes both.

Expect one pass of `synchronize()` to evict **one** pod and return, leaving the next decision to the next observation. That is the level-triggered shape from [P4](../../phases/04-controllers.md) appearing in a place people expect a batch algorithm, and it is why an eviction cascade is a series of independent decisions rather than a plan.

Expect at least one shipped default to be a percentage and at least one to be absolute, which is the reason `types.go` needed two representations.

**Write down** — the comparator pseudocode with citations, your four-pod ranking with the deciding comparator named for each pair, and the real defaults against your guesses from [exercise 10](10-the-signals-before-the-code.md). [The module's write-down](../../phases/06-kubelet-node.md#m6-3) wants the citations, so keep the line numbers.

**Teardown** — nothing to delete. **The topology stays** if it is up; [the next exercise](12-an-eviction-you-configured.md) needs the worker.
