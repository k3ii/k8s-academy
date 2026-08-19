<a id="drift-detection-off-by-default"></a>
# A hand-edit to a Flux-managed Deployment survives — until you turn drift detection on, and then it does not

**Claim** — `kubectl scale` a Deployment that helm-controller installed and, with drift detection at its default, **nothing happens**: the replica count you set by hand stays, because out of the box the controller re-runs Helm only when the *desired state in git* changes, not when the live object drifts. Flip `mode: enabled`, scale again, and the change snaps back within a reconcile. The default is the whole lesson — it is the difference between *converging on change* and *converging continuously*, which is the distinction this phase is about.

**Rests on** — [the Flux install](01-gitops-the-reconcile-loop-you-already-wrote.md), whose `HelmRelease` this drifts; and [P4's reconcile loop](../../phases/04-controllers.md#m4-1), because "reconcile" quietly means two different things here and this exercise separates them.

**Topology** — [`platform`](../../strands/lab-topologies.md#platform), continued.

**Read** — [the module framing](../../phases/12-gitops-platform.md#m12-1) and the source question below. Held to [the archaeology drill standard](../../strands/source-archaeology.md#drills): the default is a line, not a belief, so cite it.

> **Question to answer from the source:** in `helm-controller`, which function returns the drift-detection mode, and what does it return when the field is unset? Cite the line — the unset default (`DriftDetectionDisabled`) is the whole beat. Only at `mode: enabled` does the controller server-side dry-run apply and correct a hand-edit; below that it is blind to one.

**Do** — drift the Deployment by hand with the default mode, then again with drift on:

```sh
DEP=$(kubectl get deploy -l app.kubernetes.io/managed-by=Helm -o jsonpath='{.items[0].metadata.name}')
kubectl scale deploy/$DEP --replicas=5      # a hand-edit the controller did not ask for
sleep 90; kubectl get deploy/$DEP           # default mode: still 5 — nothing reverted it
# turn drift detection on in the HelmRelease:
kubectl -n flux-system patch helmrelease <name> --type=merge \
  -p '{"spec":{"driftDetection":{"mode":"enabled"}}}'
kubectl scale deploy/$DEP --replicas=5
sleep 90; kubectl get deploy/$DEP           # now back to the chart's replica count
```

**Observe** — with the field unset the replica count holds at 5 across a full reconcile interval; with `mode: enabled` it returns to the chart's value on the next reconcile, and the `HelmRelease` events name the correction. The controller did not gain a new ability — it always reconciled desired-state changes; drift mode is what makes a *live* divergence count as something to correct.

**Expect** — two different outcomes for the same `kubectl scale`, separated only by one field. If the hand-edit reverts even with the field unset, you did not read the default right — go back to the cited `GetMode()` line before trusting the behaviour.

**Write down** — the cited drift-mode function and its unset return value, and one sentence naming what changed between the two runs: not the controller's reconcile, but what counts as a thing to reconcile.

**Footprint note** — no new pods; [`platform`](../../strands/lab-topologies.md#platform) unchanged from [the Flux install](01-gitops-the-reconcile-loop-you-already-wrote.md).

**Teardown** — set `mode` back to unset (or leave it enabled for [the blast-radius drill](03-12c1-a-commit-is-a-deploy-to-everything.md), which uses drift-on as its setup) and restore the replica count from git. **The topology stays.**
