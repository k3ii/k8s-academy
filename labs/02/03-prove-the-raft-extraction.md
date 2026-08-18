<a id="prove-the-raft-extraction"></a>
# Raft is a second repository, and here is when it became one

**Claim** — you can show with a commit or a `go.mod` line that the Raft library is no longer inside `etcd-io/etcd`, and say when it left — so that any article which reads Raft and the store in a single clone is dated on sight.

**Rests on** — [exercise 1](01-two-blobless-clones.md)'s two clones, and [the stale-paths list](../../strands/source-archaeology.md#stale-paths).

**Topology** — none. [`forge`](../../strands/lab-topologies.md#build-guest) only; it is [not part of any topology](../../strands/lab-topologies.md#build-guest) and is up regardless.

**Do**

1. Ask the current tree where Raft comes from:

   ```sh
   cd ~/src/etcd
   grep -rn 'go.etcd.io/raft' server/go.mod go.mod 2>/dev/null
   ```

   A module requirement is a citation with a version in it. Record the line verbatim.

2. Confirm the code is gone rather than merely re-imported. Look for the directory the old articles cite, then for the symbol:

   ```sh
   ls raft 2>&1 | head -1
   git log --oneline --diff-filter=D -- raft/raft.go | head -3
   ```

   `--diff-filter=D` is technique 3: it finds the commit that *deleted* a path, which is the only commit `git log <path>` on the current tree will never show you.

3. Get the date and the release from the deletion sha `D`:

   ```sh
   git show -s --format='%H %ci %s' <D>
   git tag --contains <D> | grep -E '^v3\.[0-9]+\.[0-9]+$' | sort -V | head -2
   ```

4. Now from the other repo's side. In `~/src/raft`:

   ```sh
   cd ~/src/raft
   head -3 go.mod
   git log --oneline | tail -5
   ```

   Read the *oldest* commits. The extraction preserved history, so the bottom of that log is etcd's own past — which is why a symbol can be findable in both repos and current in only one.

5. Test what that costs a reader. Pick any symbol from Figure 2's vocabulary, `MsgVote` or `Ready`, and search for it in both clones:

   ```sh
   (cd ~/src/etcd && git grep -n 'MsgVote' -- '*.go' | head -3)
   (cd ~/src/raft && git grep -n 'MsgVote' -- '*.go' | head -3)
   ```

**Expect** — `etcd/go.mod` (or `server/go.mod`) requires `go.etcd.io/raft` at a pinned version, the top-level `raft/` directory does not exist in the current tree, and `--diff-filter=D` names the commit that removed it. Step 5 is the payoff: hits in `~/src/etcd` are *consumers* of the library — `etcdserver/raft.go` calling into it — while the implementation is only in `~/src/raft`. An article that walks from `Ready()` into the algorithm inside one clone was written before that commit, and you can now say which one.

**Write down** — the second `Was → Is` row, with the deletion sha or the `go.mod` line as the identifier. Both archaeology rows [the checklist](../../phases/02-etcd.md#checklist) asks for are now done, and the pinned version in step 1 is the one detail to carry forward: when [module 2.2](../../phases/02-etcd.md#m2-2) reads `raft/doc.go`, read it at *that* version, not at `main`.

**Teardown** — nothing was created. Both clones stay.
