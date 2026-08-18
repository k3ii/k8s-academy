<a id="the-model-files-before-the-machine"></a>
# kube-proxy's model in six small files, and the one key both maps are keyed on

**Artifact** — a six-row table: each backend-agnostic file in `pkg/proxy/`, the question it answers, and the type or function that answers it, with `file:line` for each. Plus one sentence naming **the map key that every backend, including Cilium, has to agree on**, because it is what makes a service port a unit of work rather than a Service being one.

**Rests on** — [exercise 4](04-eleven-kilobytes-of-endpointslice.md) for the API type these files consume. Nothing else; this is reading.

**Reading these before either `proxier.go` is the whole method** and [Area 5 says so](../../strands/source-reading.md#area-5-networking) in as many words — it is the correct on-ramp and it is routinely skipped. The two big files are 61 KB and 70 KB of rule generation; entering them without the model means every identifier is new at once.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued and idle. This exercise is reading on `forge` with two short cluster confirmations at the end.

**Read** — on `forge`, in the phase's clone, in this order and no other:

| File | The question it answers |
|---|---|
| `pkg/proxy/serviceport.go` | What is the unit of work? Not a Service — find the type, and find what its name is composed of. |
| `pkg/proxy/endpoint.go` | What does a backend need to be told about one endpoint, beyond its address? Two of the fields are about *topology* and one is about *readiness*. |
| `pkg/proxy/servicechangetracker.go` | Where does a Service watch event go between arriving and being programmed? |
| `pkg/proxy/endpointschangetracker.go` | The same question for endpoints — **and this is the hop [P6's trace](../../phases/06-kubelet-node.md#capstone) could only watch**. Find the method a backend calls to take delivery of accumulated changes. |
| `pkg/proxy/endpointslicecache.go` | Why is there a cache in front of the tracker at all, given that the informer is already a cache? The answer is about *slices* versus *endpoints*. |
| `pkg/proxy/topology.go` | Which endpoints does a node actually use, out of all the ready ones? |

**Do — the prediction, written before the cluster is asked.** For a Service with six ready endpoints — four on the control-plane node, two on the worker — predict the endpoint set a kube-proxy **on the worker** will program, for each configuration:

| Configuration | endpoints programmed on the worker | why |
|---|---|---|
| defaults | | |
| `internalTrafficPolicy: Local` | | |
| `externalTrafficPolicy: Local`, traffic arriving on the worker's NodePort | | |
| `externalTrafficPolicy: Local`, traffic arriving on the **control plane's** NodePort | | |
| `trafficDistribution: PreferClose`, no zone labels on either node | | |

The last row is the one worth thinking hardest about: a hint that cannot be evaluated is not the same as a hint that evaluates to nothing, and `topology.go` decides which of those it is.

**Verify from outside** — two commands, to confirm the prediction's last row rather than the whole table (the rest is scored in [exercise 16](16-a-clusterip-followed-to-its-kube-sep.md) and [exercise 21](21-an-address-claimed-by-arp.md)):

```sh
kubectl get nodes -o custom-columns='NAME:.metadata.name,ZONE:.metadata.labels.topology\.kubernetes\.io/zone'
kubectl -n mynet get endpointslice -o jsonpath='{.items[*].endpoints[*].hints}{"\n"}'
```

**Expect** — the answer to *what is the unit of work* to be a **service port**, keyed by namespace, name **and port name**, and expect that to explain something you have probably already seen without explaining: a Service with two ports produces two independent sets of rules, can be half-broken, and appears twice in every metric kube-proxy exports.

Expect `endpointslicecache.go` to exist because **a backend needs the union of a Service's slices and the informer delivers one slice at a time**. With [exercise 5's](05-make-the-packing-visible.md) limit of five still in place, a thirteen-endpoint Service arrives as three unrelated watch events, and something has to hold the other two while the third is processed.

Expect the zone labels to be **absent** on `pair` — nothing labels them — and therefore expect the hints array to be empty. Which means `PreferClose` on this cluster is a no-op that falls back to all endpoints, and **that fallback is the correct behaviour, not a failure**: `topology.go` is explicit that an unusable hint must not be allowed to blackhole traffic. Find the line that says so.

**Write down** — the six-row table with `file:line` for each answer, the service-port key as one sentence, and the prediction table. The `endpointschangetracker.go` row is one of [P6's three owed citations](../../phases/06-kubelet-node.md#capstone); mark it as such, and note that it is not *repaid* until [exercise 18](18-the-tracker-between-two-syncs.md) confirms it against a running proxy.

**Footprint note** — reading. No change.

**Teardown** — nothing created. **The topology stays.**
