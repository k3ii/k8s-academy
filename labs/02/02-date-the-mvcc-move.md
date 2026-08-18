<a id="date-the-mvcc-move"></a>
# The release that moved `mvcc/` under `server/`

**Claim** — you can name the first release that shipped the `server/storage/` path, and support it two independent ways: a commit sha from `git log --follow`, and a tag that contains that sha.

**Rests on** — [exercise 1](01-two-blobless-clones.md)'s clone, and technique 2 of [the method](../../strands/source-archaeology.md#method). This is the first of [the two moves that are yours this phase](../../phases/02-etcd.md#m2-0).

**Topology** — none. [`forge`](../../strands/lab-topologies.md#build-guest) only; it is [not part of any topology](../../strands/lab-topologies.md#build-guest) and is up regardless.

**Do**

1. Follow the file backwards through the rename:

   ```sh
   cd ~/src/etcd
   git log --follow --oneline -- server/storage/mvcc/key_index.go | tail -20
   ```

   Read the bottom of that output first: the earliest commits are for a path that is not the one you asked about.

2. Find the rename itself rather than eyeballing it. Ask git to show you the commit where the name changed:

   ```sh
   git log --follow --name-status --diff-filter=R --format='%H %s' \
     -- server/storage/mvcc/key_index.go | head -20
   ```

3. Now date it. Given the sha `S` from step 2:

   ```sh
   git tag --contains <S> | grep -E '^v3\.[0-9]+\.[0-9]+$' | sort -V | head -3
   ```

   The first tag in that list is your answer to *which release first shipped it*.

4. Cross-check from the other end, without using the answer you just got. Pick a release well before and one well after, and ask what the path was in each:

   ```sh
   git ls-tree --name-only v3.4.0  | head
   git ls-tree --name-only v3.5.0  | head
   ```

   One of them has a top-level `mvcc/`; one has `server/`. That bracket is the check on step 3.

5. Do the same for one more file so the technique is not a single lucky result: `server/storage/mvcc/revision.go`, which [module 2.1](../../phases/02-etcd.md#m2-1) reads next.

**Expect** — `--follow` crosses the rename and shows commits touching `mvcc/key_index.go` under its old path, and step 4's two `ls-tree` listings disagree about whether a top-level `mvcc/` exists. If `--follow` shows nothing before the move, you cloned with `--depth 1` after all — the technique needs the history [exercise 1](01-two-blobless-clones.md) told you to keep. Beware the trap in step 3: `git tag --contains` lists *every* tag containing the sha, including release candidates and later minors, so it must be sorted and read as "the earliest of these", not "the first line printed".

**Write down** — the `Was → Is` row for this move, with the sha and the release. Format it exactly as [the checklist](../../phases/02-etcd.md#checklist) asks: a path, an arrow, a path, and the identifier a hostile reader would use to check you. One of the two archaeology rows is now done.

**Teardown** — nothing was created. The clone stays; [exercise 3](03-prove-the-raft-extraction.md) uses the other one.
