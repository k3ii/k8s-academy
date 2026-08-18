<a id="cut-a-link-then-slow-it"></a>
# Chaos drill 0.C2 — sever a link, then merely delay it

**Claim** — a severed link and a delayed link fail differently, at different layers, and on different timescales. You can distinguish them from the client's output alone, without access to the network.

**Topology** — [`bare`](../../strands/lab-topologies.md#bare), still up, still as root.

**Setup** — rebuild the two-namespace veth from [link, address, route](09-link-address-route.md). No tool is installed for this drill: [the standing principle](../../strands/chaos.md#principle) is that the mechanism is only the lesson when you inflict it by hand, and [Chaos Mesh does not arrive until P6](../../phases/06-kubelet-node.md).

**Do**

1. Start a continuous `ping` from `a` to `b` and leave it running where you can watch it.
2. From the host, `ip link del veth-a`. Read what the ping does — the exact line, and how long it took to say it.
3. Rebuild the pair and get the ping working again.
4. Now add latency instead of removing the link: `ip netns exec a tc qdisc add dev veth-a root netem delay 100ms`. Watch the RTT column.
5. Raise it: `tc qdisc change dev veth-a root netem delay 100ms 50ms distribution normal`. Watch jitter appear.
6. Add loss on top: `tc qdisc change dev veth-a root netem delay 100ms loss 20%`. Watch sequence numbers go missing while the ping keeps running.
7. Read where the qdisc lives: `ip netns exec a tc qdisc show`. Confirm it is attached to an interface *inside the namespace*, not to anything global.

**Observe**

```sh
ip netns exec a tc -s qdisc show dev veth-a    # sent / dropped / overlimits
ip netns exec a ping -c20 10.0.0.2             # rtt min/avg/max/mdev at the end
ip netns exec a ip -br link
```

**Expect** — deleting the veth produces `Network is unreachable` or `Destination Host Unreachable` **immediately**, because the route went with the interface. `netem delay` produces no errors at all: every packet arrives, the RTT column reads ~100ms, `mdev` grows once you add jitter, and with 20% loss the ping reports missing sequence numbers while never once saying the network is down. **The delayed case is the dangerous one** — nothing is broken, every health check passes, and the workload is unusable.

**Write down** — the two failure signatures side by side, and one line on where `netem` lives: a qdisc on an interface inside a network namespace, which is why the later `NetworkChaos` CR needs to name a pod — it is choosing whose namespace to attach a qdisc in. That sentence is what turns [the chaos catalogue](../../strands/chaos.md#catalogue) from a list of CRDs into a list of Linux primitives.

**Teardown** — `ip netns exec a tc qdisc del dev veth-a root`, then `ip netns del a b`. Confirm no `netem` survives: `tc qdisc show` on the host should list only `noqueue`/`fq_codel` defaults. Guest stays up.
