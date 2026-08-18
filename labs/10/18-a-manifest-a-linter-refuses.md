<a id="a-manifest-a-linter-refuses"></a>
# A manifest that applies cleanly to the cluster and fails a linter before it ever gets there

**Artifact** — one Deployment YAML that `kubectl apply` accepts without complaint, and the `kubesec` score plus the `kube-linter` finding list that both reject it — each naming a specific field (`runAsNonRoot` unset, no resource limits, `allowPrivilegeEscalation` not false, capabilities not dropped). Static analysis is the control that runs *left of admission*: it catches in CI what PSA and Kyverno would catch at the door, but before the image is ever pushed, when fixing it is a one-line edit rather than a rejected deploy.

**Rests on** — [the PSA `restricted` controls from exercise 6](06-restricted-rejects-a-pod-you-can-name.md): a linter checks the same properties `restricted` enforces, so the findings here are the admission failures of exercise 6 predicted statically. The two tools police one policy at two different times.

**Topology** — **none.** `kubesec` and `kube-linter` are single binaries on [`hopper`](../../strands/lab-topologies.md#build-guest) reading a YAML file; no cluster. Footprint zero, per [the index](README.md).

**Read** — [kube-linter's check list](https://docs.kubelinter.io/#/generated/checks): each check is a named rule (`no-read-only-root-fs`, `unset-cpu-requirements`, `run-as-non-root`) with a rationale. The question to answer: *which of a linter's findings are also enforced by PSA `restricted`, and which are not* — because the gap (e.g. missing resource limits, which `restricted` does *not* require) is exactly why static analysis is not redundant with admission control.

**Do** — write a plausible-but-unhardened Deployment, apply it (to prove it is admissible), then lint it:

```sh
ssh zain@hopper
cat > deploy.yaml <<'YAML'
apiVersion: apps/v1
kind: Deployment
metadata: {name: web}
spec:
  replicas: 1
  selector: {matchLabels: {app: web}}
  template:
    metadata: {labels: {app: web}}
    spec:
      containers:
      - name: web
        image: nginx:1.27
        ports: [{containerPort: 80}]
YAML
kubesec scan deploy.yaml | jq '.[0].score, .[0].scoring.advise[].reason'
kube-linter lint deploy.yaml
```

**Observe** — `kubectl apply --dry-run=server -f deploy.yaml` in a *default* namespace succeeds (the API server has no objection); `kubesec` returns a low or negative score with an `advise` list, and `kube-linter` prints a findings block naming `run-as-non-root`, `unset-cpu-requirements`, `unset-memory-requirements`, `no-read-only-root-filesystem` and more. Now cross-reference: `run-as-non-root` and privilege-escalation findings are *also* what [exercise 6](06-restricted-rejects-a-pod-you-can-name.md)'s `restricted` PSA blocks — but the resource-limit findings are *not* enforced by PSA at all. That gap is the answer to the reading question and the reason this control exists separately: a manifest can pass every admission webhook and still be the one that OOM-kills a node, and only the linter flags it, in CI, for free.

**Expect** — admissible YAML, a failing lint. Fix the manifest (add the securityContext block and resource limits from exercise 6's `nginx-unprivileged` pattern) and re-lint until both tools are quiet — that clean pass is the artifact.

**Write down** — the kubesec score before and after, and one kube-linter finding that PSA `restricted` would *not* have caught.

**Teardown** — files on `hopper`:

```sh
ssh zain@hopper 'rm -f ~/deploy.yaml'
```
