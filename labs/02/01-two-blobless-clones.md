<a id="two-blobless-clones"></a>
# Two clones, and an entry point that resolves

**Artifact** — `etcd-io/etcd` and `etcd-io/raft` cloned on [`forge`](../../strands/lab-topologies.md#build-guest) with full history and no blobs, plus a one-line receipt proving that `server/storage/mvcc/key_index.go` exists in the tree you just cloned.

**Rests on** — [module 2.0's reading](../../phases/02-etcd.md#m2-0): [the method](../../strands/source-archaeology.md#method) and [the seven recorded moves](../../strands/source-archaeology.md#stale-paths). Read both before typing anything here. This exercise is the setup for the next three, and it is the setup for the rest of the curriculum — every phase from here on cites source, and every citation is checked against a tree that lives here.

**Topology** — none. `forge` is up regardless of which topology is running, which is [the whole point of it not being in one](../../strands/lab-topologies.md#build-guest). No lab guest is needed until [exercise 5](05-three-members-by-hand.md).

**Do**

1. On `forge`, clone both repos [blobless](../../strands/source-archaeology.md#clone):

   ```sh
   mkdir -p ~/src && cd ~/src
   git clone --filter=blob:none https://github.com/etcd-io/etcd
   git clone --filter=blob:none https://github.com/etcd-io/raft
   ```

   `--depth 1` is the wrong shortcut and the next two exercises are built to fail without history. A blobless clone has every commit and no file contents until you ask for one; `--depth 1` has one commit.

2. Confirm the entry point resolves in the tree you actually have:

   ```sh
   cd ~/src/etcd
   git log -1 --format='%H %d %ci'
   ls -l server/storage/mvcc/key_index.go
   git grep -n 'func (ki \*keyIndex) compact' -- server/storage/mvcc/key_index.go
   ```

3. Record which release you are reading, because every `file:line` you write for the next month is only true against one:

   ```sh
   git describe --tags
   git tag --sort=-v:refname | grep -E '^v3\.[0-9]+\.[0-9]+$' | head -5
   ```

4. Do the same three steps in `~/src/raft`, whose entry point is `raft.go` at the repo root — not under any `server/` path. That difference is [exercise 3](03-prove-the-raft-extraction.md)'s subject.

5. Note the cost. `du -sh ~/src/etcd ~/src/raft` now, then again after [exercise 4](04-refute-a-published-path.md) has pulled blobs on demand. A blobless clone grows as you read it.

**Expect** — `key_index.go` is present at `server/storage/mvcc/`, and `git grep` finds `compact` as a method on `*keyIndex`. If either fails you have cloned something else or you are on a detached tag old enough to predate the move, which [exercise 2](02-date-the-mvcc-move.md) will date exactly. `git describe --tags` prints a commit ahead of the newest tag — you are on `main`, not on a release, and saying so in a write-up is the difference between a citation that survives checking and one that does not.

**Write down** — the commit sha from step 2 and the newest release tag from step 3, at the top of your phase notes. Every `file:line` in [the capstone](../../phases/02-etcd.md#capstone) is a claim about *that* sha, and [gate condition 2](../../phases/02-etcd.md#gate) is checked against it.

**Footprint note** — two blobless clones of etcd and raft are on the order of a few hundred MB together, and they live on `forge`'s disk, not in a topology. They survive every teardown in this phase deliberately: the citations outlive the cluster.

**Teardown** — nothing to delete. The clones stay for the whole phase and are wanted again in [P3](../../phases/03-api-machinery.md), which reads the apiserver's storage layer down onto this one. No topology was involved.
