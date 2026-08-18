<a id="exhaust-the-pid-limit"></a>
# Chaos drill 0.C3 — fork-bomb a wall you built

**Claim** — `pids.max` makes a fork bomb a local event: `fork()` returns `EAGAIN` inside the cgroup while the rest of the guest keeps forking normally. The blast radius stops at the cgroup boundary, and you can point at where.

**Topology** — [`bare`](../../strands/lab-topologies.md#bare), still up, still as root. **This exercise is why P0 gets its own guest.** Run it on anything shared and you will take that machine out; run it here and the worst case is one `tofu apply`.

**Footprint note** — set `pids.max` *before* you fork, in the same shell session, and verify it with a read-back. A fork bomb outside the cgroup will exhaust the guest's global `kernel.pid_max` and you will not get a shell back. Have a second SSH session already open before step 3.

**Do**

1. `mkdir /sys/fs/cgroup/forkers`, with `+pids` delegated.
2. `echo 32 > /sys/fs/cgroup/forkers/pids.max`. Read it back. Do not proceed until it reads `32`.
3. In your *second* session, `echo $$ > /sys/fs/cgroup/forkers/cgroup.procs`, confirm with `cat /proc/self/cgroup`, then run a bounded forker first: `for i in $(seq 1 64); do sleep 300 & done`.
4. Read the errors. Read `pids.current` and `pids.events`.
5. Now the unbounded version, still inside the cgroup: `:(){ :|:& };:`. Watch it fail to take the machine down.
6. From the *first* session — which is outside the cgroup — confirm you can still fork: `ls`, `ps aux | wc -l`.
7. Kill the cgroup's processes wholesale: `cat /sys/fs/cgroup/forkers/cgroup.procs | xargs -r kill -9`, or write `1` to `cgroup.kill` if the kernel provides it.

**Observe**

```sh
cat /sys/fs/cgroup/forkers/pids.current /sys/fs/cgroup/forkers/pids.max
cat /sys/fs/cgroup/forkers/pids.events    # the `max` counter
cat /sys/fs/cgroup/forkers/cgroup.procs | wc -l
```

**Expect** — the shell prints `fork: retry: Resource temporarily unavailable` (`EAGAIN`), `pids.current` sits pinned at 32, and `pids.events`' `max` counter climbs once per refused fork. The first session is unaffected throughout. `cgroup.kill` — write `1`, every process in the subtree dies — is the tidiest way out, and is exactly the primitive a runtime uses to stop a container that will not stop itself.

**Write down** — the errno, the counter, and one sentence on why `pids.max` is a *containment* limit rather than a performance one: it does not make anything faster, it makes one workload unable to deny service to the rest of the box.

**Teardown** — confirm `pids.current` is `0`, then `rmdir /sys/fs/cgroup/forkers`. Check `pgrep -c sleep` is zero before moving on; strays here will confuse [the network module](09-link-address-route.md). Guest stays up.
