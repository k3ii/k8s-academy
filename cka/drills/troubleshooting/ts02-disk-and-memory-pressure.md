<a id="ts02"></a>
# TS2 — Drive a node into `DiskPressure`, then `MemoryPressure`

**Reflex** · **Core** · **10 min** · [`workhorse`](../../../strands/lab-topologies.md#workhorse) · Troubleshooting / Troubleshoot clusters and nodes

> **The kubelet evicts pods on its own authority, and it taints the node so the scheduler stops sending more.** That taint is the part worth knowing: pods leave *and* new ones stay away, so a pressured node looks both busy and empty, and the fault presents as "my pods keep moving" rather than as a disk problem.

**Break it** — *pass 1 only.* The disk case is **F04** in the catalogue; it fills `/var` to inside the default `nodefs` 10% threshold.

1. `fallocate` a large file on the node's `/var` filesystem until free space drops under the eviction threshold. Do the arithmetic from `df` first so you know how close you are putting it — this is the one fault that can genuinely damage the node if overshot.
2. For memory, run a pod that allocates hard, with a limit well above what the node can spare.

**Work it**

- **Read the condition and the taint together.** `DiskPressure=True` on the node, and `node.kubernetes.io/disk-pressure:NoSchedule` applied automatically. Confirm the taint is there — that it is applied *by the kubelet*, not by you, is the point.
- **Watch the eviction order**, which is QoS plus usage-over-request: `BestEffort` first, then `Burstable` exceeding its requests, and `Guaranteed` last. Run one of each beforehand so you can see the order rather than recite it. Evicted pods show status `Evicted` and **stay in the listing** as tombstones — they are not cleaned up automatically, and a wall of `Evicted` pods *is* the diagnosis.
- **Separate eviction from OOM-kill.** Eviction is the kubelet acting on node pressure; OOM-kill is the kernel acting on a cgroup limit, and leaves exit code 137 on one container without touching its neighbours (**TS11**). They have entirely different causes and the same vibe.
- **Find what is actually using the disk**, because the real-world version of this is never a `fallocate`: images, dead containers, and pod logs under `/var/log/pods`. `crictl imagefsinfo`, and know that the kubelet garbage-collects images under pressure on its own.
- **Clear it** and watch the condition flip back, the taint be removed automatically, and scheduling resume. Then delete the `Evicted` tombstones by hand.

**Observe**

```sh
kubectl describe node <n> | sed -n '/Conditions/,/Addresses/p'
kubectl describe node <n> | grep -i taint
kubectl get pods -A --field-selector status.phase=Failed
df -h /var; du -xh /var --max-depth=2 | sort -h | tail
journalctl -u kubelet -n 50 --no-pager | grep -i evict
kubectl delete pods -A --field-selector status.phase=Failed
```

**Done when** — you predict the eviction order before it happens, and you recognise a pressure taint as the reason new pods are not scheduling.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean. Both pressures, one pod per QoS class. | 10 min |
| **2** | Pressure already present on arrival. Identify the consumer and clear it. | 8 min |
| **3** | **Injected.** **F04**, cause unknown. | **5 min** |

**Teardown** — `cka-inject.sh revert`, **delete the filler file**, confirm `df` is back and both conditions read `False`, and clear every `Evicted` pod. A node left near the threshold will fail a later drill in a way that looks unrelated.

**See also** — **TS11** is the cgroup-level kill this is not; **W1** is the requests that decide the eviction order.
