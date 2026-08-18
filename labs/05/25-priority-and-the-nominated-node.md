<a id="priority-and-the-nominated-node"></a>
# The preemptor does not get the node it emptied — it gets a claim on it

**Claim** — when a high-priority pod triggers preemption, the scheduler writes `status.nominatedNodeName` on it and then **ends the cycle without binding it**; the pod goes back through the queue and is scheduled on a later attempt, after the victims are actually gone. The nomination is a reservation against the scheduler's own future decisions, not a placement.

**Rests on** — [the queue state machine](19-three-queues-and-two-exits.md), because the interesting half of this is which queue the preemptor is in between the nomination and the bind. [Drill 5.C2](35-5c2-preemption-with-real-victims.md) is victim *selection* among many candidates at scale; this is the mechanism, with one victim, on two nodes.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Setup**

```sh
kubectl apply -f - <<'EOF'
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata: {name: academy-low}
value: 100
globalDefault: false
---
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata: {name: academy-high}
value: 100000
globalDefault: false
EOF
```

Fill the worker with low-priority pods until nothing more fits, exactly as in [exercise 20](20-watch-a-pod-move.md) but with `priorityClassName: academy-low` on every one of them. Record which pods are where before you start.

**Do**

1. Read [KEP-268](../../strands/source-reading.md#area-3-scheduler) first and answer its question in writing **before** the experiment: why a nominated node rather than an immediate bind? Two reasons are defensible and one of them is about the binding cycle you already measured.

2. Watch three things at once. In three sessions:

   ```sh
   kubectl -n sched-lab get pods -o wide -w
   kubectl -n sched-lab get events -w --field-selector reason=Preempted
   while :; do kubectl -n sched-lab get pod bully -o jsonpath='{.status.nominatedNodeName}{" "}{.spec.nodeName}{"\n"}' 2>/dev/null; sleep 0.3; done
   ```

3. Submit the preemptor:

   ```sh
   kubectl -n sched-lab run bully --image=registry.k8s.io/pause:3.9 --restart=Never \
     --overrides='{"spec":{"priorityClassName":"academy-high","containers":[{"name":"pause","image":"registry.k8s.io/pause:3.9","resources":{"requests":{"cpu":"600m"}}}]}}'
   ```

4. Capture the sequence with timestamps: nomination appears → victim gets a `deletionTimestamp` → victim gone → preemptor bound. Note the gap between the first and the last.

5. Find the write. `PostFilter` is the extension point; the nomination is a status update:

   ```sh
   grep -n 'NominatedNodeName\|PostFilter' pkg/scheduler/framework/preemption/preemption.go | head -20
   ```

6. Answer the second question from the code: while `bully` holds a nomination and is waiting, **what stops a third, lower-priority pod from taking the space the victim vacated?** Find the mechanism; it is not a lock.

**Observe** — `status.nominatedNodeName` and `spec.nodeName` as separate fields with different lifetimes, the victim's graceful termination period, and the `Preempted` event on the victim.

**Expect** — a nomination within a second, a victim that takes its full termination grace period to go, and a preemptor that binds only after that. The gap is dominated by the victim's shutdown, which is the honest reason for the design: the scheduling cycle cannot block for thirty seconds waiting for a container to exit, so it publishes its intent and moves on to other pods.

Expect the nomination to survive across scheduling attempts, and expect the preemptor to be retried through the ordinary queue path — the same backoff and the same event-driven wake-up you have already measured, with nothing special about it. **Preemption is not a separate mechanism; it is one extension point plus a field.**

Expect the answer to step 6 to be that other pods' fit calculations account for the nominated pod on that node. Say which structure holds that, and note that this is the same problem [`assume` solved](11-what-assume-buys.md) for a different gap in time.

**Write down** — your pre-experiment answer scored against the code, the timestamped sequence, the `file:line` of the nomination write, and the mechanism from step 6.

**Footprint note** — one preemption with one real victim on `pair`. This is the smallest true preemption the lab can produce and it costs nothing above the standing 7.5GB. [The drill](35-5c2-preemption-with-real-victims.md) is where scarcity does the work across three nodes.

**Teardown** — `kubectl -n sched-lab delete pod bully --ignore-not-found`; leave the low-priority ballast and both PriorityClasses in place, [the next exercise](26-selectvictimsonnode-and-a-pdb-that-forbids.md) needs them. **The topology stays.**
