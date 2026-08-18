<a id="one-request-both-halves"></a>
# The capstone: one `GET`, cited from the netfilter rule that captured it to the endpoint IP that answered it

**Artifact** — `journal/p9-capstone.md`: **one specific request** — `sleep` to `httpbin`, `GET /get` — traced end to end, with every claim carrying a re-pullable citation. Two `iptables` rules (the outbound capture at the client and the inbound capture at the server, each mapped to the `istio-init` arg that installed it) and four `jq` paths (listener, route, cluster, endpoint), with the endpoint IP confirmed against the `EndpointSlice`. [The phase's capstone](../../phases/09-service-mesh.md#capstone) demands exactly this, and its standard is that a hostile reader can re-pull each artifact and check each line.

**Rests on** — [the netfilter reading](06-interception-reduced-to-netfilter.md) for the first half and [the four-hop walk](10-one-service-four-resource-types.md) for the second. Everything between them is context; this file is where the two halves are written as one document.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair). **This exercise releases it.**

**Setup — go back to sidecar mode.** The capstone is a sidecar walk: [ambient has no per-pod rules to cite and no per-pod dump](20-a-namespace-with-no-sidecars.md), so the data plane returns to the shape modules 9.2 and 9.3 measured:

```sh
istioctl install -f ~/istiod-academy.yaml -y
kubectl -n istio-system get ds,deploy
kubectl label namespace mesh istio.io/dataplane-mode-
kubectl label namespace mesh istio-injection=enabled
kubectl -n mesh rollout restart deploy httpbin sleep
kubectl -n mesh rollout status deploy httpbin && kubectl -n mesh rollout status deploy sleep
kubectl -n mesh get pods                       # 2/2 again
kubectl -n mesh get peerauthentication         # STRICT still in force
```

**Do — make the request, once, and make it identifiable:**

```sh
kubectl -n mesh exec deploy/sleep -c sleep -- curl -sD- -o /dev/null \
  -H 'x-academy-capstone: 1' http://httpbin:8000/get
```

**Build — the document, in six cited parts.** Each command below produces one citation; paste the command *and* its output into the journal file, because the command is what makes the claim checkable:

```sh
# 1 — outbound capture, at the client pod
SPID=$(ssh zain@10.10.10.131 'sudo crictl inspect $(sudo crictl ps -q --label io.kubernetes.container.name=istio-proxy --label io.kubernetes.pod.name=$(sudo crictl pods -q --name sleep)) | jq -r .info.pid')
ssh zain@10.10.10.131 "sudo nsenter -t $SPID -n iptables -t nat -S ISTIO_OUTPUT | tail -1"
kubectl -n mesh get pod -l app=sleep -o jsonpath='{.items[0].spec.initContainers[0].args}'; echo

# 2 — inbound capture, at the server pod
HPID=$(ssh zain@10.10.10.131 'sudo crictl inspect $(sudo crictl ps -q --label io.kubernetes.container.name=istio-proxy --label io.kubernetes.pod.name=$(sudo crictl pods -q --name httpbin)) | jq -r .info.pid')
ssh zain@10.10.10.131 "sudo nsenter -t $HPID -n iptables -t nat -S ISTIO_INBOUND"
ssh zain@10.10.10.131 "sudo nsenter -t $HPID -n iptables -t nat -S ISTIO_IN_REDIRECT"

# 3-6 — the four hops, from a dump pulled after the request
kubectl -n mesh exec deploy/sleep -c istio-proxy -- pilot-agent request GET config_dump > ~/dump-capstone.json
jq -r '.configs[] | select(."@type"|test("Listeners")) | .dynamic_listeners[] | select(.name=="0.0.0.0_8000") | .name' ~/dump-capstone.json
jq -r '.configs[] | select(."@type"|test("Routes")) | .dynamic_route_configs[] | select(.route_config.name=="8000")
       | .route_config.virtual_hosts[] | select(.name|test("httpbin")) | {domains, cluster: .routes[0].route.cluster}' ~/dump-capstone.json
jq -r '.configs[] | select(."@type"|test("Clusters")) | .dynamic_active_clusters[]
       | select(.cluster.name=="outbound|8000||httpbin.mesh.svc.cluster.local") | {name: .cluster.name, type: .cluster.type}' ~/dump-capstone.json
jq -r '.configs[] | select(."@type"|test("Endpoints")) | .dynamic_endpoint_configs[]
       | select(.endpoint_config.cluster_name=="outbound|8000||httpbin.mesh.svc.cluster.local")
       | .endpoint_config.endpoints[].lb_endpoints[].endpoint.address.socket_address' ~/dump-capstone.json
kubectl -n mesh get endpointslice -l kubernetes.io/service-name=httpbin -o json \
  | jq -c '.items[] | {endpoints: [.endpoints[].addresses[0]], ports: [.ports[].port]}'
```

**Verify from outside** — the check a hostile reader would run. Re-pull everything from scratch and confirm each citation still resolves; a dump path that only worked against the file open in your editor is not a citation:

```sh
kubectl -n mesh exec deploy/sleep -c istio-proxy -- pilot-agent request GET config_dump > ~/dump-recheck.json
# re-run each of the four jq lines above against ~/dump-recheck.json; each must print the same resource name
diff <(jq -S '.configs[] | select(."@type"|test("Clusters")) | [.dynamic_active_clusters[].cluster.name] | sort' ~/dump-capstone.json) \
     <(jq -S '.configs[] | select(."@type"|test("Clusters")) | [.dynamic_active_clusters[].cluster.name] | sort' ~/dump-recheck.json)
kubectl -n mesh exec deploy/httpbin -c istio-proxy -- pilot-agent request GET stats | grep -E 'inbound\|8000.*upstream_rq_total'
```

**Expect** — the outbound chain's **last rule to be the catch-all jump to `ISTIO_REDIRECT`** and that chain's `REDIRECT --to-ports 15001` to be what captured the packet leaving `sleep`; the inbound chain's catch-all jump to `ISTIO_IN_REDIRECT` and its `REDIRECT --to-ports 15006` to be what captured the same packet arriving at `httpbin`. **One request, captured twice, by two rules in two network namespaces** — say that explicitly in the document, because a walk that mentions only one half describes a mesh that does not exist.

Expect the four hops to resolve exactly as they did in [module 9.3](10-one-service-four-resource-types.md), and expect the endpoint address to be **the pod IP on port 80** while the cluster is named for port 8000 — the same mismatch, and by now you can say which object performed the translation and which Kubernetes resource carried it.

Expect the `diff` between the two dumps to be **empty**, and treat a non-empty one as a finding rather than an error: something pushed between the two pulls, and [the push counters](12-a-scale-event-is-one-resource-type.md) will name the resource type.

**Gate** — [the phase's gate](../../phases/09-service-mesh.md#gate) has three items, and this document plus your journal answers all three: the request walked end to end with citations; `istiod` killed with the two planes separated ([9.C3](14-9c3-istiod-killed-and-the-planes-come-apart.md)); and mTLS proven at the identity layer, with the SPIFFE SAN decoded ([exercise 15](15-a-certificate-that-names-a-serviceaccount.md)) and plaintext rejected at the Envoy layer ([exercise 16](16-strict-and-the-plaintext-refused.md)). Before tearing anything down, re-read the gate and check that each claim in your notes has an artifact behind it — after the teardown below, none of it can be re-pulled.

**Write down** — `journal/p9-capstone.md` as described, and then the closing statement [the gate also asks for](../../phases/09-service-mesh.md#gate): what this phase did **not** teach. Be concrete rather than modest. Name the components you did not touch — the scheduler, the controller manager, the kubelet's pod lifecycle, etcd — and name the one interface where the mesh did reach into Kubernetes proper: [the mutating webhook that rewrote a pod at admission](05-a-pod-the-webhook-rewrote.md), and the `EndpointSlice` watch that fed EDS. Two touchpoints, both of them ordinary API machinery from [P3](../../phases/03-api-machinery.md) and [P4](../../phases/04-controllers.md). That is the honest measure of how much of Kubernetes a service mesh is.

**Teardown — the phase ends here, and the topology goes.** Copy anything you still want out of the guests **before** running the destroy; it is not recoverable afterwards:

```sh
scp zain@10.10.10.130:~/dump-dynamic.json zain@10.10.10.130:~/istiod-academy.yaml ~/p9-artifacts/
scp zain@10.10.10.130:~/chains-permissive.json zain@10.10.10.130:~/chains-strict.json ~/p9-artifacts/
ssh hopper
cd factory
just tofu labs destroy
```

**Everything installed in this phase goes with the cluster** — `istiod`, both DaemonSets from the ambient run, the Gateway API CRDs, the `mesh` namespace and every certificate in it. Nothing needs uninstalling first, and nothing from this phase is carried into [P10](../../phases/10-security.md), which provisions its own topology.

On `forge`, three things remain and are worth one deliberate decision each: `~/envoy-academy/` (the static config and its dump — keep; it is the smallest complete Envoy you will ever have), the downloaded Istio release (delete; the next one will be a different version), and [the Linkerd clone](24-linkerd-read-and-never-installed.md) (already deleted in its own teardown — confirm).

```sh
ssh zain@10.10.10.125 'ls ~/envoy-academy/; rm -rf ~/istio-*; ls ~/src/ 2>/dev/null'
```

**The topology is released. The phase is over.**
