<a id="stomp-it-back"></a>
# Two edits: one gets stomped, one survives

**Claim** — the controller corrects only what it computes. You can predict, before making them, which of two hand edits will be reverted and which will stand — and the boundary between them is the definition of "desired state" for this controller, not a general property of Kubernetes.

**Rests on** — [the instrumented run](04-five-log-lines-five-stages.md), whose `STAGE/` tags tell you *why* each edit was or was not corrected rather than only *that* it was.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued, with the instrumented `sample-controller` still running on [`forge`](../../strands/lab-topologies.md#build-guest).

**Do**

1. Predict first, in writing, for each of these four edits: stomped, or survives?

   | Edit | Prediction |
   |---|---|
   | `kubectl scale deploy example-foo --replicas=5` | |
   | `kubectl label deploy example-foo colour=blue` | |
   | edit `foo.status.availableReplicas` to `99` | |
   | edit `foo.spec.replicas` to `3` | |

2. Make them one at a time, watching `/tmp/trace.log`, and give each ten seconds:

   ```sh
   kubectl scale deploy example-foo --replicas=5; sleep 10; kubectl get deploy example-foo
   kubectl label deploy example-foo colour=blue; sleep 10; kubectl get deploy example-foo --show-labels
   kubectl patch foo example-foo --subresource=status --type=merge -p '{"status":{"availableReplicas":99}}'
   kubectl patch foo example-foo --type=merge -p '{"spec":{"replicas":3}}'
   ```

**Observe** — for each edit, which `STAGE/` tags fired, and whether a `STAGE/write` followed.

**Expect** — the replica count is stomped back within a second or two. The label **survives**: the controller builds a `Deployment` spec and compares one field, and a label it did not set is not a field it compares. The status patch is stomped, but by a *different* path — nothing you did changed the world, so the correction comes from the next reconcile of the `Foo`, not from a watch on the world. The spec edit is honoured, because that one is the desired state and the whole loop exists to serve it.

Two things follow, and both are worth having in writing before you build your own:

- **A controller that stomps everything is a controller nobody can operate.** The surviving label is not a gap; it is the reason a `Deployment` managed by an operator can still carry an annotation added by a service mesh or a cost tool. What gets corrected is exactly what the reconcile computes, which makes the *scope of the computed spec* a design decision with real consequences.
- **The stomp is not triggered by your edit being wrong.** It is triggered by an event arriving and the reconcile re-deriving the answer. Nothing compared your edit to a stored baseline. This is what [module 4.1](../../phases/04-controllers.md#m4-1) means by level-triggered, and it is the miniature version of [drill 4.C1](17-4c1-kill-it-mid-reconcile.md): interrupt it anywhere, and the next pass computes the same answer from the same inputs.

**Write down** — your four predictions with the outcome beside each, and one sentence naming the boundary: *this controller's desired state is ⟨these fields⟩ of the Deployment, and nothing else.*

**Footprint note** — five replicas of the sample `nginx` `Deployment` exist for a few seconds on the [`pair`](../../strands/lab-topologies.md#pair) worker. Scale it back to one before moving on; nothing else in the phase needs more than one pod of it.

**Teardown** — `kubectl delete -f artifacts/examples/example-foo.yaml`, and stop the controller with `Ctrl-C`. **Leave the `Foo` CRD installed** — [exercise 8](08-deltas-are-per-key.md) puts an informer on it. **The topology stays.**
