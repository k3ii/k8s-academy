<a id="a-mismatched-btf-and-the-two-ways-it-fails"></a>
# The borrowed drill: three ways a type-layout mismatch ends, two of which are fine and one of which lies to you

**Artifact** — [the drill this phase inherited](../../strands/chaos.md#borrowed-drills) — *build against the wrong kernel's types* — run as **three separate breakages of [exercise 28's](28-a-counter-loaded-attached-read-detached.md) `connect.c`**, each classified as *loud at load time*, *loud at attach time* or *silent at read time*, with the evidence for each and the lockstep restored at the end.

**Rests on** — [exercise 28](28-a-counter-loaded-attached-read-detached.md), specifically requirement 3: `connect.c` exists because a tc program reading `struct __sk_buff` has no relocations to break. This drill is what that requirement was for.

**Topology** — none. `forge` only; [`pair`](../../strands/lab-topologies.md#pair) stays up and idle for [exercise 30](30-a-drop-decided-by-a-map-entry.md).

> **What this drill substitutes, stated up front.** [The strand's version](../../strands/chaos.md#borrowed-drills) boots the build guest on a different kernel than the nodes. That is the honest article and it costs a `linux-image` install and a reboot; part 4 says how to run it. Parts 1 to 3 produce **the same three failure modes on one kernel**, by breaking the type layout at the place a different kernel would have broken it — the compiled `vmlinux.h`. The substitution is legitimate for the failures it reproduces and is not legitimate for one thing, named in part 4.

**Setup**

```sh
cd ~/src/k8s-academy/build/07-ebpf-academy
cp bpf/vmlinux.h /tmp/vmlinux.h.good
go generate ./... && go build ./... && sudo ./counter -prog connect &
curl -sS -m2 -o /dev/null http://10.10.10.130:6443 ; echo
sudo bpftool map dump name connect_map        # a plausible destination port, in network byte order
sudo kill %1
```

Record the correct port now. Every part below is scored against it, and a drill whose baseline was taken after the break is not a drill.

**Do — part 1: move the field, and watch the relocation do its job**

Insert a padding member into `struct sock_common` in `bpf/vmlinux.h`, *before* `skc_dport`:

```sh
python3 - <<'PY'
p='bpf/vmlinux.h'; s=open(p).read()
s=s.replace("\t__be16 skc_dport;", "\t__u64 academy_injected_pad;\n\t__be16 skc_dport;",1)
open(p,'w').write(s)
PY
go generate ./... && llvm-objdump -r connect_bpf.o | head -20
sudo ./counter -prog connect & sleep 1
curl -sS -m2 -o /dev/null http://10.10.10.130:6443
sudo bpftool map dump name connect_map ; sudo kill %1
```

**Expect the correct port anyway.** The program was compiled believing the field sits eight bytes later than it does, and it read the right value regardless — because the relocation records the field **by name**, and the loader resolves it against `/sys/kernel/btf/vmlinux` at load time. Find that in the `llvm-objdump -r` output before moving on: the relocation entries are the mechanism, and this part exists so that the next two are not read as "BTF mismatch breaks eBPF", which is the wrong lesson.

**Do — part 2: take the field away** — the case where the kernel genuinely changed:

```sh
sed -i 's/\t__be16 skc_dport;/\t__be16 skc_dport_v2;/' bpf/vmlinux.h
go generate ./... 2>&1 | tail -3
sudo ./counter -prog connect 2>&1 | head -20
```

**Do — part 3: opt out of CO-RE and hard-code the offset** — the case the strand calls *much worse*. Find the true offset first, then use a wrong one on purpose:

```sh
cp /tmp/vmlinux.h.good bpf/vmlinux.h
sudo pahole -C sock_common /sys/kernel/btf/vmlinux | grep -n 'skc_dport'   # the true offset
# in bpf/connect.c, replace the BPF_CORE_READ with:
#   bpf_probe_read_kernel(&dport, sizeof(dport), (void *)sk + <true offset + 4>);
go generate ./... && go build ./... && sudo ./counter -prog connect & sleep 1
curl -sS -m2 -o /dev/null http://10.10.10.130:6443
sudo bpftool map dump name connect_map ; sudo kill %1
```

**Gate** — fill this in from what actually happened, then state the rule it implies in one sentence:

| Break | Where it surfaced | Loud or silent | What told you |
|---|---|---|---|
| 1 — field moved | | | |
| 2 — field renamed | | | |
| 3 — offset hard-coded, CO-RE bypassed | | | |

**Expect** — part 2 to fail **before a single packet arrives**, with an error naming the field and the type, at load time, from the loader rather than from the verifier. Expect part 3 to load cleanly, verify cleanly, attach cleanly, run, and report a port number that is wrong — plausibly wrong, not obviously wrong, a small integer in a field that should hold a small integer. Nothing anywhere reports an error. **The verifier cannot help here, because nothing unsafe happened**: reading four bytes into the middle of a struct you are allowed to read is legal, and it is only *incorrect*, which is not the verifier's job.

That is the whole reason [the gate is a stop-and-fix rather than a warning](../../strands/build-mechanics.md#kernel-lockstep): two of the three failure modes announce themselves and the third produces a metric, a policy decision or a drop verdict that is quietly wrong for as long as nobody checks it against a second source.

**Do — part 4: restore the lockstep, and prove it from the node's side**

```sh
cd ~/src/k8s-academy/build/07-ebpf-academy && git checkout bpf/connect.c
ssh zain@10.10.10.131 'sudo bpftool btf dump file /sys/kernel/btf/vmlinux format c' > /tmp/vmlinux.node.h
diff <(sed 's/[[:space:]]*$//' /tmp/vmlinux.node.h) <(sed 's/[[:space:]]*$//' /tmp/vmlinux.h.good) && echo 'layouts identical'
cp /tmp/vmlinux.node.h bpf/vmlinux.h
go generate ./... && go build ./... && sudo ./counter -prog connect & sleep 1
curl -sS -m2 -o /dev/null http://10.10.10.130:6443 ; sudo bpftool map dump name connect_map ; sudo kill %1
ssh zain@10.10.10.131 'sudo bpftool btf dump file /sys/kernel/btf/vmlinux format raw | grep -c tcp_v4_connect'
```

Generating the header **from the node you will load on** is the practice this whole drill argues for, and it costs one `ssh`. From here on, `bpf/vmlinux.h` in this repository is a build input with a provenance, and its provenance is a machine name.

**What parts 1 to 3 do not cover** — the last command is why. An `fentry` program attaches to a named kernel function, and a real kernel change can remove that name, rename it, or inline it away — a failure at **attach** time that no amount of correct type layout prevents, and one this substitution cannot produce because there is only one kernel here. That is the row a genuine second kernel adds to the table above. To run the full version: `sudo apt-get install linux-image-<other>`, reboot `forge`, and re-run parts 1, 2 and the `fentry` attach — one reboot, and the only part of the drill that needs the strand's original form.

**Write down** — the three-row table; the true `skc_dport` offset from `pahole` and the wrong one you used; the exact error text from part 2; and one sentence on why CO-RE makes part 1 a non-event, to be re-read the next time somebody proposes pinning a kernel to protect an eBPF build.

**Footprint note** — nothing. Compiles and a `diff`; `pair` is idle throughout, and no guest changes size.

**Teardown**

```sh
git -C ~/src/k8s-academy status --short build/07-ebpf-academy
git -C ~/src/k8s-academy diff --stat build/07-ebpf-academy/bpf
sudo bpftool prog show | grep -ci tracing        # expect 0
```

The working tree must show only the `vmlinux.h` provenance change from part 4 — if either `.c` file still carries a break, [exercise 30](30-a-drop-decided-by-a-map-entry.md) inherits it and its drop verdicts will be wrong in the silent way you just spent an hour learning to fear. **No topology to release**; `pair` has been idle and [exercise 30](30-a-drop-decided-by-a-map-entry.md) needs it.
