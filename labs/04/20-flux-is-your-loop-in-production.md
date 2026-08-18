<a id="flux-is-your-loop-in-production"></a>
# Someone else's reconcile loop, read the day after you wrote yours

**Claim** — every part you hand-wired appears in `fluxcd/kustomize-controller`, and you can cite the file for each: the queue, the key, the re-read, the finalizer, the status conditions and the requeue. You can also cite the two things it has that yours does not, and say why each is a production requirement rather than a refinement.

**Rests on** — [the hand-wired loop](15-the-hand-wired-loop.md) and [its gate](16-envtest-is-a-real-apiserver.md). This is [the ecosystem section's](../../phases/04-controllers.md#ecosystem) hands-on, and it is placed here rather than at the end of the phase on purpose: reading a mature controller is a reality-check only while your own is still fresh enough to be embarrassing.

**Topology** — none. Reading, on [`forge`](../../strands/lab-topologies.md#build-guest).

**Setup**

```sh
cd ~/src && git clone --filter=blob:none https://github.com/fluxcd/kustomize-controller
cd kustomize-controller && git log -1 --format='%H %cd'
```

Record that sha with the citations, [as always](../../strands/source-archaeology.md#drills).

**Do**

1. Fill this table with a `file:line` from *their* tree and one from *yours*:

   | Part | `kustomize-controller` | `build/04-operator-clientgo` |
   |---|---|---|
   | the reconcile entry point | | |
   | where the object is re-read | | |
   | the finalizer constant, and where it is added | | |
   | the finalizer's cleanup, and where it is removed | | |
   | the status condition types | | |
   | the requeue on error | | |
   | the requeue on **success** | | |

2. The last row is the one that has no counterpart in your operator. Find what it requeues after, where that duration comes from, and follow it back to the field on the CRD that sets it.

3. Answer two questions from the source, not from the docs:
   - **What does this controller do when nothing has changed?** Trace one full reconcile of an unchanged object and say what work it performs and what writes it makes.
   - **Where is drift corrected?** Find the comparison between the desired manifests and the live cluster, and name the function that applies the difference.

**Expect** — the shapes line up almost row for row, which is the point: what you wrote is not a toy version of this, it is the same construction with fewer features. The two additions are worth stating precisely:

- **A reconcile interval on the object.** Yours reacts to events; this one also reacts to *time*, because the thing it reconciles against — a Git commit — is outside the cluster and produces no watch events. **A controller whose desired state lives outside Kubernetes must poll, and the interval is therefore part of its API rather than a tuning knob.** That is also the answer to [exercise 18's](18-forget-to-requeue.md) stuck-forever case, arrived at from a completely different direction.
- **Drift correction as an explicit step**, with its own condition and its own events, rather than as a side effect of computing desired-versus-actual. When a human edits a managed object, this controller reports what it changed back and why.

That second point is [the gap P1 opened](../../phases/01-operate-shallow.md), closed: `helm upgrade` rendered templates and left; delete something it made and it stayed gone. This controller re-derives the same desired state on every pass and puts it back — which is [the stomp you produced in exercise 5](05-stomp-it-back.md), running in production against a Git repository. The GitOps argument is that difference and nothing more.

**Write down** — the completed table with both trees' shas, and one paragraph naming the two additions and what each buys. [P12](../../phases/12-gitops-platform.md) runs this software; this exercise is the only place in the curriculum where its *source* is read against code you wrote yourself, and the write-up is what P12 starts from.

**Footprint note** — a blobless clone, a few tens of MB on `forge`. Nothing is deployed: Flux's four controllers are [P12's](../../phases/12-gitops-platform.md) budget, on a different topology, and installing them here would spend `pair`'s headroom on something this exercise does not need.

**Teardown** — keep the clone; P12 wants it. **The topology stays.**
