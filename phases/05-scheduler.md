# Phase 5 — Scheduler

> **4 weeks.** The best-documented area in the tree — the SIG wrote a function-by-function tour most people never find — and the one phase where the homelab's scarcity stops being a constraint and becomes the curriculum: preemption here has **real victims**.
> The range is planning information. **The gate at the bottom decides when the phase is finished.**

| | |
|---|---|
| **Prerequisites** | [P4](04-controllers.md) — the scheduler *is* a controller with an unusually interesting `syncHandler`. Its informers, its workqueue, and its "re-read from cache, don't trust the event" discipline are all machinery you hand-wired and watched survive a kill in P4. `eventhandlers.go` here is the same informer-events-feed-the-queue loop, closed. |
| **Unlocks** | [P6](06-kubelet-node.md) — the scheduler *decides* a pod's node; the kubelet *makes it real*. P6 picks up the pod the instant a `Binding` is POSTed here, and eviction there is the node-side mirror of preemption here (both remove a running pod under pressure — one from above, one from below). |
| **Source area** | [Area 3 — Scheduler](../strands/source-reading.md#area-3-scheduler), entry point `framework/interface.go`. **Read the three `sig-scheduling/` SIG docs first** — they are a guided tour written for exactly this, and skipping them is the specific waste this area warns about. The queue moved to `backend/queue/`: a live [archaeology](../strands/source-archaeology.md#stale-paths) case, older citations of `internal/queue/` are stale. |
| **Language** | Go — **two build artifacts**, a ~200-line from-scratch scheduler then an out-of-tree framework plugin, [both listed in the artifact table](../strands/build-mechanics.md#artifact-table). |
| **Lab** | **The one phase whose lab splits.** Build the two schedulers on [`pair`](https://github.com/k3ii/k8s-academy/issues/8) with `forge` at 2560 MB; **score and preempt on `workhorse`** (3 nodes) with `forge` back at 1536 MB — [`build-mechanics#p5-split`](../strands/build-mechanics.md#p5-split), because *scoring across two nodes teaches almost nothing* and 1536 MB will not link a scheduler. Nothing is compiled while `workhorse` is up. |
| **Strands** | [source reading](../strands/source-reading.md#area-3-scheduler) · [build](../strands/build-mechanics.md#p5-split) · [talks](../strands/talks.md#scheduler) · [chaos](../strands/chaos.md#principle) |

---

## 1. Objectives

Every one is falsifiable — an artifact, a timed production, or a claim a hostile reader could check against source or a running cluster. *understand* and *know* appear nowhere.

By the end you can:

1. **Name every extension point** — `PreFilter → Filter → PostFilter → PreScore → Score → NormalizeScore → Reserve → Permit → PreBind → Bind → PostBind` — and say what returning an error at each does, derived from `framework/interface.go` *before* `schedule_one.go`.
2. **Build a ~200-line from-scratch scheduler** that watches unscheduled pods, picks a node, and POSTs a `Binding` — and name the one thing the real scheduler does that yours skips (`assume` and the scheduler cache).
3. **Trace one pod through `schedule_one.go`** — `schedulingCycle` then `bindingCycle` — citing `file:line`, and say why the bind is asynchronous.
4. **Explain `activeQ` / `backoffQ` / `unschedulablePods`** and when a pod moves between them, citing `scheduler_queues.md` and `backend/queue/` — naming the stale `internal/queue/` path as the archaeology case.
5. **Explain `percentage-of-nodes-to-score`** and why it exists, falsifiable against `schedule_one.go`'s `findNodesThatFitPod`.
6. **Cause a real preemption with real victims on `workhorse`** and narrate the queue transitions — which pod went where, and why it left `unschedulablePods` when it did. **This is the capstone.**
7. **Ship an out-of-tree plugin** (`kubernetes-sigs/scheduler-plugins`) that measurably changes placement under contention, run as a second scheduler via `schedulerName`.
8. **Diagnose a `FailedScheduling` backlog** to the specific failed plugin from the event message, citing the insufficient-resource messages in `noderesources/fit.go`.

---

## 2. Modules

Reading is [Area 3](../strands/source-reading.md#area-3-scheduler), and its sequencing rule is as load-bearing as P4's: **the SIG docs and `interface.go` before `schedule_one.go`**, the small plugins before the big ones. Each cited item carries a question to answer — no bare links. Modules 5.1–5.5 run on `pair`; 5.6 is the `workhorse` module.

### Module 5.1 — The framework as a table of contents (~4 days, `pair`)

`interface.go` is the whole scheduler declared as small Go interfaces with doc comments — a beginner can read it day one. Read the SIG's own tour alongside it.

**Read**

| Item | Answer from it |
|---|---|
| `sig-scheduling/scheduling_code_hierarchy_overview.md` (item 1, **read first**) | The SIG's function-by-function tour of `pkg/scheduler` in call order — *the single most underused doc in the corpus*. Read it with the source open. What is the call path from "pod appears" to "node chosen"? |
| `framework/interface.go` (item 4, ⭐) + `scheduler_framework_plugins.md` (item 2) | Every extension point as an interface, and the table of which in-tree plugin implements which. What does returning an error at `Filter` mean versus at `Reserve`? |
| `framework/plugins/registry.go` (item 5) + the three tiny plugins `nodename/`, `nodeunschedulable/`, `tainttoleration/` (item 7) | The default plugin set in one file, and the plugin *shape* at its smallest. What is the minimum a `FilterPlugin` must implement? |
| KEP-624 Scheduling Framework (item 3) | The scheduling-cycle-vs-binding-cycle split. Why are these two cycles, not one? |

**Do** — draw the extension-point sequence from memory, marking which run in the scheduling cycle and which in the binding cycle.

**Break it** — write a one-line `Filter` plugin that rejects every node; watch every pod go `Unschedulable` and read the event. That event message is the thread you pull in drill [5.C1](#3-chaos-drills).

**Write down** — the extension-point sequence with, per point, what an error there does.

### Module 5.2 — Build artifact 1: the from-scratch scheduler (~4 days, `pair`)

Before reading the real scheduling cycle, prove scheduling isn't magic — so the real one has something naive to show up.

**Do** — write a ~200-line scheduler: an informer on unscheduled pods (`spec.nodeName == ""`, your `schedulerName`), pick a node that fits, and `POST` a `Binding` to `/binding`. That is the entire contract with the apiserver. Run it against `pair`.

**Break it** — kill it mid-cycle (a preview of [5.C4](#3-chaos-drills)); the unbound pod simply waits and is re-picked on restart, because your scheduler is level-triggered exactly like the P4 controller — it reads pending pods from the cache, it does not consume an event.

**Write down** — the `POST /binding` call site in your code, and **the one thing the real scheduler does that yours skips**: `assume`, the optimistic cache write that lets it schedule the next pod before this bind is durable.

### Module 5.3 — The real scheduling cycle (~1 week, `pair`)

Now `schedule_one.go`, guided by the SIG doc — where the from-scratch scheduler is made to look naive.

**Read**

| Item | Answer from it |
|---|---|
| `schedule_one.go` — `schedulingCycle`, `bindingCycle`, `findNodesThatFitPod`, `prioritizeNodes`, `assume` (item 8) | The filter→score→reserve→permit→bind narrative in one file. Where does `assume` happen, and why is the bind pushed to an async goroutine? **This is objective 3.** |
| `noderesources/fit.go` (item 6) | `NodeResourcesFit`: requests-vs-allocatable, `PreFilter` state, and the exact insufficient-resource strings you'll see in `FailedScheduling`. Which line formats the message drill 5.C1 reads? |
| `framework/cycle_state.go` (item 9) | How `PreFilter` hands state to `Filter` without globals. Why can't a plugin just use a package variable? |

**Do** — run the default scheduler with `-v=10` and find, in the log, each stage of one pod's cycle you just read in source.

**Break it** — set `percentageOfNodesToScore` low on a full `workhorse` (preview) and observe placement quality drop; then explain from `findNodesThatFitPod` **why the default is adaptive**, not "score everything." (Objective 5.)

**Write down** — one pod's path through `schedulingCycle`/`bindingCycle` with `file:line`, and why bind is async.

### Module 5.4 — The queue (~1 week, `pair`)

Where mental models of the scheduler break — and a live archaeology case.

**Read**

| Item | Answer from it |
|---|---|
| `sig-scheduling/scheduler_queues.md` (item 14, **before the source**) | `activeQ`/`backoffQ`/`unschedulablePods` and the flush timings in seven pages. When does a pod leave `unschedulablePods`, and by which of the two paths? |
| `backend/queue/{backoff_queue.go, active_queue.go, unschedulable_entities.go}` (item 16) | **The archaeology case:** the queue moved here from `internal/queue/`. Find the current path yourself, then read `backoff_queue.go` for the exponential backoff. Which cluster event flushes `unschedulablePods` to `activeQ`? |
| KEP-4247 QueueingHint (item 15) + `eventhandlers.go` (item 18) | How a cluster event decides whether an unschedulable pod is worth retrying — and **which informer events feed the queue**, closing the loop back to [P4](04-controllers.md). Why does an arbitrary pod deletion make *this* unschedulable pod worth a retry? |

`scheduling_queue.go` (item 17, 101 KB) is **reference-only** — reach into it via the SIG doc, never read it front to back.

**Do** — submit an unschedulable pod, then free resources, and watch (`-v=10`) the QueueingHint fire and the pod move `unschedulablePods → activeQ`.

**Break it** — the full drill [5.C1](#3-chaos-drills): saturate the cluster, submit a pod, and follow it *into* `unschedulablePods` and back out, timing the backoff.

**Write down** — the two ways a pod leaves `unschedulablePods`, citing `scheduler_queues.md` and the current `backend/queue/` path, with a one-line note on why `internal/queue/` citations are stale.

### Module 5.5 — Preemption, and build artifact 2 (~1 week, build on `pair`)

Read the preemption algorithm, then build the out-of-tree plugin whose scoring you'll observe at scale in 5.6.

**Read**

| Item | Answer from it |
|---|---|
| KEP-268 Priority & Preemption (item 10) | PriorityClass, victim selection, PDB respect, the nominated-node mechanism. Why does a preempted pod get a *nominated* node rather than being scheduled immediately? |
| `framework/preemption/preemption.go` + `defaultpreemption/default_preemption.go` (items 11–12) | candidate nodes → simulate removal → `selectVictimsOnNode` → `PostFilter` returns a nominated node. Where is a `PodDisruptionBudget` accounted for, and what happens when it forbids the only viable eviction? |
| KEP-4832 Async Preemption (item 13) | Why victim *deletion* moved off the scheduling thread. What throughput problem did synchronous deletion cause? |

**Do (build artifact 2)** — write an out-of-tree plugin against `kubernetes-sigs/scheduler-plugins` (a `Score` or `Filter` extension) that measurably changes placement under contention. Build the image on `pair`, **push it to the `forge` registry** — it will be *run*, not compiled, on `workhorse`.

**Break it** — make your plugin return a hard error at `Reserve` for one node; watch the pod fail *after* scoring succeeded, and explain from `interface.go` why a `Reserve` failure is costlier than a `Filter` rejection.

**Write down** — the extension point your plugin implements and the `interface.go` line declaring it, plus the `selectVictimsOnNode` site you'll reference when narrating preemption in the capstone.

### Module 5.6 — Scoring and preemption at scale (~4 days, `workhorse`)

The one module that earns the third node. **`forge` drops to 1536 MB; run only pre-built images — nothing compiles here.**

**Do** — deploy your plugin from the `forge` registry as a second scheduler (`schedulerName`, `KubeSchedulerConfiguration`) on `workhorse`. Score real workloads across three nodes and show placement differs measurably from the default profile.

**Break it** — drills [5.C2](#3-chaos-drills) and [5.C3](#3-chaos-drills): drive a **real preemption with real victims** (a running pod actually evicted), and make a topology-spread constraint unsatisfiable. Scarcity here is genuine — the lab ceiling *is* the pressure, per [#8's constraint-as-curriculum](https://github.com/k3ii/k8s-academy/issues/8).

**Write down** — the capstone narrative: the queue transitions during one preemption, which victim was chosen and why, and when the preemptor left `unschedulablePods`.

---

## 3. Chaos drills

**Phase-authored and observed, not injected** — there is no scheduler-aware fault in either tool, and [Chaos Mesh arrives in P6](06-kubelet-node.md) regardless. These drills exploit real scarcity per [`chaos#principle`](../strands/chaos.md#principle): the homelab ceiling produces the pressure, so preemption has real victims rather than simulated ones.

| # | Drill | By hand | What you must produce afterwards |
|---|---|---|---|
| 5.C1 | **Unschedulable backlog** | saturate the cluster, submit one more pod | The pod's path into and out of `unschedulablePods`, the `FailedScheduling` message, and **which plugin** rejected it |
| 5.C2 | **Preemption with real victims** | submit a high-priority pod into a full cluster | Which running pod was evicted and why (`selectVictimsOnNode`), and the nominated-node handoff — the capstone's core |
| 5.C3 | **Unsatisfiable topology spread** | an anti-affinity / `topologySpreadConstraints` no node can satisfy | The pod stuck `Unschedulable`, **distinguished from resource starvation** by the event message |
| 5.C4 | **Two schedulers, one pod** | run the from-scratch and default scheduler with the same `schedulerName` | The conflict (double-bind race) or the recovery when yours crashes mid-cycle — the level-triggered guarantee from [P4](04-controllers.md), retested on the scheduler |

5.C2 and 5.C3 run on `workhorse`; 5.C1 and 5.C4 need only `pair`.

---

## 4. Talks

Full entries with runtimes under [Scheduler](../strands/talks.md#scheduler).

- **★ Deep Dive Into the Latest Kubernetes Scheduler Features** (Gharaibeh, SIG Scheduling) — the best available walk through the framework: the extension-point sequence, how preemption picks victims and why it can *fail* to make room, priority's interaction with the queue. Most of the runtime is mechanism despite the release-notes title. Watch it before module 5.3.
- **★ SIG-Scheduling Deep Dive** (Huang, Wang, Yin, Nakada, 2022) — the queue's *actual* behaviour: backoff, unschedulable pods, requeueing hints — exactly where scheduler mental models break. Watch it against module 5.4.
- **Kubernetes Scheduling Features / How Can I Make the System Do What I Want?** (Grabowski, 2017) — pre-framework, so predicates/priorities are raw functions over node lists. **Stale-but-useful:** the API was replaced in 1.19; its value is purely conceptual, and it *clarifies precisely because* it lacks the plugin abstraction.

---

## 5. Ecosystem

**`kubernetes-sigs/scheduler-plugins`** — the out-of-tree plugin repo that *is* build artifact 2.

- **Hands-on:** you build against it in module 5.5 — a real `Score`/`Filter` plugin run as a second scheduler, proving the framework's extension model is not theoretical.
- **Internals note:** it uses the identical `framework.Plugin` interfaces you read in `interface.go`, compiled *outside* the tree — the concrete demonstration that the in-tree plugins have no special privilege. The same repo hosts the reference implementations of coscheduling, capacity scheduling and network-aware scheduling.
- **Maturity:** a SIG-Scheduling subproject, versioned against Kubernetes minors — a plugin builds against a specific k/k version, which is why the [P5 lab split](../strands/build-mechanics.md#p5-split) exists at all. Batch/gang scheduling (**Kueue**) is the adjacent frontier the [talks](../strands/talks.md#scheduler) flag as *chase-only-if-relevant* — noted, not assigned.

---

## 6. Capstone

**A framework plugin that measurably changes placement under contention, plus a narrated preemption: which pod went where, and why it left `unschedulablePods` when it did.**

Two parts, checked together on `workhorse`:

1. **The plugin** (module 5.5–5.6): your out-of-tree `scheduler-plugins` build, run as a second scheduler via `schedulerName`, producing placement demonstrably different from the default profile under real contention — a measurement, not an assertion.
2. **The preemption narrative** (drill 5.C2): a real high-priority pod evicting a real victim, with the full queue-transition story — entry to `unschedulablePods`, the QueueingHint that flushed it, the nominated node, and the moment it reached `activeQ`.

**Cite `file:line` a hostile reader could check** — at minimum:
- the `interface.go` line declaring the extension point your plugin implements;
- the `assume` and async-bind sites in `schedule_one.go`;
- `selectVictimsOnNode` in `defaultpreemption/default_preemption.go` for the victim you observed;
- the `backend/queue/` transition, with the current path found yourself (not the stale `internal/queue/`).

Every path verified live per [P2's archaeology standard](../strands/source-archaeology.md#drills) — and the queue's relocation is the canonical [stale-path](../strands/source-archaeology.md#stale-paths) case, so a citation to `internal/queue/` is an automatic fail.

---

## 7. Checklist

Concrete, demonstrable, grouped by evidence type. No item says *understand* or *know*.

**Live against a running cluster:**
- [ ] The from-scratch scheduler binds a pod via `POST /binding` on `pair`.
- [ ] The out-of-tree plugin, run as a second scheduler on `workhorse`, measurably changes placement under contention.
- [ ] A real preemption evicts a real victim, narrated end to end (5.C2).

**Build artifacts:**
- [ ] Artifact 1: the ~200-line from-scratch scheduler.
- [ ] Artifact 2: the `scheduler-plugins` out-of-tree plugin, image built on `pair` and run from the `forge` registry on `workhorse`.

**Written artifacts (each is a module's Write-down):**
- [ ] The extension-point sequence, with what an error at each does (5.1).
- [ ] The `POST /binding` site, and what the real scheduler's `assume` does that yours skips (5.2).
- [ ] One pod's path through `schedulingCycle`/`bindingCycle` with `file:line`, and why bind is async (5.3).
- [ ] The two exits from `unschedulablePods`, current `backend/queue/` path, and why `internal/queue/` is stale (5.4).
- [ ] The plugin's extension point + `interface.go` line, and the `selectVictimsOnNode` site (5.5).
- [ ] The preemption queue-transition narrative (5.6 / capstone).

**Falsifiable claims — write, then verify against source:**
- [ ] Why `percentageOfNodesToScore` is adaptive rather than "score every node."
- [ ] Why a `Reserve` failure is costlier than a `Filter` rejection.
- [ ] Why victim *deletion* moved off the scheduling thread (KEP-4832).

---

## 8. Gate

You may advance to [P6](06-kubelet-node.md) when:

1. **Both schedulers exist and bind pods**, and you can name what the from-scratch one skips against the real one (`assume`, the cache). If scheduling still feels like magic, the ~200-line build did not land — **stay here**.
2. **You caused a real preemption and narrated the queue transitions with `file:line`.** This is the capstone; a preemption you *read about* but never drove does not count.
3. **The queue-path archaeology is reflexive** — you found `backend/queue/` yourself and can say why `internal/queue/` citations are stale. This is the [P2 skill](../strands/source-archaeology.md#stale-paths) applied to the scheduler, and from here the corpus assumes you check paths before trusting them.

The scheduler decides *where*. [P6](06-kubelet-node.md) is the kubelet making that decision real on the node — and the eviction manager there is this preemption seen from below, removing a running pod under pressure from the node instead of from the queue.
