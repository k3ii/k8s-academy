<a id="placement-that-differs-measurably"></a>
# The same workload, two profiles, three nodes, two distributions

**Artifact** — a placement measurement across three nodes: the same Deployment scheduled by the default profile and by your plugin's profile, with the per-node counts, repeated enough times to say the difference is the plugin rather than the order pods happened to arrive in.

**Rests on** — [the plugin image](28-the-out-of-tree-plugin.md) and [the two-profile deployment shape](31-a-profile-not-a-binary.md), both of which you built on a two-node cluster where the measurement was not worth taking. This is the module that [earns the third node](../../strands/build-mechanics.md#p5-split).

**Topology** — [`workhorse`](../../strands/lab-topologies.md#workhorse), continued from [the provision](33-forge-back-down-and-workhorse-up.md). Two schedulable workers with **one core each**.

**Setup** — deploy the plugin scheduler from the registry, using the same ConfigMap and RBAC shape as [exercise 31](31-a-profile-not-a-binary.md). Nothing is built; the image and the manifests come across unchanged:

```sh
kubectl -n academy-build get deploy,cm
kubectl -n academy-build logs -l app=concentrate-scheduler --tail=10
```

**Do**

1. **Predict the two distributions in writing** before submitting anything, with a number per node for each profile. You wrote what your plugin scores, and you have [the default set's scoring](04-what-actually-runs-by-default.md) on paper; this is a prediction you have the information to get right.

2. **Baseline, on an empty cluster**, and repeat it. One run is an anecdote:

   ```sh
   for run in 1 2 3; do
     kubectl -n sched-lab create deployment base-$run --image=registry.k8s.io/pause:3.9 --replicas=8 \
       --dry-run=client -o yaml \
       | sed 's/^      containers:/      schedulerName: academy-default\n      containers:/' \
       | kubectl -n sched-lab apply -f -
     sleep 15
     kubectl -n sched-lab get pods -l app=base-$run -o wide --no-headers | awk '{print $7}' | sort | uniq -c
     kubectl -n sched-lab delete deployment base-$run
     sleep 10
   done
   ```

3. **The same three runs against your profile**, with `academy-concentrate` substituted and nothing else changed.

4. **Now under contention**, which is the case that matters and the one two nodes could not produce. Give the pods a request large enough that a node holds only a few, and run both profiles again:

   ```sh
   kubectl -n sched-lab create deployment load --image=registry.k8s.io/pause:3.9 --replicas=6 \
     --dry-run=client -o yaml \
     | sed 's/^      containers:/      schedulerName: academy-concentrate\n      containers:/' \
     | sed 's/^        image: registry.k8s.io\/pause:3.9/        image: registry.k8s.io\/pause:3.9\n        resources: {requests: {cpu: 300m}}/' \
     | kubectl -n sched-lab apply -f -
   kubectl -n sched-lab get pods -l app=load -o wide
   ```

5. **Find where your plugin lost an argument.** Some pods will be placed against your plugin's preference, because it is one weighted score among several. Read the scores directly:

   ```sh
   kubectl -n academy-build logs -l app=concentrate-scheduler | grep -iE 'score|plugin' | tail -30
   ```

   Then change the weight in the ConfigMap from 10 to 1, restart, and re-run step 4. Record the placement at both weights.

6. Answer the question the two weights raise: at weight 1, is your plugin *wrong*, or merely *outvoted*? Say which score outvoted it and what that score is protecting.

**Observe** — six distributions (two profiles × three runs), the contended distributions at two weights, and the per-node allocatable CPU as it fills.

**Expect** — the default profile to spread nearly evenly across the two workers and your plugin to concentrate, with the difference obvious at eight pods and unambiguous over three runs. Expect a little variation between runs of the *same* profile, and expect it to be much smaller than the difference between profiles — that comparison is what makes this a measurement.

Expect the contended case to be the more interesting one. Concentration and capacity fight: your plugin wants the loaded node, the resource scorer wants the empty one, and the winner is decided by the weights. **A scoring plugin does not decide placement; it bids for it.** Getting a number for that bid is the point of step 5.

Expect the control-plane node to receive nothing throughout, and expect that to be a filter result rather than a score result. Confirm which — it is a one-line check against [the rejection strings](06-three-rejections-three-plugins.md) and it is the difference between "no node wanted it" and "the node was never a candidate".

**Write down** — your predictions scored against the measured distributions, the six baseline runs, the two contended runs with their weights, and the answer to step 6. [The capstone](37-the-capstone-narrative.md) uses the contended numbers.

**Footprint note** — up to fourteen pause pods on two single-core workers, deliberately requesting enough to contend. `workhorse` 7.0GB plus `forge` 1536MB = 8.5GB, **1.0GB of margin** — the phase's tightest. Nothing compiles; `forge` is a registry and a shell.

**Teardown** — `kubectl -n sched-lab delete deployment --all` and confirm both workers report their full allocatable CPU free before starting the drill:

```sh
kubectl describe node <worker-1> <worker-2> | grep -A6 'Allocated resources'
```

A leftover 300m request makes [5.C2](35-5c2-preemption-with-real-victims.md) preempt something you did not intend. Leave the plugin scheduler running. **The topology stays.**
