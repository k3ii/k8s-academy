<a id="which-object-owns-the-failure"></a>
# Kill one upstream: the listener still reports a successful accept, and the fix belongs to the cluster

**Claim** — with one endpoint dead, **the listener's accept counter keeps climbing and only cluster counters record the failure** — so the listener terminates the downstream connection and the cluster picks the upstream, which is [the module's reading question](../../phases/09-service-mesh.md#m9-1) answered by experiment rather than by the docs. The repair is an **active health check**, a property of the cluster, and it fixes the 503s without one character changing in the listener.

**Rests on** — [the config you typed](01-four-objects-in-a-file-you-typed.md) and [its static dump](02-a-dump-with-nothing-pushed-into-it.md).

**Topology** — **none.** [`forge`](../../strands/lab-topologies.md#build-guest) only.

**Setup** — both upstreams and the proxy up, as before, and confirm round robin is working before you break it:

```sh
for i in 1 2; do curl -s localhost:10000/; done      # up1 up2
```

**Do — part 1, kill the second endpoint.** Envoy is not told, and nothing reconfigures it:

```sh
pkill -f 'http.server 8082'
for i in 1 2 3 4 5 6; do curl -s -o /dev/null -w '%{http_code} ' localhost:10000/; done; echo
curl -s localhost:10000/ | head -1
```

**Observe — which counters moved.** This is the whole exercise; read them before drawing any conclusion:

```sh
curl -s localhost:9901/stats | grep -E 'listener\.0\.0\.0\.0_10000\.(downstream_cx_total|downstream_cx_destroy)'
curl -s localhost:9901/stats | grep -E 'cluster\.academy_upstream\.(upstream_rq_total|upstream_rq_5xx|upstream_cx_connect_fail)'
curl -s localhost:9901/clusters | grep 8082
```

**Do — part 2, fix it at the right layer.** Copy the config and add a health check to the **cluster**, changing nothing else:

```sh
cp ~/envoy-academy/envoy.yaml ~/envoy-academy/envoy-hc.yaml
cat >> ~/envoy-academy/envoy-hc.yaml <<'YAML'
    health_checks:
    - timeout: 1s
      interval: 2s
      unhealthy_threshold: 2
      healthy_threshold: 1
      http_health_check: { path: "/index.html" }
YAML
docker rm -f academy-envoy
docker run -d --name academy-envoy --network host \
  -v ~/envoy-academy/envoy-hc.yaml:/etc/envoy.yaml:ro \
  --entrypoint /usr/local/bin/envoy \
  docker.io/istio/proxyv2:<ISTIO_VERSION> -c /etc/envoy.yaml -l info
sleep 6
for i in 1 2 3 4 5 6; do curl -s localhost:10000/; done
curl -s localhost:9901/clusters | grep 8082
```

**Do — part 3, the number the diagram needs.** How many threads is this one process running, and when was that decided?

```sh
curl -s localhost:9901/server_info | jq '{concurrency, state, hot_restart_version}'
nproc
docker rm -f academy-envoy
docker run -d --name academy-envoy --network host \
  -v ~/envoy-academy/envoy-hc.yaml:/etc/envoy.yaml:ro \
  --entrypoint /usr/local/bin/envoy \
  docker.io/istio/proxyv2:<ISTIO_VERSION> -c /etc/envoy.yaml -l info --concurrency 1
curl -s localhost:9901/server_info | jq .concurrency
curl -s 'localhost:9901/stats?filter=worker'
```

**Expect** — in part 1, **six 503s with `upstream connect error or disconnect/reset before headers`**, `upstream_cx_connect_fail` climbing on the cluster, and — the point — `listener.0.0.0.0_10000.downstream_cx_total` climbing by six as well. From the listener's side nothing went wrong: it accepted a connection, ran its filter chain, and handed the request to a router filter that had nowhere to put it. Expect `/clusters` to still list `8082` as a member, because with no health checking configured **Envoy's only evidence that an endpoint is dead is a failed connection**, discovered per request.

Expect part 2 to return `up1` six times out of six, and `/clusters` to show `8082` carrying `health_flags::/failed_active_hc`. Nothing about the listener, the filter chain or the route changed. **Load balancing, outlier state and health are cluster-level concepts** — which is why module 9.3's `CDS` and `EDS` are two resource types and not one, and why a retry policy will turn out to be a *route* property rather than a cluster one.

Expect `concurrency` to equal `nproc` — **2 on `forge`** — and to be fixed at startup, unchangeable without a restart. Expect the `worker` stats filter to be nearly empty in a default build: the workers exist, but Envoy does not by default tell you which one served a given connection. Say that in the write-up rather than inventing an observation, and carry the number forward as a question: **a sidecar in module 9.2 is one Envoy process per pod with its own `concurrency`** — compare that number against the pod's CPU allocation when you have one to look at, because a worker per core per pod is where "a mesh costs a core per busy sidecar" comes from.

**Write down** — [objective 1's four-object diagram](../../phases/09-service-mesh.md#objectives) in `journal/p9-envoy-objects.md`, annotated with (a) which object terminated the downstream connection, (b) which object chose the upstream and by what policy, (c) which counters proved (a) and (b), and (d) the worker count with the honest note about what the admin interface does and does not expose about threads.

**Teardown**

```sh
docker rm -f academy-envoy
pkill -f 'http.server 808'
rm -f ~/envoy-academy/envoy-hc.yaml
docker ps | grep envoy       # nothing
ss -ltn | grep -E ':(10000|9901|8081|8082)'
```

Keep `envoy.yaml` and `dump-static.json`. **No topology to release** — the cluster is provisioned in [the install that will not schedule](04-the-request-that-does-not-fit.md), which is the next exercise and the first one that costs RAM.
