<a id="an-address-claimed-by-arp"></a>
# A LoadBalancer IP that exists only as an ARP reply, and the client address you can only keep by giving something up

**Artifact** — a working `type: LoadBalancer` Service on a bridge with no load balancer on it, the ARP reply that claims its address recorded from **outside both nodes**, and a four-row table of what `externalTrafficPolicy` costs and buys, measured with `agnhost`'s `/clientip` rather than argued.

**Rests on** — [exercise 16](16-a-clusterip-followed-to-its-kube-sep.md) and [exercise 17](17-the-same-service-as-a-verdict-map.md), because the `KUBE-MARK-MASQ` condition you read there is the mechanism this exercise measures from the client side, and [exercise 14's](14-the-model-files-before-the-machine.md) prediction table, whose third and fourth rows are scored here.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Read** — `network/external-lb-source-ip-preservation.md`, and answer one question before installing anything: **what does the document say you lose by preserving the source address?** It is not subtle and it is not a performance cost, and having the answer written down first is what makes the measurements below a confirmation rather than a discovery.

**Setup** — MetalLB in L2 mode, with an address range that collides with nothing. Check first, because the lab bridge is shared with the persistent fleet and [the addresses are allocated in the strand](../../strands/lab-topologies.md#addresses):

```sh
ssh hopper 'for i in 200 201 202; do ping -c1 -W1 10.10.10.$i >/dev/null 2>&1 && echo "10.10.10.$i IN USE"; done'
helm repo add metallb https://metallb.github.io/metallb && helm repo update
helm install metallb metallb/metallb -n metallb-system --create-namespace \
  --set controller.resources.limits.memory=128Mi \
  --set speaker.resources.limits.memory=128Mi
kubectl -n metallb-system rollout status deploy/controller
kubectl apply -f - <<'YAML'
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata: {name: lab, namespace: metallb-system}
spec: {addresses: ["10.10.10.200-10.10.10.202"]}
---
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata: {name: lab, namespace: metallb-system}
spec: {ipAddressPools: [lab]}
YAML
```

**Do — part 1, the address that is only an ARP reply.** Two endpoints, one per node, and a LoadBalancer:

```sh
kubectl -n svc get pods -o wide          # one web pod per node, from exercise 20's spread constraint
kubectl -n svc expose deployment web --name=web-lb --type=LoadBalancer --port=80 --target-port=8080
kubectl -n svc get svc web-lb -o wide
```

From `hopper`, which is on the bridge and is not a node — this is the only place the ARP question can be asked honestly:

```sh
ssh hopper
ip neigh flush 10.10.10.200 2>/dev/null
ping -c2 10.10.10.200
ip neigh show 10.10.10.200
for h in 130 131; do echo -n "10.10.10.$h "; ssh zain@10.10.10.$h "ip link show | grep -A1 ether | head -2 | tr -s ' '"; done
```

**Expect** — the MAC that answers for `.200` to be **one of the two nodes' NICs**, not a MAC of its own. There is no load balancer; there is a node that has agreed to answer for an address that is not configured on any of its interfaces. Expect `ip addr show` on that node to have **no** `10.10.10.200` anywhere, which is the whole trick and is worth confirming rather than assuming.

**Do — part 2, the client address, four ways.** `agnhost` will tell you what source address arrived:

```sh
ssh hopper 'for i in 1 2 3 4 5 6; do curl -s http://10.10.10.200/clientip; echo; done'
kubectl -n svc patch svc web-lb -p '{"spec":{"externalTrafficPolicy":"Local"}}'
ssh hopper 'ip neigh flush 10.10.10.200; ping -c2 10.10.10.200; ip neigh show 10.10.10.200'
ssh hopper 'for i in 1 2 3 4 5 6; do curl -s http://10.10.10.200/clientip; echo; done'
```

Fill in the table from what you measured:

| Policy | source address `agnhost` sees | which nodes answer ARP | which pods can serve | second hop? |
|---|---|---|---|---|
| `Cluster` | | | | |
| `Local` | | | | |

Then the two rows that only appear when something goes wrong:

```sh
kubectl -n svc scale deployment web --replicas=1                  # one endpoint, on one node
kubectl -n svc get pods -o wide
ssh hopper 'ip neigh flush 10.10.10.200; ping -c2 -W2 10.10.10.200; ip neigh show 10.10.10.200'
kubectl -n svc scale deployment web --replicas=0
ssh hopper 'ip neigh flush 10.10.10.200; ping -c2 -W2 10.10.10.200; curl -s -m3 http://10.10.10.200/clientip || echo NO-ANSWER'
```

**Expect** — with `Cluster`, a source address that is a **node's** address, and requests served by pods on both nodes regardless of which node the packet arrived at. With `Local`, `hopper`'s own address preserved, only the node holding an endpoint answering ARP, and **no second hop** — which is exactly the trade the design doc named, and now you have both halves of it measured.

Expect scaling to one replica to move the ARP responder, and expect scaling to zero to make the address stop existing entirely. **A `Local` LoadBalancer's availability is a function of where the scheduler put the pods**, which is a sentence worth keeping: it is the reason `Local` is not a free upgrade, and it scores [exercise 14's](14-the-model-files-before-the-machine.md) third and fourth prediction rows.

**Expect a limit this lab cannot cross, and record it rather than working around it.** `hopper` is on the bridge, so its address is genuinely preserved. **A request from the Mac is not**: it reaches the bridge through NAT, so the "preserved" source address is the bastion's and the preservation you measured is real but the client you care about is invisible behind it. That is what [the source-reading strand means](../../strands/source-reading.md#area-5-networking) by a NAT'd bridge with no physical port making this a lab in itself. Curl from both places and put both results in the table; **the honest deliverable is the pair, not the one that looks better.**

**Write down** — the table, the ARP evidence with the MAC and the node it belongs to, the two-source-address finding, and one sentence naming what a cloud provider's load balancer does that MetalLB in L2 mode cannot (there is more than one answer; one is about bandwidth and one is about failover time).

**Footprint note** — MetalLB is small: one controller and a `speaker` DaemonSet, capped above at 128Mi each, so around **250–300 Mi across two nodes**. With [Chaos Mesh's 582 Mi](../../strands/chaos.md#install) already resident, the cluster is now carrying about 900 Mi of tooling inside 5.0GB of guests. That is comfortable, and it is the high-water mark until [exercise 31](31-kube-proxy-replaced-by-map-lookups.md), where **Chaos Mesh comes out before Cilium goes in** — [the index](README.md) explains why that ordering is the smallest change rather than raising a guest.

**Teardown** — restore the replica count and drop the LoadBalancer, but **keep MetalLB installed**: [exercise 33](33-7c4-a-policy-that-reads-correct.md) uses an external client and re-creating the pool later costs more than the memory it holds.

```sh
kubectl -n svc scale deployment web --replicas=2
kubectl -n svc delete svc web-lb
ssh hopper 'ping -c1 -W2 10.10.10.200 || echo GONE'
```

**The topology stays.**
