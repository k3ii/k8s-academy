<a id="the-backoff-you-can-time"></a>
# Attempt 1, 3 and 6: the gaps double until they stop

**Claim** — a pod that keeps failing to schedule is retried on a doubling delay from an initial value to a cap, both of which you read from the source before measuring; the delay is per-pod, it resets on success, and the observable is the gap between consecutive attempts in the scheduler's own log.

**Rests on** — [the state machine](19-three-queues-and-two-exits.md) — this scores its second prediction — and [the pod already waiting](20-watch-a-pod-move.md).

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Setup** — the real scheduler at `--v=4`, not `10`: attempt lines are logged at 4 and the volume at 10 would bury them.

```sh
ssh zain@10.10.10.130 "sudo sed -i 's|- --leader-elect=true|- --leader-elect=true\n    - --v=4|' /etc/kubernetes/manifests/kube-scheduler.yaml"
kubectl -n kube-system logs -f -l component=kube-scheduler --tail=0 > /tmp/backoff.log &
```

Refill the worker so `waiter` cannot fit: `kubectl -n sched-lab scale deployment ballast --replicas=3`.

**Do**

1. Burn attempts on purpose. Each pod that leaves a node is an event that makes the scheduler reconsider `waiter`, and each reconsideration fails:

   ```sh
   for i in $(seq 1 8); do
     kubectl -n sched-lab run churn-$i --image=registry.k8s.io/pause:3.9 --restart=Never
     sleep 2
     kubectl -n sched-lab delete pod churn-$i --wait=false
     sleep 3
   done
   ```

2. Extract the attempt timestamps for that one pod and take the differences:

   ```sh
   grep 'Attempting to schedule pod' /tmp/backoff.log | grep waiter \
     | awk '{print $2}' | cat -n
   ```

   Compute the gaps by hand. Six numbers is not a script's job.

3. Compare against the constants you already wrote down, and check the shape rather than the exact values: does gap N roughly double gap N−1, and where does it stop growing?

4. Confirm the reset. Free the capacity, let `waiter` schedule, then make it unschedulable again and check whether the first retry is back at the initial delay:

   ```sh
   kubectl -n sched-lab scale deployment ballast --replicas=1
   kubectl -n sched-lab get pod waiter -o wide
   ```

5. Find the per-pod bookkeeping in the source, because "per-pod" is the claim most easily got wrong:

   ```sh
   grep -n 'Attempts\|backoffDuration\|calculateBackoffDuration' pkg/scheduler/backend/queue/backoff_queue.go
   ```

   Answer: where is the attempt count stored, and what resets it?

6. Answer the module's comparison question in one paragraph. [P4's workqueue](../../phases/04-controllers.md#m4-2) had the same doubling shape with different constants and a different failure model. Say what the scheduler's version protects that the workqueue's does not, and why the scheduler needs *both* a backoff and a separate unschedulable set when a workqueue makes do with one structure.

**Observe** — the six gaps, the cap, and the first gap after the reset.

**Expect** — gaps that double from a sub-second start to a cap in the seconds, not the minutes. Expect the cap to be reached in a handful of attempts, which is the design point: the backoff is meant to stop a hot loop, not to give up. A pod that has been failing for an hour is still being retried on that cap and will schedule promptly when the cluster changes — which you already saw in [the previous exercise](20-watch-a-pod-move.md) without yet having the reason it was still fast.

Expect the attempt count to be attached to the pod's entry in the queue and to disappear with it, so a scheduler restart resets everyone's backoff. Note that consequence: **restarting the scheduler is a way to make a stuck cluster retry everything immediately**, which is a real operational lever and also a real way to cause a thundering herd.

Expect step 1 to be fiddly, and expect some churn pods to schedule rather than staying pending. That does not matter — what generates the retry is the *deletion*, and every iteration produces one.

**Write down** — the gap table, prediction two scored, the answer to step 5 with `file:line`, and the comparison paragraph from step 6.

**Footprint note** — eight short-lived pause pods, created and deleted one at a time. Set the scheduler's verbosity back in the teardown; `--v=4` is far cheaper than `10` but this exercise runs for several minutes. 7.5GB total.

**Teardown**

```sh
kubectl -n sched-lab delete pod --all --ignore-not-found
ssh zain@10.10.10.130 'sudo cp /root/kube-scheduler.yaml.bak /etc/kubernetes/manifests/kube-scheduler.yaml'
```

Restoring the backup also removes [the `--config` plumbing](16-the-knob-that-cannot-move-here.md) if that is what the backup predates — check, and re-apply the config file if so, because [exercise 31](31-a-profile-not-a-binary.md) builds on it. Keep the `ballast` Deployment at 1 replica; [the drill](22-5c1-an-unschedulable-backlog.md) scales it. **The topology stays.**
