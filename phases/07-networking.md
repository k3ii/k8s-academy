# Phase 7 — Networking, L3/L4 datapath

> **4–5 weeks.** The area where the *specs* are more readable than the code — the CNI spec is clear prose, `proxier.go` is a 61 KB rule-generation machine — so you lead with specs and API types and enter the dataplane code only through `syncProxyRules`. The build track resumes here with **two artifacts loaded into a real kernel**, and this phase repays a debt: [P6](06-kubelet-node.md)'s capstone trace could only *watch* the EndpointSlice/kube-proxy far end; here you read it in source.
> The range is planning information. **The gate at the bottom decides when the phase is finished.**

| | |
|---|---|
| **Prerequisites** | [P6](06-kubelet-node.md) — its capstone trace stopped at the node's edge (`nft list ruleset`-observable but uncited); this phase opens that far end in source and closes the seam. [P0](00-linux-primitives.md) — pod networking *is* `ip netns` + veth + bridges + routes; the CNI plugin you build is those primitives automated, and the phase is barely legible without them. |
| **Unlocks** | [P8](08-storage.md) — the last descent phase; storage is the one major subsystem left below the abstraction line. [P9](09-service-mesh.md) — the service mesh is an L7 layer *on top of* the L3/L4 datapath built here, and Cilium (entered here) is where mesh and CNI start to merge. |
| **Source area** | [Area 5 — Networking](../strands/source-reading.md#area-5-networking), entry point `discovery/v1/types.go`. **kube-proxy in iptables *and* nftables**, IPVS comparative-only (KEP-5495 deprecates it; nftables is GA and slated default). |
| **Language** | Go — **two build artifacts** ([CNI plugin, eBPF program](../strands/build-mechanics.md#artifact-table)), both **on-node-only**: unlike the webhooks and CSI driver, neither has an out-of-cluster stage 1, because you cannot wire a netns or attach a tc hook without a node. The eBPF build carries the [kernel-lockstep gate](../strands/build-mechanics.md#kernel-lockstep). |
| **Lab** | [`pair`](../strands/lab-topologies.md#pair) — Cilium is a DaemonSet, so two nodes beat three. **`forge` never changes size this phase**: what the two artifacts need from it is [the nodes' kernel](../strands/build-mechanics.md#kernel-lockstep), not RAM. |
| **Labs** | [`labs/07/`](../labs/07/README.md) — 34 exercises, in order. One topology for 33 of them, and **three tenants that cannot all be resident at once** — the index gives the order they arrive and leave in. |
| **Strands** | [source reading](../strands/source-reading.md#area-5-networking) · [build](../strands/build-mechanics.md#artifact-table) · [talks](../strands/talks.md#networking) · [eBPF talks](../strands/talks.md#ebpf) |

---

<a id="objectives"></a>
## 1. Objectives

Every one is falsifiable — an artifact, a timed production, or a claim a hostile reader could check against source or a running cluster. *understand* and *know* appear nowhere.

By the end you can:

1. **Wire a pod's network by hand** — `ip netns`, veth pair, bridge, routes — and then say exactly what a CNI plugin automates, citing the CNI `SPEC.md` operations.
2. **Read `discovery/v1/types.go`** and explain what EndpointSlice replaced and why `Endpoints` didn't scale (O(n) watch fan-out on every pod churn), citing KEP-752 — **the far end of [P6](06-kubelet-node.md)'s trace, now cited in source.**
3. **Build a CNI plugin** (ADD/DEL, JSON on stdin, wires a netns) that gives pods a `ping`-able network. **Build artifact 1.**
4. **Compare `syncProxyRules` in iptables and nftables `proxier.go`** and name the structural difference (chain-per-service vs verdict maps) — the comparison is the lesson.
5. **Trace a Service packet** from ClusterIP to the kube-proxy rule/map that DNATs it to an endpoint, shown in a live `iptables-save` / `nft list ruleset` dump — repaying P6's far half in source (`endpointschangetracker` → `syncProxyRules`).
6. **Compile, load, attach, read a map from, and detach an eBPF program** via `cilium/ebpf`, with the [`forge`/node kernel lockstep verified](../strands/build-mechanics.md#kernel-lockstep). **Build artifact 2.**
7. **Prove a NetworkPolicy at the datapath** — the specific rule or map entry that drops the packet, not just that the connection failed (k8s ships no enforcer; the CNI does).
8. **Diagnose a DNS failure by method** — CoreDNS, `resolv.conf`, the Service behind it — the *It Wasn't DNS* procedure.

---

<a id="modules"></a>
## 2. Modules

Reading is [Area 5](../strands/source-reading.md#area-5-networking), and its rule is the corpus's clearest: **specs and API types before the `proxier.go` machines, the small backend-agnostic proxy files before any big backend.** Each cited item carries a question to answer — no bare links.

<a id="m7-1"></a>
### Module 7.1 — Networking from first principles, and EndpointSlice (~1 week)

The Linux primitives first, by hand — then the data structure the whole service dataplane consumes.

**Read**

| Item | Answer from it |
|---|---|
| CNI `SPEC.md` (item 1) + `CONVENTIONS.md` (item 2) | The spec: `ADD`/`DEL`/`CHECK`/`GC`/`STATUS`, the JSON config, chaining, and **how the runtime invokes plugins as executables with env vars**. No Kubernetes needed. What does the runtime hand a plugin on stdin? |
| `network/networking.md` design doc (item 3) | The IP-per-pod model, no NAT between pods, the four communication paths. What are the axioms every CNI must satisfy? |
| `discovery/v1/types.go` (item 4, ⭐) + KEP-752 (item 5) + KEP-4974 (item 6) | **The entry point:** `Endpoint`, `EndpointConditions{Ready,Serving,Terminating}`, the `addressType` split. Why did one `Endpoints` object per Service melt the apiserver, and what does slicing fix? **This is the data structure [P6](06-kubelet-node.md)'s trace passed through.** |

**Labs** — [1](../labs/07/01-the-four-paths-and-what-p0-wired.md) the four paths, three of them P0's · [2](../labs/07/02-the-kernel-both-sides-must-share.md) the kernel both sides must share · [3](../labs/07/03-what-the-runtime-hands-a-plugin.md) what the runtime hands a plugin · [4](../labs/07/04-eleven-kilobytes-of-endpointslice.md) `Ready`/`Serving`/`Terminating` predicted · [5](../labs/07/05-make-the-packing-visible.md) the packing heuristic made visible · [6](../labs/07/06-the-api-that-is-being-deleted.md) the API that is being deleted.

<a id="m7-2"></a>
### Module 7.2 — Build artifact 1: the CNI plugin (~1 week)

CNI demystified: a spec for an executable that receives JSON on stdin and wires a netns. Module 7.1 done by hand; now automate it.

**On-node-only — there is no out-of-cluster stage 1**, because you cannot wire a netns without a node, which is why the [artifact table](../strands/build-mechanics.md#artifact-table) lists none for it. What replaces the fast loop the other nine artifacts get is the first exercise of the module, not a footnote.

**Labs** — [7](../labs/07/07-what-replaces-stage-1.md) what replaces stage 1 · [8](../labs/07/08-add-and-del-that-cnitool-accepts.md) **artifact 1**, judged by `cnitool` · [9](../labs/07/09-an-ipam-that-does-not-leak.md) an IPAM that does not leak · [10](../labs/07/10-the-plugin-the-kubelet-calls.md) stage 2, real pods on the worker · [11](../labs/07/11-two-nodes-two-pod-cidrs-no-route.md) two pod CIDRs, no route · [12](../labs/07/12-a-malformed-result-at-the-cri-seam.md) a malformed result at the CRI seam · [13](../labs/07/13-a-second-plugin-in-the-chain.md) a second plugin in the chain.

<a id="m7-3"></a>
### Module 7.3 — The Service dataplane: kube-proxy (~1 week)

Where P6's trace debt is repaid in source. Read the small model files first — the routinely-skipped correct on-ramp.

**Read**

| Item | Answer from it |
|---|---|
| `pkg/proxy/{serviceport.go, endpoint.go, servicechangetracker.go, endpointschangetracker.go, topology.go}` (item 10, **first**) | kube-proxy's backend-agnostic model. How are changes accumulated between syncs, and how does `topology.go` filter endpoints? **`endpointschangetracker` is the P6-trace hop you could only watch.** |
| `endpointslice/reconciler.go` (item 8) + `endpointslice_controller.go` (item 9) | The pod→endpoint mapping and churn-minimising slice packing — the most readable substantial networking code in the tree. This is the reconciler [P6](06-kubelet-node.md)'s trace named as owed. |
| `iptables/proxier.go` `syncProxyRules` **only** (item 15) + `nftables/proxier.go` `syncProxyRules` (item 16) + KEP-3866/5343 | `KUBE-SERVICES`/`KUBE-SVC-*`/`KUBE-SEP-*` chains vs nftables verdict maps. **Read each beside a live dump.** What is the structural reason nftables scales where iptables' chain-per-service does not? |
| KEP-265 + KEP-5495 (items 13–14) + `external-lb-source-ip-preservation.md` (item 30) | IPVS as **comparative/historical only** (it's being deprecated), and why `externalTrafficPolicy: Local` exists and what it costs on `factory`'s NAT'd bridge. |

**Labs** — [14](../labs/07/14-the-model-files-before-the-machine.md) the model files before the machine · [15](../labs/07/15-the-reconciler-and-its-packing-heuristic.md) `reconciler.go`, cited · [16](../labs/07/16-a-clusterip-followed-to-its-kube-sep.md) a ClusterIP followed to its `KUBE-SEP` · [17](../labs/07/17-the-same-service-as-a-verdict-map.md) the same Service as a verdict map · [18](../labs/07/18-the-tracker-between-two-syncs.md) the tracker between two syncs · [19](../labs/07/19-7c3-delete-one-endpoint-rule.md) drill 7.C3 · [20](../labs/07/20-7c1-a-partition-named-by-path.md) drill 7.C1 · [21](../labs/07/21-an-address-claimed-by-arp.md) an address claimed by ARP · [22](../labs/07/22-three-backends-one-table.md) three backends, one table.

<a id="m7-4"></a>
### Module 7.4 — NetworkPolicy and DNS (~4 days)

The semantics live in the type comments; enforcement lives in the CNI, not in Kubernetes.

**Read**

| Item | Answer from it |
|---|---|
| `networking/v1/types.go` NetworkPolicy types (item 20) + `network-policy.md` (item 21) | **The normative semantics are the comments:** the default-allow→default-deny flip on selection, ingress/egress rule *union*, and `podSelector`+`namespaceSelector` **AND-vs-OR** — the classic mistake. Where does the doc say **k8s ships no enforcer**? |
| KEP-2091 AdminNetworkPolicy (item 22) | Cluster-scoped, explicitly-ordered Allow/Deny/Pass — fixing NetworkPolicy's inability to express a real deny. **Strong [CKS](10-security.md) material** — banked toward P10. |
| CoreDNS + the *It Wasn't DNS* method (talk) | How a pod resolves a Service name: `resolv.conf`, the `ndots` trap, the CoreDNS Service behind it. What are the first three things the diagnostic method checks? |

**Labs** — [23](../labs/07/23-a-policy-nobody-enforces.md) a policy nobody enforces · [24](../labs/07/24-the-semantics-are-in-the-comments.md) ten questions sealed before an enforcer exists · [25](../labs/07/25-a-name-resolved-in-five-hops.md) a name resolved in five hops · [26](../labs/07/26-7c2-it-was-dns.md) drill 7.C2 · [27](../labs/07/27-adminnetworkpolicy-read-and-banked.md) AdminNetworkPolicy, read and banked.

<a id="m7-5"></a>
### Module 7.5 — eBPF, and build artifact 2 (~1 week)

The datapath's future, loaded into a real kernel — so Cilium's "it uses eBPF" becomes personal in module 7.6.

**Read**

| Item | Answer from it |
|---|---|
| `cilium/.../bpf/architecture.rst` + `progtypes.rst` (item 29) | The eBPF primer: program types, maps, the verifier, tail calls, JIT. Readable without Cilium context. What does the verifier reject, and why? |
| `cilium/.../network/ebpf/lifeofapacket.rst` (item 28) | **"Life of a Packet":** which hooks (XDP, tc ingress/egress, socket) a packet traverses and where policy is enforced. `iptables.rst` contrasts explicitly with kube-proxy. |

**Gate — [kernel lockstep](../strands/build-mechanics.md#kernel-lockstep):** CO-RE resolves against `/sys/kernel/btf/vmlinux`, so `forge`'s kernel must match the node's. **`uname -r` on `forge` and the target node must be equal before the program loads** — a mismatch is a stop-and-fix, not a warning, because the failure is either a verifier rejection or a *silently wrong field offset*.

**Labs** — [28](../labs/07/28-a-counter-loaded-attached-read-detached.md) **artifact 2**, five verbs each proven · [29](../labs/07/29-a-mismatched-btf-and-the-two-ways-it-fails.md) the mismatched-BTF drill · [30](../labs/07/30-a-drop-decided-by-a-map-entry.md) a drop decided by a map entry.

<a id="m7-6"></a>
### Module 7.6 — Cilium (~4 days)

Entered **after** the eBPF artifact exists — detailed as ecosystem in [§5](#ecosystem), this is its hands-on. It is also the module that changes the cluster's tenancy: Cilium is not co-resident with the heavy tooling on this host, so it arrives only once the drills that need Chaos Mesh are done and Chaos Mesh has come out. Ordering, not a bigger guest — the [lab index](../labs/07/README.md) has the sequence.

**Labs** — [31](../labs/07/31-kube-proxy-replaced-by-map-lookups.md) kube-proxy replaced by map lookups · [32](../labs/07/32-the-prediction-scored-at-the-datapath.md) the prediction scored at the datapath · [33](../labs/07/33-7c4-a-policy-that-reads-correct.md) drill 7.C4.

---

<a id="chaos"></a>
## 3. Chaos drills

**Chaos Mesh is now installed** (since [P6](06-kubelet-node.md)); network faults are exactly where its [one-Linux-primitive-per-fault](../strands/chaos.md#mechanisms) design pays off — `NetworkChaos` is `netem` on a qdisc, `DNSChaos` is CoreDNS running the `k8s_dns_chaos` plugin. The two by-hand drills stay by-hand because reading the broken rule is the lesson.

| # | Drill | What you must produce afterwards |
|---|---|---|
| [7.C1](../labs/07/20-7c1-a-partition-named-by-path.md) | **Network partition** | Which of the four communication paths broke, and the `tc -s qdisc show` evidence |
| [7.C2](../labs/07/26-7c2-it-was-dns.md) | **DNS failure** | Every name-based connection failing while IPs still work — the *It Wasn't DNS* signature |
| [7.C3](../labs/07/19-7c3-delete-one-endpoint-rule.md) | **Corrupt kube-proxy rules** | The half-broken Service mapped to the specific missing `KUBE-SEP`/verdict-map entry |
| [7.C4](../labs/07/33-7c4-a-policy-that-reads-correct.md) | **A NetworkPolicy that lies** | Why the policy reads correct but over-/under-allows, proven at the datapath |

7.C3 and 7.C4 are by-hand because the exercise *is* reading the rule that broke.

---

<a id="talks"></a>
## 4. Talks

Full entries under [Networking](../strands/talks.md#networking) and [eBPF](../strands/talks.md#ebpf).

- **★ Container Networking From Scratch** (Jacobs, NA 2018) — the P0 networking talk: builds it live from `ip netns`, veth, bridges and routes, no Kubernetes. **Everything in module 7.1 becomes derivable afterwards.** Reproducible on one Debian VM.
- **★ Kubernetes Networking: How to Write a CNI Plugin From Scratch** (Yanay, EU 2019) — CNI as a spec for an executable that receives JSON and wires a netns — **module 7.2 in talk form.**
- **★ Kubernetes Networking Intro and Deep-Dive** (Du & Hockin, EU 2020, 80 min) — the canonical Service/EndpointSlice data model and kube-proxy modes from the people who designed them. The 80 minutes replace three shorter talks; watch against module 7.3.
- **★ eBPF and Kubernetes: Little Helper Minions** (Borkmann, EU 2020) — the reference eBPF talk from a kernel maintainer: verifier, maps, program types, tc/XDP hooks — *why* eBPF is fast, not just that it is. Watch before module 7.5.
- **★ Logs Told Us It Was DNS… It Wasn't DNS** (Bernaille & Andrews, EU 2022) — **the best diagnostic-method talk in the corpus**, and DNS is where this phase's failures actually live. The procedure behind drill 7.C2.

---

<a id="ecosystem"></a>
## 5. Ecosystem

**Cilium** — entered *after* the eBPF artifact exists, so "Cilium uses eBPF" is a statement about something you have personally loaded into a kernel, not a slogan.

- **Hands-on:** [module 7.6](#m7-6) — install it in kube-proxy-replacement mode and read its *Life of a Packet* against your own program.
- **Internals note (required):** k8s ships **no NetworkPolicy enforcer** — Cilium is one, in eBPF. It replaces kube-proxy's iptables/nftables `syncProxyRules` with **eBPF map lookups**: the ClusterIP→endpoint DNAT you traced in module 7.3 becomes a map entry, and policy enforcement is a program at the tc hook rather than a chain. This is the same job you read in source, done at a different layer — which is the only way to judge the claim that it's faster.
- **Maturity:** CNCF **graduated** (2023) — the first CNI to graduate, and the project that drove eBPF into mainstream Kubernetes networking. DaemonSet-shaped and **not co-resident** with Istio/Falco/Prometheus on this host ([#8](https://github.com/k3ii/k8s-academy/issues/8)); its L7 and mesh capabilities are where [P9](09-service-mesh.md) picks up.

---

<a id="capstone"></a>
## 6. Capstone

**Your CNI plugin giving pods a `ping`-able network, plus a NetworkPolicy enforcement proof read at the iptables/eBPF layer — the rule or map entry that drops the packet, not just that the connection failed.**

Two parts, plus the debt repaid:

1. **The CNI plugin** (module 7.2): real pods with connectivity from a plugin you wrote — `ADD`/`DEL`, veth, IPAM, routes.
2. **The enforcement proof** (module 7.4/7.6): a NetworkPolicy whose drop you can *point at* — the `KUBE-SEP` absence, the iptables `DROP`, or the Cilium policy-map entry / `cilium monitor` event. "The connection failed" is not a proof; the packet's fate in the datapath is.
3. **P6's trace debt repaid** (module 7.3): the far half of [corpus trace #2](../strands/source-reading.md#trace-pod-dies) — `EndpointSlice reconciler → endpointschangetracker → syncProxyRules` — now cited in source, closing the seam P6 could only observe.

**Cite `file:line` a hostile reader could check** — at minimum: the `syncProxyRules` DNAT site (name the backend); the `reconciler.go` pod→endpoint mapping; and the datapath location of your policy drop. Every path verified live per [P2's archaeology standard](../strands/source-archaeology.md#drills) — the `proxier.go` files are 60+ KB, so a copied line number rots fast.

**Lab** — [exercise 34](../labs/07/34-the-capstone-a-network-you-wrote-and-a-drop-you-can-point-at.md), which is also where the topology goes.

---

<a id="checklist"></a>
## 7. Checklist

Concrete, demonstrable, grouped by evidence type. No item says *understand* or *know*.

**Live against a running cluster:**
- [ ] Two `ip netns` `ping` each other with hand-wired veth/bridge/routes (7.1).
- [ ] Real pods get a `ping`-able network from your CNI plugin (7.2).
- [ ] A Service packet traced to its DNAT rule in *both* iptables and nftables dumps (7.3).
- [ ] An eBPF program loaded, attached, its map read, and detached — kernel lockstep verified (7.5).
- [ ] Cilium installed; a policy drop shown at the eBPF layer (7.6).

**Build artifacts:**
- [ ] Artifact 1: the CNI plugin (`ADD`/`DEL`, on-node).
- [ ] Artifact 2: the `cilium/ebpf` program (compile/load/attach/read-map/detach).

**Written artifacts (each is a module's Write-down):**
- [ ] The by-hand netns wiring, mapped to what the CNI automates (7.1).
- [ ] The `ADD` handler steps mapped to the by-hand commands (7.2).
- [ ] The ClusterIP→endpoint DNAT path with `syncProxyRules` `file:line`, both backends (7.3).
- [ ] The NetworkPolicy AND-vs-OR rule and the DNS diagnostic checklist (7.4).
- [ ] The eBPF load→attach→read-map→detach sequence + the `uname -r` gate (7.5).
- [ ] The policy-drop map entry / `cilium monitor` event (7.6).

**Falsifiable claims — write, then verify:**
- [ ] Why `Endpoints` didn't scale and slicing fixed it (KEP-752).
- [ ] The structural reason nftables scales where iptables' chain-per-service doesn't.
- [ ] Why NetworkPolicy needs a CNI to enforce it (k8s ships no enforcer).

---

<a id="gate"></a>
## 8. Gate

You may advance to [P8](08-storage.md) when:

1. **The CNI plugin gives pods a `ping`-able network**, and you can name every step it automates against the by-hand `ip netns` wiring. If the plugin works but you can't map it back to the primitives, [P0](00-linux-primitives.md) didn't land — **stay here**.
2. **A NetworkPolicy drop is proven at the datapath** — you point at the rule or map entry that drops the packet, cited. "The connection failed" does not pass this gate.
3. **P6's trace debt is repaid and the eBPF program ran in a real kernel** — trace #2's far half is now cited in `syncProxyRules`/`reconciler.go`, and Cilium's "it uses eBPF" is a claim about something you personally loaded. The seam P6 could only watch is closed in source.

Networking is the last major subsystem below the abstraction line except one. [P8](08-storage.md) opens storage — the CSI datapath, the PVC-bound-and-mounted trace — and then closes the drill block with **CKA**, the first exam since CKAD at [P1](01-operate-shallow.md).
