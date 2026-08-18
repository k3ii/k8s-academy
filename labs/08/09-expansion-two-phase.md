<a id="expansion-two-phase"></a>
# Expansion is two phases, and you can get stuck between them

**Claim** — one phase sets `FileSystemResizePending` and a different one clears it; you can name which is which, and you can recover from an expansion the backing store cannot satisfy without deleting the PVC.

**Rests on** — [Module 8.5's reading question](../../phases/08-storage.md#m8-5): which phase sets the condition, which clears it, and what must be true of the pod for the node phase to proceed.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued from [the unmount](08-umount-under-a-running-pod.md).

**Do**

1. Ensure the StorageClass has `allowVolumeExpansion: true`. Note what happens if it does not — the API rejects the edit, and the message is worth reading.
2. Patch a bound PVC's `spec.resources.requests.storage` upward. Watch `FileSystemResizePending` appear.
3. Watch it clear. If it does not clear, look at the pod before looking at the storage — the node phase has a precondition about the consumer.
4. Now request an expansion the backing store cannot fulfil, and recover from it per **KEP-1790** by reducing the request. Record whether the API lets you shrink `spec` back, and what makes that legal here when shrinking a volume normally is not.

**Observe**

```sh
kubectl get pvc <name> -o jsonpath='{.status.conditions}' | jq
kubectl get pvc <name> -o jsonpath='{.status.allocatedResourceStatuses}' | jq
kubectl -n kube-system logs -l component=kube-controller-manager --tail=200 | grep -i resize
journalctl -u kubelet | grep -i resize
```

**Expect** — the controller phase completes against the storage system and leaves the condition set; the node phase grows the filesystem and clears it. The KEP-1790 recovery works because the *allocated* size and the *requested* size are tracked separately — which is exactly what `allocatedResourceStatuses` is for.

**Write down** — which phase sets and which clears the condition, cited. [Checklist item](../../phases/08-storage.md#checklist).

**Teardown** — leave it up for [snapshots](10-snapshot-and-restore.md).
