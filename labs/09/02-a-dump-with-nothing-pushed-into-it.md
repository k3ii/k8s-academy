<a id="a-dump-with-nothing-pushed-into-it"></a>
# A config dump with nothing pushed into it: three facts that all invert once a control plane exists

**Claim** — every resource in your static Envoy's `/config_dump` is under a `static_*` key, **no entry carries a `version_info`**, and one of [the four objects](01-four-objects-in-a-file-you-typed.md) has no top-level section of its own at all. All three are consequences of there being no control plane, and all three invert in [the sidecar's dump](09-the-same-dump-now-dynamic.md) — which is the only reason that dump is legible on first contact.

**Rests on** — [the config you typed](01-four-objects-in-a-file-you-typed.md), still running or restarted from the same file.

**Topology** — **none.** [`forge`](../../strands/lab-topologies.md#build-guest) only.

**Setup** — if you tore Envoy down, bring the same config back:

```sh
ssh zain@10.10.10.125
(cd /tmp/up1 && python3 -m http.server 8081 >/dev/null 2>&1 &)
(cd /tmp/up2 && python3 -m http.server 8082 >/dev/null 2>&1 &)
docker run -d --name academy-envoy --network host \
  -v ~/envoy-academy/envoy.yaml:/etc/envoy.yaml:ro \
  --entrypoint /usr/local/bin/envoy \
  docker.io/istio/proxyv2:<ISTIO_VERSION> -c /etc/envoy.yaml -l info
```

**Do** — take the dump once, keep it, and read it offline. It is 30 KB now and it is 400 KB in module 9.3; the habit of saving it is worth forming on the small one:

```sh
curl -s localhost:9901/config_dump > ~/envoy-academy/dump-static.json
wc -c ~/envoy-academy/dump-static.json
jq -r '.configs[]."@type"' ~/envoy-academy/dump-static.json
```

**Observe** — three questions, each answered by one filter over that file:

```sh
jq -r '.configs[] | select(."@type"|test("ListenersConfigDump")) | keys[]' ~/envoy-academy/dump-static.json
jq -r '.configs[] | select(."@type"|test("ClustersConfigDump")) | keys[]' ~/envoy-academy/dump-static.json
jq '[.. | .version_info? // empty] | length' ~/envoy-academy/dump-static.json
jq -r '.configs[] | select(."@type"|test("RoutesConfigDump"))' ~/envoy-academy/dump-static.json
```

Then find your route config by name, wherever it actually lives:

```sh
grep -c academy_routes ~/envoy-academy/dump-static.json
jq -r 'paths(scalars) as $p | select(getpath($p)=="academy_routes") | $p|join(".")' ~/envoy-academy/dump-static.json
```

**Expect** — `static_listeners` and `static_clusters` present, `dynamic_listeners` and `dynamic_active_clusters` absent or empty, and **zero `version_info` fields in the entire document**. A version is a control plane's serial number for a push; nothing pushed, so nothing is versioned.

Expect the route config to be **nested inside the listener**, not listed beside it — its path runs through the HTTP connection manager's `typed_config`, because you inlined it. That is not a quirk of your file: **an inline route config is the RDS-less case**, and the reason `RDS` exists as a separate resource type is precisely to lift that nested object out and version it on its own. You have just built the *before* picture for [the four-type walk](10-one-service-four-resource-types.md) without meaning to.

Expect `BootstrapConfigDump` to be the first entry and to contain your whole file. In a sidecar it contains something you did not write, and [the dynamic dump](09-the-same-dump-now-dynamic.md) is where you find out who did.

**Write down** — the three answers (`static_*` keys, the `version_info` count of zero, the JSON path where `academy_routes` was found) in `journal/p9-static-dump.md`, and keep `dump-static.json` itself. It is the control in an experiment whose treatment arrives in module 9.3.

**Teardown**

```sh
docker rm -f academy-envoy
pkill -f 'http.server 808'
```

Keep `~/envoy-academy/`, including `dump-static.json` — [the failure-ownership exercise](03-which-object-owns-the-failure.md) restarts the same proxy and module 9.3 compares against this file. **No topology to release; none exists yet.**
