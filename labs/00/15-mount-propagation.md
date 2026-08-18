<a id="mount-propagation"></a>
# Predict whether a mount crosses the namespace boundary

**Claim** — for a given propagation mode you can predict, before mounting, whether a mount made inside a namespace appears on the host and whether a mount made on the host appears inside. `private`, `rshared` and `rslave` give three different answers and only one of them is symmetric.

**Topology** — [`bare`](../../strands/lab-topologies.md#bare), still up, still as root.

**Setup** — two directories to mount into, `/mnt/inside` and `/mnt/outside`, and a `tmpfs` to mount. Keep a second SSH session open as the host observer throughout; you will be reading `/proc/self/mountinfo` in both at once.

**Do**

1. In the host session, `findmnt -o TARGET,PROPAGATION /` and record what `/` is set to by default on this guest.
2. **Private.** `unshare --mount --propagation private --fork bash`. Inside, `mount -t tmpfs none /mnt/inside`. Check both sessions. Then, from the host, mount a `tmpfs` on `/mnt/outside` and check inside.
3. **Slave.** Repeat with `--propagation slave`. Mount from the host; check inside. Mount from inside; check the host. Note which direction works.
4. **Shared.** Repeat with `--propagation shared` (you may need `mount --make-rshared /` on the host first). Mount from each side and check the other.
5. Now do it wrong on purpose, which is [the module's break](../../phases/00-linux-primitives.md#m0-4): mount inside a `private` namespace something you intended the host to see. Confirm the host does not see it and that there is **no error anywhere** — this is a silent failure, not a loud one.
6. Read the propagation column for each mount you made: `findmnt -o TARGET,PROPAGATION,FS-OPTIONS`.

**Observe**

```sh
findmnt -o TARGET,PROPAGATION                  # run in both sessions after each step
grep /mnt/inside /proc/self/mountinfo          # the shared:N / master:N tags
```

**Expect** — three distinct outcomes:

| Mode | Host → namespace | Namespace → host |
|---|---|---|
| `private` | invisible | invisible |
| `slave` | **visible** | invisible |
| `shared` | visible | **visible** |

`mountinfo`'s optional fields carry the proof: `shared:N` marks a peer group, `master:N` marks a slave of group N, and a private mount has neither. Step 5 produces no error at all — the mount succeeds, and it is simply somewhere nobody else is looking.

**Write down** — the table above from memory, and the answer to [the checklist claim](../../phases/00-linux-primitives.md#checklist) on which mode makes an in-namespace mount visible on the host. Then name the consumer: [P8's CSI node DaemonSet](../../phases/08-storage.md) sets `mountPropagation: Bidirectional`, which is `rshared`, because a volume the driver mounts inside its own container must reach the host to be bind-mounted into other pods. Get it wrong and the mount is invisible exactly where it is needed, with no error — which is step 5, in production.

**Teardown** — `exit` each namespace, then from the host `umount /mnt/outside` and confirm `findmnt | grep -c tmpfs` is back to its starting count. If you ran step 4, `mount --make-rprivate /` to put the host's propagation back the way you found it. Guest stays up.
