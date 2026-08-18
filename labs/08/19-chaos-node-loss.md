<a id="chaos-node-loss"></a>
# Chaos drill 8.C4 — lose a node with a volume attached

**Claim** — you can state how long it takes for the cluster to give up on a volume attached to a dead node, name the flag that governs it, and say why the volume does not come back somewhere else on this lab.

**This is the drill to spend real time on.** It is the storage failure most likely to be met in production, its duration is genuinely surprising, it cannot be scripted, and **[the gate](../../phases/08-storage.md#gate) names it explicitly**: if you cannot explain the delay and name the flag, the phase is not finished.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued from [8.C6](18-chaos-kubelet-restart.md). This exercise destroys it.

**Setup** — manual. [Chaos Mesh has no native node-failure kind](../../strands/chaos.md#cannot-express) and Litmus's substitute wants an SSH private key in a Secret, which is a hazard worth reading about rather than running. The fault here is `qm stop` on Proxmox, which is as real as node loss gets.

**Do**

1. Get a pod running on the worker with a volume from your driver attached. Record the `VolumeAttachment` and `node.status.volumesInUse`.
2. Start a clock. From `hopper`:

   ```sh
   ssh hopper
   qm stop <worker-vmid>     # the vmid is the node's last octet
   ```

3. Mark, with timestamps: node `NotReady`; the taint appearing; the pod's deletion; the `VolumeAttachment` still standing; and whatever finally removes it.
4. Answer, from what you measured, which of `--node-monitor-grace-period`, the eviction toleration seconds, and the attach/detach controller's force-detach timeout accounted for which part of the wall-clock. Check against [module 8.4's reading answer](../../phases/08-storage.md#m8-4).
5. `qm start` the node and watch the reconciliation from the other side.

**Observe**

```sh
kubectl get nodes -w
kubectl get volumeattachment -o wide -w
kubectl get pod <pod> -o jsonpath='{.metadata.deletionTimestamp}'
kubectl -n kube-system logs -l component=kube-controller-manager -f | grep -i 'detach\|node'
```

**Expect — and a correction to make in your notes.** The phase's original framing asks how long until the volume is *reattached elsewhere*. **On this lab it never is, and that is the more useful answer.** Every backend available here — `hostPath`, `local-path-provisioner` and your own driver — is node-local, so the PV carries node affinity for a node that is gone; the replacement pod stays `Pending` on volume node affinity even though a second node exists. Reattachment elsewhere requires storage that is not node-local, which this node cannot host. **Measure the detach timeline, which is real, and reason about the reattachment, which is not observable here** — do not add a topology to chase it, because the blocker is storage locality and not node count.

**Write down** — the timeline with timestamps, the flag that dominates it and its default, and one paragraph on why node-local storage turns a node failure into a data-placement problem. The gate asks for exactly this.

**Teardown** — the phase's cluster ends here.

```sh
ssh hopper
just tofu labs destroy
```

Then evict the build caches too, per [the disk arithmetic](../../strands/build-mechanics.md#p5-split): `go clean -modcache` and `docker system prune` on `forge`.
