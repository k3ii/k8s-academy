<a id="the-api-that-is-being-deleted"></a>
# Point a Service at an address outside the cluster, twice: the deprecated way and the way that replaces it

**Artifact** — the same result produced through `v1.Endpoints` and through `discovery/v1.EndpointSlice`, with the `endpointslice.kubernetes.io/managed-by` label recorded for every object involved, and a two-line statement of what KEP-4974 removes and what has to change in your notes when it lands.

**Rests on** — [exercise 4](04-eleven-kilobytes-of-endpointslice.md). The reason this is an exercise rather than a footnote: **hand-writing an `Endpoints` object is the one place `Endpoints` is still routinely taught**, so it is the one place a deprecation actually costs the reader something.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Read** — KEP-4974, and answer two questions from it: which controllers go away, and what happens to an `Endpoints` object a client writes after they do.

**Do — part 1, the old way.** A Service with **no selector**, and an `Endpoints` object you write yourself. The target is the control-plane node's own SSH port, so that reachability is checkable and needs nothing installed:

```sh
kubectl create ns mirror
kubectl -n mirror apply -f - <<'YAML'
apiVersion: v1
kind: Service
metadata: {name: outside, namespace: mirror}
spec:
  ports: [{name: ssh, port: 22, targetPort: 22, protocol: TCP}]
---
apiVersion: v1
kind: Endpoints
metadata: {name: outside, namespace: mirror}
subsets:
- addresses: [{ip: 10.10.10.130}]
  ports: [{name: ssh, port: 22, protocol: TCP}]
YAML
kubectl -n mirror get endpointslice -o json | jq -c '.items[]|{n:.metadata.name, mgr:.metadata.labels."endpointslice.kubernetes.io/managed-by", e:[.endpoints[].addresses[0]]}'
```

**Do — part 2, the way that replaces it.** Delete the `Endpoints` object, and write the slice directly:

```sh
kubectl -n mirror delete endpoints outside
kubectl -n mirror apply -f - <<'YAML'
apiVersion: discovery.k8s.io/v1
kind: EndpointSlice
metadata:
  name: outside-manual
  namespace: mirror
  labels: {kubernetes.io/service-name: outside}
addressType: IPv4
ports: [{name: ssh, port: 22, protocol: TCP}]
endpoints:
- addresses: ["10.10.10.130"]
  conditions: {ready: true}
YAML
kubectl -n mirror get endpointslice -o json | jq -c '.items[]|{n:.metadata.name, mgr:.metadata.labels."endpointslice.kubernetes.io/managed-by"}'
```

**Verify from outside** — both versions must actually carry traffic, or the comparison is about YAML rather than about networking:

```sh
kubectl -n mirror run t --rm -it --restart=Never --image=busybox:1.37 -- \
  sh -c 'nc -z -w3 outside 22 && echo REACHED'
```

**Expect** — in part 1, a slice you did not write, carrying `managed-by: endpointslicemirroring-controller.k8s.io`; in part 2, only the slice you did write, with **no `managed-by` label at all**, and traffic working identically. Expect a Service *with* a selector (any of the ones from earlier exercises) to carry `managed-by: endpointslice-controller.k8s.io` — a third value, from a third controller.

Expect the mirroring path to have one property the direct path does not: **it is the reason a fifteen-year-old runbook still works.** Naming that property is the honest reason a deprecation with no functional gap still takes a KEP and several releases.

**Expect the label to be the thing worth remembering.** Three controllers can write objects of this type, and `managed-by` is how a fourth — [kube-proxy](14-the-model-files-before-the-machine.md), or Cilium at [exercise 31](31-kube-proxy-replaced-by-map-lookups.md) — avoids fighting them. There is no field named "owner"; there is a label, by convention.

**Write down** — the three `managed-by` values with which controller writes each, and one line naming what in your own notes from [exercise 4](04-eleven-kilobytes-of-endpointslice.md) becomes wrong the day KEP-4974 lands.

**Footprint note** — one short-lived `busybox` pod. Nothing.

**Teardown**

```sh
kubectl delete ns mirror --wait=true
```

**The topology stays** — the CNI plugin work begins at [exercise 7](07-what-replaces-stage-1.md), on `forge` first.
