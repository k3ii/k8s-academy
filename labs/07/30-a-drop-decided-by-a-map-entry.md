<a id="a-drop-decided-by-a-map-entry"></a>
# A drop your program decides, on a veth your plugin made, at a hook that sees the ClusterIP

**Artifact** — `counter.c` extended into a drop-by-map program, attached to **a real pod's host-side veth on `10.10.10.131`**, dropping traffic whose destination matches an entry in a hash map — plus a four-row prediction table about direction and address, scored, that shows exactly where the tc hook sits relative to netfilter.

**Rests on** — [exercise 28](28-a-counter-loaded-attached-read-detached.md) for the load/attach/detach machinery and [exercise 10](10-the-plugin-the-kubelet-calls.md) for the veth: on `.131`, **the interface this program attaches to was created by the CNI plugin you wrote**. The phase's two build artifacts meet on one link, which is the reason this exercise is at the end of module 7.5 and not the start.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued. The program goes on `.131` only; `.130` and the control plane stay untouched, for [the same safety reason exercise 10 gave](10-the-plugin-the-kubelet-calls.md).

**Read** — before predicting anything, three answers:

| Read | Answer from it |
|---|---|
| `lifeofapacket.rst` ([item 28](../../strands/source-reading.md#area-5-networking)) | **List the hooks in the order a packet meets them** — XDP, tc ingress, tc egress, socket-level — and say which of them has an `skb` and which does not. |
| The same document, on enforcement | At which hook is **policy** enforced, and at which is the **service translation** done? Are they the same hook? |
| `iptables.rst` | State its contrast with kube-proxy in one sentence that does not use the word *faster* — it names a *place in the pipeline*, and that is the claim this exercise tests. |

**Setup — find the veth, which is the fiddly part**

```sh
ssh zain@10.10.10.131
kubectl -n svc get pods -o wide            # pick a web pod on this node
PID=$(sudo crictl inspect --output go-template --template '{{.info.pid}}' $(sudo crictl ps -q --name web | head -1))
sudo nsenter -t $PID -n ip -o link show eth0 | grep -o 'link-netnsid [0-9]*\|@if[0-9]*' ; sudo nsenter -t $PID -n cat /sys/class/net/eth0/iflink
IFINDEX=$(sudo nsenter -t $PID -n cat /sys/class/net/eth0/iflink)
ip -o link | awk -F: -v i="$IFINDEX" '$1+0==i {print $2}'      # the host-side name
```

Write down that name. Then confirm what it is: `ip -d link show <name>` names the peer and the type, and it should be a veth whose creation you can point at in [your own plugin's code](08-add-and-del-that-cnitool-accepts.md).

**Build** — one map and one branch on top of the existing program:

```
bpf/drop.c     BPF_MAP_TYPE_HASH  key __be32 dst_ip, value __u64 dropped
               parse L2 → L3 with a data_end bounds check on every read
               lookup dst; on hit, __sync_fetch_and_add the counter and return TC_ACT_SHOT
               on miss, return TC_ACT_OK
cmd/counter/main.go   -drop-ip flag: insert/delete the key at runtime, without reloading
```

The runtime map update is a requirement, not a convenience: **the program is loaded once and the policy changes underneath it**, which is the property that makes an eBPF datapath interesting and the property [exercise 31](31-kube-proxy-replaced-by-map-lookups.md) finds Cilium relying on for every Service in the cluster.

**Do — predict first.** Four combinations, each `DROPPED` or `THROUGH`, written before anything is attached. `CLUSTERIP` is `web`'s ClusterIP; `PODIP` is a `web` pod's address on `.130`:

| # | Attached at | Map key | Traffic | Prediction |
|---|---|---|---|---|
| 1 | ingress on host veth | `CLUSTERIP` | pod runs `curl http://CLUSTERIP/hostname` | |
| 2 | ingress on host veth | `PODIP` | pod runs `curl http://CLUSTERIP/hostname` | |
| 3 | ingress on host veth | `PODIP` | pod runs `curl http://PODIP:8080/hostname` | |
| 4 | egress on host veth | `CLUSTERIP` | pod runs `curl http://CLUSTERIP/hostname` | |

**Do — then run all four**

```sh
cd ~/src/k8s-academy/build/07-ebpf-academy && go generate ./... && go build ./...
sudo ./counter -iface <hostveth> -attach=tcx -dir=ingress -drop-ip <CLUSTERIP> &
kubectl -n svc exec <webpod> -- curl -sS -m3 http://<CLUSTERIP>/hostname; echo "exit=$?"
sudo bpftool map dump name drop_map
sudo ./counter -map-set <PODIP> -map-del <CLUSTERIP>          # policy change, no reload
kubectl -n svc exec <webpod> -- curl -sS -m3 http://<CLUSTERIP>/hostname; echo "exit=$?"
kubectl -n svc exec <webpod> -- curl -sS -m3 http://<PODIP>:8080/hostname; echo "exit=$?"
```

**Verify from outside** — three independent witnesses, none of them your program's own stdout:

```sh
sudo bpftool prog show | grep -i sched_cls
sudo bpftool map dump name drop_map
sudo nft list counters 2>/dev/null | head
sudo conntrack -L -d <CLUSTERIP> 2>/dev/null | head
```

**Expect** — rows 1 and 2 to disagree, and that disagreement is the exercise. A packet leaving the pod carries the **ClusterIP** as its destination when it reaches the host-side veth: the DNAT that turns it into a pod address happens in netfilter's `nat` `prerouting`, and **tc ingress runs before that**. So a map keyed on the ClusterIP drops it and a map keyed on the backend pod address does not — the same packet, the same pod, two answers, decided by *where in the pipeline you stood*.

Expect row 3 to drop, expect `conntrack` to show no entry for the dropped flows at all — the packet never reached the connection tracker — and expect **nothing in Kubernetes to report any of it**: no event, no readiness change, no log line, a healthy Service, three `Ready` endpoints. That is [exercise 19's silence](19-7c3-delete-one-endpoint-rule.md) reproduced at a different layer, and it is the shape of the enforcement proof [the capstone](34-the-capstone-a-network-you-wrote-and-a-drop-you-can-point-at.md) asks for.

Expect row 4 to be the direction trap: on a **host-side** veth, "egress" is traffic being sent *toward the pod*, so it is the reply that is dropped, not the request — and the symptom is a timeout rather than the immediate failure of row 1. Name the two directions from the host's point of view rather than the pod's in your notes, once, and then never get it wrong again.

**Gate** — the verifier, as in [exercise 28](28-a-counter-loaded-attached-read-detached.md), and this program gives it more to check: every read past the L2 header needs a `data_end` comparison the verifier can follow. If it loads first time, delete one bounds check and confirm it stops loading, because a bounds check that was never load-bearing is decoration.

**Write down** — the scored four-row table; one sentence placing tc ingress relative to netfilter's `nat prerouting` using row 1 and row 2 as the evidence; and the answer this hands to **row 8 of [exercise 24's](24-the-semantics-are-in-the-comments.md) prediction table** — an egress policy evaluated at this hook sees a Service address, not a backend address, which is a mechanism you have now measured rather than a claim you have read. [Exercise 32](32-the-prediction-scored-at-the-datapath.md) scores that row against Cilium; do not score it here.

**Footprint note** — one Go binary and one loaded program on `.131`, inside the worker's 2048MB. Unchanged: `pair` at 5.0GB, [`forge` at 1536MB](../../strands/build-mechanics.md#forge), Chaos Mesh's 582Mi still resident. This is the last exercise before [exercise 31](31-kube-proxy-replaced-by-map-lookups.md), which is where three things come out to make room for Cilium — [the index](README.md) has the order.

**Teardown** — detach, and then prove the pod is well, because a leaked drop program is the most confusing possible starting state for a Cilium install:

```sh
sudo kill %1
sudo bpftool prog show | grep -ci sched_cls          # expect 0
sudo tc filter show dev <hostveth> ingress ; sudo tc filter show dev <hostveth> egress
kubectl -n svc exec <webpod> -- curl -sS -m3 http://<CLUSTERIP>/hostname; echo
```

**The topology stays** — and [exercise 31](31-kube-proxy-replaced-by-map-lookups.md) begins by removing two things from it.
