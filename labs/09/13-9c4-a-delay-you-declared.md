<a id="9c4-a-delay-you-declared"></a>
# 9.C4 — the fault filter was already in the chain; the `VirtualService` only filled in its per-route config

**Artifact** — drill [9.C4](../../phases/09-service-mesh.md#chaos): a five-second delay injected into `httpbin` by a `VirtualService`, produced with **no chaos tooling installed**, together with the two `jq` paths that prove where it lives — `envoy.filters.http.fault` in the HTTP filter chain **before** you declared anything, and a `typed_per_filter_config` on one route **after**.

**Rests on** — [the four-hop walk](10-one-service-four-resource-types.md) for the route the config attaches to. Mechanism is **mesh-native**, and [the phase's drill table](../../phases/09-service-mesh.md#chaos) says why: the proxy under study is also the fault injector, so reaching for an external tool here would hide the object being taught.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Setup — find the filter before there is any fault.** This is the observation the drill turns on, so it is taken first:

```sh
kubectl -n mesh exec deploy/sleep -c istio-proxy -- pilot-agent request GET config_dump > ~/dump-prefault.json
jq -r '.configs[] | select(."@type"|test("Listeners")) | .dynamic_listeners[]
       | select(.name=="0.0.0.0_8000") | .active_state.listener.filter_chains[].filters[]
       | select(.name|test("http_connection_manager")) | .typed_config.http_filters[].name' ~/dump-prefault.json
for i in 1 2 3; do kubectl -n mesh exec deploy/sleep -c sleep -- \
  curl -s -o /dev/null -w '%{time_total}\n' http://httpbin:8000/get; done
```

**Do — declare the fault.** One object, no installation, no privileged container, nothing scheduled:

```sh
kubectl apply -f - <<'YAML'
apiVersion: networking.istio.io/v1
kind: VirtualService
metadata: {name: httpbin-fault, namespace: mesh}
spec:
  hosts: [httpbin]
  http:
  - fault:
      delay:
        percentage: {value: 100}
        fixedDelay: 5s
    route:
    - destination: {host: httpbin, port: {number: 8000}}
YAML
sleep 5
for i in 1 2 3; do kubectl -n mesh exec deploy/sleep -c sleep -- \
  curl -s -o /dev/null -w '%{time_total}\n' http://httpbin:8000/get; done
```

**Observe — where the declaration landed, and what counted it:**

```sh
kubectl -n mesh exec deploy/sleep -c istio-proxy -- pilot-agent request GET config_dump > ~/dump-fault.json
jq -r '.configs[] | select(."@type"|test("Routes")) | .dynamic_route_configs[]
       | select(.route_config.name=="8000") | .route_config.virtual_hosts[]
       | select(.name|test("httpbin")) | .routes[].typed_per_filter_config' ~/dump-fault.json
kubectl -n mesh exec deploy/sleep -c istio-proxy -- pilot-agent request GET stats | grep -E '\.fault\.'
diff <(jq -S '[.configs[] | select(."@type"|test("Listeners")) | .dynamic_listeners[].active_state.version_info]|unique' ~/dump-prefault.json) \
     <(jq -S '[.configs[] | select(."@type"|test("Listeners")) | .dynamic_listeners[].active_state.version_info]|unique' ~/dump-fault.json)
kubectl -n mesh exec deploy/httpbin -c istio-proxy -- pilot-agent request GET stats | grep -E 'inbound\|8000.*upstream_rq_total'
```

**Expect** — `envoy.filters.http.fault` in the filter list **before the `VirtualService` existed**, sitting near the front of the chain with the router filter at the end. Every sidecar in every Istio mesh ships with a fault injector already compiled in and already wired into every HTTP listener; what a `VirtualService` supplies is configuration for it on one route. That is the drill's whole content, and it is why this fault costs **zero additional memory** while [Chaos Mesh would have cost 582Mi](../../strands/chaos.md#install).

Expect the three timings to go from milliseconds to **just over five seconds**, and `http.<stat_prefix>.fault.delays_injected` to be **3**. Expect `aborts_injected` to exist and be zero — the same filter does both, which is why the abort variant needs no new object type either.

Expect the route's `typed_per_filter_config` to be keyed by the filter name, with the delay as a `fixed_delay` of `5s` and a percentage of 100. Cite it by `jq` path; it is a re-pullable citation of exactly [the kind the capstone demands](../../phases/09-service-mesh.md#capstone).

Expect the **listener versions to change**, because a route change is an RDS push and the listener that references it is re-sent — check this rather than assuming it, and note which resource types moved against [the push counters exercise](12-a-scale-event-is-one-resource-type.md).

Expect **`httpbin`'s inbound counters to rise normally**. The delay was injected by the **client's** proxy, so the server saw an ordinary request five seconds late and has no idea anything was wrong. Write that down: in a mesh, a latency fault is applied wherever the policy attaches, and a server-side dashboard will show a perfectly healthy service while every client times out.

**Write down** — in `journal/p9-9c4.md`: the filter chain listing from *before*, the `typed_per_filter_config` from *after*, the three timings, the `delays_injected` counter, and one sentence naming what would have to be true for this fault to be invisible to you — which is exactly the situation [9.C1](08-9c1-a-port-outside-the-mesh.md) created by taking a port out of the mesh.

**Teardown — the object, and a timing that proves it is gone:**

```sh
kubectl -n mesh delete virtualservice httpbin-fault
sleep 5
for i in 1 2 3; do kubectl -n mesh exec deploy/sleep -c sleep -- \
  curl -s -o /dev/null -w '%{time_total}\n' http://httpbin:8000/get; done
kubectl -n mesh get virtualservice
rm -f ~/dump-prefault.json ~/dump-fault.json
```

Milliseconds again, and no `VirtualService` left in the namespace. **A five-second delay left in place would be misread as a broken mTLS handshake for the whole of the next module.** **The topology stays.**
