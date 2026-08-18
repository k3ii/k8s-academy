<a id="a-profile-not-a-binary"></a>
# Stage 2, shape two: one process answering to two scheduler names

**Artifact** — [your plugin's binary](28-the-out-of-tree-plugin.md) deployed in-cluster with a `KubeSchedulerConfiguration` carrying **two profiles**: one that behaves like the default and one that enables your plugin. Same process, same cache, two `schedulerName` values, and a demonstrable difference in placement between pods that name one and pods that name the other.

**Rests on** — [the plugin](28-the-out-of-tree-plugin.md) and [the flag-to-config mapping](16-the-knob-that-cannot-move-here.md) you wrote when you first gave the real scheduler a config file. This is the second of the two deployment shapes; [the first](30-a-second-scheduler-by-schedulername.md) was a separate binary with a name of its own, and the contrast between them is the exercise.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Do**

1. Read [KEP-1451](../../strands/source-reading.md#area-3-scheduler) and the profile package, and answer the question that decides the whole design: what is shared between two profiles in one scheduler, and what is not?

   ```sh
   ls pkg/scheduler/profile/
   grep -n 'func NewMap\|type Map\|frameworkFactory' pkg/scheduler/profile/profile.go
   grep -n 'Profiles\[\|sched.Profiles' pkg/scheduler/schedule_one.go | head
   ```

   The answer has two halves — one about the framework instances and one about the informers, the cache and the queue — and getting the second half wrong is what leads people to deploy three schedulers where one would do.

2. Write the two-profile configuration:

   ```yaml
   apiVersion: kubescheduler.config.k8s.io/v1
   kind: KubeSchedulerConfiguration
   leaderElection:
     leaderElect: false
   profiles:
   - schedulerName: academy-default
   - schedulerName: academy-concentrate
     plugins:
       score:
         enabled: [{name: Concentrate, weight: 10}]
     pluginConfig:
     - name: Concentrate
       args: {labelKey: app}
   ```

   Ship it as a ConfigMap, mount it, and run the image you pushed in [exercise 28](28-the-out-of-tree-plugin.md) as a Deployment in `academy-build` with its own ServiceAccount. **Do not reuse the ClusterRole from [exercise 30](30-a-second-scheduler-by-schedulername.md)** — a framework scheduler needs a good deal more than a hand-written one, and finding out how much more is step 3.

3. Start it with too few permissions on purpose, read the errors, and add rules until it runs. Then compare:

   ```sh
   kubectl -n academy-build logs -l app=concentrate-scheduler --tail=40
   kubectl get clusterrole toy-scheduler -o jsonpath='{.rules}' | tr ',' '\n' | wc -l
   kubectl get clusterrole concentrate-scheduler -o jsonpath='{.rules}' | tr ',' '\n' | wc -l
   ```

   There is a shortcut, and it is worth looking at before you decide not to take it: the cluster already has a ClusterRole for the real scheduler. Look at it, and say in one line why binding to it would have taught you nothing:

   ```sh
   kubectl get clusterrole system:kube-scheduler -o yaml | head -40
   ```

4. Drive both profiles from one process:

   ```sh
   for p in academy-default academy-concentrate; do
     kubectl -n sched-lab create deployment $p --image=registry.k8s.io/pause:3.9 --replicas=6 \
       --dry-run=client -o yaml \
       | sed "s/^      containers:/      schedulerName: $p\n      containers:/" \
       | kubectl -n sched-lab apply -f -
   done
   kubectl -n sched-lab get pods -o wide | awk '{print $1, $7}' | sort -k2
   ```

5. Confirm it really is one process:

   ```sh
   kubectl -n academy-build get pods
   kubectl -n academy-build logs -l app=concentrate-scheduler | grep -c 'academy-default\|academy-concentrate'
   ```

6. Now the comparison that makes this a separate exercise from [30](30-a-second-scheduler-by-schedulername.md). Fill in a four-row table for the two shapes: **what you had to write**, **what the API server sees**, **what happens to pods when it is down**, and **what it costs to add a third behaviour**. Give a verdict per row.

**Observe** — the placement of the twelve pods split by profile, the two ClusterRole sizes, and the pod count in `academy-build`.

**Expect** — six pods spread and six pods concentrated, decided inside a single process that keeps one informer set, one cache and one queue. That sharing is the answer to step 1 and it is the reason profiles exist at all: **two schedulers means two caches and two chances to disagree about a node; two profiles means one cache and no disagreement possible.**

Expect the framework scheduler's ClusterRole to be several times the hand-written one's. Your scheduler read pods and nodes; this one runs [the default plugin set](04-what-actually-runs-by-default.md), and those plugins read storage objects, topology labels, disruption budgets and more. **The permission list is a readable summary of what the default profile actually looks at**, which is a better answer to "what does the scheduler do" than most prose.

Expect step 6's last row to be the decisive one: a third behaviour is a new profile stanza in a ConfigMap here, and a new image, Deployment, ServiceAccount and ClusterRole there.

**Write down** — the answer to step 1, the two ClusterRole sizes with three examples of what the larger one has that the smaller does not, the placement split, and the four-row comparison table with verdicts.

**Footprint note** — a second scheduler process inside `pair`, with the default plugin set and its informers, which is a heavier resident than [artifact 1](30-a-second-scheduler-by-schedulername.md). It fits comfortably; nothing compiles. 7.5GB total.

**Teardown** — `kubectl -n sched-lab delete deployment academy-default academy-concentrate`. Leave the scheduler Deployment and its ConfigMap; [the next exercise](32-the-lease-changes-hands.md) needs both. **The topology stays.**
