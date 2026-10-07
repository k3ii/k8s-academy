<a id="s01"></a>
# S1 — A PVC binds, mounts, takes a write; delete the pod and read it back

**Reflex** · **Core** · **10 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Storage / Manage PVs and PVCs

> **This is the whole storage story in one pass, and everything else is a variation on it.** PVC → bind → mount → write → destroy the pod → read it back from a new one. If you can do this cold in three minutes, most storage questions become bookkeeping.

> **On this cluster, `local-path` binds `WaitForFirstConsumer`.** A PVC with no pod stays `Pending` and that is **correct, not broken** — the provisioner is waiting to learn which node to carve the directory on. Do not debug it. Create the pod and watch it bind within seconds.

**Do**

1. A PVC against `local-path`, 1Gi, `ReadWriteOnce`. It sits `Pending`. Read the event; it says it is waiting for a consumer.
2. A pod that mounts it. The PVC binds, a PV appears that nobody created, and the pod runs. Note the PV's name — generated, with the PVC's namespace and name in it.
3. Write a file into the mount. Then **delete the pod** and create a new one against the same PVC. Read the file back. That is the point of the whole subsystem.
4. **Find the data on the node.** `local-path` carves a directory under `/opt/local-path-provisioner` on the node the pod landed on. Go and look at it over ssh. Storage stops being abstract the moment you have `cat`-ed the file from the host.
5. Note which node that is, because the PV is now pinned there — a `nodeAffinity` on the PV says so. Read it. This is why the next pod scheduled elsewhere would not be able to use it, and it is the honest limitation of a local provisioner.
6. Delete the PVC and watch the PV go with it, because the class reclaims `Delete`. Then check the node directory is gone too.

**Observe**

```sh
kubectl get pvc,pv
kubectl describe pvc data | sed -n '/Events/,$p'
kubectl get pv <name> -o jsonpath='{.spec.nodeAffinity}' | python3 -m json.tool
kubectl exec app -- sh -c 'echo hello > /data/f; cat /data/f'
ssh -F ssh/config -J factory zain@10.10.10.131 'sudo ls -R /opt/local-path-provisioner'
```

**Done when** — data survives the pod, and you can point at the directory on the node holding it.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean. Bind, write, destroy, re-read, find it on the node. | 10 min |
| **2** | Two PVCs, two pods, one of them on the other node. | 8 min |
| **3** | Cold, no notes. PVC, pod, write, verify. | 5 min |

**Teardown** — delete the namespace, then check `kubectl get pv` is empty. A leaked PV with `Delete` normally cleans itself; one with `Retain` does not.

**See also** — **S2** is the same PVC refusing to bind for a real reason; **S8** is the reclaim policy this relies on.
