<a id="an-ack-and-a-nack"></a>
# An ACK you can see in a response header, and a NACK that leaves the version exactly where it was

**Claim** — a push Envoy accepts **changes the `version_info` you recorded** and shows up in traffic within seconds; a push Envoy rejects leaves that version **byte-identical**, increments a rejection counter, and does not stop a single request. Two `EnvoyFilter` objects, one valid and one with Lua that will not compile, produce both halves — and `istiod` accepts both, because the thing that validates a filter is the proxy.

**Rests on** — [the dynamic dump](09-the-same-dump-now-dynamic.md) for the versions you are comparing against, and [the four-hop walk](10-one-service-four-resource-types.md) for the listener the filter attaches to.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Setup — record the two versions this exercise is about**, and a baseline response to compare headers against:

```sh
istioctl -n mesh proxy-status
jq -r '[.configs[] | select(."@type"|test("Listeners")) | .dynamic_listeners[].active_state.version_info] | unique' ~/dump-dynamic.json
kubectl -n mesh exec deploy/sleep -c istio-proxy -- pilot-agent request GET stats \
  | grep -E '^listener_manager\.lds\.update_(success|rejected)|^cluster_manager\.cds\.update_(success|rejected)'
kubectl -n mesh exec deploy/sleep -c sleep -- curl -sD- -o /dev/null http://httpbin:8000/get | grep -i '^x-'
```

**Do — part 1, the ACK.** A filter that adds one response header is the smallest change that is visible from inside the data path:

```sh
kubectl apply -f - <<'YAML'
apiVersion: networking.istio.io/v1alpha3
kind: EnvoyFilter
metadata: {name: academy-ack, namespace: mesh}
spec:
  workloadSelector: {labels: {app: sleep}}
  configPatches:
  - applyTo: HTTP_FILTER
    match:
      context: SIDECAR_OUTBOUND
      listener:
        filterChain:
          filter:
            name: envoy.filters.network.http_connection_manager
            subFilter: {name: envoy.filters.http.router}
    patch:
      operation: INSERT_BEFORE
      value:
        name: academy.lua
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.http.lua.v3.Lua
          inlineCode: |
            function envoy_on_response(handle)
              handle:headers():add("x-academy-ack", "1")
            end
YAML
sleep 5
kubectl -n mesh exec deploy/sleep -c sleep -- curl -sD- -o /dev/null http://httpbin:8000/get | grep -i x-academy
kubectl -n mesh exec deploy/sleep -c istio-proxy -- pilot-agent request GET config_dump > ~/dump-ack.json
jq -r '[.configs[] | select(."@type"|test("Listeners")) | .dynamic_listeners[].active_state.version_info] | unique' ~/dump-ack.json
```

**Do — part 2, the NACK.** The same object with the function signature cut off mid-line. `istiod` does not compile Lua; Envoy does:

```sh
kubectl apply -f - <<'YAML'
apiVersion: networking.istio.io/v1alpha3
kind: EnvoyFilter
metadata: {name: academy-nack, namespace: mesh}
spec:
  workloadSelector: {labels: {app: sleep}}
  configPatches:
  - applyTo: HTTP_FILTER
    match:
      context: SIDECAR_OUTBOUND
      listener:
        filterChain:
          filter:
            name: envoy.filters.network.http_connection_manager
            subFilter: {name: envoy.filters.http.router}
    patch:
      operation: INSERT_BEFORE
      value:
        name: academy.broken
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.http.lua.v3.Lua
          inlineCode: |
            function envoy_on_response(handle
YAML
kubectl get envoyfilter -n mesh
sleep 5
```

**Observe — three places the rejection is recorded, and one place it is not:**

```sh
kubectl -n mesh logs deploy/sleep -c istio-proxy --tail=40 | grep -iE 'rejected|nack|gRPC config'
kubectl -n mesh exec deploy/sleep -c istio-proxy -- pilot-agent request GET stats \
  | grep -E '^listener_manager\.lds\.update_(success|rejected)|^listener_manager\.total_listeners'
kubectl -n mesh exec deploy/sleep -c sleep -- curl -s http://istiod.istio-system:15014/metrics | grep -E '^pilot_total_xds_rejects'
istioctl -n mesh proxy-status
kubectl -n mesh exec deploy/sleep -c istio-proxy -- pilot-agent request GET config_dump > ~/dump-nack.json
diff <(jq -S '[.configs[] | select(."@type"|test("Listeners")) | .dynamic_listeners[].active_state.version_info] | unique' ~/dump-ack.json) \
     <(jq -S '[.configs[] | select(."@type"|test("Listeners")) | .dynamic_listeners[].active_state.version_info] | unique' ~/dump-nack.json)
kubectl -n mesh exec deploy/sleep -c sleep -- curl -sD- -o /dev/null -w '%{http_code}\n' http://httpbin:8000/get | grep -i x-academy
```

**Expect** — part 1's header **`x-academy-ack: 1`** on the response, a **new listener `version_info`**, and `listener_manager.lds.update_success` up by one. That is an ACK, and it is worth noting what the ACK itself is: Envoy's next request on the same stream carries the version and nonce it just applied, so **acknowledgement is the absence of an error on the following request**, not a separate message.

Expect part 2 to be accepted by the API server and by `istiod` — `kubectl get envoyfilter` lists both objects, and no admission webhook complains. Expect the rejection at the proxy: **`lds.update_rejected` up by one, `lds.update_success` unchanged**, a log line naming the Lua error, and `pilot_total_xds_rejects` non-zero on `istiod`'s side with the listener type in its label. Expect `istioctl proxy-status` to report the proxy **`STALE`** for listeners while every other type stays `SYNCED` — the granularity of the failure is the resource type.

Expect the `diff` of the version lists to be **empty**, and expect the request to still return 200 **with `x-academy-ack` still on it**. This is the result the whole exercise exists for: Envoy did not roll back to an empty configuration and did not adopt the broken one. It **kept the last state it accepted** — the same property that makes [killing the control plane survivable](14-9c3-istiod-killed-and-the-planes-come-apart.md), observed here without killing anything.

Expect `total_listeners` to be unchanged, and expect the number of *warming* listeners to be the honest place to look if your Envoy version rejects only the affected listener rather than the whole response. Record which behaviour you saw; the counter and the unchanged version are the version-independent facts, the granularity is not.

**Write down** — in `journal/p9-ack-nack.md`: the two versions with the rejection between them, the three rejection observations, and one sentence answering [the module's question](../../phases/09-service-mesh.md#m9-3) — what Envoy sends to ACK, and what happens to the version on a NACK. Then the operational sentence: a NACK is invisible from `kubectl get` alone, so the only place a broken push shows up is the proxy's counters and `proxy-status`. An `EnvoyFilter` that applies cleanly in one cluster and NACKs in another is a normal Tuesday.

**Teardown — both objects, and prove the header is gone.** Leaving `academy-nack` in place would make every later push in this phase land on a stale listener set:

```sh
kubectl -n mesh delete envoyfilter academy-nack academy-ack
sleep 5
kubectl -n mesh exec deploy/sleep -c istio-proxy -- pilot-agent request GET stats | grep -E '^listener_manager\.lds\.update_(success|rejected)'
kubectl -n mesh exec deploy/sleep -c sleep -- curl -sD- -o /dev/null http://httpbin:8000/get | grep -ci x-academy    # 0
istioctl -n mesh proxy-status
rm -f ~/dump-ack.json ~/dump-nack.json
```

`proxy-status` fully `SYNCED` and `update_success` up by one more — the recovery push — is the gate on leaving. `~/dump-dynamic.json` stays; the two temporary dumps go. **The topology stays.**
