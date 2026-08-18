<a id="three-backends-one-table"></a>
# Three backends, one table, and the one of them you will never run

**Artifact** — a comparison of kube-proxy's three backends across six axes, two of which you measured in [exercises 16](16-a-clusterip-followed-to-its-kube-sep.md)–[18](18-the-tracker-between-two-syncs.md) and four of which come from the KEPs, plus an answer to the question that makes IPVS worth reading at all after it is deprecated: **which of the three can drain a connection, and what in the API exists because it could?**

**Rests on** — [exercises 16](16-a-clusterip-followed-to-its-kube-sep.md), [17](17-the-same-service-as-a-verdict-map.md) and [18](18-the-tracker-between-two-syncs.md) for the two columns that are measurements rather than citations, and [exercise 4](04-eleven-kilobytes-of-endpointslice.md) for the `Serving`/`Terminating` split.

**IPVS is read and not run**, deliberately. [KEP-5495](../../strands/source-reading.md#area-5-networking) deprecates it and [the phase's header row](../../phases/07-networking.md) says comparative-only, so switching a third backend on to look at `ipvsadm -Ln` output would cost a rollout and teach a data structure nobody will be asked to operate. What it *does* still teach is a capability the other two do not have, and that survives the deprecation.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued and idle. This exercise creates nothing.

**Read**

| Item | The question |
|---|---|
| KEP-265 | The virtual-server / real-server model, the schedulers, and **what `ipset` is doing there** — IPVS mode still writes iptables rules, and the KEP says which ones and why. |
| `pkg/proxy/ipvs/graceful_termination.go` | The small interesting file. How does a connection to an endpoint that is going away end? Find what is done to the real server's *weight*, and what happens to connections already established. |
| KEP-5495 | The deprecation's stated reasons. One of them is about maintenance and one is about capability parity; note which capability the KEP admits is not at parity. |
| KEP-3866 | Re-read the motivation section only, now that you have both dumps. It is the clearest account of the iptables backend's scaling problems in the corpus and it reads differently after [exercise 17](17-the-same-service-as-a-verdict-map.md). |

**Do** — fill it in. Four columns are citations and two are your own measurements; mark which is which, because a table where those are indistinguishable is worth less than one where they are not:

| Axis | iptables | IPVS | nftables |
|---|---|---|---|
| how a ClusterIP is dispatched | | | |
| cost of one endpoint change, in what is written to the kernel | **measured** ([18](18-the-tracker-between-two-syncs.md)) | | **measured** ([18](18-the-tracker-between-two-syncs.md)) |
| endpoint selection mechanism | **measured** ([16](16-a-clusterip-followed-to-its-kube-sep.md)) | | **measured** ([17](17-the-same-service-as-a-verdict-map.md)) |
| does it still need iptables/nftables rules for anything | | | |
| can an established connection outlive its endpoint's removal | | | |
| status as of the current release | | | |

**Expect the fifth row to be the one worth the exercise.** IPVS holds per-real-server state, so removing an endpoint can mean *setting its weight to zero* — no new connections, existing ones allowed to finish. The other two backends dispatch per packet with no such handle: an endpoint is in the ruleset or it is not, and conntrack is what keeps established connections working, with no mechanism to distinguish "drain" from "remove".

Then answer the question this raises, which is the one that ties the phase together: `EndpointConditions.Serving` exists so that a consumer can be told *this endpoint is terminating and still answering*. **Who is that consumer?** Two of the three backends cannot act on the distinction, so name what can — and note that the answer includes things that are not kube-proxy at all, which is the point of [exercise 6's](06-the-api-that-is-being-deleted.md) `managed-by` label and of [Cilium's](31-kube-proxy-replaced-by-map-lookups.md) arrival at the end of this phase.

**Expect the fourth row to be a mild surprise** — IPVS mode does not replace iptables, it adds a virtual-server table in front of it and keeps rules for masquerading and for the packet-mark path. "IPVS instead of iptables" is a simplification the KEP itself does not make.

**Write down** — the table with its measured and cited cells marked, the drain answer, and one sentence on what [KEP-5343's](../../strands/source-reading.md#area-5-networking) default switch means for a cluster running IPVS today. This is the phase's third [falsifiable claim](../../phases/07-networking.md#checklist) alongside the two from [exercises 5](05-make-the-packing-visible.md) and [17](17-the-same-service-as-a-verdict-map.md), and it is the only one of the three whose evidence is entirely on paper — worth saying so in the write-up.

**Footprint note** — reading. Nothing.

**Teardown** — nothing created. **The topology stays** — [module 7.4](../../phases/07-networking.md#m7-4) starts at [exercise 23](23-a-policy-nobody-enforces.md) with a negative result.
