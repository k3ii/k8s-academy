<a id="snapshot-and-restore"></a>
# Snapshot a volume, destroy the source, restore from it

**Artifact** — a PVC restored from a `VolumeSnapshot` after its source PVC was deleted, with the data intact.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued from [expansion](09-expansion-two-phase.md).

**Footprint note** — this installs the `external-snapshotter` CRDs plus a snapshot controller, which is a controller Deployment the phase's original costing did not include. It is small, but take [a memory request from `kubectl top`](../../strands/build-mechanics.md#sizing) for it the way you would for your own work.

**Do**

1. Install the `external-snapshotter` CRDs and controller. **Notice what you just installed**: CRDs plus a controller watching them, which is the shape you built in [P4](../../phases/04-controllers.md).
2. Write identifiable data into a bound PVC from a pod.
3. Take a `VolumeSnapshot` against a `VolumeSnapshotClass`. Watch the `VolumeSnapshotContent` object appear beside it.
4. Delete the **source PVC**.
5. Create a new PVC with `dataSource` naming the snapshot, mount it, and check the data.

**Observe**

```sh
kubectl get volumesnapshot,volumesnapshotcontent -o wide
kubectl get volumesnapshotclass
kubectl describe volumesnapshot <name> | sed -n '/Status/,$p'
```

**Expect** — the same two-object split as PV/PVC, one namespaced and one cluster-scoped, with a class in front of both. Snapshots are **not** in-tree: they are CRDs and an out-of-tree controller, and that is the point of doing them right after reading KEP-177.

**Write down** — the object triple (`VolumeSnapshot` / `VolumeSnapshotContent` / `VolumeSnapshotClass`) mapped onto the PVC/PV/StorageClass triple, and where the analogy breaks.

**Teardown** — leave it up for [the finalizer deadlock](11-finalizer-deadlock.md).
