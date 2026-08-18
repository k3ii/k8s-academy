<a id="four-ways-to-expose"></a>
# One Deployment, four exposures, four different components

**Claim** — for each of ClusterIP, NodePort, LoadBalancer and Ingress you can name the component that makes it work and the OSI layer it works at, and show what stops working when you remove that component.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), still up, with `deploy/web`.

**Setup** — this is the exercise that installs **MetalLB**, and every later phase inherits it. [The strand records `.200`–`.250` as reserved in prose only](../../strands/lab-topologies.md#unverified) — there is no pool object anywhere yet, so the `IPAddressPool` you write in step 3 is the first one in the curriculum. Commit it; it is a lab asset, not scratch.

**Do**

1. **ClusterIP.** `kubectl expose deploy/web --port=80`. Reach it from a pod, then try to reach it from the node's shell, then from the Mac. Two of those three fail, and the two failures have different causes.

   ```sh
   kubectl run probe --rm -it --image=busybox --restart=Never -- wget -qO- web
   ```

2. **NodePort.** Change the type and find the allocated port. Hit it on *both* node addresses, including the node with no pod on it. Say what forwarded the request on that second node.
3. **LoadBalancer via MetalLB.** Install MetalLB, then write the pool and the advertisement:

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

   Set the Service to `type: LoadBalancer` and watch `EXTERNAL-IP` go from `<pending>` to an address. Then prove *how*, from a node: `ip neigh` and `arping` show one node answering ARP for an address no interface owns.

4. **Ingress.** Install ingress-nginx, give its own Service a VIP from the same pool, and write one Ingress with a path rule and a host rule pointing at two different backend Services. Reach both through the single VIP.
5. Open it in a browser on the Mac with [the forward from the strand](../../strands/lab-topologies.md#access).
6. **Remove the component, one at a time**, and record what breaks: scale the MetalLB controller to zero and create a new LoadBalancer Service; scale the ingress controller to zero and re-request a host rule; delete `kube-proxy`'s DaemonSet on one node and retry the NodePort there. Restore each before moving on.

**Expect** — ClusterIP is reachable from inside the cluster only, and the node-shell attempt fails for a *different* reason than the Mac's: the node has the `iptables`/IPVS rules but is not a cluster member for DNS. NodePort works on the node with no pod because `kube-proxy` programmed a rule that forwards to the other node — the second hop is invisible and is [P7](../../phases/07-networking.md)'s subject. MetalLB's L2 mode is one node answering ARP: no protocol, no load balancing across nodes, just a gratuitous ARP and a claim. With the MetalLB controller stopped, a new Service sits at `<pending>` forever — which is exactly what a LoadBalancer Service does on any cluster with no cloud provider, and is worth having seen once.

**Write down** — the four-row table: exposure, component, layer, and the symptom when that component is gone. [The checklist](../../phases/01-operate-shallow.md#checklist) asks for the four exposure types with their components.

**Footprint note** — MetalLB (a controller plus a speaker per node) and ingress-nginx together are roughly 250Mi across the two nodes, and both stay up for the rest of the phase — [the capstone](23-the-multi-service-app.md) needs them. That is inside `pair`'s worker headroom, but it is the phase's first standing cost: from here on, the worker has one fewer application's worth of room than it did.

**Teardown** — delete the probe pods and any extra Services, but **keep MetalLB, ingress-nginx and the pool**. **The topology stays.**
