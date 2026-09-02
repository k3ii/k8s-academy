# Talks

This document lists 73 conference talks. Every URL here was verified against YouTube
itself, and no URL was recalled from memory. There are no keynotes, because this corpus
prefers mechanism over release notes. **40 talks carry a ★.** A ★ means that the talk earns
its runtime unconditionally. Out of those 40, the [viewing spine](#spine) names the 24 to
watch first, in dependency order. That set of 24 is what the curriculum actually commits to.
Every unmarked talk is a labelled second pass. A second-pass talk is kept for one of two
reasons: it closes a stated gap, or it is cheap relative to what it teaches.

This document derives from [`../research/kubecon-talks.md`](../research/kubecon-talks.md),
with research date 2026-08-17. The runtimes are exact video durations. They are not
scheduled slot lengths.

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

**The chaos strand does not source from the chaos area.** Two talks exist there, and both
are tool pitches. This corpus holds no maintainer-grade chaos deep dive. So the strand takes
its material from the postmortems in [Debugging](#debugging) instead. That is a curriculum
decision, and not an omission. It is recorded in
[#4](https://github.com/k3ii/k8s-academy/issues/4).

---

<a id="spine"></a>
## The viewing spine — the ★ CORE 24, in order

The order puts each talk after its prerequisites. The total runtime is about **14h20m**,
spread across the whole curriculum. That is roughly twenty minutes a week over a year. This
is why the strand is a spine, and not a module.

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

Watch the rest when its phase opens. Those talks are `Operating kube-apiserver Without Hiccups` · `The Cluster Killer Bug (APF)` · `Webhook Fatigue? (CEL)` · the three eBPF and Cilium talks · `Intro + Deep Dive: Kubernetes Storage SIG` · the remaining postmortems · `Envoy Internals Deep Dive` · `Life of a Packet: Ambient Edition` · and the four security talks.

---

<a id="etcd"></a>
## 1. etcd internals, Raft, watch, operational failure and recovery

### ★ Understanding Distributed Consensus in etcd and Kubernetes
- **Speaker:** Laura Frank, CloudBees
- **Conference:** KubeCon + CloudNativeCon EU 2018 (Copenhagen)
- **URL:** https://www.youtube.com/watch?v=n9VKAKwBj_0 · **37:00**
- **Why:** This is the best first-principles Raft explanation in the corpus. It builds leader election, log replication and quorum up from the problem statement, and not from etcd's API. Watch it *before* any etcd maintainer deep dive.
- **Ages well.** It is algorithm content; nothing in it has moved.

### ★ Deep Dive: etcd
- **Speakers:** Xiang Li (Alibaba — etcd co-creator) & Wenjia Zhang (Google)
- **Conference:** KubeCon + CloudNativeCon NA 2018 (Seattle)
- **URL:** https://www.youtube.com/watch?v=GJqO1TYzVDE · **45:52**
- **Why:** This is the best entry instalment of the long-running `Deep Dive: etcd` maintainer series. It covers the storage engine layout, MVCC revisions, watch and compaction. It also gives the operational consequence of each one, from the person who wrote the code.
- **Series note:** the series runs most years. The later instalments cover the same ground with a different emphasis. One example is `Deep Dive: etcd — Jingyi Hu`, at https://www.youtube.com/watch?v=DrtdrdwDpZE · 39:52, uploaded in July 2019. It is **most likely KubeCon China 2019 (Shanghai), so the event attribution is hedged.** Start with the talk above. Chase another instalment only for a specific subsystem.
- **Mildly stale:** the defrag tooling and the `--experimental-*` flag surface are described as they were before 3.5. The MVCC, watch and compaction mechanics are unchanged.

### ★ Debugging etcd
- **Speakers:** Joe Betz & Jingyi Hu, Google
- **Conference:** KubeCon + CloudNativeCon NA 2018 (Seattle)
- **URL:** https://www.youtube.com/watch?v=NVMZBBQ9hsM · **42:36**
- **Why:** This is the highest-value etcd talk for the diagnosis goal. It shows how to read etcd's metrics and logs, so that you can separate three causes: disk-fsync stalls, network latency, and leader-election churn. It names the actual signals for each. This is the talk that turns "etcd is slow" into a falsifiable statement.
- **Ages well.** The metric names and the failure taxonomy are still current.

### ★ Secrets of Running Etcd
- **Speaker:** Marek Siarkowicz, Google (etcd maintainer)
- **Conference:** KubeCon + CloudNativeCon NA 2023 (Chicago)
- **URL:** https://www.youtube.com/watch?v=aJVMWcVZOPQ · **40:33**
- **Why:** This is the modern operational counterpart to the 2018 deep dive. It explains why etcd is latency-sensitive at the disk layer, how compaction and defrag interact with cluster size, and what actually breaks at scale. It applies directly to one homelab task: run a single-node etcd on cramped hardware, and watch it degrade.
- **Ages well.**

### ★ Lessons Learned From Etcd the Data Inconsistency Issues
- **Speakers:** Marek Siarkowicz (Google) & Benjamin Wang (VMware) — both etcd maintainers
- **Conference:** KubeCon + CloudNativeCon NA 2022 (Detroit)
- **URL:** https://www.youtube.com/watch?v=_nSJ_vozyqk · **35:24**
- **Why:** This is a maintainer-authored postmortem of a real correctness bug that shipped. It shows how a distributed-consensus datastore can lose linearizability without anyone noticing. It also says which testing failed to catch it. Few talks teach distrust of your own storage layer, and this is one of them.
- **Ages well**, because it is history. **Follow-up instalment:** `On the Hunt for Etcd Data Inconsistencies`, by Marek Siarkowicz at KubeCon EU 2023, at https://www.youtube.com/watch?v=IIMs0EjQZHg · **42:08**. That is the payoff talk. It covers the model-based, deterministic robustness testing framework that was built in response. Watch the 2022 talk first.

### Second pass
- `Dr etcd; or; How I Learned to Stop Worrying and Love the Datastore` — Nick Young, VMware — KubeCon NA 2019 — https://www.youtube.com/watch?v=CE9uwBoSk-8 · **18:39**. This is a cheap orientation talk. Use it as a warm-up before the Frank talk, if etcd still feels abstract.
- `Forging a Stronger Bond Between Etcd and Kubernetes` — Siarkowicz, Wenjia Zhang, James Blair — KubeCon NA 2023 — https://www.youtube.com/watch?v=6JYgBJAjpNQ · **36:28**. It covers the apiserver-to-etcd contract. Watch it *after* the API server area below.

**Honest gap:** the CNCF corpus has no strong standalone war story about losing quorum in production and recovering from it, at least none with a verifiable recording. The closest real-incident content sits inside `Lessons Learned` and `Secrets of Running Etcd`. So disaster-recovery drilling has to be a lab, and not a talk.

---

<a id="apiserver"></a>
## 2. API server internals, admission control, API Priority and Fairness

### ★ The Life (or Death) of a Kubernetes API Request, 2025 Edition
- **Speakers:** Abu Kashem & Stefan Schimanski (SIG API Machinery)
- **Conference:** KubeCon + CloudNativeCon EU 2025 (London)
- **URL:** https://www.youtube.com/watch?v=Hc0jj-654lA · **30:49**
- **Why:** **This is the single best entry point to the whole control plane.** It traces one request from end to end. The stages are authentication, authorisation, APF queueing, the admission chain, the storage encode, the etcd write, and the watch fan-out. The modern APF and CEL stages are in place. Every other apiserver talk hangs off this spine.
- **Ages well.** It is also recent enough to be the current picture.

### ★ Life of a Kubernetes API Request
- **Speaker:** Daniel Smith, Google (SIG API Machinery lead)
- **Conference:** KubeCon + CloudNativeCon NA 2016 (Seattle)
- **URL:** https://www.youtube.com/watch?v=ryeINNfVOi8 · **44:07**
- **Why:** This is the original. It is slower and more patient than the 2025 edition. It is also better on *why* the API machinery has this shape. It covers declarative intent, resource versions, optimistic concurrency and watch semantics.
- **STALE-BUT-USEFUL:** it predates APF entirely. It predates CRDs reaching v1, and it predates ValidatingAdmissionPolicy and CEL. Its admission discussion also assumes compiled-in admission plugins, rather than webhooks. So watch it for the model, and not for the pipeline stages. If time is short, watch the 2025 edition instead. Come back to this one only if the *why* is still murky.

### ★ Operating kube-apiserver Without Hiccups
- **Speakers:** Stefan Schimanski & David Eads, Red Hat
- **Conference:** KubeCon + CloudNativeCon EU 2019 (Barcelona)
- **URL:** https://www.youtube.com/watch?v=pED17NXiexw · **25:56**
- **Why:** It covers graceful termination and readiness semantics. It also says what actually happens to in-flight requests and watches during an apiserver rollout. Almost nothing else covers the apiserver *lifecycle*, and that is exactly the knowledge you need to upgrade a control plane without dropping traffic.
- **Ages well.** Some self-hosting details are dated, because they belong to the OpenShift context of the time.

### ★ The Cluster Killer Bug: Learning API Priority and Fairness the Hard Way
- **Speaker:** Eddie Zaneski, Independent
- **Conference:** KubeCon + CloudNativeCon NA 2023 (Chicago)
- **URL:** https://www.youtube.com/watch?v=4mYUyAeyr-U · **34:59**
- **Why:** It teaches APF through a real outage. A client that looked well behaved saturated one priority level, and it took the control plane down. The talk shows how the team diagnosed that from the APF metrics. Pair it with the mechanism talk below, and the APF metrics stop being noise.
- **Ages well.**

### API Priority and Fairness: Kube-APIServer Flow-control Protection
- **Speaker:** Min Jin, Ant Group (SIG API Machinery)
- **Conference:** KubeCon + CloudNativeCon NA 2020 (virtual)
- **URL:** https://www.youtube.com/watch?v=Tps4eAjuCr8 · **29:46**
- **Why:** This is the design talk for APF, given by one of its designers. It covers priority levels, FlowSchemas and seat accounting. It also explains why the apiserver previously had no defence against a single bad client.
- **STALE-BUT-USEFUL:** it predates the GA of APF, which landed in 1.29. The API group versions that it shows, such as `flowcontrol.apiserver.k8s.io/v1beta1`, have changed, and so have some defaults. The concurrency-sharing model has not changed.

### ★ Webhook Fatigue? You're Not Alone: Introducing the CEL Expression Language Features...
- **Speaker:** Joe Betz, Google (SIG API Machinery tech lead)
- **Conference:** KubeCon + CloudNativeCon NA 2022 (Detroit)
- **URL:** https://www.youtube.com/watch?v=gJWMvsC7Mzo · **35:15**
- **Why:** It explains admission by explaining what is *wrong* with webhook admission. The three problems are latency in the request path, availability coupling, and failure-policy tradeoffs. It then explains why CEL inside the apiserver was the answer. This is the best available talk on how admission control actually costs you.
- **STALE-BUT-USEFUL:** this is the prequel to ValidatingAdmissionPolicy, which went GA in 1.30. The motivation and the CEL mechanics are current. The feature status and the API shape are not. Pair it with the CEL talk below.

### Second pass
- `A Field Guide To Integrating CEL in the Kubernetes Codebase` — Sreeram Venkitesh & Priyanka Saggu — KubeCon EU 2025 — https://www.youtube.com/watch?v=ODI3KwDLKas · **33:24**. This is an unusually good fit for the read-the-source strand. It walks the actual CEL integration points in `k/k`, rather than the user-facing API.
- `SIG API Machinery Deep Dive` — Abu Kashem, Stefan Schimanski, Joe Betz, Federico Bongiovanni — KubeCon NA 2021 — https://www.youtube.com/watch?v=oiC2w1PVjrQ · **29:37**. This is the instalment with the APF and CEL authors in the room.

---

<a id="crds"></a>
## 3. CRDs, aggregation, operator patterns and anti-patterns

### ★ Extending the Kubernetes API: What the Docs Don't Tell You
- **Speaker:** James Munnelly, Jetstack
- **Conference:** KubeCon + CloudNativeCon NA 2017 (Austin)
- **URL:** https://www.youtube.com/watch?v=PYLFZVv68lM · **33:46**
- **Why:** This is still the clearest treatment of the real decision, which is a CRD against an aggregated API server. It says what each option gives up, across validation, subresources, storage control, and versioning and conversion. Most later talks assume the CRD answer, and never argue for it.
- **STALE-BUT-USEFUL:** it comes from the CRD-beta era. Structural schemas, CRD conversion webhooks, `x-kubernetes-validations` in CEL, and server-side apply all postdate it. Several of its "CRDs can't do this" caveats have been fixed since. The tradeoff *axes* are still the right ones.

### ★ Deep Dive Into API Machinery
- **Speakers:** Antoine Pelisse (Google) & Stefan Schimanski (Red Hat)
- **Conference:** KubeCon + CloudNativeCon NA 2019 (San Diego)
- **URL:** https://www.youtube.com/watch?v=qTm-g3vtVOE · **27:36**
- **Why:** This is the best entry instalment of the `SIG API Machinery Deep Dive` series. It covers the group, version and kind machinery, the scheme and conversion, and how the extension points hang off it. It is short and dense. The vocabulary that it installs is what makes `k/k` navigable.
- **Series note:** the series runs at most KubeCons, and you should not watch them all. Watch this one. Then watch the 2021 instalment above, if you want commentary from the APF and CEL authors.

### ★ A Vision For API Machinery: Coming to Terms with the Platform We Built
- **Speaker:** Daniel Smith, Google
- **Conference:** KubeCon + CloudNativeCon NA 2018 (Seattle)
- **URL:** https://www.youtube.com/watch?v=u6weI_3WVTM · **40:38**
- **Why:** This is a design-philosophy talk from the person who owns the API machinery. It says what the Kubernetes API is *for*, where its abstractions leak, and which extension mechanisms are load-bearing rather than accidental. This is the talk that makes operator design decisions feel principled, instead of cargo-culted.
- **Ages well**, because it is almost entirely about invariants.

### Implementing Anti-patterns: Kubernetes Cross-namespace Resource Ownership
- **Speaker:** Tom Coufal, Red Hat
- **Conference:** KubeCon + CloudNativeCon EU 2022 (Valencia)
- **URL:** https://www.youtube.com/watch?v=iWz5AAbbT-c · **33:17**
- **Why:** It takes one concrete operator anti-pattern seriously. Owner references do not cross namespaces. So garbage collection does the wrong thing, and every workaround costs something. It beats the generic "operator best practices" talks, because it takes one real failure mode and follows it all the way down.
- **Ages well.**

**Honest gap:** the CNCF corpus has no great *general* talk on operator anti-patterns. SDK and framework pitches dominate the genre. The controller-mistakes talk in area 5, `Charlie Don't Does`, is the better substitute.

---

<a id="scheduler"></a>
## 4. Scheduler internals, scheduling framework, preemption, scheduling at scale

### ★ Deep Dive Into the Latest Kubernetes Scheduler Features
- **Speaker:** Abdullah Gharaibeh, Google (SIG Scheduling)
- **Conference:** KubeCon + CloudNativeCon NA 2019 (San Diego)
- **URL:** https://www.youtube.com/watch?v=eDkE4WNWKUc · **41:37**
- **Why:** This is the best available walk through the **scheduling framework**. It covers the extension-point sequence of filter, score, reserve, permit and bind. It covers how preemption picks its victims, and why preemption can fail to make room. It also covers how pod priority interacts with the scheduling queue. The title reads like release notes, and most of the runtime is mechanism anyway.
- **Mildly stale:** the framework plugin names have moved on, and so have some feature gates. The extension-point model and the preemption algorithm are unchanged.

### ★ SIG-Scheduling Deep Dive
- **Speakers:** Wei Huang (Apple), Qingcan Wang (Alibaba), Kante Yin, Kensei Nakada
- **Conference:** KubeCon + CloudNativeCon NA 2022 (Detroit)
- **URL:** https://www.youtube.com/watch?v=1GpTE9L9oBM · **38:43**
- **Why:** This is the best entry instalment of the SIG Scheduling maintainer track. It covers the real behaviour of the scheduling queue: backoff, unschedulable pods, and requeueing hints. That is exactly where mental models of the scheduler usually break.
- **Series note:** the later instalments are increasingly about workload and AI scheduling, such as Kueue and gang scheduling, rather than core internals. So watch this one for the internals. Chase a newer instalment only if batch or GPU scheduling becomes relevant.

### Kubernetes Scheduling Features or How Can I Make the System Do What I Want?
- **Speaker:** Marek Grabowski, Google
- **Conference:** KubeCon + CloudNativeCon EU 2017 (Berlin)
- **URL:** https://www.youtube.com/watch?v=bbPcb2JuJPw · **34:07**
- **Why:** It predates the framework. So it explains predicates and priorities as raw functions over node lists. It is *conceptually clarifying* for exactly that reason: it has no plugin abstraction in the way.
- **STALE-BUT-USEFUL:** the scheduling framework replaced the predicate and priority API in 1.19. The node affinity syntax that it shows is also dated. Its value is entirely conceptual, so skip it if time is short.

### Second pass
- `Enhancing the Kubernetes Scheduler for Diverse Workloads in Large Clusters` — Yuan Chen & Yan Xu — https://www.youtube.com/watch?v=0O_06RNEiL4 · **29:34**. It covers the throughput characteristics of scheduling at scale.
- `A Tale of Two Plugins: Safely Extending the Kubernetes Scheduler with WebAssembly` — Kensei Nakada — https://www.youtube.com/watch?v=TfS2ONQGlC4 · **32:19**. It teaches the framework's plugin contract from the outside in.

---

<a id="controllers"></a>
## 5. Controllers, reconciliation, client-go internals, informer behaviour

### ★ The Life of a Kubernetes Watch Event
- **Speakers:** Wenjia Zhang & Haowei Cai, Google
- **Conference:** KubeCon + CloudNativeCon NA 2018 (Seattle)
- **URL:** https://www.youtube.com/watch?v=PLSDvFjR9HY · **33:00**
- **Why:** **For anyone who writes a controller, this is the most load-bearing talk in the whole document.** It follows a single change from the etcd watch, through the apiserver watch cache, over the wire, and into the client-go reflector, the DeltaFIFO, the indexer and the workqueue. It explains resource versions, the relist on `410 Gone`, and why informers are eventually consistent. That last point is why level-triggered reconciliation is not a style preference.
- **Ages well.** The watch-cache internals have been optimised since, with consistent reads from cache, watch bookmarks and streaming list. The pipeline stages are the same.

### ★ client-go: The Good, The Bad and The Ugly
- **Speaker:** Lili Cosic, Kinvolk
- **Conference:** KubeCon + CloudNativeCon NA 2017 (Austin)
- **URL:** https://www.youtube.com/watch?v=Q88kI8X5R48 · **24:16**
- **Why:** This is a short, honest tour of the moving parts in client-go, and of their sharp edges. It covers the informer, lister and workqueue wiring, rate limiting, and the ergonomics that trip people up. These are the best 24 minutes available on the library itself.
- **Mildly stale:** the generated-client and codegen ergonomics have changed, and `controller-runtime` now hides much of this. It is still the right talk if you wire a reconcile loop *by hand*. That is exactly the plan here. [#9](https://github.com/k3ii/k8s-academy/issues/9) settled that the first operator is hand-wired `client-go`, and that `kubebuilder` is held back deliberately until afterwards. So the sharp edges in this talk are the ones that you will hit.

### ★ Don't Write Controllers Like Charlie Don't Does: Avoiding Common Kubernetes Controller Mistakes
- **Speaker:** Nick Young, Isovalent at Cisco
- **Conference:** KubeCon + CloudNativeCon EU 2025 (London)
- **URL:** https://www.youtube.com/watch?v=tnSraS9JqZ8 · **31:38**
- **Why:** This is the current, opinionated catalogue of controller bugs. It covers confusion between status and spec, non-idempotent reconciles, hot loops, requeue misuse, and assumptions about cross-resource ordering. It is recent enough to reflect modern practice, and specific enough to act on.
- **Ages well.**

### Second pass
- `Writing Kube Controllers for Everyone` — Maciej Szulik, Red Hat — KubeCon EU 2018 — https://www.youtube.com/watch?v=AUNPLQVxvmw · **37:23**. It is labelled as beginner content. It is really a careful build-up of the reconcile loop, from a `k/k` controller maintainer. Use it as a scaffold *before* the client-go talk.
- `Controllers at Chaos` — Kesavan Subramanian & Gaurav Gupta, SAP — https://www.youtube.com/watch?v=kQT82Qx97L4 · **31:37**. It covers controller behaviour under injected failure. It doubles as chaos content, for area 13.

---

<a id="networking"></a>
## 6. Pod networking from first principles, kube-proxy, EndpointSlice, CNI

### ★ Container Networking From Scratch
- **Speaker:** Kristen Jacobs, Oracle
- **Conference:** KubeCon + CloudNativeCon NA 2018 (Seattle)
- **URL:** https://www.youtube.com/watch?v=6v_BDHIgOY8 · **34:44**
- **Why:** **This is the Phase-0 networking talk.** It builds container networking live, from `ip netns`, veth pairs, bridges and routes. There is no Kubernetes in it, no CNI, and no abstraction. Afterwards, everything in Kubernetes networking becomes derivable. You can also reproduce it directly on a single Debian VM, which matters under the RAM ceiling here.
- **Ages well.** Linux primitives do not move.

### ★ Kubernetes Networking Intro and Deep-Dive
- **Speakers:** Bowei Du & Tim Hockin, Google (SIG Network)
- **Conference:** KubeCon + CloudNativeCon EU 2020 (virtual)
- **URL:** https://www.youtube.com/watch?v=tq9ng_Nz9j8 · **1:19:50**
- **Why:** This is the long-form canonical treatment, from the people who designed the Service abstraction. It covers the Service, Endpoint and EndpointSlice data model, the iptables and IPVS modes of kube-proxy, and the explicit design constraints that produced them. The 80 minutes are earned, because this one talk replaces three shorter ones.
- **Mildly stale:** it predates the nftables backend for kube-proxy, and it predates the maturity of Gateway API. The Service data model and the kube-proxy iptables mechanics are unchanged.

### ★ Kubernetes Networking: How to Write a CNI Plugin From Scratch
- **Speaker:** Eran Yanay, Twistlock
- **Conference:** KubeCon + CloudNativeCon EU 2019 (Barcelona)
- **URL:** https://www.youtube.com/watch?v=zmYxdtFzK6s · **33:14**
- **Why:** It demystifies CNI, by showing what CNI is. CNI is a spec for an executable that receives JSON on stdin and wires a network namespace. This talk pairs perfectly with the Jacobs talk, and it is a build-it-yourself lab in talk form.
- **Ages well**, because the CNI spec is stable. It does not cover the CNI 1.0 and 1.1 additions, and it does not cover dynamic device plugins.

### ★ Scaling Kubernetes Networking Beyond 100k Endpoints
- **Speakers:** Rob Scott & Minhan Xia, Google
- **Conference:** KubeCon + CloudNativeCon EU 2020 (virtual)
- **URL:** https://www.youtube.com/watch?v=a6SfbeM06Qo · **38:30**
- **Why:** This is the EndpointSlice origin story. It explains why one `Endpoints` object per Service melts the apiserver, and every kube-proxy with it, at scale. The cause is an O(n) watch fan-out on every pod churn. So the talk explains a Kubernetes API design decision by the load that it was fixing. That is the most transferable kind of lesson in this corpus.
- **Ages well.**

### Second pass
- `Deep Dive: CNI` — Bryan Boreham (Weaveworks) & Dan Williams (Red Hat) — KubeCon NA 2019 — https://www.youtube.com/watch?v=zChkx-AB5Xc · **39:05**. This is the maintainer view of the spec, of chaining, and of IPAM.
- `Life of a Packet [I]` — Michael Rubin, Google — KubeCon EU 2017 — https://www.youtube.com/watch?v=0Omvgd7Hg1I · **34:19**. This is the original packet-walk talk. The Hockin deep dive now overlaps it heavily. It is still a good 34-minute alternative, if 80 minutes is too much.
- `Understand and Troubleshoot the "Magic" of Kubernetes Networking` — Minhan Xia & Rohit Ramkumar — KubeCon EU 2018 — https://www.youtube.com/watch?v=knIJEzTd3kc · **31:57**.

**Note on kube-proxy nftables:** this corpus holds no verified deep-dive recording for the nftables backend, which is KEP-3866. So treat that subject as reading, meaning the KEP itself, rather than as a talk.

---

<a id="ebpf"></a>
## 7. eBPF and the Cilium datapath

### ★ eBPF and Kubernetes: Little Helper Minions for Scaling Microservices
- **Speaker:** Daniel Borkmann, Cilium/Isovalent (eBPF and Linux networking maintainer)
- **Conference:** KubeCon + CloudNativeCon EU 2020 (virtual)
- **URL:** https://www.youtube.com/watch?v=99jUcLt3rSk · **39:28**
- **Why:** **This is the reference eBPF talk**, and it comes from a kernel-side maintainer. It covers the verifier, maps, program types, and the tc and XDP hook points. It then shows how Cilium uses them to replace iptables-based service handling. It works at kernel level, so it explains *why* eBPF is fast, instead of asserting that it is.
- **Ages well.** Kernel features have been added since. Nothing that it shows is wrong.

### ★ Understanding and Troubleshooting the eBPF Datapath in Cilium
- **Speaker:** Nathan Sweet, DigitalOcean
- **Conference:** KubeCon + CloudNativeCon NA 2019 (San Diego)
- **URL:** https://www.youtube.com/watch?v=Kmm8Hl57WDU · **38:07**
- **Why:** This is an *operator's* eBPF talk. It shows how to inspect loaded programs and maps, how to follow a packet through Cilium's datapath, and how to localise a fault. That makes it rare and valuable. Almost every other eBPF talk sells the technology, and this one debugs it.
- **Mildly stale:** the CLI, the tooling and the datapath structure of Cilium have all evolved considerably, with kube-proxy replacement modes and with ambient and Envoy integration. The debugging *method* still transfers.

### ★ Liberating Kubernetes From Kube-proxy and Iptables
- **Speaker:** Martynas Pumputis, Cilium
- **Conference:** KubeCon + CloudNativeCon NA 2019 (San Diego)
- **URL:** https://www.youtube.com/watch?v=bIRwSIwNHC0 · **35:07**
- **Why:** This is the clearest side-by-side comparison of the two datapaths. It says what iptables and conntrack actually do per packet for a Service, what the eBPF replacement does instead, and where each one costs you. Watch it immediately after the Hockin kube-proxy material, for the contrast.
- **Mildly stale** on the Cilium feature status. The comparison itself is intact.

---

<a id="storage"></a>
## 8. Storage and CSI internals

### ★ Intro + Deep Dive: Kubernetes Storage SIG
- **Speaker:** Saad Ali, Google (SIG Storage lead, CSI co-author)
- **Conference:** KubeCon + CloudNativeCon EU 2019 (Barcelona)
- **URL:** https://www.youtube.com/watch?v=PcMairR7-4U · **1:16:01**
- **Why:** This is the best entry instalment of the SIG Storage series, and the most complete account of the volume lifecycle. It covers provision, attach and mount. It also covers the split between the attach and detach controller and the kubelet's volume manager, and where each step can wedge. That attach-and-detach boundary is the origin of most real storage incidents.
- **Mildly stale:** the in-tree-to-CSI migration was in progress then, and it is now complete. Ephemeral volumes, capacity tracking and volume health all postdate the talk.

### Kubernetes SIG Storage Deep Dive
- **Speakers:** Xing Yang (VMware) & Mauricio Poppe (Google)
- **Conference:** KubeCon + CloudNativeCon NA 2022 (Detroit)
- **URL:** https://www.youtube.com/watch?v=_XXn3-yDZA0 · **32:18**
- **Why:** This is the modern update. It covers the CSI landscape after the migration, snapshots, and capacity-aware provisioning. Watch it after the Saad Ali deep dive, so that it patches the staleness. Do not watch it instead of that deep dive.

### Understanding Kubernetes Storage: Getting in Deep by Writing a CSI Driver — **NOT a CNCF talk**
- **Conference:** USENIX Vault '20 (February 2020)
- **URL:** https://www.youtube.com/watch?v=drbKyJgC-sU · **31:31**
- **Why:** This talk sits outside the requested corpus, and it is included deliberately. It is the only verified recording that treats CSI as *an interface that you implement*. It covers the gRPC services, the sidecar containers, and what each sidecar actually does. Nothing in the CNCF catalogue matches it for the build-it-yourself strand.
- **Flagged:** the source is not CNCF. The video title also does not carry the speaker attribution.

**Honest gap:** for deep internals, storage is the weakest area in the CNCF corpus. There is no verified postmortem talk about a stuck volume or a multi-attach incident. So storage debugging has to be lab-driven.

---

<a id="node"></a>
## 9. kubelet, eviction, cgroups, node-level debugging

### ★ Evicted! All the Ways Kubernetes Kills Your Pods (and How To Avoid Them)
- **Speaker:** Ahmet Alp Balkan, LinkedIn
- **Conference:** KubeCon + CloudNativeCon NA 2025 (Atlanta)
- **URL:** https://www.youtube.com/watch?v=jVwXcuNEDYE · **28:11**
- **Why:** **This is the definitive taxonomy of pod death.** It separates six causes: kubelet node-pressure eviction, the eviction API, preemption, OOMKill, graceful node shutdown, and taint-based eviction. It also says which component to blame for each one. It is recent, from November 2025, so it reflects the current eviction surface. It applies directly to a resource-starved homelab, where pods die constantly.
- **Ages well**, and it is current.

### ★ Cgroupv2 Is Coming Soon To a Cluster Near You
- **Speakers:** David Porter (Google) & Mrunal Patel (Red Hat) — SIG Node
- **Conference:** KubeCon + CloudNativeCon NA 2022 (Detroit)
- **URL:** https://www.youtube.com/watch?v=sgyFCp1CRhA · **45:44**
- **Why:** It gives the cgroup v1 to v2 mechanics, from the maintainers who did the kubelet work. It covers the unified hierarchy, `memory.high` and `memory.max` against the v1 limits, the PSI pressure metrics, and how the kubelet maps pod QoS onto cgroup trees. This is the talk that makes `/sys/fs/cgroup` readable.
- **Mildly stale on framing only.** The title says "coming soon". In fact cgroup v2 is now the default on Debian 13, and recent Kubernetes requires it. The mechanics are exactly right.

### ★ Who Killed My Pod? #Whodunit
- **Speaker:** Suneeta Mall, Nearmap
- **Conference:** KubeCon + CloudNativeCon NA 2021 (Los Angeles)
- **URL:** https://www.youtube.com/watch?v=eH4x5PGgDoM · **31:54**
- **Why:** It teaches a node-level forensic method. You start from a dead pod, and you work backwards through the kubelet logs, the container runtime state, the exit codes, the kernel OOM messages and the cgroup accounting, until you can name the killer. It is explicitly a diagnosis-from-first-principles talk.
- **Ages well.**

### Resource Requests and Limits Under the Hood: The Journey of a Pod Spec
- **Speakers:** Kohei Ota & Kaslin Fields
- **Conference:** KubeCon + CloudNativeCon EU 2021 (virtual)
- **URL:** https://www.youtube.com/watch?v=WB3_sV_EQrQ · **24:19**
- **Why:** It traces `requests` and `limits` through four stages: the YAML, the scheduler arithmetic, CRI, and the cgroup values. It includes CPU shares against CPU quota, which is the actual source of the confusion about CPU throttling. At 24 minutes it is cheap.
- **Mildly stale:** it uses cgroup v1 units, and it has no in-place pod resize.

### Second pass
- `SIG-Node: Intro and Deep Dive` — Sergey Kanzhelev & Dawn Chen (Google), Mrunal Patel (Red Hat) — **KubeCon NA 2024 (Salt Lake City). The attribution is inferred from a January 2025 upload, so it is hedged.** — https://www.youtube.com/watch?v=bb0Op1G6XjQ · **56:58**. This is the best recent entry to the SIG Node maintainer series. It covers the kubelet's responsibilities, the CRI boundary, and who owns the pod lifecycle.

---

<a id="debugging"></a>
## 10. Cluster debugging and "we broke production" postmortems

*This area is weighted most generously, as the ticket asks. These talks model the diagnostic reasoning that the curriculum tries to install.*

### ★ Logs Told Us It Was DNS, It Felt Like DNS, It Had To Be DNS, It Wasn't DNS
- **Speakers:** Laurent Bernaille & Elijah Andrews, Datadog
- **Conference:** KubeCon + CloudNativeCon EU 2022 (Valencia)
- **URL:** https://www.youtube.com/watch?v=NunyPkN0n3c · **36:14**
- **Why:** **This is the best single debugging talk in the corpus.** It follows a four-week incident all the way down. The chain runs from apparent DNS failures during rolling updates → conntrack table overflow → martian-packet drops → the kernel source → a gRPC client reconnect algorithm. The resolution was three lines of code. The talk shows the *whole* method: form a hypothesis, instrument it, disconfirm it, and descend a layer. That method is the transferable skill.
- **Ages well.**

### ★ How the OOM-Killer Deleted My Namespace, and Other Kubernetes Tales
- **Speaker:** Laurent Bernaille, Datadog
- **Conference:** KubeCon + CloudNativeCon NA 2020 (virtual)
- **URL:** https://www.youtube.com/watch?v=MrNhdmyXXKg · **31:10**
- **Why:** It presents several real incidents. In each one, a small node-level event produced an absurd control-plane-level outcome. In one of them, a memory-pressure kill cascaded into a namespace deletion. The lesson is about coupling and blast radius, across components that look independent.
- **Ages well.**

### ★ 10 Ways to Shoot Yourself in the Foot with Kubernetes, #9 Will Surprise You
- **Speakers:** Laurent Bernaille & Robert Boll, Datadog
- **Conference:** KubeCon + CloudNativeCon EU 2019 (Barcelona)
- **URL:** https://www.youtube.com/watch?v=QKI-JRs2RIE · **37:19**
- **Why:** It presents ten real production failures at scale. Each one is traced to a specific mechanism: conntrack, resource limits, DNS, controller assumptions, or apiserver load. The clickbait title hides a serious talk. It is effectively a failure-mode catalogue with the root causes attached.
- **Ages well.** A couple of the failures involve defaults that have since been fixed. The mechanisms remain.

### ★ Kubernetes Failure Stories and How to Crash Your Clusters
- **Speaker:** Henning Jacobs, Zalando SE
- **Conference:** KubeCon + CloudNativeCon EU 2019 (Barcelona)
- **URL:** https://www.youtube.com/watch?v=6sDTB4eV4F8 · **29:26**
- **Why:** This is the canonical failure-stories talk, from the person who curates `k8s.af`. It covers many clusters' worth of outages, and it names the pattern behind each one. It is the best breadth-first survey of *how clusters actually fail*, and it belongs before you specialise.
- **Ages well.**

### ★ How to Break your Kubernetes Cluster with Networking
- **Speaker:** Thomas Graf, Isovalent (Cilium co-creator)
- **Conference:** KubeCon + CloudNativeCon EU 2021 (virtual)
- **URL:** https://www.youtube.com/watch?v=7qUDyQQ52Uk · **28:01**
- **Why:** It injects failure deliberately at the network layer, and it names the observable symptoms. The faults are MTU mismatch, asymmetric routing, conntrack exhaustion and policy misapplication. For each one, it says how the fault *presents* to a confused operator. It also doubles as a design list for chaos experiments, which the chaos area badly needs.
- **Ages well.**

### ★ CrashLoopBackoff, Pending, FailedMount and Friends: Debugging Common Kubernetes Cluster and Application Issues
- **Speaker:** Joe Thompson, Oteemo
- **Conference:** KubeCon + CloudNativeCon NA 2017 (Austin)
- **URL:** https://www.youtube.com/watch?v=7FOCG5kua1w · **34:54**
- **Why:** This is the systematic triage talk that takes you from beginner to competent. For each common bad pod state, it says which object to inspect, in what order, and what each field actually tells you. It is labelled as beginner content, and it is structurally sound. It is the right talk to watch *early* in the curriculum.
- **Mildly stale:** `kubectl debug` and ephemeral containers did not exist yet. The event and condition output has also changed cosmetically. The triage order is still correct.

### Second pass
- `A Basic Kubernetes Debugging Kit: curl, jq, openssl, and Other Best Friends` — Joe Thompson — KubeCon NA 2018 — https://www.youtube.com/watch?v=QtXHkzLtqZE · **33:38**. It debugs the API and TLS layers *without* `kubectl`. That is valuable for the goal of debugging the control plane itself.
- `101 Ways to Crash Your Cluster` — Marius Grigoriu & Emmanuel Gomez, Nordstrom — KubeCon NA 2017 — https://www.youtube.com/watch?v=xZO9nx6GBu0 · **36:20**.
- `Surviving Day 2 — How to Troubleshoot Kubernetes Networking` — Thomas Graf — KubeCon EU 2023 — https://www.youtube.com/watch?v=920BZXvQpVs · **49:15**. This is a longer companion to the 2021 talk, with more Cilium flavour.
- `Surviving From Endless Issues Coming From 7K+ Kubernetes Clusters` — Wanhae Lee & Seok-yong Hong — KubeCon NA 2022 — https://www.youtube.com/watch?v=dMwQEUl9IZg · **31:32**. It covers fleet-scale failure patterns.

---

<a id="mesh"></a>
## 11. Service mesh internals — Envoy, xDS, Istio sidecar vs ambient

### ★ Envoy Internals Deep Dive
- **Speaker:** Matt Klein, Lyft (Envoy creator)
- **Conference:** KubeCon + CloudNativeCon EU 2018 (Copenhagen)
- **URL:** https://www.youtube.com/watch?v=gQF23Vw0keg · **36:56**
- **Why:** It is labelled "advanced skill level", and it means it. It covers Envoy's threading model, its connection and listener handling, the listener → filter chain → cluster → endpoint object model, and hot restart. You must understand that object model before you can read any xDS config dump. Reading config dumps is how mesh debugging is actually done.
- **Ages well** on architecture. Envoy has gained a great deal since. That is exactly why the object model matters more than the feature list does.

### ★ Life of a Packet: Ambient Edition
- **Speakers:** John Howard (Solo.io — Istio maintainer) & Keith Mattix (Microsoft)
- **Conference:** KubeCon + CloudNativeCon NA 2024 (Salt Lake City)
- **URL:** https://www.youtube.com/watch?v=5IJwd9X5Yk8 · **35:52**
- **Why:** It traces a packet through Istio ambient mode. It covers the node-level ztunnel, the redirection mechanics, and the waypoint proxies for L7. It also contrasts all of that explicitly with sidecar interception. This is the sidecar-against-ambient talk to watch, and it is mechanism the whole way down.
- **Ages well**, and it is current.

### Build Your Own Envoy Control Plane
- **Speaker:** Steve Sloka, VMware (Contour maintainer)
- **Conference:** KubeCon + CloudNativeCon NA 2020 (virtual)
- **URL:** https://www.youtube.com/watch?v=qAuq4cKEG_E · **24:27**
- **Why:** It presents xDS from the *server* side. It covers the discovery-service gRPC streams, the resource types LDS, RDS, CDS and EDS, and the versioning and ACK semantics. It is the cheapest way to stop treating xDS as magic. It is also a natural optional exercise for the build track, in Go. See [#9](https://github.com/k3ii/k8s-academy/issues/9).
- **Mildly stale** on the xDS API versions, because it shows v2 rather than v3. The protocol shape is unchanged.

### Second pass
- `Envoy's Using 10GB of Memory and It's All My Fault!` — Steve Sloka — KubeCon NA 2019 — https://www.youtube.com/watch?v=rdJZk6k314k · **9:40**. This is a lightning talk, and it is flagged as one. It is still a complete and honest memory-blowup postmortem, in under 10 minutes.

---

<a id="security"></a>
## 12. Security — CVE walkthroughs, container escape mechanics, attack/defence

### ★ Crafty Requests: Deep Dive Into Kubernetes CVE-2018-1002105
- **Speaker:** Ian Coldwater, Heroku
- **Conference:** KubeCon + CloudNativeCon EU 2019 (Barcelona)
- **URL:** https://www.youtube.com/watch?v=VjSJqc13PNk · **33:35**
- **Why:** **This is the model CVE walkthrough.** The bug sat in the apiserver's aggregation-layer proxy upgrade, and it allowed unauthenticated escalation to cluster-admin. The talk explains it from the protocol level up. It says why the connection-upgrade path skipped authorisation, and what the fix changed. It is a strong candidate for anchoring the CVE-driven security lab that the map still leaves unspecified. Here is why. The vulnerability is *in the control plane*, and not in an app. Understanding it also requires the apiserver request-flow knowledge from area 2.
- **Ages well.** The CVE is patched. The class of bug, meaning proxy paths that bypass authorisation, is evergreen.

### ★ Exploiting a Slightly Peculiar Volume Configuration with SIG-Honk (runc CVE-2021-30465)
- **Speakers:** Ian Coldwater (Twilio); Brad Geesaman & Rory McCune (Aqua Security); Duffie Cooley (Isovalent)
- **Conference:** KubeCon + CloudNativeCon NA 2021 (Los Angeles)
- **URL:** https://www.youtube.com/watch?v=V8JXexaLGCU · **34:12**
- **Why:** It does container **escape** mechanics properly. The team took a runc symlink and mount-race vulnerability from a thin advisory to a working proof-of-concept. They then validated it across cluster types, demonstrated it live, and disclosed it. So the talk teaches the exploit-development *process*, and not just the payload. That is the right shape for a sandboxed lab.
- **Ages well.** Note that the YouTube title is truncated. The full session title is given above.

### ★ The Path Less Traveled: Abusing Kubernetes Defaults
- **Speakers:** Duffie Cooley (VMware) & Ian Coldwater (Heroku)
- **Conference:** KubeCon + CloudNativeCon NA 2019 (San Diego)
- **URL:** https://www.youtube.com/watch?v=gtaaONq-XGY · **27:59**
- **Why:** It builds a live attack chain entirely from *default* configuration, and it needs no CVE. It shows why "not misconfigured" and "secure" are two different claims. It also gives the concrete privilege-escalation paths that CKS then tests you on: hostPath, privileged containers, and the reach of a service-account token.
- **Mildly stale:** the framing comes from the PodSecurityPolicy era. Pod Security Admission, and the changes to default service-account tokens, have closed some of these paths. The attack reasoning holds.

### Kubernetes Attack and Defense: Inception-Style
- **Speaker:** Jay Beale, InGuardians
- **Conference:** KubeCon + CloudNativeCon EU 2020 (virtual)
- **URL:** https://www.youtube.com/watch?v=cCyDAJHkNO4 · **31:39**
- **Why:** It demonstrates container escape and lateral movement, and it shows the *defence* for each one alongside it. That paired structure makes the talk usable as a lab script, rather than as just a scare.
- **Mildly stale** on tooling. The mechanics are current.

### Second pass
- `The Hitchhiker's Guide to Kubernetes Vulnerabilities` — Robert Clark & Micah Hausler, Amazon — KubeCon NA 2021 — https://www.youtube.com/watch?v=RKm5QA3pdaQ · **28:59**. It shows how Kubernetes CVEs are triaged, scored and disclosed. That is useful context for reading advisories critically.
- `Advanced Persistence Threats: The Future of Kubernetes Attacks` — Ian Coldwater & Brad Geesaman — KubeCon EU 2020 — https://www.youtube.com/watch?v=auUgVullAWM · **32:27**. It covers post-compromise persistence inside a cluster.
- `Container Forensics: What to Do When Your Cluster is a Cluster` — Maya Kaczorowski & Ann Wallace — KubeCon EU 2019 — https://www.youtube.com/watch?v=MyXROAqO7YI · **33:48**. Incident response on ephemeral workloads.

---

<a id="chaos"></a>
## 13. Chaos engineering on Kubernetes

**Take the honest assessment first.** This is by far the weakest area in the CNCF corpus. Tool introductions and vendor case studies dominate the genre. There is no maintainer-grade deep dive on how chaos tooling actually injects failure, so there is nothing comparable to the etcd or Envoy talks. **The recommendation follows. Take the *content* of the chaos strand from the debugging and postmortem talks in area 10. Thomas Graf's `How to Break your Kubernetes Cluster with Networking` is the best of them, because it is a better chaos-experiment catalogue than anything in this section. Then use the two talks below for tooling orientation only.**

### Make Cloud Native Chaos Engineering Easier — Deep Dive into Chaos Mesh
- **Speaker:** Cwen Yin, PingCAP
- **Conference:** KubeCon + CloudNativeCon EU 2022 (Valencia)
- **URL:** https://www.youtube.com/watch?v=bZnI5omUKe4 · **38:30**
- **Why:** This is the most internals-oriented of the chaos-tool talks. It shows how experiments are modelled as CRDs, and how the injection actually happens, through a sidecar or daemon and through the network and I/O fault primitives. That is enough mechanism to judge the tool, rather than only to install it. It therefore satisfies the map's requirement that an ecosystem module carries an internals note.
- **Mildly stale** on Chaos Mesh's own feature set.

### Making Sense of Chaos: Implementing Chaos Engineering in a Fintech
- **Speakers:** Iqbal Farabi & Giovanni Sakti
- **Conference:** KubeCon + CloudNativeCon EU 2022 (Valencia)
- **URL:** https://www.youtube.com/watch?v=-7NdVuSVZFo · **29:18**
- **Why:** This talk is about practice, and not about tooling. It covers how to choose experiments, how to set a blast radius, and how to run game days without breaking trust. It is useful for one reason. A solo learner has no organisational pressure to design experiments carefully, and will otherwise just kill random pods.

### Second pass
- `Controllers at Chaos` — Kesavan Subramanian & Gaurav Gupta, SAP — KubeCon EU 2020 — https://www.youtube.com/watch?v=kQT82Qx97L4 · **31:37**. Area 5 lists it as well. Its crossover subject is controller correctness under injected failure, and that is the most curriculum-relevant chaos content in the corpus.

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

Out of the 40 ★ entries, commit [the spine's ordered 24](#spine) to the curriculum. The other 16 ★ entries are phase-gated, because each one makes sense only once its area opens.

*(One talk, `Controllers at Chaos`, is cross-listed in areas 5 and 13. It is counted once, in area 5.)*

<a id="gaps"></a>
## Known gaps, stated rather than papered over

1. **etcd disaster recovery and quorum loss.** No verifiable standalone war-story talk exists. So this has to be a lab.
2. **The nftables backend for kube-proxy.** There is no verified deep-dive recording. Read KEP-3866 instead.
3. **The apiserver watch-cache internals.** No dedicated mechanism talk was found. The SIG Scalability maintainer series touches the subject, for example `Intro + Deep Dive: Kubernetes SIG Scalability` by Wojciech Tyczyński, at https://www.youtube.com/watch?v=nrAskCyG_Xk · **33:43**. It is not a watch-cache deep dive.
4. **ValidatingAdmissionPolicy after GA.** Every CEL talk listed here is either pre-GA or codebase-oriented.
5. **Storage incident postmortems.** None were found.
6. **General operator anti-patterns.** SDK pitches dominate the genre. Substitute the controller-mistakes talk.
7. **Chaos engineering internals.** No maintainer-grade deep dive exists in this corpus.

---

<a id="selection"></a>
## Selection rules applied

- **No keynotes.** Every entry here is a breakout session, a maintainer-track session, or an end-user technical session. One 9-minute lightning talk is included, and it is flagged as one.
- **Mechanism over release notes.** A talk was preferred when its content is "how the thing works", rather than "what shipped in 1.2x". Some talks *are* release-note-shaped and have no better substitute. Each one of those is marked **STALE-BUT-USEFUL**, and the specific rot is named.
- **Fewer, better.** 40 entries are marked **★**, which means core, and which means that the talk earns its runtime unconditionally. Out of those 40, [the viewing spine](#spine) names the 24 to watch first, in dependency order. Every unmarked entry is a labelled second pass. A second-pass entry is kept only because it closes a stated gap, or because it is cheap, meaning under 30 minutes, relative to what it teaches. None of them is kept because it deserves equal billing.
- **Series handling.** Several maintainer tracks recur: `Deep Dive: etcd`, `SIG API Machinery Deep Dive`, `SIG-Scheduling Deep Dive`, `SIG-Node Intro and Deep Dive` and `SIG Storage Deep Dive`. For each one, this document names a single **best entry instalment**, and notes the series. It does not list every year.

<a id="verification"></a>
## Verification method

Every URL in this document was resolved with `yt-dlp`, against the live YouTube API. That API returns the **exact video title, duration, channel and upload date**. A wrong or dead ID fails loudly, with `Video unavailable`. So every link that appears here resolved, and its title matched the talk that is claimed for it.

- **URLs verified: 73 out of 73.** None is unverified, none is dead, and none was guessed from memory. The titles here are reproduced verbatim, as YouTube returns them. CNCF truncates a long title with `...` inside the video title itself, so the full session title is given wherever the two differ.
- Candidate discovery also went through the YouTube search in `yt-dlp`, rather than through memory. So every candidate considered was a real video from the start. Several plausible-sounding titles were recalled from memory, failed to resolve, and were dropped. That is exactly the failure mode that this method guards against.
- **Durations** are exact runtimes from the video metadata. They are not scheduled slot lengths.
- **The conference and year** are derived from the upload date on the CNCF channel, because CNCF publishes a conference's videos in a tight window afterwards. Each one is then cross-checked against the "next flagship event" promo line in the video description. This is reliable at the level of the event. But note that CNCF **rewrites old descriptions**. So a promo line was used only as a corroborating signal, and never as the primary one. Two attributions are hedged explicitly above, for `DrtdrdwDpZE` and `bb0Op1G6XjQ`.
- **One entry is not a CNCF talk at all.** It comes from USENIX Vault '20, and it is flagged inline. It is included because the CNCF corpus has no equivalent.

