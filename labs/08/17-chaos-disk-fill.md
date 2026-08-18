<a id="chaos-disk-fill"></a>
# Chaos drill 8.C5 — fill the disk

**Claim** — you can state how the eviction path for disk pressure differs from the one for memory pressure, and name the thresholds that drive each.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued from [8.C3](16-chaos-detach-failure.md).

**Footprint note** — the worker's disk is 20G and it holds container images, the kubelet's volumes and your fill file. **Fill toward a threshold, not to 100%**, and read [the ceiling](../../strands/lab-topologies.md#ceiling) first: a node whose root filesystem is genuinely full may not recover without a reprovision, and a reprovision costs the rest of this chain.

**Do**

1. Record `kubectl describe node <worker>` conditions and the kubelet's eviction thresholds before touching anything.
2. Fill the volume — `chaosd disk-fill` on the host, or a `StressChaos` inside the pod — to just past `nodefs.available` soft.
3. Watch the `DiskPressure` condition, the eviction, and which pod was chosen.
4. Compare with what you saw for memory pressure in [P6](../../phases/06-kubelet-node.md): which is graceful, which is immediate, and which one the pod can be `Ready` through.
5. Free the space and watch the condition clear after its grace period.

**Observe**

```sh
kubectl describe node <worker> | sed -n '/Conditions/,/Addresses/p'
kubectl get events --field-selector reason=Evicted
ssh zain@10.10.10.131 'df -h /var/lib/kubelet; journalctl -u kubelet | grep -i evict'
```

**Expect** — disk-pressure eviction is *ranked* and graceful; memory pressure ends in an OOMKill by the kernel with no ranking and no notice. The kubelet also garbage-collects images before it evicts anything, so the first response to a filling disk is invisible in the pod list.

**Write down** — the two eviction paths side by side, with the signal, the actor and the pod's experience for each.

**Teardown** — delete the fill. Leave the cluster up for [8.C6](18-chaos-kubelet-restart.md).
