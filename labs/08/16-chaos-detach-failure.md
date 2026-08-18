<a id="chaos-detach-failure"></a>
# Chaos drill 8.C3 — make your own driver refuse to unstage

**Claim** — you can name where the retry loop lives, its period, and describe what a `VolumeAttachment` looks like while it is stuck.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued from [8.C2](15-chaos-io-errors.md), with your driver from [the in-cluster driver](13-csi-driver-in-cluster.md).

**Setup** — no chaos tool can express this one. **The fault is a flag in your own code**, which is the reason this drill is here rather than in the catalogue: add a `--fail-unstage` flag to `cmd/toy-csi` that makes `NodeUnstageVolume` return `codes.Internal`, redeploy the DaemonSet with it set, and turn it off to recover.

**Do**

1. With the flag off, bind a PVC to a pod and confirm normal teardown works.
2. Redeploy with `--fail-unstage`, then delete the pod.
3. Watch the retry loop from three places at once: your driver's logs, the kubelet's, and the `VolumeAttachment` object.
4. Time the interval between retries and check it against the reading answer from [module 8.4](../../phases/08-storage.md#m8-4).
5. Now delete the *node*'s pod forcibly and watch whether that changes anything. It should not — record why.
6. Turn the flag off and watch the queue drain.

**Observe**

```sh
kubectl get volumeattachment -o yaml | grep -A5 'status:'
kubectl logs -l app=toy-csi-node -c toy-csi -f
ssh zain@10.10.10.131 'journalctl -u kubelet -f | grep -i unstage'
kubectl -n kube-system logs -l component=kube-controller-manager | grep -i detach
```

**Expect** — the retry is not exponential forever; it settles into the reconcile period, and the `VolumeAttachment` sits with `attached: true` long after nothing is using the volume. Nothing times out into a clean state on its own.

**Write down** — the retry period you measured, the flag that governs it, and what an operator can do about a stuck detach that does not involve editing objects.

**Teardown** — remove the flag and redeploy. Leave the cluster up for [8.C5](17-chaos-disk-fill.md).
