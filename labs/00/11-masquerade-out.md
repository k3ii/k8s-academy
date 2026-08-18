<a id="masquerade-out"></a>
# The namespace reaches the internet through one NAT rule

**Claim** — a namespace on a private bridge reaches the outside world when two things are added and not before: a default route pointing at the bridge, and a `MASQUERADE` rule that rewrites its source address on the way out. Remove either and you can name which one from the symptom.

**Topology** — [`bare`](../../strands/lab-topologies.md#bare), still up, still as root. The guest itself sits behind [`factory`'s own NAT](../../strands/lab-topologies.md#access), so you are about to build a second layer of exactly the same thing.

**Do**

1. Rebuild the bridge and one namespace `a` at `10.0.0.11/24`, as in [the bridge exercise](10-a-bridge-for-three.md).
2. From inside `a`, `ping -c2 10.10.10.1` — the guest's own gateway. It fails. Read the error.
3. Add the default route: `ip netns exec a ip route add default via 10.0.0.1`. Ping again. It *still* fails, but differently — this is the step worth slowing down for.
4. Enable forwarding on the host: `sysctl -w net.ipv4.ip_forward=1`.
5. Add the NAT rule: `iptables -t nat -A POSTROUTING -s 10.0.0.0/24 ! -o br0 -j MASQUERADE`. Ping again.
6. `ping -c2 1.1.1.1` from inside `a`, and watch the counters on the rule move.
7. Delete the `MASQUERADE` rule and ping again. Then put it back and instead set `ip_forward=0`. Two different failures.

**Observe**

```sh
iptables -t nat -L POSTROUTING -v -n      # packet and byte counters per rule
sysctl net.ipv4.ip_forward
ip netns exec a ip route
tcpdump -ni br0 icmp                       # run during step 3 to see the reply that never comes back
```

**Expect** — after step 3 the packets *leave*: `tcpdump` on `br0` shows ICMP echo requests with source `10.0.0.11` going out, and nothing coming back, because the far side has no route to `10.0.0.0/24`. That is the signature of missing NAT and it is completely different from `Network is unreachable`, which is the signature of a missing route. With `MASQUERADE`, the source is rewritten to the guest's own `10.10.10.192` and replies find their way home; the rule's counters increment once per connection.

**Write down** — the two symptoms next to their causes: **`Network is unreachable` → no route, the packet was never sent**; **silence with visible egress → no NAT, the reply has nowhere to return to**. Then note that `-j MASQUERADE` here is the same target every CNI installs for pod egress, differing only in which chain it lands in and who wrote it.

**Teardown** — `iptables -t nat -D POSTROUTING -s 10.0.0.0/24 ! -o br0 -j MASQUERADE`, `sysctl -w net.ipv4.ip_forward=0`, `ip netns del a`, `ip link del br0`. **Check `iptables -t nat -L -n` is back to empty** — an orphaned NAT rule survives every namespace you delete and will silently affect [the capstone](20-container-from-scratch.md). Guest stays up.
