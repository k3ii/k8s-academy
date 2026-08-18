<a id="the-capstone-writeup"></a>
# The capstone — one sitting, two artifacts, four citations

**Artifact** — [the phase's capstone](../../phases/02-etcd.md#capstone): a quorum-loss recovery and a defrag curve, done in one sitting against a cluster you have not prepared, written up with four `file:line` citations that survive checking. **[Gate condition 2](../../phases/02-etcd.md#gate) is those citations resolving in the live tree**, and a cluster that came back with a write-up whose paths do not resolve is a fail.

**Rests on** — everything, and specifically [exercise 20](20-compaction-frees-no-disk.md) and [exercise 21](21-defrag-frees-disk-and-blocks.md) for the curve, [exercise 27](27-lose-quorum.md) and [exercise 28](28-restore-from-snapshot.md) for the recovery, and [exercise 19](19-the-chain-four-layers-up.md) for [gate condition 1](../../phases/02-etcd.md#gate), which is recited rather than written.

**The rule that makes this a capstone rather than a repetition: no reading from the previous files.** Notes you wrote are allowed; the exercise files are not. If you cannot get through the restore without opening [exercise 28](28-restore-from-snapshot.md), that is the finding, and the answer is to run 28 again rather than to look.

**Topology** — [`etcd-only`](../../strands/lab-topologies.md#etcd-only), three healthy members with agreeing `hashkv`. This is the last thing the cluster does.

**Do**

**Part 1 — the defrag curve.**

1. Churn the store with write-delete traffic until `dbSize` has moved by a factor you can plot. Record `dbSize`, `dbSizeInUse` and the file size at three or four points during the churn, not just at the end — the curve needs more than two points to have a shape.
2. Compact. Record all three numbers again.
3. Defrag, one member at a time, timing each. Record all three again.
4. Tabulate or plot it. **The claim you are defending is the shape**: one number falls at step 2 and one at step 3, and they are not the same number.

**Part 2 — the quorum-loss recovery.**

5. Snapshot, and note the revision.
6. Write a countable amount of data after the snapshot.
7. Stop two members with `qm stop`. Demonstrate — with commands and their output, not with assertion — that the survivor cannot write and cannot serve a linearizable read, and *can* serve a stale one.
8. Restore all three from the snapshot with a new token, fix the units, bring them back, verify membership and hashes.
9. Count what the restore discarded, and state it as a number.

**Part 3 — the write-up.**

10. Four citations, each a `file:line` in the tree at the sha you recorded in [exercise 1](01-two-blobless-clones.md):

    - the batched-delete loop in `server/storage/mvcc/kvstore_compaction.go` that frees revisions without freeing disk;
    - where `Defrag()` runs in `server/storage/backend/` and why it must block;
    - the `ErrCompacted` site in `server/storage/mvcc/watchable_store.go`;
    - the `revision{main, sub}` encoding in `server/storage/mvcc/revision.go`.

11. **Check your own citations before submitting them to yourself.** For each, run the command that proves it and paste the output:

    ```sh
    cd ~/src/etcd && git rev-parse HEAD
    sed -n '<line>p' server/storage/mvcc/kvstore_compaction.go
    ```

    A `file:line` without the sha it is true at is not checkable, because line numbers move. State the sha once at the top of the write-up and every citation inherits it.

12. Write the recovery procedure so **another person could follow it** — which is a different document from the one you followed. Ordered steps, each with the reason it is in that position, and the two failure modes that come from doing it out of order.

**Expect** — part 1 takes an hour and part 2 takes longer than you plan for, because the restore's per-member steps are where the time goes and because something will be wrong with a unit file. That is the realistic shape and it is worth measuring: **note the wall-clock time of the recovery next to the store size**, because a recovery plan without a duration is not a plan.

The two places this most often fails on a first attempt: the write-up claims absolute byte counts as if they meant something, which [the capstone explicitly calls the failure mode](../../phases/02-etcd.md#capstone) on a 35 W i5 with contended disk; and a citation is copied from a note taken three weeks ago against a tree that has since moved under `git pull`. Step 11 is the guard against the second, and there is no guard against the first except writing *shape* and not *magnitude*.

**Write down** — the whole thing, in `journal/02-etcd.md`. Then close it, and recite [the four-arrow chain](19-the-chain-four-layers-up.md) from memory. That is [gate condition 1](../../phases/02-etcd.md#gate), it is not written anywhere in the capstone, and it is the one the next two phases actually depend on.

**Footprint note** — nothing new. The churn in part 1 is bounded by the guests' 10G disks and by the fact that you are about to destroy them.

**Teardown — the topology goes.** This is the end of the phase and there is no continuity marker: [`just tofu labs destroy`](../../strands/lab-topologies.md#teardown), all three guests. Before you do, check the two things that outlive the cluster are safe — **the write-up is in `journal/`, and the two clones from [exercise 1](01-two-blobless-clones.md) are on [`forge`](../../strands/lab-topologies.md#build-guest)**, which is not part of any topology and survives the destroy. [P3](../../phases/03-api-machinery.md) opens the apiserver's storage layer down onto both.
