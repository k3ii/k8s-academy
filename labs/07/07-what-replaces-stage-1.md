<a id="what-replaces-stage-1"></a>
# The fast loop for an artifact that has no stage 1: `cnitool` against a netns you made

**Artifact** — a working `cnitool` harness on [`forge`](../../strands/lab-topologies.md#build-guest), **proved against the reference `bridge` plugin before your own code exists**, plus a written list of the three things this loop cannot exercise and therefore hands to [exercise 10](10-the-plugin-the-kubelet-calls.md) alone.

**Rests on** — [exercise 3](03-what-the-runtime-hands-a-plugin.md) for the input contract this harness reproduces, and [exercise 1](01-the-four-paths-and-what-p0-wired.md) for the netns it wires into.

**Both of P7's artifacts are listed with no stage 1** in [the artifact table](../../strands/build-mechanics.md#artifact-table), and the reason is real: you cannot wire a netns or attach a tc hook from outside a node. But *no stage 1* is not the same as *no fast loop*, and this exercise is where the difference gets named. **What the other nine artifacts get is an edit/run loop that reaches the live API from outside the cluster. What these two get is an edit/run loop that reaches a real kernel with no Kubernetes in it at all** — `cnitool` here, `bpftool` and `ip link` at [exercise 28](28-a-counter-loaded-attached-read-detached.md). Same seconds-long cycle, same "the thing under test is not a simulation", different axis: out-of-Kubernetes instead of out-of-cluster.

That works only because `forge` is a Debian guest with the same kernel as the nodes — which is what [exercise 2](02-the-kernel-both-sides-must-share.md) established and why it ran second.

**Topology** — **none.** `pair` is up and idle; nothing here touches it.

**Setup**

```sh
ssh zain@10.10.10.125
go install github.com/containernetworking/cni/cnitool@latest
git clone https://github.com/containernetworking/plugins ~/src/cni-plugins
cd ~/src/cni-plugins && ./build_linux.sh && ls bin/
```

Two directories, kept deliberately separate from anything a node uses:

```sh
sudo mkdir -p /opt/cni/lab-bin /etc/cni/lab-net.d
sudo cp ~/src/cni-plugins/bin/{bridge,host-local,loopback,portmap} /opt/cni/lab-bin/
sudo tee /etc/cni/lab-net.d/10-harness.conflist >/dev/null <<'JSON'
{
  "cniVersion": "1.0.0",
  "name": "harness",
  "plugins": [
    { "type": "bridge", "bridge": "br-harness", "isGateway": true,
      "ipam": { "type": "host-local", "subnet": "10.99.0.0/24",
                "routes": [{ "dst": "0.0.0.0/0" }] } }
  ]
}
JSON
```

**Do — prove the harness with somebody else's plugin.** This ordering is the whole method: when your own `ADD` fails at [exercise 8](08-add-and-del-that-cnitool-accepts.md), the harness must already be known good, or you will spend an evening debugging a `conflist` typo as if it were a bug in your code:

```sh
sudo -i
export CNI_PATH=/opt/cni/lab-bin NETCONFPATH=/etc/cni/lab-net.d PATH=$PATH:/root/go/bin:/home/zain/go/bin
ip netns add h1
cnitool add harness /var/run/netns/h1 | tee /tmp/add.json
ip netns exec h1 ip -br addr show
ip netns exec h1 ping -c2 10.99.0.1
cnitool check harness /var/run/netns/h1 && echo CHECK-OK
cnitool del harness /var/run/netns/h1
ip netns exec h1 ip -br addr show
```

**Expect** — a result JSON on stdout with `cniVersion`, an `interfaces` array naming both ends of the veth, and an `ips` entry in `10.99.0.0/24`; an address inside `h1` that matches it; a `ping` to the gateway; and after `del`, an `h1` with nothing but `lo`. The whole cycle is under a second, which is the number that matters — it is what makes this a loop rather than a deployment.

**Expect `cnitool del` to be idempotent.** Run it twice. The second run must exit 0 and print nothing, because [the spec](../../strands/source-reading.md#area-5-networking) requires it and because the kubelet will call `DEL` more than once for the same sandbox in the normal course of events, not only when something has gone wrong.

**Write down — the three things this loop does not test**, because they are the entire content of [exercise 10](10-the-plugin-the-kubelet-calls.md) and the reason stage 2 carries more risk here than in any other phase:

1. **Discovery** — `cnitool` is told which config to use by name. The kubelet is not: it takes the *lexically first* file in `/etc/cni/net.d`, and getting that ordering wrong is a plugin that is installed, correct, and never called.
2. **Invocation** — `cnitool` builds `CNI_ARGS` itself. The runtime builds them from the sandbox, as [exercise 3](03-what-the-runtime-hands-a-plugin.md) captured, and passes `CNI_CONTAINERID` values your IPAM has never seen.
3. **The CRI seam** — nothing here can produce a kubelet that rejects a sandbox. That failure mode has its own exercise ([12](12-a-malformed-result-at-the-cri-seam.md)) precisely because the harness cannot reach it.

**Footprint note** — the reference plugins build in seconds and are a few MiB of binaries; `cnitool` is smaller. Nowhere near [the 564 MiB the strand measured](../../strands/build-mechanics.md#measurements) for a controller-runtime link, which is why **`forge` needs no resize this phase**.

**Teardown** — the netns, and only the netns. **The harness stays** — [exercises 8](08-add-and-del-that-cnitool-accepts.md), [9](09-an-ipam-that-does-not-leak.md) and [13](13-a-second-plugin-in-the-chain.md) all drive it:

```sh
ip netns del h1
ip link del br-harness 2>/dev/null; ip -br link show | grep -c veth
```

That last count must be zero. A leaked veth pair from a failed `DEL` is the most common way this harness starts lying to you.
