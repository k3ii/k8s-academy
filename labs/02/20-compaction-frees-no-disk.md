<a id="compaction-frees-no-disk"></a>
# Compaction moves one number and not the other

**Claim** — compaction removes revisions and returns **no bytes to the filesystem**; the `db` file does not shrink, and etcd reports this honestly in two separate fields whose divergence is the whole story. This is the first half of [objective 6](../../phases/02-etcd.md#objectives) and the first half of [the capstone's](../../phases/02-etcd.md#capstone) measurement.

**Rests on** — [module 2.4's](../../phases/02-etcd.md#m2-4) `kvstore_compaction.go` reading question: compaction is a **batched bbolt delete loop** — why does deleting revisions free logical space but return no disk? Write the answer first. This exercise is the proof, and it should not surprise you.

**Topology** — [`etcd-only`](../../strands/lab-topologies.md#etcd-only), ideally still carrying the `/sync/` keys [exercise 17](17-synced-unsynced-victim.md) told you to keep.

**Setup — the churn**

Inflate the store with write-delete churn, which is the pattern that produces the problem in the field: the key count stays flat and the revision count does not.

```sh
for round in $(seq 1 40); do
  for b in $(seq 0 24); do
    { echo; for i in $(seq 0 99); do echo "put /churn/$i r$round"; done; echo; } | etcdctl txn > /dev/null
  done
  echo "round $round"
done
```

**Do**

1. Take the measurement in the form that separates the two numbers. `-w table` shows one of them; `-w json` shows both:

   ```sh
   etcdctl endpoint status --cluster -w table
   etcdctl endpoint status --cluster -w json | python3 -m json.tool | grep -E 'dbSize|dbSizeInUse|revision'
   ls -l /var/lib/etcd/member/snap/db
   ```

   Record all three: `dbSize`, `dbSizeInUse`, and the file size on disk. Say now which two of the three you expect to move when you compact.

2. Compact to the current revision:

   ```sh
   REV=$(etcdctl endpoint status -w json | python3 -c 'import sys,json; print(json.load(sys.stdin)[0]["Status"]["header"]["revision"])')
   etcdctl compact $REV
   ```

3. Measure again, all three, on all three members.

4. Prove the revisions are actually gone rather than merely hidden — a read below the compaction point must now fail:

   ```sh
   etcdctl get /churn/0 --rev=$((REV - 5000))
   ```

5. Read the loop that did it, and cite it:

   ```sh
   cd ~/src/etcd
   git grep -n 'func (s \*store) scheduleCompaction' -A 30 -- server/storage/mvcc/kvstore_compaction.go
   ```

   Answer from the code: what does it delete, in batches of what, and what does it **not** call? The absence is the point — find the operation that would have returned space and confirm it is not there.

6. Say where the freed space went. It is not gone and it is not returned; name the structure it is now in and what will reuse it:

   ```sh
   git grep -n 'freelist\|FreelistType' -- server/storage/backend/backend.go | head
   ```

**Observe** — after the compaction, `dbSizeInUse` drops substantially. `dbSize` does not move. The file on disk does not move.

**Expect** — exactly that divergence, on all three members, because compaction is replicated. `dbSize` is what the file costs you; `dbSizeInUse` is what the data inside it costs. The gap between them is free pages inside the file — space bbolt will happily reuse for the next writes and will never hand back to the filesystem on its own.

This is why "we compacted and the disk is still full" is one of the most common etcd support threads in existence, and it is not a bug in any layer. **Compaction is a logical operation on a B+tree; the file is a container the tree lives in.** Nothing in the compaction path resizes the container.

**Footprint note — read the shape, not the magnitude.** The churn above is sized to move these numbers visibly on a 10G guest, not to resemble any real cluster. What you are producing is a *direction* per number: `dbSizeInUse` down, `dbSize` flat. Absolute bytes on this hardware are meaningless and claiming them in the capstone is [the stated failure mode](../../phases/02-etcd.md#capstone).

**Write down** — the three numbers before and after, and the one-sentence *why* from step 5, carrying the `kvstore_compaction.go` `file:line`. That citation is one of the four [the capstone](../../phases/02-etcd.md#capstone) requires, and this before/after pair is the first half of its measurement.

**Teardown** — **nothing.** Leave the inflated `db` exactly as it is; [exercise 21](21-defrag-frees-disk-and-blocks.md) is the other half of this measurement and needs the gap you just created. **The topology stays.**
