<a id="a-counter-loaded-attached-read-detached"></a>
# Build artifact 2: compile, load, attach, read the map, detach — and prove each of the five happened

**Artifact** — `build/07-ebpf-academy/`: an eBPF program you compiled, loaded, attached to a tc hook, read a map from, and detached, driven from a Go binary using `cilium/ebpf`. The five verbs are the artifact; the program itself counts packets and is deliberately dull.

**Rests on** — [exercise 2](02-the-kernel-both-sides-must-share.md), whose result this exercise spends. Nothing below is safe if [`forge`](../../strands/lab-topologies.md#build-guest) and the nodes are not on the same kernel.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair) stays up and idle; everything here happens on `forge`, in a network namespace with no Kubernetes in it.

**What replaces stage 1** — the same answer as [exercise 7](07-what-replaces-stage-1.md), one layer down. [The strand lists both P7 artifacts as "none — on-node only"](../../strands/build-mechanics.md#artifact-table), so there is no out-of-cluster fast loop; what there is instead is a **veth pair in a netns on a kernel-matched host**, where `go generate && sudo go run ./cmd/counter` is a two-second cycle and a failed verifier costs you nothing but a log to read. That loop is legitimate for exactly one reason — `forge` runs the nodes' kernel — which is why the lockstep check is a precondition and not a footnote.

Three things this harness cannot reach, named now so that they are not discovered as surprises later: **another program already occupying the same hook** (the CNI's, and then Cilium's), **real pod traffic through a real pod's veth**, and **the lifetime question** — what happens to your program when the process that loaded it goes away. The third one is testable here and is part 5 below; the first two are [exercise 30's](30-a-drop-decided-by-a-map-entry.md) and [exercise 31's](31-kube-proxy-replaced-by-map-lookups.md).

**Setup — the lockstep, in one line, because it was an exercise once**

```sh
ssh zain@10.10.10.125 uname -r; ssh zain@10.10.10.131 uname -r
ssh zain@10.10.10.125 'sudo sha256sum /sys/kernel/btf/vmlinux'; ssh zain@10.10.10.131 'sudo sha256sum /sys/kernel/btf/vmlinux'
```

Equal, or stop and re-read [exercise 2](02-the-kernel-both-sides-must-share.md). Then the toolchain and the header that makes CO-RE possible:

```sh
sudo apt-get install -y clang llvm libbpf-dev linux-headers-$(uname -r) bpftool
go install github.com/cilium/ebpf/cmd/bpf2go@latest
mkdir -p ~/src/k8s-academy/build/07-ebpf-academy/bpf && cd $_
sudo bpftool btf dump file /sys/kernel/btf/vmlinux format c > vmlinux.h
wc -l vmlinux.h && grep -c 'struct sock {' vmlinux.h
```

That header is your kernel's type layout written out as C. **It is a build input, and it came from the machine you are building for** — which is the whole content of the lockstep rule and is worth seeing as a file rather than as a rule.

**Build**

```
build/07-ebpf-academy/
  bpf/vmlinux.h            generated above; never hand-edited, never committed as authoritative
  bpf/counter.c            SEC("tc")   packet/byte counter, per-CPU map
  bpf/connect.c            SEC("fentry/tcp_v4_connect")   one CO-RE field read
  gen.go                   //go:generate bpf2go -cc clang -target bpfel counter bpf/counter.c
  cmd/counter/main.go      load → attach → poll → detach, and the two attach modes
  internal/harness/netns.sh   the veth pair and namespace this runs against
```

Six requirements, as an interface:

1. **The tc program returns `TC_ACT_OK` and never drops.** A counter that changes the datapath is not a counter, and [exercise 30](30-a-drop-decided-by-a-map-entry.md) is where dropping becomes the point.

2. **The map is `BPF_MAP_TYPE_PERCPU_ARRAY`**, one key, a `{packets, bytes}` value — and userspace must **sum across CPUs**. A plain `ARRAY` with `value++` in a program that runs concurrently on every CPU loses updates, silently, under exactly the load you would care about. Write the per-CPU version, and say in your notes what the shared version would have cost.

3. **`connect.c` exists because `counter.c` cannot exercise CO-RE.** `struct __sk_buff` is stable UAPI: a tc program reading `skb->len` needs no BTF and would load happily against the wrong kernel. So the artifact carries one program that reads a real kernel struct — `BPF_CORE_READ(sk, __sk_common.skc_dport)` from `struct sock` in an `fentry` hook — because **an artifact whose gate is kernel lockstep must contain at least one relocation that the lockstep protects.** This is the program [exercise 29](29-a-mismatched-btf-and-the-two-ways-it-fails.md) breaks.

4. **Attach to a veth inside a netns, by way of a `clsact` qdisc**, from Go via `cilium/ebpf/link` — not by shelling out to `tc`. Shelling out works and teaches you nothing about the lifetime in requirement 6.

5. **Read the map while the program is attached**, on a timer, and print a running total.

6. **Implement detach twice**: once as a classic netlink `clsact` filter, and once with `link.AttachTCX`. Then compare what survives your process.

**Do — parts 1 to 3: the harness, the load, the count**

```sh
sudo ip netns add ebpflab
sudo ip link add veth0 type veth peer name veth1
sudo ip link set veth1 netns ebpflab
sudo ip addr add 10.99.0.1/24 dev veth0 && sudo ip link set veth0 up
sudo ip netns exec ebpflab ip addr add 10.99.0.2/24 dev veth1
sudo ip netns exec ebpflab ip link set veth1 up
cd ~/src/k8s-academy/build/07-ebpf-academy && go generate ./... && go build ./...
sudo ./counter -iface veth0 &
ping -c 20 -i 0.2 10.99.0.2
```

**Verify from outside** — from a second session, without touching your own program's output:

```sh
sudo sysctl -w kernel.bpf_stats_enabled=1
sudo bpftool prog show | grep -A3 -i 'sched_cls\|tracing'
sudo bpftool map dump name counter_map
sudo tc filter show dev veth0 ingress
sudo tc qdisc show dev veth0
```

**Gate** — [the verifier accepts it, or it does not](../../strands/build-mechanics.md#gates): objective, free, and not a harness you wrote. **Make it reject you twice on purpose**, because a gate nobody has watched fail is not evidence:

```sh
# (a) direct packet access with no bounds check: read *(u8 *)(long)skb->data without
#     comparing against skb->data_end, rebuild, load.
# (b) a loop whose bound the verifier cannot prove: for (i = 0; i < n; i++) with n from the packet.
```

Read the rejection logs rather than skimming them, and write down **the exact phrase** each one produced. Then answer, from `architecture.rst` and `progtypes.rst` ([item 29](../../strands/source-reading.md#area-5-networking)): why is each of those two a *safety* requirement rather than a style rule, and what does the verifier's answer cost you in expressiveness? Note where tail calls and `bpf_loop` re-buy some of it.

**Do — part 5, the lifetime**

```sh
sudo ./counter -iface veth0 -attach=netlink & sleep 2; sudo kill -9 %1
sudo tc filter show dev veth0 ingress ; sudo bpftool prog show | tail -5
sudo ./counter -iface veth0 -attach=tcx & sleep 2; sudo kill -9 %1
sudo tc filter show dev veth0 ingress ; sudo bpftool prog show | tail -5
```

**Expect** — the map total to be **twice** the ping count if you attached at both ingress and egress and equal to it if you attached at one, and `run_cnt` from `bpftool` to agree with your own map within a few packets — two independent counts of the same thing, which is the only reason to enable `bpf_stats` at all. Expect the byte figure to be larger than 20 × 64 and to be able to say why from the hook's position relative to the L2 header.

Expect part 5 to split cleanly: the **netlink filter survives `kill -9`** — the program stays loaded and attached, still counting, with nothing left running that can remove it — while the **TCX link goes away with the file descriptor**. That is [exercise 9's leak](09-an-ipam-that-does-not-leak.md) in a different subsystem, and it has the same shape: state whose owner is a process, versus state whose owner is a kernel object with a refcount. Write both down; "clean up on exit" is not a design, and `kill -9` is the test that says so.

**Write down** — the five verbs with the command or call that performed each and the outside-evidence for each; both verifier rejection phrases; the per-CPU sum and why it is a sum; and the two lifetimes from part 5. That sequence is [the checklist's](../../phases/07-networking.md#checklist) 7.5 item, and it must carry the `uname -r` check that gated it — a load→attach→read→detach log with no kernel version in it is not reproducible.

**Footprint note** — [`forge` at 1536MB](../../strands/build-mechanics.md#forge) is enough and **P7 asks for no resize**: `clang` on a small C file with `vmlinux.h` peaks well under [the 564 MiB the strand measured for a controller-runtime link](../../strands/build-mechanics.md#measurements), and the Go binary is smaller still. What this phase needs from `forge` is the kernel, not the RAM. `pair` is untouched at 5.0GB; keep it idle rather than destroying it — [exercise 30](30-a-drop-decided-by-a-map-entry.md) needs a real pod veth.

**Teardown** — remove the program *and* prove it is gone, since part 5 has just shown that leaving is the default:

```sh
sudo tc filter del dev veth0 ingress 2>/dev/null; sudo tc qdisc del dev veth0 clsact 2>/dev/null
sudo bpftool prog show | grep -ci 'sched_cls'
sudo ip link del veth0 ; sudo ip netns del ebpflab
sudo sysctl -w kernel.bpf_stats_enabled=0
```

Keep `build/07-ebpf-academy/` and both programs — [exercise 29](29-a-mismatched-btf-and-the-two-ways-it-fails.md) breaks them on purpose and [exercise 30](30-a-drop-decided-by-a-map-entry.md) extends `counter.c` into a drop. **The topology stays.**
