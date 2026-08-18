<a id="ten-writes-and-a-compaction"></a>
# Predict which historical reads survive a compaction

**Claim** — given a key written ten times and a compaction at revision *r*, you can say **before running anything** which `get --rev=k` calls still return a value and which return `ErrCompacted` — derived from the generations structure in `key_index.go`, not by trying it.

**Rests on** — [module 2.1's](../../phases/02-etcd.md#m2-1) `key_index.go` reading question: what a *generation* contains, and what `compact(rev)` removes versus leaves behind. **[Gate condition 3](../../phases/02-etcd.md#gate) is this exercise.** Answer the reading question in writing first; the prediction below is worthless if you make it after seeing the output.

**Topology** — [`etcd-only`](../../strands/lab-topologies.md#etcd-only), the cluster from [exercise 5](05-three-members-by-hand.md).

**Setup**

```sh
etcdctl put /gen/pred 0        # note the header revision of this one
for i in $(seq 1 9); do etcdctl put /gen/pred $i; done
etcdctl get /gen/pred -w json | python3 -m json.tool
```

Record the `mod_revision` of the last write and the cluster's current `header.revision`. Those two numbers are not the same and the gap is other traffic — your own earlier keys, plus etcd's internal writes.

**Do**

1. **Predict, on paper.** Let your ten writes land at revisions `R0 … R9`. Choose a compaction revision `C = R5`. Write down, for each of `R0`, `R4`, `R5`, `R6`, `R9`, and `C-1`, whether `get /gen/pred --rev=<that>` will return a value, return an error, or return a *different* value than it would have before. Six answers, committed before step 3.

2. Confirm your reads work *now*, before compaction, so a later failure is unambiguous:

   ```sh
   for r in R0 R4 R5 R6 R9; do echo "== $r"; etcdctl get /gen/pred --rev=$r; done
   ```

3. Compact:

   ```sh
   etcdctl compact R5
   ```

4. Run the same loop again, plus `--rev=$((R5-1))`.

5. Now the case that separates a correct model from a lucky one. Create a *second* key, write it three times, **delete it**, then write it twice more, then compact past the delete:

   ```sh
   etcdctl put /gen/tomb a; etcdctl put /gen/tomb b; etcdctl put /gen/tomb c
   etcdctl del /gen/tomb
   etcdctl put /gen/tomb d; etcdctl put /gen/tomb e
   ```

   Predict first: after compacting at a revision *above* the delete, how many generations does this keyIndex have left, and what does a `--rev` read at a revision inside the first generation return — an error, an empty result, or `c`? These are three different answers and only one is right.

**Expect** — reads at or above `C` succeed; reads below `C` fail with `etcdserver: mvcc: required revision has been compacted`. The one that catches people is `--rev=C` itself: it survives, because compaction keeps the *latest* revision of each live key at or below `C` — that is what makes the store readable at all after a compaction, and it is why `compact(rev)` in `key_index.go` removes a prefix of a generation rather than the generation.

Step 5's answer comes from the same function: a delete closes a generation with a tombstone, and compacting past a tombstone drops the whole closed generation. So the read at a revision inside it does not return `c` and does not return "no such key at that revision" — it returns the same compaction error, because that revision no longer exists in the index at all.

**Write down** — the six predictions from step 1 against the six results, marked right or wrong, and the generations of `/gen/pred` and `/gen/tomb` before and after. That before/after pair is [the checklist's](../../phases/02-etcd.md#checklist) *ten-write key's generations* item. **The wrong predictions are the valuable half** — note which one you got wrong and which sentence of `key_index.go` you had misread.

**Teardown** — `etcdctl del --prefix /gen/`. Note that the deletion does not shrink anything; it adds revisions. **The topology stays.**
