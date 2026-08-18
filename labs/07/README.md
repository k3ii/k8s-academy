# Labs — Phase 7, networking, the L3/L4 datapath

Thirty-four exercises in the order they are meant to run, for **the only phase whose two
build artifacts have no fast loop**: [the strand lists both the CNI plugin and the eBPF
program as on-node-only](../../strands/build-mechanics.md#artifact-table), so there is no
stage 1 to edit-and-rerun against a live API from outside. What replaces it is named twice
and built twice — a `cnitool` harness in [exercise 7](07-what-replaces-stage-1.md) and a
veth in a namespace in [exercise 28](28-a-counter-loaded-attached-read-detached.md) — and
both are legitimate only because `forge` runs the nodes' kernel, which is why
[exercise 2](02-the-kernel-both-sides-must-share.md) checks that before anything is
compiled.

Each file states one claim to test or one artifact to produce, links its
[topology](../../strands/lab-topologies.md) rather than restating a footprint, and ends
with a teardown that does two things: **deletes what that exercise created**, then says
whether the topology stays or goes.

The framing — why each module exists, what to read and the question to answer from it —
stays in [`phases/07-networking.md`](../../phases/07-networking.md). These files hold only
what you type and what you should see.

| # | Exercise | Why it exists |
|---|---|---|
| 1 | [The four communication paths, three of them already built in P0](01-the-four-paths-and-what-p0-wired.md) | The model's four paths mapped onto P0's veth exercises, so nothing here re-teaches a veth pair. |
| 2 | [`forge` and the nodes must share a kernel](02-the-kernel-both-sides-must-share.md) | The precondition made an exercise: the repair is a reprovision, so week four is the wrong place to find out. |
| 3 | [What the runtime hands a plugin](03-what-the-runtime-hands-a-plugin.md) | A real `ADD` captured by shimming the installed binary — the spec met as evidence rather than as prose. |
| 4 | [`Ready`, `Serving` and `Terminating` for five pod states](04-eleven-kilobytes-of-endpointslice.md) | Fifteen cells predicted from the comments, scored against a pod with a 90-second `preStop`. |
| 5 | [Shrink the slice limit to five](05-make-the-packing-visible.md) | KEP-752's write amplification made visible on a two-node cluster by one flag. |
| 6 | [A Service pointed outside the cluster, twice](06-the-api-that-is-being-deleted.md) | The mirroring controller, the three `managed-by` values, and what KEP-4974 is removing. |
| 7 | [The fast loop for an artifact with no stage 1](07-what-replaces-stage-1.md) | Builds the harness, proves it with somebody else's plugin, and names the three things it cannot test. |
| 8 | [Build artifact 1: `ADD`, `DEL`, and `cnitool` as judge](08-add-and-del-that-cnitool-accepts.md) | The plugin, with the gate made to fail twice on purpose before it is allowed to pass. |
| 9 | [An allocator, and the leak `DEL` cannot free](09-an-ipam-that-does-not-leak.md) | Frees by container id rather than by address, and `kill -9` mid-`ADD` proves why `GC` exists. |
| 10 | [Stage 2: real pods, addressed by your allocator](10-the-plugin-the-kubelet-calls.md) | Discovery order, three failure modes, and the worker-only install that keeps the control plane known-good. |
| 11 | [Two nodes, two pod CIDRs, no route](11-two-nodes-two-pod-cidrs-no-route.md) | The row P0 could not build; each command maps to host-gw, overlay, BGP or eBPF, and none of it survives a reboot. |
| 12 | [A malformed result at the CRI seam](12-a-malformed-result-at-the-cri-seam.md) | The error surfaces in containerd first and the kubelet second — P6's named seam, paid. |
| 13 | [A second plugin in the chain](13-a-second-plugin-in-the-chain.md) | `prevResult` is byte-for-byte yours, `DEL` runs backwards, and a chained failure leaks an address. |
| 14 | [kube-proxy's model in six small files](14-the-model-files-before-the-machine.md) | The unit of work is a service port; read the model before any backend, or every backend looks arbitrary. |
| 15 | [`reconciler.go`, cited](15-the-reconciler-and-its-packing-heuristic.md) | P6's first owed citation, verified against the running commit because staging paths move. |
| 16 | [One ClusterIP followed to its `KUBE-SEP`](16-a-clusterip-followed-to-its-kube-sep.md) | Four chains, the probability arithmetic worked, and two hashes with two different scopes. |
| 17 | [The same Service as a verdict map](17-the-same-service-as-a-verdict-map.md) | Switch the backend and diff the dumps: two structural reasons, written as claims rather than as *faster*. |
| 18 | [The tracker between two syncs](18-the-tracker-between-two-syncs.md) | P6's second owed citation, with `minSyncPeriod` widened so the pending counter can be caught above zero. |
| 19 | [7.C3 — one wrong DNAT](19-7c3-delete-one-endpoint-rule.md) | A third of requests failing with three `Ready` endpoints and no event anywhere; timed against the resync. |
| 20 | [7.C1 — one partition, two primitives](20-7c1-a-partition-named-by-path.md) | Checks the strand's one-primitive-per-fault claim instead of repeating it. Chaos Mesh arrives here. |
| 21 | [An address that exists only as an ARP reply](21-an-address-claimed-by-arp.md) | `externalTrafficPolicy` measured both ways, with the bastion NAT recorded as a limit rather than worked around. |
| 22 | [Three backends, one table](22-three-backends-one-table.md) | IPVS read and never run; the row that earns it is weight-zero draining, which the other two cannot do. |
| 23 | [A policy nobody enforces](23-a-policy-nobody-enforces.md) | A perfect deny-all changes nothing, and nothing in the cluster reports that — the negative result is the finding. |
| 24 | [Ten policy questions, sealed](24-the-semantics-are-in-the-comments.md) | Predictions committed to git before an enforcer exists, so exercise 32 scores a claim rather than a transcript. |
| 25 | [One `curl` by name, counted in queries](25-a-name-resolved-in-five-hops.md) | The `ndots` trap measured, and DNS shown to be a client of module 7.3's datapath. |
| 26 | [7.C2 — a resolver that lies](26-7c2-it-was-dns.md) | The checklist run against a fault four of its five checks cannot see; the second action succeeds and is wrong. |
| 27 | [Three rules NetworkPolicy cannot express](27-adminnetworkpolicy-read-and-banked.md) | KEP-2091 read, three manifests written, and banked to P10 rather than installed here. |
| 28 | [Build artifact 2: five verbs, each proven](28-a-counter-loaded-attached-read-detached.md) | Load, attach, read, detach — plus the CO-RE program the kernel gate exists to protect. |
| 29 | [The borrowed drill: a type-layout mismatch](29-a-mismatched-btf-and-the-two-ways-it-fails.md) | Three endings — loud at load, loud at attach, silent at read — and only the third is the dangerous one. |
| 30 | [A drop decided by a map entry](30-a-drop-decided-by-a-map-entry.md) | Your program on the veth your plugin made, at a hook that sees the ClusterIP and not the backend. |
| 31 | [The same DNAT, a third time](31-kube-proxy-replaced-by-map-lookups.md) | Chains, verdict map, `cilium bpf lb list` — one Service, three representations, from your own saved dumps. |
| 32 | [Ten predictions opened and scored](32-the-prediction-scored-at-the-datapath.md) | Every miss traced to a citation, and a column naming which component actually answered each row. |
| 33 | [7.C4 — three policies that read correct](33-7c4-a-policy-that-reads-correct.md) | Blind-picked and timed; the over-allow is the slow one, because nothing is broken and nothing shows up. |
| 34 | [The capstone](34-the-capstone-a-network-you-wrote-and-a-drop-you-can-point-at.md) | A pod on your own plugin, a drop with a map entry behind it, and P6's three citations re-verified live. |

## Which cluster is running when

**Exercise 1 needs no cluster** — it runs on [`forge`](../../strands/lab-topologies.md#build-guest)
with `ip netns` and nothing else, which defers the phase's first provision by a day.
[`pair`](../../strands/lab-topologies.md#pair) comes up at
[exercise 2](02-the-kernel-both-sides-must-share.md) and is held to the end, destroyed at
[the capstone](34-the-capstone-a-network-you-wrote-and-a-drop-you-can-point-at.md). It is
provisioned *for the kernel check*, before there is any Kubernetes work to do on it, and
that ordering is the point of exercise 2.

**`forge` never changes size, and P7 is the phase that proves the standing 1536MB is
enough.** Nothing here links a control-plane binary — the biggest compile is `clang` on one
small C file, well under [the 564 MiB the strand measured](../../strands/build-mechanics.md#measurements)
— so [the P5 resize](../../strands/build-mechanics.md#forge) has no analogue here. What this
phase needs from `forge` is the kernel, not the RAM.

| Exercises | Topology | `forge` | Inside the guests | Total | Margin |
|---|---|---|---|---|---|
| 1 | none | 1536MB | — | 1.5GB | 8.0GB |
| 2–19 | `pair` 5.0GB | 1536MB | — | 6.5GB | 3.0GB |
| 20 | `pair` 5.0GB | 1536MB | Chaos Mesh 582Mi | 6.5GB | 3.0GB |
| 21–30 | `pair` 5.0GB | 1536MB | + MetalLB 250–300Mi | 6.5GB | 3.0GB |
| 31–34 | `pair` 5.0GB | 1536MB | Chaos Mesh **out**, Cilium **in** | 6.5GB | 3.0GB |

against the [9.5GB ceiling](../../strands/lab-topologies.md#ceiling). The guest total never
moves, and neither does the margin.

**The one real pressure in this phase is tenancy, not totals, and it is flagged here rather
than softened.** Three DaemonSet-shaped tenants wanted to be resident at once inside
`pair`'s 5.0GB: [Chaos Mesh at 582Mi](../../strands/chaos.md#install), MetalLB at 250–300Mi,
and Cilium — against [the phase's own note](../../phases/07-networking.md#ecosystem) that
Cilium is *not co-resident* with the heavy tooling on this host. **The smallest change is
ordering, and that is the change taken**: Chaos Mesh goes in at
[exercise 20](20-7c1-a-partition-named-by-path.md), both drills that need it are done by
[exercise 26](26-7c2-it-was-dns.md), and it is uninstalled at the start of
[exercise 31](31-kube-proxy-replaced-by-map-lookups.md) before Cilium is installed. No guest
is resized and no drill is dropped — the two remaining drills, 7.C3 and 7.C4, are by-hand
and need nothing installed. If the worker is still under pressure after Cilium,
[exercise 31](31-kube-proxy-replaced-by-map-lookups.md) names MetalLB as the next removal,
in advance, so that the decision is not made under time pressure.

**Two CNIs, one cluster, on purpose.** From [exercise 10](10-the-plugin-the-kubelet-calls.md)
to [exercise 30](30-a-drop-decided-by-a-map-entry.md) your plugin owns `.131` and the stock
one owns `.130`. That is what makes a cross-node failure a comparison rather than an outage,
keeps `kubectl` working while pod networking on the worker is deliberately broken, and
guarantees [exercise 23's](23-a-policy-nobody-enforces.md) negative result instead of hoping
for it. It ends at [exercise 31](31-kube-proxy-replaced-by-map-lookups.md), which also says
what the arrangement implies for a real CNI migration.

## Exceptions

- **Exercise 1 needs no cluster at all**, and exercises **7, 8, 9 and 13** need none either — they are `forge`, a netns and the `cnitool` harness, with `pair` up and idle beside them.
- **Exercises 28 and 29** are also `forge`-only. `pair` stays up and idle rather than being destroyed, because [exercise 30](30-a-drop-decided-by-a-map-entry.md) needs a real pod's veth and a reprovision costs more than the idle RAM.
- **Exercises 22, 24 and 27 create nothing.** Two are reading with a table as the artifact; the third is a prediction committed to git and scored at [exercise 32](32-the-prediction-scored-at-the-datapath.md).
- **Exercise 2 is a precondition exercise, not a check.** It provisions the topology solely to compare two kernels, and its two named fixes are both reprovisions — which is why it is second rather than in module 7.5.
- **Exercise 29 substitutes for [the strand's drill](../../strands/chaos.md#borrowed-drills)** rather than running it exactly: it produces three of the four failure modes on one kernel and says, in the exercise, which one only a genuine second kernel and a reboot can produce.
- **Drills 7.C3 and 7.C4 use no chaos tooling** — [the phase says why](../../phases/07-networking.md#chaos): reading the rule that broke is the exercise, and a tool that injects the break also names it.
- **Exercise 21 records a limit instead of engineering around it.** A request from the Mac arrives NAT'd by the bastion, so the "preserved" client address is the bastion's; the deliverable is the pair of results, and the note says so.
