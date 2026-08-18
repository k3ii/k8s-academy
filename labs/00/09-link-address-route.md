<a id="link-address-route"></a>
# Three things must be true before a ping crosses

**Claim** — a veth pair between two network namespaces carries traffic only when **link**, **address** and **route** are all correct, and each one fails differently when removed. You can name which of the three is missing from the error alone.

**Topology** — [`bare`](../../strands/lab-topologies.md#bare), still up, still as root.

**Do**

1. `ip netns add a` and `ip netns add b`. Inspect each: `ip netns exec a ip -br addr`. One interface, `lo`, and it is **down**.
2. `ip link add veth-a type veth peer name veth-b`. Both ends are in the host namespace right now — confirm with `ip -br link`.
3. Move the ends: `ip link set veth-a netns a`, `ip link set veth-b netns b`. Watch them vanish from the host's list. A veth end is *in* exactly one namespace.
4. Bring everything up: in each namespace, `ip link set lo up` and `ip link set veth-x up`.
5. Address them: `10.0.0.1/24` in `a`, `10.0.0.2/24` in `b`.
6. `ip netns exec a ping -c2 10.0.0.2`. It works.
7. **Now break each of the three, one at a time, and restore it before breaking the next.** Remove the route (`ip netns exec a ip route del 10.0.0.0/24`), then the address (`ip addr del`), then the link (`ip link set veth-a down`). Record the exact error text for each.

**Observe**

```sh
ip netns exec a ip -br link            # state: UP / DOWN / LOWERLAYERDOWN
ip netns exec a ip -br addr
ip netns exec a ip route
ip netns exec a ping -c2 -W1 10.0.0.2
```

**Expect** — three distinct errors, and this is the point of the exercise:

- **No route** → `connect: Network is unreachable`, immediately, with no packet sent.
- **No address** → also `Network is unreachable` on most kernels, because deleting the address deletes the connected route with it. Delete the route only and you see the pure case.
- **Link down** → the peer's state reads `LOWERLAYERDOWN` rather than `DOWN`, because a veth end reflects its partner. Pings time out rather than failing fast.

`LOWERLAYERDOWN` on one end when you downed the *other* is the veth-specific detail worth carrying: the pair is a single cable, and each end reports on the far side.

**Write down** — the three-line recipe as a checklist you can execute from memory — *link up, address, route* — plus the error each omission produces. [The checklist](../../phases/00-linux-primitives.md#checklist) asks for this build in **under 5 minutes with no notes**, so write the recipe as commands, not prose.

**Teardown** — `ip netns del a; ip netns del b`. Deleting a namespace deletes the veth ends inside it, and a veth pair with one end deleted takes the other with it, so this is complete. Confirm with `ip -br link` on the host. Guest stays up.
