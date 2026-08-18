<a id="move-a-process-into-a-cgroup"></a>
# Membership is a write to a file

**Claim** — a process's cgroup is set by writing its PID into `cgroup.procs`, one PID per write, and the tree will refuse the write if it would break the no-internal-processes rule.

**Rests on** — [Module 0.2's reading question](../../phases/00-linux-primitives.md#m0-2) on `cgroup.controllers` versus `cgroup.subtree_control`. Steps 4 and 5 will not make sense without the answer, and will look like a permissions bug.

**Topology** — [`bare`](../../strands/lab-topologies.md#bare), still up, still as root.

**Do**

1. Confirm you are on cgroup v2 only: `mount | grep cgroup` should show one `cgroup2` mount on `/sys/fs/cgroup` and no `cgroup` (v1) mounts. If there are v1 mounts, stop — the guest was not built to [the baseline](../../strands/lab-topologies.md#provision).
2. `mkdir /sys/fs/cgroup/demo`. List what the kernel created inside it without you asking.
3. Start `sleep 3600 &`, then `echo <pid> > /sys/fs/cgroup/demo/cgroup.procs`.
4. Confirm the move from the other side: `cat /proc/<pid>/cgroup`.
5. Now try to nest: `mkdir /sys/fs/cgroup/demo/inner`, and try to write a *second* PID into `demo/cgroup.procs` while `inner` also holds processes and a controller is enabled. Read the errno.
6. Read `/sys/fs/cgroup/cgroup.controllers`, then `/sys/fs/cgroup/demo/cgroup.controllers`. Note that `demo` has none until you `echo "+memory +cpu +pids" > /sys/fs/cgroup/cgroup.subtree_control`.

**Observe**

```sh
cat /proc/<pid>/cgroup                       # 0::/demo
cat /sys/fs/cgroup/demo/cgroup.procs
cat /sys/fs/cgroup/cgroup.subtree_control    # what the parent delegates down
cat /sys/fs/cgroup/demo/cgroup.controllers   # what this cgroup can therefore use
```

**Expect** — `/proc/<pid>/cgroup` reads `0::/demo`: one line, one hierarchy, which is the entire difference from v1's controller-per-hierarchy sprawl. A cgroup's `cgroup.controllers` is empty until the *parent* enables the controller in `subtree_control`, so `memory.max` does not exist as a file until you delegate `+memory` downward. And a cgroup with children may not itself hold processes once a controller is enabled — the write fails with `EBUSY`, not `EPERM`.

**Write down** — the delegation direction in one line (*a parent enables controllers for its children, never for itself*), and what `0::/demo` in `/proc/<pid>/cgroup` tells you that a v1 listing would have spread over eight lines. Every limit in the next three exercises is a file inside this directory.

**Teardown** — `kill %1`, then `rmdir /sys/fs/cgroup/demo/inner /sys/fs/cgroup/demo`. `rmdir` fails while any process remains in the cgroup, which is the check you want. Guest stays up.
