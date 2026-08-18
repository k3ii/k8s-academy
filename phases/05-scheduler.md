# Phase 5 — Scheduler

> **4 weeks.** The best-documented area in the tree — the SIG wrote a function-by-function tour most people never find — and the one phase where the homelab's scarcity stops being a constraint and becomes the curriculum: preemption here has **real victims**.
> The range is planning information. **The gate at the bottom decides when the phase is finished.**

| | |
|---|---|
| **Prerequisites** | [P4](04-controllers.md) — the scheduler *is* a controller with an unusually interesting `syncHandler`. Its informers, its workqueue, and its "re-read from cache, don't trust the event" discipline are all machinery you hand-wired and watched survive a kill in P4. `eventhandlers.go` here is the same informer-events-feed-the-queue loop, closed. |
| **Unlocks** | [P6](06-kubelet-node.md) — the scheduler *decides* a pod's node; the kubelet *makes it real*. P6 picks up the pod the instant a `Binding` is POSTed here, and eviction there is the node-side mirror of preemption here (both remove a running pod under pressure — one from above, one from below). |
| **Source area** | [Area 3 — Scheduler](../strands/source-reading.md#area-3-scheduler), entry point `framework/interface.go`. **Read the three `sig-scheduling/` SIG docs first** — they are a guided tour written for exactly this, and skipping them is the specific waste this area warns about. The queue moved to `backend/queue/`: a live [archaeology](../strands/source-archaeology.md#stale-paths) case, older citations of `internal/queue/` are stale. |
| **Language** | Go — **two build artifacts**, a ~200-line from-scratch scheduler then an out-of-tree framework plugin, [both listed in the artifact table](../strands/build-mechanics.md#artifact-table). |
| **Lab** | **The one phase whose lab splits.** Build the two schedulers on [`pair`](../strands/lab-topologies.md#pair) with `forge` at 2560 MB; **score and preempt on `workhorse`** (3 nodes) with `forge` back at 1536 MB — [`build-mechanics#p5-split`](../strands/build-mechanics.md#p5-split), because *scoring across two nodes teaches almost nothing* and 1536 MB will not link a scheduler. Nothing is compiled while `workhorse` is up. |
| **Labs** | [`labs/05/`](../labs/05/README.md) — 37 exercises, in order. `forge` resizes **up at [exercise 7](../labs/05/07-fifteen-thirty-six-will-not-link-a-scheduler.md) and back down at [exercise 33](../labs/05/33-forge-back-down-and-workhorse-up.md)**; both are steps, not footnotes. |
| **Strands** | [source reading](../strands/source-reading.md#area-3-scheduler) · [build](../strands/build-mechanics.md#p5-split) · [talks](../strands/talks.md#scheduler) · [chaos](../strands/chaos.md#principle) |

---

<a id="objectives"></a>
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

<a id="modules"></a>
## 2. Modules

Reading is [Area 3](../strands/source-reading.md#area-3-scheduler), and its sequencing rule is as load-bearing as P4's: **the SIG docs and `interface.go` before `schedule_one.go`**, the small plugins before the big ones. Each cited item carries a question to answer — no bare links. Modules 5.1–5.5 run on `pair`; 5.6 is the `workhorse` module.

<a id="m5-1"></a>
### Module 5.1 — The framework as a table of contents (~4 days, `pair`)

`interface.go` is the whole scheduler declared as small Go interfaces with doc comments — a beginner can read it day one. Read the SIG's own tour alongside it.

**Read**

| Item | Answer from it |
|---|---|
| `sig-scheduling/scheduling_code_hierarchy_overview.md` (item 1, **read first**) | The SIG's function-by-function tour of `pkg/scheduler` in call order — *the single most underused doc in the corpus*. Read it with the source open. What is the call path from "pod appears" to "node chosen"? |
| `framework/interface.go` (item 4, ⭐) + `scheduler_framework_plugins.md` (item 2) | Every extension point as an interface, and the table of which in-tree plugin implements which. What does returning an error at `Filter` mean versus at `Reserve`? |
| `framework/plugins/registry.go` (item 5) + the three tiny plugins `nodename/`, `nodeunschedulable/`, `tainttoleration/` (item 7) | The default plugin set in one file, and the plugin *shape* at its smallest. What is the minimum a `FilterPlugin` must implement? |
| KEP-624 Scheduling Framework (item 3) | The scheduling-cycle-vs-binding-cycle split. Why are these two cycles, not one? |

**Labs** — [The tour the SIG wrote, read with the source open](../labs/05/01-the-sig-tour-in-call-order.md) · [The extension points, and what an error at each one costs](../labs/05/02-eleven-points-and-what-an-error-does.md) · [Two cycles, one thread](../labs/05/03-two-cycles-not-one.md) · [The default plugin set, mapped onto the points it fills](../labs/05/04-what-actually-runs-by-default.md) · [A `Filter` plugin is two methods and a string](../labs/05/05-the-smallest-plugin-that-exists.md) · [Three ways to make every node refuse](../labs/05/06-three-rejections-three-plugins.md)

<a id="m5-2"></a>
### Module 5.2 — Build artifact 1: the from-scratch scheduler (~4 days, `pair`)

Before reading the real scheduling cycle, prove scheduling isn't magic — so the real one has something naive to show up.

**Labs** — [The OOM you were promised, produced on purpose](../labs/05/07-fifteen-thirty-six-will-not-link-a-scheduler.md) · [Scheduling, minus the scheduler: one POST](../labs/05/08-bind-a-pod-with-one-post.md) · [Build artifact 1: a scheduler with no framework in it](../labs/05/09-two-hundred-lines-that-schedule.md) · [5.C4 — two schedulers, one pod](../labs/05/10-5c4-two-schedulers-one-pod.md) · [The node that fits ten times because the cache has not caught up](../labs/05/11-what-assume-buys.md)

<a id="m5-3"></a>
### Module 5.3 — The real scheduling cycle (~1 week, `pair`)

Now `schedule_one.go`, guided by the SIG doc — where the from-scratch scheduler is made to look naive.

**Read**

| Item | Answer from it |
|---|---|
| `schedule_one.go` — `schedulingCycle`, `bindingCycle`, `findNodesThatFitPod`, `prioritizeNodes`, `assume` (item 8) | The filter→score→reserve→permit→bind narrative in one file. Where does `assume` happen, and why is the bind pushed to an async goroutine? **This is objective 3.** |
| `noderesources/fit.go` (item 6) | `NodeResourcesFit`: requests-vs-allocatable, `PreFilter` state, and the exact insufficient-resource strings you'll see in `FailedScheduling`. Which line formats the message drill 5.C1 reads? |
| `framework/cycle_state.go` (item 9) | How `PreFilter` hands state to `Filter` without globals. Why can't a plugin just use a package variable? |

**Labs** — [One pod, at `-v=10`, mapped onto `schedule_one.go`](../labs/05/12-one-pod-through-schedule-one.md) · [Pod B is scheduled while pod A is still being bound](../labs/05/13-why-the-bind-is-async.md) · [Why a plugin cannot keep state in a package variable](../labs/05/14-state-without-globals.md) · [`Insufficient cpu` — the line that formats it](../labs/05/15-the-line-that-writes-insufficient-cpu.md) · [The knob that cannot move here](../labs/05/16-the-knob-that-cannot-move-here.md) · [Above the floor at last: a hundred nodes that do not exist](../labs/05/17-a-hundred-nodes-that-do-not-exist.md)

<a id="m5-4"></a>
### Module 5.4 — The queue (~1 week, `pair`)

Where mental models of the scheduler break — and a live archaeology case.

**Read**

| Item | Answer from it |
|---|---|
| `sig-scheduling/scheduler_queues.md` (item 14, **before the source**) | `activeQ`/`backoffQ`/`unschedulablePods` and the flush timings in seven pages. When does a pod leave `unschedulablePods`, and by which of the two paths? |
| `backend/queue/{backoff_queue.go, active_queue.go, unschedulable_entities.go}` (item 16) | **The archaeology case:** the queue moved here from `internal/queue/`. Find the current path yourself, then read `backoff_queue.go` for the exponential backoff. Which cluster event flushes `unschedulablePods` to `activeQ`? |
| KEP-4247 QueueingHint (item 15) + `eventhandlers.go` (item 18) | How a cluster event decides whether an unschedulable pod is worth retrying — and **which informer events feed the queue**, closing the loop back to [P4](04-controllers.md). Why does an arbitrary pod deletion make *this* unschedulable pod worth a retry? |

`scheduling_queue.go` (item 17, 101 KB) is **reference-only** — reach into it via the SIG doc, never read it front to back.

**Labs** — [The archaeology case: the path that no longer exists](../labs/05/18-find-the-queue-yourself.md) · [The queue state machine, written before any code is opened](../labs/05/19-three-queues-and-two-exits.md) · [A pod moving between queues, timed](../labs/05/20-watch-a-pod-move.md) · [Attempt 1, 3 and 6: the gaps double until they stop](../labs/05/21-the-backoff-you-can-time.md) · [5.C1 — fifty pods that will not schedule](../labs/05/22-5c1-an-unschedulable-backlog.md) · [Ten cluster changes, one retry](../labs/05/23-the-hint-that-decides-a-retry.md) · [`SchedulingGated` — a pod the scheduler declines to look at](../labs/05/24-a-pod-that-is-never-considered.md)

<a id="m5-5"></a>
### Module 5.5 — Preemption, and build artifact 2 (~1 week, build on `pair`)

Read the preemption algorithm, then build the out-of-tree plugin whose scoring you'll observe at scale in 5.6.

**Read**

| Item | Answer from it |
|---|---|
| KEP-268 Priority & Preemption (item 10) | PriorityClass, victim selection, PDB respect, the nominated-node mechanism. Why does a preempted pod get a *nominated* node rather than being scheduled immediately? |
| `framework/preemption/preemption.go` + `defaultpreemption/default_preemption.go` (items 11–12) | candidate nodes → simulate removal → `selectVictimsOnNode` → `PostFilter` returns a nominated node. Where is a `PodDisruptionBudget` accounted for, and what happens when it forbids the only viable eviction? |
| KEP-4832 Async Preemption (item 13) | Why victim *deletion* moved off the scheduling thread. What throughput problem did synchronous deletion cause? |

**Labs** — [The preemptor gets a claim, not the node](../labs/05/25-priority-and-the-nominated-node.md) · [A PDB that makes preemption fail, and says so](../labs/05/26-selectvictimsonnode-and-a-pdb-that-forbids.md) · [Why victim deletion left the scheduling thread](../labs/05/27-why-victim-deletion-left-the-thread.md) · [Build artifact 2: a scoring plugin in a scheduler you own](../labs/05/28-the-out-of-tree-plugin.md) · [Failing after the decision costs more than failing before it](../labs/05/29-a-hard-error-at-reserve.md) · [Stage 2, shape one: a Deployment nobody privileged](../labs/05/30-a-second-scheduler-by-schedulername.md) · [Stage 2, shape two: one process, two scheduler names](../labs/05/31-a-profile-not-a-binary.md) · [Both artifacts, two replicas each, one lease](../labs/05/32-the-lease-changes-hands.md)

<a id="m5-6"></a>
### Module 5.6 — Scoring and preemption at scale (~4 days, `workhorse`)

The one module that earns the third node. **`forge` drops to 1536 MB; run only pre-built images — nothing compiles here.**

**Labs** — [The revert: 2560MB back to 1536MB](../labs/05/33-forge-back-down-and-workhorse-up.md) · [The same workload, two profiles, two distributions](../labs/05/34-placement-that-differs-measurably.md) · [5.C2 — which pod died, on which node, and why that one](../labs/05/35-5c2-preemption-with-real-victims.md) · [5.C3 — unschedulable for a reason that is not scarcity](../labs/05/36-5c3-a-spread-nobody-can-satisfy.md) · [The capstone: a measurement and a story](../labs/05/37-the-capstone-narrative.md)

---

<a id="chaos"></a>
## 3. Chaos drills

**Phase-authored and observed, not injected** — there is no scheduler-aware fault in either tool, and [Chaos Mesh arrives in P6](06-kubelet-node.md) regardless. These drills exploit real scarcity per [`chaos#principle`](../strands/chaos.md#principle): the homelab ceiling produces the pressure, so preemption has real victims rather than simulated ones.

| # | Drill | What you must produce afterwards |
|---|---|---|
| [5.C1](../labs/05/22-5c1-an-unschedulable-backlog.md) | **Unschedulable backlog** | The pod's path into and out of `unschedulablePods`, the `FailedScheduling` message, and **which plugin** rejected it |
| [5.C2](../labs/05/35-5c2-preemption-with-real-victims.md) | **Preemption with real victims** | Which running pod was evicted and why (`selectVictimsOnNode`), and the nominated-node handoff — the capstone's core |
| [5.C3](../labs/05/36-5c3-a-spread-nobody-can-satisfy.md) | **Unsatisfiable topology spread** | The pod stuck `Unschedulable`, **distinguished from resource starvation** by the event message |
| [5.C4](../labs/05/10-5c4-two-schedulers-one-pod.md) | **Two schedulers, one pod** | The conflict (double-bind race) or the recovery when yours crashes mid-cycle — the level-triggered guarantee from [P4](04-controllers.md), retested on the scheduler |

5.C2 and 5.C3 run on `workhorse`; 5.C1 and 5.C4 need only `pair`.

---

<a id="talks"></a>
## 4. Talks

Full entries with runtimes under [Scheduler](../strands/talks.md#scheduler).

- **★ Deep Dive Into the Latest Kubernetes Scheduler Features** (Gharaibeh, SIG Scheduling) — the best available walk through the framework: the extension-point sequence, how preemption picks victims and why it can *fail* to make room, priority's interaction with the queue. Most of the runtime is mechanism despite the release-notes title. Watch it before module 5.3.
- **★ SIG-Scheduling Deep Dive** (Huang, Wang, Yin, Nakada, 2022) — the queue's *actual* behaviour: backoff, unschedulable pods, requeueing hints — exactly where scheduler mental models break. Watch it against module 5.4.
- **Kubernetes Scheduling Features / How Can I Make the System Do What I Want?** (Grabowski, 2017) — pre-framework, so predicates/priorities are raw functions over node lists. **Stale-but-useful:** the API was replaced in 1.19; its value is purely conceptual, and it *clarifies precisely because* it lacks the plugin abstraction.

---

<a id="ecosystem"></a>
## 5. Ecosystem

**`kubernetes-sigs/scheduler-plugins`** — the out-of-tree plugin repo that *is* build artifact 2.

- **Hands-on:** you build against it in module 5.5 — a real `Score`/`Filter` plugin run as a second scheduler, proving the framework's extension model is not theoretical.
- **Internals note:** it uses the identical `framework.Plugin` interfaces you read in `interface.go`, compiled *outside* the tree — the concrete demonstration that the in-tree plugins have no special privilege. The same repo hosts the reference implementations of coscheduling, capacity scheduling and network-aware scheduling.
- **Maturity:** a SIG-Scheduling subproject, versioned against Kubernetes minors — a plugin builds against a specific k/k version, which is why the [P5 lab split](../strands/build-mechanics.md#p5-split) exists at all. Batch/gang scheduling (**Kueue**) is the adjacent frontier the [talks](../strands/talks.md#scheduler) flag as *chase-only-if-relevant* — noted, not assigned.

---

<a id="capstone"></a>
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

**Lab** — [The capstone: a measurement and a story](../labs/05/37-the-capstone-narrative.md), which runs the two-profile measurement and the preemption on the same `workhorse` and assembles the four citations.

Every path verified live per [P2's archaeology standard](../strands/source-archaeology.md#drills) — and the queue's relocation is the canonical [stale-path](../strands/source-archaeology.md#stale-paths) case, so a citation to `internal/queue/` is an automatic fail.

---

<a id="checklist"></a>
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

<a id="gate"></a>
## 8. Gate

You may advance to [P6](06-kubelet-node.md) when:

1. **Both schedulers exist and bind pods**, and you can name what the from-scratch one skips against the real one (`assume`, the cache). If scheduling still feels like magic, the ~200-line build did not land — **stay here**.
2. **You caused a real preemption and narrated the queue transitions with `file:line`.** This is the capstone; a preemption you *read about* but never drove does not count.
3. **The queue-path archaeology is reflexive** — you found `backend/queue/` yourself and can say why `internal/queue/` citations are stale. This is the [P2 skill](../strands/source-archaeology.md#stale-paths) applied to the scheduler, and from here the corpus assumes you check paths before trusting them.

The scheduler decides *where*. [P6](06-kubelet-node.md) is the kubelet making that decision real on the node — and the eviction manager there is this preemption seen from below, removing a running pod under pressure from the node instead of from the queue.
