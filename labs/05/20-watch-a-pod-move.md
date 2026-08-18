<a id="watch-a-pod-move"></a>
# A pod moving between queues, timed against your own prediction

**Claim** — the scheduler exposes which queue every pending pod is in as a metric, and a pod moves from the unschedulable set to running **within a second** of the cluster event that makes it schedulable — three orders of magnitude faster than the periodic flush, which proves the event path is the mechanism and the flush is the net.

**Rests on** — [the state machine and the three predictions](19-three-queues-and-two-exits.md). This scores the first and third of them.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Setup** — find the metric that names the queues, so you are watching the scheduler's own accounting rather than inferring from pod phases:

```sh
kubectl get --raw /metrics | grep -E '^scheduler_pending_pods'
```

Fill the worker until one more pod cannot fit. Use a Deployment so you can free capacity with one `scale`:

```sh
kubectl -n sched-lab apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata: {name: ballast}
spec:
  replicas: 3
  selector: {matchLabels: {app: ballast}}
  template:
    metadata: {labels: {app: ballast}}
    spec:
      containers:
      - name: pause
        image: registry.k8s.io/pause:3.9
        resources: {requests: {cpu: 500m}}
EOF
```

Adjust `replicas` and `cpu` until the node reports nearly no allocatable CPU left — [the accounting you read](15-the-line-that-writes-insufficient-cpu.md) is what you are filling, not the node's actual load.

**Do**

1. Start a metrics watch in one session:

   ```sh
   while :; do date +%T; kubectl get --raw /metrics | grep -E '^scheduler_pending_pods'; sleep 1; done
   ```

2. Submit the pod that cannot fit, and confirm it lands in the unschedulable set rather than anywhere else:

   ```sh
   kubectl -n sched-lab run waiter --image=registry.k8s.io/pause:3.9 --restart=Never \
     --overrides='{"spec":{"containers":[{"name":"pause","image":"registry.k8s.io/pause:3.9","resources":{"requests":{"cpu":"600m"}}}]}}'
   ```

3. Leave it there for **five minutes without touching anything**, watching the metric. This is the boring step and it is the one that scores prediction three: does the pod get retried on its own, and does the count move between queues while nothing in the cluster changes?

4. Now free the capacity and time the move to the millisecond:

   ```sh
   date +%T.%N; kubectl -n sched-lab scale deployment ballast --replicas=1
   kubectl -n sched-lab get pod waiter -o wide -w
   ```

5. Get the scheduler's own view of the same moment:

   ```sh
   kubectl -n sched-lab describe pod waiter | sed -n '/Events/,$p'
   kubectl get --raw /metrics | grep -E 'scheduler_pod_scheduling_attempts|scheduler_queue_incoming_pods_total' | head -20
   ```

**Observe** — the queue gauge over the whole five minutes, the elapsed time between the `scale` and the pod having a node, and the `scheduler_queue_incoming_pods_total` labels, which name the *event* that caused each move.

**Expect** — the pod to sit in the unschedulable gauge, to be moved out and back periodically without being scheduled (the flush, on the multi-minute cadence you read), and then to be scheduled within a second or so of the `scale`. Time both. The ratio between them is the finding.

Expect `scheduler_queue_incoming_pods_total` to carry an event label naming *what kind of cluster change* moved the pod, and expect the label on the fast move to name a pod deletion rather than a node change — the node did not change at all; other pods left it. That distinction is the whole subject of [exercise 23](23-the-hint-that-decides-a-retry.md).

Expect the `FailedScheduling` event on the pod **not** to be repeated once per retry. Events are aggregated, and a pod that has been retried forty times may show a count rather than forty lines. If you conclude from the event list that the scheduler stopped trying, you have been fooled by aggregation — the metric is the truth here, and picking the right one of two sources is worth more than the measurement.

**Write down** — predictions one and three scored against measured numbers, the event label from the fast path, and one sentence on why the flush exists given how much slower it is.

**Footprint note** — four small pause pods on `pair`. The five-minute wait in step 3 is real and unavoidable; it is the shortest way to observe a timer whose whole purpose is to be slower than everything else. 7.5GB total.

**Teardown** — leave `ballast` at 1 replica and `waiter` running; [the next exercise](21-the-backoff-you-can-time.md) refills from here. **The topology stays.**
