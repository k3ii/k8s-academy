<a id="the-capstone-trace"></a>
# The capstone: one `kubectl apply`, cited end to end

**Artifact** — [the capstone](../../phases/03-api-machinery.md#capstone) as the phase specifies it: a serving cluster with three webhooks on it, and a written trace of a single `kubectl apply` from the client to the etcd transaction, every stage cited to `file:line` in the tree you have been reading, each citation verified live.

**Rests on** — all of it. The instrumentation from [the create.go exercise](08-the-order-of-calls-in-create-go.md) is the backbone: the trace's spine is the five log points you added, and the citations are what those points let you confirm rather than assume.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), re-provisioned. See the footprint note.

**Setup**

1. Provision `pair` per [the strand](../../strands/lab-topologies.md#provision).
2. Redeploy the three webhooks from their manifests. The images are still in the registry on [`forge`](../../strands/lab-topologies.md#build-guest) — nothing needs rebuilding:

   ```sh
   kubectl apply -k build/03-validating-webhook/deploy/
   kubectl apply -k build/03-mutating-webhook/deploy/
   kubectl apply -k build/03-conversion-webhook/deploy/
   ```

   If those directories do not exist, you stored the manifests somewhere else, and the fix belongs in the earlier exercises rather than here.
3. Restart the instrumented apiserver on `forge` from [module 3.1](05-hand-start-an-apiserver.md). The trace's log-point evidence comes from **that** apiserver, not from `pair`'s — `pair` runs the webhooks and the CRD, `forge` runs the binary you can see inside. Say so explicitly in the write-up; a trace that pretends one process did both is the exact kind of unchecked claim this capstone is graded against.

**Do**

1. Send one `kubectl apply -v=8` of a Pod that all three mechanisms touch: it is mutated (gets a memory limit), validated (has one, so it passes), and is in the selected namespace.

2. Write the trace as an ordered list. For each stage: what happens, the `file:function`, the line number, and **how you confirmed it** — a log line you added, a `-v=8` client output, an audit entry, or a `debug.Stack()` frame. A citation with no confirmation column is not finished.

   The stages the capstone requires:

   | # | Stage | Where |
   |---|---|---|
   | 1 | the client builds the request | `kubectl/pkg/cmd/apply/apply.go` |
   | 2 | the URL becomes a `RequestInfo` | `endpoints/filters/requestinfo.go` |
   | 3 | the identity is established | `endpoints/filters/authentication.go` |
   | 4 | the decision is made | `endpoints/filters/authorization.go` |
   | 5 | mutating before validating | `admission/chain.go` — and [its caller](14-the-line-that-orders-the-chain.md) |
   | 6 | the handler orchestrates | `endpoints/handlers/create.go` |
   | 7 | the strategy prepares | `registry/rest/create.go`, `pkg/registry/core/pod/strategy.go` |
   | 8 | the generic store writes | `registry/generic/registry/store.go` |
   | 9 | the etcd transaction | `storage/etcd3/store.go` |

3. Add the two stages the table omits and the phase's spine talk includes: **APF**, which happens before any of this, and the **watch fan-out**, which happens after. Cite both. Their absence from the required list is not an accident — find where each sits relative to stage 2, and note that one of them is *not* in the request path at all.

4. Verify every citation per [the archaeology standard](../../strands/source-archaeology.md#drills), against the sha you recorded in [exercise 2](02-every-flag-located-in-source.md). The `cacher` split is the [known trap](../../strands/source-archaeology.md#stale-paths) and is not the only one; a line number copied from anywhere but your own tree is a citation you have not made.

5. Have the trace read by a hostile reader — or be one. Pick the three citations a sceptic would check first and check them again.

**Expect** — the trace is graded on whether the references survive checking, so expect to lose two or three of them on step 4 and count that as the exercise working. The most commonly wrong stage is 5, because the ordering is not stated where it looks like it should be — [that exercise](14-the-line-that-orders-the-chain.md) already told you the honest citation is the caller, and the capstone is where you find out whether you wrote that down or nodded at it.

Stage 7 has the second trap: the line where the strategy is *invoked* and the line where the strategy's *behaviour* is defined are in different repositories' worth of directory distance, and citing only one of them is an incomplete answer.

**Write down** — the trace, the three-webhook cluster's `kubectl get validatingwebhookconfigurations,mutatingwebhookconfigurations` output and the CRD's conversion stanza as evidence of artifact 2, and a short note on which citations you lost at step 4 and why.

**Footprint note — this is the phase's one deliberate re-provision, and it is a real cost.** `pair` was destroyed at [the end of module 3.5](41-3c5-an-expired-component-certificate.md) so that [k0s](42-k0s-in-one-binary.md) could be met against a clean machine rather than beside a kubeadm cluster, which is the whole point of module 3.6. Keeping `pair` alive through 3.6 instead would cost 5.0GB + 2.0GB + `forge` at 2560MB = 9.5GB, exactly [the ceiling](../../strands/lab-topologies.md#ceiling) with no margin, on a phase whose peak is already the highest in the curriculum so far.

**The smallest change that makes the re-provision cheap** is to store each build artifact's Kubernetes manifests in `build/03-*/deploy/` as it is written, rather than pasting them from the exercise files — then the whole apparatus comes back in three `kubectl apply -k` invocations against images that were never deleted. Do that at [exercise 18](18-the-webhook-the-apiserver-dials.md), not here.

The alternative considered and rejected: running the capstone on `k0s-light`. It fails because k0s is a demonstration of *not* configuring the seams, and the capstone is a demonstration of having configured them.

**Teardown** — the phase ends here.

```sh
just tofu labs destroy
ssh hopper 'qm set 125 --memory 1536 && qm reboot 125'
```

The second line returns [`forge`](../../strands/lab-topologies.md#build-guest) to its normal 1536MB — [module 3.1](05-hand-start-an-apiserver.md) raised it for the apiserver build and nothing after this phase needs it. Keep the k/k clone and the `GOCACHE`; [P4](../../phases/04-controllers.md) reads the same tree.
