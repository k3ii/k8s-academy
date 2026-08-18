<a id="strict-and-the-plaintext-refused"></a>
# `STRICT` deletes the plaintext filter chain: the refusal happens before any HTTP exists to refuse

**Claim** — switching `PeerAuthentication` to `STRICT` **removes filter chains from the inbound listener** rather than adding a rule to reject anything. A plaintext client is then refused by `no_filter_chain_match` on port 15006 — a listener-level event with no request, no response and no status code — which is what "read the rejection at the Envoy layer" means and why the client's `connection reset` tells you nothing about the cause.

**Rests on** — [the identity certificate](15-a-certificate-that-names-a-serviceaccount.md) for what the surviving chain requires, and [the netfilter reading](06-interception-reduced-to-netfilter.md) for why port 15006 is where inbound arrives.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Setup — a client that is genuinely outside the mesh**, in a namespace with no injection label, plus the before-state of the listener you are about to change:

```sh
kubectl create namespace raw
kubectl -n raw get namespace raw --show-labels
kubectl -n raw run client --image=curlimages/curl --restart=Never -- sleep 3600
kubectl -n raw get pod client -o jsonpath='{.spec.containers[*].name}'; echo      # one container
istioctl -n mesh proxy-config listener deploy/httpbin --port 15006 -o json \
  | jq -r '.[0].filterChains[].filterChainMatch | {transportProtocol, applicationProtocols, destinationPort}' | tee ~/chains-permissive.json
kubectl -n raw exec client -- curl -s -o /dev/null -w '%{http_code}\n' http://httpbin.mesh:8000/get
```

**Do — turn the namespace `STRICT`:**

```sh
kubectl apply -f - <<'YAML'
apiVersion: security.istio.io/v1
kind: PeerAuthentication
metadata: {name: default, namespace: mesh}
spec:
  mtls: {mode: STRICT}
YAML
sleep 5
istioctl -n mesh proxy-config listener deploy/httpbin --port 15006 -o json \
  | jq -r '.[0].filterChains[].filterChainMatch | {transportProtocol, applicationProtocols, destinationPort}' | tee ~/chains-strict.json
diff ~/chains-permissive.json ~/chains-strict.json
```

**Observe — the refusal, from four vantage points.** The client's view is the least informative and is taken first so that the contrast lands:

```sh
kubectl -n raw exec client -- curl -sv -m 5 -o /dev/null http://httpbin.mesh:8000/get 2>&1 | tail -5
istioctl -n mesh proxy-config log deploy/httpbin --level filter:debug,conn_handler:debug
kubectl -n mesh exec deploy/httpbin -c istio-proxy -- pilot-agent request GET stats \
  | grep -E 'no_filter_chain_match|tls_inspector\.(tls_found|tls_not_found)|downstream_cx_total'
kubectl -n mesh logs deploy/httpbin -c istio-proxy --tail=30 | grep -iE 'closing|filter chain|tls'
kubectl -n mesh exec deploy/sleep -c sleep -- curl -s -o /dev/null -w '%{http_code}\n' http://httpbin:8000/get
```

**Expect** — the `diff` to **lose chains, not gain them**. In the permissive state the 15006 listener carries chains matching `transportProtocol: "raw_buffer"` alongside chains matching `"tls"`; under `STRICT` the `raw_buffer` chains are gone. Nothing in the listener says "reject plaintext" — plaintext simply matches nothing, and Envoy closes a connection it has no chain for. Record both JSON files; that pair is the exercise's evidence.

Expect `tls_inspector.tls_not_found` to increment for the plaintext attempt and `listener.0.0.0.0_15006.no_filter_chain_match` to increment with it. The order matters and is worth writing down: a **listener filter** peeked at the first bytes, classified the connection as non-TLS, and the chain matcher then found nothing to hand it to. The connection died **before any HTTP filter ran**, which is why there is no 403, no 503 and no access-log line of the usual shape.

Expect the client to see a **reset or an empty reply**, with no explanation whatsoever. Say plainly in the notes why: a proxy that answered "your connection was rejected because it lacked a client certificate" would be answering an unauthenticated peer. **The silence is the design**, and it is also why the only way to debug this is from the server's proxy — the vantage point you just used.

Expect `sleep`'s request to still return **200**. It presented a certificate, matched the `tls` chain, and never noticed the policy changed. Expect the pod to stay **Ready** as well — the kubelet's probe goes to 15021, [a port `ISTIO_INBOUND` returns rather than redirects](06-interception-reduced-to-netfilter.md), so it never meets the mTLS requirement at all.

**Expect one thing that ought to worry you**: re-read [9.C1](08-9c1-a-port-outside-the-mesh.md). A port excluded from redirection is not covered by this policy either, because the policy is enforced by a proxy that the packet never reaches. `PeerAuthentication: STRICT` is a statement about **traffic that arrives at Envoy**, not about traffic that arrives at the pod. Verify it if you want the point to stick — re-apply the exclusion annotation, curl from `client` again, and then remove it.

**Write down** — in `journal/p9-strict.md`: the two filter-chain listings with the `diff` between them, the two counters, and one sentence distinguishing "plaintext is rejected" from "plaintext cannot be routed anywhere". Add the caveat sentence about excluded ports — a security control whose scope is defined by an `iptables` rule is worth stating precisely once.

**Teardown — the policy stays, the client goes.** [The next exercise](17-the-boundary-is-the-netns.md) needs `STRICT` in place and needs a client outside the mesh, so the only thing removed here is the debug log level, which is expensive and easy to forget:

```sh
istioctl -n mesh proxy-config log deploy/httpbin --level info
kubectl -n mesh exec deploy/httpbin -c istio-proxy -- pilot-agent request GET stats | grep -c no_filter_chain_match
kubectl -n mesh get peerauthentication
```

**`PeerAuthentication` and the `raw` namespace both stay** — [the netns-boundary exercise](17-the-boundary-is-the-netns.md) is the next file and uses both. Keep `~/chains-permissive.json` and `~/chains-strict.json`. **The topology stays.**
