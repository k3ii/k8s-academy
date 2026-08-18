<a id="an-ipam-that-does-not-leak"></a>
# An address allocator, and the leak you can only produce by killing it mid-`ADD`

**Artifact** — `pkg/ipam/` in the plugin: a file-backed allocator under `/var/lib/cni/academy/<network>/`, one file per address named for the address and containing the container id that holds it, plus **three recorded results**: forty clean cycles leaving an empty store, an exhausted subnet failing as a CNI error rather than a panic, and a deliberately leaked address recovered by `GC`.

**Rests on** — [exercise 8](08-add-and-del-that-cnitool-accepts.md), which left the address hard-coded in the config. This exercise removes `testAddress` and is the last thing artifact 1 needs before a kubelet can call it.

**Topology** — **none.** `forge` and the [harness](07-what-replaces-stage-1.md).

**Build** — what the allocator must satisfy:

1. **The file name is the address; the contents are the holder.** That is the reference `host-local` design and it is worth copying rather than improving on, because the file system provides the mutual exclusion: `O_CREAT|O_EXCL` either wins the address or fails, with no lock file and no daemon.

2. **`DEL` frees by container id, not by address.** `DEL` is handed `CNI_CONTAINERID` and a netns that may already be gone; the address is not recoverable from a namespace that no longer exists. An allocator that can only free by address is an allocator that leaks every time a sandbox dies badly — which is most of the times that matter.

3. **`.1` of the subnet is the gateway and is never allocatable**, and neither is the network or broadcast address. Getting this wrong produces a pod that cannot reach its own gateway, one time in 253.

4. **Exhaustion returns a `types.Error` with a code**, not a nil pointer dereference. The runtime prints your error text into the pod's events, and that text is the only diagnostic anyone will have.

5. **`GC` takes the list of container ids the runtime still knows about** and releases everything else. This is the CNI 1.1 command that exists for exactly the failure produced in part 3, and implementing it is four lines once `DEL` frees by holder.

**Do — part 1, forty cycles.** The store must be empty at the end, which is a stronger statement than "it works":

```sh
sudo -i
export CNI_PATH=/opt/cni/lab-bin NETCONFPATH=/etc/cni/lab-net.d
for i in $(seq 1 40); do
  ip netns add c$i
  cnitool add harness /var/run/netns/c$i >/dev/null || echo "ADD failed at $i"
  cnitool del harness /var/run/netns/c$i   || echo "DEL failed at $i"
  ip netns del c$i
done
ls -1 /var/lib/cni/academy/harness/ | wc -l
```

**Do — part 2, exhaustion.** Point the config at a `/29` — six usable addresses — and ask for seven:

```sh
sudo sed -i 's#10.98.0.0/24#10.98.1.0/29#; s#10.98.0.1#10.98.1.1#' /etc/cni/lab-net.d/10-harness.conflist
for i in $(seq 1 7); do
  ip netns add x$i
  cnitool add harness /var/run/netns/x$i >/dev/null 2>/tmp/err$i || echo "$i: $(cat /tmp/err$i)"
done
ls -1 /var/lib/cni/academy/harness/
```

**Do — part 3, the leak.** Kill the plugin after it has reserved an address and before it has finished wiring. A `SIGKILL` mid-`ADD` is not a hypothetical — it is what a kubelet restart during sandbox creation looks like from the plugin's side:

```sh
ip netns add leak1
cnitool add harness /var/run/netns/leak1 & sleep 0.05; kill -9 %1
ls -1 /var/lib/cni/academy/harness/          # one file, held by a container that will never come back
cnitool del harness /var/run/netns/leak1     # exits 0 and frees nothing — the id it was given never got recorded
ls -1 /var/lib/cni/academy/harness/
cnitool gc harness                            # the spec's answer, with an empty valid-id set
ls -1 /var/lib/cni/academy/harness/
```

**Expect** — part 1: `0`. Part 2: six successes, then a seventh that prints your error text and exits non-zero, with exactly six files on disk — **an exhausted allocator must not leave a seventh half-written**. Part 3: one leaked file that survives `DEL` and is removed by `GC`.

**Expect part 3 to be the finding, and expect the ordering inside `ADD` to be what decides how bad it is.** Reserve-then-wire leaks an address when the wiring fails. Wire-then-reserve leaks a *veth pair* — which is worse, because a leaked address is one entry in a file and a leaked veth pair is a name collision that makes the next `ADD` for that container fail too. Write down which order you chose and what it costs; there is no order that leaks nothing, which is why `GC` is in the spec.

**Verify from outside** — while part 1 runs, from a second session on `forge`:

```sh
watch -n1 'ls -1 /var/lib/cni/academy/harness/ | wc -l; ip -br link show | grep -c veth'
```

Both numbers should oscillate between 0 and 1 and return to 0. A number that only climbs is the leak, found before forty cycles have finished rather than after.

**Write down** — the three results, the reserve/wire ordering with its cost, and the `file:line` of your `DEL` where it frees by container id. That last one is the line a reviewer should be pointed at first.

**Footprint note** — nothing measurable. The `/29` is a config edit, not an allocation.

**Teardown** — restore the `/24`, and clear the store so [exercise 10](10-the-plugin-the-kubelet-calls.md) starts from a known state:

```sh
sudo sed -i 's#10.98.1.0/29#10.98.0.0/24#; s#10.98.1.1#10.98.0.1#' /etc/cni/lab-net.d/10-harness.conflist
for i in $(seq 1 7); do ip netns del x$i 2>/dev/null; done; ip netns del leak1 2>/dev/null
rm -rf /var/lib/cni/academy/harness; ip link del br-academy 2>/dev/null
ip netns list; ip -br link show | grep -c veth
```

**The topology stays** — and is about to be used for the first time since [exercise 6](06-the-api-that-is-being-deleted.md).
