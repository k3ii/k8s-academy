<a id="four-objects-in-a-file-you-typed"></a>
# The four objects, in a config file you typed, with no mesh anywhere

**Artifact** — a **static** Envoy on [`forge`](../../strands/lab-topologies.md#build-guest) that you configured by hand: one listener, one filter chain, one route, one cluster, two endpoints, proxying to two upstreams you can tell apart. The four objects [the module names](../../phases/09-service-mesh.md#m9-1) exist in this file because you typed them, which is the only reason the dump in module 9.3 will be readable.

**Rests on** — nothing in this phase. It deliberately precedes every Kubernetes step: an object model learned from a live mesh is learned from 400 KB of JSON that something else generated, and there is no way to tell which parts are Envoy and which parts are Istio.

**Topology** — **none.** This runs entirely on [`forge`](../../strands/lab-topologies.md#build-guest); no cluster is provisioned until [the install that will not schedule](04-the-request-that-does-not-fit.md).

**Setup** — the Istio release, on `forge`, because it carries `istioctl` *and* names the proxy image you are about to run:

```sh
ssh zain@10.10.10.125
curl -L https://istio.io/downloadIstio | sh -
cd istio-*/ && export PATH=$PWD/bin:$PATH
istioctl version --remote=false
```

**Record that version string now.** Every image tag, flag name and CRD version in this phase is that release's, and the one hard requirement is **ambient mode GA — Istio 1.24 or later**. `ISTIO_VERSION` below is what `istioctl version --remote=false` printed.

Two upstreams that are trivially distinguishable, because an endpoint you cannot identify proves nothing about load balancing:

```sh
mkdir -p /tmp/up1 /tmp/up2
echo up1 > /tmp/up1/index.html
echo up2 > /tmp/up2/index.html
(cd /tmp/up1 && python3 -m http.server 8081 >/dev/null 2>&1 &)
(cd /tmp/up2 && python3 -m http.server 8082 >/dev/null 2>&1 &)
curl -s localhost:8081; curl -s localhost:8082
```

**Do** — write the config. Four objects, in the order the module walks them, and nothing else:

```sh
mkdir -p ~/envoy-academy && cat > ~/envoy-academy/envoy.yaml <<'YAML'
admin:
  address:
    socket_address: { address: 127.0.0.1, port_value: 9901 }
static_resources:
  listeners:
  - name: academy_listener
    address:
      socket_address: { address: 0.0.0.0, port_value: 10000 }
    filter_chains:
    - name: academy_chain
      filters:
      - name: envoy.filters.network.http_connection_manager
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
          stat_prefix: academy
          route_config:
            name: academy_routes
            virtual_hosts:
            - name: academy_vhost
              domains: ["*"]
              routes:
              - match: { prefix: "/" }
                route: { cluster: academy_upstream }
          http_filters:
          - name: envoy.filters.http.router
            typed_config:
              "@type": type.googleapis.com/envoy.extensions.filters.http.router.v3.Router
  clusters:
  - name: academy_upstream
    type: STATIC
    lb_policy: ROUND_ROBIN
    load_assignment:
      cluster_name: academy_upstream
      endpoints:
      - lb_endpoints:
        - endpoint: { address: { socket_address: { address: 127.0.0.1, port_value: 8081 }}}
        - endpoint: { address: { socket_address: { address: 127.0.0.1, port_value: 8082 }}}
YAML
```

Run it as the **same binary that will later be a sidecar** — `proxyv2` is the image Istio injects, and its `envoy` is on the path inside it:

```sh
docker run -d --name academy-envoy --network host \
  -v ~/envoy-academy/envoy.yaml:/etc/envoy.yaml:ro \
  --entrypoint /usr/local/bin/envoy \
  docker.io/istio/proxyv2:<ISTIO_VERSION> -c /etc/envoy.yaml -l info
docker logs academy-envoy | tail -5
```

**Observe** — the data path, then the object that each part of it belongs to:

```sh
for i in 1 2 3 4; do curl -s localhost:10000/; done
curl -s localhost:9901/listeners
curl -s localhost:9901/clusters | head -20
curl -s localhost:9901/stats | grep -E '^(listener|cluster)\.' | grep -E 'cx_total|rq_total'
```

**Expect** — `up1 up2 up1 up2`: round robin across two endpoints of one cluster, chosen by the cluster, over a connection the listener accepted. `/listeners` names `academy_listener` and the socket you bound; `/clusters` names both endpoints with `health_flags::healthy`; and the stats split cleanly — `listener.0.0.0.0_10000.downstream_cx_total` counts what came *in*, `cluster.academy_upstream.upstream_rq_total` counts what went *out*. Two counters, two objects, one request.

Expect the commonest failure to be a `@type` typo, and expect Envoy to be unusually good about it: it refuses to start and names the field. A config Envoy accepts is a config Envoy has fully validated, which is the property [the NACK](11-an-ack-and-a-nack.md) is built on.

**Write down** — the config file itself in `journal/p9-static-envoy.yaml`, the four object names you chose, and the recorded `istioctl version --remote=false`. [The module's diagram](../../phases/09-service-mesh.md#m9-1) is annotated in [the failure-ownership exercise](03-which-object-owns-the-failure.md); this file is where its four boxes get their names.

**Footprint note** — **the phase's first three exercises provision nothing.** Envoy at this scale is tens of MiB and two `python3 -m http.server` processes are noise, all inside `forge`'s [1536MB](../../strands/build-mechanics.md#forge), which is up regardless. The topology arrives at [the install that will not schedule](04-the-request-that-does-not-fit.md) and not before, which is three days of the ceiling left free for nothing better than good manners — but it is also three days in which a `pair` cannot be left half-configured.

**Teardown**

```sh
docker rm -f academy-envoy
pkill -f 'http.server 808'
rm -rf /tmp/up1 /tmp/up2
ss -ltn | grep -E ':(10000|9901|8081|8082)'      # nothing
```

Keep `~/envoy-academy/envoy.yaml` — [the static dump](02-a-dump-with-nothing-pushed-into-it.md) and [which object owns the failure](03-which-object-owns-the-failure.md) both re-run this exact config. **No topology to release; none exists yet.**
