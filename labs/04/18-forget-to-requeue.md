<a id="forget-to-requeue"></a>
# The error you returned, and the retry that never came

**Claim** — a `syncHandler` that returns an error is only retried because the worker loop chose to retry it. Remove that choice and the object stops reconciling forever while every other object keeps working, the queue stays empty, and no metric moves. You can produce that state, then produce its opposite — a key retried forever with no ceiling — and state which of the two an operator would notice first.

**Rests on** — [the backoff you measured](07-the-hot-loop-and-the-backoff-that-hides-it.md) and [the drill](17-4c1-kill-it-mid-reconcile.md). Those two cover interruption and over-retry; this is the third corner, under-retry, and it is the quiet one.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Do**

1. Make one `Ensemble` fail reliably. Point it at a namespace that does not exist, so the registry write returns `NotFound`:

   ```sh
   kubectl -n academy-lab apply -f - <<'EOF'
   apiVersion: academy.k3ii.dev/v1alpha1
   kind: Ensemble
   metadata: {name: doomed}
   spec: {voices: 2, registryNamespace: nowhere}
   EOF
   ```

2. Watch the correct behaviour first: `doomed` retries on the backoff curve you measured, `alpha` is unaffected, and `status.conditions[Ready]` on `doomed` carries a reason naming the missing namespace.

3. Now break the worker loop in the three ways that are all one line each. Run each, then repair:

   | Change | Predict the symptom |
   |---|---|
   | `Forget(key)` unconditionally, before checking the error | |
   | drop the `AddRateLimited` on the error path entirely | |
   | keep the requeue, never `Forget` on success | |

4. For each, ask three questions at the cluster and answer them from outside the process: does `alpha` still reconcile? does `doomed` ever recover once you create the `nowhere` namespace? how long does `alpha` take to react to a change after `doomed` has been failing for ten minutes?

**Observe** — the operator's log rate, the `Ready` condition on both objects, and the time to react on `alpha`.

**Expect** — the first two produce the same visible state and different causes: `doomed` is stuck, `alpha` is fine, the process is idle. **Creating the missing namespace does not fix it** — nothing re-enqueues the key, because nothing is watching the thing that changed. The object is repaired only by a write to the object, or by a restart, or by the resync interval if you set one. That last is worth pausing on: **a periodic resync is the thing that turns "stuck forever" into "stuck for at most one resync period"**, which is why the informer offers one and why choosing zero is a decision rather than a default.

The third is the one that is invisible until it is not: `doomed` accumulates requeues, and because the default limiter's per-item delay is shared with nothing, `alpha` stays fast — right up until you have a hundred failing objects and the overall bucket limiter, not the per-item one, is what you are up against.

**Which an operator notices first** is the sentence to write down. The hot loop from [exercise 7](07-the-hot-loop-and-the-backoff-that-hides-it.md) shows up on a CPU graph and an apiserver request-rate graph within minutes. This one shows up when somebody asks why their object never became ready, which may be never.

**Write down** — the three predictions and outcomes, and the resync-interval sentence. Then check your own [operator](15-the-hand-wired-loop.md) for which of the three it currently does, before [the stage-2 exercise](19-stage-2-and-the-role-you-write-yourself.md) puts it in the cluster where you cannot watch its stdout.

**Footprint note** — nothing new. Two `Ensemble` objects and their children.

**Teardown**

```sh
kubectl -n academy-lab delete ensemble doomed
```

Confirm its two children go with it, which is the garbage collector and not your code. **The topology stays.**
