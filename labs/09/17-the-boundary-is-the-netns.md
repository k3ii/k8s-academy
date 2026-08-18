<a id="the-boundary-is-the-netns"></a>
# `STRICT` protects a network namespace, not a Service: the pod IP is refused and `127.0.0.1` is not

**Claim** — under `STRICT`, a plaintext connection to `httpbin`'s **pod IP** is refused exactly as the ClusterIP was, including from the node itself — so the policy is not a property of the Service. The same request made **from inside the pod's own network namespace to `127.0.0.1`** succeeds in plaintext, because [the redirect is hooked on `PREROUTING`](06-interception-reduced-to-netfilter.md) and loopback traffic never passes it. The mesh's boundary is the netns edge.

**Rests on** — [the `STRICT` policy and the out-of-mesh client](16-strict-and-the-plaintext-refused.md), both left in place by the previous exercise.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Setup**

```sh
POD_IP=$(kubectl -n mesh get pod -l app=httpbin -o jsonpath='{.items[0].status.podIP}')
CLUSTER_IP=$(kubectl -n mesh get svc httpbin -o jsonpath='{.spec.clusterIP}')
echo "pod $POD_IP  service $CLUSTER_IP"
kubectl -n mesh get svc httpbin -o jsonpath='{.spec.ports[0]}'; echo      # 8000 → 80
```

**Do — three probes at three distances, all plaintext, all to the same process:**

```sh
kubectl -n raw exec client -- curl -s -m 5 -o /dev/null -w 'via ClusterIP:  %{http_code}\n' http://$CLUSTER_IP:8000/get
kubectl -n raw exec client -- curl -s -m 5 -o /dev/null -w 'via pod IP:     %{http_code}\n' http://$POD_IP:80/get
ssh zain@10.10.10.131 "curl -s -m 5 -o /dev/null -w 'from the node:  %{http_code}\n' http://$POD_IP:80/get"
```

**Do — the fourth probe, from inside.** Enter the pod's netns on the node and call the application on loopback:

```sh
HPID=$(ssh zain@10.10.10.131 'sudo crictl inspect $(sudo crictl ps -q --label io.kubernetes.container.name=httpbin) | jq -r .info.pid')
ssh zain@10.10.10.131 "sudo nsenter -t $HPID -n curl -s -m 5 -o /dev/null -w 'from inside the netns: %{http_code}\n' http://127.0.0.1:80/get"
ssh zain@10.10.10.131 "sudo nsenter -t $HPID -n iptables -t nat -S ISTIO_OUTPUT | grep 127.0.0.1"
ssh zain@10.10.10.131 "sudo nsenter -t $HPID -n ss -ltn"
```

**Observe — what the server proxy recorded for each of the four:**

```sh
kubectl -n mesh exec deploy/httpbin -c istio-proxy -- pilot-agent request GET stats \
  | grep -E 'no_filter_chain_match|inbound\|8000.*upstream_rq_total|tls_inspector\.tls_not_found'
kubectl -n mesh get pod -l app=httpbin      # still Ready
```

**Expect** — the first three probes to **all fail identically**, and the third to be the one that settles the argument: a request from the node's root namespace to the pod's own IP, with no Service and no `kube-proxy` involved, is refused by the same `no_filter_chain_match`. Whatever chose the destination address, the packet entered the pod's netns through `PREROUTING`, met `ISTIO_INBOUND`, and was redirected to a listener that has no plaintext chain.

Expect the fourth probe to return **200 in plaintext**, and expect the `ISTIO_OUTPUT` rule you just grepped to explain it: traffic destined for `127.0.0.1` is `RETURN`ed, and traffic that never leaves loopback is not seen by `PREROUTING` in the first place. Expect `ss -ltn` to show the application listening on `0.0.0.0:80` — it was never made loopback-only, and nothing about the mesh changed how the application binds.

Expect the server's counters to show **three connections that produced no requests** and **one request that produced no connection through 15006**. Two different ways of being invisible, in one exercise.

**The consequence is the exercise's real output, and it belongs in the notes as a security statement**: everything inside the pod's network namespace is *inside* the mesh boundary and is not authenticated by it. A second container in the same pod reaches the application on loopback with no certificate, no policy and no telemetry — as does any process that can enter that namespace, which on this node is anything with `CAP_SYS_ADMIN` and the pod's PID. `PeerAuthentication` constrains **who may connect from another netns**; it says nothing about who is already in this one. That is the sentence [P10](../../phases/10-security.md) picks up when it asks what a compromised sidecar or a debug container can reach.

**Write down** — in `journal/p9-boundary.md`: the four probes as a table with their results, the loopback `RETURN` rule, and one sentence each on (a) why the pod-IP refusal disproves "mTLS protects Services", and (b) what a second container in `httpbin`'s pod could do. Note the connection to [the UID exemption](07-the-uid-that-breaks-the-loop.md): both are cases where the mesh's guarantees are bounded by a netfilter rule rather than by a policy object, and both are readable in one `iptables -S`.

**Teardown — the out-of-mesh client and its namespace go; the policy stays:**

```sh
kubectl delete namespace raw
kubectl -n mesh get peerauthentication
kubectl -n mesh exec deploy/sleep -c sleep -- curl -s -o /dev/null -w '%{http_code}\n' http://httpbin:8000/get
```

A 200 from inside the mesh confirms `STRICT` is still in force and still working. **`PeerAuthentication` stays** — [the root drill](18-9c2-a-root-that-no-longer-signs.md) needs mTLS to be mandatory, or breaking the trust chain would degrade quietly to plaintext and prove nothing. **The topology stays.**
