<a id="three-rejections-three-plugins"></a>
# Three ways to make every node refuse, and three different sentences

**Claim** — when no node fits, the event on the pod names *which* filter refused and *how many* nodes each refusal accounted for; the sentence is assembled from the `ErrReason` strings you just read, and you can produce any of them on demand by constructing the matching condition.

**Rests on** — [the three tiny plugins](05-the-smallest-plugin-that-exists.md). You have the strings written down; this is where they appear on a cluster. The event message is the thread [drill 5.C1](22-5c1-an-unschedulable-backlog.md) pulls.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), provisioned here and continued through [exercise 32](32-the-lease-changes-hands.md). Provision it [the standard way](../../strands/lab-topologies.md#provision); the two nodes are at [the addresses in the strand](../../strands/lab-topologies.md#addresses).

**Setup**

```sh
kubectl create namespace sched-lab
kubectl get nodes -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints,UNSCHED:.spec.unschedulable
```

Record that starting state. One of the two nodes is already refusing most pods before you touch anything, and telling which is the difference between reading `0/2` and reading `0/1`.

**Do**

Three constructions, each a separate pod, each with the event read before the next one is created.

1. **Unschedulable.** Cordon both nodes, then ask for one pod:

   ```sh
   kubectl cordon <cp-node>; kubectl cordon <worker-node>
   kubectl -n sched-lab run probe-a --image=registry.k8s.io/pause:3.9 --restart=Never
   kubectl -n sched-lab describe pod probe-a | sed -n '/Events/,$p'
   kubectl uncordon <cp-node>; kubectl uncordon <worker-node>
   ```

2. **Untolerated taint.** Pin a pod to the control-plane node by hostname, with no toleration:

   ```sh
   kubectl -n sched-lab apply -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata: {name: probe-b}
   spec:
     nodeSelector: {kubernetes.io/hostname: <cp-node>}
     containers: [{name: pause, image: registry.k8s.io/pause:3.9}]
   EOF
   kubectl -n sched-lab describe pod probe-b | sed -n '/Events/,$p'
   ```

3. **Selector matches nothing.** A label no node carries:

   ```sh
   kubectl -n sched-lab run probe-c --image=registry.k8s.io/pause:3.9 --restart=Never \
     --overrides='{"spec":{"nodeSelector":{"academy.k3ii.dev/nonexistent":"true"}}}'
   kubectl -n sched-lab describe pod probe-c | sed -n '/Events/,$p'
   ```

**Observe** — the `FailedScheduling` event message on each, character for character, and the pod's `status.conditions`:

```sh
kubectl -n sched-lab get pod probe-b -o jsonpath='{.status.conditions[0]}{"\n"}'
```

**Expect** — three sentences with the same grammar and different clauses: a count of nodes that were available out of the total, then one clause per reason with its own count. Probe B's message should carry **two** clauses, not one, because the hostname selector refused one node and the taint refused the other, and the scheduler reports both — which is the observable proof that filters are run across all nodes rather than short-circuited at the first refusal.

Match each clause against the `ErrReason` literals from [the previous exercise](05-the-smallest-plugin-that-exists.md). Every clause should be one you already have written down. If one is not, you missed a plugin in the default set and [the mapping](04-what-actually-runs-by-default.md) is where to fix it.

Expect the pod condition to be `PodScheduled=False` with reason `Unschedulable`, and expect it to stay that way rather than the pod erroring out. The pod is not failed; it is waiting, and where it is waiting is [module 5.4](18-find-the-queue-yourself.md).

**Write down** — the three messages verbatim, with the plugin that produced each clause beside it, and one sentence on why probe B produced two clauses.

**Footprint note — one deviation from the phase, stated rather than softened.** [The module](../../phases/05-scheduler.md#m5-1) asks for a one-line `Filter` plugin that rejects every node. Doing that here would need the out-of-tree scaffold, a `KubeSchedulerConfiguration`, a scheduler **link** and therefore [`forge` at 2560MB](../../strands/build-mechanics.md#p5-split) — all of it three exercises before the phase builds anything, and all of it duplicated at [exercise 28](28-the-out-of-tree-plugin.md).

The teaching target here is the *event message and its attribution*, not the Go, and the default set contains three plugins that already refuse every node on demand. So the smallest change is this: produce the observable from stock plugins now, and keep the reject-everything plugin as a two-line variant of build artifact 2, where the toolchain already exists. [Exercise 28](28-the-out-of-tree-plugin.md) carries it.

Cost as run: `pair` at 5.0GB and `forge` at 1536MB against [the 9.5GB ceiling](../../strands/lab-topologies.md#ceiling) — 3.0GB of margin, and the phase's easiest moment.

**Teardown** — `kubectl -n sched-lab delete pod probe-a probe-b probe-c`, and confirm no node is left cordoned:

```sh
kubectl get nodes -o custom-columns=NAME:.metadata.name,UNSCHED:.spec.unschedulable
```

A cordoned node left behind is the single most confusing way to start [the next module](07-fifteen-thirty-six-will-not-link-a-scheduler.md), because everything after it fails for a reason you already stopped suspecting. **The topology stays.**
