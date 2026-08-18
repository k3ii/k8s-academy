# Phase 11 — Synthesis

> **2–3 weeks.** No new subsystem, no new tool, no new area. This phase reads *across* everything already read: it walks one request — `kubectl run nginx` — from the terminal to a running container, through every area entered in P2–P10, and it cites each seam to source. Then it uses the whole picture for the two operations that only make sense once you have it: a live minor-version upgrade with nothing dropped, and scaling under real load. This is the loop [P0](00-linux-primitives.md) opened in week one, closed.
> The range is planning information. **The gate at the bottom decides when the phase is finished.**

| | |
|---|---|
| **Prerequisites** | **All of P2–P10** — this is the only phase that is prerequisite on the whole descent. The trace crosses [Area 2](../strands/source-reading.md#area-2-api-machinery) (P3), [Area 1](../strands/source-reading.md#area-1-etcd) (P2), [Area 3](../strands/source-reading.md#area-3-scheduler) (P5), [Area 7](../strands/source-reading.md#area-7-kubelet) (P6) and [Area 5](../strands/source-reading.md#area-5-networking) (P7) in a single request, and lands on the [P0](00-linux-primitives.md) syscalls. An unentered area is an unreadable seam. |
| **Unlocks** | [P12](12-gitops-platform.md) — the climb back up. Everything before this phase asks *how does Kubernetes work*; having answered it end-to-end, P12 asks what you build on top so other people don't have to. The synthesis is the last thing that must be true before abstraction is honest. |
| **Source** | **The whole corpus**, re-read along one path rather than by subsystem — [the three cross-area traces](../strands/source-reading.md#traces), of which this phase attempts [trace #1](../strands/source-reading.md#trace-pod-create). No new file is opened that a prior phase didn't already read; what is new is reading them *in the order a single pod-create visits them*, which is the order no single phase could. |
| **Build track** | **None** — [build mechanics](../strands/build-mechanics.md#artifact-table) lists no P11 artifact. Everything this phase runs was built or installed earlier; synthesis produces a trace and two incident write-ups, not a binary. |
| **Ecosystem** | **None** — this phase installs nothing new. The [ecosystem distribution](https://github.com/k3ii/k8s-academy/issues/10) gives P11 no big rock by design: it is synthesis, not another tool. The distribution *comparison* that does appear (kubeadm vs k0s upgrade paths) is a property of the cluster you already run, folded into the upgrade capstone, not a new install. |
| **Lab** | [`pair`](https://github.com/k3ii/k8s-academy/issues/8) for the trace — two nodes are enough to watch scheduling pick one. **`workhorse` (3 nodes) for the upgrade-and-scale beat**, because a zero-downtime upgrade means draining one node at a time while the other two keep serving, which two nodes cannot demonstrate honestly. Switching topology mid-phase is itself the point: the trace needs a pod, the upgrade needs a quorum-plus-spare. |
| **Strands** | [talks](../strands/talks.md#debugging) · [chaos](../strands/chaos.md#manual-drills) · [archaeology](../strands/source-archaeology.md#drills) |

---

## 1. Objectives

Every one is falsifiable — a cited trace, a timed production, or a claim a hostile reader could check against source or a running cluster. *understand* and *know* appear nowhere; a trace you cannot cite is not a trace.

By the end you can:

1. **Walk `kubectl run nginx` from the terminal to a running container**, naming every area boundary it crosses and citing a `file:line` (or commit sha) at each — the six seams, not the endpoints.
2. **Name the exact handoff at each seam** — how the object leaves the client and enters the apiserver, leaves the apiserver and enters etcd, leaves etcd and reaches the scheduler, leaves the scheduler and reaches the kubelet, leaves the kubelet and becomes a container — as a mechanism, not a diagram label.
3. **Run a minor-version cluster upgrade with zero workload downtime**, proven by a load generator that records **0 dropped requests / 0 5xx** across the whole upgrade window, not by "it looked fine."
4. **Scale a workload under real load** and name, from observation, which component acted at each step (metrics → HPA → scheduler → kubelet) and the measured latency of each hop.
5. **Re-watch the DNS postmortem** and, at each layer it descends, name the phase that taught that layer — the talk's four-week descent is the curriculum's spine read backwards.
6. **Produce a one-page incident write-up** in the format [P1](01-operate-shallow.md)/[P6](06-kubelet-node.md)/[P8](08-storage.md) escalated: symptom, objects inspected in order, mechanism cited to source, fix.

---

## 2. Modules

The corpus offers no new reading here — every file below was opened in an earlier phase. The rule is unchanged and now at its strictest: **every hop resolves to a `file:line` a hostile reader could open**, and the deliverable *is* those citations. The [archaeology drill standard](../strands/source-archaeology.md#drills) applies with no slack: a seam you can describe but not cite is a seam you did not actually cross. Live-verify every path before trusting it — the tree moves ([stale paths](../strands/source-archaeology.md#stale-paths)).

### Module 11.1 — The trace on paper, before the cluster (~3 days)

You assemble the map from eight phases of notes *before* instrumenting anything, so the live trace confirms a prediction rather than discovers a path.

**Do** — from your P2–P10 notes alone, draw the full path of a pod-create and mark, at each area boundary, the file you expect the request to be in. Then read [trace #1's spec](../strands/source-reading.md#trace-pod-create) and reconcile — where your map is wrong is where a phase didn't land.

> **Question to answer from the source:** the trace crosses five areas. At each of the four *internal* seams, which single function hands the object to the next area — the last frame in area N and the first frame in area N+1? Name both.

**Break it** — chaos drill [11.C4](#3-chaos-drills): predict, then check, what the trace does when one component is down mid-flight (apiserver up, scheduler down → the pod sits `Pending` at a nameable line; scheduler up, kubelet down → `Scheduled` but not `Running`). The gap tells you which frame owns which transition.

**Write down** — the predicted map with a file per seam, kept beside you, corrected in red as the live modules below prove or disprove each guess.

### Module 11.2 — Seam A: client → apiserver → etcd (~4 days)

Areas [2](../strands/source-reading.md#area-2-api-machinery) (P3) and [1](../strands/source-reading.md#area-1-etcd) (P2), read as one continuous handoff.

**Do** — trace the create from `kubectl`'s command through the request filters, the create handler, the admission chain you read the dispatch for in P3, the generic registry, the etcd3 storage backend, and the etcd transaction that finally persists it — then confirm the write landed by reading it back out of etcd directly (the P2 skill).

> **Question to answer from the source:** `handlers/create.go` runs admission *before* the object reaches `registry/generic/registry/store.go`. Cite the line where admission is invoked, and the line in `storage/etcd3/store.go` where the object becomes an etcd `Txn` — and state what guarantees the object is validated *before* it is durable, not after.

**Break it** — chaos drill [11.C1](#3-chaos-drills): corrupt the `caBundle` on a `failurePolicy: Fail` webhook (the P3/[P10](10-security.md) admission chain) and watch the create wedge *at the admission line you just cited* — diagnosed from apiserver logs alone. The outage names the frame.

**Write down** — the `kubectl → filters → create.go → admission → store.go → etcd3/store.go → Txn` sub-path with a cited line at each arrow, and the raw etcd key the object landed under.

### Module 11.3 — Seam B: watch cache → scheduler → Binding (~3 days)

Area [3](../strands/source-reading.md#area-3-scheduler) (P5) — how the persisted-but-unscheduled pod becomes a scheduled one.

**Do** — trace the pod out of the watch cache into the scheduler's informer, through `schedule_one.go`'s filter/score cycle (the framework you built in P5), to the **Binding** it writes back through the apiserver — a second trip through Seam A, now for a `Binding` subresource. Watch the pod's `spec.nodeName` go from empty to set.

> **Question to answer from the source:** the scheduler does not mutate the pod's node field directly — it POSTs a `Binding`. Cite the line in `schedule_one.go` that issues the bind, and explain why binding is a separate write and not an in-place update of the pod the scheduler already holds in cache.

**Break it** — chaos drill [11.C4](#3-chaos-drills): cordon every node and create the pod. It persists (Seam A completes) but never binds — `Pending`, `unschedulable`, at the scheduler frame that gives up. Uncordon one and watch the exact line fire.

**Write down** — the `watch cache → informer → schedule_one.go → Binding` sub-path with the bind line cited, and the before/after of `spec.nodeName`.

### Module 11.4 — Seam C: kubelet → CRI → CNI → the syscalls (~4 days)

Areas [7](../strands/source-reading.md#area-7-kubelet) (P6) and [5](../strands/source-reading.md#area-5-networking) (P7) — the pod becomes a process, and the loop closes on [P0](00-linux-primitives.md).

**Do** — trace the bound pod arriving at the kubelet through `config/apiserver.go`, into `pod_workers.go`, to `kuberuntime_manager.computePodActions`, across the **CRI** gRPC boundary to the runtime, and out to the **CNI** ADD that wires the netns — the exact CNI plugin you built in [P7 module 7.2](07-networking.md). End at the namespaces and cgroups you created by hand in [P0](00-linux-primitives.md): the container the trace produces *is* those primitives, now created for you.

> **Question to answer from the source:** `computePodActions` decides *what* to do; cite the line where it decides a container must be created, and follow it to the CRI call. Then name the CNI ADD result — the veth/netns — and point at the P0 syscall (`clone`/`setns`/`unshare`) it corresponds to. The whole trace ends on a syscall you once made yourself.

**Break it** — chaos drill [11.C4](#3-chaos-drills): break the CNI (rename the plugin binary) and watch the pod stick at `ContainerCreating` — Seam C's last frame failing, the [CRI→CNI seam P6 named](06-kubelet-node.md) as the one it could only watch, now cited.

**Write down** — the `config/apiserver.go → pod_workers.go → computePodActions → CRI → CNI` sub-path cited to source, ending with the P0 syscall the running container reduces to. The three sub-paths (11.2/11.3/11.4) joined are the capstone.

### Module 11.5 — The postmortems, re-read with the internals known (~3 days)

The debugging corpus watched differently now. The [DNS talk](../strands/talks.md#debugging) was planted in [P1](01-operate-shallow.md) for its *method*; you re-watch it here for its *mechanism*, because you have now read every layer it descends into.

**Read/watch** — the [debugging strand](../strands/talks.md#debugging), the DNS four-week-incident talk first. Map its descent — apparent DNS failure → conntrack overflow → martian-packet drops → kernel source → a gRPC reconnect bug — onto the phases: conntrack is [P7](07-networking.md), the kernel drop is [P0](00-linux-primitives.md), the reconnect is a client the apiserver work in [P3](03-api-machinery.md) made legible.

> **Question to answer (from the talk against your own trace):** the talk's resolution was three lines of code, found four layers below the symptom. For each layer it descended, name the phase that taught you to read it — and name the one layer, if any, this curriculum still leaves you unable to read.

**Break it** — chaos drill [11.C3](#3-chaos-drills): reproduce the *shape* of the DNS incident on your own cluster — a rolling update, `conntrack -L` watched as the table fills — not to exhaust it, but to see the mechanism the talk names begin on hardware you own.

**Write down** — the DNS talk's descent as a layer-to-phase table, and a one-line statement of the transferable method it models: **hypothesis → instrument → disconfirm → descend a layer.**

---

## 3. Chaos drills

Anchored in [`chaos.md#manual-drills`](../strands/chaos.md#manual-drills). These are the drills the strand marks **permanently manual** — upgrade, botched rollout, drain — because the failure modes are *procedural*, not injected, and each needs the whole picture the earlier phases could not yet supply. They are the rehearsals the [§5](#5-capstone) upgrade-and-scale capstone assembles.

| # | Drill | Mechanism | What you must produce afterwards |
|---|---|---|---|
| 11.C1 | **Wedge a create at admission** | by hand (corrupt a `Fail` webhook `caBundle`) | The create failing *at the admission line cited in 11.2*, diagnosed from apiserver logs alone |
| 11.C2 | **Botched rollout during the upgrade window** | by hand — the fault is your own YAML ([manual-drills #5](../strands/chaos.md#manual-drills)) | The rollout wedged, recognised from the controller's behaviour, rolled back with `kubectl rollout undo` |
| 11.C3 | **Rolling update under conntrack watch** | by hand (`conntrack -L` during a rollout) | The conntrack table filling — the DNS-talk mechanism, observed on your cluster |
| 11.C4 | **Kill one trace component mid-flight** | by hand (cordon nodes / rename CNI / stop scheduler) | The pod stuck at the exact frame the missing component owns — `Pending`, `ContainerCreating` — cited |

Every drill here is **by hand** and stays that way ([manual-drills](../strands/chaos.md#manual-drills)): the skill is recognising your own procedure's failure from the system's behaviour, and injecting the fault externally removes exactly that skill. The drain drill lives in the capstone because it *is* the upgrade.

---

## 4. Talks

Full entries under [Cluster debugging and postmortems](../strands/talks.md#debugging) — the strand weights these most generously, and this is the phase they were saved for.

- **★ Logs Told Us It Was DNS… It Wasn't DNS** (Bernaille & Andrews, EU 2022) — **the best debugging talk in the corpus**, planted in [P1](01-operate-shallow.md) for method, re-watched here for mechanism. A four-week incident descended four layers to three lines of code; you can now read every layer. The module 11.5 spine.
- **★ How the OOM-Killer Deleted My Namespace** (Bernaille, NA 2020) — a node-level event cascading into a control-plane outcome. The lesson is coupling and blast radius across components that *look* independent — which, having traced them as one path, you can now see are not.
- **★ Kubernetes Failure Stories and How to Crash Your Clusters** (Jacobs, EU 2019) — the breadth-first survey of how clusters actually fail, from the curator of `k8s.af`. The pattern-catalogue against which your own two incidents are single data points.
- **★ 10 Ways to Shoot Yourself in the Foot with Kubernetes** (Bernaille & Boll, EU 2019) — ten production failures, each traced to a specific mechanism (conntrack, limits, DNS, controller assumptions). Effectively a failure-mode catalogue with root causes attached — read it as a checklist of seams to distrust.

---

## 5. Capstone

**Two capstones. The first proves you can read the whole machine; the second proves you can operate it without stopping it.**

### Capstone 1 — corpus trace #1, `kubectl run nginx` to a running container

Join the three sub-paths from modules 11.2–11.4 into one cited trace, terminal to container:

`kubectl` → request filters → `handlers/create.go` → admission chain → `registry/generic/registry/store.go` → `storage/etcd3/store.go` → etcd `Txn` → watch cache → scheduler informer → `schedule_one.go` → **Binding** → kubelet `config/apiserver.go` → `pod_workers.go` → `computePodActions` → **CRI** → **CNI** → the [P0](00-linux-primitives.md) namespaces and cgroups.

**Cite `file:line` a hostile reader could check at every seam** — this is [trace #1's spec](../strands/source-reading.md#trace-pod-create), and the deliverable is the *citations*, not the diagram. A reader clones `k/k` at your stated commit and opens every line. "The apiserver validates it" fails the gate; `create.go:NNN` (at sha `abc123`) passes. Attempted only now, after every area is behind you — and named in [P0](00-linux-primitives.md) as the target from week one, so this closes the loop the curriculum opened.

### Capstone 2 — a minor-version upgrade with nothing dropped, then scale under load

On `workhorse`, with a load generator running against a Service the whole time:

1. **Upgrade** one minor version — `kubeadm upgrade plan`/`apply` (and note where **k0s** differs), draining one node at a time so the other two keep serving, watching `kubectl drain` fight PDBs ([manual-drills #4/#7](../strands/chaos.md#manual-drills)). **Prove 0 dropped requests / 0 5xx** across the window from the load generator's own log — a re-readable artifact, the "file:line" of an operation with no source line.
2. **Scale under load** — drive load past the HPA threshold and name each component as it acts: metrics → HPA decision → new pod persisted (Seam A) → scheduled (Seam B) → running (Seam C) → in the Service's EndpointSlice ([P7](07-networking.md)). Record the measured latency of each hop; when a node can't satisfy the request, name the `Pending` frame.

The two capstones are one claim from two sides: you can read the machine top to bottom, and you can change it underneath a running load without it noticing.

---

## 6. Checklist

Concrete, demonstrable, grouped by evidence type. No item says *understand* or *know*.

**The trace (cited to source):**
- [ ] Seam A — `kubectl → filters → create.go → admission → store.go → etcd3/store.go → Txn` with a line at each arrow + the raw etcd key (11.2).
- [ ] Seam B — `watch cache → informer → schedule_one.go → Binding` with the bind line + `spec.nodeName` before/after (11.3).
- [ ] Seam C — `config/apiserver.go → pod_workers.go → computePodActions → CRI → CNI` with the P0 syscall it ends on (11.4).
- [ ] The three sub-paths joined into one trace, every seam cited at a stated commit sha (Capstone 1).

**Operations (proven by artifact):**
- [ ] A minor-version upgrade with the load generator showing **0 5xx** across the window (Capstone 2).
- [ ] A scale-under-load run with per-hop component and latency named, including the `Pending` frame when a node is full (Capstone 2).

**Written artifacts (each is a module's Write-down):**
- [ ] The paper trace-map, corrected in red against the live run (11.1).
- [ ] The DNS talk's descent as a layer-to-phase table + the transferable method one-liner (11.5).
- [ ] A one-page incident write-up from 11.C2, in the escalated [P1](01-operate-shallow.md)/[P6](06-kubelet-node.md)/[P8](08-storage.md) format.

**Falsifiable claims — write, then verify:**
- [ ] Why admission runs before the object is durable, not after (11.2).
- [ ] Why the scheduler POSTs a `Binding` instead of updating the pod in place (11.3).
- [ ] The one layer, if any, this curriculum still leaves you unable to read (11.5).

---

## 7. Gate

You may advance to [P12](12-gitops-platform.md) when:

1. **The full trace is cited, terminal to container** — every one of the six seams resolves to a `file:line` at a stated commit that a hostile reader opens and confirms. If any seam is a description rather than a citation, the area behind it did not land — **go back to that phase, not forward.** This is the gate the whole curriculum was built to reach.
2. **The upgrade dropped nothing** — the load generator's own log shows 0 5xx across a real minor-version upgrade on `workhorse`, and you can name which node was draining at each moment. "It seemed fine" is not the artifact; the log is.
3. **You scaled under load and narrated it by component** — metrics → HPA → Seam A → B → C → EndpointSlice, with the frame that stalls when a node is full. If scaling is still "Kubernetes handled it," the trace did not transfer to operations.

The descent is over. [P12](12-gitops-platform.md) is the inverse of everything before it — eleven phases removed abstraction; the last one builds it back, deliberately, for people who will never read the trace you just cited. You can only hide a machine well once you have seen all of it, which is why this gate comes first.
