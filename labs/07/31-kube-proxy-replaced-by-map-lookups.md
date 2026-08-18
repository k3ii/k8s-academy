<a id="kube-proxy-replaced-by-map-lookups"></a>
# The same DNAT, a third time: chains, then a verdict map, then a map entry with no netfilter in it

**Artifact** — Cilium installed on [`pair`](../../strands/lab-topologies.md#pair) in kube-proxy-replacement mode, with **`web`'s ClusterIP→backend mapping shown three ways from your own saved evidence**: the `KUBE-SVC`/`KUBE-SEP` chains from [exercise 16](16-a-clusterip-followed-to-its-kube-sep.md), the verdict map from [exercise 17](17-the-same-service-as-a-verdict-map.md), and `cilium bpf lb list` — one service, three representations, one of which has no kube-proxy behind it at all.

**Rests on** — [exercise 30](30-a-drop-decided-by-a-map-entry.md), because "Cilium uses eBPF" is now a statement about a hook you have personally attached a program to on this exact veth. Also on the two saved dumps: `/root/nat-iptables-mode.rules` from [exercise 16](16-a-clusterip-followed-to-its-kube-sep.md) and the `nft` dump from [exercise 17](17-the-same-service-as-a-verdict-map.md). If they are gone, this exercise is a demo instead of a comparison.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued, and **this is the exercise where its tenancy changes**. Read the footprint note before the first command, because two things come out before anything goes in.

**Setup — three removals, in this order, each with its own lesson**

```sh
helm uninstall chaos-mesh -n chaos-mesh && kubectl delete ns chaos-mesh
kubectl get crd | grep -c chaos-mesh.org        # not zero — uninstall does not remove CRDs
kubectl api-resources --api-group=chaos-mesh.org
```

```sh
ssh zain@10.10.10.131 'sudo mv /etc/cni/net.d/05-academy.conflist /root/05-academy.conflist.kept; ls /etc/cni/net.d'
ssh zain@10.10.10.131 'sudo ls /var/lib/cni/academy/*/ | head'      # your IPAM's remaining leases
```

Your conflist is numbered `05-`, and so is Cilium's. Moving yours aside is not tidiness — it is the [discovery order from exercise 10](10-the-plugin-the-kubelet-calls.md) deciding which of two plugins wires the next pod, and leaving both in place makes that decision alphabetical. Then run [your own `GC`](09-an-ipam-that-does-not-leak.md) once the pods are gone: it is the last chance to use it, and a leftover lease directory is the finding either way.

```sh
kubectl -n kube-system delete ds kube-proxy
kubectl -n kube-system delete cm kube-proxy
ssh zain@10.10.10.131 'sudo nft list table ip kube-proxy | head -5'      # still there
ssh zain@10.10.10.130 'sudo nft list table ip kube-proxy | head -5'
```

**The rules outlive the DaemonSet.** Deleting the controller does not undo its writes — the same property as [the netlink filter that survived `kill -9`](28-a-counter-loaded-attached-read-detached.md) and [the qdisc a dead helper pod orphans](../../strands/chaos.md#mechanisms). Flush them by hand on both nodes and check the Service breaks *before* Cilium takes over, so that when it works again you know which component made it work:

```sh
for n in 130 131; do ssh zain@10.10.10.$n 'sudo nft delete table ip kube-proxy; sudo nft list tables'; done
kubectl -n svc exec <webpod> -- curl -sS -m3 http://<CLUSTERIP>/hostname; echo "exit=$?"
```

**Do — install it**

```sh
helm repo add cilium https://helm.cilium.io && helm repo update
helm install cilium cilium/cilium -n kube-system --version 1.17.6 \
  --set kubeProxyReplacement=true \
  --set k8sServiceHost=10.10.10.130 --set k8sServicePort=6443 \
  --set operator.replicas=1 \
  --set hubble.enabled=false \
  --set ipam.mode=kubernetes \
  --set cni.exclusive=false
kubectl -n kube-system rollout status ds/cilium
kubectl -n kube-system delete pod -l app=web --ignore-not-found
kubectl -n svc delete pod --all       # pods keep the network they were created with
kubectl -n svc get pods -o wide
```

`cni.exclusive=false` is a **deliberate deviation from the default**, and the default is right for a real cluster: with it true, the agent removes every other conflist from `/etc/cni/net.d` and keeps removing them, which is exactly what you want when one CNI owns a node. It is false here so that [the capstone](34-the-capstone-a-network-you-wrote-and-a-drop-you-can-point-at.md) can put your plugin back on `.131` for one pod. Note in your write-up what the true setting implies for a migration: there is no supported moment when two CNIs each half-own a node.

The pod deletion is required, not defensive: a running pod holds the veth and the addresses whichever plugin created it, so the cluster is only fully on Cilium once every pod has been recreated. Say in your notes what that implies for a real cluster's CNI migration.

**Do — the three representations, side by side**

```sh
kubectl -n kube-system exec ds/cilium -- cilium-dbg status --brief
kubectl -n kube-system exec ds/cilium -- cilium-dbg status | grep -i 'kubeproxy\|routing\|masquerad'
kubectl -n kube-system exec ds/cilium -- cilium-dbg bpf lb list | grep -A3 <CLUSTERIP>
kubectl -n kube-system exec ds/cilium -- cilium-dbg service list | head
grep -c 'KUBE-SEP' /root/nat-iptables-mode.rules
ssh zain@10.10.10.131 'sudo nft list tables; sudo bpftool prog show | grep -c .; sudo bpftool map show | grep -c .'
```

Fill in one row per backend and one line per representation:

| Representation | Where the ClusterIP appears | Where the backend appears | What performs the lookup |
|---|---|---|---|
| `KUBE-SVC`/`KUBE-SEP` chains ([16](16-a-clusterip-followed-to-its-kube-sep.md)) | | | |
| `service-ips` verdict map ([17](17-the-same-service-as-a-verdict-map.md)) | | | |
| `cilium bpf lb list` | | | |

**Read** — re-read `lifeofapacket.rst` ([item 28](../../strands/source-reading.md#area-5-networking)) now, against `bpftool prog show` on the node, and answer two things you could not have answered before writing your own program: **which hooks does Cilium occupy on which interfaces**, and **at which of them does the service translation happen** — noting whether that is before or after the point where [exercise 30's](30-a-drop-decided-by-a-map-entry.md) program saw a ClusterIP rather than a pod address. Then answer the question `iptables.rst` is really making: which of kube-proxy's three backends does Cilium *skip*, and which one is still underneath it for the traffic Cilium does not handle?

**Expect** — the Service to work again with **no netfilter table named `kube-proxy` on either node**, `cilium-dbg status` reporting `KubeProxyReplacement: True`, and `bpftool prog show` to have gone from the one program you loaded to some dozens. Expect the ClusterIP to appear in `cilium bpf lb list` as a **key with a list of backend slots**, in the same shape as [exercise 17's map element](17-the-same-service-as-a-verdict-map.md) and nothing like [exercise 16's chain-per-endpoint](16-a-clusterip-followed-to-its-kube-sep.md) — and to be able to say, from your own three-row table, that **the interesting difference between backends two and three is not the data structure but which subsystem owns it**.

Expect one honest surprise: `nft list tables` is not empty. Cilium still writes some rules, and finding out which and why is the last row of the table.

**Write down** — the three-row representation table; the `KubeProxyReplacement` line; the before/after `bpftool prog show` counts; and the sentence from `iptables.rst` translated into your own evidence. This is the entry [the capstone](34-the-capstone-a-network-you-wrote-and-a-drop-you-can-point-at.md) uses to close the loop on [P6's third owed citation](../../phases/06-kubelet-node.md#capstone), which was `syncProxyRules` reprogramming nftables — a function that is no longer running on this cluster.

**Footprint note — this is the phase's tightest moment and it is managed by ordering, not by more RAM.** Cilium is a DaemonSet with an agent per node plus an operator, and [the phase's own ecosystem note](../../phases/07-networking.md#ecosystem) records that it is **not co-resident with the heavy tooling** on this host. Three tenants wanted to be resident at once here: [Chaos Mesh's 582Mi](../../strands/chaos.md#install), [MetalLB's 250–300 Mi](21-an-address-claimed-by-arp.md), and Cilium. The smallest change that removes the clash is the removal above — **Chaos Mesh comes out, and the drills that needed it are already done** ([7.C1](20-7c1-a-partition-named-by-path.md), [7.C2](26-7c2-it-was-dns.md)); [7.C3](19-7c3-delete-one-endpoint-rule.md) and [7.C4](33-7c4-a-policy-that-reads-correct.md) are by-hand and need nothing installed. No guest is resized, and [`forge` stays at 1536MB](../../strands/build-mechanics.md#forge) as it has all phase.

Measure it rather than trusting the arithmetic, and record the number — it is the figure P9 will need:

```sh
for n in 130 131; do ssh zain@10.10.10.$n 'free -m | head -2; ps -o rss=,comm= -C cilium-agent'; done
```

MetalLB stays because [exercise 21's](21-an-address-claimed-by-arp.md) address pool is still in use and it is the smaller of the two. If the worker is under pressure after this install, `helm uninstall metallb` is the next removal — in that order, and stated here so the decision is not made under time pressure.

**Teardown** — nothing to remove: Cilium is now this cluster's CNI and the next three exercises are its. Confirm the state you are leaving behind, because [exercise 32](32-the-prediction-scored-at-the-datapath.md) scores a prediction against it and a half-migrated cluster would score it wrong:

```sh
kubectl -n svc get pods -o wide          # every pod recreated under Cilium
kubectl -n kube-system get ds            # no kube-proxy
ssh zain@10.10.10.131 'ls /etc/cni/net.d'
```

**The topology stays** — through [32](32-the-prediction-scored-at-the-datapath.md), [33](33-7c4-a-policy-that-reads-correct.md) and [the capstone](34-the-capstone-a-network-you-wrote-and-a-drop-you-can-point-at.md), which is where it goes.
