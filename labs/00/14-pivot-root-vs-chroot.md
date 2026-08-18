<a id="pivot-root-vs-chroot"></a>
# The old root has to become unreachable, not just unused

**Claim** — `chroot` leaves the old root reachable and a process with `CAP_SYS_CHROOT` can walk back out of it; `pivot_root` in a private mount namespace, followed by unmounting the old root, leaves no path to it at all. You can demonstrate the escape and then demonstrate that it stops working.

**Rests on** — [Module 0.4's reading question](../../phases/00-linux-primitives.md#m0-4) on which of the two changes `/` for the whole mount namespace. Answer it from `man 2 pivot_root` before step 5, not after.

**Topology** — [`bare`](../../strands/lab-topologies.md#bare), still up, still as root.

**Setup** — a minimal root filesystem with a static binary in it. Fetch the `busybox-static` package and unpack a tree at `/root/rootfs` with `/bin/busybox` plus its symlinks, `/proc`, `/sys`, `/dev` and `/oldroot`. It needs nothing else, because a static binary needs no loader and no libc.

**Do**

1. `chroot /root/rootfs /bin/sh`. Confirm you cannot name `/etc/hostname` from the host. So far, so isolated.
2. **Escape it.** From inside the `chroot`, run the classic: open a directory fd, `chroot` into a subdirectory, then `chdir` up past the new root repeatedly and `chroot .`. Do it with `busybox` or a five-line C program. Confirm you can read a host file.
3. Explain, from the reading, why that works: `chroot` changes one process's idea of `/` and does not touch the mount tree, and the process's *current directory* can still sit outside the new root.
4. Now the correct version. `unshare --mount --fork bash`, and inside it `mount --make-rprivate /` so nothing you do propagates back.
5. `mount --bind /root/rootfs /root/rootfs` (`pivot_root` requires the new root to be a mount point), then `cd /root/rootfs && pivot_root . oldroot`.
6. `umount -l /oldroot`, then `rmdir /oldroot`.
7. Repeat the step-2 escape. It fails. Establish *why* by reading `/proc/self/mountinfo` from inside.

**Observe**

```sh
cat /proc/self/mountinfo        # inside: the old root's mounts are simply absent
ls /                            # only the rootfs
readlink /proc/self/root
ls /oldroot 2>&1                # after umount + rmdir: No such file or directory
```

**Expect** — the `chroot` escape works and produces host file contents; a correct `pivot_root` plus `umount` makes the same code fail with `ENOENT`, because the old root is not merely forbidden, it is **not mounted anywhere in this namespace** and therefore has no name. `/proc/self/mountinfo` inside the pivoted namespace lists only your rootfs and what you mounted under it. The `--make-rprivate` in step 4 is load-bearing: without it, the unmount can propagate to the host and take the host's mounts with it.

**Write down** — the one-sentence answer to [the checklist claim](../../phases/00-linux-primitives.md#checklist) on why a correct `pivot_root` resists an escape that `chroot` does not, phrased in terms of the mount namespace rather than permissions. You will need it verbatim as an [attacker in P10](../../phases/10-security.md).

**Teardown** — `exit` the mount namespace; every mount you made inside it dies with it, which is the reason for step 4. Verify from the host: `findmnt | grep rootfs` returns nothing. Leave `/root/rootfs` on disk — [the capstone](20-container-from-scratch.md) uses it. Guest stays up.
