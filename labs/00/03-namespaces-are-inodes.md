<a id="namespaces-are-inodes"></a>
# A namespace is a file you can point at

**Claim** — a namespace's identity is an inode under `/proc/<pid>/ns/`. Two processes are "in the same namespace" exactly when those inode numbers match, and joining one is an open-and-`setns` on that file — which is all `nsenter` does.

**Rests on** — [Module 0.1's reading question](../../phases/00-linux-primitives.md#m0-1) on which namespace a process joins by writing to `/proc/<pid>/ns/*`, and the `man 7 user_namespaces` answer on UID/GID mapping.

**Topology** — [`bare`](../../strands/lab-topologies.md#bare), still up from [the UTS namespace](01-uts-namespace.md), still as root.

**Do**

1. `readlink /proc/self/ns/*` in your login shell. Record all seven inode numbers.
2. Open a second SSH session and do the same. Compare: every number matches, because both shells are in the host's namespaces.
3. Start a long-lived process in a new network namespace: `unshare --net --fork sleep 3600 &`, and note its host PID.
4. `readlink /proc/<pid>/ns/net` for that process. It differs from yours; every other one matches.
5. Join it: `nsenter -t <pid> -n ip addr`. You see one interface, `lo`, and it is down.
6. Do the same from the other direction — `nsenter -t 1 -n ip addr` — and confirm you are back to the host's interfaces.
7. `ls -l /proc/<pid>/ns/net` and note it is a symlink to a magic target, not a real path. You cannot `cat` it; you can only `open` it and hand the fd to `setns`.

**Observe**

```sh
readlink /proc/self/ns/net /proc/<pid>/ns/net
lsns -t net                       # every net namespace on the box, with its users
nsenter -t <pid> -n ip -br addr
```

**Expect** — `lsns` lists the new network namespace with exactly one process in it. The `sleep` has its own empty network stack and shares everything else with the host, which is why it is still visible in `ps` and still shares your hostname. Kill the `sleep` and the namespace disappears from `lsns` — a namespace with no processes and no bind-mounted reference does not exist.

**Write down** — the mechanism in one line: *a namespace lives as long as something references it — a process, or a bind mount of its `/proc/<pid>/ns/` file.* That second half is how `ip netns add` makes a namespace that outlives every process in it, which is what [the veth exercise](09-link-address-route.md) depends on.

**Teardown** — `kill %1` to end the `sleep`. Confirm with `lsns -t net` that the namespace is gone. Guest stays up.
