<a id="uts-namespace"></a>
# One flag, one thing hidden

**Claim** — `unshare --uts` isolates the hostname and nothing else. Change it inside and the host's hostname does not move; everything else the process can see is unchanged, because you asked for exactly one namespace.

**Rests on** — [Module 0.1's reading question](../../phases/00-linux-primitives.md#m0-1) on the seven namespace types. Have the list in front of you before step 1; the point of this exercise is that you can predict which line of that list you just crossed.

**Topology** — [`bare`](../../strands/lab-topologies.md#bare), fresh. Bring it up with [the five provision steps](../../strands/lab-topologies.md#provision), substituting `topology=bare`, then `ssh zain@10.10.10.192`.

**Setup** — everything in this phase runs as root on the guest. `sudo -i` once, at the start of each session, and stay there. Nothing here is safe to leave running in a shell you forget about, which is what the teardown lines are for.

**Do**

1. Note the hostname: `hostname`.
2. `unshare --uts --fork bash`. You are now in a new UTS namespace.
3. Inside, `hostname container-0`, then `hostname` again.
4. From a *second* SSH session on the same guest, `hostname`. It has not changed.
5. Still inside, check the things you did **not** isolate: `ps aux | head`, `ip addr`, `ls /`, `df -h`. All of them are the host's. Say out loud which flag each one would have needed.
6. `exit`. The namespace has no processes left, so the kernel destroys it.

**Observe**

```sh
readlink /proc/self/ns/uts        # run in both shells; two different inode numbers
hostname                          # run in both shells; two different names
```

**Expect** — `/proc/self/ns/uts` reads as `uts:[4026532...]` and the two numbers differ, while `/proc/self/ns/pid`, `net` and `mnt` are *identical* between the two shells. That asymmetry is the whole lesson: a namespace flag is not a container, it is one axis of isolation, and there are seven of them.

**Write down** — start the seven-namespaces table [the module asks for](../../phases/00-linux-primitives.md#m0-1): one row per type, with one thing a process in that namespace cannot see or affect. UTS is now filled in. You will complete it over the next three exercises and the capstone will need it.

**Teardown** — `exit` the `unshare` shell. Leave the guest up; [the PID namespace](02-pid-namespace-and-proc.md) is next and every exercise in this phase runs on it.
