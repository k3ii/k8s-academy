<a id="cpu-max-and-the-throttle-counter"></a>
# A CPU limit is a quota per period, and the counter that proves you set it too low

**Claim** — `limits.cpu` becomes two integers in one file, and a container that wants more CPU than its quota is not slowed smoothly — it is stopped dead for the rest of each period. The counter that records this is per-container, free to read, and almost never looked at.

**Rests on** — [the cgroup tree](15-the-cgroup-tree-under-one-pod.md) for the path; the `cgroups` namespace should still be up.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued. Worker `.131`, which has 2 cores — a number you will need.

**Do**

1. **Predict the two integers.** For a container with `limits.cpu: 100m`, what appears in `cpu.max`? Write down both values and the unit of each before looking.

   ```sh
   kubectl -n cgroups apply -f - <<'EOF2'
   apiVersion: v1
   kind: Pod
   metadata: {name: burner}
   spec:
     nodeName: pair-worker
     containers:
     - name: c
       image: busybox:1.36
       command: ["sh","-c","while :; do :; done"]
       resources: {requests: {cpu: 100m}, limits: {cpu: 100m}}
   EOF2
   ```

2. Read them, and watch the counter that is about to move:

   ```sh
   ssh zain@10.10.10.131 'CG=<the burner pod cgroup path>; \
     cat $CG/cpu.max; \
     for i in 1 2 3 4 5 6; do cat $CG/cpu.stat | tr "\n" " "; echo; sleep 5; done'
   ```

3. Compare with what the cluster reports for the same container:

   ```sh
   kubectl get --raw "/api/v1/nodes/pair-worker/proxy/metrics/cadvisor" \
     | grep -e 'container_cpu_cfs_throttled_periods_total{.*pod="burner"' \
            -e 'container_cpu_cfs_periods_total{.*pod="burner"'
   ```

4. Raise the limit to `1` and repeat step 2 without changing anything else about the workload.

**Observe** — the ratio `nr_throttled / nr_periods`, sampled twice, at both limits. That ratio is the honest measure of "is this limit hurting", and it is the number to reach for when a service is slow and its CPU usage graph looks comfortably below its limit — which it always does, because the average hides the stops.

**Expect** — a busy loop capped at `100m` to be throttled in nearly every period, with `throttled_usec` accumulating at close to 90% of wall-clock, while `container_cpu_usage_seconds_total` shows a perfectly well-behaved 0.1 core. Both numbers are true. **The usage graph is the one everyone looks at and the throttle counter is the one that answers the question.**

At `limits.cpu: 1` on a 2-core node, expect the throttling to stop almost entirely — the loop is single-threaded and now fits inside its quota.

Expect the period to be the same at both limits: only the quota moved. That is why a multi-threaded process with a small limit throttles far harder than the arithmetic suggests — several threads spend the same quota in a fraction of the period and then all wait together.

**Write down** — the predicted and actual `cpu.max` at both limits, the two throttle ratios, and one sentence contrasting a CPU limit with a memory limit: one of them is enforced by waiting and the other by killing, and that asymmetry decides which one is safe to set aggressively.

**Footprint note** — a busy loop on a 2-core worker for about a minute. It is limited, so it cannot starve the kubelet, but do not leave it running: an unlimited version of this pod is a genuinely effective way to make the node miss its heartbeats, which is [exercise 21's](21-two-heartbeats-two-frequencies.md) subject and should arrive there deliberately.

**Teardown**

```sh
kubectl delete ns cgroups
```

**The topology stays.**
