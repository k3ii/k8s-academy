<a id="5c4-two-schedulers-one-pod"></a>
# 5.C4 — two schedulers, one pod: the race, then the recovery

**Claim** — two schedulers claiming the same pods do not corrupt anything, because the loser of every race gets a `409` from the `binding` subresource; and a scheduler killed between deciding and binding loses nothing, because on restart it re-lists and the pod is still unbound. Both halves are properties of the *API*, not of the scheduler, and neither is true of a scheduler that has written its decision down somewhere else first.

**Rests on** — [the from-scratch scheduler](09-two-hundred-lines-that-schedule.md) and [the 409](08-bind-a-pod-with-one-post.md) you already produced by hand. This is [drill 5.C4](../../phases/05-scheduler.md#chaos), and it is the phase's cheapest drill: it needs two nodes and no scale at all.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Setup** — stop your scheduler and restart it under the *default scheduler's own name*, so that both programs believe every pod in the cluster is theirs:

```sh
kubectl -n sched-lab delete deployment mine
go run ./cmd/toy-scheduler --kubeconfig=$HOME/.kube/config \
  --scheduler-name=default-scheduler -v=4 2>&1 | tee /tmp/toy.log
```

Write the prediction down **before** the first pod. Three questions, three answers, in ink:

1. Will any pod end up running on two nodes?
2. Will any pod be bound twice, and if the second bind is refused, by whom?
3. Which of the two schedulers will win more often, and why?

**Do**

1. **The race.** Submit a burst with no `schedulerName` at all, so both take it:

   ```sh
   kubectl -n sched-lab create deployment race --image=registry.k8s.io/pause:3.9 --replicas=20
   kubectl -n sched-lab get pods -o wide | awk '{print $7}' | sort | uniq -c
   ```

2. **Count the losses on both sides.** Yours is in your own log; the real one is in its container's:

   ```sh
   grep -ci 'conflict\|already assigned' /tmp/toy.log
   ssh zain@10.10.10.130 'sudo crictl logs $(sudo crictl ps -q --name kube-scheduler) 2>&1 | grep -ci "conflict\|already assigned"'
   ```

3. **Check for the thing that would actually be a bug**: a pod whose `spec.nodeName` disagrees with the node its container is running on, or two containers for one pod on two nodes.

   ```sh
   kubectl -n sched-lab get pods -o custom-columns=NAME:.metadata.name,NODE:.spec.nodeName,HOST:.status.hostIP
   ssh zain@10.10.10.131 'sudo crictl ps --name pause -o json | grep -c sandboxID'
   ```

4. **The recovery half.** Delete the Deployment, restart your scheduler, and this time kill it in the middle of a burst:

   ```sh
   kubectl -n sched-lab delete deployment race
   kubectl -n sched-lab create deployment burst --image=registry.k8s.io/pause:3.9 --replicas=30
   # in the scheduler's session, within the first second:
   # Ctrl-\  (SIGQUIT — a stack dump, and it dies where it was)
   ```

5. Read the stack dump for which function it was in, then look at the cluster with **nothing** scheduling for your pods:

   ```sh
   kubectl -n sched-lab get pods --field-selector spec.nodeName= | wc -l
   ```

6. Restart it and time the catch-up:

   ```sh
   time go run ./cmd/toy-scheduler --kubeconfig=$HOME/.kube/config --scheduler-name=default-scheduler -v=4
   ```

**Observe** — the two conflict counts from step 2, the placement distribution, and how long after restart the last unbound pod gets a node.

**Expect** — no pod on two nodes, ever. Both schedulers bind; the second bind of each pod is refused with the same `409` you produced by hand, and the count of refusals on the two sides adds up to roughly the number of pods. **The API server is the arbiter and there is no coordination anywhere else** — no lock, no lease, no agreement between the two programs.

Expect the win ratio to be lopsided and to have a mundane cause: whichever program does less work per pod gets there first. Yours checks two resources; the real one runs a dozen plugins. A worse scheduler is a faster one, which is a sentence worth keeping for [module 5.3](12-one-pod-through-schedule-one.md).

Expect the kill to cost nothing. The pods that had been decided but not bound are indistinguishable from pods that were never looked at, because **the decision existed only in a local variable**. On restart the informer lists them and they are scheduled. This is the same level-triggered property you produced against a dead control plane in [3.C4](../../phases/03-api-machinery.md#chaos), now from the other side, and it is why a scheduler needs no write-ahead log.

Expect one asterisk, and find it: the real scheduler *does* keep state across a decision — its cache of assumed pods — and losing that is not free. What it costs is [the next exercise](11-what-assume-buys.md).

**Write down** — your three predictions with the answers beside them, the two conflict counts, the win ratio with its cause, and one sentence on what a scheduler would have to do to make a crash mid-cycle expensive.

**Footprint note** — thirty pause pods on a two-node cluster is inside `pair`'s capacity but not by a lot; if pods stay `Pending` with an `Insufficient` message, that is a real resource limit and not a bug in the drill. `pair` 5.0GB, `forge` 2560MB, 2.0GB margin.

**Teardown** — `kubectl -n sched-lab delete deployment burst`, stop the scheduler, and confirm no pod is left unbound: `kubectl -n sched-lab get pods --field-selector spec.nodeName=`. Restart it under its own `--scheduler-name` default before moving on, or [the next exercise](11-what-assume-buys.md) measures the wrong program. **The topology stays.**
