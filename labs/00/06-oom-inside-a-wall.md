<a id="oom-inside-a-wall"></a>
# Chaos drill 0.C1 — OOMKilled while the host barely notices

**Claim** — you can drive a process to an OOMKill by `memory.max` alone, point at the counter in `memory.events` that proves it, and say why the host's `free -m` hardly moved. **This is the sentence every eviction conversation from [P6](../../phases/06-kubelet-node.md) onward rests on.**

**Topology** — [`bare`](../../strands/lab-topologies.md#bare), still up, still as root. The guest has 2048MB; the limit you are about to set is 50MB, so the host has no reason to notice.

**Do**

1. `mkdir -p /sys/fs/cgroup/wall/leaf` — a parent *and* a leaf, not one directory. The [no-internal-processes rule from the previous exercise](05-move-a-process-into-a-cgroup.md) is about to bite for real: a cgroup that delegates a controller may not also hold processes, so the limit and the process need separate directories. Then delegate memory downward: `echo +memory > /sys/fs/cgroup/wall/cgroup.subtree_control` (the root must delegate `+memory` first — confirm with `cat /sys/fs/cgroup/cgroup.subtree_control`; systemd normally has it there already, and if not, add it as in [the previous exercise](05-move-a-process-into-a-cgroup.md)).
2. `echo 50M > /sys/fs/cgroup/wall/memory.max`. The limit goes on the **parent**; the process will sit in the leaf underneath it.
3. Record `free -m` on the host and `cat /sys/fs/cgroup/wall/memory.events` **before** anything runs. Write both down; you are going to compare against them.
4. Start a *dedicated* shell and move that, not your login shell: run `bash`, then inside it `echo $$ > /sys/fs/cgroup/wall/leaf/cgroup.procs`. Two reasons: writing your PID into `wall` itself now fails with `EBUSY` — you enabled a controller in its `subtree_control` in step 1, so it is no longer allowed to hold processes — and your login shell belongs to a systemd session scope (`cat /proc/$$/cgroup` shows `session-*.scope`) that systemd manages; a child shell in your own leaf is a cgroup systemd has no opinion about. Then allocate inside it: `python3 -c "x = bytearray(200*1024*1024)"` or `tail /dev/zero`.
5. Read `memory.events` again, and `dmesg | tail`. Name the counter that moved.
6. Read `memory.current` and `memory.peak` after the kill.
7. Now do it again with `memory.high` set to 50M instead of `memory.max` (`echo max > /sys/fs/cgroup/wall/memory.max`, then `echo 50M > /sys/fs/cgroup/wall/memory.high`). Watch what happens *differently*.

**Observe**

```sh
cat /sys/fs/cgroup/wall/memory.events     # low high max oom oom_kill — hierarchical, so the leaf's kill shows here
cat /sys/fs/cgroup/wall/memory.current /sys/fs/cgroup/wall/memory.peak
dmesg | grep -i 'killed process'
free -m                                    # compare with what you recorded in step 3
```

**Expect** — `oom_kill` increments by exactly one and `dmesg` names the process, its cgroup and the limit it hit — look for `oom_memcg=/wall,task_memcg=/wall/leaf`: the limit that killed and the cgroup that held the process are different directories, which is exactly the split step 1 built. `free -m` moves by a few tens of megabytes at most, because 50MB was never a shortage for a 2048MB guest — **the process died against a wall you built, not against a scarcity**. With `memory.high` instead, nothing is killed: the process is throttled and reclaimed against, `high` increments instead of `oom_kill`, and it crawls rather than dies. That pair is the mechanism under the request-versus-limit distinction, and `memory.high` is what makes "throttled but alive" a state that exists at all.

**Write down** — the exact `memory.events` line before and after, the `dmesg` line, and one paragraph on why the host was unaffected. This is a [checklist item](../../phases/00-linux-primitives.md#checklist) and it is named explicitly in [the gate](../../phases/00-linux-primitives.md#gate): if you cannot produce this from memory, the phase is not finished.

**Teardown** — `exit` the dedicated shell from step 4; your login shell was never moved, so nothing of yours remains in the tree. Then `rmdir /sys/fs/cgroup/wall/leaf /sys/fs/cgroup/wall` — leaf first, and `rmdir` fails while any process remains in a cgroup, which is the check you want. Guest stays up.
