<a id="kyverno-on-the-chain-you-already-read"></a>
# Kyverno is two webhooks on the P3 chain: a mutating one adds the default, a validating one checks what the mutating one produced

**Artifact** — a demonstration that a Kyverno `mutate` policy (adding a `seccompProfile` default) and a Kyverno `validate` policy (requiring `runAsNonRoot`) run at the two ends of [the admission chain you already read in P3](../../phases/03-api-machinery.md#m3-2): the mutating webhook fires first and its output is what the validating webhook sees, proven by a pod that is admitted *only because* the mutation ran before the validation. The evidence is the two `MutatingWebhookConfiguration`/`ValidatingWebhookConfiguration` objects Kyverno registered — no new apiserver machinery, the dispatch code is P3's.

**Rests on** — [P3's chain ordering](../../phases/03-api-machinery.md#m3-2) (all-mutating-then-all-validating) — this exercise does not re-establish that ordering, it stands a policy engine on top of it and watches the guarantee hold. [Exercise 6](06-restricted-rejects-a-pod-you-can-name.md) is the built-in comparison; Kyverno is the programmable one.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued. **Kyverno arrives here and stays** for [the supply-chain admission exercise](20-verifyimages-rejects-the-unsigned.md); [the index](README.md) tracks it as the first of three resident tools.

**Read** — [the phase's admission question](../../phases/10-security.md#m10-2): at what point does a Kyverno validating webhook run relative to a mutating one that adds a `securityContext` default. You read the ordering *guarantee* in P3; here confirm Kyverno registers on both sides of it:

```sh
kubectl get mutatingwebhookconfigurations,validatingwebhookconfigurations | grep -i kyverno
```

**Setup — install Kyverno**, limits set explicitly because the node runs near its ceiling later:

```sh
helm repo add kyverno https://kyverno.github.io/kyverno/ && helm repo update
helm install kyverno kyverno/kyverno -n kyverno --create-namespace \
  --set admissionController.replicas=1 --set backgroundController.replicas=1 \
  --set cleanupController.enabled=false --set reportsController.enabled=false
kubectl -n kyverno rollout status deploy/kyverno-admission-controller
```

**Do — a mutate that supplies the default, and a validate that demands the result:**

```sh
kubectl apply -f - <<'YAML'
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata: {name: add-seccomp}
spec:
  rules:
  - name: default-seccomp
    match: {any: [{resources: {kinds: [Pod]}}]}
    mutate:
      patchStrategicMerge:
        spec:
          securityContext:
            seccompProfile: {type: RuntimeDefault}
---
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata: {name: require-nonroot}
spec:
  validationFailureAction: Enforce
  rules:
  - name: check-nonroot
    match: {any: [{resources: {kinds: [Pod]}}]}
    validate:
      message: "runAsNonRoot is required"
      pattern:
        spec:
          =(securityContext):
            runAsNonRoot: true
YAML
```

Create a pod that sets `runAsNonRoot` but *not* `seccompProfile`, then read what was actually stored:

```sh
kubectl create namespace kv
kubectl -n kv apply -f - <<'YAML'
apiVersion: v1
kind: Pod
metadata: {name: p, namespace: kv}
spec:
  securityContext: {runAsNonRoot: true}
  containers: [{name: c, image: nginxinc/nginx-unprivileged:stable}]
YAML
kubectl -n kv get pod p -o jsonpath='{.spec.securityContext}'; echo
```

**Observe** — the stored pod has `seccompProfile: {type: RuntimeDefault}` that you never wrote: the mutating webhook added it. Had the validate run first, a pod missing `runAsNonRoot` would be judged before any mutation could rescue it — but ordering is fixed, so the mutation's output is the validation's input. Two webhook configurations, both pointing at Kyverno, one on each side of the chain.

**Expect** — the mutation to be invisible in your manifest and present in the API object, and the validation to reject a pod with `runAsNonRoot: false` regardless of mutation. **This is the ordering guarantee from P3 doing work you can see** — the reason Kyverno needs no new theory is that it plugs into machinery you already traced.

**Write down** — the two webhook-configuration names, and one sentence: why a validate policy can safely assume defaults a mutate policy supplies. That assumption is exactly what [10.C2](10-10c2-a-policy-that-matches-the-wrong-kind.md) breaks by matching the wrong kind.

**Footprint note** — Kyverno's admission + background controllers at one replica each are **~320Mi** ([the phase's ecosystem note](../../phases/10-security.md#ecosystem)), spent inside the worker. Base 6.5GB → ~6.8GB; [the index](README.md) carries the running total.

**Teardown** — the test namespace goes; **the two policies and Kyverno stay** — [exercise 20](20-verifyimages-rejects-the-unsigned.md) needs the engine:

```sh
kubectl delete namespace kv
```
**The topology stays.**
