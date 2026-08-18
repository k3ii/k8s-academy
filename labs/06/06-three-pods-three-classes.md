<a id="three-pods-three-classes"></a>
# Classify five pods from the algorithm, then let the API server mark your paper

**Claim** — QoS class is a pure function of requests and limits with no node state in it at all, so you can classify any pod correctly from `GetPodQOS` alone — including the three cases where people reliably get it wrong.

**Rests on** — nothing in this phase; it rests on [P5's resource arithmetic](../../phases/05-scheduler.md#m5-3), where requests were promises the scheduler counted. Here the same two fields decide who dies.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued, though only the API server is needed: **classification never reaches the node**, and proving that is part of the exercise.

**Read** — `~/src/design-proposals-archive/node/resource-qos.md` (item 7) for the *why*, then the algorithm itself:

```sh
sed -n '/func GetPodQOS/,/^}/p' ~/src/kubernetes/pkg/apis/core/v1/helper/qos/qos.go
```

4.6 KB, one function, no dependencies worth chasing. Answer [module 6.2's question](../../phases/06-kubelet-node.md#m6-2) from the code: what exact combination of requests and limits yields each class?

**Do**

1. **Predict before applying.** Write your five answers down first:

   ```sh
   kubectl create ns qos-lab
   kubectl -n qos-lab apply -f - <<'EOF2'
   apiVersion: v1
   kind: Pod
   metadata: {name: a-limits-only}
   spec:
     nodeSelector: {node-role.kubernetes.io/control-plane: ""}
     tolerations: [{operator: Exists}]
     containers:
     - {name: c, image: registry.k8s.io/pause:3.10, resources: {limits: {cpu: 100m, memory: 64Mi}}}
   ---
   apiVersion: v1
   kind: Pod
   metadata: {name: b-equal-both}
   spec:
     nodeSelector: {node-role.kubernetes.io/control-plane: ""}
     tolerations: [{operator: Exists}]
     containers:
     - {name: c, image: registry.k8s.io/pause:3.10, resources: {requests: {cpu: 100m, memory: 64Mi}, limits: {cpu: 100m, memory: 64Mi}}}
   ---
   apiVersion: v1
   kind: Pod
   metadata: {name: c-cpu-only}
   spec:
     nodeSelector: {node-role.kubernetes.io/control-plane: ""}
     tolerations: [{operator: Exists}]
     containers:
     - {name: c, image: registry.k8s.io/pause:3.10, resources: {requests: {cpu: 100m}, limits: {cpu: 100m}}}
   ---
   apiVersion: v1
   kind: Pod
   metadata: {name: d-two-containers}
   spec:
     nodeSelector: {node-role.kubernetes.io/control-plane: ""}
     tolerations: [{operator: Exists}]
     containers:
     - {name: strict, image: registry.k8s.io/pause:3.10, resources: {requests: {cpu: 50m, memory: 32Mi}, limits: {cpu: 50m, memory: 32Mi}}}
     - {name: loose, image: registry.k8s.io/pause:3.10, resources: {requests: {cpu: 50m, memory: 32Mi}}}
   ---
   apiVersion: v1
   kind: Pod
   metadata: {name: e-nothing}
   spec:
     nodeSelector: {node-role.kubernetes.io/control-plane: ""}
     tolerations: [{operator: Exists}]
     containers:
     - {name: c, image: registry.k8s.io/pause:3.10}
   EOF2
   ```

2. Mark your paper:

   ```sh
   kubectl -n qos-lab get pods -o custom-columns=NAME:.metadata.name,QOS:.status.qosClass
   ```

3. For every pod you got wrong, find the branch in `GetPodQOS` that decided it and quote the line.

4. Prove classification is node-independent. Pick the pod you were most confident about, delete it, change nothing but the node it lands on, re-apply to the worker, and compare the class. Then find the field: is `status.qosClass` written by the API server or by the kubelet? Answer it with evidence — `kubectl -n qos-lab get pod e-nothing -o yaml | grep -A2 qosClass` on a pod that is still `Pending` because it fits nowhere will settle it.

**Expect** — the limits-only pod to come back **Guaranteed**, which is the first surprise: limits with no requests are defaulted to equal the limits, so the loosest-looking spec produces the strictest class. The cpu-only pod is **Burstable** even though its cpu is exactly equal, because the class is decided across *all* resources and memory is unset. And `d-two-containers` is **Burstable** — one loose container is enough, so a Guaranteed pod is an all-or-nothing property of the whole pod, which is exactly why a sidecar can silently downgrade a workload someone carefully tuned.

Expect `status.qosClass` to be populated before any node accepts the pod. That is the evidence that this is API-level, not node-level, and it is why [the next exercise](07-oom-score-adj-from-the-formula.md) is where the node finally gets a say.

**Write down** — the five predictions against the five answers, the `qos.go` line for each mistake, and the one-line rule per class, which [the phase's checklist](../../phases/06-kubelet-node.md#checklist) asks for and [the eviction ranking](11-synchronize-and-the-ranking.md) will consume.

**Footprint note** — five `pause` pods pinned to the control plane, a few MB in total. They sit on `.130` deliberately: everything from [the OOM work](09-6c3-who-killed-the-pod.md) onward treats the worker's 2048MB as the instrument, and leaving stray pods there costs you the baseline you are about to measure.

**Teardown** — `kubectl delete ns qos-lab`. **The topology stays.**
