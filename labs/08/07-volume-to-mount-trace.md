<a id="volume-to-mount-trace"></a>
# Follow one volume down to a mount line

**Artifact** — an arrow diagram from PVC to a `mount` line on a node, every hop naming the component responsible, plus the staging/publish path pair for your own volume. **This diagram is a required input to [the capstone](../../phases/08-storage.md#capstone)** and the checklist asks you to redraw it from memory in five minutes.

**Rests on** — [Module 8.4's reading question](../../phases/08-storage.md#m8-4) on the attach/detach reconcile period, and module 8.1's answer about which CSI call happens per node versus per pod.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued from [the Pending drill](06-four-ways-a-pvc-stays-pending.md).

**Do**

1. Deploy a pod with a dynamically-provisioned PVC.
2. On the worker node, find both paths:

   ```sh
   ssh zain@10.10.10.131
   findmnt -R /var/lib/kubelet | grep -B2 -A2 csi
   ls /var/lib/kubelet/plugins/kubernetes.io/csi/*/*/globalmount   # staging
   ls /var/lib/kubelet/pods/*/volumes/kubernetes.io~csi/*/mount     # publish
   ```

3. **Say the relationship between those two paths out loud before reading further.** This is `NodeStageVolume` versus `NodePublishVolume` made physical.
4. Scale to two pods on the same node against one `ReadWriteMany` volume. A second publish path appears against the **same** staging path.
5. `nsenter` into the container's mount namespace and confirm what the container sees is the publish path and not the staging one.

   ```sh
   pid=$(crictl inspect $(crictl ps -q --name <container>) | jq .info.pid)
   nsenter -t $pid -m findmnt <mountpath>
   ```

**Observe**

```sh
findmnt -R /var/lib/kubelet | grep -A2 csi
kubectl get volumeattachment -o wide
journalctl -u kubelet -f | grep -i 'volume\|mount'
```

**Expect** — one staging mount per node per volume, one bind mount per pod. The `VolumeAttachment` object is the cluster-level record of the first; nothing in the API represents the second.

**Write down** — the diagram, and the literal staging and publish paths for your volume.

**Teardown** — leave it up; [the unmount](08-umount-under-a-running-pod.md) breaks this exact mount.
