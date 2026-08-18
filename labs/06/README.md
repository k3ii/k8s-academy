# Labs — Phase 6, kubelet, the node and observability

Twenty-nine exercises in the order they are meant to run, for **the phase where the
cramped lab stops being a constraint and becomes the instrument**: a 2048MB worker is
small enough that eviction, OOMKill and disk pressure are things you can produce
deliberately in minutes rather than things you read about. Each file states one claim to
test or one artifact to produce, links its
[topology](../../strands/lab-topologies.md) rather than restating a footprint, and ends
with a teardown that does two things: **deletes what that exercise created**, then says
whether the topology stays or goes.

The framing — why each module exists, what to read and the question to answer from it —
stays in [`phases/06-kubelet-node.md`](../../phases/06-kubelet-node.md). These files hold
only what you type and what you should see.

| # | Exercise | Why it exists |
|---|---|---|
| 1 | [The sub-managers, named before any of them is read](01-the-sub-managers-named.md) | The kubelet has no readable entry point, so the map is built from the SIG's own document first. |
| 2 | [One pod is how many CRI calls](02-one-pod-is-how-many-cri-calls.md) | The proto is easier than the Go that consumes it, and the sandbox stops being a mystery process. |
| 3 | [Relist is one loop, and `Healthy()` is one subtraction](03-relist-and-the-threshold-it-checks.md) | The threshold located in `generic.go`, then watched moving in the kubelet's own metrics. |
| 4 | [`PLEG is not healthy`, produced on a deadline](04-pleg-is-not-healthy.md) | The error names the observer, not the thing that broke — the phase's first diagnostic lesson. |
| 5 | [What this node actually runs for PLEG](05-what-the-node-actually-runs-for-pleg.md) | Evented or generic, answered from `configz` — and why relist survives either way. |
| 6 | [Classify five pods from the algorithm](06-three-pods-three-classes.md) | Three of the five are the cases people get wrong, including limits-only. |
| 7 | [Compute the number the kernel will use](07-oom-score-adj-from-the-formula.md) | Two Burstable pods, two different scores, both predicted from the formula. |
| 8 | [Install the injector once, and read every capability it asks for](08-chaos-mesh-at-582mi.md) | Chaos Mesh enters the curriculum here; the capability table is the artifact, and the install is never an exercise again. |
| 9 | [6.C3 — two OOM kills that look the same from `kubectl`](09-6c3-who-killed-the-pod.md) | A cgroup OOM kill and an `OOMKilled` status are different events; one of them is silent. |
| 10 | [Four signals, eight predictions, written before the code](10-the-signals-before-the-code.md) | Commit to answers the source can contradict — the cheapest way to read `eviction_manager.go`. |
| 11 | [One function decides who dies](11-synchronize-and-the-ranking.md) | "BestEffort first" is a consequence of the comparators, not a rule anyone wrote. |
| 12 | [Set the threshold yourself, cross it on purpose](12-an-eviction-you-configured.md) | Every step of `synchronize()` in the log, and a corpse that stays behind to explain itself. |
| 13 | [The kubelet reacts before its own timer does](13-faster-than-housekeeping.md) | Two runs at two speeds tell a watermark notifier apart from a poller. |
| 14 | [Evicted or OOMKilled, decided by allocation speed](14-evicted-or-oomkilled.md) | The discrimination procedure, built from two runs of one pod spec. |
| 15 | [Walk from the root cgroup down to one container](15-the-cgroup-tree-under-one-pod.md) | Guaranteed pods have no class directory, and that asymmetry explains itself. |
| 16 | [Write one number and turn an OOMKill into a slowdown](16-throttled-instead-of-killed.md) | `memory.high` is the file Kubernetes does not set, and the kubelet reconciles it back. |
| 17 | [Account for every megabyte](17-where-the-ram-went.md) | The eviction threshold is a permanent tax on schedulable memory — proved by changing it. |
| 18 | [A CPU limit is a quota per period](18-cpu-max-and-the-throttle-counter.md) | The usage graph looks fine while the throttle counter says otherwise. |
| 19 | [The pod that will not die](19-the-mirror-pod-that-will-not-die.md) | Three ways to delete a static pod, two of which the API server cheerfully accepts. |
| 20 | [The node refuses what the scheduler allowed](20-the-node-refuses-what-the-scheduler-allowed.md) | `Pending` and `Failed/OutOfmemory` are the same request refused by different components. |
| 21 | [Two heartbeats, two frequencies](21-two-heartbeats-two-frequencies.md) | The detection latency computed from four settings, before anything is broken. |
| 22 | [6.C2 — the kubelet stops; the pods do not](22-6c2-the-kubelet-stops-the-pods-do-not.md) | Traffic uninterrupted, `Ready=Unknown`, and a `Terminating` pod that cannot terminate. |
| 23 | [6.C1 — the node vanishes](23-6c1-the-node-vanishes.md) | Identical to 6.C2 for forty seconds, then completely different — and the divergence is the finding. |
| 24 | [The whole kubelet, as one `select`](24-one-hundred-lines-of-select.md) | The only function read from `kubelet.go`, and where the two-set reconcile pattern gets its names. |
| 25 | [The stack that must not be evicted](25-the-stack-that-must-not-be-evicted.md) | Pinned to the control plane on purpose, and the phase's footprint argument in full. |
| 26 | [node-exporter's number is not the kubelet's number](26-the-metric-is-the-file.md) | The obvious PromQL does not predict eviction on the node it is drawn for. |
| 27 | [An eviction as a slope](27-an-eviction-as-a-slope.md) | The graph shows two things the log cannot: the approach, and the overshoot. |
| 28 | [6.C4 — disk pressure has a preamble](28-6c4-disk-pressure-cascade.md) | The kubelet deletes images before it touches a pod; memory reclaim has no such move. |
| 29 | [The capstone: a pod dies, a Service stops sending traffic](29-the-capstone-trace.md) | Half the hops cited in source, half observed with the citations named as owed to P7. |

## Which cluster is running when

**Exercise 1 needs no topology** — the map is built from design documents before anything
runs. [`pair`](../../strands/lab-topologies.md#pair) comes up at
[exercise 2](02-one-pod-is-how-many-cri-calls.md) and stays up for the rest of the phase,
destroyed at [the capstone](29-the-capstone-trace.md). Twenty-eight exercises on one
cluster is the longest continuous run in the curriculum, and it is deliberate: Chaos Mesh
and the monitoring stack are both installed once and left, so every drill after
[exercise 8](08-chaos-mesh-at-582mi.md) starts with its instruments already in place.

**`forge` never changes size and is never used for a build** — [there is no build artifact
this phase](../../phases/06-kubelet-node.md), so the 1536MB guest sits at its standing size
throughout and the whole phase runs at one footprint:

| Exercises | Topology | `forge` | Inside the guests | Total | Margin |
|---|---|---|---|---|---|
| 2–7 | `pair` 5.0GB | 1536MB | — | 6.5GB | 3.0GB |
| 8–24 | `pair` 5.0GB | 1536MB | Chaos Mesh 582Mi | 6.5GB | 3.0GB |
| 25–29 | `pair` 5.0GB | 1536MB | + monitoring ~850Mi | 6.5GB | 3.0GB |

against the [9.5GB ceiling](../../strands/lab-topologies.md#ceiling). The guest total never
moves, because **this phase's pressure is entirely inside the two nodes** — 582Mi of
injector and 850Mi of monitoring come out of the control plane's 3072MB, not out of the
host's margin. That is the number to watch, and
[exercise 25](25-the-stack-that-must-not-be-evicted.md) does the arithmetic in full.

**The worker's 2048MB is the instrument, not the constraint.** Exercises 12, 14, 27 and 28
are all sized to drive it into a real eviction, and the monitoring stack is pinned to the
*other* node so the recorder survives the event it is recording.

## Exceptions

- **Exercises 1, 10 and 11** create nothing; the prediction table and the comparator pseudocode are the artifacts, and 10 is scored two exercises later.
- **Exercise 8 is the phase's one install-and-never-again exercise.** Chaos Mesh's helm command lives in [the chaos strand](../../strands/chaos.md#install); later phases re-run it as one line of setup rather than as a new exercise, and the capability-to-mechanism reading happens here, once.
- **Exercise 14 is the deliberate cascade.** It is the only exercise designed to make a node unresponsive, and its footprint note says what to do if it does — which is not to destroy the topology.
- **Exercise 25 is the phase's footprint flag:** metrics only, no logs and no traces, with the arithmetic showing why adding them would not fit and why the smallest change is to leave them out.
- **Exercise 28 costs disk rather than RAM** — the only exercise in the phase that tests the other half of the one-topology-at-a-time rule.
- **Exercises 22, 23 and 28 use no chaos tooling at all.** `systemctl stop`, `qm stop` and `dd` are more precise than anything a tool would inject, and [the strand says so](../../strands/chaos.md#cannot-express).
