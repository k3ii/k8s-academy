<a id="docker-flags-to-primitives"></a>
# Every container flag, mapped to the primitive it sets

**Artifact** — a table mapping the flags you would otherwise have typed to the exact file, syscall or command in [your own script](20-container-from-scratch.md) that does the same thing. **This is [the phase's second gate condition](../../phases/00-linux-primitives.md#gate)** and it is separate from the first: a container that runs proves the mechanism works, and this proves you can name it.

**Topology** — [`bare`](../../strands/lab-topologies.md#bare), still up, with `contain.sh` running so you can point at live state rather than at the script text.

**Do**

1. Start from these and add any you have met: `--memory`, `--memory-swap`, `--cpus`, `--pids-limit`, `--cap-drop` / `--cap-add`, `--privileged`, `--network`, `--hostname`, `--read-only`, `--tmpfs`, `--pid=host`, `--volume`, `--user`, `--security-opt seccomp=`, `--restart`.
2. For each, write **three** columns: the flag, the primitive it sets (a file path, a syscall, or an `ip`/`mount` command), and the line of `contain.sh` that does it — or **the honest admission that your script does not implement it**.
3. Three of them have no single primitive and are the interesting rows: `--restart` (nothing in the kernel does this), `--volume` (a bind mount, plus a propagation decision from [exercise 15](15-mount-propagation.md)), and `--privileged` (a bundle, per [the delta exercise](19-the-privileged-delta.md)). Say what supplies the missing part in each case.
4. Verify at least five rows against the running container rather than from memory — read the cgroup file, the `Cap` line, the mount, the namespace inode.
5. Then do the harder direction: pick three `kubectl`/Pod-spec fields — `resources.limits.memory`, `securityContext.capabilities.drop`, `hostPID: true` — and follow each down to the same primitive. Name the component that performs the write.

**Observe**

```sh
cat /sys/fs/cgroup/<name>/memory.max /sys/fs/cgroup/<name>/pids.max /sys/fs/cgroup/<name>/cpu.max
grep ^Cap /proc/<pid>/status
findmnt -N <pid> -o TARGET,SOURCE,PROPAGATION
readlink /proc/<pid>/ns/pid /proc/1/ns/pid       # equal under --pid=host, different otherwise
```

**Expect** — most rows resolve to one file under `/sys/fs/cgroup` or one `unshare` flag, and the exercise is quick. The rows that resist are the lesson: **`--restart` has no kernel primitive at all**, because supervision is not a container feature — which is exactly the gap a controller fills, and the first concrete answer to *what does Kubernetes actually add*. Keep that row.

**Write down** — the completed table, committed alongside `contain.sh`. [The gate](../../phases/00-linux-primitives.md#gate)'s standard is that for any container flag a reader names, you can point at the primitive it sets — so the test is a reader picking a row at random, not you reciting the ones you remember.

**Teardown** — stop `contain.sh` and run its cleanup. Guest stays up for [the last exercise](22-find-your-container-in-config-json.md), which needs no cluster and no container.
