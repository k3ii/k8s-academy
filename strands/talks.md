# Talks

73 conference talks, every URL verified against YouTube itself rather than recalled.
No keynotes; mechanism over release notes. **40 are marked ★** as earning their
runtime unconditionally, and of those the [viewing spine](#spine) names the 24 to
watch first, in dependency order — that is the set the curriculum actually commits to.
Everything unmarked is a labelled second pass, kept because it closes a stated gap or
is cheap relative to what it teaches.

Derived from [`../research/kubecon-talks.md`](../research/kubecon-talks.md), research
date 2026-08-17. Runtimes are exact video durations, not scheduled slot lengths.

## Which phase watches what

| Phase | Anchors |
|---|---|
| P0 Linux primitives | [Networking](#networking) — *Container Networking From Scratch* is reproducible on one VM |
| P1 Operate shallow | [Debugging](#debugging) |
| P2 etcd | [etcd](#etcd) — five ★ talks, the densest area in the corpus |
| P3 API machinery | [API server](#apiserver) · [CRDs and operators](#crds) |
| P4 Controllers | [Controllers](#controllers) |
| P5 Scheduler | [Scheduler](#scheduler) |
| P6 kubelet / node | [Node](#node) |
| P7 Networking | [Networking](#networking) · [eBPF and Cilium](#ebpf) |
| P8 Storage | [Storage](#storage) |
| P9 Mesh | [Service mesh](#mesh) |
| P10 Security | [Security](#security) |
| P11 Synthesis | [Debugging](#debugging) — the postmortems read differently once the internals are known |
| Chaos strand | [Chaos](#chaos), but see below |

**The chaos strand does not source from the chaos area.** Two talks exist and both are
tool pitches; there is no maintainer-grade deep dive in this corpus. The strand takes
its material from [Debugging](#debugging)'s postmortems instead — which is a
curriculum decision, recorded in
[#4](https://github.com/k3ii/k8s-academy/issues/4), not an omission.

---

<a id="spine"></a>
## The viewing spine — the ★ CORE 24, in order

Ordered so each talk's prerequisites are already watched. Total runtime ≈ **14h20m**
across the whole curriculum — roughly twenty minutes a week over a year, which is
why this strand is a spine and not a module.

| # | Area | Talk | Runtime |
|---|---|---|---|
| 1 | Node primitives | Container Networking From Scratch (Jacobs) | 34:44 |
| 2 | Debugging | CrashLoopBackoff, Pending, FailedMount and Friends (Thompson) | 34:54 |
| 3 | etcd | Understanding Distributed Consensus in etcd and Kubernetes (Frank) | 37:00 |
| 4 | API server | The Life (or Death) of a Kubernetes API Request, 2025 Edition (Kashem/Schimanski) | 30:49 |
| 5 | API server | Life of a Kubernetes API Request (Smith) — for the *why* | 44:07 |
| 6 | etcd | Deep Dive: etcd (Xiang Li/Wenjia Zhang) | 45:52 |
| 7 | etcd | Debugging etcd (Betz/Hu) | 42:36 |
| 8 | etcd | Secrets of Running Etcd (Siarkowicz) | 40:33 |
| 9 | etcd | Lessons Learned From Etcd the Data Inconsistency Issues (Siarkowicz/Wang) | 35:24 |
| 10 | Controllers | The Life of a Kubernetes Watch Event (Zhang/Cai) | 33:00 |
| 11 | Controllers | client-go: The Good, The Bad and The Ugly (Cosic) | 24:16 |
| 12 | Controllers | Don't Write Controllers Like Charlie Don't Does (Young) | 31:38 |
| 13 | API machinery | Deep Dive Into API Machinery (Pelisse/Schimanski) | 27:36 |
| 14 | API machinery | A Vision For API Machinery (Smith) | 40:38 |
| 15 | CRDs | Extending the Kubernetes API: What the Docs Don't Tell You (Munnelly) | 33:46 |
| 16 | Scheduler | Deep Dive Into the Latest Kubernetes Scheduler Features (Gharaibeh) | 41:37 |
| 17 | Scheduler | SIG-Scheduling Deep Dive (Huang/Wang/Yin/Nakada) | 38:43 |
| 18 | Node | Evicted! All the Ways Kubernetes Kills Your Pods (Balkan) | 28:11 |
| 19 | Node | Cgroupv2 Is Coming Soon To a Cluster Near You (Porter/Patel) | 45:44 |
| 20 | Node | Who Killed My Pod? #Whodunit (Mall) | 31:54 |
| 21 | Networking | Kubernetes Networking Intro and Deep-Dive (Du/Hockin) | 1:19:50 |
| 22 | Networking | Kubernetes Networking: How to Write a CNI Plugin From Scratch (Yanay) | 33:14 |
| 23 | Networking | Scaling Kubernetes Networking Beyond 100k Endpoints (Scott/Xia) | 38:30 |
| 24 | Debugging | Logs Told Us It Was DNS… It Wasn't DNS (Bernaille/Andrews) | 36:14 |

Then, gated on the relevant phase: `Operating kube-apiserver Without Hiccups` · `The Cluster Killer Bug (APF)` · `Webhook Fatigue? (CEL)` · the three eBPF/Cilium talks · `Intro + Deep Dive: Kubernetes Storage SIG` · the remaining postmortems · `Envoy Internals Deep Dive` · `Life of a Packet: Ambient Edition` · the four security talks.

---

<a id="etcd"></a>
## 1. etcd internals, Raft, watch, operational failure and recovery

### ★ Understanding Distributed Consensus in etcd and Kubernetes
- **Speaker:** Laura Frank, CloudBees
- **Conference:** KubeCon + CloudNativeCon EU 2018 (Copenhagen)
- **URL:** https://www.youtube.com/watch?v=n9VKAKwBj_0 · **37:00**
- **Why:** The best first-principles Raft explanation in the corpus — leader election, log replication and quorum built up from the problem statement rather than from etcd's API. Watch this *before* any etcd maintainer deep-dive.
- **Ages well.** It is algorithm content; nothing in it has moved.

### ★ Deep Dive: etcd
- **Speakers:** Xiang Li (Alibaba — etcd co-creator) & Wenjia Zhang (Google)
- **Conference:** KubeCon + CloudNativeCon NA 2018 (Seattle)
- **URL:** https://www.youtube.com/watch?v=GJqO1TYzVDE · **45:52**
- **Why:** The best entry instalment of the long-running `Deep Dive: etcd` maintainer series — storage engine layout, MVCC revisions, watch, compaction and the operational consequences of each, from the person who wrote it.
- **Series note:** the series runs most years. Later instalments (e.g. `Deep Dive: etcd — Jingyi Hu`, https://www.youtube.com/watch?v=DrtdrdwDpZE · 39:52, upload July 2019, **most likely KubeCon China 2019 (Shanghai) — event attribution hedged**) cover the same ground with different emphasis. Start here; only chase others for a specific subsystem.
- **Mildly stale:** pre-3.5 specifics on defrag tooling and the `--experimental-*` flag surface. The MVCC/watch/compaction mechanics are unchanged.

### ★ Debugging etcd
- **Speakers:** Joe Betz & Jingyi Hu, Google
- **Conference:** KubeCon + CloudNativeCon NA 2018 (Seattle)
- **URL:** https://www.youtube.com/watch?v=NVMZBBQ9hsM · **42:36**
- **Why:** Highest-value etcd talk for the learner's diagnosis goal — how to read etcd's metrics and logs to distinguish disk-fsync stalls from network latency from leader-election churn, with the actual signals named. This is the talk that makes "etcd is slow" a falsifiable statement.
- **Ages well** — the metric names and failure taxonomy are still current.

### ★ Secrets of Running Etcd
- **Speaker:** Marek Siarkowicz, Google (etcd maintainer)
- **Conference:** KubeCon + CloudNativeCon NA 2023 (Chicago)
- **URL:** https://www.youtube.com/watch?v=aJVMWcVZOPQ · **40:33**
- **Why:** The modern operational counterpart to the 2018 deep dive: why etcd is latency-sensitive at the disk layer, how compaction and defrag interact with cluster size, and what actually breaks at scale. Directly applicable to running a single-node etcd on a cramped homelab and watching it degrade.
- **Ages well.**

### ★ Lessons Learned From Etcd the Data Inconsistency Issues
- **Speakers:** Marek Siarkowicz (Google) & Benjamin Wang (VMware) — both etcd maintainers
- **Conference:** KubeCon + CloudNativeCon NA 2022 (Detroit)
- **URL:** https://www.youtube.com/watch?v=_nSJ_vozyqk · **35:24**
- **Why:** A maintainer-authored postmortem of a real correctness bug that shipped — how a distributed-consensus datastore can lose linearizability without anyone noticing, and what testing did not catch it. This is the rare talk that teaches distrust of your own storage layer.
- **Ages well** (it is history). **Follow-up instalment:** `On the Hunt for Etcd Data Inconsistencies` — Marek Siarkowicz, KubeCon EU 2023 — https://www.youtube.com/watch?v=IIMs0EjQZHg · **42:08** — the payoff talk: the model-based/deterministic robustness testing framework built in response. Watch the 2022 talk first.

### Second pass
- `Dr etcd; or; How I Learned to Stop Worrying and Love the Datastore` — Nick Young, VMware — KubeCon NA 2019 — https://www.youtube.com/watch?v=CE9uwBoSk-8 · **18:39**. Cheap orientation talk; good as a warm-up before the Frank talk if etcd feels abstract.
- `Forging a Stronger Bond Between Etcd and Kubernetes` — Siarkowicz, Wenjia Zhang, James Blair — KubeCon NA 2023 — https://www.youtube.com/watch?v=6JYgBJAjpNQ · **36:28**. On the apiserver↔etcd contract; useful *after* the API server area below.

**Honest gap:** there is no strong, standalone "we lost quorum in production and here is the recovery" war story in the CNCF corpus with a verifiable recording. The closest real-incident content is inside `Lessons Learned` and `Secrets of Running Etcd`. Disaster-recovery drilling will have to be a lab, not a talk.

---

<a id="apiserver"></a>
## 2. API server internals, admission control, API Priority and Fairness

### ★ The Life (or Death) of a Kubernetes API Request, 2025 Edition
- **Speakers:** Abu Kashem & Stefan Schimanski (SIG API Machinery)
- **Conference:** KubeCon + CloudNativeCon EU 2025 (London)
- **URL:** https://www.youtube.com/watch?v=Hc0jj-654lA · **30:49**
- **Why:** **The single best entry point to the whole control plane.** Traces one request end to end — authn, authz, APF queueing, admission chain, storage encode, etcd write, watch fan-out — with the modern APF and CEL stages in place. This is the spine every other apiserver talk hangs off.
- **Ages well**, and is recent enough to be the current picture.

### ★ Life of a Kubernetes API Request
- **Speaker:** Daniel Smith, Google (SIG API Machinery lead)
- **Conference:** KubeCon + CloudNativeCon NA 2016 (Seattle)
- **URL:** https://www.youtube.com/watch?v=ryeINNfVOi8 · **44:07**
- **Why:** The original. Slower and more patient than the 2025 edition, and better on *why* the API machinery is shaped this way — declarative intent, resource versions, optimistic concurrency, watch semantics.
- **STALE-BUT-USEFUL:** predates APF entirely, predates CRDs reaching v1, predates ValidatingAdmissionPolicy/CEL, and its admission discussion assumes compiled-in admission plugins rather than webhooks. Watch it for the model, not the pipeline stages. If time is short, watch the 2025 edition instead and come back to this only if the *why* is still murky.

### ★ Operating kube-apiserver Without Hiccups
- **Speakers:** Stefan Schimanski & David Eads, Red Hat
- **Conference:** KubeCon + CloudNativeCon EU 2019 (Barcelona)
- **URL:** https://www.youtube.com/watch?v=pED17NXiexw · **25:56**
- **Why:** Graceful termination, readiness semantics, and what actually happens to in-flight requests and watches during an apiserver rollout. Almost nothing else covers the apiserver *lifecycle*, and it is exactly the knowledge needed to upgrade a control plane without dropping traffic.
- **Ages well;** some self-hosting details are dated to the OpenShift context of the time.

### ★ The Cluster Killer Bug: Learning API Priority and Fairness the Hard Way
- **Speaker:** Eddie Zaneski, Independent
- **Conference:** KubeCon + CloudNativeCon NA 2023 (Chicago)
- **URL:** https://www.youtube.com/watch?v=4mYUyAeyr-U · **34:59**
- **Why:** APF taught through a real outage — how a well-behaved-looking client saturated a priority level and took the control plane down, and how it was diagnosed from the APF metrics. Pair it with the mechanism talk below and the APF metrics stop being noise.
- **Ages well.**

### API Priority and Fairness: Kube-APIServer Flow-control Protection
- **Speaker:** Min Jin, Ant Group (SIG API Machinery)
- **Conference:** KubeCon + CloudNativeCon NA 2020 (virtual)
- **URL:** https://www.youtube.com/watch?v=Tps4eAjuCr8 · **29:46**
- **Why:** The design talk for APF from a designer: priority levels, FlowSchemas, seat accounting, and why the apiserver previously had no defence against one bad client.
- **STALE-BUT-USEFUL:** predates APF's GA (1.29). API group versions shown (`flowcontrol.apiserver.k8s.io/v1beta1`) and some defaults have changed; the concurrency-sharing model has not.

### ★ Webhook Fatigue? You're Not Alone: Introducing the CEL Expression Language Features...
- **Speaker:** Joe Betz, Google (SIG API Machinery tech lead)
- **Conference:** KubeCon + CloudNativeCon NA 2022 (Detroit)
- **URL:** https://www.youtube.com/watch?v=gJWMvsC7Mzo · **35:15**
- **Why:** Explains admission by explaining what is *wrong* with webhook admission — latency in the request path, availability coupling, failure-policy tradeoffs — and why CEL-in-apiserver was the answer. The best available "how admission control actually costs you" talk.
- **STALE-BUT-USEFUL:** this is the prequel to ValidatingAdmissionPolicy, which went GA in 1.30. The motivation and CEL mechanics are current; the feature status and API shape are not. Pair with the CEL talk below.

### Second pass
- `A Field Guide To Integrating CEL in the Kubernetes Codebase` — Sreeram Venkitesh & Priyanka Saggu — KubeCon EU 2025 — https://www.youtube.com/watch?v=ODI3KwDLKas · **33:24**. Unusually good fit for the "read the source" strand: it walks the actual `k/k` CEL integration points rather than the user-facing API.
- `SIG API Machinery Deep Dive` — Abu Kashem, Stefan Schimanski, Joe Betz, Federico Bongiovanni — KubeCon NA 2021 — https://www.youtube.com/watch?v=oiC2w1PVjrQ · **29:37**. The instalment with the APF and CEL authors in the room.

---

<a id="crds"></a>
## 3. CRDs, aggregation, operator patterns and anti-patterns

### ★ Extending the Kubernetes API: What the Docs Don't Tell You
- **Speaker:** James Munnelly, Jetstack
- **Conference:** KubeCon + CloudNativeCon NA 2017 (Austin)
- **URL:** https://www.youtube.com/watch?v=PYLFZVv68lM · **33:46**
- **Why:** Still the clearest treatment of the actual decision — CRD vs aggregated API server — and what each gives up (validation, subresources, storage control, versioning/conversion). Most later talks assume the CRD answer without arguing for it.
- **STALE-BUT-USEFUL:** from the CRD-beta era. Structural schemas, CRD conversion webhooks, `x-kubernetes-validations` (CEL) and server-side apply all postdate it, and several of its "CRDs can't do this" caveats have since been fixed. The tradeoff *axes* are still the right ones.

### ★ Deep Dive Into API Machinery
- **Speakers:** Antoine Pelisse (Google) & Stefan Schimanski (Red Hat)
- **Conference:** KubeCon + CloudNativeCon NA 2019 (San Diego)
- **URL:** https://www.youtube.com/watch?v=qTm-g3vtVOE · **27:36**
- **Why:** Best entry instalment of the `SIG API Machinery Deep Dive` series: group/version/kind machinery, the scheme and conversion, and how extension points hang off it. Short, dense, and the vocabulary it installs makes `k/k` navigable.
- **Series note:** the series runs most KubeCons; do not watch them all. This one, then the 2021 instalment above if you want APF/CEL author commentary.

### ★ A Vision For API Machinery: Coming to Terms with the Platform We Built
- **Speaker:** Daniel Smith, Google
- **Conference:** KubeCon + CloudNativeCon NA 2018 (Seattle)
- **URL:** https://www.youtube.com/watch?v=u6weI_3WVTM · **40:38**
- **Why:** A design-philosophy talk from the person who owns the API machinery — what Kubernetes' API is *for*, where the abstractions leak, and which extension mechanisms are load-bearing vs accidental. This is the talk that makes operator design decisions feel principled instead of cargo-culted.
- **Ages well** — it is almost entirely about invariants.

### Implementing Anti-patterns: Kubernetes Cross-namespace Resource Ownership
- **Speaker:** Tom Coufal, Red Hat
- **Conference:** KubeCon + CloudNativeCon EU 2022 (Valencia)
- **URL:** https://www.youtube.com/watch?v=iWz5AAbbT-c · **33:17**
- **Why:** A concrete operator anti-pattern taken seriously: owner references don't cross namespaces, garbage collection therefore does the wrong thing, and the workarounds all cost something. Better than generic "operator best practices" talks because it has one real failure mode and follows it down.
- **Ages well.**

**Honest gap:** the CNCF corpus has no great *general* "operator anti-patterns" talk — the genre is dominated by SDK/framework pitches. The controller-mistakes talk in area 5 (`Charlie Don't Does`) is the better substitute.

---

<a id="scheduler"></a>
## 4. Scheduler internals, scheduling framework, preemption, scheduling at scale

### ★ Deep Dive Into the Latest Kubernetes Scheduler Features
- **Speaker:** Abdullah Gharaibeh, Google (SIG Scheduling)
- **Conference:** KubeCon + CloudNativeCon NA 2019 (San Diego)
- **URL:** https://www.youtube.com/watch?v=eDkE4WNWKUc · **41:37**
- **Why:** The best available walk through the **scheduling framework** — the extension-point sequence (filter/score/reserve/permit/bind), how preemption picks victims and why it can fail to make room, and pod priority's interaction with the scheduling queue. Despite the release-notes title, most of the runtime is mechanism.
- **Mildly stale:** framework plugin names and some feature gates have moved on; the extension-point model and preemption algorithm are unchanged.

### ★ SIG-Scheduling Deep Dive
- **Speakers:** Wei Huang (Apple), Qingcan Wang (Alibaba), Kante Yin, Kensei Nakada
- **Conference:** KubeCon + CloudNativeCon NA 2022 (Detroit)
- **URL:** https://www.youtube.com/watch?v=1GpTE9L9oBM · **38:43**
- **Why:** Best entry instalment of the SIG Scheduling maintainer track — the scheduling queue's actual behaviour (backoff, unschedulable pods, requeueing hints) which is exactly where mental models of the scheduler usually break.
- **Series note:** later instalments are increasingly about workload/AI scheduling (Kueue, gang scheduling) rather than core internals; watch this one for internals and only chase newer ones if batch/GPU scheduling becomes relevant.

### Kubernetes Scheduling Features or How Can I Make the System Do What I Want?
- **Speaker:** Marek Grabowski, Google
- **Conference:** KubeCon + CloudNativeCon EU 2017 (Berlin)
- **URL:** https://www.youtube.com/watch?v=bbPcb2JuJPw · **34:07**
- **Why:** Pre-framework, so it explains predicates/priorities as raw functions over node lists — which is *conceptually clarifying* precisely because it lacks the plugin abstraction.
- **STALE-BUT-USEFUL:** the predicate/priority API it describes was replaced by the scheduling framework in 1.19, and node affinity syntax shown is dated. Value is entirely conceptual; skip if short on time.

### Second pass
- `Enhancing the Kubernetes Scheduler for Diverse Workloads in Large Clusters` — Yuan Chen & Yan Xu — https://www.youtube.com/watch?v=0O_06RNEiL4 · **29:34**. Scheduling-at-scale throughput characteristics.
- `A Tale of Two Plugins: Safely Extending the Kubernetes Scheduler with WebAssembly` — Kensei Nakada — https://www.youtube.com/watch?v=TfS2ONQGlC4 · **32:19**. Teaches the framework's plugin contract from the outside in.

---

<a id="controllers"></a>
## 5. Controllers, reconciliation, client-go internals, informer behaviour

### ★ The Life of a Kubernetes Watch Event
- **Speakers:** Wenjia Zhang & Haowei Cai, Google
- **Conference:** KubeCon + CloudNativeCon NA 2018 (Seattle)
- **URL:** https://www.youtube.com/watch?v=PLSDvFjR9HY · **33:00**
- **Why:** **The most load-bearing talk in this entire document for anyone writing a controller.** Follows a single change from the etcd watch, through the apiserver watch cache, over the wire, into the client-go reflector, DeltaFIFO, indexer and workqueue. Explains resource versions, relist-on-`410 Gone`, and why informers are eventually consistent — i.e. why level-triggered reconciliation is not a style preference.
- **Ages well.** Watch-cache internals have been optimised since (consistent reads from cache, watch bookmarks, streaming list) but the pipeline stages are the same.

### ★ client-go: The Good, The Bad and The Ugly
- **Speaker:** Lili Cosic, Kinvolk
- **Conference:** KubeCon + CloudNativeCon NA 2017 (Austin)
- **URL:** https://www.youtube.com/watch?v=Q88kI8X5R48 · **24:16**
- **Why:** Short, honest tour of client-go's moving parts and their sharp edges — informer/lister/workqueue wiring, rate limiting, and the ergonomics that trip people up. The best 24 minutes available on the library itself.
- **Mildly stale:** generated-client and codegen ergonomics have changed; `controller-runtime` now hides much of this. Still the right talk if you are wiring a reconcile loop *by hand* — which is exactly the plan: [#9](https://github.com/k3ii/k8s-academy/issues/9) settled that the first operator is hand-wired `client-go`, with `kubebuilder` deliberately held back until afterwards. The "sharp edges" in this talk are the ones you will hit.

### ★ Don't Write Controllers Like Charlie Don't Does: Avoiding Common Kubernetes Controller Mistakes
- **Speaker:** Nick Young, Isovalent at Cisco
- **Conference:** KubeCon + CloudNativeCon EU 2025 (London)
- **URL:** https://www.youtube.com/watch?v=tnSraS9JqZ8 · **31:38**
- **Why:** The current, opinionated catalogue of controller bugs — status vs spec confusion, non-idempotent reconciles, hot loops, requeue misuse, cross-resource ordering assumptions. Recent enough to reflect modern practice and specific enough to act on.
- **Ages well.**

### Second pass
- `Writing Kube Controllers for Everyone` — Maciej Szulik, Red Hat — KubeCon EU 2018 — https://www.youtube.com/watch?v=AUNPLQVxvmw · **37:23**. Labelled beginner, but a genuinely careful build-up of the reconcile loop from a `k/k` controller maintainer. Good scaffold *before* the client-go talk.
- `Controllers at Chaos` — Kesavan Subramanian & Gaurav Gupta, SAP — https://www.youtube.com/watch?v=kQT82Qx97L4 · **31:37**. Controller behaviour under injected failure; doubles as chaos content (area 13).

---

<a id="networking"></a>
## 6. Pod networking from first principles, kube-proxy, EndpointSlice, CNI

### ★ Container Networking From Scratch
- **Speaker:** Kristen Jacobs, Oracle
- **Conference:** KubeCon + CloudNativeCon NA 2018 (Seattle)
- **URL:** https://www.youtube.com/watch?v=6v_BDHIgOY8 · **34:44**
- **Why:** **The Phase-0 networking talk.** Builds container networking live from `ip netns`, veth pairs, bridges and routes — no Kubernetes, no CNI, no abstraction. Everything in Kubernetes networking becomes derivable afterwards. Directly reproducible on a single Debian VM, which matters given the RAM ceiling.
- **Ages well.** Linux primitives don't move.

### ★ Kubernetes Networking Intro and Deep-Dive
- **Speakers:** Bowei Du & Tim Hockin, Google (SIG Network)
- **Conference:** KubeCon + CloudNativeCon EU 2020 (virtual)
- **URL:** https://www.youtube.com/watch?v=tq9ng_Nz9j8 · **1:19:50**
- **Why:** The long-form canonical treatment from the people who designed the Service abstraction — Service/Endpoint/EndpointSlice data model, kube-proxy's iptables and IPVS modes, and the explicit design constraints that produced them. The 80 minutes are earned; it replaces three shorter talks.
- **Mildly stale:** predates the nftables kube-proxy backend and Gateway API's maturity. The Service data model and kube-proxy iptables mechanics are unchanged.

### ★ Kubernetes Networking: How to Write a CNI Plugin From Scratch
- **Speaker:** Eran Yanay, Twistlock
- **Conference:** KubeCon + CloudNativeCon EU 2019 (Barcelona)
- **URL:** https://www.youtube.com/watch?v=zmYxdtFzK6s · **33:14**
- **Why:** Demystifies CNI by revealing it as a spec for an executable that receives JSON on stdin and wires a netns. Pairs perfectly with the Jacobs talk and is a build-it-yourself lab in talk form.
- **Ages well** (CNI spec is stable); does not cover CNI 1.0/1.1 additions or dynamic device plugins.

### ★ Scaling Kubernetes Networking Beyond 100k Endpoints
- **Speakers:** Rob Scott & Minhan Xia, Google
- **Conference:** KubeCon + CloudNativeCon EU 2020 (virtual)
- **URL:** https://www.youtube.com/watch?v=a6SfbeM06Qo · **38:30**
- **Why:** The EndpointSlice origin story — why one `Endpoints` object per Service melts the apiserver and every kube-proxy at scale (O(n) watch fan-out on every pod churn). Explains a Kubernetes API design decision by the load it was fixing, which is the most transferable kind of lesson here.
- **Ages well.**

### Second pass
- `Deep Dive: CNI` — Bryan Boreham (Weaveworks) & Dan Williams (Red Hat) — KubeCon NA 2019 — https://www.youtube.com/watch?v=zChkx-AB5Xc · **39:05**. Maintainer view of the spec, chaining, and IPAM.
- `Life of a Packet [I]` — Michael Rubin, Google — KubeCon EU 2017 — https://www.youtube.com/watch?v=0Omvgd7Hg1I · **34:19**. The original packet-walk talk; heavily overlapped by the Hockin deep dive now, but a good 34-minute alternative if 80 minutes is too much.
- `Understand and Troubleshoot the "Magic" of Kubernetes Networking` — Minhan Xia & Rohit Ramkumar — KubeCon EU 2018 — https://www.youtube.com/watch?v=knIJEzTd3kc · **31:57**.

**Note on kube-proxy nftables:** there is no verified deep-dive recording in this corpus for the nftables backend (KEP-3866). Treat that as reading (the KEP) rather than a talk.

---

<a id="ebpf"></a>
## 7. eBPF and the Cilium datapath

### ★ eBPF and Kubernetes: Little Helper Minions for Scaling Microservices
- **Speaker:** Daniel Borkmann, Cilium/Isovalent (eBPF and Linux networking maintainer)
- **Conference:** KubeCon + CloudNativeCon EU 2020 (virtual)
- **URL:** https://www.youtube.com/watch?v=99jUcLt3rSk · **39:28**
- **Why:** **The reference eBPF talk**, from a kernel-side maintainer. Verifier, maps, program types, and the tc/XDP hook points — then how Cilium uses them to replace iptables-based service handling. Kernel-level enough that it explains *why* eBPF is fast rather than asserting it.
- **Ages well.** Kernel features have been added since; nothing shown is wrong.

### ★ Understanding and Troubleshooting the eBPF Datapath in Cilium
- **Speaker:** Nathan Sweet, DigitalOcean
- **Conference:** KubeCon + CloudNativeCon NA 2019 (San Diego)
- **URL:** https://www.youtube.com/watch?v=Kmm8Hl57WDU · **38:07**
- **Why:** An *operator's* eBPF talk — how to inspect loaded programs and maps, follow a packet through Cilium's datapath, and localise a fault. Rare and valuable: almost all eBPF talks sell the technology; this one debugs it.
- **Mildly stale:** Cilium's CLI/tooling and datapath structure have evolved considerably (kube-proxy replacement modes, ambient/Envoy integration). The debugging *method* transfers.

### ★ Liberating Kubernetes From Kube-proxy and Iptables
- **Speaker:** Martynas Pumputis, Cilium
- **Conference:** KubeCon + CloudNativeCon NA 2019 (San Diego)
- **URL:** https://www.youtube.com/watch?v=bIRwSIwNHC0 · **35:07**
- **Why:** The clearest side-by-side of the two datapaths: what iptables/conntrack actually does per packet for a Service, what the eBPF replacement does instead, and where each costs. Best watched immediately after the Hockin kube-proxy material for contrast.
- **Mildly stale** on Cilium feature status; the comparison is intact.

---

<a id="storage"></a>
## 8. Storage and CSI internals

### ★ Intro + Deep Dive: Kubernetes Storage SIG
- **Speaker:** Saad Ali, Google (SIG Storage lead, CSI co-author)
- **Conference:** KubeCon + CloudNativeCon EU 2019 (Barcelona)
- **URL:** https://www.youtube.com/watch?v=PcMairR7-4U · **1:16:01**
- **Why:** Best entry instalment of the SIG Storage series and the most complete account of the volume lifecycle — provision, attach, mount, the attach/detach controller vs kubelet's volume manager split, and where each step can wedge. The attach/detach boundary is the origin of most real storage incidents.
- **Mildly stale:** in-tree-to-CSI migration was in progress then and is now complete; ephemeral volumes, capacity tracking and volume health postdate it.

### Kubernetes SIG Storage Deep Dive
- **Speakers:** Xing Yang (VMware) & Mauricio Poppe (Google)
- **Conference:** KubeCon + CloudNativeCon NA 2022 (Detroit)
- **URL:** https://www.youtube.com/watch?v=_XXn3-yDZA0 · **32:18**
- **Why:** The modern update — post-migration CSI landscape, snapshots, capacity-aware provisioning. Watch after the Saad Ali deep dive to patch the staleness rather than instead of it.

### Understanding Kubernetes Storage: Getting in Deep by Writing a CSI Driver — **NOT a CNCF talk**
- **Conference:** USENIX Vault '20 (February 2020)
- **URL:** https://www.youtube.com/watch?v=drbKyJgC-sU · **31:31**
- **Why:** Included deliberately despite being out of the requested corpus: it is the only verified recording that treats CSI as *an interface you implement* — the gRPC services, the sidecar containers and what each one actually does. Nothing in the CNCF catalogue matches it for the build-it-yourself strand.
- **Flagged:** non-CNCF source; speaker attribution not carried in the video title.

**Honest gap:** storage is the weakest area in the CNCF corpus for deep internals. There is no verified "stuck volume / multi-attach incident" postmortem talk. Storage debugging will need to be lab-driven.

---

<a id="node"></a>
## 9. kubelet, eviction, cgroups, node-level debugging

### ★ Evicted! All the Ways Kubernetes Kills Your Pods (and How To Avoid Them)
- **Speaker:** Ahmet Alp Balkan, LinkedIn
- **Conference:** KubeCon + CloudNativeCon NA 2025 (Atlanta)
- **URL:** https://www.youtube.com/watch?v=jVwXcuNEDYE · **28:11**
- **Why:** **The definitive taxonomy of pod death** — kubelet node-pressure eviction vs the eviction API vs preemption vs OOMKill vs graceful node shutdown vs taint-based eviction — and which component to blame for each. Recent (Nov 2025), so it reflects the current eviction surface. Directly relevant to a resource-starved homelab where pods will die constantly.
- **Ages well** and is current.

### ★ Cgroupv2 Is Coming Soon To a Cluster Near You
- **Speakers:** David Porter (Google) & Mrunal Patel (Red Hat) — SIG Node
- **Conference:** KubeCon + CloudNativeCon NA 2022 (Detroit)
- **URL:** https://www.youtube.com/watch?v=sgyFCp1CRhA · **45:44**
- **Why:** The cgroup v1→v2 mechanics from the maintainers who did the kubelet work: the unified hierarchy, `memory.high`/`memory.max` vs v1's limits, PSI pressure metrics, and how the kubelet maps pod QoS onto cgroup trees. This is the talk that makes `/sys/fs/cgroup` readable.
- **Mildly stale on framing only** ("coming soon" — cgroup v2 is now the default on Debian 13 and required by recent Kubernetes). The mechanics are exactly right.

### ★ Who Killed My Pod? #Whodunit
- **Speaker:** Suneeta Mall, Nearmap
- **Conference:** KubeCon + CloudNativeCon NA 2021 (Los Angeles)
- **URL:** https://www.youtube.com/watch?v=eH4x5PGgDoM · **31:54**
- **Why:** A node-level forensic method: given a dead pod, work backwards through kubelet logs, container runtime state, exit codes, kernel OOM messages and cgroup accounting to name the killer. Explicitly a diagnosis-from-first-principles talk.
- **Ages well.**

### Resource Requests and Limits Under the Hood: The Journey of a Pod Spec
- **Speakers:** Kohei Ota & Kaslin Fields
- **Conference:** KubeCon + CloudNativeCon EU 2021 (virtual)
- **URL:** https://www.youtube.com/watch?v=WB3_sV_EQrQ · **24:19**
- **Why:** Traces `requests`/`limits` from YAML to scheduler arithmetic to CRI to cgroup values — including CPU shares vs quota, i.e. the actual source of CPU throttling confusion. Cheap at 24 minutes.
- **Mildly stale:** cgroup v1 units; no in-place pod resize.

### Second pass
- `SIG-Node: Intro and Deep Dive` — Sergey Kanzhelev & Dawn Chen (Google), Mrunal Patel (Red Hat) — **KubeCon NA 2024 (Salt Lake City) — attribution inferred from a Jan 2025 upload; hedged** — https://www.youtube.com/watch?v=bb0Op1G6XjQ · **56:58**. Best recent entry to the SIG Node maintainer series: kubelet responsibilities, CRI boundary, pod lifecycle ownership.

---

<a id="debugging"></a>
## 10. Cluster debugging and "we broke production" postmortems

*Weighted most generously per the ticket. These are the talks that model the diagnostic reasoning the curriculum is trying to install.*

### ★ Logs Told Us It Was DNS, It Felt Like DNS, It Had To Be DNS, It Wasn't DNS
- **Speakers:** Laurent Bernaille & Elijah Andrews, Datadog
- **Conference:** KubeCon + CloudNativeCon EU 2022 (Valencia)
- **URL:** https://www.youtube.com/watch?v=NunyPkN0n3c · **36:14**
- **Why:** **The best single debugging talk in the corpus.** A four-week incident followed all the way down: apparent DNS failures during rolling updates → conntrack table overflow → martian-packet drops → kernel source → a gRPC client reconnect algorithm. Resolution was three lines of code. It shows the *whole* method — hypothesis, instrument, disconfirm, descend a layer — which is exactly the transferable skill.
- **Ages well.**

### ★ How the OOM-Killer Deleted My Namespace, and Other Kubernetes Tales
- **Speaker:** Laurent Bernaille, Datadog
- **Conference:** KubeCon + CloudNativeCon NA 2020 (virtual)
- **URL:** https://www.youtube.com/watch?v=MrNhdmyXXKg · **31:10**
- **Why:** Several real incidents where a small node-level event produced an absurd control-plane-level outcome — including a memory-pressure kill that cascaded into namespace deletion. The lesson is about coupling and blast radius across components that look independent.
- **Ages well.**

### ★ 10 Ways to Shoot Yourself in the Foot with Kubernetes, #9 Will Surprise You
- **Speakers:** Laurent Bernaille & Robert Boll, Datadog
- **Conference:** KubeCon + CloudNativeCon EU 2019 (Barcelona)
- **URL:** https://www.youtube.com/watch?v=QKI-JRs2RIE · **37:19**
- **Why:** Ten real production failures at scale, each traced to a specific mechanism — conntrack, resource limits, DNS, controller assumptions, apiserver load. The clickbait title hides a serious talk; it is effectively a failure-mode catalogue with root causes attached.
- **Ages well** (a couple of failures involve since-fixed defaults; the mechanisms remain).

### ★ Kubernetes Failure Stories and How to Crash Your Clusters
- **Speaker:** Henning Jacobs, Zalando SE
- **Conference:** KubeCon + CloudNativeCon EU 2019 (Barcelona)
- **URL:** https://www.youtube.com/watch?v=6sDTB4eV4F8 · **29:26**
- **Why:** The canonical failure-stories talk from the person who curates `k8s.af`, covering many clusters' worth of outages with the pattern behind each. Best breadth-first survey of *how clusters actually fail* before you specialise.
- **Ages well.**

### ★ How to Break your Kubernetes Cluster with Networking
- **Speaker:** Thomas Graf, Isovalent (Cilium co-creator)
- **Conference:** KubeCon + CloudNativeCon EU 2021 (virtual)
- **URL:** https://www.youtube.com/watch?v=7qUDyQQ52Uk · **28:01**
- **Why:** Deliberate failure injection at the network layer with the observable symptoms named — MTU mismatch, asymmetric routing, conntrack exhaustion, policy misapplication — and how each *presents* to a confused operator. Doubles as a chaos-experiment design list, which the chaos area badly needs.
- **Ages well.**

### ★ CrashLoopBackoff, Pending, FailedMount and Friends: Debugging Common Kubernetes Cluster and Application Issues
- **Speaker:** Joe Thompson, Oteemo
- **Conference:** KubeCon + CloudNativeCon NA 2017 (Austin)
- **URL:** https://www.youtube.com/watch?v=7FOCG5kua1w · **34:54**
- **Why:** The systematic beginner-to-competent triage talk: for each common bad pod state, which object to inspect, in what order, and what each field actually tells you. Labelled beginner but structurally sound, and the right talk *early* in the curriculum.
- **Mildly stale:** `kubectl debug`/ephemeral containers didn't exist yet, and event/condition output has changed cosmetically. The triage order is still correct.

### Second pass
- `A Basic Kubernetes Debugging Kit: curl, jq, openssl, and Other Best Friends` — Joe Thompson — KubeCon NA 2018 — https://www.youtube.com/watch?v=QtXHkzLtqZE · **33:38**. Debugging the API and TLS layers *without* `kubectl` — valuable for the "debug the control plane itself" goal.
- `101 Ways to Crash Your Cluster` — Marius Grigoriu & Emmanuel Gomez, Nordstrom — KubeCon NA 2017 — https://www.youtube.com/watch?v=xZO9nx6GBu0 · **36:20**.
- `Surviving Day 2 — How to Troubleshoot Kubernetes Networking` — Thomas Graf — KubeCon EU 2023 — https://www.youtube.com/watch?v=920BZXvQpVs · **49:15**. Longer, more Cilium-flavoured companion to the 2021 talk.
- `Surviving From Endless Issues Coming From 7K+ Kubernetes Clusters` — Wanhae Lee & Seok-yong Hong — KubeCon NA 2022 — https://www.youtube.com/watch?v=dMwQEUl9IZg · **31:32**. Fleet-scale failure patterns.

---

<a id="mesh"></a>
## 11. Service mesh internals — Envoy, xDS, Istio sidecar vs ambient

### ★ Envoy Internals Deep Dive
- **Speaker:** Matt Klein, Lyft (Envoy creator)
- **Conference:** KubeCon + CloudNativeCon EU 2018 (Copenhagen)
- **URL:** https://www.youtube.com/watch?v=gQF23Vw0keg · **36:56**
- **Why:** Explicitly "advanced skill level" and it means it: Envoy's threading model, connection and listener handling, the listener→filter chain→cluster→endpoint object model, and hot restart. Understanding this object model is the prerequisite for reading any xDS config dump, which is how mesh debugging is actually done.
- **Ages well** on architecture; Envoy has gained a great deal since (this is why the object model matters more than the feature list).

### ★ Life of a Packet: Ambient Edition
- **Speakers:** John Howard (Solo.io — Istio maintainer) & Keith Mattix (Microsoft)
- **Conference:** KubeCon + CloudNativeCon NA 2024 (Salt Lake City)
- **URL:** https://www.youtube.com/watch?v=5IJwd9X5Yk8 · **35:52**
- **Why:** Traces a packet through Istio ambient mode — node-level ztunnel, redirection mechanics, waypoint proxies for L7 — with the explicit contrast against sidecar interception. This is the sidecar-vs-ambient talk to watch, and it is mechanism the whole way down.
- **Ages well** and is current.

### Build Your Own Envoy Control Plane
- **Speaker:** Steve Sloka, VMware (Contour maintainer)
- **Conference:** KubeCon + CloudNativeCon NA 2020 (virtual)
- **URL:** https://www.youtube.com/watch?v=qAuq4cKEG_E · **24:27**
- **Why:** xDS from the *server* side — the discovery-service gRPC streams, resource types (LDS/RDS/CDS/EDS), and versioning/ACK semantics. The cheapest way to stop treating xDS as magic; also a natural optional build-track exercise (Go — see [#9](https://github.com/k3ii/k8s-academy/issues/9)).
- **Mildly stale** on xDS API versions (v2→v3); the protocol shape is unchanged.

### Second pass
- `Envoy's Using 10GB of Memory and It's All My Fault!` — Steve Sloka — KubeCon NA 2019 — https://www.youtube.com/watch?v=rdJZk6k314k · **9:40**. Lightning talk, flagged as such — but a complete, honest memory-blowup postmortem in under 10 minutes.

---

<a id="security"></a>
## 12. Security — CVE walkthroughs, container escape mechanics, attack/defence

### ★ Crafty Requests: Deep Dive Into Kubernetes CVE-2018-1002105
- **Speaker:** Ian Coldwater, Heroku
- **Conference:** KubeCon + CloudNativeCon EU 2019 (Barcelona)
- **URL:** https://www.youtube.com/watch?v=VjSJqc13PNk · **33:35**
- **Why:** **The model CVE walkthrough.** The apiserver's aggregation-layer proxy upgrade bug that allowed unauthenticated escalation to cluster-admin, explained from the protocol level up — why the connection-upgrade path skipped authorisation, and what the fix changed. Strong candidate for anchoring the map's still-unspecified CVE-driven security lab: the vulnerability is *in the control plane*, not in an app, and understanding it requires the apiserver request-flow knowledge from area 2.
- **Ages well** (the CVE is patched; the class of bug — proxy paths that bypass authz — is evergreen).

### ★ Exploiting a Slightly Peculiar Volume Configuration with SIG-Honk (runc CVE-2021-30465)
- **Speakers:** Ian Coldwater (Twilio); Brad Geesaman & Rory McCune (Aqua Security); Duffie Cooley (Isovalent)
- **Conference:** KubeCon + CloudNativeCon NA 2021 (Los Angeles)
- **URL:** https://www.youtube.com/watch?v=V8JXexaLGCU · **34:12**
- **Why:** Container **escape** mechanics done properly: a runc symlink/mount-race vulnerability taken from a thin advisory to a working proof-of-concept, validated across cluster types, demonstrated live, and disclosed. Teaches the exploit-development *process*, not just the payload — the right shape for a sandboxed lab.
- **Ages well.** Note the YouTube title is truncated; the full session title is given above.

### ★ The Path Less Traveled: Abusing Kubernetes Defaults
- **Speakers:** Duffie Cooley (VMware) & Ian Coldwater (Heroku)
- **Conference:** KubeCon + CloudNativeCon NA 2019 (San Diego)
- **URL:** https://www.youtube.com/watch?v=gtaaONq-XGY · **27:59**
- **Why:** Live attack chain built entirely from *default* configuration — no CVE required. Shows why "not misconfigured" and "secure" are different claims, and gives the concrete privilege-escalation paths (hostPath, privileged, service-account token reach) that CKS then tests you on.
- **Mildly stale:** PodSecurityPolicy-era framing; Pod Security Admission and default service-account token changes have closed some paths. The attack reasoning holds.

### Kubernetes Attack and Defense: Inception-Style
- **Speaker:** Jay Beale, InGuardians
- **Conference:** KubeCon + CloudNativeCon EU 2020 (virtual)
- **URL:** https://www.youtube.com/watch?v=cCyDAJHkNO4 · **31:39**
- **Why:** Container-escape and lateral-movement demos with the *defence* for each shown alongside — the paired structure makes it usable as a lab script rather than just a scare.
- **Mildly stale** on tooling; mechanics current.

### Second pass
- `The Hitchhiker's Guide to Kubernetes Vulnerabilities` — Robert Clark & Micah Hausler, Amazon — KubeCon NA 2021 — https://www.youtube.com/watch?v=RKm5QA3pdaQ · **28:59**. How Kubernetes CVEs are triaged, scored and disclosed — useful context for reading advisories critically.
- `Advanced Persistence Threats: The Future of Kubernetes Attacks` — Ian Coldwater & Brad Geesaman — KubeCon EU 2020 — https://www.youtube.com/watch?v=auUgVullAWM · **32:27**. Post-compromise persistence in a cluster.
- `Container Forensics: What to Do When Your Cluster is a Cluster` — Maya Kaczorowski & Ann Wallace — KubeCon EU 2019 — https://www.youtube.com/watch?v=MyXROAqO7YI · **33:48**. Incident response on ephemeral workloads.

---

<a id="chaos"></a>
## 13. Chaos engineering on Kubernetes

**Honest assessment first:** this is by far the weakest area in the CNCF corpus. The genre is dominated by tool introductions and vendor case studies; there is no maintainer-grade "how chaos tooling actually injects failure" deep dive comparable to the etcd or Envoy talks. **Recommendation: take the chaos strand's *content* from the debugging/postmortem talks in area 10 — especially Thomas Graf's `How to Break your Kubernetes Cluster with Networking`, which is a better chaos-experiment catalogue than anything in this section — and use the two talks below only for tooling orientation.**

### Make Cloud Native Chaos Engineering Easier — Deep Dive into Chaos Mesh
- **Speaker:** Cwen Yin, PingCAP
- **Conference:** KubeCon + CloudNativeCon EU 2022 (Valencia)
- **URL:** https://www.youtube.com/watch?v=bZnI5omUKe4 · **38:30**
- **Why:** The most internals-oriented of the chaos-tool talks — how experiments are modelled as CRDs and how the injection actually happens (sidecar/daemon, network and I/O fault primitives). Enough mechanism to judge the tool rather than just install it, which satisfies the map's "ecosystem modules need an internals note" requirement.
- **Mildly stale** on Chaos Mesh's own feature set.

### Making Sense of Chaos: Implementing Chaos Engineering in a Fintech
- **Speakers:** Iqbal Farabi & Giovanni Sakti
- **Conference:** KubeCon + CloudNativeCon EU 2022 (Valencia)
- **URL:** https://www.youtube.com/watch?v=-7NdVuSVZFo · **29:18**
- **Why:** Practice rather than tooling — how to choose experiments, set blast radius, and run game days without breaking trust. Useful because a solo learner has no organisational pressure to design experiments carefully and will otherwise just kill random pods.

### Second pass
- `Controllers at Chaos` — Kesavan Subramanian & Gaurav Gupta, SAP — KubeCon EU 2020 — https://www.youtube.com/watch?v=kQT82Qx97L4 · **31:37**. Also listed under area 5; the crossover (controller correctness under injected failure) is the most curriculum-relevant chaos content found.

---

---

<a id="counts"></a>
## Counts per area

| Area | ★ Core | Second pass | Area total |
|---|---|---|---|
| etcd / Raft / watch / recovery | 5 | 4 | 9 |
| API server / admission / APF | 5 | 3 | 8 |
| CRDs / aggregation / operators | 3 | 1 | 4 |
| Scheduler internals | 2 | 3 | 5 |
| Controllers / client-go / informers | 3 | 2 | 5 |
| Pod networking / kube-proxy / CNI | 4 | 3 | 7 |
| eBPF / Cilium datapath | 3 | 0 | 3 |
| Storage / CSI | 1 | 2 | 3 |
| kubelet / eviction / cgroups | 3 | 2 | 5 |
| Cluster debugging / postmortems | 6 | 4 | 10 |
| Service mesh / Envoy / xDS | 2 | 2 | 4 |
| Security / CVE / escapes | 3 | 4 | 7 |
| Chaos engineering | 0 | 2 | 2 |
| [Gaps](#gaps) pointer (SIG Scalability) | 0 | 1 | 1 |
| **Total** | **40** | **33** | **73 verified links** |

Of the 40 ★ entries, [the spine's ordered 24](#spine) is the set to actually commit to the curriculum; the other 16 ★ entries are phase-gated (they only make sense once their area opens).

*(One talk, `Controllers at Chaos`, is cross-listed in areas 5 and 13 and is counted once, in area 5.)*

<a id="gaps"></a>
## Known gaps, stated rather than papered over

1. **etcd disaster recovery / quorum loss** — no verifiable standalone war-story talk exists. Must be a lab.
2. **kube-proxy nftables backend** — no verified deep-dive recording. Read KEP-3866 instead.
3. **apiserver watch-cache internals** — no dedicated mechanism talk found; the SIG Scalability maintainer series (`Intro + Deep Dive: Kubernetes SIG Scalability`, Wojciech Tyczyński, e.g. https://www.youtube.com/watch?v=nrAskCyG_Xk · **33:43**) touches it but is not a watch-cache deep dive.
4. **Post-GA ValidatingAdmissionPolicy** — the CEL talks listed are all pre-GA or codebase-oriented.
5. **Storage incident postmortems** — none found.
6. **General operator anti-patterns** — genre is dominated by SDK pitches; substitute the controller-mistakes talk.
7. **Chaos engineering internals** — no maintainer-grade deep dive exists in this corpus.

---

<a id="selection"></a>
## Selection rules applied

- **No keynotes.** Every entry below is a breakout, maintainer-track, or end-user technical session. The one 9-minute lightning talk included is flagged as such.
- **Mechanism over release notes.** Talks were preferred when the content is "how the thing works" rather than "what shipped in 1.2x". Where a talk *is* release-note-shaped but has no better substitute, it is marked **STALE-BUT-USEFUL** with the specific rot named.
- **Fewer, better.** 40 entries are marked **★** (core — earns its runtime unconditionally); of those, [the viewing spine](#spine) names the 24 to watch first, in dependency order. Everything unmarked is a labelled second pass, kept only because it closes a stated gap or is cheap (under 30 min) relative to what it teaches — not because it deserves equal billing.
- **Series handling.** For recurring maintainer tracks (`Deep Dive: etcd`, `SIG API Machinery Deep Dive`, `SIG-Scheduling Deep Dive`, `SIG-Node Intro and Deep Dive`, `SIG Storage Deep Dive`) one **best entry instalment** is named and the series is noted, rather than listing every year.

<a id="verification"></a>
## Verification method

Every URL in this document was resolved with `yt-dlp` against the live YouTube API, which returns the **exact video title, duration, channel, and upload date**. A wrong or dead ID fails loudly (`Video unavailable`), so a link that appears here resolved and its title matched the talk claimed.

- **URLs verified: 73 / 73.** Zero unverified, zero dead, zero guessed-from-memory. Titles below are reproduced verbatim as YouTube returns them (CNCF truncates long titles with `...` in the video title itself; the full session title is given where it differs).
- Candidate discovery was also done through `yt-dlp`'s YouTube search rather than from memory, so every candidate considered was a real video from the start. Several plausible-sounding titles recalled from memory failed to resolve and were dropped — this is exactly the failure mode the method is guarding against.
- **Durations** are exact runtimes from the video metadata, not scheduled slot lengths.
- **Conference + year** is derived from the CNCF channel upload date (CNCF publishes a conference's videos in a tight window afterwards) and cross-checked against the "next flagship event" promo line in each video description. This is reliable to the event, but note CNCF **rewrites old descriptions**, so promo lines were only used as a corroborating signal, never as the primary one. Two attributions are explicitly hedged below (`DrtdrdwDpZE`, `bb0Op1G6XjQ`).
- **One entry is not a CNCF talk at all** (USENIX Vault '20) and is flagged inline. It is included because the CNCF corpus has no equivalent.

