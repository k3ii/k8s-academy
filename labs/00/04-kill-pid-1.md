<a id="kill-pid-1"></a>
# Kill PID 1 and take the namespace with it

**Claim** — PID 1 in a namespace is not an ordinary process. Killing it kills every other process in that namespace, and the kernel enforces this rather than an init system choosing to do it.

**Topology** — [`bare`](../../strands/lab-topologies.md#bare), still up from [the UTS namespace](01-uts-namespace.md), still as root.

**Do**

1. `unshare --pid --fork --mount-proc bash`.
2. Inside, start two background processes: `sleep 3600 & sleep 3600 &`. Confirm with `ps aux` that you have PID 1 and two children.
3. Before killing anything, try `kill -9 1` **from inside**, as PID 1, against yourself. Note what happens — and what does *not*.
4. Now try it from the host: find the shell's host PID and `kill -9` it. Watch the two `sleep`s from the host with `ps aux | grep sleep` before and after.
5. Repeat step 1–2, then from *inside* send `kill -9` to one of the `sleep`s by its namespace-local PID. That one works normally.

**Observe**

```sh
# from the host, before and after killing the namespace's PID 1
ps -eo pid,ppid,comm | grep -c sleep
lsns -t pid
```

**Expect** — step 3 does nothing: the kernel drops signals sent to PID 1 by its own children unless PID 1 installed a handler for them, which is why a naive `kill -TERM 1` inside a container is silently ignored and why `docker stop` waits then escalates. Step 4 works, and both `sleep`s die with it — `SIGKILL` to the namespace's init reaps the whole namespace. Step 5 shows ordinary signalling is unaffected; only PID 1 is special.

**Write down** — the two consequences you will meet again: a container image whose entrypoint is a shell that does not forward signals will not stop cleanly, and a container's processes cannot outlive its PID 1. [The capstone](../../phases/00-linux-primitives.md#capstone) inherits both, because your hand-made container's workload *is* PID 1.

**Teardown** — confirm no stray `sleep` survives: `pgrep -a sleep`. Guest stays up for [the cgroups module](05-move-a-process-into-a-cgroup.md).
