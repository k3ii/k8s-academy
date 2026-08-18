<a id="finalizer-deadlock"></a>
# A PVC that will not delete, cleared correctly

**Claim** — a `Terminating` PVC held by `kubernetes.io/pvc-protection` is released by removing its consumer, and stripping the finalizer instead leaves an orphaned volume nobody will ever clean up.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued from [snapshots](10-snapshot-and-restore.md).

**Do**

1. Create a PVC, mount it in a pod, then `kubectl delete pvc`. It hangs.
2. Identify the finalizer and identify what is holding it:

   ```sh
   kubectl get pvc <name> -o jsonpath='{.metadata.finalizers}'
   kubectl get pvc <name> -o jsonpath='{.metadata.deletionTimestamp}'
   ```

3. Clear it **correctly** — delete the consumer. Watch the `pvcprotection` controller drop the finalizer itself.
4. Now do it wrong, deliberately, on a second PVC: strip the finalizer with a patch. Then go find the volume that nobody is going to reclaim.

   ```sh
   kubectl patch pvc <name> -p '{"metadata":{"finalizers":null}}' --type=merge
   ```

5. Do the same for `kubernetes.io/pv-protection` on a PV and note which consumer holds *that* one.

**Observe**

```sh
kubectl -n kube-system logs -l component=kube-controller-manager --tail=200 | grep -i protection
kubectl get pv,pvc -o custom-columns=KIND:.kind,NAME:.metadata.name,FINALIZERS:.metadata.finalizers,DELETED:.metadata.deletionTimestamp
ssh zain@10.10.10.131 'ls /var/lib/kubelet/plugins/kubernetes.io/csi/*/*/globalmount 2>/dev/null; ls /opt/local-path-provisioner 2>/dev/null'
```

**Expect** — the object disappears the moment the finalizer count reaches zero, whichever way it got there. The difference is entirely in what the controller was going to do first and now never will: unmount, detach, and delete the backing directory.

**Write down** — why stripping a finalizer is the wrong fix, stated in terms of the work the controller had queued. [Checklist item](../../phases/08-storage.md#checklist); it is also the most common wrong answer on the internet.

**Teardown** — leave the cluster up. The build-track exercises run alongside these modules and [stage 1](12-csi-driver-sanity.md) does not touch it.
