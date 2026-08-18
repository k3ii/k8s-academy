<a id="the-waypoint-l7-policy-needs"></a>
# Write an L7 authorization rule with no L7 proxy in the path, then add the one Envoy the namespace needs

**Claim** — an `AuthorizationPolicy` whose rule names an **HTTP method** cannot be enforced by `ztunnel`, which sees a TCP stream and an identity. Deploying a **waypoint** — one Envoy for the whole namespace, not one per pod — makes the same policy enforceable, and the 403 it produces is readable in the waypoint's own RBAC counters.

**Rests on** — [the ambient switch](20-a-namespace-with-no-sidecars.md), whose two-column table has an empty cell this exercise fills, and [the identity certificate](15-a-certificate-that-names-a-serviceaccount.md) for the principal the policy is written against.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Setup — the Gateway API CRDs, which a waypoint is an instance of.** Record the version the way [the Istio version was recorded](01-four-objects-in-a-file-you-typed.md); Istio's release notes for your version name the channel and release it expects:

```sh
kubectl get crd gateways.gateway.networking.k8s.io 2>/dev/null || \
  kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/<GATEWAY_API_VERSION>/standard-install.yaml
kubectl get crd | grep gateway.networking.k8s.io
kubectl -n mesh exec deploy/sleep -c sleep -- curl -s -o /dev/null -w 'GET  %{http_code}\n' http://httpbin:8000/get
kubectl -n mesh exec deploy/sleep -c sleep -- curl -s -o /dev/null -w 'POST %{http_code}\n' -X POST http://httpbin:8000/post
```

**Do — part 1, the policy with nothing to enforce it:**

```sh
kubectl apply -f - <<'YAML'
apiVersion: security.istio.io/v1
kind: AuthorizationPolicy
metadata: {name: get-only, namespace: mesh}
spec:
  selector: {matchLabels: {app: httpbin}}
  action: ALLOW
  rules:
  - from: [{source: {principals: ["cluster.local/ns/mesh/sa/sleep"]}}]
    to: [{operation: {methods: ["GET"]}}]
YAML
sleep 5
kubectl -n mesh exec deploy/sleep -c sleep -- curl -s -o /dev/null -w 'GET  %{http_code}\n' http://httpbin:8000/get
kubectl -n mesh exec deploy/sleep -c sleep -- curl -s -o /dev/null -w 'POST %{http_code}\n' -X POST http://httpbin:8000/post
istioctl ztunnel-config policy -n mesh 2>/dev/null || kubectl -n istio-system logs ds/ztunnel --tail=20
```

**Do — part 2, add the waypoint:**

```sh
istioctl waypoint apply -n mesh --enroll-namespace --wait
kubectl -n mesh get gateway
kubectl -n mesh get pods -o wide
kubectl -n mesh get namespace mesh --show-labels
sleep 5
kubectl -n mesh exec deploy/sleep -c sleep -- curl -s -o /dev/null -w 'GET  %{http_code}\n' http://httpbin:8000/get
kubectl -n mesh exec deploy/sleep -c sleep -- curl -s -o /dev/null -w 'POST %{http_code}\n' -X POST http://httpbin:8000/post
```

**Observe — the waypoint is an Envoy, and everything you learned in module 9.3 applies to it:**

```sh
WP=$(kubectl -n mesh get pod -l gateway.networking.k8s.io/gateway-name=waypoint -o jsonpath='{.items[0].metadata.name}')
kubectl -n mesh exec $WP -- pilot-agent request GET stats | grep -E 'rbac\.(allowed|denied)'
istioctl -n mesh proxy-config listener $WP -o json | jq -r '.[].filterChains[].filters[].name' | sort -u
kubectl -n mesh logs $WP --tail=20
kubectl -n mesh get pods -l app=httpbin -o jsonpath='{.items[0].spec.containers[*].name}'; echo    # still 1/1
```

**Expect** — part 1's outcome to be **one of two things, and which one it is matters more than which one you guessed**. Either the L7 clause is silently unenforceable and the POST succeeds, or the implementation fails closed and denies traffic it cannot evaluate. Record what your version did, with the evidence, and write one sentence on the operational consequence of each: a policy that fails open is a security hole nobody is alerted to; a policy that fails closed is an outage on a config change. There is no third option that is quietly correct, which is the argument for the waypoint being explicit rather than automatic.

Expect part 2 to produce **one waypoint pod for the whole namespace**, a `Gateway` object with `gatewayClassName: istio-waypoint`, and a namespace label pointing traffic at it. Expect `GET` 200 and `POST` **403**, and expect the 403 to be attributable: `rbac.denied` on the waypoint's counters, an `envoy.filters.http.rbac` filter in its listener, and a log line naming the request. Expect the workload pods to still be **`1/1`** — the L7 proxy is in the path without being in the pod.

Expect the waypoint to cost roughly what **one sidecar** cost in [the cost curve](19-what-a-sidecar-costs.md), and expect that to be the entire point of the ratio: one Envoy per namespace serving eight pods rather than eight Envoys. Measure it rather than assuming — `mem` from that exercise still works — and add the figure to `journal/p9-sidecar-cost.md` as the third column the table has been missing.

**Write down** — in `journal/p9-ambient.md`: part 1's outcome with its evidence, the `Gateway` object, the waypoint's memory, the `rbac.denied` counter, and the completed two-column table from [the ambient exercise](20-a-namespace-with-no-sidecars.md) with its last row filled in. Then one sentence answering [the module's question](../../phases/09-service-mesh.md#m9-5): what a waypoint is *for* — which is not "L7" in the abstract, but "the place a policy that reads HTTP can be evaluated, sized per namespace instead of per pod".

**Teardown — the waypoint and the policy stay**; [the next exercise](23-the-waypoint-removed-and-the-silence.md) removes the waypoint deliberately and needs the policy in place to observe what happens to it. Confirm the state you are leaving:

```sh
kubectl -n mesh get gateway,authorizationpolicy
kubectl -n mesh get pods
```

**The topology stays.**
