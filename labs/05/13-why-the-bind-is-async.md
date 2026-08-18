<a id="why-the-bind-is-async"></a>
# Pod B is being scheduled while pod A is still being bound

**Claim** — in one scheduler's log, the "attempting to schedule" line for one pod appears **before** the "successfully bound" line of the pod before it, and this is not a logging artefact: the scheduling cycle is strictly serial and the binding cycle is not, so the two overlap by design. The serial part is what makes the scheduler's decisions consistent; the overlapping part is what stops API latency from setting its throughput.

**Rests on** — [the annotated single-pod log](12-one-pod-through-schedule-one.md). You have one pod's path on paper; this is what two look like when they are in flight together.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued, with `--v=10` put back on the real scheduler for the length of this exercise only.

**Setup** — same manifest edit as [the previous exercise](12-one-pod-through-schedule-one.md), and the same backup. Before the burst, capture the metrics baseline:

```sh
kubectl get --raw /metrics | grep -E '^scheduler_.*duration_seconds_count' | sort
```

**Do**

1. Predict first, in one line each: with N pods submitted at once, will the scheduler's total wall time be closer to N × (decide + bind), or to N × decide + one bind?

2. Burst, small enough that every pod fits:

   ```sh
   kubectl -n sched-lab create deployment overlap --image=registry.k8s.io/pause:3.9 --replicas=8
   ```

3. Extract the two lines per pod and sort them by time, ignoring which pod they belong to:

   ```sh
   grep -E 'Attempting to schedule pod|Successfully bound pod' /tmp/sched-burst.log \
     | sed -E 's/.*(Attempting|Successfully)[^"]*"pod"="([^"]+)".*/\1 \2/' | cat -n
   ```

4. Find the interleaving. You are looking for a line of the form *attempt B* sitting between *attempt A* and *bound A*. Mark every such crossing.

5. Confirm the serial half is genuinely serial: look for two *attempt* lines with no *bound* line between them and check whether the second pod's filtering could have started before the first pod's decision was made. Then find the mechanism in code:

   ```sh
   grep -n 'func (sched \*Scheduler) scheduleOne\|SchedulingQueue.Pop()' pkg/scheduler/schedule_one.go
   ```

   One pod is popped, and the function does not return until the scheduling cycle is done. That is the whole of the serialisation — there is no lock, because there is only one caller.

6. Now measure the two halves separately from the metrics, whose names tell you which is which:

   ```sh
   kubectl get --raw /metrics | grep -E '^scheduler_.*(binding|attempt|extension_point).*_sum|_count' | sort
   ```

**Observe** — the count of crossings from step 4, and the ratio of the binding histogram's mean to the scheduling attempt histogram's mean.

**Expect** — crossings on most pods, and a bind that costs several times what the decision costs. That ratio is the answer to step 1: the total is much closer to N × decide than to N × (decide + bind), and the difference is precisely what the `go` statement bought.

Expect the serialisation to be structural rather than defended by a mutex. A single goroutine calling `Pop` in a loop is why the scheduler can keep an internal cache without locking it against itself during the scheduling cycle — and why the *binding* cycle, which does run concurrently, has to be careful about exactly that cache. [The assumed-pods mechanism](11-what-assume-buys.md) is the thing living on that seam, which is a better reason to remember it than the one you had.

Expect one honest limitation of this measurement, and state it: on a two-node cluster with eight pods, the filter and score work is trivially small, so the ratio you measure exaggerates the bind's share compared with a real cluster. What survives the objection is the *ordering*, which is qualitative and does not care about scale.

**Write down** — your prediction, the crossing count, the two histogram means with the ratio, and the limitation above in your own words.

**Footprint note** — a second `-v=10` capture; the disk warning from [exercise 12](12-one-pod-through-schedule-one.md) applies unchanged and this exercise is the one that would actually fill `.130`, because a burst at `-v=10` writes far more than one pod does. Check `df -h /` on `.130` before and after.

**Teardown** — restore the manifest, `kubectl -n sched-lab delete deployment overlap`, and confirm disk. **The topology stays.**
