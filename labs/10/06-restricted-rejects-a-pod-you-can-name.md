<a id="restricted-rejects-a-pod-you-can-name"></a>
# `restricted` Pod Security Admission names every field a pod is missing before it schedules

**Claim** — a namespace labelled `pod-security.enforce=restricted` refuses a plain `nginx` pod at admission with a message that lists *every* violated control at once — `allowPrivilegeEscalation`, `capabilities` drop, `runAsNonRoot`, `seccompProfile` — and admits the same workload only when all four are set; the identical pod goes into a `privileged`-labelled namespace untouched. PSA is a built-in admission plugin, not a controller, so the rejection happens before the object is stored and there is nothing to clean up.

**Rests on** — [exercise 1](01-one-verb-one-resource.md)'s namespace pattern. This is the PSP-successor [the certs strand records as a CKS-era change](../../strands/certs.md#cks-changes); the fact that it is *the* mechanism now lives there, so this file only produces the rejection.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Read** — the three Pod Security Standards (`privileged`, `baseline`, `restricted`) as [the phase names them](../../phases/10-security.md#m10-2). The reading question worth answering before you apply the label: which two of `restricted`'s controls a typical upstream image (like `nginx`) violates *by default* — the answer is why "just add the labels" breaks real workloads.

**Do — two namespaces, one workload, opposite labels:**

```sh
kubectl create namespace r-strict
kubectl label namespace r-strict \
  pod-security.enforce=restricted pod-security.enforce-version=latest \
  pod-security.warn=restricted
kubectl create namespace r-open
kubectl label namespace r-open pod-security.enforce=privileged

kubectl -n r-open  run web --image=nginx --restart=Never     # admitted, no fuss
kubectl -n r-strict run web --image=nginx --restart=Never    # rejected — read the whole message
```

**Do — satisfy every control the message named:**

```sh
kubectl -n r-strict apply -f - <<'YAML'
apiVersion: v1
kind: Pod
metadata: {name: web, namespace: r-strict}
spec:
  securityContext:
    runAsNonRoot: true
    seccompProfile: {type: RuntimeDefault}
  containers:
  - name: web
    image: nginxinc/nginx-unprivileged:stable
    securityContext:
      allowPrivilegeEscalation: false
      runAsNonRoot: true
      capabilities: {drop: ["ALL"]}
YAML
kubectl -n r-strict get pod web
```

**Observe** — the `nginx` rejection in `r-strict` enumerates all four violated controls in a single admission error; the same command in `r-open` returns a running pod; and the hardened pod (note the *unprivileged* image, because stock `nginx` binds port 80 as root and cannot satisfy `runAsNonRoot`) is admitted. The switch from `nginx` to `nginx-unprivileged` is not incidental — it is the reading question's answer made mechanical: `restricted` is unsatisfiable by an image that needs root.

**Expect** — one admission message carrying every violation rather than one-at-a-time, which is what makes PSA fast to satisfy: you fix the whole list once. **Expect no object to exist after a rejection** — `kubectl -n r-strict get pods` shows nothing from the failed attempt, because PSA runs as validating admission and the pod was never stored. That is the difference between PSA and [the Kyverno policy in the next exercise](07-kyverno-on-the-chain-you-already-read.md), whose scope gaps [10.C2](10-10c2-a-policy-that-matches-the-wrong-kind.md) will exploit.

**Write down** — the four controls the rejection listed, and one sentence on why a namespace can be `restricted` and still run nothing useful if its images assume root.

**Teardown** — both namespaces go; **the topology stays**:

```sh
kubectl delete namespace r-strict r-open
```
