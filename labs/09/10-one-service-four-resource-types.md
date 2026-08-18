<a id="one-service-four-resource-types"></a>
# One Service, four resource types: walk LDS→RDS→CDS→EDS and land on a port the Service does not advertise

**Claim** — one `Service` becomes **four separately versioned resources** in the sidecar, and following them from the listener to the endpoint IPs ends on the pod's **container port, not the Service port** — which proves the last hop is `EndpointSlice` data and not a copy of the Service object. This is [module 9.3's chain](../../phases/09-service-mesh.md#m9-3) and the second half of [the capstone](25-one-request-both-halves.md).

**Rests on** — [the dynamic dump](09-the-same-dump-now-dynamic.md). Every command below has a `jq` equivalent against `~/dump-dynamic.json`, and the exercise is only finished when you have both — `istioctl` for reading and a JSON path for citing.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Setup — the Service as Kubernetes sees it**, so that the mesh's version can be checked against something:

```sh
kubectl -n mesh get svc httpbin -o jsonpath='{.spec.ports}'; echo
kubectl -n mesh get endpointslice -l kubernetes.io/service-name=httpbin \
  -o jsonpath='{.items[*].endpoints[*].addresses[*]} {.items[*].ports[*].port}'; echo
```

**Do — the four hops, in order, from the client's proxy.** `sleep` is the client, so this is `sleep`'s configuration; `httpbin`'s proxy has a mirror-image inbound view and is not what you want here:

```sh
istioctl -n mesh proxy-config listeners deploy/sleep --port 8000
istioctl -n mesh proxy-config routes deploy/sleep --name 8000 -o json | jq '.[0].virtualHosts[] | {name, domains, routes: [.routes[].route.cluster]}'
istioctl -n mesh proxy-config cluster deploy/sleep --fqdn httpbin.mesh.svc.cluster.local --port 8000
istioctl -n mesh proxy-config endpoints deploy/sleep --cluster 'outbound|8000||httpbin.mesh.svc.cluster.local'
```

**Do — the same four hops as citable JSON paths.** [The capstone demands a re-pullable citation](../../phases/09-service-mesh.md#capstone), and `istioctl`'s tables are not one:

```sh
jq -r '.configs[] | select(."@type"|test("Listeners")) | .dynamic_listeners[] | select(.name=="0.0.0.0_8000") | .name' ~/dump-dynamic.json
jq -r '.configs[] | select(."@type"|test("Routes")) | .dynamic_route_configs[]
       | select(.route_config.name=="8000") | .route_config.virtual_hosts[].routes[].route.cluster' ~/dump-dynamic.json
jq -r '.configs[] | select(."@type"|test("Clusters")) | .dynamic_active_clusters[]
       | select(.cluster.name|test("httpbin")) | {name: .cluster.name, type: .cluster.type, eds: .cluster.eds_cluster_config}' ~/dump-dynamic.json
jq -r '.configs[] | select(."@type"|test("Endpoints")) | .dynamic_endpoint_configs[]
       | select(.endpoint_config.cluster_name|test("httpbin"))
       | .endpoint_config.endpoints[].lb_endpoints[].endpoint.address.socket_address' ~/dump-dynamic.json
```

**Observe — the listener nobody routes through, and the one that does the work:**

```sh
istioctl -n mesh proxy-config listeners deploy/sleep | head -20
jq -r '.configs[] | select(."@type"|test("Listeners")) | .dynamic_listeners[]
       | select(.name|test("virtualOutbound")) | .active_state.listener
       | {address: .address.socket_address, use_original_dst: .use_original_dst, filters: [.listener_filters[].name]}' ~/dump-dynamic.json
```

**Expect** — a listener named **`0.0.0.0_8000`**, bound to `0.0.0.0` rather than to `httpbin`'s ClusterIP, and expect that to be the right design once you have read [the redirect rule](06-interception-reduced-to-netfilter.md): the packet arrives at port **15001** with its original destination recorded by netfilter, so the only listener holding a socket is `virtualOutbound`, and `0.0.0.0_8000` is selected by **original destination** rather than by having been listened on. Two consequences worth writing down: `ss -ltn` inside the pod will not show a socket on 8000, and a Service on a port no listener matches falls through to a passthrough or blackhole cluster instead of failing loudly.

Expect the route config named `8000` to hold a virtual host whose `domains` include `httpbin`, `httpbin.mesh`, `httpbin.mesh.svc.cluster.local` and the ClusterIP — **the same service under every name a client might use** — routing to a cluster named `outbound|8000||httpbin.mesh.svc.cluster.local`. Expect that name to be a four-field key of direction, port, subset and FQDN, and expect the empty third field to be the reason a `DestinationRule` subset can appear there without changing anything else in the chain.

Expect the cluster's type to be **`EDS`** with an `eds_cluster_config` naming the ADS source, not a list of hosts. Then expect the endpoints to be **the pod IPs on port 80** while the cluster is named for port **8000**. This is the exercise's claim: the mapping from 8000 to 80 was done by Kubernetes and written into an `EndpointSlice`, and `istiod` read that object — the same data structure [P7](../../phases/07-networking.md) watched `kube-proxy` consume, now consumed by a second reader that turns it into EDS instead of into `nat` rules. Compare the IP list with the `EndpointSlice` above; they must match exactly, and if they do not, one of the two readers is stale and [the push counters](12-a-scale-event-is-one-resource-type.md) will say which.

**Write down** — the four resource names, each with the `jq` path that produced it, in `journal/p9-xds-chain.md`, plus the endpoint IP:port and the `EndpointSlice` line it matches. That file **is** the capstone's second half; write it as though a hostile reader will re-pull the dump and check every path, because that is exactly [the standard the phase inherits](../../strands/source-archaeology.md#drills).

**Teardown** — nothing created; all four commands are reads. Keep `~/dump-dynamic.json` and `journal/p9-xds-chain.md`.

**The topology stays.**
