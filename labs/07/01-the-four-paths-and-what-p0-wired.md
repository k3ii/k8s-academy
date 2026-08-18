<a id="the-four-paths-and-what-p0-wired"></a>
# The four communication paths, three of them already built in P0

**Artifact** — a four-row table: each communication path from `network/networking.md`, the [P0](../../phases/00-linux-primitives.md) exercise that already built it by hand, the one command that proves it, and **what a CNI plugin has to do so that the path holds for pods**. The table is the input to [exercise 8](08-add-and-del-that-cnitool-accepts.md); every row of it becomes a line of the `ADD` handler or an admission that the plugin does not do that part.

**Rests on** — P0, and deliberately nothing else. [Three things must be true before a ping crosses](../00/09-link-address-route.md) is the link/address/route triple, [a bridge is what replaces N² cables](../00/10-a-bridge-for-three.md) is the node's pod bridge in miniature, and [the namespace reaches the internet through one NAT rule](../00/11-masquerade-out.md) is pod egress. **None of that is repeated here.** If any of the three is not reproducible from memory in five minutes, the honest move is to go back and re-run them; [the phase's prerequisite row](../../phases/07-networking.md) says so in one sentence and it means it.

**Topology** — **none.** This runs on [`forge`](../../strands/lab-topologies.md#build-guest), which is a Debian guest with a kernel and root, and needs no cluster. Deferring the phase's first provision to [exercise 2](02-the-kernel-both-sides-must-share.md) is deliberate.

**Setup**

```sh
ssh zain@10.10.10.125
sudo -i
```

**Do — part 1: rebuild P0's bridge, without being taught it again.** Six commands, from your P0 write-up, not from here:

```sh
ip netns add ns1; ip netns add ns2
ip link add br-pods type bridge; ip link set br-pods up; ip addr add 10.244.0.1/24 dev br-pods
for n in 1 2; do
  ip link add veth$n type veth peer name eth0 netns ns$n
  ip link set veth$n master br-pods up
  ip netns exec ns$n ip addr add 10.244.0.1$n/24 dev eth0
  ip netns exec ns$n ip link set eth0 up
  ip netns exec ns$n ip route add default via 10.244.0.1
done
ip netns exec ns1 ping -c2 10.244.0.12
```

**Do — part 2: the one thing P0 could not do with one namespace per workload.** A pod is *several* processes in **one** netns, and that is where the first real Kubernetes-specific failure lives:

```sh
ip netns exec ns1 python3 -m http.server 8080 --bind 127.0.0.1 &
ip netns exec ns1 curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8080/     # second process, same netns
ip netns exec ns2 curl -s -m 2 -o /dev/null -w '%{http_code}\n' http://10.244.0.11:8080/
```

Then rebind and repeat:

```sh
kill %1
ip netns exec ns1 python3 -m http.server 8080 --bind 0.0.0.0 &
ip netns exec ns2 curl -s -m 2 -o /dev/null -w '%{http_code}\n' http://10.244.0.11:8080/
kill %1
```

**Expect** — `200` from inside `ns1` both times; from `ns2`, a timeout in the first run and `200` in the second. **The container did not change and the network did not change** — only the bind address did, and that is the whole of the difference between "my sidecar can reach it" and "the Service has no healthy endpoints". This is path 1 versus path 2, produced in four commands.

**Expect** the second `ping` in part 1 to work with no NAT, no proxy and no encapsulation anywhere. That is the model's first axiom stated as an observation rather than a slogan: pods talk to pods at their own addresses.

**Write down** — the table. Four rows, and the fourth is deliberately empty of a P0 exercise:

| Path | Built by hand in | Proved by | What a CNI must do |
|---|---|---|---|
| container ↔ container in one pod | *nothing in P0* — one netns held one workload | `curl 127.0.0.1:8080` from a second `ip netns exec` | nothing at all: the sandbox netns already exists when `ADD` is called |
| pod ↔ pod, same node | [P0 exercise 10](../00/10-a-bridge-for-three.md) | `ping` between the two netns | veth pair, bridge enslavement, address, route |
| pod ↔ pod, **different nodes** | — | *you cannot, on one guest* | the part [exercise 11](11-two-nodes-two-pod-cidrs-no-route.md) finds missing |
| pod → outside the cluster | [P0 exercise 11](../00/11-masquerade-out.md) | `ping 1.1.1.1` from `ns1` | one `MASQUERADE` rule, or a plugin in the chain that writes it |

Answer, from `network/networking.md` and in one sentence each: what does the design doc forbid between pods, and which of the four rows above is the one that makes an overlay network necessary?

**Footprint note** — two netns and a bridge on a guest that is already running: single-digit MiB, no cluster, **nothing subtracted from the [ceiling](../../strands/lab-topologies.md#ceiling)**. `forge` stays at 1536MB for the whole of P7 and [the index says why](README.md).

**Teardown**

```sh
ip netns del ns1; ip netns del ns2; ip link del br-pods
ip netns list; ip -br link show type bridge
```

Both commands must print nothing about this exercise. A leaked netns is invisible until [exercise 7](07-what-replaces-stage-1.md) puts a real plugin into one and gets the wrong answer. **No topology to release** — there is none yet.
