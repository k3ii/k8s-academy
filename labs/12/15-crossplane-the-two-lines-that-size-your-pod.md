<a id="crossplane-the-two-lines-that-size-your-pod"></a>
# Crossplane v2: the `mode` enum with one value, the empty `DeploymentRuntimeConfig` that makes your function pod BestEffort, and the override that fixes it

**Artifact** — a Crossplane v2 Composition that provisions native Kubernetes children with **no cloud provider** (v2 composes core resources directly), plus two cited `file:line`s at a pinned tag: the Composition `mode` enum proving it has exactly one value (`Pipeline`) and that `Resources` is *absent from the schema, not deprecated*; and the default `DeploymentRuntimeConfig` proving its spec is empty — the line that makes your function pod land BestEffort with `resources: {}`. Then the mandatory `DeploymentRuntimeConfig` override that sizes it — [`build-mechanics#sizing`](../../strands/build-mechanics.md#sizing) applied to the platform *you* are building. The platform has a pod-sizing problem of its own, and that is the phase's thesis in miniature.

**Rests on** — [KRO's bare mechanism](14-kro-custom-resource-in-children-out.md), the contrast that makes Crossplane's extra machinery legible; [P8's discipline of seeing what an abstraction costs its consumer](../../phases/08-storage.md#m8-1); and [the build-track sizing rule](../../strands/build-mechanics.md#sizing), which the phase's Build-track line points straight at your own function pods.

**Topology** — [`platform`](../../strands/lab-topologies.md#platform), continued.

**Read** — [the module framing](../../phases/12-gitops-platform.md#m12-5) and the source question below, and [the stale-levers note](../../phases/12-gitops-platform.md#ecosystem): `mode: Resources` is a lever older material recommends that no longer exists. Held to [the archaeology standard](../../strands/source-archaeology.md#drills) — cite the tool's own Go, and [live-verify, because it moves](../../strands/source-archaeology.md#stale-paths).

> **Question to answer from the source:** in Crossplane at its pinned tag, the Composition `mode` enum — enumerate its values (there is one) and confirm `Resources` is **absent from the schema**, not deprecated. Then find where the default `DeploymentRuntimeConfig` is created and show its spec is empty — the line that makes your function pod BestEffort. Cite both. *The platform you build has the pod-sizing problem you spent [P8](../../phases/08-storage.md) learning to see.*

**Build** — install Crossplane, a function, and a Composition that emits native children; observe the function pod ship `resources: {}`; then fix it:

```sh
helm install crossplane crossplane-stable/crossplane -n crossplane-system --create-namespace
kubectl apply -f function-patch-and-transform.yaml   # functions are mandatory now
kubectl apply -f webapp-xrd.yaml -f webapp-composition.yaml   # mode: Pipeline — the only value
# the hazard, before the fix:
kubectl get pod -n crossplane-system -l pkg.crossplane.io/function -o \
  jsonpath='{.items[0].spec.containers[0].resources}{"\n"}'   # {} — BestEffort, no request, no limit
# the mandatory override:
kubectl apply -f - <<'YAML'
apiVersion: pkg.crossplane.io/v1beta1
kind: DeploymentRuntimeConfig
metadata: {name: sized}
spec:
  deploymentTemplate:
    spec:
      template:
        spec:
          containers:
          - name: package-runtime
            resources: {requests: {memory: 128Mi}, limits: {memory: 256Mi}}
YAML
```

**Verify from outside** — both mechanism claims are `file:line` a reader clones and opens: the `mode` enum with one entry, and the empty default runtime config. "Crossplane composes it" fails the gate; `<file>:<line>@<tag>` for each passes. The `resources: {}` on the function pod is a live `jsonpath` output, not an assertion — and the override changing it to a sized pod is the fix, checkable the same way.

**Expect** — a Composition provisioning native children with no provider, a function pod that ships unbounded until you size it, and two citations a hostile reader can verify. The `DeploymentRuntimeConfig` override is non-optional on this node — [12.C4](17-12c4-the-function-pod-with-no-limits.md) is what happens without it.

**Write down** — the two cited Crossplane lines (the `mode` enum, the empty runtime config) and the override that sized the function pod. Combined with [the KRO baseline](14-kro-custom-resource-in-children-out.md): what the extra machinery buys, and what it costs.

**Footprint note** — Crossplane core is [3 pods, ~384Mi](../../research/platform-engineering-footprints.md) plus one function pod that is BestEffort until sized — the exact hazard class that [ruled out Argo CD](../../research/platform-engineering-footprints.md), now on a pod you cannot avoid. On [the single `platform` node](../../strands/lab-topologies.md#platform) the override is mandatory.

**Teardown** — keep the XRD, Composition and a `DeploymentRuntimeConfig` for [the Helm contrast](16-helm-cannot-publish-an-api.md) and [the capstone](18-the-platform-and-its-critique.md); [12.C4](17-12c4-the-function-pod-with-no-limits.md) deliberately removes the override next, so note its current state. **The topology stays.**
