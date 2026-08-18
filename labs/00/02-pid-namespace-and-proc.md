<a id="pid-namespace-and-proc"></a>
# `ps` lies until you remount `/proc`

**Claim** — a new PID namespace renumbers processes, but `ps` still shows the host's until you give the namespace its own `/proc`. The PID namespace and the mount namespace are separate things, and this is the first place that separation bites.

**Topology** — [`bare`](../../strands/lab-topologies.md#bare), still up from [the UTS namespace](01-uts-namespace.md), still as root.

**Do**

1. `unshare --pid --fork bash` — **without** `--mount-proc`. Run `ps aux`. Read the PIDs.
2. Now `echo $$`. Compare that number with what `ps` reports for the same shell.
3. `exit`, and redo it as `unshare --pid --fork --mount-proc bash`. Run `ps aux` again.
4. Inside, `echo $$` and `ls /proc | head`.
5. From a second session on the host, find the same shell process and read *its* PID. One process, two numbers, both correct.

**Observe**

```sh
echo $$                                    # inside: 1
ps aux | wc -l                             # before --mount-proc: the host's count
                                           # after:  two or three lines
ls -l /proc/self/ns/pid /proc/self/ns/mnt  # both differ from the host's
```

**Expect** — without `--mount-proc`, `$$` says `1` while `ps` lists every process on the box. `ps` is not lying about the kernel; it is reading `/proc`, which is still the *host's* `/proc` mount, which reports host PIDs. `--mount-proc` unshares the mount namespace as well and mounts a fresh `procfs`, which the kernel renders from the *reader's* PID namespace. After that, `ps` shows two processes and `$$` is 1.

**Write down** — one sentence on why `/proc` is a mount and not a namespace, and what that implies for any tool that reports on processes. Add the PID row to your seven-namespaces table.

**Teardown** — `exit`. Nothing persists: the namespace dies with its last process, and the `procfs` mount died with the mount namespace. Guest stays up.
