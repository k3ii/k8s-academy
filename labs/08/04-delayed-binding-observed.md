<a id="delayed-binding-observed"></a>
# Delayed binding, observed delaying something

**Claim** — a PVC against a `WaitForFirstConsumer` class stays `Pending` with no error until a pod that consumes it is scheduled, and the bind then happens *at scheduling time*, inside the scheduler.

**Rests on** — [Module 8.3's reading question](../../phases/08-storage.md#m8-3): what `volume_binding.go` does at each of `PreFilter`, `Filter`, `Reserve` and `PreBind`. Steps 2 and 3 below are that answer made visible.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued from [the claimRef rewrite](03-rewrite-a-claimref.md).

**Do**

1. Install `local-path-provisioner` if it is not already up (it is the phase's [ecosystem rock](../../phases/08-storage.md#ecosystem)), and create two StorageClasses over it that differ in one field only:

   ```yaml
   volumeBindingMode: Immediate            # class A
   volumeBindingMode: WaitForFirstConsumer # class B
   ```

2. Create one PVC against each, **with no pod at all**. One binds within a second; the other sits `Pending`.
3. Create a pod for each PVC. Watch the second bind as the pod is scheduled, not before.

**Observe**

```sh
kubectl get pvc -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.phase}{"\t"}{.spec.volumeName}{"\n"}{end}'
kubectl describe pvc <wfc-pvc> | tail -20
kubectl -n kube-system logs -l component=kube-scheduler --tail=300 | grep -i volumebinding
kubectl get events --sort-by=.lastTimestamp -w
```

**Expect** — the `WaitForFirstConsumer` PVC's events carry `waiting for first consumer to be created before binding`. **Nothing is broken; that is the design.** The scheduler log shows the `volumebinding` plugin acting during the pod's scheduling cycle, and `pvc.spec.volumeName` appears in the same moment the pod gets a node.

**Write down** — which of the four extension points did which part of that, in your own words, checked against the reading answer.

**Teardown** — leave it up; [the zone mismatch](05-zone-mismatch-by-construction.md) needs both StorageClasses.
