<a id="n10"></a>
# N10 — Pod to pod across nodes, and the route that carries it

**Reflex** · **Core** · **10 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Servicing and Networking / Pod connectivity

> **Every node gets a slice of the cluster CIDR, and the node routing table is where the slices meet.** Pod networking stops being magic the moment you can point at the `/24` a node owns and the route that sends the other `/24` across the overlay. This drill is that pointing exercise.

**Do**

1. A pod on each node — use `nodeName` or an anti-affinity, do not hope. Curl one from the other and confirm it works before you explain it.
2. **Read the allocation.** Each node carries a `podCIDR`, carved out of the cluster CIDR the control plane was initialised with. On this cluster:

   ```
   pair-cp   10.244.0.0/24
   pair-w1   10.244.1.0/24
   ```

   both out of `10.244.0.0/16`. Confirm the pod addresses fall inside their node's slice.
3. **Read the routes on the node itself**, over ssh. Local pods go out the bridge; the other node's slice goes over the overlay device:

   ```
   10.244.0.0/24 dev cni0 proto kernel scope link src 10.244.0.1
   10.244.1.0/24 via 10.244.1.0 dev flannel.1 onlink
   ```

   That second line is the whole answer to "how does the packet get there".
4. Trace the path: pod → `veth` → `cni0` → `flannel.1` (VXLAN-encapsulated) → the node's real NIC → the other node, and back up. Name each hop.
5. **Then check where the cluster CIDR is written down**, because a mismatch between the CNI's idea of it and the control plane's is a classic failure: `--cluster-cidr` on the controller manager, and the CNI's own config.

**Observe**

```sh
kubectl get nodes -o custom-columns=NAME:.metadata.name,CIDR:.spec.podCIDR
kubectl get pods -o wide
ssh -F ssh/config -J factory zain@10.10.10.130 'ip route; ip -d link show flannel.1'
kubectl -n kube-system get pod -l app=flannel -o wide
```

**Done when** — you can say which node a pod address belongs to from the address alone, and point at the route line that carries cross-node traffic.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean. Two pods, read both nodes' routes. | 10 min |
| **2** | Three pods, one of which is `hostNetwork: true`. Explain why its address is different. | 8 min |
| **3** | Cold, no notes. From a pod address alone, name its node and its route. | 5 min |

**Teardown** — delete the pods. Change nothing on the nodes.

**See also** — **TS5** is a node whose pods cannot be reached; **N6** is the Service layer sitting on top of this.
