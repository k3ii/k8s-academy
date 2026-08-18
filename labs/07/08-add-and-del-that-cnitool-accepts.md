<a id="add-and-del-that-cnitool-accepts"></a>
# Build artifact 1: `ADD` wires a netns, `DEL` unwires it, and `cnitool` is the judge

**Artifact** — `build/07-cni-academy/`: a CNI plugin in Go whose `ADD` creates a veth pair, moves one end into the sandbox netns, addresses it, sets a default route through the node bridge, and returns a spec-conformant result; whose `DEL` removes all of that and is idempotent; and whose `CHECK` says whether the wiring it claims is actually present. **Build artifact 1** of the phase's two.

**Rests on** — [exercise 7](07-what-replaces-stage-1.md) for the harness (which must already be green against the reference `bridge` plugin), [exercise 3](03-what-the-runtime-hands-a-plugin.md) for the input contract, and [exercise 1](01-the-four-paths-and-what-p0-wired.md)'s table for the list of steps. Every command in that table's *what a CNI must do* column becomes a function here; nothing in it is re-derived.

**Topology** — **none.** All of this is `forge` and a netns. `pair` is up and idle, and stays untouched until [exercise 10](10-the-plugin-the-kubelet-calls.md).

**Build**

```
build/07-cni-academy/
  cmd/academy/main.go     skel.PluginMain wiring, version support, and nothing else
  pkg/conf/conf.go        the NetConf struct, its JSON decode, and its defaults
  pkg/wire/bridge.go      the node bridge: create-if-absent, up, gateway address
  pkg/wire/veth.go        the pair, the move into the netns, address, routes
  pkg/wire/result.go      assembling types100.Result from what was actually configured
```

The IPAM half is [exercise 9](09-an-ipam-that-does-not-leak.md) and is deliberately not in this list; for now `ADD` may take the address from a `"testAddress"` field in the config so that the wiring can be finished and judged on its own.

What it must satisfy, as an interface rather than an implementation:

1. **`skel.PluginMain` with all four commands and a version list.** `ADD`, `DEL`, `CHECK` and `GC` are dispatched by the library; the version list is what `cnitool` negotiates against, and a plugin that advertises a version it does not implement fails in a way that looks like a config error.

2. **The config is read from stdin, once, and never from a file.** A plugin that opens `/etc/cni/net.d` itself is a plugin that behaves differently under `cnitool` and under the kubelet, which destroys the only fast loop this artifact has.

3. **The netns is entered exactly twice and never held.** Create the pair in the *host* namespace, move one end in, then do all in-namespace work inside a single `ns.WithNetNSPath` closure. Holding a netns handle across the return is how a plugin leaks a file descriptor per pod.

4. **The interface name inside the sandbox comes from `CNI_IFNAME`**, not from a constant. It is `eth0` in every Kubernetes invocation you will ever see, which is exactly why hard-coding it survives testing and fails the one time it matters.

5. **The result names both interfaces and gives the sandbox one an `ips` entry with a `gateway`.** The runtime reads `ips` to populate the pod's status; a result that configures a working network and reports an empty `ips` produces a pod with connectivity and no `podIP`, which is a fault [exercise 10](10-the-plugin-the-kubelet-calls.md) will show you from the API side.

6. **`DEL` succeeds when there is nothing to delete.** No netns, no veth, no address: exit 0, no output. This is a spec requirement and it is also the single most valuable line of defensive code in the plugin, because it is what stops a failed `ADD` from wedging a pod in `Terminating` forever.

7. **`CHECK` asserts rather than assumes.** It must look at the sandbox and report a mismatch — which means it is the one command that can catch a `DEL` that half-worked.

Build and install into the harness's own bin directory:

```sh
cd ~/src/k8s-academy/build/07-cni-academy
go build -o /opt/cni/lab-bin/academy ./cmd/academy
sudo tee /etc/cni/lab-net.d/10-harness.conflist >/dev/null <<'JSON'
{
  "cniVersion": "1.0.0",
  "name": "harness",
  "plugins": [
    { "type": "academy", "bridge": "br-academy", "subnet": "10.98.0.0/24",
      "gateway": "10.98.0.1", "testAddress": "10.98.0.20/24" }
  ]
}
JSON
```

**Gate** — [`cnitool` `ADD`/`DEL` against a netns](../../strands/build-mechanics.md#gates), which the strand lists as an objective harness. It is objective for a specific reason worth stating: **`cnitool` validates the result JSON against the spec's schema for the negotiated version**, so a result that is nearly right is rejected by somebody else's code rather than accepted by your own eyes.

```sh
sudo -i
export CNI_PATH=/opt/cni/lab-bin NETCONFPATH=/etc/cni/lab-net.d
ip netns add a1
cnitool add harness /var/run/netns/a1 | jq .
ip netns exec a1 ip -br addr show; ip netns exec a1 ip route
ip netns exec a1 ping -c2 10.98.0.1
cnitool check harness /var/run/netns/a1 && echo CHECK-OK
cnitool del harness /var/run/netns/a1
cnitool del harness /var/run/netns/a1 && echo SECOND-DEL-OK
ip netns exec a1 ip -br addr show
```

**Expect** — the same shape of output as the reference plugin produced in [exercise 7](07-what-replaces-stage-1.md), a `ping` to the gateway, `CHECK-OK`, and `SECOND-DEL-OK`. Then make the gate fail on purpose, twice, because **a gate nobody has watched fail is not evidence**:

- Return the result with `ips` omitted. `cnitool add` must reject it. Note the error text; you will see it again in [exercise 12](12-a-malformed-result-at-the-cri-seam.md) wearing kubelet's clothes.
- Skip the `ip link set eth0 up` inside the netns. `cnitool add` **succeeds** — nothing in the result is wrong — and `ping` fails. Then `cnitool check` catches it. That asymmetry is the argument for having written `CHECK` at all.

**Write down** — the `ADD` handler's steps in order, each annotated with the exact command from [exercise 1](01-the-four-paths-and-what-p0-wired.md)'s part 1 that it replaces, and the two steps that have **no** by-hand equivalent because P0 never needed them (reading a config off stdin, and reporting a result). That mapping is [the checklist's](../../phases/07-networking.md#checklist) 7.2 written artifact.

**Footprint note** — a small Go binary; the build is nothing next to [the measured figures](../../strands/build-mechanics.md#measurements). One bridge and one veth pair per run on `forge`.

**Teardown**

```sh
ip netns del a1; ip link del br-academy 2>/dev/null
ip -br link show | grep -c veth        # must be 0
```

**The harness stays** — [exercise 9](09-an-ipam-that-does-not-leak.md) drives it thirty more times.
