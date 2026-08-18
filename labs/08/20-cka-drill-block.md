<a id="cka-drill-block"></a>
# The CKA drill block, as a timed harness

**Artifact** — a repeatable timed session, run until every task lands inside its clock twice in a row on a cluster you did not prepare.

**This is a different activity from every exercise above it.** Everything above optimises for mechanism; this optimises for speed and correctness under a clock. Do not blend them, and **do not read source during this block** — [the phase's framing says why](../../phases/08-storage.md#cka-block).

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), freshly provisioned, and **not** the cluster from [8.C4](19-chaos-node-loss.md) — a drill against a cluster you built is a drill against your own memory of it. Two nodes rather than [`solo`](../../strands/lab-topologies.md#solo): CKA weights troubleshooting and cluster architecture heavily, and a single node cannot drill cordon, drain or a node that has stopped reporting.

**The harness**

| | |
|---|---|
| **Clock** | Per task, below. Start it before reading the task, as the exam does. |
| **Docs** | Only what [the tab policy](../../strands/certs.md#tab-policy) permits. Nothing else open. |
| **Environment** | A cluster you did not prepare, with a context set to the wrong namespace. |
| **Pass mark** | Every task inside its clock, **twice in consecutive sessions.** One clean run is luck. |
| **Scoring** | Binary per task. A task that needed a second look did not pass, even if the object is right. |

**The task list** — the timed items are [the phase's own checklist](../../phases/08-storage.md#checklist), not a new set:

1. StorageClass with dynamic provisioning + PVC + pod consuming it — **4 minutes**, from memory.
2. Diagnose a `Pending` PVC from `describe` alone — **90 seconds** — for each of the four causes drilled in [the Pending drill](06-four-ways-a-pvc-stays-pending.md).
3. Recover a PVC stuck in `Terminating` without stripping the finalizer — **3 minutes**, per [the finalizer deadlock](11-finalizer-deadlock.md).
4. Then leave storage alone. **It is the smallest of CKA's four relevant domains** and you have just spent a month on it; the weighting and the drill list are in [speed tactics](../../strands/certs.md#speed-tactics) and [practice resources](../../strands/certs.md#practice).

**Expect** — task 1 is the one that fails first, and it fails on typing speed rather than on recall. That is the point of the clock. Everything about weights, exam mechanics, the currency test and the vouchers lives in [the certs strand](../../strands/certs.md#cka) and is not repeated here.

**Write down** — per session, which tasks passed and the wall-clock for each. The trend is the signal, not any single run.

**Teardown** — `just tofu labs destroy` when the block ends. The exam result is [deliberately not a gate condition](../../phases/08-storage.md#gate).
