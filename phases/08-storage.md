# Phase 8 — Storage

> **3–4 weeks**, plus a **1–2 week CKA drill block** at the end.
> The range is planning information. **The gate at the bottom of this file decides when the phase is finished** — not the calendar. A phase that runs long and passes its gate has succeeded.

| | |
|---|---|
| **Prerequisites** | [P4 Controllers](04-controllers.md) — the `syncClaim`/`syncVolume` loops are unreadable without informers and workqueues. [P5 Scheduler](05-scheduler.md) — `WaitForFirstConsumer` lives *in the scheduler*, so its plugin sequence must already be familiar. [P6 kubelet](06-kubelet-node.md) — the volume manager reuses the desired/actual-state-of-world pattern. |
| **Unlocks** | The **CKA** checkpoint (this is the last phase whose material the exam covers). [P12](12-gitops-platform.md)'s platform API provisions storage, so this is where you learn what you'll be abstracting. |
| **Source area** | [Area 6 — Storage](../strands/source-reading.md#area-6-storage) |
| **Language** | Go ([#9](https://github.com/k3ii/k8s-academy/issues/9)) |
| **Labs** | [`labs/08/`](../labs/08/README.md) — twenty exercises, in order |
| **Strands** | [certs](../strands/certs.md#cka) · [chaos](../strands/chaos.md#catalogue) · [talks](../strands/talks.md#storage) · [build mechanics](../strands/build-mechanics.md#artifact-table) · [source archaeology](../strands/source-archaeology.md#stale-paths) |

---

## 1. Objectives

Mechanism-level. Each is phrased so that failing it is detectable — "understand storage" is not on this list, and the word *understand* appears nowhere in it.

By the end of this phase you can:

1. **Name which component issues each of the five CSI calls**, in order, for a dynamically-provisioned volume — and explain why `NodeStageVolume` happens once per node while `NodePublishVolume` happens once per pod.
2. **Predict which PV a given PVC will bind to**, before applying it, by reasoning through `findBestMatchForClaim`'s predicate — access modes, capacity, selector, class, volume mode — and be right.
3. **Explain why delayed binding lives in the scheduler and not the PV controller**, and state concretely what breaks if it doesn't: the volume gets provisioned in one topology domain and the pod scheduled in another.
4. **Explain the `desiredStateOfWorld`/`actualStateOfWorld` pattern**, name the two components that use it, and explain why storage in particular needs reconciliation against observed reality rather than a single sync.
5. **Explain why a PVC with the `kubernetes.io/pvc-protection` finalizer will not delete**, what is holding it, and how to clear it correctly — not by removing the finalizer.
6. **Explain the two-phase volume expansion**, why it is two phases, and what the `FileSystemResizePending` condition means about which phase is outstanding.
7. **Say what to ignore in `pkg/volume/`** and why it is still there — the in-tree-to-CSI migration story.
8. **Write a CSI driver that passes `csi-sanity`.**

---

## 2. Modules

<a id="m8-1"></a>
### Module 8.1 — The CSI contract, before any Kubernetes code (~3 days)

Read the spec *first*. The in-tree volume subsystem is sprawling, historically layered and full of dead in-tree-plugin scaffolding; the CSI spec is a clean gRPC contract, and it makes the sprawl suddenly coherent. Reading them in the other order is the single most common way to waste a week here.

**Read** — [Area 6](../strands/source-reading.md#area-6-storage) items 1–3. For each, the question to answer *from the source*, not from a blog:

| Read | Answer from it |
|---|---|
| `container-storage-interface/spec/spec.md` + `csi.proto` | Which of the three services (Identity / Controller / Node) must a driver implement to be minimally useful, and which are optional? Which calls **must** be idempotent, and where does the spec say so? |
| `design-proposals-archive/storage/persistent-storage.md` | Why is storage **two objects** rather than one? Write the answer in terms of who owns each — this is the whole PV/PVC design in one sentence. |
| `design-proposals-archive/storage/volume-provisioning.md` | What problem does `StorageClass` solve that a PV template would not? |

**No lab** — this module is reading, and it is the highest-leverage three days in the phase. Its answer is an input to [stage 1](../labs/08/12-csi-driver-sanity.md), where `csi-sanity` checks it for you.

---

<a id="m8-2"></a>
### Module 8.2 — PV/PVC binding, by hand (~4 days)

**Read** — Area 6 item 4, `pkg/controller/volume/persistentvolume/index.go` (6.8 KB). Small, self-contained, and the single most useful storage file for a beginner.

> **Question to answer from the source:** `findBestMatchForClaim` walks candidate PVs. In what order, and what is the tie-break when two PVs both satisfy the claim? Cite the line.

Then Area 6 items 8 and 9 — `pv_controller_base.go` (the skeleton: informers, two sync loops, resync) **before** `pv_controller.go`. The big one is 92.8 KB and is **reference-only as a whole**; read exactly four functions: `syncClaim`, `syncVolume`, `bind`, `provisionClaim`.

**Labs** — [Predict which PV a PVC will bind to](../labs/08/01-predict-the-bind.md) · [A released PV does not return to the pool](../labs/08/02-released-not-available.md) · [Binding is reconciled state](../labs/08/03-rewrite-a-claimref.md)

---

<a id="m8-3"></a>
### Module 8.3 — Delayed binding, and why it lives in the scheduler (~3 days)

The conceptual centre of the phase, and the place where P5 pays off.

**Read** — Area 6 item 11, `design-proposals-archive/storage/volume-topology-scheduling.md`, **before** any code. The corpus is explicit that item 12's code is "nearly unreadable without it." Then item 12, `pkg/scheduler/framework/plugins/volumebinding/volume_binding.go`.

> **Path note, and a live example of [source archaeology](../strands/source-archaeology.md#stale-paths) from P2:** this moved from `pkg/controller/volume/scheduling/`, which **no longer exists**. Any material citing that path is stale. Before reading the plugin, do [archaeology drill 1](../strands/source-archaeology.md#drills) — find the commit that deleted the old path and read its PR. The move *is* the lesson: the decision has to be made where the node is chosen.

> **Question to answer from the source:** `volume_binding.go` implements `PreFilter`, `Filter`, `Reserve` and `PreBind`. What does each one do about volumes, and why does the work have to be split across four extension points rather than done in one?

Then item 13's `assume_cache.go` — how the scheduler acts on binds that are not yet persisted.

**Labs** — [Delayed binding, observed](../labs/08/04-delayed-binding-observed.md) · [Build the failure it prevents](../labs/08/05-zone-mismatch-by-construction.md) · [Four ways a PVC stays Pending](../labs/08/06-four-ways-a-pvc-stays-pending.md)

---

<a id="m8-4"></a>
### Module 8.4 — The node side: attach, stage, publish (~4 days)

**Read** — Area 6 items 15, 16, 18:
- `attachdetach/attach_detach_controller.go` + `reconciler/` — learn the DSW/ASW pattern **here**, where it is smaller, because the kubelet volume manager reuses it.
- `pkg/kubelet/volumemanager/` — the node-side half, including `populator/` turning the pod list into desired state.
- `pkg/volume/csi/csi_client.go` **first** of that group — it maps one-to-one onto the RPCs from module 8.1, which makes it the easiest bridge between spec and implementation in the whole area.

> **Question to answer from the source:** find where `--attach-detach-reconcile-sync-period` is consumed. What happens to a *stuck* detach as that period elapses, and what does that imply about how long a node failure takes to release a volume?

Also read Area 6 item 23, **KEP-625 (in-tree to CSI migration)** — not for the migration itself, but to know **what to ignore in `pkg/volume/`**. Without this you will waste days on dead plugin scaffolding.

**Labs** — [Follow one volume down to a mount line](../labs/08/07-volume-to-mount-trace.md) · [Unmount a volume under a running pod](../labs/08/08-umount-under-a-running-pod.md)

---

<a id="m8-5"></a>
### Module 8.5 — Expansion, snapshots, and finalizers (~3 days)

The short module, but it holds three of the most instructive failure modes in Kubernetes storage.

**Read** — Area 6 items 19/20 (expansion, and **KEP-1790: recovering from an expansion you cannot fulfil** — a wonderfully instructive failure), item 21 (**KEP-177 snapshots**: note these are **CRDs plus `external-snapshotter`, out of tree** — the same two-object pattern as PV/PVC), and item 26, `pkg/controller/volume/{pvprotection,pvcprotection}/` — tiny packages and the best concrete finalizer example in the codebase.

> **Question to answer from the source:** expansion is two-phase, controller then node. Which phase sets `FileSystemResizePending`, and which clears it? What must be true of the pod for the node phase to proceed?

**Labs** — [Expansion is two phases](../labs/08/09-expansion-two-phase.md) · [Snapshot, destroy the source, restore](../labs/08/10-snapshot-and-restore.md) · [A PVC that will not delete](../labs/08/11-finalizer-deadlock.md)

---

<a id="artifact"></a>
## 3. Build-track artifact — a CSI driver

The phase's build component, inline per the spine. Roughly a week, running alongside modules 8.2–8.5 rather than after them.

**Reference implementations to read, not copy:** `kubernetes-csi/csi-driver-host-path` (the canonical toy) and `kubernetes-csi/external-provisioner`'s `doc/design.md` (Area 6 item 6) — the sidecar pattern of *Kubernetes controllers translating Kubernetes objects into CSI RPCs* is the architectural idea to take away.

**Why this artifact.** It is the one place in the curriculum where the thing you write is checked by something other than your own judgement. `csi-sanity` (from `kubernetes-csi/csi-test`) either passes or it does not, and it finds idempotency bugs no amount of manual testing would — which is exactly why module 8.1 asked you to locate the spec's idempotency requirements first.

Both halves of the [two-stage rule](../strands/build-mechanics.md#two-stages) apply, and here the two stages are genuinely different exercises with different footprints: stage 1 is a UNIX socket with **no Kubernetes present at all** — no topology, no cluster — and only then do the sidecars arrive.

> **Scope discipline:** no snapshots, no expansion, no topology in your driver. Those are read about in module 8.5, not implemented. A driver that passes `csi-sanity` for the basic lifecycle is the goal; a driver that grows features is a month you did not budget.

**Labs** — [A CSI driver passing `csi-sanity`, no cluster](../labs/08/12-csi-driver-sanity.md) · [Deploy the driver with its sidecars](../labs/08/13-csi-driver-in-cluster.md)

---

<a id="chaos"></a>
## 4. Chaos drills

Storage failures are slow, which makes them a different diagnostic skill from the fast failures of earlier phases — the symptom often appears minutes after the cause. All drills use **Chaos Mesh** (introduced in [P6](06-kubelet-node.md), 582Mi minimised) except where noted; the mechanism behind each action is in the [chaos catalogue](../strands/chaos.md#catalogue), and [the principle](../strands/chaos.md#principle) still holds — by hand first, scripted second.

| # | Drill | What you must be able to say afterwards |
|---|---|---|
| 8.C1 | [**Slow disk under a workload**](../labs/08/14-chaos-slow-disk.md) | Which layer surfaced the symptom first, and why a pod can be `Running` and useless simultaneously |
| 8.C2 | [**I/O errors**](../labs/08/15-chaos-io-errors.md) | What the application saw versus what the kubelet reported. Partial failure is harder than total failure |
| 8.C3 | [**Volume detach failure**](../labs/08/16-chaos-detach-failure.md) | Where the retry loop lives, its period, and what the `VolumeAttachment` looks like while stuck |
| 8.C4 | [**Node loss with a volume attached**](../labs/08/19-chaos-node-loss.md) | How long until the cluster gives up on the volume, which flag governs that, and why it does not come back elsewhere on this lab. This is drill 8.C4 *and* the answer to module 8.4's reading question |
| 8.C5 | [**Disk fill**](../labs/08/17-chaos-disk-fill.md) | The eviction path for disk pressure versus memory pressure — connects to P6 |
| 8.C6 | [**Kubelet restart with mounts held**](../labs/08/18-chaos-kubelet-restart.md) | What reconstruction recovers and what it cannot (KEP-3756) |

**8.C4 is the one to spend real time on.** It is the storage failure most likely to be encountered in production, it has a genuinely surprising duration, and it cannot be scripted — which is the point. It runs last of the six because it ends the phase's cluster.

---

## 5. Talks

Slotted where they reinforce this phase. Full entries, with exact runtimes, under [Storage](../strands/talks.md#storage) in the talk index.

- **Container Storage Interface: Present and Future** — the CSI architecture from the people who designed it. Watch after module 8.1, so the spec is fresh.
- **Kubernetes Storage Lingo 101** — worth it only if the PV/PVC/SC/VolumeAttachment vocabulary is still slippery after 8.2. Skip if not.
- Re-watch, from P6: **Evicted! All the Ways Kubernetes Kills Your Pods** — the disk-pressure section means something different now.

---

<a id="ecosystem"></a>
## 6. Ecosystem

One light rock this phase, deliberately — the build artifact is the heavy item.

**`local-path-provisioner`** (Rancher) — the provisioner that k0s and k3s ship. Tiny footprint, which is why it is here rather than Longhorn or OpenEBS on a node with 9.5GB.

- **Hands-on:** install it, provision against it, delete and observe the reclaim.
- **Internals note:** it is not a CSI driver. It is a **controller that watches PVCs and creates a `hostPath` PV**, plus a helper pod that `mkdir`s on the node. Read its reconcile loop — perhaps 300 lines — and compare it to your CSI driver. The comparison is the lesson: two legitimate answers to the same problem, one inside the CSI contract and one outside it, with different trade-offs in portability and privilege.
- **CNCF maturity:** not a CNCF project — a vendor-maintained component of k3s. Worth naming explicitly: it is production-used at scale *for its niche* (single-node, node-local storage) and inappropriate outside it, which is a cleaner example of "fit for purpose beats maturity tier" than anything in the graduated list.

---

<a id="cka-block"></a>
## 7. ⏱ CKA drill block — 1–2 weeks

> **This section is a different activity from everything above.** Everything above optimises for understanding; this optimises for **speed and correctness under a clock**. Do not blend them. Do not read source during this block. When it ends, it ends.

Domain weights, exam mechanics, the practice-resource verdicts, the currency test and the speed tactics all live in the [certs strand](../strands/certs.md#cka) and are not restated here. What follows is only what is specific to *this* phase's relationship with the exam.

**Why the checkpoint is here:** CKA's domains span P3 (Cluster Architecture), P5 (Workloads & Scheduling), P7 (Services & Networking) and P8 (Storage) — this is the first phase where all of it is covered.

**What this phase contributed to the exam.** A rare genuine alignment, worth noticing: CKA **v1.32 moved Storage from "understand" to "implement"** and added *"Understand extension interfaces (CNI, CSI, CRI, etc.)"* — see [Recent changes (CKA)](../strands/certs.md#cka-changes). So the CSI driver in §3 is not just internals indulgence: it services a listed competency, and you will be the rare candidate who has written one.

**What NOT to drill, despite every older course insisting:** **etcd backup and restore was removed from the CKA curriculum entirely in v1.32.** P2's etcd month was internals work and is *not* billed as exam prep — which is a [standing rule of the certs strand](../strands/certs.md), not a note about this phase.

**Drill focus, weighted to the exam rather than to this phase:** troubleshooting above all, then cluster architecture and networking. **Storage is the smallest of the four** — resist the temptation to over-drill what you have just spent a month on. Weights and the drill list: [Speed tactics](../strands/certs.md#speed-tactics), [Practice resources](../strands/certs.md#practice).

**The harness** — clock, task list, pass mark and scoring rule: [The CKA drill block](../labs/08/20-cka-drill-block.md). It drills [this phase's own checklist](#checklist) and adds nothing to it.

**Exit:** CKA passed. If it is not passed, that is a drill-block problem, not a phase problem — the gate below is independent of it.

---

<a id="capstone"></a>
## 8. Capstone

**Corpus trace #3 — a PVC gets bound and mounted — traced end to end, in writing, with citations.**

PVC created → `pv_controller.syncClaim` (or delayed by the `volumebinding` plugin) → `csi-provisioner` calls `CreateVolume` → attach/detach controller → `VolumeAttachment` → kubelet volume manager → `NodeStageVolume` → `NodePublishVolume`.

Requirements:
1. **Every hop names the component that performs it and cites a `file:line` in current source.** Not a package — a line. If you cannot cite it, you do not yet know it, which is the entire point of this format.
2. **Do it twice**: once for `Immediate` binding and once for `WaitForFirstConsumer`, and mark exactly where the two traces diverge and rejoin.
3. **Use your own driver** for one of the two runs, so at least one `CreateVolume` in the trace is code you wrote.
4. **Attach the evidence**: the `findmnt` output, the `VolumeAttachment` object, and the arrow diagram from [the mount trace](../labs/08/07-volume-to-mount-trace.md).

**Plus:** `csi-sanity` passing clean against your driver, output included.

---

<a id="checklist"></a>
## 9. Checklist

Concrete demonstrable outputs. No item says *understand* or *know*; each is either an artifact, a timed production, or a falsifiable claim.

**Produce from a blank cluster, under time:**
- [ ] A StorageClass with dynamic provisioning, a PVC, and a pod consuming it — **under 4 minutes**, from memory, no docs.
- [ ] Diagnose a `Pending` PVC and state the cause from `describe` output alone — **under 90 seconds** — across all four causes you induced: no matching PV, no provisioner, `WaitForFirstConsumer` with an unschedulable pod, and exhausted capacity.
- [ ] Recover a PVC stuck in `Terminating` **without stripping the finalizer**.

**Produce as a written artifact:**
- [ ] The completed capstone trace, both variants, every hop cited to `file:line`.
- [ ] The PVC-to-`mount`-line arrow diagram from [the mount trace](../labs/08/07-volume-to-mount-trace.md), drawn from memory in under 5 minutes.
- [ ] A one-paragraph explanation of the zone-mismatch failure that `WaitForFirstConsumer` prevents, written to be understood by someone who has not done this phase.
- [ ] Your five bind predictions from [the bind predictions](../labs/08/01-predict-the-bind.md), with outcomes — including at least one you got wrong and why.

**Objective harness:**
- [ ] `csi-sanity` passes clean against your driver. Output committed.

**Falsifiable claims — write the answer, then verify against source:**
- [ ] Which flag governs how long a stuck detach takes to resolve, and its default.
- [ ] Which phase of expansion sets `FileSystemResizePending`, and which clears it.
- [ ] Which four scheduler extension points `volumebinding` implements, and what each does.
- [ ] Why `mountPropagation: Bidirectional` is required on a CSI node DaemonSet.
- [ ] What in `pkg/volume/` is dead code, and why it has not been deleted.

**Cert:**
- [ ] CKA passed.

---

<a id="gate"></a>
## 10. Gate

You may advance to [P9](09-service-mesh.md) when:

1. **`csi-sanity` passes.** Objective, non-negotiable, no judgement required.
2. **The capstone trace is complete with real citations.** The standard is that a hostile reader with the source open could check every line and find you right. "I understand the binding flow" is unfalsifiable; "`syncClaim` calls `findBestMatchForClaim` at `pv_controller.go:NNN`" is either true or it is not.
3. **No chaos drill remains mysterious.** Specifically 8.C4: if you cannot explain the delay between node loss and volume reattachment, and name the flag that governs it, **stay in this phase.** A red drill is the one condition permitted to extend a phase without renegotiating the schedule.

The CKA result is deliberately **not** a gate condition. It is a milestone in a different track, and a phase that produces a working CSI driver and a cited trace has succeeded regardless of what a 2-hour exam says.
