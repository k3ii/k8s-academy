<a id="umount-under-a-running-pod"></a>
# Unmount a volume out from under a running pod

**Claim** — the container keeps running, sees an empty directory rather than an error, and the kubelet repairs the bind mount on its own schedule — which is longer than you expect.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued from [the mount trace](07-volume-to-mount-trace.md), with the same pod and the same two paths.

**Do**

1. From inside the pod, start something that writes to the volume once a second and logs what it sees.
2. On the node, `umount` the **publish** path — not the staging path.

   ```sh
   umount /var/lib/kubelet/pods/<uid>/volumes/kubernetes.io~csi/<pv>/mount
   ```

3. Time how long until the kubelet notices and what it does. Do not restart anything.
4. Repeat against the **staging** path with the pod still running, and record the different outcome.

**Observe**

```sh
journalctl -u kubelet -f | grep -i 'mount\|orphan\|reconstruct'
kubectl describe pod <pod> | sed -n '/Events/,$p'
findmnt -R /var/lib/kubelet | grep csi
```

**Expect** — no crash and no event at the moment of the unmount. The process's open file descriptors survive; new opens land on the underlying directory, which is empty. This is the mount-namespace lesson from [P0](../../phases/00-linux-primitives.md) arriving with consequences, and it is why the CSI node DaemonSet needs `mountPropagation: Bidirectional` — a mount made inside that container has to be visible to the host, or the kubelet's view and the node's view diverge exactly like this.

**Write down** — how long the kubelet took, what log line marked it, and one sentence connecting this to `mountPropagation`. [The checklist asks you to defend that field](../../phases/08-storage.md#checklist).

**Teardown** — leave it up for [expansion](09-expansion-two-phase.md).
