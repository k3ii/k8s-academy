<a id="ckad-drill-block"></a>
# The CKAD drill block, as a timed harness

**Artifact** — a repeatable timed session. Run it until every task lands inside its clock twice in a row, on a cluster that you did not prepare.

**This is a different activity from every exercise above it.** Everything above optimises for referents and fluency. This block optimises for speed and correctness under a clock. Do not blend the two. **Do not read source during this block** — [the phase's framing says why](../../phases/01-operate-shallow.md#ckad-block).

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), **freshly provisioned**. It is not the cluster that you spent three weeks on. That cluster is gone by [the incident note](24-the-incident-note.md), and it is gone deliberately: a drill against a cluster that you built is a drill against your own memory of it. Use two nodes rather than [`solo`](../../strands/lab-topologies.md#solo), because [the exposure tasks](14-four-ways-to-expose.md) need a NodePort that lands somewhere you are not.

**The harness**

| | |
|---|---|
| **Clock** | Per task, below. Start it before you read the task, as the exam does. |
| **Docs** | Only what [the tab policy](../../strands/certs.md#tab-policy) permits. Nothing else open. |
| **Environment** | A cluster you did not prepare, with the context set to the wrong namespace. Set it wrong on purpose each session. The first thing that every exam task needs is `-n`. |
| **Pass mark** | Every task inside its clock, **twice in consecutive sessions.** One clean run is luck. |
| **Scoring** | Binary per task. A task that needed a second look did not pass, even if the object is right. |

**The task list** — the timed items are [the phase's own checklist](../../phases/01-operate-shallow.md#checklist), and not a new set.

1. A Deployment, a Service and a ConfigMap-configured app, exposed through NodePort — **4 minutes**, from memory, with no docs.
2. Diagnose a wedged rollout, and roll it back from `kubectl` output alone — **3 minutes**. Use [the triage order that you wrote](22-botch-a-rollout-and-roll-back.md). Run it against all three break-shapes, and not only against the probe one.
3. A Pod with a dropped-and-re-added capability and `runAsNonRoot`, proven with `capsh` inside the container — **3 minutes**, per [the capability exercise](11-drop-a-capability-in-a-manifest.md).
4. **What not to drill is as timed as what to drill.** [The phase says which topics are wasted effort](../../phases/01-operate-shallow.md#ckad-block). The weights, the mechanics and the practice-resource verdicts are in [the certs strand](../../strands/certs.md#ckad). Neither source is repeated here. For the drill list and the tactics, see [speed tactics](../../strands/certs.md#speed-tactics) and [practice resources](../../strands/certs.md#practice).

**Expect** — task 1 fails first, and it fails on typing rather than on recall. `kubectl create deploy --image=... --dry-run=client -o yaml` plus an editor beats writing YAML by hand every time. Finding that out under a clock is the point of the clock. Task 2 improves most between sessions, because the triage order is a list that you own, and not a fact that you remember.

**Write down** — for each session, which tasks passed, and the wall-clock time for each one. The trend is the signal, and no single run is.

**Teardown** — run `just tofu labs destroy` when the block ends. **This ends P1's cluster for good.** [P2](../../phases/02-etcd.md) provisions [`etcd-only`](../../strands/lab-topologies.md#etcd-only), and it needs the RAM. The exam result is [deliberately not a gate condition](../../phases/01-operate-shallow.md#gate).
