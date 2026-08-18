<a id="the-capstone-narrative"></a>
# The capstone: a measurement and a story, both with citations that survive a hostile reader

**Artifact** — [the phase's capstone](../../phases/05-scheduler.md#capstone) in two parts, written as one document: the plugin's placement measurement under contention, and one preemption narrated from the pod's arrival to its bind, with every `file:line` re-derived live at a recorded sha.

**Rests on** — everything, but three things carry it: [the contended distributions](34-placement-that-differs-measurably.md), [the drill transcript](35-5c2-preemption-with-real-victims.md), and [the queue archaeology](18-find-the-queue-yourself.md), which is what makes one of the required citations a test rather than a formality.

**Topology** — [`workhorse`](../../strands/lab-topologies.md#workhorse), for the last time. It is destroyed at the end of this exercise.

**Do**

1. **Re-derive every citation, live, at one sha.** Not from your notes — from the tree, now:

   ```sh
   ssh zain@10.10.10.125 'cd ~/src/kubernetes && git rev-parse --short HEAD'
   ```

   Then, for each of the four required citations, produce the line and its number in a single command whose output you paste:

   ```sh
   grep -n 'ScorePlugin interface' pkg/scheduler/framework/interface.go
   grep -n 'assume(\|func (sched \*Scheduler) assume\|go func()' pkg/scheduler/schedule_one.go
   grep -n 'func .*selectVictimsOnNode' pkg/scheduler/framework/plugins/defaultpreemption/default_preemption.go
   grep -rn 'movePodsToActiveOrBackoffQueue\|func (p \*PriorityQueue) Pop' pkg/scheduler/backend/queue/
   ```

   A citation to `internal/queue/` is [an automatic fail](../../phases/05-scheduler.md#capstone), and the reason it is worth failing on is that it is the one mistake a reader can check without leaving their chair.

2. **Part one — the measurement.** Write it as a claim with numbers, not a description. It needs: the workload, the two profiles, the per-node counts at both weights, the number of runs, and the sentence that would be false if the plugin did nothing. State the weight at which your plugin stops winning, because a measurement that only reports the favourable configuration is advocacy.

3. **Part two — the narrative.** One preemption, told as a sequence with timestamps, and it must answer all four of the capstone's questions in order: when the preemptor entered the unschedulable set; **which event flushed it, and which plugin's hint allowed that flush**; which node it was nominated onto and which victims were selected there and why; and the moment it reached the active queue and was bound.

   The hint question is the one people skip. Answer it from the metric labels, per [exercise 23](23-the-hint-that-decides-a-retry.md), and say explicitly whether the flush was event-driven or the periodic net.

4. **Take the gate honestly.** [Its three conditions](../../phases/05-scheduler.md#gate) are not a summary of this document; the first one in particular is about whether scheduling still feels like magic. Answer it in one paragraph naming the specific thing your 200-line scheduler skips, which by now you can say precisely rather than gesturally.

5. **Add the negative results**, because they are the phase's most defensible findings and no other section will hold them: the knob that [could not be moved on real hardware](16-the-knob-that-cannot-move-here.md) with the arithmetic that proves it, and the largest synthetic workload [`forge` could actually run](17-a-hundred-nodes-that-do-not-exist.md).

6. **Attach the diagnostic table** from [5.C3](36-5c3-a-spread-nobody-can-satisfy.md). It is the part of this document you will re-read.

**Expect** — the citation re-derivation to move at least one line number and possibly one path, if any time has passed since you first wrote them down. That is the archaeology skill working, and the document should say what moved rather than quietly using the new number.

Expect part two to be harder to write than part one, because a measurement is a table and a narrative has to be *true in order*. If your notes cannot establish whether the nomination preceded the victims' deletion, say so — a gap named is worth more than a sequence assumed, and [the drill](35-5c2-preemption-with-real-victims.md) is repeatable if you want the timestamps badly enough.

Expect the gate's first condition to be the one that decides whether the phase is finished. The honest answer names `assume` and the cache, and describes the failure you produced with your own hands in [exercise 11](11-what-assume-buys.md) rather than restating what the mechanism is for.

**Write down** — the document. It replaces the module write-downs as the phase's deliverable, and it is what [P6](../../phases/06-kubelet-node.md) starts from: the scheduler decided *where*, and the kubelet is what makes the decision real.

**Footprint note** — the writing needs no cluster; the citation re-derivation needs only `forge`. Keep `workhorse` up only while step 3 still has gaps to fill, and destroy it as soon as it does not — it is 7.0GB held for a document.

**Teardown — the phase ends, and this is the aggressive one.**

```sh
ssh zain@10.10.10.125 'cd ~/src/k8s-academy && git add -A && git commit -m "P5 capstone" && git push'
```

Then, [the standard way](../../strands/lab-topologies.md#teardown), `just tofu labs destroy`. **The topology goes.**

Confirm the phase left nothing behind, because two of these outlive a topology destroy and one of them would silently break [P6](../../phases/06-kubelet-node.md):

```sh
ssh hopper 'qm list'                                    # forge at 1536MB, nothing else running
ssh zain@10.10.10.125 'free -m; df -h /'                # the revert held, and the disk came back
curl -s http://forge.lab:5000/v2/_catalog                # both images kept, deliberately
```

Keep the images: they cost megabytes, and re-creating them costs a resize, a provision and a link. **`forge` must be at 1536MB when P6 begins** — [that was the promise made when it went up](07-fifteen-thirty-six-will-not-link-a-scheduler.md), and this is where it is kept.
