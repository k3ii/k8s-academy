<a id="ts01"></a>
# TS1 — A node is `NotReady`: work the ladder, name the rung before you fix it

**Reflex** · **Core** · **10 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Troubleshooting / Troubleshoot clusters and nodes

> **`NotReady` is one word for at least five different faults, and `kubectl` can tell you almost nothing about any of them.** The node's conditions come *from* the kubelet, so when the kubelet is the problem the cluster's view is stale by construction. Everything useful is on the node, and the ladder is: is the unit running → what does it say → can it reach the runtime → does it have a CNI → can it reach the API server.

**Break it** — *pass 1 only.* Two of these are in the catalogue as **F01** and **F02**; produce them yourself first so the signatures are yours.

1. `systemctl stop kubelet`. The clean case.
2. Corrupt `/var/lib/kubelet/config.yaml`. The unit is alive and flapping — a different signature entirely, and the one people misread.
3. Stop the container runtime underneath it.
4. Move the CNI config out of `/etc/cni/net.d/`. The node goes `NotReady` with a condition that says so in words.

**Work it** — the ladder, in order, naming the rung before fixing:

- **From the cluster, first and briefly.** `kubectl describe node` and read the **conditions** with their messages — `KubeletNotReady` with `container runtime network not ready: cni plugin not initialized` names rung four outright, and costs ten seconds. Note `LastHeartbeatTime`: a heartbeat that stopped minutes ago means the kubelet is gone, not sick.
- **Rung 1 — the unit.** `systemctl status kubelet`. Running, dead, or restart-looping? A loop means it starts and dies, which points at config, not at the process being stopped.
- **Rung 2 — its own words.** `journalctl -u kubelet -n 50 --no-pager`, and `-f` while you fix. This is where nearly every answer is, and reading it is the habit the drill exists to build. A config error is explicit here and invisible everywhere else.
- **Rung 3 — the runtime.** `crictl ps` and `crictl info`. If `crictl` cannot reach its socket, the kubelet cannot either, and the kubelet log says so in a way that reads like a kubelet fault.
- **Rung 4 — CNI.** `ls /etc/cni/net.d/`. Empty is the fault.
- **Rung 5 — the API server.** Certificates and reachability from the node: can it talk at all, and is its client certificate still valid (**TS7**).

**Observe**

```sh
kubectl get nodes
kubectl describe node <n> | sed -n '/Conditions/,/Addresses/p'
systemctl status kubelet
journalctl -u kubelet -n 50 --no-pager
crictl ps -a | head
ls -l /etc/cni/net.d/ /var/lib/kubelet/config.yaml
```

**Done when** — you name the rung before touching anything, every time, and you reach for `journalctl -u kubelet` as the second command rather than the sixth.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean. Produce all four, fix all four. | 10 min |
| **2** | Workload running on the node. Fix it without evicting anything. | 8 min |
| **3** | **Injected.** One of **F01**/**F02**, cause unknown. | **5 min** |

**Teardown** — `cka-inject.sh revert`, then confirm `kubectl get nodes` shows every node `Ready` and no node is left cordoned.

**See also** — **TS4** is the node gone entirely rather than sick; **TS5** is the control plane broken underneath `kubectl`.
