<a id="the-incident-note"></a>
# The one-page incident note

**Artifact** — one page that describes the wedged rollout. Write it so that another person can reproduce your diagnosis without asking you a question. **This is [the capstone's second half](../../phases/01-operate-shallow.md#capstone) and [a gate condition](../../phases/01-operate-shallow.md#gate).** It is also the format that [P6](../../phases/06-kubelet-node.md), [P8](../../phases/08-storage.md) and [P11](../../phases/11-synthesis.md) escalate.

**Rests on** — [the 1.C3 transcript](22-botch-a-rollout-and-roll-back.md). Write from the transcript, and not from memory. The difference shows on the page.

**Topology** — **none** for the writing itself. This is desk work, and you can do it anywhere. But this exercise ends the phase's cluster, so run it while [`pair`](../../strands/lab-topologies.md#pair) is still up and you can go back to check a claim.

**Do** — write four sections, in this order. The order is the point.

1. **Symptom.** Say what a person would have noticed, from outside, before any diagnosis. If your symptom sentence contains the word *ReplicaSet*, then you have written a conclusion, and not a symptom. Include what was *not* wrong: the service stayed up, and no request failed.
2. **The objects that you inspected, in order, with what each one told you.** Write four or five lines. Each line is one command and the one fact that it contributed. Keep a step that contributed nothing. A diagnosis is a search, and the dead ends are the honest part.
3. **The mechanism.** Answer four things here. Why did the rollout stop instead of failing? Why did the old ReplicaSet still exist to roll back to? Which field capped the blast radius? What would the number have been at `maxUnavailable: 2`? You measured that last number, so use the measurement. Also name the controller, and name the two values that it compared.
4. **The fix, and the risk of the fix.** Say what `rollout undo` actually did, and to which object. Then say what it did *not* do: the broken image is still the image in your registry, in your chart, and in the next `helm upgrade`.

**Constraints**

- **One page.** If the note runs long, then the mechanism section is doing work that belongs in section 2.
- **No `file:line` citations.** [The phase stays deliberately above the source](../../phases/01-operate-shallow.md#capstone). The trace runs through objects and controllers. That standard returns in [P2](../../phases/02-etcd.md).
- **Reproducible.** A reader must be able to follow section 2 on their own cluster, and see what you saw. Include the manifest that broke it.

**Expect** — section 3 is where the note either earns the page or does not. One sentence defeats most people on the first attempt: the sentence that explains why the old ReplicaSet was still there. It was not kept *for* the rollback. It was kept because [`revisionHistoryLimit`](08-rolling-update-predictions.md) had not yet trimmed it, and rollback is possible as a consequence. Getting that causality the right way round is the difference between a note that explains and a note that narrates.

**Write down** — the note itself, committed. It is the artifact.

**Teardown** — **the topology goes.** Run `helm uninstall app`, then [destroy it](../../strands/lab-topologies.md#teardown). Check two things before you do. First, [the kubeadm map](02-what-kubeadm-generated.md) is written and committed, because P3 reads the map and not the guest. Second, the chart is committed, because [the checklist](../../phases/01-operate-shallow.md#checklist) asks for the chart rather than for a running release. Everything after this point in the phase — [the Go primer](25-the-go-primer-program.md) and [the CKAD block](26-ckad-drill-block.md) — either needs no cluster or wants a fresh one.
