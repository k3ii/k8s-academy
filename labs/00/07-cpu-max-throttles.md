<a id="cpu-max-throttles"></a>
# CPU limits throttle; they never kill

**Claim** — `cpu.max` withholds runtime rather than terminating anything, and `cpu.stat`'s `throttled_usec` is the only place the loss is visible. A process at its CPU limit is slow and healthy; a process at its memory limit is dead.

**Topology** — [`bare`](../../strands/lab-topologies.md#bare), still up, still as root. Two vCPU, so "half a core" is a quarter of the box.

**Do**

1. `mkdir /sys/fs/cgroup/slow`, with `+cpu` delegated from the parent.
2. `echo "50000 100000" > /sys/fs/cgroup/slow/cpu.max` — 50ms of runtime per 100ms period, i.e. half a core.
3. Put a busy loop in it and time a fixed amount of work: run `time sh -c 'while :; do :; done'` for a measured interval, or better, `time openssl speed -seconds 5 sha256` inside and outside the cgroup and compare.
4. Read `cpu.stat` before and after.
5. Set `cpu.max` to `max 100000` (unlimited) and repeat step 3. Compare the wall-clock.
6. Leave it running at the limit for a minute. Confirm nothing is killed and `memory.events` is untouched.

**Observe**

```sh
cat /sys/fs/cgroup/slow/cpu.stat          # usage_usec nr_periods nr_throttled throttled_usec
cat /sys/fs/cgroup/slow/cpu.max
uptime                                     # load average rises; nothing dies
```

**Expect** — `nr_throttled` and `throttled_usec` climb steadily while the work takes roughly twice the wall-clock it took unthrottled. No signal is delivered, nothing appears in `dmesg`, and the process's own view of the world is identical — it simply is not scheduled for part of each period. That invisibility is the problem: a CPU-limited workload reports as healthy on every axis a liveness probe can reach.

**Write down** — the two failure shapes side by side: **memory limit → `SIGKILL`, immediate, from the kernel, with a `dmesg` line**; **CPU limit → throttling, gradual, silent, visible only in `cpu.stat`**. You will re-derive this in [P6](../../phases/06-kubelet-node.md) as the reason CPU limits are contentious and memory limits are not.

**Teardown** — kill the busy loop, `rmdir /sys/fs/cgroup/slow`. Guest stays up.
