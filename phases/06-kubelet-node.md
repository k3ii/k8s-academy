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
| **Lab** | [`pair`](../strands/lab-topologies.md#pair) — DaemonSet-heavy phases pay per node, so two nodes beat three here. **The worker's 2048MB is this phase's instrument**, not its constraint: eviction, OOMKill and disk pressure are all produced deliberately on it. |
| **Labs** | [`labs/06/`](../labs/06/README.md) — 29 exercises, in order. One topology for 28 of them, and **no build artifact** — `forge` never changes size this phase. |
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
5. **Compute `allocatable` for [`pair`](../strands/lab-topologies.md#pair)'s 2048MB worker** (`capacity − kube-reserved − system-reserved − eviction-hard`) and say where the RAM went, citing `node-allocatable.md`.
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

**Labs** — [1](../labs/06/01-the-sub-managers-named.md) the sub-manager map · [2](../labs/06/02-one-pod-is-how-many-cri-calls.md) the CRI calls one pod makes · [3](../labs/06/03-relist-and-the-threshold-it-checks.md) relist and its threshold · [4](../labs/06/04-pleg-is-not-healthy.md) `PLEG is not healthy`, produced · [5](../labs/06/05-what-the-node-actually-runs-for-pleg.md) generic or evented on this node.

<a id="m6-2"></a>
### Module 6.2 — QoS and the kernel's OOM killer (~3 days)

The mechanism by which the kernel — not Kubernetes — kills your BestEffort pod first. Directly load-bearing on a deliberately memory-pressured host.

**Read**

| Item | Answer from it |
|---|---|
| `node/resource-qos.md` (item 7) + `qos/qos.go` `GetPodQOS` (item 8) | **The classification algorithm in 4.6 KB.** What exact combination of requests/limits yields each class? Classify three pods by hand, then check against the function. |
| `pkg/kubelet/qos/policy.go` (item 9) | OOM-score-adj per class. What score does each class get, and why does that make the kernel pick BestEffort first under global pressure? |

**Labs** — [6](../labs/06/06-three-pods-three-classes.md) five pods classified from the algorithm · [7](../labs/06/07-oom-score-adj-from-the-formula.md) the score predicted, then read from `/proc` · [8](../labs/06/08-chaos-mesh-at-582mi.md) Chaos Mesh installed and its capabilities read · [9](../labs/06/09-6c3-who-killed-the-pod.md) drill 6.C3.

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

**Labs** — [10](../labs/06/10-the-signals-before-the-code.md) the signals predicted before the code · [11](../labs/06/11-synchronize-and-the-ranking.md) `synchronize()` and the comparator order · [12](../labs/06/12-an-eviction-you-configured.md) an eviction you configured and drove · [13](../labs/06/13-faster-than-housekeeping.md) faster than housekeeping · [14](../labs/06/14-evicted-or-oomkilled.md) evicted or OOMKilled, told apart.

<a id="m6-4"></a>
### Module 6.4 — cgroups v2 and node-allocatable (~4 days)

Where the RAM went on a 9.9 GB host, and the tree that enforces it. **cgroups v2 only** — Debian 13 is v2 by default and v1 is being removed (KEP-5573).

**Read**

| Item | Answer from it |
|---|---|
| `node/pod-resource-management.md` (item 15) + `cm/cgroup_manager_linux.go` (item 16) | The `kubepods → QoS-class → pod → container` hierarchy. Pair with reading `/sys/fs/cgroup/kubepods.slice/` on a live node — **that pairing is the lab.** Which directory holds a Burstable pod's limit? |
| KEP-2254 cgroups v2 (item 17) + KEP-2570 Memory QoS (item 19) | `memory.max`/`memory.high`, `cpu.max`, and `memory.high` throttling instead of a straight OOM-kill. What does `memory.high` do that `memory.max` doesn't? |
| `node/node-allocatable.md` (item 20) | `capacity − kube-reserved − system-reserved − eviction-hard = allocatable`. **Compute it for the 2048MB worker** and account for every missing MB. **Objective 5.** |

**Labs** — [15](../labs/06/15-the-cgroup-tree-under-one-pod.md) the cgroup tree under one pod · [16](../labs/06/16-throttled-instead-of-killed.md) `memory.high` written by hand · [17](../labs/06/17-where-the-ram-went.md) the allocatable arithmetic, proved by changing a term · [18](../labs/06/18-cpu-max-and-the-throttle-counter.md) `cpu.max` and the throttle counter.

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

**Labs** — [19](../labs/06/19-the-mirror-pod-that-will-not-die.md) the static pod that will not die · [20](../labs/06/20-the-node-refuses-what-the-scheduler-allowed.md) node-level admission refusing a scheduled pod · [21](../labs/06/21-two-heartbeats-two-frequencies.md) the detection latency computed first · [22](../labs/06/22-6c2-the-kubelet-stops-the-pods-do-not.md) drill 6.C2 · [23](../labs/06/23-6c1-the-node-vanishes.md) drill 6.C1 · [24](../labs/06/24-one-hundred-lines-of-select.md) `syncLoopIteration`, alone.

<a id="m6-6"></a>
### Module 6.6 — Observability (~3 days)

The layer that makes eviction legible. Detailed as ecosystem in [§6](#ecosystem) — this is its hands-on.

**Labs** — [25](../labs/06/25-the-stack-that-must-not-be-evicted.md) the stack installed and pinned away from the node it measures · [26](../labs/06/26-the-metric-is-the-file.md) node-exporter's number against the kubelet's · [27](../labs/06/27-an-eviction-as-a-slope.md) an eviction read as a slope · [28](../labs/06/28-6c4-disk-pressure-cascade.md) drill 6.C4.

The drill is **deliberately out of module order**: 6.C4 belongs to [module 6.3](#m6-3) and is run here because a disk-pressure cascade is only legible on a time series.

---

<a id="chaos"></a>
## 3. Chaos drills

**Chaos Mesh is introduced here** — [installed minimised at 582 Mi](../strands/chaos.md#install), dashboard off (that switch is also the [P10](10-security.md) CVE surface — you re-enable it there deliberately). It arrives now, after four phases of hand-driven failure, so it reads as **a scripted wrapper over the [Linux primitives](../strands/chaos.md#mechanisms) met in [P0](00-linux-primitives.md)** — `StressChaos` is `stress-ng` in the target's cgroup (so the OOMKill is *real*), `PodChaos` is three different layers of "the pod died," and the daemon enters the target with `setns(2)`. Reading *why `chaos-daemon` needs each capability* is a better privilege lesson than any policy exercise. `KernelChaos` is a [verify-first stretch goal](../strands/chaos.md#verify-first), not required.

| # | Drill | What you must produce afterwards |
|---|---|---|
| [6.C1](../labs/06/23-6c1-the-node-vanishes.md) | **Hard node failure** | The node-failure detection latency, explained from the lease mechanism (KEP-589) |
| [6.C2](../labs/06/22-6c2-the-kubelet-stops-the-pods-do-not.md) | **kubelet stopped under load** | Why pods keep running while the node is `NotReady`, and when eviction begins |
| [6.C3](../labs/06/09-6c3-who-killed-the-pod.md) | **OOMKill forensics** | From `dmesg` + cgroup `memory.events`: the killer (kernel vs kubelet) and **which QoS victim, and why** |
| [6.C4](../labs/06/28-6c4-disk-pressure-cascade.md) | **Disk-pressure eviction cascade** | The eviction manager's ranking and the `imagefs.available` threshold that fired, read on the Grafana time series |

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

**Lab** — [exercise 29](../labs/06/29-the-capstone-trace.md), which is also where the topology goes.

---

<a id="checklist"></a>
## 7. Checklist

Concrete, demonstrable, grouped by evidence type. No item says *understand* or *know*.

**Live against a running node:**
- [ ] `PLEG is not healthy` reproduced and traced to the `generic.go` latency check.
- [ ] One pod of each QoS class deployed; `oom_score_adj` read and matched to `policy.go`.
- [ ] An eviction driven to completion and read against `synchronize()`.
- [ ] The worker's allocatable computed and reconciled against the node's reported `allocatable`.
- [ ] Node-failure detection latency measured (kubelet stopped).
- [ ] `kube-prometheus-stack` up; an eviction read as a time series.

**Written artifacts (each is a module's Write-down):**
- [ ] The `relist` loop with the health-threshold `generic.go:line` (6.1).
- [ ] The three QoS classes, their OOM-score-adj, and the assigning rule (6.2).
- [ ] The eviction's signal/threshold/victim-order with citations (6.3).
- [ ] The worker's allocatable arithmetic, every subtraction cited (6.4).
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
