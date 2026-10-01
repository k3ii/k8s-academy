<a id="a07"></a>
# A7 — Name the CNI, the CSI and the CRI; find each config on disk and its socket

**Reflex** · **Pinned** · **10 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Cluster Architecture, Installation and Configuration / Extension interfaces

> **Three interfaces, three questions each: what is installed, where is its config, and what socket or API does it speak through.** Nine answers in ten minutes, from the cluster rather than from memory. The exam asks this sideways — as "the CNI is misconfigured" — and you cannot repair a plugin you cannot locate.

**Do**

Answer the nine, out loud, before running anything. Then run the commands and mark yourself.

| | What is installed | Config on disk | Socket or API |
|---|---|---|---|
| **CRI** | | | |
| **CNI** | | | |
| **CSI** | | | |

The CRI answer is a runtime and a `.sock` path, and the path is also a kubelet flag — find it in both places. The CNI answer is a `.conflist` whose **filename ordering matters**, plus a binary directory, plus the DaemonSet that wrote them. The CSI answer on this cluster is the interesting one: **there may not be a CSI driver at all**, and "none, and here is the query that proves it" is the correct answer, not a failure to find one. A provisioner is not automatically a CSI driver.

**Observe**

```sh
kubectl get nodes -o wide                       # CONTAINER-RUNTIME column
sudo crictl info | head -20
sudo ls -l /etc/cni/net.d/ /opt/cni/bin/
kubectl get csidrivers
kubectl get csinodes -o custom-columns=NODE:.metadata.name,DRIVERS:.spec.drivers
sudo grep -r containerRuntimeEndpoint /var/lib/kubelet/config.yaml /etc/default/kubelet 2>/dev/null
```

**Done when** — all nine cells are filled, each from a command you ran rather than from this file, and you can say which DaemonSet or Deployment owns each of the three.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean. Fill the grid with notes open. | 10 min |
| **2** | No notes, and answer the follow-up: *what breaks first* if each of the three stops — and does `kubectl` still work? | 8 min |
| **3** | Cold, clock visible, on whichever topology is up. **The answers differ between topologies**, and noticing that is the point. | 5 min |

**Teardown** — none. This drill is read-only, which is why it is safe to run on a cluster that is mid-way through something else.

**See also** — [the baseline](../../baseline.md#node) records what these answers were on 1 Oct, so it is the mark scheme — but check it against the live cluster first, because the baseline is a snapshot and the cluster is not. **TS1** is this grid used in anger: a `NotReady` node is usually one of these three.
