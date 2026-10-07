<a id="n06"></a>
# N6 — NodePort: reached from the node, then from off the node

**Reflex** · **Core** · **10 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Servicing and Networking / Service types

> **A NodePort is open on every node, including nodes with none of the backing pods.** That is the single fact to internalise: hitting the worker reaches a pod on the control plane, because `kube-proxy` on the worker forwards it. People test only the node their pod is on and learn nothing.

**Do**

1. A Deployment with one replica, a NodePort Service. Note which node holds the pod.
2. Curl the NodePort on **that** node. Then curl it on the **other** node. Both work. Understand why before moving on.
3. Then from off-cluster entirely — your workstation against each node address in turn.
4. Read the port range: `30000–32767` by default, and a Service that asks for a port outside it is rejected at admission with a clear message. Let one be auto-assigned and then pin one explicitly.
5. **`externalTrafficPolicy`.** Flip it from `Cluster` to `Local`. Now only the node actually running a pod answers, and the other one refuses — but the client's source IP is preserved, which `Cluster` destroys by SNAT. This is the real trade and it is frequently the point of the question.
6. Note that a NodePort Service also gets a ClusterIP. NodePort is additive, not an alternative.

**Observe**

```sh
kubectl get svc <name> -o wide
kubectl get pods -o wide
curl -s http://10.10.10.130:<nodeport>/        # control plane
curl -s http://10.10.10.131:<nodeport>/        # worker -- also works
kubectl patch svc <name> -p '{"spec":{"externalTrafficPolicy":"Local"}}'
```

**Done when** — you can predict, for each node and each `externalTrafficPolicy`, whether the curl succeeds, before you run it.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean. Both nodes, both policies. | 10 min |
| **2** | Scale to two replicas across both nodes and re-reason. | 8 min |
| **3** | Cold, no notes. Imperative `expose --type=NodePort`. | 5 min |

**Teardown** — delete the namespace.

**See also** — **TS18** is this unreachable from off-node and the chain that finds out why. **N7** is the LoadBalancer that gets you out of hand-picking ports.
