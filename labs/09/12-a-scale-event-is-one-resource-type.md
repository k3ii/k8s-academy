<a id="a-scale-event-is-one-resource-type"></a>
# Scale a Deployment and only EDS moves; create a Service and four types move

**Claim** — scaling `httpbin` from 1 to 3 replicas increments **`pilot_xds_pushes{type="eds"}` and nothing else**, while creating one new Service increments the listener, route and cluster counters as well. The four xDS types are not four names for one push; they have different change rates, and that is the entire reason the protocol splits them.

**Rests on** — [the four-hop walk](10-one-service-four-resource-types.md) for the cluster whose endpoint list you are about to change, and [the ACK and the NACK](11-an-ack-and-a-nack.md) for what a push counter means.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Setup — reach `istiod`'s own metrics from inside the mesh.** Port 15014 is a Service port on `istiod`, so a pod with `curl` is the whole tooling requirement, and the reason [the telemetry stack was declined](04-the-request-that-does-not-fit.md) is visible in this one line:

```sh
kubectl -n mesh exec deploy/sleep -c sleep -- curl -s http://istiod.istio-system:15014/metrics \
  | grep -E '^pilot_xds_pushes' | tee ~/pushes-before.txt
istioctl -n mesh proxy-config endpoints deploy/sleep --cluster 'outbound|8000||httpbin.mesh.svc.cluster.local'
kubectl -n mesh get endpointslice -l kubernetes.io/service-name=httpbin -o jsonpath='{.items[*].endpoints[*].addresses[*]}'; echo
```

**Do — part 1, a scale event:**

```sh
kubectl -n mesh scale deploy httpbin --replicas=3
kubectl -n mesh rollout status deploy httpbin
sleep 5
kubectl -n mesh exec deploy/sleep -c sleep -- curl -s http://istiod.istio-system:15014/metrics \
  | grep -E '^pilot_xds_pushes' | tee ~/pushes-after-scale.txt
diff ~/pushes-before.txt ~/pushes-after-scale.txt
istioctl -n mesh proxy-config endpoints deploy/sleep --cluster 'outbound|8000||httpbin.mesh.svc.cluster.local'
kubectl -n mesh get endpointslice -l kubernetes.io/service-name=httpbin -o jsonpath='{.items[*].endpoints[*].addresses[*]}'; echo
```

**Do — part 2, a new Service.** No new pods, no new image, nothing running behind it — a Service with a selector that matches nothing at all:

```sh
kubectl -n mesh create service clusterip academy-nothing --tcp=9999:9999
kubectl -n mesh get svc academy-nothing -o jsonpath='{.spec.selector}{"\n"}'
sleep 5
kubectl -n mesh exec deploy/sleep -c sleep -- curl -s http://istiod.istio-system:15014/metrics \
  | grep -E '^pilot_xds_pushes' | tee ~/pushes-after-svc.txt
diff ~/pushes-after-scale.txt ~/pushes-after-svc.txt
istioctl -n mesh proxy-config listeners deploy/sleep --port 9999
istioctl -n mesh proxy-config cluster deploy/sleep --fqdn academy-nothing.mesh.svc.cluster.local
istioctl -n mesh proxy-config endpoints deploy/sleep --cluster 'outbound|9999||academy-nothing.mesh.svc.cluster.local'
```

**Observe — how long convergence took, from the pusher's side:**

```sh
kubectl -n mesh exec deploy/sleep -c sleep -- curl -s http://istiod.istio-system:15014/metrics \
  | grep -E '^pilot_proxy_convergence_time_bucket|^pilot_xds\{|^pilot_xds_push_time_bucket' | head -20
```

**Expect** — part 1's `diff` to show **`eds` climbing and `cds`, `lds` and `rds` standing still**, and the endpoint list going from one IP to three while the cluster itself is untouched. The cluster was already `EDS`-typed with a name that mentions no addresses, so adding endpoints is not a change to it. Expect the three IPs to match the `EndpointSlice` exactly — and expect one of the three to be on the same node and two of them to be as well, because [the control plane is tainted](04-the-request-that-does-not-fit.md) and all three replicas are on the worker.

Expect part 2 to push **`lds`, `rds` and `cds`**, and to produce a listener, a route and a cluster for a Service with **no endpoints and no pods**. Expect `proxy-config endpoints` for it to be empty. This is the shape of the sidecar's cost: a proxy is configured for the services that *exist*, not for the ones it calls, so a namespace full of unused Services is per-pod memory in every sidecar in the mesh. Note the number — this one Service added three resources to `sleep`'s configuration, and `sleep` will never talk to it.

Expect `eds` to move in part 2 as well, possibly. Do not treat that as a contradiction: `istiod` recomputes and pushes endpoints for a service set that has changed shape, and the claim being tested is the asymmetry — **a scale event is one type, a new Service is several** — not that any single counter is frozen. Write the actual deltas down rather than a summary of them.

Expect `pilot_proxy_convergence_time` to be a histogram with almost everything in its lowest bucket for a mesh of two proxies, and expect that to be the most misleading number in the phase: convergence time is a function of proxy count and push size, and this lab has [two proxies and a 512Mi `istiod`](04-the-request-that-does-not-fit.md). It is the right *metric* to watch and the wrong *value* to remember.

**Write down** — in `journal/p9-push-types.md`: the two `diff` outputs, the endpoint list before and after, and one sentence on why splitting endpoints from clusters is the difference between "a pod moved" costing a small delta push and costing a full listener rebuild. Note also where the endpoint data came from: `istiod` watched `EndpointSlice`, the object [P7](../../phases/07-networking.md) watched `kube-proxy` consume. **Two independent readers of one data structure, converging on the same three IPs by completely different mechanisms** — that sentence is the whole justification for this phase sitting after P7.

**Teardown — both changes, in the order that keeps the next exercise's arithmetic intact:**

```sh
kubectl -n mesh delete svc academy-nothing
kubectl -n mesh scale deploy httpbin --replicas=1
kubectl -n mesh rollout status deploy httpbin
istioctl -n mesh proxy-config endpoints deploy/sleep --cluster 'outbound|8000||httpbin.mesh.svc.cluster.local'
istioctl -n mesh proxy-config listeners deploy/sleep --port 9999      # gone
rm -f ~/pushes-before.txt ~/pushes-after-scale.txt ~/pushes-after-svc.txt
```

**Scale back to 1 before moving on.** Three sidecars is 180Mi rather than 60Mi on [a worker with 1948Mi](04-the-request-that-does-not-fit.md), and [the cost curve exercise](19-what-a-sidecar-costs.md) measures exactly this scaling deliberately and needs to start from one. **The topology stays.**
