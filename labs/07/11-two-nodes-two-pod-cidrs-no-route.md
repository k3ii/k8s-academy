<a id="two-nodes-two-pod-cidrs-no-route"></a>
# The row of the table with no P0 exercise: make cross-node pod traffic work, and name what you just implemented

**Artifact** — cross-node pod-to-pod connectivity, and pod egress, both made to work by hand on top of your plugin, with **each command labelled with the name of the mechanism a real CNI would use instead**. This is the fourth row of [exercise 1](01-the-four-paths-and-what-p0-wired.md)'s table — the one P0 could not build, because it needs two machines.

**Rests on** — [exercise 10](10-the-plugin-the-kubelet-calls.md), and the state it deliberately left running. [P0's link/address/route triple](../00/09-link-address-route.md) is the diagnostic method used here and [P0's one NAT rule](../00/11-masquerade-out.md) is part 3; neither is re-taught.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued, with `.131` on your CNI and `.130` on the stock one.

**Do — part 1, establish the failure in both directions and diagnose each separately.** They are not the same failure and treating them as one is how an afternoon disappears:

```sh
kubectl -n mynet get pods -o wide          # your pods, on .131
kubectl -n kube-system get pods -o wide | grep <a non-hostNetwork pod on .130>
kubectl -n mynet exec deploy/web -- ping -c2 -W2 <a pod IP on .130>
ssh zain@10.10.10.130 'ping -c2 -W2 <one of your pod IPs>'
```

For each direction, work the triple in order and record which of the three is missing:

```sh
ssh zain@10.10.10.130 'ip route | grep -v ^default'
ssh zain@10.10.10.131 'ip route | grep -v ^default'
ssh zain@10.10.10.131 'sysctl net.ipv4.ip_forward; sudo iptables -S FORWARD | head'
```

**Do — part 2, add exactly what is missing, one command at a time.** After each one, re-test, so that every line of the write-up has an observation attached to it:

```sh
ssh zain@10.10.10.130 "sudo ip route add 10.98.0.0/24 via 10.10.10.131"
ssh zain@10.10.10.131 "sudo sysctl -w net.ipv4.ip_forward=1"
ssh zain@10.10.10.131 "sudo iptables -I FORWARD 1 -i br-academy -j ACCEPT; sudo iptables -I FORWARD 1 -o br-academy -j ACCEPT"
```

and, if the worker's own routing table has no path to the control plane's pod CIDR:

```sh
ssh zain@10.10.10.131 "sudo ip route add <the .130 pod CIDR> via 10.10.10.130"
```

**Do — part 3, egress.** A pod that can reach another pod still cannot reach the internet, for the reason [P0 exercise 11](../00/11-masquerade-out.md) established: the existing `MASQUERADE` rule matches a source CIDR that is not yours.

```sh
kubectl -n mynet exec deploy/web -- ping -c2 -W2 1.1.1.1
ssh zain@10.10.10.131 'sudo iptables -t nat -S POSTROUTING'
ssh zain@10.10.10.131 "sudo iptables -t nat -A POSTROUTING -s 10.98.0.0/24 ! -d 10.98.0.0/24 -j MASQUERADE"
kubectl -n mynet exec deploy/web -- ping -c2 -W2 1.1.1.1
```

**Expect** — part 1 to fail with **two different symptoms**: from the pod outward, no reply at all (the reply has nowhere to come back to); from the node inward, `Network is unreachable` from the sending host's own routing table, which is a locally-generated error and never reaches the wire. Being able to tell those two apart from the error text alone is worth more than either fix.

Expect part 2's route to be sufficient in exactly one direction, and expect the second direction to need the `FORWARD` rules — because the packet arrives at `.131` addressed to something that is not `.131`, and the node has to agree to forward it. **A plugin that wires a perfect veth and does not set `ip_forward` produces a pod network that works on one node and silently does not route.**

Expect the `ping 1.1.1.1` in part 3 to fail **with a reply that never comes rather than an error**, and to start working on the exact command that adds the NAT rule.

**Write down** — the completed table, four commands with four mechanism names:

| What you typed | What a real CNI does instead |
|---|---|
| `ip route add <peer cidr> via <peer node>` | **host-gw**: the same route, programmed on every node by an agent watching `node.spec.podCIDR` |
| — | **overlay**: VXLAN or Geneve, when the nodes are not on one L2 segment and cannot route to each other at all |
| — | **BGP**: the route advertised to the physical network, so the fabric knows the pod CIDRs |
| `sysctl`, `iptables -I FORWARD` | node configuration the agent asserts on every start, because something else will change it |
| `iptables -t nat -A POSTROUTING … MASQUERADE` | the same rule, or a `portmap`/`bandwidth`-style chained plugin, or [an eBPF program](28-a-counter-loaded-attached-read-detached.md) |

Also write [the checklist's](../../phases/07-networking.md#checklist) 7.2 artifact if you have not: the `ADD` handler's steps mapped one-to-one to the commands you typed by hand, now including the three in part 2 that your plugin **does not** do and a real one would.

**Answer in one line**: which of the two rows above with no command is the one that would be needed if `pair`'s two guests were not on the same bridge, and which mechanism does the stock CNI on this cluster actually use?

**Footprint note** — routes and rules. Nothing.

**Teardown** — leave everything; [exercise 12](12-a-malformed-result-at-the-cri-seam.md) breaks the plugin on top of this working state, which is the only way its failure is legible. **The topology stays.**

Write the undo down beside [exercise 10's](10-the-plugin-the-kubelet-calls.md), since these four commands are the other half of it and none of them survives a reboot — **which is itself the finding**: everything you did in part 2 is unpersisted, and an agent that reasserts it on every start is not defensive programming, it is the requirement.
