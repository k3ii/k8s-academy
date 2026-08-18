<a id="why-victim-deletion-left-the-thread"></a>
# Deleting the victims used to happen on the one thread that schedules everything

**Claim** — before KEP-4832, the scheduling cycle issued the victims' deletions and waited for them, so a single preemption of several pods stalled **every other pod's scheduling** for the duration of several API round trips; moving deletion to its own executor made preemption's cost local to the preemptor. This is [the checklist's third falsifiable claim](../../phases/05-scheduler.md#checklist) and it is provable from the code without producing the old behaviour.

**Rests on** — [the serial scheduling cycle](13-why-the-bind-is-async.md), which is the reason the old design was expensive, and [the preemption you ran](25-priority-and-the-nominated-node.md), which is the operation being moved.

**Topology** — none. Reading on [`forge`](../../strands/lab-topologies.md#build-guest); `pair` stays up.

**Do**

1. Read [KEP-4832](../../strands/source-reading.md#area-3-scheduler) for the problem statement and write down the throughput argument in your own words before looking at any code — specifically, what the cost of one preemption was in units of *other pods not being scheduled*.

2. Find the executor and read it. It is small:

   ```sh
   wc -l pkg/scheduler/framework/preemption/executor.go
   grep -n 'func \|goroutine\|go ' pkg/scheduler/framework/preemption/executor.go
   ```

3. Establish the boundary precisely: which part of preemption still runs on the scheduling thread, and which part does not. The nomination write is the pivot — say which side of the line it falls on and why it must.

4. Find the evidence in history rather than in prose:

   ```sh
   git log --oneline -8 -- pkg/scheduler/framework/preemption/
   git log -1 --format='%B' $(git log --format=%H -1 --grep='async preemption' -- pkg/scheduler/framework/preemption/)
   ```

5. Now make the claim falsifiable. Write it as a sentence a hostile reader could check, of this shape: *"in `<file>:<line>`, `<function>` does X, which means a preemption of N victims blocks the scheduling cycle for Y rather than for N API deletions."* Fill in every placeholder from the code, not from the KEP.

6. Answer the question the change raises and does not close: if deletion is asynchronous, what stops the scheduler from choosing the *same* victims again for a second preemptor in the interval before they are gone? Find the answer; it is in the same package.

**Expect** — a small executor with a bounded set of workers, and a boundary that leaves the *decision* on the scheduling thread and the *deletions* off it. Expect the nomination to be on the synchronous side, and expect that to be forced rather than chosen: nothing else can prevent the next pod's cycle from claiming the space, so the nomination has to be visible before the cycle ends.

Expect step 6's answer to be a set of in-flight victims tracked in memory, and expect it to have the same shape as [`assume`](11-what-assume-buys.md) and the same shape as the nomination accounting — three separate mechanisms in this phase, all solving *"I have decided something the cluster has not recorded yet"*. Naming that as one recurring problem rather than three details is what this exercise is for.

Expect the commit history to be less tidy than the KEP. If the change landed across several commits with feature-gate scaffolding, say so; a claim citing a line that is behind a gate must say which gate and whether it is on by default at your sha.

**Write down** — the falsifiable claim from step 5 in full, the boundary from step 3, the answer to step 6 with `file:line`, and the feature gate's name and default if there is one.

**Footprint note** — reading only. `pair` up and idle; 7.5GB unchanged.

**Teardown** — nothing created. **The topology stays.**
