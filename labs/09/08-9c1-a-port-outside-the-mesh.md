<a id="9c1-a-port-outside-the-mesh"></a>
# 9.C1 — exclude one port from redirection and watch the identity header disappear

**Artifact** — drill [9.C1](../../phases/09-service-mesh.md#chaos): the same request served twice, **once through the mesh and once around it**, with the `RETURN` rule that let it past pasted beside the two responses. The evidence that the second request left the mesh is not that it failed — it succeeds — but that the **`X-Forwarded-Client-Cert` header is gone from it**, because no proxy on the receiving side was there to attest who called.

**Rests on** — [the netfilter reading](06-interception-reduced-to-netfilter.md) for the chain being edited, and [the injected workloads](05-a-pod-the-webhook-rewrote.md) for something to call. Mechanism is **by hand**, as [the phase's drill table](../../phases/09-service-mesh.md#chaos) specifies: reading the missing rule is the lesson, and a tool that injected the fault would be one more thing between you and it.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Setup — the through-the-mesh baseline, kept.** `httpbin` echoes the request headers back, which makes the mesh's own additions readable without any telemetry stack:

```sh
kubectl -n mesh exec deploy/sleep -c sleep -- curl -s http://httpbin:8000/get \
  | jq -r '.headers | keys[]' | tee /tmp/headers-inside-mesh.txt
kubectl -n mesh exec deploy/httpbin -c istio-proxy -- pilot-agent request GET stats \
  | grep -E 'inbound\|8000.*(upstream_rq_total|downstream_cx_total)'
```

**Do — exclude the port, declaratively.** The annotation goes on the pod template, so this is one patch and one rollout:

```sh
kubectl -n mesh patch deploy httpbin --type=merge -p \
  '{"spec":{"template":{"metadata":{"annotations":{"traffic.sidecar.istio.io/excludeInboundPorts":"8000"}}}}}'
kubectl -n mesh rollout status deploy httpbin
kubectl -n mesh get pod -l app=httpbin -o jsonpath='{.items[0].spec.initContainers[0].args}'; echo
```

**Observe — the rule, then the request.** The rule first: the arg you just changed should have produced exactly one new line in a chain you can name from the previous exercise:

```sh
HPID=$(ssh zain@10.10.10.131 'sudo crictl inspect $(sudo crictl ps -q --label io.kubernetes.container.name=istio-proxy | head -1) | jq -r .info.pid')
ssh zain@10.10.10.131 "sudo nsenter -t $HPID -n iptables -t nat -S ISTIO_INBOUND"
kubectl -n mesh exec deploy/sleep -c sleep -- curl -s http://httpbin:8000/get \
  | jq -r '.headers | keys[]' | tee /tmp/headers-outside-mesh.txt
diff /tmp/headers-inside-mesh.txt /tmp/headers-outside-mesh.txt
kubectl -n mesh exec deploy/httpbin -c istio-proxy -- pilot-agent request GET stats \
  | grep -E 'inbound\|8000.*(upstream_rq_total|downstream_cx_total)'
```

**Expect** — the request to **still return 200**, and that is the point of the drill: nothing looks broken. Expect one added `RETURN` for `--dport 8000` in `ISTIO_INBOUND`, sitting with the proxy's own exempt ports, and expect it to be the *same shape* of rule as the ones for 15021 and 15090 — the mesh has no separate concept of "excluded"; a port is outside the mesh exactly when a `RETURN` precedes the redirect.

Expect the `diff` to lose **`X-Forwarded-Client-Cert`**, and expect that to be the single most informative line of output in the phase so far. That header is written by the *receiving* proxy from the peer certificate of the mTLS connection it terminated; with the port excluded there was no receiving proxy, no mTLS, and therefore no attestation. Expect `X-Request-Id` and the `X-Envoy-*` headers added by the **client's** proxy to survive, because the client side was never touched — which means a response that still carries `X-Envoy-Attempt-Count` is not evidence that the request went through the mesh. Half a mesh looks like a mesh from the client's side.

Expect `httpbin`'s `inbound|8000` counters to be **flat across the second request**. Two facts that should sit uncomfortably together in the notes: the traffic was not counted, and nothing anywhere reported an error. **A mesh's telemetry cannot see the traffic that bypassed its interception**, so the absence of a metric is not the absence of traffic — it is the shape this failure takes in every dashboard you would build on top of it.

**Verify from outside** — the control plane's opinion of a pod it can no longer see the traffic of:

```sh
kubectl -n mesh get pod -l app=httpbin
istioctl -n mesh proxy-status
```

Both healthy, both synced. The pod is a full mesh member with a hole in it, and no object in the API says so except the annotation you wrote.

**Write down** — the `RETURN` rule, the header `diff`, and the flat counters, in `journal/p9-9c1.md`. Then the deliverable sentence: what policy would have been enforced on this port and now is not — `PeerAuthentication`, authorization, retries, timeouts, and every metric — all of it configured over xDS to a proxy the packet never reached. Keep this file; [the `STRICT` exercise](16-strict-and-the-plaintext-refused.md) re-runs the same request under a policy that is supposed to make plaintext impossible, and this is the exception that will still get through.

**Teardown — remove the annotation and prove the header is back**, because a silently excluded port would make the mTLS module measure nothing:

```sh
kubectl -n mesh patch deploy httpbin --type=json \
  -p '[{"op":"remove","path":"/spec/template/metadata/annotations/traffic.sidecar.istio.io~1excludeInboundPorts"}]'
kubectl -n mesh rollout status deploy httpbin
kubectl -n mesh exec deploy/sleep -c sleep -- curl -s http://httpbin:8000/get \
  | jq -r '.headers | keys[]' | grep -i forwarded-client-cert
rm -f /tmp/headers-inside-mesh.txt /tmp/headers-outside-mesh.txt
```

**The topology stays.** No tool was installed for this drill and none is left behind.
