<a id="drop-a-capability"></a>
# Drop one capability, lose one syscall

**Claim** — dropping `CAP_NET_RAW` from a process makes `ping` fail while TCP keeps working, and you can read the change directly out of `/proc/<pid>/status` as a bitmask before and after.

**Rests on** — [Module 0.5's reading question](../../phases/00-linux-primitives.md#m0-5) on the permitted, effective and bounding sets. Step 4 asks which set a container's `drop: ALL` / `add: NET_BIND_SERVICE` manipulates, and the answer is not guessable from the command.

**Topology** — [`bare`](../../strands/lab-topologies.md#bare), still up, still as root.

**Do**

1. As root, `ping -c1 10.10.10.1`. It works. `grep Cap /proc/self/status` and decode each of the five lines with `capsh --decode=<hex>`.
2. `capsh --drop=cap_net_raw -- -c 'ping -c1 10.10.10.1'`. Read the failure.
3. In the same dropped shell, prove TCP is unaffected: `capsh --drop=cap_net_raw -- -c 'curl -sI http://10.10.10.1 || nc -zv 10.10.10.1 22'`.
4. Compare `grep Cap /proc/self/status` inside and outside the dropped shell. Identify which of `CapInh`, `CapPrm`, `CapEff`, `CapBnd` and `CapAmb` changed, and say which one `--drop` actually manipulates.
5. Try to get it back inside the dropped shell. You cannot — establish from the reading why a capability removed from the bounding set is gone for the lifetime of the process tree.
6. Check whether `ping` on this guest is a `setuid` binary or carries a file capability: `getcap $(which ping); ls -l $(which ping)`. That determines whether step 2's failure is about *your* capabilities or the binary's.

**Observe**

```sh
grep ^Cap /proc/self/status
capsh --decode=00000000a80425fb
getcap /usr/bin/ping
capsh --drop=cap_net_raw -- -c 'ping -c1 -W1 10.10.10.1'; echo "exit=$?"
```

**Expect** — `ping` fails with `socket: Operation not permitted` on the raw socket, and TCP connections are entirely unaffected, because only `SOCK_RAW` and packet sockets are gated by `CAP_NET_RAW`. `CapBnd` loses the bit and `CapEff`/`CapPrm` follow; nothing can add it back. If `ping` on this guest carries `cap_net_raw+ep` as a *file* capability, the drop still wins, because a file capability cannot exceed the bounding set — which is the mechanism that makes `--cap-drop` on a container meaningful even for setuid binaries inside the image.

**Write down** — the capability, the syscall it gated, the exact error, and the four-word summary of the sets: *bounding caps the ceiling*. [The checklist](../../phases/00-linux-primitives.md#checklist) wants this as a falsifiable claim, so write it before you verify it.

**Teardown** — nothing persists; `capsh` changes only the process it starts. Guest stays up.
