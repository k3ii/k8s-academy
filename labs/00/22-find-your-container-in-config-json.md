<a id="find-your-container-in-config-json"></a>
# Find your script inside the OCI runtime spec

**Artifact** — a third column added to [your flag mapping](21-docker-flags-to-primitives.md): the field in an OCI `config.json` that carries the same setting. This is [the phase's ecosystem item](../../phases/00-linux-primitives.md#ecosystem), and it is **read, do not run** — you already built what `runc` is.

**Rests on** — nothing new. Every row you need is already in the mapping table; this exercise only asks where the productised form writes it down.

**Topology** — **none.** This is reading and typing on any machine with a browser and a git clone. `bare` can stay up or come down; it is not involved.

**Do**

1. Open [`opencontainers/runtime-spec`](https://github.com/opencontainers/runtime-spec) and read `config.md` and `config-linux.md` — the schema, not the prose introduction.
2. Find each of your six capstone steps in it. The questions to answer from the document, with the field paths to confirm:
   - `linux.namespaces` — it is a *list of objects*, not a set of flags. What is the second field of each object for, and what does it let a runtime do that `unshare` flags cannot?
   - `linux.resources.memory` — which of its fields correspond to `memory.max`, `memory.high` and `memory.swap.max`, and which one has no cgroup v2 equivalent at all?
   - `process.capabilities` — five sets are listed. Compare them with the five `Cap*` lines you read in [the capability exercise](17-drop-a-capability.md). Which one does the spec make you set explicitly that `capsh --drop` handled implicitly?
   - `root.path` and `root.readonly` — the spec says the runtime performs a `pivot_root` *or* a `chroot`. Find the sentence, and say which one it prefers and under what condition.
   - `mounts` — find where propagation is expressed, and match it to the modes from [exercise 15](15-mount-propagation.md).
3. Then read one implementation, not for code to copy: in [`opencontainers/runc`](https://github.com/opencontainers/runc), open `libcontainer/container_linux.go` and `libcontainer/rootfs_linux.go`, and find the `pivot_root` call and the cgroup path writes. Cite the function name for each.
4. Answer the question the comparison exists to answer: **what does `runc` do that `contain.sh` does not?** Aim for four or five specific items, not a general "it is more robust". Hooks, the console socket, the `create`/`start` split, cgroup v1 compatibility and rootless mode are the ones worth finding.

**Observe**

```sh
git clone --depth 1 https://github.com/opencontainers/runc
grep -rn 'pivot_root\|PivotRoot' runc/libcontainer/rootfs_linux.go | head
grep -rn 'func (c \*Container) Start\|func (c \*Container) Create' runc/libcontainer/container_linux.go
```

**Expect** — the mapping is nearly one-to-one, and that is the finding: a container runtime is a program that reads that JSON and makes the syscalls you made by hand. The `create`/`start` split is the largest genuine difference, and it exists so that a supervisor can set up a container and start it later — the same supervision gap [the flag mapping](21-docker-flags-to-primitives.md) found had no kernel primitive.

**Write down** — the third column, plus the four-or-five-item answer to step 4. Then one sentence you will re-read in [P11](../../phases/11-synthesis.md): the synthesis capstone traces `kubectl run` down to a `runc` invocation, and `runc` bottoms out in `config.json`, which bottoms out here.

**Teardown** — nothing was provisioned. **This is the end of P0's lab chain**: run [the teardown](../../strands/lab-topologies.md#teardown) and destroy `bare` before starting [P1](../../phases/01-operate-shallow.md), which needs the RAM for a real cluster.
