<a id="the-cgroup-tree-under-one-pod"></a>
# Walk from the node's root cgroup down to one container, naming every level

**Artifact** — a diagram of the worker's cgroup v2 tree from `/sys/fs/cgroup` down to a single container, with the QoS level labelled, and for each level the value of `memory.max` and `cpu.max` — showing which limits are set by the kubelet, which by you, and which are `max` because nobody set them.

**Rests on** — [the QoS classification](06-three-pods-three-classes.md); the tree's middle level *is* the class, and seeing it as a directory is the point.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued. Worker `.131`.

**Setup** — one pod of each class, on the worker, so all three branches exist at once:

```sh
kubectl create ns cgroups
kubectl -n cgroups apply -f - <<'EOF2'
apiVersion: v1
kind: Pod
metadata: {name: g}
spec:
  nodeName: pair-worker
  containers: [{name: c, image: registry.k8s.io/pause:3.10, resources: {requests: {cpu: 100m, memory: 64Mi}, limits: {cpu: 100m, memory: 64Mi}}}]
---
apiVersion: v1
kind: Pod
metadata: {name: b}
spec:
  nodeName: pair-worker
  containers: [{name: c, image: registry.k8s.io/pause:3.10, resources: {requests: {cpu: 50m, memory: 32Mi}, limits: {memory: 128Mi}}}]
---
apiVersion: v1
kind: Pod
metadata: {name: be}
spec:
  nodeName: pair-worker
  containers: [{name: c, image: registry.k8s.io/pause:3.10}]
EOF2
```

**Do** — on the worker, walk the tree and print the two files at every level:

```sh
ssh zain@10.10.10.131 'find /sys/fs/cgroup/kubepods.slice -maxdepth 2 -type d | sort'
ssh zain@10.10.10.131 'for d in $(find /sys/fs/cgroup/kubepods.slice -type d | sort); do
    printf "%-90s mem.max=%-12s cpu.max=%-12s cur=%s\n" "${d#/sys/fs/cgroup/}" \
      "$(cat $d/memory.max 2>/dev/null)" "$(cat $d/cpu.max 2>/dev/null | tr " " "/")" \
      "$(cat $d/memory.current 2>/dev/null)"
  done'
```

Then place your three pods in it. Map each pod UID to a directory:

```sh
kubectl -n cgroups get pods -o custom-columns=NAME:.metadata.name,QOS:.status.qosClass,UID:.metadata.uid
```

Answer four questions from what you printed, not from documentation:

1. Which of the three pods has **no QoS directory above it**, and what does that placement say about how the kubelet groups Guaranteed pods?
2. What is `memory.max` on the BestEffort pod's own cgroup, and what is it on `kubepods-besteffort.slice`? Which of the two is the constraint that matters?
3. There is one more directory level below the pod. What lives there besides the container you asked for, and which exercise met that process already?
4. What is `memory.max` on `kubepods.slice` itself, and where did that number come from? It is not the node's RAM. [Exercise 17](17-where-the-ram-went.md) is where you account for the difference.

**Expect** — three branches under `kubepods.slice`: `kubepods-burstable.slice`, `kubepods-besteffort.slice`, and the Guaranteed pods sitting **directly under `kubepods.slice`** with no class directory of their own. That asymmetry is not a quirk — a Guaranteed pod has nothing to share with its class, because its limit is its own.

Expect two directories per pod: the sandbox and the container, which is the [pause process](02-one-pod-is-how-many-cri-calls.md) turning up in a third place. Expect `memory.max` to be `max` for BestEffort at every level up to `kubepods.slice`, which is exactly why a BestEffort pod can take the whole node and why [run B of the previous exercise](14-evicted-or-oomkilled.md) had no cgroup to stop it.

**Write down** — the tree diagram with the four levels named (root → `kubepods.slice` → QoS slice → pod → container), the values at each, and the four answers. This is [the module's 6.4 artifact](../../phases/06-kubelet-node.md#m6-4).

**Footprint note** — three `pause` pods; negligible. The tree is the artifact and it costs nothing to produce.

**Teardown** — **leave the namespace up**: [exercises 16](16-throttled-instead-of-killed.md) and [18](18-cpu-max-and-the-throttle-counter.md) write into these same cgroups. **The topology stays.**
