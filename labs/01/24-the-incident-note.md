<a id="the-incident-note"></a>
# The one-page incident note

**Artifact** — one page describing the wedged rollout, written so that another person could reproduce your diagnosis without asking you a question. **This is [the capstone's second half](../../phases/01-operate-shallow.md#capstone) and [a gate condition](../../phases/01-operate-shallow.md#gate)** — and the format [P6](../../phases/06-kubelet-node.md), [P8](../../phases/08-storage.md) and [P11](../../phases/11-synthesis.md) escalate.

**Rests on** — [the 1.C3 transcript](22-botch-a-rollout-and-roll-back.md). Write from the transcript, not from memory; the difference shows on the page.

**Topology** — **none** for the writing itself; this is desk work and can be done anywhere. But it is the exercise that ends the phase's cluster, so run it while [`pair`](../../strands/lab-topologies.md#pair) is still up and you can go back and check a claim.

**Do** — four sections, in this order, and the order is the point:

1. **Symptom.** What a person would have noticed, stated from outside, before any diagnosis. If your symptom sentence contains the word *ReplicaSet*, you have written a conclusion, not a symptom. Include what was *not* wrong: the service stayed up, no request failed.
2. **The objects you inspected, in order, with what each one told you.** Four or five lines. Each line is a command and the one fact it contributed. A step that contributed nothing stays in — a diagnosis is a search, and the dead ends are the honest part.
3. **The mechanism.** Why the rollout stopped instead of failing; why the old ReplicaSet still existed to roll back to; which field capped the blast radius and what the number would have been at `maxUnavailable: 2` — you measured that, so use the measurement. Name the controller, and name the two values it compared.
4. **The fix, and the fix's own risk.** `rollout undo`, what it actually did to which object, and the thing it did *not* do: the broken image is still the one in your registry, in your chart, and in the next `helm upgrade`.

**Constraints**

- **One page.** If it runs long, the mechanism section is doing work that belongs in section 2.
- **No `file:line` citations.** [The phase is deliberately above the source](../../phases/01-operate-shallow.md#capstone); the trace is in objects and controllers. That standard returns in [P2](../../phases/02-etcd.md).
- **Reproducible.** A reader must be able to follow section 2 on their own cluster and see what you saw. Include the manifest that broke it.

**Expect** — section 3 is where the note either earns the page or does not, and the sentence most people cannot write on the first attempt is the one explaining why the old ReplicaSet was still there. It was not kept *for* the rollback; it was kept because [`revisionHistoryLimit`](08-rolling-update-predictions.md) had not yet trimmed it, and rollback is possible as a consequence. Getting that causality the right way round is the difference between a note that explains and a note that narrates.

**Write down** — the note itself, committed. It is the artifact.

**Teardown** — **the topology goes.** `helm uninstall app`, then [destroy it](../../strands/lab-topologies.md#teardown). Two things to check before you do: [the kubeadm map](02-what-kubeadm-generated.md) is written and committed, because P3 reads the map and not the guest, and the chart is committed, because [the checklist](../../phases/01-operate-shallow.md#checklist) asks for the chart rather than for a running release. Everything after this point in the phase — [the Go primer](25-the-go-primer-program.md) and [the CKAD block](26-ckad-drill-block.md) — either needs no cluster or wants a fresh one.
