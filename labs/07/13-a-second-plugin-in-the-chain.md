<a id="a-second-plugin-in-the-chain"></a>
# Chaining: what the second plugin is handed, and which order `DEL` runs in

**Artifact** — the harness conflist with `portmap` chained after your plugin, the captured stdin of that second invocation showing your result arriving as `prevResult`, and a recorded answer to the one question a chain raises that a single plugin does not: **which order does `DEL` use?**

**Rests on** — [exercise 8](08-add-and-del-that-cnitool-accepts.md)'s plugin, [exercise 7](07-what-replaces-stage-1.md)'s harness, and [exercise 3](03-what-the-runtime-hands-a-plugin.md)'s shim trick, reused here on a plugin you did not write.

**Topology** — **none.** `forge`, and `pair` is left in the state [exercise 12](12-a-malformed-result-at-the-cri-seam.md) restored it to.

**Read** — `CONVENTIONS.md`, for one thing: the difference between a config field and a **capability**. `portMappings` is not in `SPEC.md`; it is a runtime-supplied capability, which is why the conflist declares `capabilities` and the value arrives in `runtimeConfig` rather than in the plugin's own config block.

**Setup** — chain it, and wrap it:

```sh
sudo -i
export CNI_PATH=/opt/cni/lab-bin NETCONFPATH=/etc/cni/lab-net.d
mv /opt/cni/lab-bin/portmap /opt/cni/lab-bin/portmap.real
cat > /opt/cni/lab-bin/portmap <<'SHIM'
#!/bin/sh
{ echo "=== $(date -Ins) $CNI_COMMAND ==="; } >> /tmp/portmap-in.log
tee -a /tmp/portmap-in.log | /opt/cni/lab-bin/portmap.real
SHIM
chmod +x /opt/cni/lab-bin/portmap
tee /etc/cni/lab-net.d/10-harness.conflist >/dev/null <<'JSON'
{
  "cniVersion": "1.0.0",
  "name": "harness",
  "plugins": [
    { "type": "academy", "bridge": "br-academy",
      "subnet": "10.98.0.0/24", "gateway": "10.98.0.1" },
    { "type": "portmap", "capabilities": { "portMappings": true } }
  ]
}
JSON
```

**Do**

```sh
ip netns add ch1
ip netns exec ch1 python3 -m http.server 8080 --bind 0.0.0.0 &
export CAP_ARGS='{"portMappings":[{"hostPort":18888,"containerPort":8080,"protocol":"tcp"}]}'
cnitool add harness /var/run/netns/ch1 | jq -c '{ips:.ips,ifs:[.interfaces[].name]}'
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:18888/
iptables -t nat -S | grep -i hostport | head
cnitool del harness /var/run/netns/ch1
curl -s -m2 -o /dev/null -w '%{http_code}\n' http://127.0.0.1:18888/ ; kill %1
```

**Observe** — the transcript, which is the artifact:

```sh
jq -c '{prev: (.prevResult|{ips:.ips, ifs:[.interfaces[].name]}), rc: .runtimeConfig}' < /tmp/portmap-in.log 2>/dev/null || cat /tmp/portmap-in.log
grep -c '=== .* ADD' /tmp/portmap-in.log; grep -c '=== .* DEL' /tmp/portmap-in.log
```

**Expect** — `portmap`'s stdin to contain three things: its own config block, a `runtimeConfig.portMappings` array carrying what `CAP_ARGS` supplied, and a **`prevResult` that is byte-for-byte the result your plugin returned**. A chained plugin does not re-discover the network; it is told, and it is told by you.

Expect the `curl` to `127.0.0.1:18888` to work while the netns has no idea it is reachable that way, and to stop working on the `del`. Expect the `iptables -t nat` output to name `CNI-HOSTPORT-DNAT` — the same kind of DNAT rule [exercise 16](16-a-clusterip-followed-to-its-kube-sep.md) reads for a Service, written by a plugin rather than by kube-proxy, which is a useful thing to have met before the `KUBE-` chains.

**Expect the ordering answer to be asymmetric.** `ADD` runs the chain front to back so that each plugin can build on the previous result. `DEL` runs it **back to front**, and the reason is worth writing down rather than memorising: `portmap`'s rules reference the address your plugin allocated, so they have to be removed before the address is freed. Confirm it from the transcript, not from this file — the `ADD` and `DEL` blocks are in the log in the order they happened.

**Expect a chained plugin's failure to abort the whole chain**, leaving the earlier plugins' work in place for the runtime to `DEL`. Provoke it once: point `portmap` at a `hostPort` already in use and watch `cnitool add` fail *after* your plugin has already allocated an address. Then check the store — that is [exercise 9](09-an-ipam-that-does-not-leak.md)'s leak, arriving through a completely different door, and the reason `GC` is not optional.

**Write down** — the three parts of the second plugin's stdin, the two orderings with the reason for the asymmetry, and one line on where in your own `ADD` you would read `prevResult` if `academy` were ever chained *after* something else.

**Footprint note** — nothing. A netns, a Python process, four `iptables` rules.

**Teardown** — un-shim, and clear up:

```sh
mv /opt/cni/lab-bin/portmap.real /opt/cni/lab-bin/portmap; rm -f /tmp/portmap-in.log
ip netns del ch1; ip link del br-academy 2>/dev/null
rm -rf /var/lib/cni/academy/harness
iptables -t nat -S | grep -c -i hostport      # must be 0
```

**Artifact 1 is finished here.** [The checklist's](../../phases/07-networking.md#checklist) two 7.2 items — the plugin, and the `ADD`-steps mapping — are both satisfied, and [module 7.3](../../phases/07-networking.md#m7-3) is reading, on the cluster that is still up. **The topology stays.**
