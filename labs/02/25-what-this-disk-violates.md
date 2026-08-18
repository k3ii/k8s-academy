<a id="what-this-disk-violates"></a>
# Predict which timing this hardware breaks, then break it

**Claim** — you can name, from the `hardware` and `performance` docs and **before measuring**, which of etcd's latency expectations a 35 W i5 with a contended disk violates; then produce the log lines that say so, and explain each one as a consequence of the `fsync` placement you established in [exercise 14](14-where-the-fsync-sits.md).

**Rests on** — [module 2.5's](../../phases/02-etcd.md#m2-5) `performance` + `hardware` reading question, and [exercise 13's](13-the-ready-advance-contract.md) step 6: the raft library counts **ticks**, not milliseconds. That is the mechanism behind everything below.

**Topology** — [`etcd-only`](../../strands/lab-topologies.md#etcd-only), all three healthy.

**Do**

1. **Predict, in writing, before touching anything.** From the docs, write down the recommended ceiling for WAL `fsync` p99 and for backend commit p99, and the rule the docs give for deriving `--heartbeat-interval` and `--election-timeout` from RTT. Then state which of the four numbers you expect `factory` to violate first under load, and which of them it satisfies comfortably.

2. Measure the baseline honestly. `endpoint status` will not tell you this; the histograms will:

   ```sh
   for n in 160 161 162; do
     echo "== $n"
     curl -s http://10.10.10.$n:2379/metrics | grep -E '^etcd_disk_wal_fsync_duration_seconds_bucket' | tail -8
   done
   ```

   Read the buckets rather than the mean: the cumulative counts tell you the tail, and the tail is what elections are decided by.

3. Also measure what the network under it is doing, since half the derivation depends on RTT:

   ```sh
   ping -c 20 10.10.10.161 | tail -3
   curl -s http://10.10.10.160:2379/metrics | grep -E '^etcd_network_peer_round_trip_time_seconds_bucket' | tail -6
   ```

4. Now make the disk the bottleneck, on the leader:

   ```sh
   ssh zain@10.10.10.160 'sudo dd if=/dev/zero of=/var/lib/load bs=1M count=4000 oflag=dsync' &
   ```

   While it runs, drive writes and watch the logs on all three:

   ```sh
   while true; do etcdctl put /slowdisk/k "$(date +%s%N)" > /dev/null || echo FAIL; done
   ssh zain@10.10.10.160 'journalctl -u etcd -f'
   ```

5. Collect the log lines. There are several distinct ones and they mean different things — capture each verbatim and pair it with its cause:

   - a line about applying entries taking too long;
   - a line about failing to send a heartbeat on time;
   - a line about a slow read-index or an overloaded server;
   - if you push hard enough, a leader change with nothing having failed.

6. Kill the load, remove the file, and let it settle:

   ```sh
   ssh zain@10.10.10.160 'sudo rm -f /var/lib/load'
   curl -s http://10.10.10.160:2379/metrics | grep -E '^etcd_server_leader_changes_seen_total'
   ```

7. Explain the election, if you got one, without using the word *slow*. The chain is: the process blocks in `fsync` → its tick loop does not run → the election timer is counted in ticks → a member that has not heard from the leader for `election-timeout` ticks starts a campaign → the leader was never gone. Say which of those steps is a design choice and which is a consequence.

**Observe** — WAL `fsync` p99 moves by an order of magnitude under `dd`, the log lines from step 5 appear in a predictable order, and `leader_changes_seen_total` may increment with every member healthy the entire time.

**Expect** — a disk-latency violation, not a network one. The `10.10.10.0/24` bridge between guests on one host has an RTT far below anything the derivation rule cares about, so the network side is comfortable; the `fsync` side is the one this hardware cannot hold under load. **That is the finding, and it is the reason this phase is worth a month on a 35 W box:** a cluster with plenty of CPU and RAM and a contended disk fails in exactly the way production etcd fails, and it fails as an *availability* problem that looks like a network problem.

The lesson to carry into every later phase: **"etcd is slow" is not a claim until it names a histogram.** Which one moved, at which quantile, compared to which recommended ceiling. [The `Debugging etcd` talk](../../strands/talks.md#etcd) is the companion here, and it is worth watching while step 4 is running rather than afterwards.

**Footprint note** — `dd` writes 4GB to `.160`'s 10G disk and it is removed in step 6. **Check it is gone**; a 4GB file left behind will make [the corruption drill](26-corrupt-a-member.md)'s recovery fail for a reason that has nothing to do with corruption. Nothing else is added, and no member is harmed — this drill only makes them slow.

**Write down** — the prediction from step 1 against what you measured, the four log lines with their causes, and the tick-versus-milliseconds sentence from step 7. That sentence is the one you will want when a real cluster starts electing and every member is up.

**Teardown** — `etcdctl del --prefix /slowdisk/`, confirm `/var/lib/load` is gone on `.160`, confirm `etcdctl endpoint health --cluster` is clean. **The topology stays.**
