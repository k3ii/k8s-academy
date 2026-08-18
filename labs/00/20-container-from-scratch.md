<a id="container-from-scratch"></a>
# A container with no container runtime

**Artifact** — one shell script that starts an isolated process, and a static Go binary for it to run. **This is [the phase's capstone](../../phases/00-linux-primitives.md#capstone) and the first of its two gate conditions.** No Docker, no `runc`, no `podman`, no `nerdctl` — only the primitives from the nineteen exercises above.

**Topology** — [`bare`](../../strands/lab-topologies.md#bare), still up, still as root. [`forge`](../../strands/lab-topologies.md#build-guest) is needed once, for step 1, and is already running.

**Build**

**This is not one of [the eleven build-track artifacts](../../strands/build-mechanics.md#artifact-table)**, and nothing in `build-mechanics` applies to it — no module path, no version stamp, no ship step. It sits in `build/` because it is code, and it is a shell script plus five lines of Go.

The workload is trivial on purpose — the lesson is the isolation, not the program:

```
build/00-scratch/
  hello.go       package main; print the hostname, the PID, and sleep
  contain.sh     the script below, and it is the actual artifact
  rootfs/        busybox-static + the compiled hello, and nothing else
```

Build `hello` on `forge` and copy it in: `CGO_ENABLED=0 go build -o rootfs/hello ./hello.go`. **It must be static**, and the reason is not portability — it is that `rootfs/` contains no `ld.so` and no libc, so a dynamically linked binary cannot start after [`pivot_root`](14-pivot-root-vs-chroot.md). Confirm with `file rootfs/hello` and `ldd rootfs/hello`.

`contain.sh` must do these six things, in an order you can defend, and print what it did at each step:

1. **Create the namespaces together** — mount, PID, network, UTS, IPC via `unshare`'s flags, plus user for the harder version. You must be able to say what each one is doing, per [the seven-namespaces table](01-uts-namespace.md) you have been filling in.
2. **Create the cgroup** and set `memory.max`, before the workload starts, and write the child's PID into `cgroup.procs`. [Exercise 6](06-oom-inside-a-wall.md) is the mechanism.
3. **Wire the network** — a veth pair, one end into the container's netns, the other into a bridge, an address, a default route and `MASQUERADE`. [Exercises 9 through 11](09-link-address-route.md) are the recipe.
4. **Assemble the root** — an overlay over `rootfs/` as `lower`, then `mount --make-rprivate /`, a bind mount of the merged dir onto itself, `pivot_root`, and `umount -l` the old root. [Exercises 13 and 14](13-overlayfs-by-hand.md).
5. **Drop capabilities** to a hand-picked set — not `ALL` dropped and not left alone; pick a set and justify each one you kept. [Exercise 17](17-drop-a-capability.md).
6. **Exec the workload** as PID 1, and handle its exit, remembering that [PID 1 does not receive signals it has no handler for](04-kill-pid-1.md).

**Verify from outside — this is the assessed part**

```sh
nsenter -t <pid> -a hostname                       # UTS: the container's, not the host's
nsenter -t <pid> -p -m ps aux                      # PID+mount: two processes, not the host's
nsenter -t <pid> -n ip -br addr                    # net: one veth, one address
ping -c2 <container-ip>                            # from the host, across the bridge
cat /proc/<pid>/cgroup                             # 0::/<your cgroup>
cat /sys/fs/cgroup/<name>/memory.max
readlink /proc/<pid>/root                          # the overlay, not /
grep ^Cap /proc/<pid>/status                       # your hand-picked set, decoded
```

Then **OOM it from the host** by lowering `memory.max` under the running workload, and confirm `memory.events`' `oom_kill` increments — the same counter as [drill 0.C1](06-oom-inside-a-wall.md), now against something you built.

**Expect** — every axis above verifies independently, and the failures are informative when they do not. The two that most often go wrong first: the workload exits immediately because the static binary is not actually static, and the network is up but unreachable because `MASQUERADE` or `ip_forward` was left behind by [exercise 11's teardown](11-masquerade-out.md).

**Write down** — commit `contain.sh` with the step-by-step output it prints. That transcript is the artifact; [the gate](../../phases/00-linux-primitives.md#gate) asks that the container runs and survives outside verification, and the transcript is how you show it did.

**Teardown** — the script must clean up after itself, and writing that cleanup is part of the exercise: kill the workload, `ip netns del`, `ip link del` the bridge, delete the `MASQUERADE` rule, `umount` the overlay, `rmdir` the cgroup. Verify with `ip -br link`, `iptables -t nat -L -n`, `findmnt | grep overlay` and `ls /sys/fs/cgroup`. **Leave the guest up** — [the flag mapping](21-docker-flags-to-primitives.md) needs a running container to point at, so run `contain.sh` again when you get there.
