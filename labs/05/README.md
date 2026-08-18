# Labs — Phase 5, Scheduler

Thirty-seven exercises in the order they are meant to run, for **the one phase whose lab
splits in two and the one phase that changes the lab's own hardware**. Each states one
claim to test or one artifact to produce, links its
[topology](../../strands/lab-topologies.md) rather than restating a footprint, and ends
with a teardown that does two things: **deletes what that exercise created**, then says
whether the topology stays or goes.

The framing — why each module exists, what to read and the question to answer from it —
stays in [`phases/05-scheduler.md`](../../phases/05-scheduler.md). These files hold only
what you type and what you should see.

| # | Exercise | Why it exists |
|---|---|---|
| 1 | [The tour the SIG wrote, read with the source open](01-the-sig-tour-in-call-order.md) | The call path, built from the guided tour the area says to read first. |
| 2 | [The extension points, and what an error at each one costs](02-eleven-points-and-what-an-error-does.md) | The table every later exercise indexes into — and the cost of failing rises down it. |
| 3 | [Two cycles, one thread](03-two-cycles-not-one.md) | Drawn from memory before the KEP corrects it; the boundary is never where people put it. |
| 4 | [The default plugin set, mapped onto the points it fills](04-what-actually-runs-by-default.md) | Twenty plugins, half again as many registrations — and where `VolumeBinding` sits, for P8 to collect. |
| 5 | [A `Filter` plugin is two methods and a string](05-the-smallest-plugin-that-exists.md) | The shape build artifact 2 must reproduce from outside the tree. |
| 6 | [Three ways to make every node refuse](06-three-rejections-three-plugins.md) | Provisions `pair`; the event message is the thread 5.C1 pulls. Flags the module's one substitution. |
| 7 | [The OOM you were promised, produced on purpose](07-fifteen-thirty-six-will-not-link-a-scheduler.md) | The hardware change, stated as steps, with the revert named forward. |
| 8 | [Scheduling, minus the scheduler: one POST](08-bind-a-pod-with-one-post.md) | Demystifies the next exercise before it exists, and produces the 409 that 5.C4 depends on. |
| 9 | [Build artifact 1: a scheduler with no framework in it](09-two-hundred-lines-that-schedule.md) | The phase's centre; every module after it answers *what does the real one do that this does not?* |
| 10 | [5.C4 — two schedulers, one pod](10-5c4-two-schedulers-one-pod.md) | The race and the recovery in one drill: the API server is the only arbiter. |
| 11 | [The node that fits ten times because the cache has not caught up](11-what-assume-buys.md) | `assume` is a correctness mechanism that looks like a performance one. |
| 12 | [One pod, at `-v=10`, mapped onto `schedule_one.go`](12-one-pod-through-schedule-one.md) | The only sane way into a 54 KB file: enter it from a log line. |
| 13 | [Pod B is scheduled while pod A is still being bound](13-why-the-bind-is-async.md) | The overlap, measured from timestamps in one log. |
| 14 | [Why a plugin cannot keep state in a package variable](14-state-without-globals.md) | Written as a defect report, not a rule — the wrong placement it causes. |
| 15 | [`Insufficient cpu` — the line that formats it](15-the-line-that-writes-insufficient-cpu.md) | A node 100% scheduled and 3% busy: the scheduler is a bookkeeper of promises. |
| 16 | [The knob that cannot move here](16-the-knob-that-cannot-move-here.md) | The phase's footprint flag, and where the real scheduler first gets a config file. |
| 17 | [Above the floor at last: a hundred nodes that do not exist](17-a-hundred-nodes-that-do-not-exist.md) | The smallest change that makes exercise 16 measurable — upstream's own harness, no VMs. |
| 18 | [The archaeology case: the path that no longer exists](18-find-the-queue-yourself.md) | The gate's third condition, and the technique matters more than the answer. |
| 19 | [The queue state machine, written before any code is opened](19-three-queues-and-two-exits.md) | Two exits from `unschedulablePods`, three orders of magnitude apart. |
| 20 | [A pod moving between queues, timed](20-watch-a-pod-move.md) | The five-minute wait is the point: the flush is a net, not the mechanism. |
| 21 | [Attempt 1, 3 and 6: the gaps double until they stop](21-the-backoff-you-can-time.md) | And a scheduler restart resets everyone's backoff, which is a real operational lever. |
| 22 | [5.C1 — fifty pods that will not schedule](22-5c1-an-unschedulable-backlog.md) | A blind-drawn cause, diagnosed against a clock from events and metrics alone. |
| 23 | [Ten cluster changes, one retry](23-the-hint-that-decides-a-retry.md) | The event was delivered and the hint declined it — two states the counter can tell apart. |
| 24 | [`SchedulingGated` — a pod the scheduler declines to look at](24-a-pod-that-is-never-considered.md) | The one pending state with no event at all, and a one-way door in the API. |
| 25 | [The preemptor gets a claim, not the node](25-priority-and-the-nominated-node.md) | Preemption is one extension point plus a field. |
| 26 | [A PDB that makes preemption fail, and says so](26-selectvictimsonnode-and-a-pdb-that-forbids.md) | The negative result: full cluster, high priority, and nothing happens. |
| 27 | [Why victim deletion left the scheduling thread](27-why-victim-deletion-left-the-thread.md) | The checklist's third falsifiable claim, provable without reproducing the old behaviour. |
| 28 | [Build artifact 2: a scoring plugin in a scheduler you own](28-the-out-of-tree-plugin.md) | The last thing in the phase that compiles, and the image module 5.6 depends on. |
| 29 | [Failing after the decision costs more than failing before it](29-a-hard-error-at-reserve.md) | Measured in extension-point counters, and the diagnostics get worse as you go down. |
| 30 | [Stage 2, shape one: a Deployment nobody privileged](30-a-second-scheduler-by-schedulername.md) | The ClusterRole derived from your own API calls — and why the real scheduler is a static pod. |
| 31 | [Stage 2, shape two: one process, two scheduler names](31-a-profile-not-a-binary.md) | Two profiles share one cache; two schedulers cannot. |
| 32 | [Both artifacts, two replicas each, one lease](32-the-lease-changes-hands.md) | What leader election buys a scheduler when the API already prevents double-binds. |
| 33 | [The revert: 2560MB back to 1536MB](33-forge-back-down-and-workhorse-up.md) | The arithmetic first, then the teardown, the disk, the resize and the third node. |
| 34 | [The same workload, two profiles, two distributions](34-placement-that-differs-measurably.md) | A scoring plugin does not decide placement; it bids for it. Capstone part one. |
| 35 | [5.C2 — which pod died, on which node, and why that one](35-5c2-preemption-with-real-victims.md) | Real scarcity, real victims, predicted in advance. Capstone part two. |
| 36 | [5.C3 — unschedulable for a reason that is not scarcity](36-5c3-a-spread-nobody-can-satisfy.md) | Four messages in one diagnostic table: the phase's most portable artifact. |
| 37 | [The capstone: a measurement and a story](37-the-capstone-narrative.md) | Graded on citations re-derived live, and on the gate answered honestly. |

## Which cluster is running when, and what changes on the host

**Exercises 1 to 5 need no topology at all** — the whole first half of module 5.1 is
reading on [`forge`](../../strands/lab-topologies.md#build-guest), which defers the phase's
first provision until there is something to look at.

[`pair`](../../strands/lab-topologies.md#pair) comes up at **exercise 6** and runs through
**exercise 32** — modules 5.1 to 5.5, twenty-seven exercises, both build artifacts and two
deployment shapes. It is destroyed at [exercise 33](33-forge-back-down-and-workhorse-up.md),
which then provisions [`workhorse`](../../strands/lab-topologies.md#workhorse) for the last
four.

**`forge` changes size twice in this phase, and both changes are exercises.**
[Exercise 7](07-fifteen-thirty-six-will-not-link-a-scheduler.md) raises it from 1536MB to
2560MB by producing the OOM kill that justifies it; [exercise 33](33-forge-back-down-and-workhorse-up.md)
puts it back before `workhorse` comes up. This is [the split the strand
specifies](../../strands/build-mechanics.md#p5-split) and it is not optional in either
direction — the phase's two configurations are:

| Exercises | Topology | `forge` | Total | Margin |
|---|---|---|---|---|
| 6 | `pair` 5.0GB | 1536MB | 6.5GB | 3.0GB |
| 7–32 | `pair` 5.0GB | **2560MB** | 7.5GB | 2.0GB |
| 34–37 | `workhorse` 7.0GB | 1536MB | **8.5GB** | **1.0GB** |

against the [9.5GB ceiling](../../strands/lab-topologies.md#ceiling). The third row is why
**nothing compiles once `workhorse` is up**: `workhorse` plus a 2560MB `forge` is 9.5GB with
no margin at all. The plugin image is built at [exercise 28](28-the-out-of-tree-plugin.md),
pushed to the registry, and only *run* on `workhorse`.

**Disk is tighter than RAM on this phase.** Two k/k-scale module graphs accumulate on
`forge` across modules 5.2 to 5.5, so `go clean -modcache` and `docker system prune` are
teardown steps in [exercise 33](33-forge-back-down-and-workhorse-up.md) rather than advice.

## Exceptions

- **Exercises 1 to 5, 14, 18, 19 and 27** are reading and writing only; several run while `pair` is up and idle, and their footprint notes say so.
- **Exercise 6** is where the module's planned custom `Filter` plugin is replaced by three stock plugins that produce the same observable; the substitution and the reject-everything plugin's new home are argued in that file's footprint note.
- **Exercise 16** is the phase's footprint flag: `percentageOfNodesToScore` cannot be demonstrated on any topology this lab can build, and the arithmetic proves it rather than the demo failing to.
- **Exercise 17** needs `pair` down or idle — the scheduler performance harness runs an API server, an etcd and a scheduler inside one process on a 2560MB guest, and finding where it dies is part of the exercise.
- **Exercises 25 and 26** run preemption on two nodes deliberately, to isolate the *mechanism* and the *PDB refusal*; victim **selection** among candidates is [5.C2](35-5c2-preemption-with-real-victims.md) on three.
- **Exercise 33** is a hardware change and a teardown rather than a lesson, and it is numbered because eleven parallel readers hitting an unexplained OOM during a link is what happens when it is a footnote.
