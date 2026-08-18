<a id="one-hundred-lines-of-select"></a>
# The whole kubelet, as one `select` over five channels

**Artifact** — a one-page annotation of `syncLoopIteration`: every channel it reads, what feeds that channel, what it does with each message, and — the part that makes the rest of the kubelet legible — the two-set reconcile pattern named, with the code that holds each set.

**Rests on** — everything in the phase so far. Each of the five channels has already produced an observable event for you, and the point of doing this last is that you can name them from memory instead of from the comments.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued, for step 3. The reading is on any clone.

**Read** — `pkg/kubelet/kubelet.go`, **`syncLoopIteration` only** (item 19). The file is 156 KB and reading it linearly is a waste of a week; this function is about a hundred lines and it is the kubelet's entire main loop. [The reading order says so explicitly](../../strands/source-reading.md#area-7-kubelet) — take it at its word.

For each `case` in the `select`, answer three things: what type flows on the channel, which component writes to it, and what the handler does with a pod it has never seen before.

Then read the type comments at the top of `pkg/kubelet/pod_workers.go` (item 20) — **the comments, not the implementation** — for the one question that `syncLoopIteration` does not answer: what guarantees two goroutines are never syncing the same pod at once?

**The pattern to name.** The loop maintains two sets and works to close the gap between them:

- the **desired** set — every pod assigned to this node, merged from [the three sources](19-the-mirror-pod-that-will-not-die.md) into one stream of updates;
- the **observed** set — what the runtime actually reports, refreshed by [relist](03-relist-and-the-threshold-it-checks.md);

and `syncLoopIteration` is the reconciler between them: it never asks *what changed*, it asks *what is the gap now*. Find the upstream names for these two sets — they are a matched pair of nouns, they appear in the sub-manager you are about to read about, and once you have them you will see the same pair in three other places in the kubelet. **Write both names down.** [P8's volume manager](../../phases/08-storage.md) is where the pattern is read properly, in the sub-manager that owns the clearest copy of it; here you only need the shape and the vocabulary, so that P8 is a second sighting rather than a first.

**Do**

1. Annotate the function: one line per `case`, with the writer named.
2. Match each channel to an exercise in this phase that fired it. Four of the five have one; name it.
3. Fire two of them deliberately and confirm the handler ran, from the kubelet's log at `-v=4` on the worker:

   ```sh
   ssh zain@10.10.10.131 'sudo journalctl -u kubelet -f' &
   kubectl -n default run probe-me --image=registry.k8s.io/e2e-test-images/agnhost:2.47 \
     --overrides='{"spec":{"nodeName":"pair-worker","containers":[{"name":"probe-me","image":"registry.k8s.io/e2e-test-images/agnhost:2.47","args":["netexec","--http-port=8080"],"livenessProbe":{"httpGet":{"path":"/healthz","port":8081},"periodSeconds":5,"failureThreshold":2}}]}}'
   ```

   That liveness probe points at a port nothing is listening on, so it fails on schedule: one channel delivers the pod addition, another delivers the probe result, and both appear in the log with the pod's name.

**Expect** — five sources, no timers you did not already meet, and **no branching on event type anywhere in the handlers**: an add and an update take the same path, because the handler recomputes from the pod spec rather than applying a delta. That is the same property [P4's controllers](../../phases/04-controllers.md) had and it is why a kubelet that misses a message recovers on the next housekeeping tick instead of drifting.

Expect the housekeeping case to be the one that catches everything the other four missed — orphaned pods, pods that should have been cleaned up, work that got dropped. Every reconciler in Kubernetes has this case and it is always the least interesting to read and the most important to have.

Expect `pod_workers.go`'s comments to describe a per-pod goroutine with a single queued update, which is the answer to the concurrency question and the reason a slow pod cannot block another pod's sync — but *can* block its own next update indefinitely.

**Write down** — the five-channel annotation, the two set names with a `file:line` for each, and one sentence connecting the pattern to the level-triggered reconcile from [P4](../../phases/04-controllers.md). This is [objective 1](../../phases/06-kubelet-node.md#objectives) and it is the phase's most reusable page.

**Footprint note** — one small pod, deleted immediately.

**Teardown** — `kubectl delete pod probe-me --now` and stop the log follower. **The topology stays** — [the observability stack](25-the-stack-that-must-not-be-evicted.md) goes on next.
