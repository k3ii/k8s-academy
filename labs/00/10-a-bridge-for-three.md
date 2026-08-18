<a id="a-bridge-for-three"></a>
# A bridge is what replaces N² cables

**Claim** — connecting three namespaces pairwise needs three veth pairs and three subnets; connecting them through one bridge needs three veth pairs, one subnet and no per-pair configuration. That difference is why every CNI puts a bridge on the node.

**Topology** — [`bare`](../../strands/lab-topologies.md#bare), still up, still as root.

**Do**

1. First, feel the problem. Sketch — do not build — what pairwise connection of three namespaces requires: how many veth pairs, how many addresses per namespace, how many routes. Then do the same for four and for ten. Write the two numbers down before continuing.
2. Build the bridge version. `ip link add br0 type bridge`, `ip link set br0 up`, `ip addr add 10.0.0.1/24 dev br0`.
3. For each of `a`, `b`, `c`: create a veth pair, move one end into the namespace, and `ip link set <host-end> master br0`. Bring every end and every `lo` up.
4. Address the namespace ends `10.0.0.11/24`, `.12`, `.13`. One subnet, one address each.
5. Ping between all three. Then ping `10.0.0.1` — the bridge itself — from inside each.
6. Read the bridge's learned MAC table.
7. Take one namespace's veth down and re-read the table. Watch the entry age out.

**Observe**

```sh
bridge link                            # which interfaces are enslaved
bridge fdb show br br0                 # learned MACs, one per namespace
ip -br link show master br0
ip netns exec a ping -c2 10.0.0.13
```

**Expect** — all three reach each other with no routes beyond the connected `/24`, because they are on one L2 segment and the bridge learns MACs from traffic it forwards. `bridge fdb show` lists one entry per namespace end, plus the permanent local entries. Pinging `10.0.0.1` works because the bridge has an address, which makes the host a fourth participant — and that is precisely the node's role in a pod network.

**Write down** — the two counts from step 1, and one sentence naming what the bridge replaces. Then the mapping that makes the rest of the curriculum legible: **a bridge per node, a veth per pod, one subnet per node** — which is what [P7](../../phases/07-networking.md) will call a CNI plugin doing its job.

**Teardown** — `ip netns del a b c`, then `ip link del br0`. Confirm `ip -br link` shows no `veth` and no `br0`. Guest stays up for [MASQUERADE](11-masquerade-out.md), which rebuilds this.
