# Labs — Phase 4, Controllers & reconciliation

Thirty-four exercises in the order they are meant to run. The phase has one shape and
repeats it: a loop that watches, enqueues a key, re-reads the world and writes toward
desired state. You meet it three times — reading it in `sample-controller`, writing it by
hand, then watching a scaffold generate the wiring around it — and the third meeting is
only worth anything because the second one hurt.

Each file states one claim to test or one artifact to produce, links its
[topology](../../strands/lab-topologies.md) rather than restating a footprint, and ends
with a teardown that does two things: **deletes what that exercise created**, then says
whether the topology stays or goes.

The framing — why each module exists, what to read and the question to answer from it —
stays in [`phases/04-controllers.md`](../../phases/04-controllers.md). These files hold
only what you type and what you should see.

**Where the clusters are.** Exercises 1–2, 6–7 and 13 need no cluster at all: two are
reading and drawing, two are standalone Go probes on [`forge`](../../strands/lab-topologies.md#build-guest),
and one is a redrawing. [`pair`](../../strands/lab-topologies.md#pair) is provisioned at
[exercise 3](03-sample-controller-against-a-real-cluster.md) and stays up until
[the capstone](34-the-capstone-writeup.md) destroys it — one provision for the whole phase.
Exercises 8–12 run probes on `forge` against that same cluster. Steady state is 5.0GB for
`pair` plus 1536MB for `forge`: **6.5GB against the [9.5GB ceiling](../../strands/lab-topologies.md#ceiling)**,
with 3.0GB of margin and no point in the phase that needs more. `forge` is not raised;
[the one place that is tight](16-envtest-is-a-real-apiserver.md) is handled by not running
two things at once rather than by buying memory.

| # | Exercise | Why it exists |
|---|---|---|
| 1 | [Draw the pipeline before you open any of it](01-draw-it-before-you-read-it.md) | A wrong drawing you keep, so exercise 13 has something to be a correction of. |
| 2 | [The line that enqueues a key, and the line that pays for it](02-the-line-that-enqueues-a-key.md) | The phase's first falsifiable claim, answered from `sample-controller` before anything runs. |
| 3 | [The Rosetta Stone, running against a cluster you can break](03-sample-controller-against-a-real-cluster.md) | Provisions `pair`; makes the read code a process with logs you can interrupt. |
| 4 | [One log line per stage, and the order they fire in](04-five-log-lines-five-stages.md) | Five `klog` tags, and the discovery that the counts do not match. |
| 5 | [Two edits: one gets stomped, one survives](05-stomp-it-back.md) | A prediction table that draws the boundary of what a controller actually owns. |
| 6 | [Add one key a hundred times, count the reconciles](06-the-same-key-a-hundred-times.md) | The dirty/processing sets, predicted from source then measured in a 40-line probe. |
| 7 | [The gap between retries, measured against the limiter that sets it](07-the-hot-loop-and-the-backoff-that-hides-it.md) | Eight predicted gaps, then the hot loop you get by dropping one call. |
| 8 | [One Pop, one key, several deltas](08-deltas-are-per-key.md) | A hand-wired reflector and DeltaFIFO — the informer taken apart rather than constructed. |
| 9 | [The delete you never saw, delivered anyway](09-force-a-relist.md) | `DeletedFinalStateUnknown`, produced deterministically instead of waited for. |
| 10 | [The third layer of a failure you have met twice](10-the-410-under-your-own-informer.md) | The 410-to-relist chain under your own reflector — the gate's third condition. |
| 11 | [`HasSynced` is a promise about one moment, not about being current](11-what-hassynced-actually-promises.md) | Three things it does not promise, each shown rather than listed. |
| 12 | [4.C4 — a controller with an empty cache concludes nothing should exist](12-4c4-act-before-the-cache-is-synced.md) | Fifty objects deleted with no error, which is why objective 2 exists. |
| 13 | [The same drawing, now with the file names checked](13-the-same-drawing-corrected.md) | Module 4.1's written artifact, scored against exercise 1's guesses. |
| 14 | [The API type you write, and the four things generated from it](14-generate-the-clientset.md) | Fixes the `Ensemble` type the rest of the phase — and P8 — points back at. |
| 15 | [Build artifact 1: every moving part wired by hand](15-the-hand-wired-loop.md) | Seven requirements, no framework, and a finalizer that is genuinely necessary. |
| 16 | [The gate: four assertions a fake client would pass and a real API server fails you on](16-envtest-is-a-real-apiserver.md) | The gate for both artifacts, chosen so the comparison later is honest. |
| 17 | [4.C1 — SIGKILL mid-`syncHandler`, twice, with one flag changed](17-4c1-kill-it-mid-reconcile.md) | Killing the correct version proves nothing; the second version is the proof. |
| 18 | [The error you returned, and the retry that never came](18-forget-to-requeue.md) | Three one-line breakages, each producing a different flavour of silent under-retry. |
| 19 | [Stage 2: the same binary, and a ClusterRole discovered one 403 at a time](19-stage-2-and-the-role-you-write-yourself.md) | A role grown from evidence, including the two verbs nobody predicts. |
| 20 | [Someone else's reconcile loop, read the day after you wrote yours](20-flux-is-your-loop-in-production.md) | Seven rows of mapping, and the two additions that close P1's helm gap. |
| 21 | [`manageReplicas`: the subtraction, and the two policies wrapped around it](21-the-diff-is-the-easy-half.md) | Slow-start and ranked deletion — the policy that is not arithmetic. |
| 22 | [Make your own operator over-create, then name the two defences against it](22-expectations-or-over-create.md) | The phase's second falsifiable claim, caused on purpose before it is explained. |
| 23 | [Three things an owner reference will not do for you](23-one-owner-may-be-the-controller.md) | Three rules, three failures, and the justification for exercise 15's finalizer. |
| 24 | [The same delete, three times, with three different meanings](24-three-propagation-policies.md) | A nine-cell prediction table, and foreground deletion recognised as your own dance. |
| 25 | [4.C2 — stuck in `Terminating`, cleared twice, once wrongly](25-4c2-a-finalizer-that-never-completes.md) | The wrong clearance and the right one look identical from outside; only one leaks. |
| 26 | [A namespace that will not go, and the condition that says why](26-a-namespace-stuck-in-terminating.md) | Two causes with opposite repairs, distinguished by reading `status.conditions`. |
| 27 | [The garbage collector matches on UID, and it checks before it deletes](27-the-uid-is-the-edge.md) | The GC obeying 4.C4's rule, which is a satisfying place to end module 4.4. |
| 28 | [Two replicas, one Lease, and a failover you can time](28-two-replicas-one-lease.md) | Objective 7's measurement: three configured durations against two measured gaps. |
| 29 | [Why the renew deadline is shorter than the lease, and the window it does not close](29-why-the-renew-deadline-is-shorter.md) | The third falsifiable claim, and the thing that actually stops the second writer. |
| 30 | [4.C3 — two replicas, no lease, and the fight you can measure](30-4c3-two-replicas-no-leader-election.md) | Nothing visibly breaks; the damage is three numbers you have to go and count. |
| 31 | [Scaffold the same operator, and change nothing about the test](31-scaffold-the-same-operator.md) | Build artifact 2, gated by artifact 1's `envtest` file copied across unmodified. |
| 32 | [The same kill, and where the framework actually helps](32-the-same-kill-a-different-graceful.md) | Identical under SIGKILL; the difference is under SIGTERM and it is not correctness. |
| 33 | [The diff: every generated file against the line you wrote by hand](33-the-diff.md) | The capstone artifact the phase cannot omit — forty files, three verdicts, one ratio. |
| 34 | [The capstone: two operators, one proof, four citations](34-the-capstone-writeup.md) | The no-lost-work transcript, and four citations that have probably moved. |

## Exceptions

- **Exercises 1, 2 and 13** create nothing anywhere. The artifact is a drawing and its correction, and exercise 2's citation is read from a clone on `forge`.
- **Exercises 6 and 7** are standalone Go probes with no cluster involved: the workqueue is an ordinary library and runs fine on its own.
- **Exercise 16** is [the phase's one tight spot](16-envtest-is-a-real-apiserver.md). `envtest` starts a real `kube-apiserver` and `etcd` on `forge` beside a linking Go build. The fix is `go test -p 1` and not running stage 1 at the same time — flagged there with the arithmetic, rather than raising the guest.
- **Exercise 20** is the ecosystem read, placed immediately after the operator because [the phase says so](../../phases/04-controllers.md#ecosystem) and because a day later it stops being a reality check.
- **Exercise 25** requires the operator deployed *in* the cluster, not `go run` on `forge` — the drill breaks its ClusterRole, and a binary running with your admin kubeconfig has nothing to break.
- **Exercises 31–33** need artifact 1 scaled to zero. Two operators managing one CRD is [4.C3](30-4c3-two-replicas-no-leader-election.md) by accident.
