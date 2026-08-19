<a id="kro-custom-resource-in-children-out"></a>
# KRO first: a `ResourceGraphDefinition` in, child resources out, with nothing in the way — one pod, 128Mi, no packages, no functions, no providers

**Artifact** — a working KRO `ResourceGraphDefinition` that a developer consumes by creating one instance of a new kind, and that emits child resources (a `Deployment`, a `Service`) — the bare shape "custom resource → controller → children" with **no packages, no functions, no providers, no revisions, no OCI protocol** between the CR and its children. KRO is taught *first* deliberately: it shows the mechanism naked, so that [Crossplane's extra machinery](15-crossplane-the-two-lines-that-size-your-pod.md) arrives with a reason to exist rather than as unexplained ceremony.

**Rests on** — [P4's CRD-plus-controller](../../phases/04-controllers.md#m4-1), which is exactly what a `ResourceGraphDefinition` compiles down to; and [the tenancy boundary](11-a-tenancy-boundary-and-where-it-leaks.md), the namespace this provisions into.

**Topology** — [`platform`](../../strands/lab-topologies.md#platform), continued — Group B.

**Read** — [the module framing](../../phases/12-gitops-platform.md#m12-5) and [the maturity note](../../phases/12-gitops-platform.md#ecosystem): KRO has **no CNCF tier of its own** (a Kubernetes SIG subproject, `v0.9.x`, `v1alpha1`, its central CRD recently renamed from `ResourceGroup` to `ResourceGraphDefinition`). It is a contrast exercise, not a production vehicle — which is exactly the role the numbers give it.

**Build** — install KRO, define a graph, and consume it as a developer would:

```sh
helm install kro oci://ghcr.io/kro-run/kro/kro --namespace kro --create-namespace
kubectl top pod -n kro     # 1 pod, ~128Mi — the whole install
# define a new kind whose instance emits a Deployment + Service:
kubectl apply -f webapp-rgd.yaml     # ResourceGraphDefinition: schema in, child template out
# the developer's whole action — one instance of the new kind:
kubectl apply -f - <<'YAML'
apiVersion: kro.run/v1alpha1
kind: WebApp
metadata: {name: shop, namespace: team-a}
spec: {image: shop:2.1, replicas: 2}
YAML
kubectl get deploy,svc -n team-a -l kro.run/owned    # children, emitted by KRO
```

**Verify from outside** — the "nothing in the way" claim is checkable by absence: `kubectl get pods -n kro` is one pod, there is no function pod, no provider pod, no package revision object anywhere. A reader looking for the machinery Crossplane needs finds none of it — that emptiness is the artifact, and it is what makes the [Crossplane](15-crossplane-the-two-lines-that-size-your-pod.md) contrast land.

**Expect** — a developer creating one `WebApp` and getting a `Deployment` and `Service`, with a single 128Mi controller and zero supporting machinery. This is "custom resource in, children out" with the mechanism visible and nothing hiding it.

**Write down** — the KRO half of the KRO-vs-Crossplane contrast: what the graph did, and the count of supporting pods (zero beyond the one controller) — the baseline against which Crossplane's cost is measured next.

**Footprint note** — KRO is [1 pod, 128Mi](../../research/platform-engineering-footprints.md), the cheapest platform API in the phase; [`platform`](../../strands/lab-topologies.md#platform) barely moves.

**Teardown** — keep the `WebApp` instance and KRO for the [contrast in the next exercise](15-crossplane-the-two-lines-that-size-your-pod.md); delete nothing yet. **The topology stays.**
