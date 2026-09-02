<a id="four-ways-to-expose"></a>
# One Deployment, four exposures, four different components

**Claim** — take ClusterIP, NodePort, LoadBalancer and Ingress. For each one you can name the component that makes it work, and the OSI layer that it works at. You can also show what stops working when you remove that component.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), still up, with `deploy/web`.

**Setup** — this is the exercise that installs **MetalLB**, and every later phase inherits it. [The strand records `.200`–`.250` as reserved in prose only](../../strands/lab-topologies.md#unverified). No pool object exists anywhere yet. The `IPAddressPool` that you write in step 3 is therefore the first one in the curriculum. Commit it. It is a lab asset, and not scratch.

**Do**

1. **ClusterIP.** Run `kubectl expose deploy/web --port=80`. Then try to reach the Service three times: from a pod, from the shell of the node, and from the Mac. Two of the three attempts fail, and the two failures have different causes.

   ```sh
   kubectl run probe --rm -it --image=busybox --restart=Never -- wget -qO- web
   ```

2. **NodePort.** Change the type of the Service, and find the allocated port. Then hit the port on *both* node addresses. This includes the node that has no pod on it. Say what forwarded the request on that second node.
3. **LoadBalancer, through MetalLB.** Install MetalLB. Then write the pool and the advertisement:

   ```yaml
   apiVersion: metallb.io/v1beta1
   kind: IPAddressPool
   metadata: {name: lab, namespace: metallb-system}
   spec:
     addresses: ['10.10.10.200-10.10.10.250']
   ---
   apiVersion: metallb.io/v1beta1
   kind: L2Advertisement
   metadata: {name: lab, namespace: metallb-system}
   spec:
     ipAddressPools: [lab]
   ```

   Set the Service to `type: LoadBalancer`. Watch `EXTERNAL-IP` change from `<pending>` to an address. Then prove *how* it works, from a node. `ip neigh` and `arping` show one node answering ARP for an address that no interface owns.

4. **Ingress.** Install ingress-nginx. Give its own Service a VIP from the same pool. Then write one Ingress with a path rule and a host rule. Point the two rules at two different backend Services. Reach both backends through the single VIP.
5. Open the Service in a browser on the Mac. Use [the forward from the strand](../../strands/lab-topologies.md#access).
6. **Remove one component at a time, and record what breaks.** Scale the MetalLB controller to zero, then create a new LoadBalancer Service. Scale the ingress controller to zero, then re-request a host rule. Delete the DaemonSet of `kube-proxy` on one node, then retry the NodePort there. Restore each component before you move on.

**Expect** — ClusterIP is reachable from inside the cluster only. The attempt from the node shell fails for a *different* reason than the attempt from the Mac: the node has the `iptables` and IPVS rules, but it is not a cluster member for DNS. NodePort works on the node with no pod, because `kube-proxy` programmed a rule that forwards to the other node. That second hop is invisible here, and it is the subject of [P7](../../phases/07-networking.md). The L2 mode of MetalLB is one node answering ARP. There is no protocol and no load balancing across nodes. There is a gratuitous ARP and a claim. With the MetalLB controller stopped, a new Service sits at `<pending>` forever. That is exactly what a LoadBalancer Service does on any cluster with no cloud provider, and it is worth seeing once.

**Write down** — the table of four rows: the exposure, the component, the layer, and the symptom when that component is gone. [The checklist](../../phases/01-operate-shallow.md#checklist) asks for the four exposure types with their components.

**Footprint note** — MetalLB is a controller plus one speaker per node. Together with ingress-nginx it costs approximately 250Mi across the two nodes. Both stay up for the rest of the phase, because [the capstone](23-the-multi-service-app.md) needs them. That cost is inside the worker headroom of `pair`. It is still the first standing cost of the phase: from here on, the worker has room for one application less than before.

**Teardown** — delete the probe pods and any extra Services. But **keep MetalLB, ingress-nginx and the pool**. **The topology stays.**
