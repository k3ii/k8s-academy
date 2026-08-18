<a id="the-on-disk-trio"></a>
# Three kinds of file, and which one you cannot lose

**Claim** — of the WAL segments, the Raft snapshot files and the bbolt `db`, exactly one cannot be rebuilt from the others; you can say which before testing, and then delete each in turn on a member and be right about what happens.

**Rests on** — [module 2.5's](../../phases/02-etcd.md#m2-5) `persistent-storage-files` reading question: what is each file *for*, and which can be rebuilt from the others? **Predict all three outcomes before step 3.** A member that fails to start is not a surprise here; being wrong about which one fails is the finding.

**Topology** — [`etcd-only`](../../strands/lab-topologies.md#etcd-only). All destruction happens on `.162`, and the other two carry the cluster throughout — this is the first exercise in the phase that relies on that, and every remaining one does.

**Do**

1. Look at what is actually there, and at the sizes:

   ```sh
   ssh zain@10.10.10.162 'find /var/lib/etcd -type f -printf "%10s  %p\n" | sort -k2'
   ```

   Note which directory holds which, how many WAL segments there are, whether any `.snap` files exist at all, and that the segments are pre-allocated to a fixed size — a WAL segment's size tells you nothing about how much is in it.

2. Take a safety copy so the exercise is repeatable, then stop the member:

   ```sh
   ssh zain@10.10.10.162 'sudo systemctl stop etcd && sudo cp -a /var/lib/etcd /var/lib/etcd.bak'
   ```

3. **Delete the `db` and start it.** Predict first: does it come back, and if so from what?

   ```sh
   ssh zain@10.10.10.162 'sudo rm -f /var/lib/etcd/member/snap/db && sudo systemctl start etcd'
   ssh zain@10.10.10.162 'journalctl -u etcd -n 40 --no-pager'
   etcdctl endpoint status --cluster -w table
   ```

4. Restore from the copy, stop it again, and **delete the WAL directory**. Predict first:

   ```sh
   ssh zain@10.10.10.162 'sudo systemctl stop etcd && sudo rm -rf /var/lib/etcd && sudo cp -a /var/lib/etcd.bak /var/lib/etcd'
   ssh zain@10.10.10.162 'sudo rm -rf /var/lib/etcd/member/wal && sudo systemctl start etcd'
   ssh zain@10.10.10.162 'journalctl -u etcd -n 40 --no-pager'
   ```

5. Whatever happened in step 4, the fix is the same and it is a procedure worth having: **remove the member and add it back**, which is not the same as restarting it.

   ```sh
   etcdctl member list -w table
   etcdctl member remove <the-.162-member-id>
   etcdctl member add m3 --peer-urls=http://10.10.10.162:2380
   ```

   Read what `member add` prints. It gives you an `--initial-cluster` and an `--initial-cluster-state`, and the second one is **not** what [exercise 5](05-three-members-by-hand.md)'s unit file says. Change the unit, wipe the data dir, start it:

   ```sh
   ssh zain@10.10.10.162 'sudo rm -rf /var/lib/etcd/* && sudo systemctl daemon-reload && sudo systemctl start etcd'
   etcdctl endpoint status --cluster -w table
   ```

6. Say why the two states exist. `new` versus `existing` is one word in one flag and it decides whether the member tries to *bootstrap a cluster* or *join one*. Name what goes wrong if a member that should join instead bootstraps — this is the failure [the restore drill](28-restore-from-snapshot.md) is built to avoid, and it is the reason a restore uses a fresh `--initial-cluster-token`.

**Observe** — one of steps 3 and 4 comes back on its own; the other does not.

**Expect** — the WAL is the record of what was agreed and it is the only file with no other source. The `db` is derived state: it is the log applied, and it can be reconstructed by replaying. The `.snap` files are an optimisation on that replay — they exist so the WAL can be truncated, and their absence costs time, not correctness.

**The caveat is the interesting part and you should check it rather than take it from here:** the `db` is only rebuildable from the WAL if the WAL still reaches back far enough. Once a snapshot has been taken and old segments removed, the derivation is `snapshot + remaining WAL`, not `WAL` alone — so on a member that has been running long enough, deleting both the `db` and the `.snap` files is unrecoverable even though neither is individually so. Look at what step 1 found on your member and say which regime you are in before you trust step 3's result.

Step 5 is the procedure that makes all of this survivable and it should be unremarkable by the end: **a member that cannot be repaired is removed and re-added, not fixed.** Its data is in the other two.

**Footprint note** — `cp -a /var/lib/etcd` doubles that member's data directory on a 10G guest. With the store small after [exercise 23](23-fill-the-quota.md)'s teardown this is nothing; if you skipped that teardown, do it now rather than here.

**Write down** — the three files, what each is for in one clause, and which is irreducible. Then the `new` versus `existing` sentence from step 6 — [the restore drill](28-restore-from-snapshot.md) assumes it.

**Teardown** — `ssh zain@10.10.10.162 'sudo rm -rf /var/lib/etcd.bak'`, and **put the unit file back to `--initial-cluster-state new`** so it matches the other two and so a future restart is not carrying a flag that was true for one afternoon. Confirm three healthy members. **The topology stays.**
