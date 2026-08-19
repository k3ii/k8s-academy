<a id="backstage-read-never-installed"></a>
# Backstage, read from its own source and never installed: a scaffolder that runs once against a golden path that reconciles forever

**Artifact** — an answer, cited from Backstage's own source on [`forge`](../../strands/lab-topologies.md#build-guest), to one structural question: its scaffolder is a **one-shot linear task runner** — no reconcile loop, no drift detection, no desired-state comparison — the opposite of everything [Group A](01-gitops-the-reconcile-loop-you-already-wrote.md) taught. Backstage is **read, not installed**: its `yarn tsc` build OOMs at ~4GB and no `--set` fixes it, so the disqualifier is the build, not the runtime — which is itself the lesson about why it does not fit here.

**Rests on** — [the golden path you built](07-a-golden-path-with-no-portal.md), the Flux-reconciled CRD that this reads *against*; and [the drift beat](02-drift-detection-off-by-default.md), because "runs once" versus "converges continuously" is the exact axis this compares on.

**Topology** — **no cluster.** This is a source clone on [`forge`](../../strands/lab-topologies.md#build-guest); [`platform`](../../strands/lab-topologies.md#platform) may be up and idle beside it or torn down — the reading does not touch it.

**Read** — [the module framing](../../phases/12-gitops-platform.md#m12-3) and the question below, against Backstage's actual scaffolder code. Held to [the archaeology drill standard](../../strands/source-archaeology.md#drills): the "runs once" claim resolves to a function a reader can open, not to a blog assertion.

> **Question to answer (from the tools against each other):** a Backstage scaffolder template and a Flux-reconciled CRD both "create an app from a form." One converges continuously and one runs once. Which failure does each hide from the developer, and which does it expose? Name a concrete case where the difference bites — e.g. someone hand-edits the generated `Deployment`: the reconciled CRD corrects it, the scaffolder never sees it was created.

**Do** — clone Backstage on `forge` and read the scaffolder, without building it:

```sh
ssh zain@forge 'git clone --depth 1 https://github.com/backstage/backstage && \
  ls backstage/plugins/scaffolder-backend/src/scaffolder'
# read the task runner: it executes a list of steps once and stops. Find where.
# DO NOT run `yarn install && yarn tsc` — it scaffolds NODE_OPTIONS=--max-old-space-size=8192
# and still OOMs at ~4GB. The build is the disqualifier, not the runtime.
```

**Verify from outside** — the "one-shot" claim is a citation: a reader opens the scaffolder's task-execution path at your stated commit and finds a linear run of steps with no requeue, no watch, no `resourceVersion` — structurally unlike [the P4 loop](../../phases/04-controllers.md#m4-1) every Group A tool is. "Backstage doesn't reconcile" fails the gate; `<file>:<function>@<commit>` passes.

**Expect** — a precise structural contrast, not a preference: the scaffolder is *strictly more* interesting to compare than to install, because its lack of a control loop is the whole point next to Flagger and Flux in the same phase. The golden path you built from a reconciled CRD does something Backstage's scaffolder cannot — notice drift.

**Write down** — the cited scaffolder function proving "runs once," and the concrete case where one-shot-versus-reconciled bites a developer. This feeds [the failure-mode catalogue](09-12c5-the-leak-in-the-golden-path.md) and [the capstone critique](18-the-platform-and-its-critique.md).

**Footprint note** — a source clone on [`forge`](../../strands/lab-topologies.md#build-guest), which is [never part of any topology](../../strands/lab-topologies.md#build-guest); **do not** attempt the Backstage build anywhere — [it exceeds the ceiling on its own](../../research/platform-engineering-footprints.md).

**Teardown** — remove the clone from `forge`. No cluster state was touched. **Whatever topology was idle beside it stays.**
