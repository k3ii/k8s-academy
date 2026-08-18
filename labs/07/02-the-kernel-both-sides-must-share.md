<a id="the-kernel-both-sides-must-share"></a>
# The precondition: `forge` and the nodes must be running the same kernel, checked now and not in week four

**Claim** — `uname -r` on [`forge`](../../strands/lab-topologies.md#build-guest) and on both nodes of [`pair`](../../strands/lab-topologies.md#pair) are the same string, **and** the BTF blob the compiler will resolve against is byte-identical to the one the loader will resolve against. Written as a claim rather than a check because the interesting outcome is the one where it is false, and [the strand](../../strands/build-mechanics.md#kernel-lockstep) says a mismatch is a stop-and-fix.

**Rests on** — nothing in this phase. It runs second **on purpose**: the eBPF artifact is four weeks away at [exercise 28](28-a-counter-loaded-attached-read-detached.md), and the repair for a mismatch is a reprovision. Finding that out now costs an hour; finding it out from a verifier rejection in module 7.5 costs the module, and finding it out from a *silently wrong field offset* costs more than that, because the program loads and reports numbers that are not the numbers you asked for.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), provisioned here and **held for the entire phase**. Every remaining exercise in P7 uses it.

**Setup** — bring the topology up [the standard way](../../strands/lab-topologies.md#provision):

```sh
ssh hopper
cd factory && git pull
just tofu labs apply -var 'topology=pair'
just gate 130 && just gate 131
just play
```

**Do**

```sh
for h in 10.10.10.125 10.10.10.130 10.10.10.131; do
  printf '%-15s ' $h
  ssh zain@$h 'uname -r'
done
```

Then the stronger form, which is the one that actually gates the artifact — the compiler and the loader must agree about the *contents* of the kernel's type information, not merely about a version string:

```sh
for h in 10.10.10.125 10.10.10.130 10.10.10.131; do
  printf '%-15s ' $h
  ssh zain@$h 'sudo sha256sum /sys/kernel/btf/vmlinux' 2>&1
done
```

And confirm the three things the toolchain needs are present on `forge` and are the versions you will be citing later:

```sh
ssh zain@10.10.10.125 'clang --version | head -1; ls /sys/kernel/btf/vmlinux; bpftool version | head -1'
```

**Expect** — three identical release strings and three identical digests. `bpftool btf dump file /sys/kernel/btf/vmlinux format c | wc -l` on `forge` and on `.131` is a third, slower confirmation of the same thing and is worth running once so that the object being compared is a concrete artifact rather than a hash.

**Expect a missing `/sys/kernel/btf/vmlinux` to be a harder stop than a version mismatch.** A mismatch has a fix that takes an hour; a kernel built without `CONFIG_DEBUG_INFO_BTF` has no fix short of a different kernel, and every CO-RE claim in [module 7.5](../../phases/07-networking.md#m7-5) rests on that file existing.

**If the strings differ** — the fix is one of two, and it is taken **now**:

1. `forge` was provisioned from a different template or has taken an unattended kernel upgrade the nodes have not. Bring them level (`apt list --installed 'linux-image-*'` on each, then align and reboot), and pin, so that an upgrade during the phase does not silently reintroduce this.
2. If they cannot be brought level, `forge` is not the build host for artifact 2 and [exercise 28](28-a-counter-loaded-attached-read-detached.md) compiles on the node itself. That is a real cost — it puts a toolchain on a lab node that [the whole build-guest design](../../strands/build-mechanics.md#forge) exists to keep off — so it is a fallback, recorded as one, not a preference.

**Write down** — the release string, the digest, and the `clang` version, in the phase's notes where [exercise 28](28-a-counter-loaded-attached-read-detached.md) will re-check them in one line. Also write down the date: the claim is only true until something upgrades, and [exercise 29](29-a-mismatched-btf-and-the-two-ways-it-fails.md) breaks it deliberately to show what that looks like from the other side.

**Footprint note** — `pair` is 5.0GB and `forge` is 1536MB, so the phase opens at **6.5GB against the [9.5GB ceiling](../../strands/lab-topologies.md#ceiling)** — 3.0GB of margin, before anything is installed into the cluster. [The index](README.md) tracks what that margin is spent on, and P7 is the phase where three DaemonSets want it at once.

**P7 needs no `forge` resize**, unlike [P5](../../strands/build-mechanics.md#p5-split). Both artifacts here are small Go programs and one small object file; what this phase needs from `forge` is not memory, it is the kernel checked above.

**Teardown** — nothing created. **The topology stays** — it is up for the rest of the phase, and [the capstone](34-the-capstone-a-network-you-wrote-and-a-drop-you-can-point-at.md) is what releases it.
