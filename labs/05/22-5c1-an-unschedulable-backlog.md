<a id="5c1-an-unschedulable-backlog"></a>
# 5.C1 — fifty pods that will not schedule, diagnosed from the outside

**Claim** — a backlog of unschedulable pods is fully diagnosable without reading scheduler source or logs: the pod events name the plugin, the metrics name the queue and the count, and together they distinguish *"the cluster is full"* from *"these pods ask for something no node has"* — which are the same symptom and different incidents. And when capacity returns, the backlog drains in one stampede whose shape you can predict.

**Rests on** — [the queue metrics](20-watch-a-pod-move.md) and [the rejection strings](06-three-rejections-three-plugins.md). This is [drill 5.C1](../../phases/05-scheduler.md#chaos), and the thread it pulls is the event message you first produced ten exercises ago.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Setup** — have someone else, or a coin, choose **one** of three causes without telling you which, and apply it. If you are working alone, write the three on slips and draw one, then leave it for a day:

- **A.** Scale `ballast` until the worker's allocatable CPU is exhausted.
- **B.** Give every submitted pod a `nodeSelector` for a label no node carries.
- **C.** Taint both nodes with a taint the submitted pods do not tolerate.

Then submit the backlog:

```sh
kubectl -n sched-lab create deployment backlog --image=registry.k8s.io/pause:3.9 --replicas=50
```

**Do** — diagnose against a clock, and write the time at each step.

1. Establish the scale of the incident before the cause. Metrics only:

   ```sh
   kubectl get --raw /metrics | grep -E '^scheduler_pending_pods|^scheduler_unschedulable_pods'
   ```

2. Name the cause from a **single** pod:

   ```sh
   kubectl -n sched-lab get pods --field-selector spec.nodeName= -o name | head -1
   kubectl -n sched-lab describe pod <that one> | sed -n '/Events/,$p'
   ```

   Stop and commit to an answer of A, B or C in writing before step 3. The clause counts in that message — how many nodes each reason accounted for — are what separate them.

3. Confirm without guessing, using the check that matches your answer, and only that one:

   ```sh
   kubectl describe node <worker-node> | sed -n '/Allocated resources/,/^Events/p'   # for A
   kubectl get nodes --show-labels                                                    # for B
   kubectl get nodes -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints        # for C
   ```

4. State the smallest change that clears the backlog, then make it, and **time the drain**:

   ```sh
   date +%T.%N
   # the single change
   kubectl -n sched-lab get pods --field-selector spec.nodeName= -w
   ```

5. Watch the drain as a rate, not an outcome:

   ```sh
   while :; do date +%T; kubectl -n sched-lab get pods --field-selector spec.nodeName= --no-headers | wc -l; sleep 1; done
   ```

**Observe** — the time from backlog to named cause, the queue gauge before and during the drain, and the pods-per-second of the drain itself.

**Expect** — a diagnosis in under two minutes, because the event message is unusually good: it names the plugin and it counts nodes. Expect cause A and cause C to produce visibly different sentences, and expect the count clauses to give away which is which even before you check the node.

Expect the drain to be fast and **not instant**, and expect the rate to be limited by the same serial scheduling cycle [you measured](13-why-the-bind-is-async.md), not by anything in the queue. Fifty pods do not schedule simultaneously; they schedule one after another at whatever the cycle costs, and the whole backlog clears in a small number of seconds on two nodes.

Expect the pods that fitted to be placed in an order you cannot control and should not care about. If more pods fit than nodes have room for, expect the tail to stay pending with the same message — the backlog shrank, it did not vanish, and reporting "resolved" on a partial drain is the operational mistake this drill inoculates against.

**Write down** — the drawn cause, your committed answer, the time to diagnosis, the smallest change, and the drain rate in pods per second. Add one sentence naming what would have made this diagnosis *hard*: a cause that produces a message you do not recognise, which is what [the next exercise](23-the-hint-that-decides-a-retry.md) and [24](24-a-pod-that-is-never-considered.md) both supply.

**Footprint note** — fifty pause pods requested at once on a two-node cluster. Almost all stay `Pending`, which costs the API server and etcd a little and costs the nodes nothing — a pending pod is an object, not a process. If cause A is drawn, `ballast` is what fills the node, and that is the only variant that puts real containers on it. 7.5GB total.

**Teardown**

```sh
kubectl -n sched-lab delete deployment backlog
kubectl uncordon <cp-node> <worker-node> 2>/dev/null
kubectl taint node <worker-node> <the drill taint>- 2>/dev/null
kubectl get nodes -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints,UNSCHED:.spec.unschedulable
```

That last line is the check that matters: a taint left on from cause C makes every later exercise in this phase fail for a reason you have stopped suspecting. **The topology stays.**
