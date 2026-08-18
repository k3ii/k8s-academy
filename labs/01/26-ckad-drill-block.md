<a id="ckad-drill-block"></a>
# The CKAD drill block, as a timed harness

**Artifact** — a repeatable timed session, run until every task lands inside its clock twice in a row on a cluster you did not prepare.

**This is a different activity from every exercise above it.** Everything above optimises for referents and fluency; this optimises for speed and correctness under a clock. Do not blend them, and **do not read source during this block** — [the phase's framing says why](../../phases/01-operate-shallow.md#ckad-block).

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), **freshly provisioned** and not the cluster you spent three weeks on — that one is gone by [the incident note](24-the-incident-note.md), and deliberately: a drill against a cluster you built is a drill against your own memory of it. Two nodes rather than [`solo`](../../strands/lab-topologies.md#solo) because [the exposure tasks](14-four-ways-to-expose.md) need a NodePort that lands somewhere you are not.

**The harness**

| | |
|---|---|
| **Clock** | Per task, below. Start it before reading the task, as the exam does. |
| **Docs** | Only what [the tab policy](../../strands/certs.md#tab-policy) permits. Nothing else open. |
| **Environment** | A cluster you did not prepare, with the context set to the wrong namespace. Set it wrong on purpose each session; the first thing every exam task needs is `-n`. |
| **Pass mark** | Every task inside its clock, **twice in consecutive sessions.** One clean run is luck. |
| **Scoring** | Binary per task. A task that needed a second look did not pass, even if the object is right. |

**The task list** — the timed items are [the phase's own checklist](../../phases/01-operate-shallow.md#checklist), not a new set:

1. A Deployment, a Service and a ConfigMap-configured app exposed via NodePort — **4 minutes**, from memory, no docs.
2. Diagnose a wedged rollout and roll it back from `kubectl` output alone — **3 minutes** — using [the triage order you wrote](22-botch-a-rollout-and-roll-back.md), against all three break-shapes, not just the probe one.
3. A Pod with a dropped-and-re-added capability and `runAsNonRoot`, proven with `capsh` inside — **3 minutes**, per [the capability exercise](11-drop-a-capability-in-a-manifest.md).
4. **What not to drill is as timed as what to drill**: [the phase says which topics are wasted effort](../../phases/01-operate-shallow.md#ckad-block), and the weights, mechanics and practice-resource verdicts are in [the certs strand](../../strands/certs.md#ckad). Neither is repeated here. The drill list and the tactics: [speed tactics](../../strands/certs.md#speed-tactics), [practice resources](../../strands/certs.md#practice).

**Expect** — task 1 fails first and it fails on typing, not on recall: `kubectl create deploy --image=... --dry-run=client -o yaml` and an editor beats writing YAML by hand every time, and finding that out under a clock is the point of the clock. Task 2 is the one that improves most between sessions, because the triage order is a list you own rather than a fact you remember.

**Write down** — per session, which tasks passed and the wall-clock for each. The trend is the signal, not any single run.

**Teardown** — `just tofu labs destroy` when the block ends. **This ends P1's cluster for good**; [P2](../../phases/02-etcd.md) provisions [`etcd-only`](../../strands/lab-topologies.md#etcd-only) and needs the RAM. The exam result is [deliberately not a gate condition](../../phases/01-operate-shallow.md#gate).
