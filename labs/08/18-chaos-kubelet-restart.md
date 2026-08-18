<a id="chaos-kubelet-restart"></a>
# Chaos drill 8.C6 — restart the kubelet with mounts held

**Claim** — you can state what volume reconstruction recovers after a kubelet restart and what it cannot, and point at KEP-3756 for why.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued from [8.C5](17-chaos-disk-fill.md), with pods on volumes from your driver and from `local-path`.

**Do**

1. Record the full mount tree and the pod-to-volume mapping before touching anything — you are about to compare against it.
2. `systemctl restart kubelet` on the worker. Time how long the node is `NotReady` and what happens to the running containers.
3. Diff the mount tree afterwards. Everything the kubelet rebuilt from its own on-disk state is reconstruction; everything that came back from the API is not.
4. Now make it harder: restart the kubelet while a pod is *terminating* with its volume still mounted, and see what is left behind.
5. Look for orphaned pod directories under `/var/lib/kubelet/pods/` and decide whether the kubelet will clean them.

**Observe**

```sh
ssh zain@10.10.10.131 'findmnt -R /var/lib/kubelet > /tmp/before'
ssh zain@10.10.10.131 'systemctl restart kubelet; sleep 30; findmnt -R /var/lib/kubelet > /tmp/after; diff /tmp/before /tmp/after'
ssh zain@10.10.10.131 'journalctl -u kubelet -b | grep -i "reconstruct\|orphan"'
kubectl get nodes -w
```

**Expect** — the containers keep running; the kubelet is not in their execution path. Reconstruction rebuilds the volume manager's actual-state-of-world from the mount table, and **KEP-3756** exists because what it could infer before was not enough — specifically the parts of a volume's identity that live only in the API.

**Write down** — the list of what survived and what did not, and one sentence on why the desired/actual-state-of-world split makes this recoverable at all.

**Teardown** — leave it up for [8.C4](19-chaos-node-loss.md), which ends the phase's cluster.
