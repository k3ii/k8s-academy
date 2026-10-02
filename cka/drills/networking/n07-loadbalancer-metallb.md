<a id="n07"></a>
# N7 — A LoadBalancer Service, against MetalLB with a real address pool

**Reflex** · **Core** · **10 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Servicing and Networking / Service types

> **A `LoadBalancer` Service on a cluster with no load-balancer controller sits `<pending>` forever, and that is not a bug.** Kubernetes has no built-in implementation; the type is a request for something outside to act. Recognising `<pending>` as "nothing is listening for this" rather than "it is still working" is most of the value here.

> **Depends on B4**, which installs MetalLB in L2 mode with the pool `10.10.10.200–10.10.10.209`. That range is what [`lab-topologies`](../../../strands/lab-topologies.md#addresses) reserves for MetalLB, and **the reservation is prose only** — nothing in `tofu` enforces it — so confirm it is idle before relying on it.

**Do**

1. Create a `LoadBalancer` Service. Watch it get an `EXTERNAL-IP` out of the pool, and curl that address from your workstation.
2. **Then prove the negative.** Request `loadBalancerIP` or a pool annotation for an address outside the pool, and watch it stay `<pending>` with an event explaining why. That event is the thing to be able to find.
3. Exhaust the pool. Create more Services than it has addresses and see what the last one does. Ten addresses is a small number and this is a two-minute experiment.
4. Read what L2 mode actually does: one node answers ARP for the address, so all traffic for that Service enters through a single node. It is not load balancing across nodes, and knowing that explains the failure modes.
5. Note the layering. A LoadBalancer Service is also a NodePort, which is also a ClusterIP. All three are live at once; check all three.

**Observe**

```sh
kubectl get svc -o wide
kubectl describe svc <name> | sed -n '/Events/,$p'
kubectl -n metallb-system get ipaddresspool,l2advertisement
kubectl -n metallb-system logs -l app.kubernetes.io/component=controller --tail=30
curl -s http://10.10.10.20x/
```

**Done when** — the Service has an address from the pool, you curled it from outside the cluster, and you have seen a `<pending>` with its event and can say what caused it.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean. One Service, one pool, one failure case. | 10 min |
| **2** | A pool that is already partly used. Request a specific address. | 8 min |
| **3** | Cold, no notes, clock visible. | 5 min |

**Teardown** — delete the Services so their addresses return to the pool. Leave MetalLB; it is a B4 fixture.

**See also** — **N6** is the NodePort underneath. **N13** is the Gateway that takes an address from this same pool.
