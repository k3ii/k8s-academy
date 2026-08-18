# Phase 6 — kubelet, the node, and observability

> **3–4 weeks.** The hardest area to read in the whole tree — `kubelet.go` is 156 KB with no readable main loop — so the approach changes: enter through the SIG doc and the archived design proposals, then through the small sub-managers, with **exactly one function** assigned from `kubelet.go`. This is also where **Chaos Mesh arrives**, deliberately after four phases of hand-driven failure, and where observability lands because eviction is only legible with a time series in front of you.
> The range is planning information. **The gate at the bottom decides when the phase is finished.**

| | |
|---|---|
| **Prerequisites** | [P5](05-scheduler.md) — the scheduler *decided* the node; the kubelet makes it real, picking up the pod the instant the `Binding` is POSTed. The eviction manager here is [P5's preemption seen from below](05-scheduler.md): both remove a running pod under pressure — one from the queue, one from the node. [P0](00-linux-primitives.md) — Chaos Mesh's fault mechanisms *are* the Linux primitives (cgroups, `setns`, `ptrace`, `netem`) met there; the tool reads as a scripted wrapper over them, not a magic fault box. |
| **Unlocks** | [P7](07-networking.md) — this phase's capstone trace stops at the node's edge (`kubectl`/`nft`-observable but not yet read in source); P7 opens the EndpointSlice/kube-proxy far end whose `file:line` this phase deliberately defers. `kubelet-cri-networking.md` is the exact seam. |
| **Source area** | [Area 7 — kubelet](../strands/source-reading.md#area-7-kubelet), entry point `pleg/generic.go`. **The one area where the source is genuinely too hostile** — design docs and sub-managers first, `syncLoopIteration` the only function read from `kubelet.go`. |
| **Language** | Go — read only. **No build artifact this phase** (the build track resumes at [P7](07-networking.md)); the hands-on is the observability stack and the trace. |
| **Chaos** | **Chaos Mesh is introduced here**, [minimised to 582 Mi](../strands/chaos.md#install) (dashboard off, one controller replica) — its [per-fault Linux primitive](../strands/chaos.md#mechanisms) is the point, not its CRDs. |
| **Lab** | [`pair`](https://github.com/k3ii/k8s-academy/issues/8) — DaemonSet-heavy phases pay per node, so two nodes beat three here. |
| **Strands** | [source reading](../strands/source-reading.md#area-7-kubelet) · [chaos](../strands/chaos.md#install) · [talks](../strands/talks.md#node) |

---

<a id="objectives"></a>
## 1. Objectives

Every one is falsifiable — an artifact, a timed production, or a claim a hostile reader could check against source or a running node. *understand* and *know* appear nowhere.

By the end you can:

1. **Explain PLEG's `relist`** — why per-pod polling didn't scale, what relist replaced it with, and the origin of the `PLEG is not healthy` error — citing `pleg/generic.go` and the PLEG design doc.
2. **Classify any pod** as Guaranteed / Burstable / BestEffort from its spec and predict its OOM-score-adj, citing `GetPodQOS` in `qos.go` and `qos/policy.go`.
3. **Read the eviction manager's `synchronize()`** and name the signal, threshold and victim-ranking that fired, citing `eviction_manager.go` and the actual defaults in `defaults_linux.go`.
4. **Do OOMKill forensics** — from `dmesg` and cgroup `memory.events`, name the killer (kernel vs kubelet) and *why that pod*, citing the OOM-score mechanism.
5. **Compute `allocatable` for the `factory` node** (`capacity − kube-reserved − system-reserved − eviction-hard`) and say where the RAM went, citing `node-allocatable.md`.
6. **Read `syncLoopIteration` alone** — the ~100-line channel-multiplexing core — and name the channels it selects over. The only function assigned from `kubelet.go`.
7. **Stand up Prometheus + Grafana + node-exporter** and read one eviction as a time series — the reason observability lands in this phase.
8. **Trace corpus trace #2** — a pod dies and a Service stops sending it traffic — end to end with `nft list ruleset` evidence and Area-7 `file:line` citations. **This is the capstone.**

---

<a id="modules"></a>
## 2. Modules

Reading is [Area 7](../strands/source-reading.md#area-7-kubelet), and its rule is the strongest in the corpus: **the design docs before the code, the small sub-managers before the big files, and `kubelet.go` only for `syncLoopIteration`.** Each cited item carries a question to answer — no bare links.

<a id="m6-1"></a>
### Module 6.1 — The map, and PLEG (~4 days)

The kubelet has no readable entry loop; PLEG is the one part that reduces to one file, one loop, one idea.

**Read**

| Item | Answer from it |
|---|---|
| `sig-node/kubelet.md` (item 1, **read first**) + `container-runtime-interface.md` (item 2) | The SIG's map of the sub-managers, and the CRI RuntimeService/ImageService split. What is the sandbox (pause) container *for*? |
| `cri-api/.../v1/api.proto` (item 3) | **The CRI contract as protobuf** — `RunPodSandbox`, `CreateContainer`, `StartContainer`. Reading the proto is far easier than the Go that consumes it; which calls does starting one pod make, in order? |
| `node/pod-lifecycle-event-generator.md` (item 4) then `pleg/pleg.go` → `pleg/generic.go` (item 5, ⭐) | **The entry point.** Why did per-pod polling not scale, and what does `relist` emit instead? Where in `generic.go` is the `PLEG is not healthy` threshold? **Objective 1.** |
| KEP-3386 Evented PLEG (item 6) | Runtime-pushed CRI events replacing polling, relist kept as a safety net. Why keep relist at all once events exist? |

**Do** — run `crictl ps`/`crictl pods` on a live node and match its output to the CRI proto messages you just read.

**Break it** — stop the container runtime briefly and watch `PLEG is not healthy` appear; trace it to the relist-latency check in `generic.go`.

**Write down** — the `relist` loop in one paragraph, with the `generic.go:line` of the health threshold.

<a id="m6-2"></a>
### Module 6.2 — QoS and the kernel's OOM killer (~3 days)

The mechanism by which the kernel — not Kubernetes — kills your BestEffort pod first. Directly load-bearing on a deliberately memory-pressured host.

**Read**

| Item | Answer from it |
|---|---|
| `node/resource-qos.md` (item 7) + `qos/qos.go` `GetPodQOS` (item 8) | **The classification algorithm in 4.6 KB.** What exact combination of requests/limits yields each class? Classify three pods by hand, then check against the function. |
| `pkg/kubelet/qos/policy.go` (item 9) | OOM-score-adj per class. What score does each class get, and why does that make the kernel pick BestEffort first under global pressure? |

**Do** — deploy one pod of each QoS class; read each container's `oom_score_adj` from `/proc/<pid>/oom_score_adj` and match it to `policy.go`.

**Break it** — chaos drill [6.C3](#chaos) in miniature: stress one node's memory and watch which pod the *kernel* kills first, confirming the class order.

**Write down** — the three classes, their OOM-score-adj, and the one-line rule that assigns each — reused in the checklist.

<a id="m6-3"></a>
### Module 6.3 — The eviction manager (~1 week)

The heart of the phase: how the kubelet reclaims a node *before* the kernel has to, and who it picks.

**Read**

| Item | Answer from it |
|---|---|
| `node/kubelet-eviction.md` (item 10, **before the code**) | Signals (`memory.available`, `nodefs.available`, `imagefs.available`, `pid.available`), hard vs soft thresholds, grace periods, `evictionMinimumReclaim`, victim ranking. Which signal has no grace period, and why? |
| `eviction/types.go` then `eviction_manager.go` `synchronize()` (item 11) | The threshold-evaluation and pod-ranking loop. In what order are pods ranked for eviction, and how does QoS enter that order? **Objective 3.** |
| `eviction/defaults_linux.go` (item 12) | **The actual default thresholds.** What is the default `memory.available` hard threshold? (Treat `helpers.go` as reference only.) |
| `eviction/memory_threshold_notifier.go` (item 13) + KEP-4205 PSI metrics (item 14) | cgroup pressure notification via `eventfd`, and PSI as a first-class signal. How does the kubelet react *faster* than its housekeeping interval? |

**Do** — set an aggressive `--eviction-hard` on a node and drive it to eviction; read the kubelet log's eviction decision against `synchronize()`.

**Break it** — chaos drill [6.C4](#chaos): a disk-pressure cascade (fill `imagefs`) and watch the manager rank and evict — reading it on the Grafana time series from [module 6.6](#m6-6).

**Write down** — the signal, threshold and victim order for the eviction you drove, with `eviction_manager.go`/`defaults_linux.go` citations.

<a id="m6-4"></a>
### Module 6.4 — cgroups v2 and node-allocatable (~4 days)

Where the RAM went on a 9.9 GB host, and the tree that enforces it. **cgroups v2 only** — Debian 13 is v2 by default and v1 is being removed (KEP-5573).

**Read**

| Item | Answer from it |
|---|---|
| `node/pod-resource-management.md` (item 15) + `cm/cgroup_manager_linux.go` (item 16) | The `kubepods → QoS-class → pod → container` hierarchy. Pair with reading `/sys/fs/cgroup/kubepods.slice/` on a live node — **that pairing is the lab.** Which directory holds a Burstable pod's limit? |
| KEP-2254 cgroups v2 (item 17) + KEP-2570 Memory QoS (item 19) | `memory.max`/`memory.high`, `cpu.max`, and `memory.high` throttling instead of a straight OOM-kill. What does `memory.high` do that `memory.max` doesn't? |
| `node/node-allocatable.md` (item 20) | `capacity − kube-reserved − system-reserved − eviction-hard = allocatable`. **Compute it for `factory`** and account for every missing MB. **Objective 5.** |

**Do** — walk `/sys/fs/cgroup/kubepods.slice/` and locate one running pod's `memory.max`; compare to its spec limit.

**Break it** — set a pod's `memory.high` below its working set and watch it throttle (not die); contrast with setting `memory.max` low (it dies). The difference is KEP-2570 made concrete.

**Write down** — the `factory` allocatable arithmetic, every subtraction cited.

<a id="m6-5"></a>
### Module 6.5 — The node reports itself (~4 days)

Static pods, node-level admission, status, heartbeats — and the single `kubelet.go` read.

**Read**

| Item | Answer from it |
|---|---|
| `kubelet/config/file.go` (item 21) | **Static pods**: three pod sources merged into one stream, and why a static pod has a mirror pod. Every kubeadm control plane depends on this — which directory does `file.go` watch? (P1's kubeadm static-pod manifests, now explained.) |
| `kubelet/lifecycle/predicate.go` (item 22) | **Node-level admission**: the kubelet's last-chance check *after* the scheduler decided. What produces an `OutOfmemory`/`OutOfcpu` pod failure, and why can the node reject what the scheduler accepted? |
| `status/status_manager.go` (item 23) + `component-helpers/.../lease/controller.go` + KEP-589 (items 25–26) | The write side of `kubectl get pod`, and **why `Lease` objects exist** — full NodeStatus every 10 s was an etcd write-amplification disaster. What is the real node-failure detection latency (lease duration vs `node-status-update-frequency`)? |
| `kubelet.go` `syncLoopIteration` **only** (item 29) | The ~100-line channel-multiplexing core — the single function assigned from the 156 KB file. Which channels does the `select` read, and what does each deliver? **Objective 6. Never read this file linearly.** |

**Do** — `systemctl stop kubelet` on one node and time how long until the node goes `NotReady` and pods are marked for eviction — the KEP-589 latency, measured.

**Break it** — chaos drill [6.C2](#chaos): kubelet stopped under load. Pods keep running while the node is `NotReady`; explain the gap from the lease mechanism.

**Write down** — the node-failure detection latency you measured, against the lease-vs-status-frequency split.

<a id="m6-6"></a>
### Module 6.6 — Observability (~3 days)

The layer that makes eviction legible. Detailed as ecosystem in [§6](#ecosystem) — this is its hands-on.

**Do** — install `kube-prometheus-stack` (Prometheus + Grafana + node-exporter) minimised for the lab ceiling. Point a dashboard at node memory, cgroup pressure and pod restarts.

**Break it** — re-run an eviction (drill [6.C3](#chaos) or [6.C4](#chaos)) and read it *as a time series*: the `memory.available` slope into the threshold, the eviction, the recovery. An eviction you only saw in a log you half-saw.

**Write down** — the PromQL for "node `memory.available` approaching the eviction threshold," and where node-exporter reads that number from (a `/proc` or `/sys` file you met in module 6.4).

---

<a id="chaos"></a>
## 3. Chaos drills

**Chaos Mesh is introduced here** — [installed minimised at 582 Mi](../strands/chaos.md#install), dashboard off (that switch is also the [P10](10-security.md) CVE surface — you re-enable it there deliberately). It arrives now, after four phases of hand-driven failure, so it reads as **a scripted wrapper over the [Linux primitives](../strands/chaos.md#mechanisms) met in [P0](00-linux-primitives.md)** — `StressChaos` is `stress-ng` in the target's cgroup (so the OOMKill is *real*), `PodChaos` is three different layers of "the pod died," and the daemon enters the target with `setns(2)`. Reading *why `chaos-daemon` needs each capability* is a better privilege lesson than any policy exercise. `KernelChaos` is a [verify-first stretch goal](../strands/chaos.md#verify-first), not required.

| # | Drill | Chaos Mesh / by hand | What you must produce afterwards |
|---|---|---|---|
| 6.C1 | **Hard node failure** | Proxmox guest stop (or `PodChaos` node-kill) | The node-failure detection latency, explained from the lease mechanism (KEP-589) |
| 6.C2 | **kubelet stopped under load** | `systemctl stop kubelet` | Why pods keep running while the node is `NotReady`, and when eviction begins |
| 6.C3 | **OOMKill forensics** | `StressChaos` (real OOMKill) | From `dmesg` + cgroup `memory.events`: the killer (kernel vs kubelet) and **which QoS victim, and why** |
| 6.C4 | **Disk-pressure eviction cascade** | fill `imagefs`/`nodefs` | The eviction manager's ranking and the `imagefs.available` threshold that fired, read on the Grafana time series |

6.C3 is the forensic drill the *Who Killed My Pod?* talk models directly.

---

<a id="talks"></a>
## 4. Talks

Full entries with runtimes under [Node](../strands/talks.md#node).

- **★ Evicted! All the Ways Kubernetes Kills Your Pods** (Balkan, NA 2025) — the definitive taxonomy of pod death: node-pressure eviction vs the eviction API vs preemption vs OOMKill vs graceful shutdown vs taint-eviction, and *which component to blame for each*. The map for this whole phase; watch it first. Recent enough to reflect the current eviction surface.
- **★ Who Killed My Pod? #Whodunit** (Mall, NA 2021) — the node-level forensic *method*: from a dead pod, work backwards through kubelet logs, runtime state, exit codes, kernel OOM messages and cgroup accounting to name the killer. This is drill 6.C3's procedure.
- **★ Cgroupv2 Is Coming Soon To a Cluster Near You** (Porter & Patel, NA 2022) — the v1→v2 mechanics from the maintainers: the unified hierarchy, `memory.high`/`memory.max`, PSI, and how QoS maps onto cgroup trees. **The talk that makes `/sys/fs/cgroup` readable** — watch it against module 6.4.

---

<a id="ecosystem"></a>
## 5. Ecosystem

**Prometheus + Grafana + node-exporter, and OpenTelemetry** — observability lands here because eviction is only legible with a time series in front of you.

- **Hands-on:** [module 6.6](#m6-6) — stand up `kube-prometheus-stack` and read a real eviction as a time series, the `memory.available` slope into the threshold and out.
- **Internals note (required, not "install and look at the dashboard"):** **node-exporter reads the same `/proc` and `/sys/fs/cgroup` files you read by hand in module 6.4** — the metric *is* the file, scraped on an interval. Prometheus is a pull-based TSDB (it scrapes targets; targets do not push), which is why a dead node's metrics simply stop rather than reporting failure. OpenTelemetry unifies traces/metrics/logs behind one collector — the vendor-neutral wire format, distinct from Prometheus's storage.
- **Maturity:** Prometheus — CNCF **graduated** (2018), the second project to graduate. **OpenTelemetry — graduated 2026-05-11** ([per #6](https://github.com/k3ii/k8s-academy/issues/6)), now the default instrumentation layer. node-exporter is a first-party Prometheus component. All three are single-big-rock-safe alongside the kubelet work; Cilium/Istio/Falco are not co-resident with this stack ([#8](https://github.com/k3ii/k8s-academy/issues/8)).

---

<a id="capstone"></a>
## 6. Capstone

**Corpus trace #2 — a pod dies and a Service stops sending it traffic — traced end to end**, [the corpus's flagged best mid-curriculum exercise](../strands/source-reading.md#trace-pod-dies) because every hop is directly observable.

The full path is `PLEG relist → status manager → apiserver → EndpointSlice reconciler → kube-proxy endpointschangetracker → syncProxyRules`, ending in `nft list ruleset`. It crosses Areas 7, 4 and 5 — and **Area 5 is [P7](07-networking.md), not yet read.** So the trace splits by design:

- **The near half is source-cited** (Area 7, this phase): the `ContainerDied` emission in `pleg/generic.go`, and the version-bookkeeping write in `status_manager.go` that pushes the new status to the apiserver. `file:line`, a hostile reader could check.
- **The far half is observed, not yet read** (Area 5, deferred to P7): watch the `EndpointSlice` lose the endpoint (`kubectl get endpointslice -w`) and the nftables rule disappear (`nft list ruleset` before/after). The `file:line` for the EndpointSlice reconciler and `syncProxyRules` is **P7's to demand** — naming that seam as owed is part of the exercise.

This is deliberate: the trace proves the seam *by observation now*, and P7 comes back to cite the far end in source. Every Area-7 path verified live per [P2's archaeology standard](../strands/source-archaeology.md#drills).

---

<a id="checklist"></a>
## 7. Checklist

Concrete, demonstrable, grouped by evidence type. No item says *understand* or *know*.

**Live against a running node:**
- [ ] `PLEG is not healthy` reproduced and traced to the `generic.go` latency check.
- [ ] One pod of each QoS class deployed; `oom_score_adj` read and matched to `policy.go`.
- [ ] An eviction driven to completion and read against `synchronize()`.
- [ ] `factory` allocatable computed and reconciled against a live node's reported `allocatable`.
- [ ] Node-failure detection latency measured (kubelet stopped).
- [ ] `kube-prometheus-stack` up; an eviction read as a time series.

**Written artifacts (each is a module's Write-down):**
- [ ] The `relist` loop with the health-threshold `generic.go:line` (6.1).
- [ ] The three QoS classes, their OOM-score-adj, and the assigning rule (6.2).
- [ ] The eviction's signal/threshold/victim-order with citations (6.3).
- [ ] The `factory` allocatable arithmetic, every subtraction cited (6.4).
- [ ] The node-failure detection latency vs the lease/status-frequency split (6.5).
- [ ] The PromQL for approaching-eviction and the `/proc`|`/sys` file behind it (6.6).

**Forensic fluency (the CKA Troubleshooting groundwork this phase banks toward [P8](08-storage.md)):**
- [ ] Given a dead pod, name the killer from `dmesg` + cgroup `memory.events` + QoS.
- [ ] For each Chaos Mesh fault used, name the underlying [Linux primitive](../strands/chaos.md#mechanisms).

---

<a id="gate"></a>
## 8. Gate

You may advance to [P7](07-networking.md) when:

1. **Corpus trace #2 is traced end to end** — the near half cited to Area-7 `file:line`, the far half shown with `nft list ruleset` before/after, and the deferred P7 citations named as owed. If any hop is asserted rather than observed, the seam did not land — **stay here**.
2. **OOMKill forensics is reflexive** — given a dead pod, you name the killer (kernel vs kubelet) from `dmesg`, cgroup `memory.events` and QoS, without guessing. This is the CKA Troubleshooting fluency the [chaos strand](../strands/chaos.md#install) has been building since [P0](00-linux-primitives.md).
3. **Chaos Mesh is understood as a wrapper, not a black box** — for every fault class you used, you can name the [Linux primitive](../strands/chaos.md#mechanisms) underneath (`stress-ng` in a cgroup, `setns` into a namespace, `netem` on a qdisc). If the tool is magic, [P0](00-linux-primitives.md) did not land.

The kubelet makes a scheduled pod real on the node. [P7](07-networking.md) opens the wire between nodes — the CNI plugin the kubelet delegated to, the veth pair behind every pod IP, and the EndpointSlice/kube-proxy far end this phase's trace could only *watch*.
