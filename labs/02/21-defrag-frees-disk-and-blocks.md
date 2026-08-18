<a id="defrag-frees-disk-and-blocks"></a>
# Defrag returns the disk and stops the member while it does

**Claim** — `defrag` rewrites the `db` file and **does** return bytes to the filesystem, and it **blocks the member it runs on** for the duration — so the same operation that fixes the disk problem is an availability event, and running it on all three members at once is a self-inflicted outage.

**Rests on** — [exercise 20](20-compaction-frees-no-disk.md)'s inflated file, which must still be inflated, and [module 2.4's](../../phases/02-etcd.md#m2-4) `backend.go` question: where does `Defrag()` run, and why must it block?

**Topology** — [`etcd-only`](../../strands/lab-topologies.md#etcd-only).

**Setup**

Record the three numbers again, and start a writer and a reader against **`.161`, the member you are not about to defrag**, plus one against `.160`, which you are:

```sh
etcdctl endpoint status --cluster -w json | python3 -m json.tool | grep -E 'dbSize|dbSizeInUse'

# terminal A — against the member being defragged
while true; do
  S=$( { time etcdctl --endpoints=http://10.10.10.160:2379 get /churn/0 ; } 2>&1 | grep real )
  echo "160 $S"
done

# terminal B — against a member that is not
while true; do etcdctl --endpoints=http://10.10.10.161:2379 put /defrag/probe "$(date +%s%N)" > /dev/null \
  && echo "161 ok" || echo "161 FAIL"; sleep 0.2; done
```

**Do**

1. Defrag **one member only**, and time it:

   ```sh
   time etcdctl --endpoints=http://10.10.10.160:2379 defrag
   ```

2. While it runs, watch both terminals. Note when `.160` stops answering and for how long, and whether `.161` ever misses a write.

3. Measure afterwards:

   ```sh
   etcdctl endpoint status --cluster -w json | python3 -m json.tool | grep -E 'dbSize|dbSizeInUse'
   ls -l /var/lib/etcd/member/snap/db
   ```

   Note that `.161` and `.162` are unchanged. **Defrag is not replicated** — it is a local file operation, and each member needs it separately. Say why that follows from what the file is.

4. Defrag the other two, one at a time, waiting for each to finish:

   ```sh
   etcdctl --endpoints=http://10.10.10.161:2379 defrag
   etcdctl --endpoints=http://10.10.10.162:2379 defrag
   ```

5. Now find out what "blocks" means precisely. Read the code and answer with `file:line`:

   ```sh
   cd ~/src/etcd
   git grep -n 'func (b \*backend) Defrag\|func (b \*backend) defrag' -A 40 -- server/storage/backend/backend.go
   ```

   What lock does it take? What does it do to the existing bbolt handle? And the question that explains all of it: **bbolt permits one writer at a time** — given that, is there any implementation of defrag that would not block?

6. Consider the thing you did not do, and say what it would have cost:

   ```sh
   # do NOT run this
   # etcdctl defrag --cluster
   ```

   With three members and one defrag taking `T` seconds, say what `--cluster` does to availability and why the ordering in step 4 was not fussiness.

**Observe** — `.160` stops answering for the duration in terminal A. Terminal B never fails: two members are a quorum, the third is merely absent, and the cluster is exactly as available as [exercise 15](15-partition-one-member.md) showed a two-of-three cluster to be.

**Expect** — `dbSize` drops to near `dbSizeInUse` and the file on disk drops with it. That is the second half of the pair: **compaction moved `dbSizeInUse`, defrag moved `dbSize`.** Two operations, two numbers, and conflating them is the misconception [module 2.4](../../phases/02-etcd.md#m2-4) exists to remove.

Step 5's answer is the mechanism: defrag rewrites the file by copying live pages into a new one and swapping it in, under a lock that excludes everything. With a single-writer B+tree there is no incremental version of that, which is why the operation is offline-by-construction rather than offline-by-neglect.

**Footprint note** — the defrag rewrites the file, so **the guest needs free space for two copies at once**. On a 10G disk with a `db` of a few hundred MB this is comfortable; with a `db` at the default 2GB quota it would still be fine, and on a real cluster it is the check to make before starting. Time it on this hardware and note the number: a 35 W i5 with contended disk is the slow end, which makes it a useful upper bound rather than a bad measurement.

**Write down** — the four numbers (`dbSize` and `dbSizeInUse`, before and after) and the blocked duration, plus one sentence each on why compaction did not move the first number and defrag did. That is [the checklist's](../../phases/02-etcd.md#checklist) two-measurements item, and with [exercise 20](20-compaction-frees-no-disk.md) it is [the capstone's](../../phases/02-etcd.md#capstone) defrag curve. Cite the `backend.go` `Defrag()` `file:line` — the capstone requires it.

**Teardown** — `etcdctl del --prefix /defrag/`, `etcdctl del --prefix /churn/`, `etcdctl del --prefix /sync/` — the last of these has been carried since [exercise 17](17-synced-unsynced-victim.md) and this is where it is finally spent — and stop both loops. **The topology stays.**
