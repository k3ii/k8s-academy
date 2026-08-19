<a id="gitops-the-reconcile-loop-you-already-wrote"></a>
# A change reaches the cluster with no `kubectl apply`: `commit → Source → Kustomization/HelmRelease → applied`, and the chart pulled from a git revision with no registry

**Artifact** — the delivery path `git commit → GitRepository Source → Kustomization` (and a parallel `HelmRelease`) `→ applied`, each arrow a thing you watched happen, with the reconcile interval read off the object's status; plus one cited line proving the `HelmRelease`'s chart came from a `GitRepository` and not a registry — so the isolated bridge needs no `oci://` endpoint at all. Nothing here is new machinery: this is [the P4 reconcile loop you hand-wrote](../../phases/04-controllers.md#m4-1), with a git `Source` bolted on the front.

**Rests on** — [P4's controller](../../phases/04-controllers.md#m4-1) — Flux *is* that loop, so if "watch → diff → act" is not already reflex, Flux reads as magic; and [the module framing](../../phases/12-gitops-platform.md#m12-1), which is where the *why* lives.

**Topology** — [`platform`](../../strands/lab-topologies.md#platform) comes up here — the phase's single node, added [for P12 specifically](../../research/platform-engineering-footprints.md) and **not a replay** of any earlier topology. Provision it [the standard way](../../strands/lab-topologies.md#provision) with `topology=platform`; it stays up through all of Group A.

**Read** — [the module framing](../../phases/12-gitops-platform.md#m12-1) and its source question below. The mechanics of a reconcile loop are [P4's](../../phases/04-controllers.md#m4-1) and are **not restated here**. Platform tooling moves fast, so [live-verify every path before trusting it](../../strands/source-archaeology.md#stale-paths).

> **Question to answer from the source:** `HelmChart.spec.sourceRef.kind` accepts `GitRepository` in source-controller's kubebuilder enum — cite the line, and state why that means **no chart registry is needed** on an isolated bridge: for a git source the chart version is ignored and the git revision *is* the version. This is the fact that lets a bare git repo on the Proxmox host be a complete chart-delivery path.

**Setup — measure the empty node first.** The phase's first lab step, and the number the [two-group budget](README.md) rests on:

```sh
kubectl top pod -A          # baseline: what the bare cluster costs before you add a platform
kubectl top node
```

Write that baseline down — every install below is measured against it, and the reason the phase runs as [two groups with a teardown between](../../phases/12-gitops-platform.md#ecosystem) is that this baseline plus both groups at once is unmeasured and unwise.

**Build** — install Flux, point a `GitRepository` at a repo holding a Kustomize app and a Helm chart, and watch the handoff:

```sh
flux install
# a git Source, reconciled on an interval you can read back:
flux create source git demo --url=<repo-url> --branch=main --interval=1m
flux create kustomization demo --source=GitRepository/demo --path=./app --prune=true --interval=1m
kubectl -n flux-system get gitrepository,kustomization -o wide
# the HelmRelease whose chart comes from the same git source, no registry:
kubectl -n flux-system get helmrelease,helmchart
kubectl -n flux-system get helmchart -o jsonpath='{.items[0].spec.sourceRef.kind}{"\n"}'   # GitRepository
```

**Verify from outside** — a reader clones source-controller at your stated tag and opens the `sourceRef.kind` enum: `GitRepository` is one of the accepted kinds, and the git-source path treats the revision as the version. "Flux can use git for charts" fails the gate; `<file>:<line>@<tag>` passes. The `HelmChart` object above, reporting `GitRepository` as its source kind, is the same fact seen from the cluster.

**Expect** — a commit to the repo becoming an applied change on the cluster with no `kubectl apply` in the loop, the `Kustomization` and `HelmRelease` reporting `Ready` with a `lastAppliedRevision`, and the reconcile interval visible in status. The chart resolved from git, not from any registry.

**Write down** — the `commit → Source → Kustomization/HelmRelease → applied` path with the reconcile-interval line and the cited `sourceRef.kind` enum line; and the empty-node baseline from Setup.

**Footprint note** — [`platform` at 6.0GB](../../strands/lab-topologies.md#platform), inside [the 9.5GB ceiling](../../strands/lab-topologies.md#ceiling); Flux is four controllers at [256Mi requested / <150Mi measured idle each](../../research/platform-engineering-footprints.md), the cheapest thing Group A installs.

**Teardown** — Flux and the git Source **stay**: [the drift beat](02-drift-detection-off-by-default.md), [the secrets exercise](04-three-ways-to-not-commit-a-secret.md) and every Group A exercise build on this install. **The topology stays.** Only the demo app is torn down, and only [at the group boundary](10-the-teardown-that-proves-git.md), where its return from git is the test.
