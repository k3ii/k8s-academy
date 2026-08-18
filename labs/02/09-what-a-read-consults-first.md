<a id="what-a-read-consults-first"></a>
# The index is in memory, and it is not free

**Claim** — the read path resolves a key to a revision in an **in-memory B-tree** before it touches bbolt; that tree is rebuilt from disk at every start; its size tracks the number of keys and generations rather than the number of bytes; and **deleting keys does not shrink it**.

**Rests on** — [module 2.1's](../../phases/02-etcd.md#m2-1) `index.go` reading question — what a read consults before it ever touches bbolt — and [exercise 6](06-ten-writes-and-a-compaction.md)'s generations. The last clause of the claim is the one to predict before measuring: say now whether `del` on 100,000 keys returns memory, and why.

**Topology** — [`etcd-only`](../../strands/lab-topologies.md#etcd-only). Do the writing from `.160` and the measuring on whichever member you prefer; the index is per-member and all three should agree.

**Setup**

Record the baseline on one member before anything:

```sh
ssh zain@10.10.10.161 'ps -o rss=,etime= -C etcd; ls -l /var/lib/etcd/member/snap/db'
```

**Do**

1. Write 100,000 small keys. One `put` per key is a Raft round trip and a `fsync` and will take the afternoon, so batch them the way [exercise 8](08-what-sub-is-for.md) showed:

   ```sh
   for b in $(seq 0 999); do
     { echo; for i in $(seq 0 99); do echo "put /bulk/$b/$i x"; done; echo; } | etcdctl txn > /dev/null
   done
   ```

2. Measure again, on the same member, and also on disk:

   ```sh
   ssh zain@10.10.10.161 'ps -o rss= -C etcd; ls -l /var/lib/etcd/member/snap/db'
   ```

3. **Restart that member and time it.** This is the load-bearing observation — the tree is not persisted, it is rebuilt:

   ```sh
   ssh zain@10.10.10.161 'sudo systemctl restart etcd; journalctl -u etcd -n 40 --no-pager'
   ```

   Compare to how long it took to start in [exercise 5](05-three-members-by-hand.md) with an empty store, and read the log lines about recovering the store — they name what is being rebuilt and from what.

4. **Now delete everything and measure a third time**, without restarting:

   ```sh
   etcdctl del --prefix /bulk/
   ssh zain@10.10.10.161 'ps -o rss= -C etcd'
   ```

5. Then compact, and measure a fourth time:

   ```sh
   etcdctl compact "$(etcdctl endpoint status -w json | python3 -c 'import sys,json; print(json.load(sys.stdin)[0]["Status"]["header"]["revision"])')"
   ssh zain@10.10.10.161 'ps -o rss= -C etcd'
   ```

6. Read the code that made steps 4 and 5 come out the way they did:

   ```sh
   (cd ~/src/etcd && git grep -n 'func (ti \*treeIndex) Range\|func (ti \*treeIndex) Compact' -- server/storage/mvcc/index.go)
   ```

**Expect** — RSS rises with key count in step 2, does **not** come back in step 4, and only moves after step 5. `del` writes a tombstone and closes a generation; the keyIndex stays in the tree so that a `--rev` read below the tombstone can still be answered. Compaction is the only thing that removes it, which is why an etcd whose keys churn constantly but is never compacted grows in memory with nothing to show for it on disk.

**Two confounds, and you should name both rather than ignore them.** bbolt is `mmap`ed, so part of the RSS you measured is file pages, not index — bound it by comparing the RSS delta to the `db` file's growth in step 2. And Go's heap does not return freed memory to the OS promptly, so step 5's drop may lag; if RSS has not moved, wait and measure again rather than concluding the compaction did nothing. **This is why the phase insists on reading the shape and not the magnitude** — the direction of each of these four measurements is the claim, and the absolute numbers on a 1024MB guest are not.

The restart in step 3 takes visibly longer than the empty start. That time is the rebuild, and it is the answer to a question that will come back in [module 2.5](../../phases/02-etcd.md#m2-5): a member with a large store is slow to come back, which is a thing you have to plan a recovery around.

**Write down** — the four RSS numbers with what changed between each, and one sentence naming what a `Range` call consults first and what it consults second. That sentence is the module's `index.go` answer.

**Teardown** — the keys are already deleted and compacted. Confirm with `etcdctl get --prefix /bulk/ --keys-only | head`. **The topology stays** — but note the `db` file is still large, and [exercise 20](20-compaction-frees-no-disk.md) is about exactly that.
