<a id="where-the-fsync-sits"></a>
# The leader write path, with the `fsync` in the right place

**Artifact** — the leader write path written as an ordered sequence, with the WAL `fsync` placed relative to *sending messages to peers* and *applying committed entries*, citing the function in `etcdserver/raft.go` where it happens — and a measurement of that `fsync` from a running member to prove the sequence describes this cluster.

**Rests on** — [exercise 13](13-the-ready-advance-contract.md)'s ordering, which is the library's half. This is the server's half: the same contract, honoured by concrete code, with a disk under it. [Module 2.2's](../../phases/02-etcd.md#m2-2) `etcdserver/raft.go` reading question is exactly this, and `write_workflow_leader.png` is the one-picture check on your answer — **draw yours before you open the picture.**

**Topology** — [`etcd-only`](../../strands/lab-topologies.md#etcd-only) for the measurement; the reading is on `forge`.

**Do**

1. Find the loop:

   ```sh
   cd ~/src/etcd
   git grep -n 'func (r \*raftNode) start' -- server/etcdserver/raft.go
   ```

   Read it top to bottom once without stopping to look anything up. It is a `select` over channels, and the `case rd := <-r.Ready():` arm is the whole of this exercise.

2. Inside that arm, find and cite by `file:line`:

   - where entries and hard state are handed to the WAL;
   - where the `fsync` actually happens — which is **not** in this file, so follow the call:

     ```sh
     git grep -n 'func (w \*WAL) Save\|func (w \*WAL) sync' -- server/storage/wal/wal.go
     ```

   - where messages go to peers;
   - where committed entries are handed off to be applied.

3. Answer the question the code is arranged to answer: **is there a case where the leader sends before it syncs?** Look for a distinction between the leader and a follower in that arm, and for anything named after `MustSync`. State what the optimisation is, why it is safe for the leader specifically, and why it is not safe for a follower.

4. Now measure it. On a live member:

   ```sh
   curl -s http://10.10.10.160:2379/metrics | grep -E '^etcd_disk_wal_fsync_duration_seconds_(sum|count)'
   curl -s http://10.10.10.160:2379/metrics | grep -E '^etcd_disk_backend_commit_duration_seconds_(sum|count)'
   ```

   Take those four numbers, run a hundred writes, and take them again:

   ```sh
   for i in $(seq 1 100); do etcdctl put /fsync/k "$i" > /dev/null; done
   ```

   Compute the mean `fsync` over that window: the delta of `_sum` divided by the delta of `_count`.

5. Two histograms, two different things. Say which of the two you just measured is the Raft log write and which is the bbolt commit, and — from the counts, not the durations — say **why the two `_count` deltas are not equal for a hundred puts.**

6. Confirm the placement is causal rather than incidental. Make the disk slow and see which number moves:

   ```sh
   ssh zain@10.10.10.160 'sudo dd if=/dev/zero of=/var/lib/etcd/ballast bs=1M count=2000 oflag=dsync &'
   ```

   Re-run step 4 during it. Then `ssh zain@10.10.10.160 'sudo rm -f /var/lib/etcd/ballast'`.

**Expect** — the `fsync` sits **between** persisting the entries and applying them, and the leader is allowed to send to peers before it has synced its own copy, because a leader that crashes without its own entry simply has not committed it — a follower that acknowledges an entry it has not persisted, by contrast, has lied to the leader about a promise the leader will count towards a quorum. That asymmetry is the whole content of the optimisation and it is the sharpest thing in module 2.2.

Step 5's count difference is the other payoff: bbolt commits are **batched**, so a hundred puts do not produce a hundred backend commits, while the WAL sync count tracks the Raft batches. Two different batching regimes on two different files, and conflating them is why "etcd is slow" reports so often blame the wrong one.

Step 6 should move `wal_fsync` hard and `backend_commit` less, and if your `fsync` p99 goes past 10ms you have just met the number [module 2.5's](../../phases/02-etcd.md#m2-5) `hardware` doc warns about — on a 35 W i5, deliberately.

**Write down** — the ordered sequence with the `fsync` placed and each step carrying a `file:line`, plus your measured mean `fsync` and what it was during step 6. That sequence is [the checklist's](../../phases/02-etcd.md#checklist) *leader write path* artifact and one of [the capstone's](../../phases/02-etcd.md#capstone) required citations.

**Teardown** — `etcdctl del --prefix /fsync/`, and **confirm the ballast file is gone** — 2GB left in `/var/lib/etcd` on a 10G guest will fail [the quota drill](23-fill-the-quota.md) for the wrong reason. **The topology stays.**
