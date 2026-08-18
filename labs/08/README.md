# Labs — Phase 8, Storage

Twenty exercises in the order they are meant to run. Each states one claim to test or
one artifact to produce, links its [topology](../../strands/lab-topologies.md) rather
than restating a footprint, and ends with a teardown line — which is usually a
*continuity marker*, because [teardown is ruled per
phase](../../strands/lab-topologies.md#teardown) and a provision costs minutes before
any teaching happens.

The framing — why each module exists, what to read and the question to answer from it —
stays in [`phases/08-storage.md`](../../phases/08-storage.md). These files hold only what
you type and what you should see.

| # | Exercise | Why it exists |
|---|---|---|
| 1 | [Predict which PV a PVC will bind to](01-predict-the-bind.md) | Turns `findBestMatchForClaim` from a function you read into a prediction you can be wrong about. |
| 2 | [A released PV does not return to the pool](02-released-not-available.md) | The reclaim policy is the only thing standing between a namespace delete and lost data. |
| 3 | [Binding is reconciled state, not a transaction](03-rewrite-a-claimref.md) | Breaks the bind from both sides to show there is no atomic moment in it. |
| 4 | [Delayed binding, observed delaying something](04-delayed-binding-observed.md) | `WaitForFirstConsumer` is invisible until you watch a PVC wait for a pod that does not exist. |
| 5 | [Build the failure that delayed binding prevents](05-zone-mismatch-by-construction.md) | The design is only convincing once you have constructed the incident it exists to stop. |
| 6 | [Four ways a PVC stays Pending, diagnosed in 90s](06-four-ways-a-pvc-stays-pending.md) | The phase's most reusable reflex, and the one where the cause is often not storage. |
| 7 | [Follow one volume down to a mount line](07-volume-to-mount-trace.md) | Produces the arrow diagram the capstone and the checklist both require. |
| 8 | [Unmount a volume under a running pod](08-umount-under-a-running-pod.md) | Makes `mountPropagation: Bidirectional` something you have felt rather than copied. |
| 9 | [Expansion is two phases, and you can get stuck](09-expansion-two-phase.md) | KEP-1790 recovery is the instructive half; the happy path is the setup for it. |
| 10 | [Snapshot, destroy the source, restore](10-snapshot-and-restore.md) | The PV/PVC two-object pattern, repeated out of tree, so the pattern is visibly a pattern. |
| 11 | [A PVC that will not delete, cleared correctly](11-finalizer-deadlock.md) | Does the wrong fix deliberately, then goes and finds the orphan it created. |
| 12 | [A CSI driver passing `csi-sanity`, no cluster](12-csi-driver-sanity.md) | The only fully objective gate in the curriculum outside the exams — and it needs no topology at all. |
| 13 | [Deploy the driver with its sidecars](13-csi-driver-in-cluster.md) | Where the sidecar architecture stops being a diagram: your binary never watches the API. |
| 14 | [8.C1 — a slow disk under a live workload](14-chaos-slow-disk.md) | A pod that is `Running`, `Ready` and useless at the same time. |
| 15 | [8.C2 — I/O errors on a fraction of calls](15-chaos-io-errors.md) | Partial failure, which the API surface reports as nothing at all. |
| 16 | [8.C3 — make your own driver refuse to unstage](16-chaos-detach-failure.md) | No chaos tool can express this; the fault is a flag you add to your own code. |
| 17 | [8.C5 — fill the disk](17-chaos-disk-fill.md) | Disk-pressure eviction is ranked and graceful; memory pressure is neither. |
| 18 | [8.C6 — restart the kubelet with mounts held](18-chaos-kubelet-restart.md) | What reconstruction recovers, and the gap KEP-3756 exists to close. |
| 19 | [8.C4 — lose a node with a volume attached](19-chaos-node-loss.md) | The gate names this one. Manual `qm stop`, and the answer is not the one the drill originally expected. |
| 20 | [The CKA drill block, as a timed harness](20-cka-drill-block.md) | A different activity with a different success condition: a clock, not a mechanism. |

**One cluster runs 8.1 through 8.18.** [`pair`](../../strands/lab-topologies.md#pair) comes
up once at 8.1 and is destroyed by 8.19, which ends the phase's cluster on purpose. 8.12
needs no topology — it runs on [`forge`](../../strands/lab-topologies.md#build-guest)
alone — and 8.20 wants a **fresh** `pair` it did not build.

Two things arrive mid-chain and are worth provisioning attention: **Chaos Mesh** at 8.14
([minimised install, 582Mi](../../strands/chaos.md#install), installed once and left up),
and **`external-snapshotter`** at 8.10, which is a controller the phase's original
costing did not include.
