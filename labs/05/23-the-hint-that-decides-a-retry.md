<a id="the-hint-that-decides-a-retry"></a>
# Ten cluster changes, one retry: the plugin decides which events are its business

**Claim** — not every cluster change wakes a pending pod. Each plugin declares which event types could possibly change its own verdict, and a hint function decides per event whether *this* pod is worth retrying; you can produce ten irrelevant events and see zero extra scheduling attempts, then produce one relevant event and see exactly one.

**Rests on** — [the backoff measurement](21-the-backoff-you-can-time.md), which counted attempts, and [the queue state machine](19-three-queues-and-two-exits.md), which is where the moved pods go. This is the mechanism that makes the event-driven exit selective rather than a broadcast.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued, real scheduler at `--v=4` again as in [exercise 21](21-the-backoff-you-can-time.md).

**Setup** — one pod pending for a resource reason, and a clean attempt count:

```sh
kubectl -n sched-lab scale deployment ballast --replicas=3
kubectl -n sched-lab run waiter --image=registry.k8s.io/pause:3.9 --restart=Never \
  --overrides='{"spec":{"containers":[{"name":"pause","image":"registry.k8s.io/pause:3.9","resources":{"requests":{"cpu":"600m"}}}]}}'
kubectl -n kube-system logs -f -l component=kube-scheduler --tail=0 > /tmp/hints.log &
kubectl get --raw /metrics | grep '^scheduler_queue_incoming_pods_total' > /tmp/incoming-before.txt
```

**Do**

1. **Read the declaration before producing the events.** Every plugin that can be affected by cluster state declares it:

   ```sh
   grep -rn 'EventsToRegister' pkg/scheduler/framework/plugins/noderesources/fit.go \
        pkg/scheduler/framework/plugins/tainttoleration/*.go
   ```

   Write down what `noderesources` declares. Then find its hint function — the one that is handed the old and new objects and returns a decision:

   ```sh
   grep -n 'func (f \*Fit) isSchedulableAfter\|QueueSkip\|QueueAfterBackoff\|Queue(' pkg/scheduler/framework/plugins/noderesources/fit.go
   ```

   Predict, from that code alone, what it will say about a node whose **labels** changed and whose allocatable did not.

2. **Read the registration side.** `eventhandlers.go` is where informers are wired to the queue:

   ```sh
   grep -n 'AddEventHandler\|addAllEventHandlers\|func (sched \*Scheduler) add' pkg/scheduler/eventhandlers.go | head -20
   ```

   List the resources the scheduler watches. It is a longer list than "pods and nodes", and the extras are the ones you will not have guessed.

3. **Ten irrelevant events:**

   ```sh
   for i in $(seq 1 10); do kubectl label node <worker-node> academy.k3ii.dev/churn=$i --overwrite; sleep 1; done
   grep -c 'Attempting to schedule pod.*waiter' /tmp/hints.log
   ```

4. **One relevant event:**

   ```sh
   kubectl -n sched-lab scale deployment ballast --replicas=2
   grep -c 'Attempting to schedule pod.*waiter' /tmp/hints.log
   ```

5. **Attribute the moves.** The counter carries the triggering event as a label:

   ```sh
   kubectl get --raw /metrics | grep '^scheduler_queue_incoming_pods_total' > /tmp/incoming-after.txt
   diff /tmp/incoming-before.txt /tmp/incoming-after.txt
   ```

6. Read [KEP-4247](../../strands/source-reading.md#area-3-scheduler) for the problem statement, and answer the module's question: what did the scheduler do before hints existed, and what does that cost on a cluster with a large unschedulable backlog and a busy node population?

**Observe** — the two attempt counts, and which event labels moved in the counter diff.

**Expect** — the label churn to produce **no** additional scheduling attempts for `waiter`, and the single scale-down to produce one. The counter diff should show the node-update event arriving and being accounted for without moving your pod: **the event was delivered and the hint declined it**, which is a different thing from the event not happening, and the counter is where you can tell them apart.

Expect the answer to step 6 to be an amplification argument: without hints, every node update moves the entire unschedulable set back for a retry, so a cluster with a thousand stuck pods and a node whose status updates every ten seconds spends its scheduler doing nothing else. That is the failure mode the KEP names, and it is the same shape as the hot loop [P4 measured on a workqueue](../../phases/04-controllers.md#m4-2) — a retry policy that is correct and unaffordable.

Expect the watched-resource list from step 2 to include things with no obvious connection to placement. For each surprise, name the plugin that must have asked for it. If you cannot, you have found a plugin you have not read.

**Write down** — the two counts, the counter diff, the `EventsToRegister` declaration and hint verdict with `file:line`, the full watched-resource list, and the amplification paragraph.

**Footprint note** — label writes and one scale. No new pods beyond `waiter`. 7.5GB total.

**Teardown**

```sh
kubectl label node <worker-node> academy.k3ii.dev/churn-
kubectl -n sched-lab delete pod waiter --ignore-not-found
rm /tmp/incoming-*.txt
```

**The topology stays.**
