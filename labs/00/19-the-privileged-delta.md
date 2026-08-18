<a id="the-privileged-delta"></a>
# Find one operation that only the privileged version can do

**Claim** — you can name a specific operation that succeeds with all capabilities and fails with `ALL` dropped, and that single delta is a concrete definition of what `securityContext.privileged: true` hands an attacker.

**Topology** — [`bare`](../../strands/lab-topologies.md#bare), still up, still as root.

**Setup** — the `pivot_root`'d rootfs from [the mount-namespace exercise](14-pivot-root-vs-chroot.md). You are going to enter it twice with different capability sets and find the difference.

**Do**

1. Enter your hand-made root with capabilities intact and confirm one of these works: `mount -t proc proc /proc`, `ip link add dummy0 type dummy`, `mknod /dev/loop-test b 7 200`, or writing to `/proc/sys/kernel/hostname`.
2. Enter it again under `capsh --drop=all --`, and run the same four. Record which fail and with what error.
3. For each failure, name the capability that gated it: `CAP_SYS_ADMIN`, `CAP_NET_ADMIN`, `CAP_MKNOD`, `CAP_SYS_ADMIN` respectively. Verify one of them by dropping *only* that capability rather than all of them, and confirming the same operation fails.
4. Now the part that matters: list what `privileged: true` grants beyond capabilities. Check each on the guest — is `/sys` writable, is the host's `/dev` present, is AppArmor/seccomp still applied, does the container keep its own namespaces or inherit the host's?
5. Find one operation from the privileged set that leads *out* of the container rather than merely doing more inside it — mounting the host's root filesystem from `/dev/sda1` is the canonical one. Do not run it against the guest's real root device unless you want to reprovision; identify the command and the capability it needs, and stop there.

**Observe**

```sh
capsh --print                                  # current, bounding, ambient
capsh --drop=all -- -c 'ip link add dummy0 type dummy'; echo "exit=$?"
capsh --drop=cap_mknod -- -c 'mknod /tmp/x b 7 200'; echo "exit=$?"
ls -l /dev | wc -l                             # host /dev vs a container's handful
```

**Expect** — with `ALL` dropped, every one of the four fails with `Operation not permitted` despite UID 0, because **root is not a capability set**; UID 0 is merely the default holder of one. The privileged delta is not a single flag but a bundle: all capabilities, plus the host's `/dev`, plus relaxed AppArmor/seccomp, plus write access to `/sys`. Any one of those alone is an escape route; together they are equivalent to being root on the node.

**Write down** — the one-line definition [the checklist](../../phases/00-linux-primitives.md#checklist) asks for: what `privileged: true` grants, in terms of capabilities, device access, and which namespaces are *not* created. Keep the operation you found in step 5; you will re-derive it as an attacker in [P10](../../phases/10-security.md), and it is much more convincing having first watched it fail.

**Teardown** — `ip link del dummy0` if step 1 created it, `rm -f /dev/loop-test /tmp/x`, and exit any namespace you entered. Confirm `ip -br link` on the host shows no `dummy0`. Guest stays up for [the capstone](20-container-from-scratch.md).
