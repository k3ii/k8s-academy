<a id="the-same-dump-now-dynamic"></a>
# The same dump, now dynamic: every object carries a version, and nobody typed any of them

**Claim** — a sidecar's `/config_dump` holds the **same object types** as [the file you wrote by hand](01-four-objects-in-a-file-you-typed.md), with two differences that are the whole of module 9.3: every section is `dynamic_*` rather than `static_*`, and the count of `version_info` fields goes from [the zero you measured](02-a-dump-with-nothing-pushed-into-it.md) to one per resource. Nothing about Envoy changed. What changed is who wrote its configuration, and that Envoy now records where each object came from.

**Rests on** — [the static dump](02-a-dump-with-nothing-pushed-into-it.md), which exists to be the control in this comparison, and [the injected pod](05-a-pod-the-webhook-rewrote.md) that is the treatment.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Setup — put both dumps side by side on the same host.** The static one was produced on `forge`; bring it to the control-plane node rather than trying to reach the cluster from `forge`:

```sh
scp zain@10.10.10.125:~/envoy-academy/dump-static.json ~/dump-static.json
kubectl -n mesh exec deploy/sleep -c istio-proxy -- pilot-agent request GET config_dump > ~/dump-dynamic.json
wc -c ~/dump-static.json ~/dump-dynamic.json
```

**Do — the three counts.** Each one is a single number, and the three together are the module's opening result:

```sh
jq -r '.configs[]."@type"' ~/dump-static.json
jq -r '.configs[]."@type"' ~/dump-dynamic.json
for f in ~/dump-static.json ~/dump-dynamic.json; do
  printf '%-24s version_info fields: ' $(basename $f)
  jq '[.. | .version_info? // empty] | length' $f
done
jq -r '.configs[] | select(."@type"|test("Listeners")) | {static: (.static_listeners|length), dynamic: (.dynamic_listeners|length)}' ~/dump-dynamic.json
jq -r '.configs[] | select(."@type"|test("Clusters")) | {static: (.static_clusters|length), dynamic: (.dynamic_active_clusters|length)}' ~/dump-dynamic.json
```

**Observe — where a version lives, and what else it comes with:**

```sh
jq -r '.configs[] | select(."@type"|test("Listeners")) | .dynamic_listeners[0]
       | {name, version: .active_state.version_info, last_updated: .active_state.last_updated}' ~/dump-dynamic.json
jq -r '[.configs[] | select(."@type"|test("Listeners")) | .dynamic_listeners[].active_state.version_info] | unique' ~/dump-dynamic.json
jq -r '[.configs[] | select(."@type"|test("Clusters")) | .dynamic_active_clusters[].version_info] | unique' ~/dump-dynamic.json
```

**Expect** — the `@type` list to be **nearly the same in both files**, which is the surprising half: bootstrap, listeners, clusters and routes are the same four sections whether a human or a control plane filled them. Expect the dynamic dump to carry **two sections the static one has not** — an endpoints dump and a secrets dump — and expect both to be explainable rather than mysterious: endpoints arrive separately because they change most often ([the next exercise](10-one-service-four-resource-types.md)), and secrets arrive separately because they are certificates with their own lifetime ([the identity exercise](15-a-certificate-that-names-a-serviceaccount.md)).

Expect `version_info` to go from **0 to hundreds**, and expect every listener to share one version string while every cluster shares another. That is the shape of the protocol: a version is **per resource type**, not per resource — one push of LDS carries all listeners and one version, which is why a single bad listener can invalidate an entire push and why [a NACK](11-an-ack-and-a-nack.md) is a statement about a type rather than about an object.

Expect the dynamic dump to be **one to two orders of magnitude larger** than the file you typed, and expect that to be honest rather than bloated: it holds a listener and a cluster for every Service the proxy might talk to, in a cluster you did not configure it for. Count them. Then read the number as a footprint statement — this is the per-pod memory a sidecar spends holding configuration for services it will never call, and the reason `Sidecar` scoping and ambient exist at all.

**Write down** — a two-column table in `journal/p9-dump-compare.md`: sections, `version_info` count, listener count, cluster count, bytes, for static and dynamic. One sentence on which of those numbers you could have predicted from Envoy's docs and which required the cluster. Keep `~/dump-dynamic.json`; [the LDS→RDS→CDS→EDS walk](10-one-service-four-resource-types.md), [the NACK](11-an-ack-and-a-nack.md) and [the capstone](25-one-request-both-halves.md) all cite JSON paths in this exact file.

**Teardown** — nothing created in the cluster; two files on the control-plane node, both kept deliberately. Do not delete `~/dump-static.json` either — the comparison above is re-run at the end of the phase against an **ambient** proxy, and having all three is what makes [the flat curve](21-the-same-curve-flat.md) readable.

**The topology stays.**
