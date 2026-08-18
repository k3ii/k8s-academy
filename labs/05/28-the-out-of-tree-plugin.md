<a id="the-out-of-tree-plugin"></a>
# Build artifact 2: a scoring plugin compiled into a scheduler you own

**Artifact** — `build/05-plugin/`: an out-of-tree scheduler plugin built against `kubernetes-sigs/scheduler-plugins`, producing a `kube-scheduler` binary with your `Score` plugin linked in, published as an image in [the `forge` registry](../../strands/build-mechanics.md#registry). This is the compile step, and it is the **last thing in this phase that compiles anything** — [module 5.6 only runs images](33-forge-back-down-and-workhorse-up.md).

**Rests on** — [the plugin shape](05-the-smallest-plugin-that-exists.md) for the interface, [`CycleState`](14-state-without-globals.md) for where a `PreScore` result may live, and [the resized guest](07-fifteen-thirty-six-will-not-link-a-scheduler.md), without which this exercise is an OOM kill.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued, with [`forge` at 2560MB](07-fifteen-thirty-six-will-not-link-a-scheduler.md). The plugin is *built* here and *run* here in stage 1; [running it at scale](34-placement-that-differs-measurably.md) happens on another cluster from the registry.

**Build**

```
build/05-plugin/
  go.mod                     requires sigs.k8s.io/scheduler-plugins and k8s.io/kubernetes
  cmd/scheduler/main.go      app.NewSchedulerCommand(app.WithPlugin(concentrate.Name, concentrate.New))
  pkg/concentrate/
    plugin.go                the struct, Name(), New(), and the Score/NormalizeScore methods
    args.go                  the plugin's own configuration type, and its defaults
  Dockerfile
```

What it must satisfy:

1. **A `Score` plugin, not a `Filter` one.** A filter changes whether a pod can be placed; a score changes *where*, and "where" is what [module 5.6](34-placement-that-differs-measurably.md) can measure across three nodes. Implement `ScorePlugin`, and implement `ScoreExtensions` so the raw scores are normalised — a plugin that returns unnormalised scores is silently outweighed by every other plugin in the profile, which is the most common way a first plugin appears to do nothing.

2. **A rule whose effect is unmistakable.** Score a node by **how many pods carrying the incoming pod's own workload label already run on it**, and score *higher* for more. That is the deliberate inverse of what the default profile does, so the difference is visible with ten pods rather than requiring statistics. Take the label key from the plugin's own arguments, defaulting to `app`.

3. **Configuration through `KubeSchedulerConfiguration`.** The plugin's arguments arrive as a `pluginConfig` entry, decoded into your `args.go` type. Wiring this now is what makes [exercise 31](31-a-profile-not-a-binary.md) a deployment exercise rather than a code change.

4. **One deliberate refusal, kept behind an argument.** Add a `rejectEverything` boolean that, when set, makes the plugin also implement `Filter` and return an unschedulable status for every node. This is the reject-all plugin [that module 5.1 asked for](06-three-rejections-three-plugins.md) and that could not be built there; it costs four lines here and it gives you an event message with **your own plugin's name in it**, which is worth producing once.

5. **No state outside `CycleState`.** The pod's label value is computed once; where it lives is [the subject you already read](14-state-without-globals.md), and this is the exercise that cashes it in.

**Do**

```sh
cd ~/src/k8s-academy/build/05-plugin
go build -o /tmp/scheduler ./cmd/scheduler && ls -lh /tmp/scheduler
```

Then stage 1: run it as a **second scheduler from outside the cluster**, with a profile of its own, before any image exists:

```sh
cat > /tmp/profile.yaml <<'EOF'
apiVersion: kubescheduler.config.k8s.io/v1
kind: KubeSchedulerConfiguration
clientConnection:
  kubeconfig: /home/zain/.kube/config
leaderElection:
  leaderElect: false
profiles:
- schedulerName: concentrate-scheduler
  plugins:
    score:
      enabled: [{name: Concentrate, weight: 10}]
  pluginConfig:
  - name: Concentrate
    args: {labelKey: app}
EOF
/tmp/scheduler --config=/tmp/profile.yaml -v=4
```

```sh
kubectl -n sched-lab create deployment spread --image=registry.k8s.io/pause:3.9 --replicas=6 \
  --dry-run=client -o yaml \
  | sed 's/^      containers:/      schedulerName: concentrate-scheduler\n      containers:/' \
  | kubectl -n sched-lab apply -f -
kubectl -n sched-lab get pods -l app=spread -o wide | awk '{print $7}' | sort | uniq -c
```

**Gate** — [upstream's own framework test helpers](../../strands/build-mechanics.md#gates), which is this artifact's objective harness and the reason it has one where [artifact 1 does not](09-two-hundred-lines-that-schedule.md). Write a Go test that constructs a framework handle with the fake node informer helpers from `pkg/scheduler/framework/runtime` and the test utilities under `pkg/scheduler/testing`, then calls your `Score` directly with a hand-built pod and node set:

```sh
grep -rn 'func NewFramework\|WithSnapshotSharedLister\|func MakeNode\|func MakePod' pkg/scheduler/framework/runtime/framework.go pkg/scheduler/testing/*.go | head
go test ./pkg/concentrate/... -count=1 -v
```

Assert three things: a node with more matching pods scores higher; normalisation maps your raw range onto the framework's; and the empty-cluster case returns equal scores rather than an error. **Make one of them fail on purpose and watch it fail** — a gate nobody has watched fail is not evidence.

**Verify from outside** — build and push the image, then confirm the registry has it, because [module 5.6 has nothing to build with](33-forge-back-down-and-workhorse-up.md) if this step was skipped:

```sh
docker buildx build --platform linux/amd64 -t forge.lab:5000/academy/concentrate-scheduler:v1 --push .
curl -s http://forge.lab:5000/v2/academy/concentrate-scheduler/tags/list
```

**Expect** — six pods on one node where the default profile would have put three on each. Expect the effect to be strong but not absolute: your plugin is one score among several, its weight is one number in the profile, and the resource-based scorers still have opinions. If the placement does not change at all, check normalisation before checking your logic — that is the failure this exercise predicts in requirement 1.

Expect the link to be the slow part and to sit near the peak [the strand measured](../../strands/build-mechanics.md#measurements). Expect the image to be large; [the base image discussion](../../strands/build-mechanics.md#base-image) applies unchanged, and the registry has room.

**Write down** — [the module's write-down](../../phases/05-scheduler.md#m5-5): the extension point your plugin implements and the `interface.go` line declaring it. Plus the image tag, and the placement counts with and without your profile.

**Footprint note** — the phase's heaviest single moment: a `kube-scheduler` link on a 2560MB guest, with `pair` at 5.0GB — **7.5GB against [the 9.5GB ceiling](../../strands/lab-topologies.md#ceiling), 2.0GB of margin**. Do not run [the perf harness](17-a-hundred-nodes-that-do-not-exist.md) or a second build concurrently.

Disk is tighter than RAM here. A second k/k-scale module graph now exists alongside the first; check before continuing:

```sh
df -h /; du -sh ~/go/pkg/mod ~/.cache/go-build
```

**Teardown** — stop the stage-1 scheduler, `kubectl -n sched-lab delete deployment spread`, `rm /tmp/scheduler`. **Keep the image in the registry** — it is the only artifact that survives into module 5.6, and rebuilding it there is impossible. **The topology stays.**
