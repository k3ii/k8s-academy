# Phase 8 — Storage

> **3–4 weeks**, plus a **1–2 week CKA drill block** at the end.
> The range is planning information. **The gate at the bottom of this file decides when the phase is finished** — not the calendar. A phase that runs long and passes its gate has succeeded.

| | |
|---|---|
| **Prerequisites** | [P4 Controllers](04-controllers.md) — the `syncClaim`/`syncVolume` loops are unreadable without informers and workqueues. [P5 Scheduler](05-scheduler.md) — `WaitForFirstConsumer` lives *in the scheduler*, so its plugin sequence must already be familiar. [P6 kubelet](06-kubelet-node.md) — the volume manager reuses the desired/actual-state-of-world pattern. |
| **Unlocks** | The **CKA** checkpoint (this is the last phase whose material the exam covers). [P12](12-gitops-platform.md)'s platform API provisions storage, so this is where you learn what you'll be abstracting. |
| **Source area** | [Area 6 — Storage](../strands/source-reading.md#area-6-storage) |
| **Language** | Go ([#9](https://github.com/k3ii/k8s-academy/issues/9)) |
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

### Module 8.1 — The CSI contract, before any Kubernetes code (~3 days)

Read the spec *first*. The in-tree volume subsystem is sprawling, historically layered and full of dead in-tree-plugin scaffolding; the CSI spec is a clean gRPC contract, and it makes the sprawl suddenly coherent. Reading them in the other order is the single most common way to waste a week here.

**Read** — [Area 6](../strands/source-reading.md#area-6-storage) items 1–3. For each, the question to answer *from the source*, not from a blog:

| Read | Answer from it |
|---|---|
| `container-storage-interface/spec/spec.md` + `csi.proto` | Which of the three services (Identity / Controller / Node) must a driver implement to be minimally useful, and which are optional? Which calls **must** be idempotent, and where does the spec say so? |
| `design-proposals-archive/storage/persistent-storage.md` | Why is storage **two objects** rather than one? Write the answer in terms of who owns each — this is the whole PV/PVC design in one sentence. |
| `design-proposals-archive/storage/volume-provisioning.md` | What problem does `StorageClass` solve that a PV template would not? |

**No lab.** This module is reading, and it is the highest-leverage three days in the phase.

---

### Module 8.2 — PV/PVC binding, by hand (~4 days)

**Read** — Area 6 item 4, `pkg/controller/volume/persistentvolume/index.go` (6.8 KB). Small, self-contained, and the single most useful storage file for a beginner.

> **Question to answer from the source:** `findBestMatchForClaim` walks candidate PVs. In what order, and what is the tie-break when two PVs both satisfy the claim? Cite the line.

Then Area 6 items 8 and 9 — `pv_controller_base.go` (the skeleton: informers, two sync loops, resync) **before** `pv_controller.go`. The big one is 92.8 KB and is **reference-only as a whole**; read exactly four functions: `syncClaim`, `syncVolume`, `bind`, `provisionClaim`.

#### Lab 8.2 — Predict the bind

**Goal** — bind PVCs to PVs by reasoning rather than by trial, and be right before you apply.

**Topology** — `pair` (control plane 3072MB / 2c / 25G at `10.10.10.130`; worker 2048MB / 2c / 20G at `10.10.10.131`). 5.0GB, 45G disk. Everything from Phase 7 torn down first — this is a hard precondition, not hygiene.

**Provision**
```
cd tofu/labs && tofu apply -var 'topology=pair'
ssh -J factory debian@10.10.10.130
```

**Do**
1. Create six `hostPath` PVs that differ deliberately: two at 5Gi and two at 10Gi; one `ReadWriteOnce` and one `ReadWriteMany` at each size; one with a `storageClassName` and one without; one with a label.
2. **Before applying any PVC, write down which PV you expect it to bind to and why.** Then apply and check. Do this for at least five PVCs, including a 7Gi `ReadWriteOnce` claim (which PV, and how much capacity is wasted?), and a claim with a `selector`.
3. Get one wrong on purpose: write a claim you believe cannot bind, and confirm it sits `Pending` with the reason you predicted.
4. Delete a bound PVC and watch the PV go `Released` rather than `Available`. Explain why it does not return to the pool, then make it do so.

**Observe**
```
kubectl get pv,pvc -o wide --watch
kubectl -n kube-system logs -l component=kube-controller-manager --tail=200 | grep -i 'volume\|claim'
kubectl get pv <name> -o jsonpath='{.spec.claimRef}' | jq
```
The bidirectional binding is the thing to see: `pv.spec.claimRef` and `pvc.spec.volumeName` both get written, and by different code paths.

**Break it** — bind a PVC, then edit the PV's `claimRef` to point at a different PVC. Watch what the controller does about it. This is the fastest way to internalise that binding is *reconciled state*, not a transaction.

**Write down** — your five predictions with the outcome of each, and one paragraph on the capacity waste in step 2: the PV/PVC model has no partial fulfilment, and that has consequences for how you size a StorageClass.

---

### Module 8.3 — Delayed binding, and why it lives in the scheduler (~3 days)

The conceptual centre of the phase, and the place where P5 pays off.

**Read** — Area 6 item 11, `design-proposals-archive/storage/volume-topology-scheduling.md`, **before** any code. The corpus is explicit that item 12's code is "nearly unreadable without it." Then item 12, `pkg/scheduler/framework/plugins/volumebinding/volume_binding.go`.

> **Path note, and a live example of [source archaeology](../strands/source-archaeology.md#stale-paths) from P2:** this moved from `pkg/controller/volume/scheduling/`, which **no longer exists**. Any material citing that path is stale. Before reading the plugin, do [archaeology drill 1](../strands/source-archaeology.md#drills) — find the commit that deleted the old path and read its PR. The move *is* the lesson: the decision has to be made where the node is chosen.

> **Question to answer from the source:** `volume_binding.go` implements `PreFilter`, `Filter`, `Reserve` and `PreBind`. What does each one do about volumes, and why does the work have to be split across four extension points rather than done in one?

Then item 13's `assume_cache.go` — how the scheduler acts on binds that are not yet persisted.

#### Lab 8.3 — Immediate versus delayed, observed

**Goal** — see delayed binding actually delay something, and see the failure it prevents.

**Topology** — `pair`, continued from 8.2.

**Do**
1. Create two StorageClasses over `local-path`: one `volumeBindingMode: Immediate`, one `WaitForFirstConsumer`.
2. Create a PVC against each, with **no pod**. Observe: one binds immediately, one stays `Pending` with `WaitForFirstConsumer` in its events. Nothing is broken — this is the design.
3. Create a pod for each PVC. Watch the second bind *at scheduling time*.
4. Now construct the failure the design prevents. Label your two nodes as distinct topology domains, add `allowedTopologies` to the `Immediate` class, and force a situation where the volume lands on node A and the pod cannot run there. Then repeat with `WaitForFirstConsumer` and show it does not happen.

**Observe**
```
kubectl get events --sort-by=.lastTimestamp -w
kubectl -n kube-system logs -l component=kube-scheduler --tail=300 | grep -i volumebinding
kubectl get pvc -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.phase}{"\t"}{.spec.volumeName}{"\n"}{end}'
```

**Break it** — with `WaitForFirstConsumer`, create a pod whose node affinity is unsatisfiable. The PVC now stays `Pending` forever because binding waits for a scheduling decision that will never come. Diagnose this from `kubectl describe pvc` and `describe pod` alone, then write down how you would recognise it in a cluster you did not build.

**Write down** — the four-extension-point split from the reading question, and a description of the zone-mismatch failure in your own words. This one is a common production incident; the note is worth keeping.

---

### Module 8.4 — The node side: attach, stage, publish (~4 days)

**Read** — Area 6 items 15, 16, 18:
- `attachdetach/attach_detach_controller.go` + `reconciler/` — learn the DSW/ASW pattern **here**, where it is smaller, because the kubelet volume manager reuses it.
- `pkg/kubelet/volumemanager/` — the node-side half, including `populator/` turning the pod list into desired state.
- `pkg/volume/csi/csi_client.go` **first** of that group — it maps one-to-one onto the RPCs from module 8.1, which makes it the easiest bridge between spec and implementation in the whole area.

> **Question to answer from the source:** find where `--attach-detach-reconcile-sync-period` is consumed. What happens to a *stuck* detach as that period elapses, and what does that imply about how long a node failure takes to release a volume?

Also read Area 6 item 23, **KEP-625 (in-tree to CSI migration)** — not for the migration itself, but to know **what to ignore in `pkg/volume/`**. Without this you will waste days on dead plugin scaffolding.

#### Lab 8.4 — Follow one volume down to the mount

**Goal** — connect every layer read so far to a single `mount` line on a node.

**Do**
1. Deploy a pod with a dynamically-provisioned PVC.
2. On the worker node, find the volume: `findmnt | grep kubelet`, then locate both the *staging* path (`/var/lib/kubelet/plugins/kubernetes.io/csi/.../globalmount`) and the *publish* path (`/var/lib/kubelet/pods/<uid>/volumes/...`).
3. **Explain the relationship between those two paths out loud** before reading on. This is `NodeStageVolume` versus `NodePublishVolume` made physical: one mount per node, bind-mounted once per pod.
4. Scale the workload to two pods on the same node with a `ReadWriteMany` volume. Watch a second publish path appear against the *same* staging path.
5. `nsenter` into the container's mount namespace and confirm what the container sees.

**Observe**
```
findmnt -R /var/lib/kubelet | grep -A2 csi
kubectl get volumeattachment -o wide
journalctl -u kubelet -f | grep -i 'volume\|mount'
```

**Break it** — `umount` the publish path from under a running pod. What does the pod see? What does the kubelet do about it, and after how long? Then kill the kubelet with volumes mounted, restart it, and watch reconstruction — that is **KEP-3756** (Area 6 item 17) happening in front of you.

**Write down** — the staging/publish path pair for your volume, with an arrow diagram from PVC to `mount` line naming the component responsible for each hop. This diagram is a required input to the capstone.

---

### Module 8.5 — Expansion, snapshots, and finalizers (~3 days)

The short module, but it holds three of the most instructive failure modes in Kubernetes storage.

**Read** — Area 6 items 19/20 (expansion, and **KEP-1790: recovering from an expansion you cannot fulfil** — a wonderfully instructive failure), item 21 (**KEP-177 snapshots**: note these are **CRDs plus `external-snapshotter`, out of tree** — the same two-object pattern as PV/PVC), and item 26, `pkg/controller/volume/{pvprotection,pvcprotection}/` — tiny packages and the best concrete finalizer example in the codebase.

> **Question to answer from the source:** expansion is two-phase, controller then node. Which phase sets `FileSystemResizePending`, and which clears it? What must be true of the pod for the node phase to proceed?

#### Lab 8.5 — Three deadlocks

**Do**
1. **Expand** a PVC. Watch `FileSystemResizePending`, then watch it clear. Then request an expansion the backing store cannot satisfy and recover from it per KEP-1790.
2. **Snapshot**: install `external-snapshotter` CRDs and controller, take a `VolumeSnapshot`, delete the source PVC, restore from the snapshot. Note that you installed CRDs and a controller — you built exactly this shape in [P4](04-controllers.md).
3. **Finalizer deadlock**: create a PVC, mount it in a pod, then `kubectl delete pvc`. It hangs. Identify the finalizer, identify what is holding it, and clear it **correctly** by removing the consumer — not by stripping the finalizer, which is the internet's favourite wrong answer and leaves an orphaned volume.

**Write down** — why stripping a finalizer is the wrong fix, in terms of what the finalizer's controller was going to do and now never will.

---

## 3. Build-track artifact — a CSI driver

The phase's build component, inline per the spine. Roughly a week, running alongside modules 8.2–8.5 rather than after them.

**Reference implementations to read, not copy:** `kubernetes-csi/csi-driver-host-path` (the canonical toy) and `kubernetes-csi/external-provisioner`'s `doc/design.md` (Area 6 item 6) — the sidecar pattern of *Kubernetes controllers translating Kubernetes objects into CSI RPCs* is the architectural idea to take away.

**Build**
- All three services: **Identity** (`GetPluginInfo`, `GetPluginCapabilities`, `Probe`), **Controller** (`CreateVolume`, `DeleteVolume`, and `ControllerGetCapabilities`), **Node** (`NodeStageVolume`, `NodePublishVolume`, their unwinds, `NodeGetInfo`).
- Back it with directories on the host. The storage backend is deliberately trivial: the lesson is the **contract and the lifecycle**, not a filesystem.
- Deploy the Controller service as a Deployment with the `csi-provisioner` sidecar; deploy the Node service as a DaemonSet with the `node-driver-registrar` sidecar. Each gets [its own ServiceAccount and hand-written ClusterRole](../strands/build-mechanics.md#identity) and [a memory request taken from `kubectl top`](../strands/build-mechanics.md#sizing) — the Controller and Node services need genuinely different permissions, which makes this the artifact where separate identities are least arbitrary.
- The DaemonSet needs `hostPath` access to `/var/lib/kubelet/plugins` and **`mountPropagation: Bidirectional`**. When you find out why — you will, the hard way — write it down. That single field is the phase's best lesson about mount namespaces, and it connects directly to [P0](00-linux-primitives.md).

**Ship it** — built on [`forge`](../strands/build-mechanics.md#forge), a static binary in a [`scratch` image](../strands/build-mechanics.md#base-image), pushed to `forge`'s registry and pulled by the nodes. Both halves of the [two-stage rule](../strands/build-mechanics.md#two-stages) apply here: stage 1 is `csi-sanity` over a UNIX socket with no Kubernetes present at all, and only then do the sidecars arrive. Note that a `scratch` image has no shell — `kubectl exec` into the DaemonSet will fail, and the way in is `kubectl debug --target=`.

**The objective gate**
```
csi-sanity --csi.endpoint=/tmp/csi.sock
```
`csi-sanity` (from `kubernetes-csi/csi-test`) is **the only fully objective gate in this curriculum outside the three exams.** It either passes or it does not, and it will find idempotency bugs you would never have found by hand — which is exactly why module 8.1 asked you to locate the spec's idempotency requirements.

> **Scope discipline:** no snapshots, no expansion, no topology in your driver. Those are read about in 8.5, not implemented. A driver that passes `csi-sanity` for the basic lifecycle is the goal; a driver that grows features is a month you did not budget.

---

## 4. Chaos drills

Storage failures are slow, which makes them a different diagnostic skill from the fast failures of earlier phases — the symptom often appears minutes after the cause. All drills use **Chaos Mesh** (introduced in [P6](06-kubelet-node.md), 582Mi minimised) except where noted; the mechanism behind each action is in the [chaos catalogue](../strands/chaos.md#catalogue), and [the principle](../strands/chaos.md#principle) still holds — by hand first, scripted second.

| # | Drill | Mechanism | What you must be able to say afterwards |
|---|---|---|---|
| 8.C1 | **Slow disk under a workload** | `IOChaos` — `latency` action against the volume's mount path | Which layer surfaced the symptom first, and why a pod can be `Running` and useless simultaneously |
| 8.C2 | **I/O errors** | `IOChaos` — `fault` action, injecting `EIO` on a percentage of calls | What the application saw versus what the kubelet reported. Partial failure is harder than total failure |
| 8.C3 | **Volume detach failure** | Manual: make your own driver return an error from `NodeUnstageVolume` | Where the retry loop lives, its period, and what the `VolumeAttachment` looks like while stuck |
| 8.C4 | **Node loss with a volume attached** | `qm stop` on Proxmox — genuinely manual, because [Chaos Mesh has no native node-failure kind](../strands/chaos.md#cannot-express) and Litmus's substitute wants an SSH private key in a Secret | How long until the volume is released and reattached elsewhere, and which flag governs that. This is drill 8.C4 *and* the answer to module 8.4's reading question |
| 8.C5 | **Disk fill** | `chaosd disk-fill` on the host, or `StressChaos` | The eviction path for disk pressure versus memory pressure — connects to P6 |
| 8.C6 | **Kubelet restart with mounts held** | `systemctl restart kubelet` | What reconstruction recovers and what it cannot (KEP-3756) |

**8.C4 is the one to spend real time on.** It is the storage failure most likely to be encountered in production, it has a genuinely surprising duration, and it cannot be scripted — which is the point.

---

## 5. Talks

Slotted where they reinforce this phase. Full entries, with exact runtimes, under [Storage](../strands/talks.md#storage) in the talk index.

- **Container Storage Interface: Present and Future** — the CSI architecture from the people who designed it. Watch after module 8.1, so the spec is fresh.
- **Kubernetes Storage Lingo 101** — worth it only if the PV/PVC/SC/VolumeAttachment vocabulary is still slippery after 8.2. Skip if not.
- Re-watch, from P6: **Evicted! All the Ways Kubernetes Kills Your Pods** — the disk-pressure section means something different now.

---

## 6. Ecosystem

One light rock this phase, deliberately — the build artifact is the heavy item.

**`local-path-provisioner`** (Rancher) — the provisioner that k0s and k3s ship. Tiny footprint, which is why it is here rather than Longhorn or OpenEBS on a node with 9.5GB.

- **Hands-on:** install it, provision against it, delete and observe the reclaim.
- **Internals note:** it is not a CSI driver. It is a **controller that watches PVCs and creates a `hostPath` PV**, plus a helper pod that `mkdir`s on the node. Read its reconcile loop — perhaps 300 lines — and compare it to your CSI driver. The comparison is the lesson: two legitimate answers to the same problem, one inside the CSI contract and one outside it, with different trade-offs in portability and privilege.
- **CNCF maturity:** not a CNCF project — a vendor-maintained component of k3s. Worth naming explicitly: it is production-used at scale *for its niche* (single-node, node-local storage) and inappropriate outside it, which is a cleaner example of "fit for purpose beats maturity tier" than anything in the graduated list.

---

## 7. ⏱ CKA drill block — 1–2 weeks

> **This section is a different activity from everything above.** Everything above optimises for understanding; this optimises for **speed and correctness under a clock**. Do not blend them. Do not read source during this block. When it ends, it ends.

Domain weights, exam mechanics, the practice-resource verdicts, the currency test and the speed tactics all live in the [certs strand](../strands/certs.md#cka) and are not restated here. What follows is only what is specific to *this* phase's relationship with the exam.

**Why the checkpoint is here:** CKA's domains span P3 (Cluster Architecture), P5 (Workloads & Scheduling), P7 (Services & Networking) and P8 (Storage) — this is the first phase where all of it is covered.

**What this phase contributed to the exam.** A rare genuine alignment, worth noticing: CKA **v1.32 moved Storage from "understand" to "implement"** and added *"Understand extension interfaces (CNI, CSI, CRI, etc.)"* — see [Recent changes (CKA)](../strands/certs.md#cka-changes). So the CSI driver in §3 is not just internals indulgence: it services a listed competency, and you will be the rare candidate who has written one.

**What NOT to drill, despite every older course insisting:** **etcd backup and restore was removed from the CKA curriculum entirely in v1.32.** P2's etcd month was internals work and is *not* billed as exam prep — which is a [standing rule of the certs strand](../strands/certs.md), not a note about this phase.

**Drill focus, weighted to the exam rather than to this phase:** troubleshooting above all, then cluster architecture and networking. **Storage is the smallest of the four** — resist the temptation to over-drill what you have just spent a month on. Weights and the drill list: [Speed tactics](../strands/certs.md#speed-tactics), [Practice resources](../strands/certs.md#practice).

**Exit:** CKA passed. If it is not passed, that is a drill-block problem, not a phase problem — the gate below is independent of it.

---

## 8. Capstone

**Corpus trace #3 — a PVC gets bound and mounted — traced end to end, in writing, with citations.**

PVC created → `pv_controller.syncClaim` (or delayed by the `volumebinding` plugin) → `csi-provisioner` calls `CreateVolume` → attach/detach controller → `VolumeAttachment` → kubelet volume manager → `NodeStageVolume` → `NodePublishVolume`.

Requirements:
1. **Every hop names the component that performs it and cites a `file:line` in current source.** Not a package — a line. If you cannot cite it, you do not yet know it, which is the entire point of this format.
2. **Do it twice**: once for `Immediate` binding and once for `WaitForFirstConsumer`, and mark exactly where the two traces diverge and rejoin.
3. **Use your own driver** for one of the two runs, so at least one `CreateVolume` in the trace is code you wrote.
4. **Attach the evidence**: the `findmnt` output, the `VolumeAttachment` object, and the arrow diagram from lab 8.4.

**Plus:** `csi-sanity` passing clean against your driver, output included.

---

## 9. Checklist

Concrete demonstrable outputs. No item says *understand* or *know*; each is either an artifact, a timed production, or a falsifiable claim.

**Produce from a blank cluster, under time:**
- [ ] A StorageClass with dynamic provisioning, a PVC, and a pod consuming it — **under 4 minutes**, from memory, no docs.
- [ ] Diagnose a `Pending` PVC and state the cause from `describe` output alone — **under 90 seconds** — across all four causes you induced: no matching PV, no provisioner, `WaitForFirstConsumer` with an unschedulable pod, and exhausted capacity.
- [ ] Recover a PVC stuck in `Terminating` **without stripping the finalizer**.

**Produce as a written artifact:**
- [ ] The completed capstone trace, both variants, every hop cited to `file:line`.
- [ ] The PVC-to-`mount`-line arrow diagram from lab 8.4, drawn from memory in under 5 minutes.
- [ ] A one-paragraph explanation of the zone-mismatch failure that `WaitForFirstConsumer` prevents, written to be understood by someone who has not done this phase.
- [ ] Your five bind predictions from lab 8.2, with outcomes — including at least one you got wrong and why.

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

## 10. Gate

You may advance to [P9](09-service-mesh.md) when:

1. **`csi-sanity` passes.** Objective, non-negotiable, no judgement required.
2. **The capstone trace is complete with real citations.** The standard is that a hostile reader with the source open could check every line and find you right. "I understand the binding flow" is unfalsifiable; "`syncClaim` calls `findBestMatchForClaim` at `pv_controller.go:NNN`" is either true or it is not.
3. **No chaos drill remains mysterious.** Specifically 8.C4: if you cannot explain the delay between node loss and volume reattachment, and name the flag that governs it, **stay in this phase.** A red drill is the one condition permitted to extend a phase without renegotiating the schedule.

The CKA result is deliberately **not** a gate condition. It is a milestone in a different track, and a phase that produces a working CSI driver and a cited trace has succeeded regardless of what a 2-hour exam says.
