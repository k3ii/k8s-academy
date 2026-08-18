<a id="10c2-a-policy-that-matches-the-wrong-kind"></a>
# 10.C2 — a policy that admits every Deployment while rejecting every bare Pod, and the one word that explains it

**Claim** — a Kyverno validate policy scoped to `kind: Pod` refuses a bare `kubectl run` root pod but *admits* a `Deployment` whose pod template is equally root — and the Deployment's pods then come up unhardened. The bug is not the rule; the rule is correct. The bug is *what the rule was pointed at*: a Deployment is not a Pod, its pods are born from a template the API server expands *after* admission on the Deployment has already passed. This is the single most common self-inflicted policy gap in the field, and 10.C2 is designed to let you cause it, observe it, and name it.

**Rests on** — [exercise 7](07-kyverno-on-the-chain-you-already-read.md) installed Kyverno and put policies on the chain; this drill breaks one of those policies in the specific way a hurried author does, so it depends on Kyverno already running from that exercise.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued. Kyverno is still installed from [exercise 7](07-kyverno-on-the-chain-you-already-read.md).

**Read** — [Kyverno's `match` semantics](https://kyverno.io/docs/writing-policies/match-exclude/): a rule fires only when the *admission request's* `kind` is in the match block. Then read one thing about the API server: [how a Deployment's pods are created](../../phases/04-controllers.md#m4-1) — the controller manager writes Pods from the template in a *separate* API call, which is its own admission request. Hold the question: *if a policy matches only `Pod`, whose admission request carries the Deployment's template — and has that request happened yet when the Deployment is admitted?*

**Do** — write a policy that matches only `Pod`, then test it against both shapes:

```sh
kubectl apply -f - <<'YAML'
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata: {name: require-nonroot}
spec:
  validationFailureAction: Enforce
  rules:
  - name: nonroot
    match:
      any:
      - resources: {kinds: [Pod]}
    validate:
      message: "runAsNonRoot must be true"
      pattern:
        spec:
          =(securityContext):
            runAsNonRoot: true
YAML
kubectl create namespace c2
# a bare root pod — the request's kind IS Pod
kubectl -n c2 run rootpod --image=nginx --restart=Never
# a Deployment whose template is equally root — the request's kind is Deployment
kubectl -n c2 create deployment rootdeploy --image=nginx
kubectl -n c2 get pods -l app=rootdeploy
```

**Observe** — the bare `run` is refused with the policy message; the `create deployment` *succeeds*, and its pod appears and runs. The pod was equally root, but the admission request that Kyverno saw for it never carried `kind: Pod` from a user — it carried `kind: Deployment`, which the rule did not match. When the controller manager later POSTs the actual Pod, that request *is* `kind: Pod` and *is* matched — so confirm which way your Kyverno version fell: some versions' pod-controller auto-generation catches this, others do not, and **which behaviour you got is the thing to record, not to assume**. Run `kubectl -n c2 describe pod -l app=rootdeploy | grep -A3 Events` and look for a Kyverno rejection event on the generated pod; its presence or absence is the whole finding.

**Expect** — either the Deployment's pods run root (no auto-generated pod rule fired) or they are blocked at the controller's create call with a Kyverno event naming the same rule. The lesson is identical in both outcomes: **a policy author who tests only with `kubectl run` never sees which of these they have.** The fix is to add the pod-controller kinds — `Deployment`, `StatefulSet`, `DaemonSet`, `Job`, `CronJob` — to the match block, or to rely on Kyverno's autogen (which writes those rules for you) and to *verify it did* rather than trust it.

**Write down** — which outcome your cluster produced, and the one-word name for the gap: the policy matched a *kind*, not a *workload*.

**Teardown** — the namespace and the policy go; Kyverno stays for [exercise 20](20-verifyimages-rejects-the-unsigned.md); **the topology stays**:

```sh
kubectl delete namespace c2
kubectl delete clusterpolicy require-nonroot
```
