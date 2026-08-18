<a id="scaffold-the-same-operator"></a>
# Scaffold the same operator, and change nothing about the test

**Artifact** — build artifact 2: `build/04-operator-kubebuilder/`, a `kubebuilder` project reconciling **the same `Ensemble` CRD to the same behaviour** as [the hand-wired operator](15-the-hand-wired-loop.md), gated by [the same `envtest` file](16-envtest-is-a-real-apiserver.md) copied across **unmodified**. Holding the test fixed is what makes [the diff](33-the-diff.md) a comparison rather than two anecdotes.

**Rests on** — all of [module 4.3](../../phases/04-controllers.md#m4-3). The scaffold is met *after* the hand-wiring on purpose, so `controller-gen`, `Reconcile(ctx, req)` and `zz_generated.deepcopy.go` land as recognition. If any of it still reads as magic, that is a signal to go back to [the hand-wired loop](15-the-hand-wired-loop.md), not to push on.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued, with the build on [`forge`](../../strands/lab-topologies.md#build-guest) as usual.

**Setup — the two operators cannot both run.** They manage the same CRD and would be [4.C3](30-4c3-two-replicas-no-leader-election.md) with extra steps. Before anything else:

```sh
kubectl -n academy-build scale deploy academy-operator --replicas=0
```

Leave the CRD and the existing Ensembles in place. Artifact 2 inheriting artifact 1's live objects is not a complication, it is a free test.

**Build**

```sh
mkdir -p ~/k8s-academy/build/04-operator-kubebuilder && cd $_
kubebuilder init --domain k3ii.dev --repo github.com/k3ii/k8s-academy/build/04-operator-kubebuilder
kubebuilder create api --group academy --version v1alpha1 --kind Ensemble --resource --controller
```

Then five edits, and no more:

1. **Paste the same `EnsembleSpec` and `EnsembleStatus`** from [the type you fixed in exercise 14](14-generate-the-clientset.md) into `api/v1alpha1/ensemble_types.go`, and express the validation as markers instead of hand-written schema — `+kubebuilder:validation:Minimum=1` and `Maximum=8` on `Voices`, `+kubebuilder:subresource:status` and `+kubebuilder:printcolumn` on the type. Note as you type them which hand-written lines each marker is standing in for.
2. **Port the reconcile body** from `pkg/controller/sync.go`. It should port nearly verbatim: it was already a pure function of cluster state keyed by a name, which is the shape `Reconcile(ctx, req)` demands. Anywhere it does *not* port cleanly, write down why — that is a finding about your hand-wired code, not about the framework.
3. **The finalizer, the children and the registry entry** keep the same names and the same semantics. `academy.k3ii.dev/registry-cleanup`, `<name>-voice-N`, the same key in the same namespace. If the names drift, [the drills](25-4c2-a-finalizer-that-never-completes.md) stop being repeatable against this artifact.
4. **The manager's watches**: `Owns(&corev1.ConfigMap{})` for the children, and whatever you need for the registry ConfigMap. Say which hand-wired lines each replaces before you look at the answer in [the diff](33-the-diff.md).
5. **Copy the `envtest` suite in unchanged.** Same file, same four assertions, adjusted only for package and import paths. Changing an assertion to make it pass is the one move that destroys the exercise; if one fails, artifact 2 is wrong.

Generate and run:

```sh
make manifests generate
make install          # applies config/crd/bases/…
make run              # stage 1: the binary runs on forge against the cluster
```

**Gate** — [tier 1](../../strands/build-mechanics.md#gates): `make test`, which is `envtest`, with the file byte-identical to artifact 1's apart from imports. Plus one live check that artifact 2 picked up artifact 1's objects and left them alone: no ConfigMap churn, no `resourceVersion` bump on the existing Ensembles beyond a status write.

**Verify from outside** — the generated CRD against the one you wrote by hand:

```sh
kubectl get crd ensembles.academy.k3ii.dev -o yaml > /tmp/crd-generated.yaml
diff <(yq '.spec.versions[0].schema' /tmp/crd-generated.yaml) <(yq '.spec.versions[0].schema' ~/hand-written-crd.yaml)
```

**Expect** — the operator runs and does nothing, because the world already matches. That is the correct first result and it is worth pausing on: two independently written controllers agreeing on desired state is the level-triggered property, demonstrated by accident.

The CRD diff is where the surprise is. `controller-gen` emits a schema that is stricter than the one you hand-wrote — required fields you left optional, an `x-kubernetes-preserve-unknown-fields` you did or did not think about, and defaults materialised from struct tags. Read every difference and decide in each case which version you would rather ship. Some of the generated strictness is better than what you wrote; at least one thing is not, and finding it is the point of looking.

Two smaller expectations worth stating so they are not mistaken for problems: `make run` takes noticeably longer to start than your `go run` did, because the manager builds a cache and waits for it to sync before starting any controller — [that is `WaitForCacheSync`](12-4c4-act-before-the-cache-is-synced.md), which the framework does not let you forget. And `zz_generated.deepcopy.go` is code you already wrote by hand in [exercise 14](14-generate-the-clientset.md); open both and confirm they are the same shape.

**Write down** — the five markers with the hand-written lines each replaces, the CRD schema diff with a verdict per difference, and the one place your reconcile body did not port cleanly.

**Footprint note** — [the same 564 MiB build shape](../../strands/build-mechanics.md#measurements) as artifact 1, and artifact 1 is scaled to zero, so this is a swap and not an addition. `make test` runs `envtest`, so [the sequential-run constraint from the gate exercise](16-envtest-is-a-real-apiserver.md) applies here too and for the same reason.

**Teardown** — leave `make run` up; [the next exercise](32-the-same-kill-a-different-graceful.md) kills it. **The topology stays.**
