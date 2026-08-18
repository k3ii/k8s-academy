<a id="auto-compaction-runs-without-you"></a>
# History that disappears while you are not looking

**Claim** — with `--auto-compaction-mode` set, revisions become unreadable on a schedule you configured and then forgot, with no operator action and no log line most people read — so `ErrCompacted` in production is usually nobody's fault and everybody's surprise.

**Rests on** — [module 2.4's](../../phases/02-etcd.md#m2-4) `maintenance` doc question. Every previous compaction in this phase was one you typed. This is the one that runs on its own, and it is the configuration a Kubernetes cluster actually ships with.

**Topology** — [`etcd-only`](../../strands/lab-topologies.md#etcd-only). You will edit unit files and restart all three members, then put them back.

**Do**

1. Check what the members are running with now:

   ```sh
   etcdctl get / --prefix --keys-only | head -1     # anything, to have a baseline revision
   for n in 160 161 162; do ssh zain@10.10.10.$n 'grep -c auto-compaction /etc/systemd/system/etcd.service'; done
   ```

   Zero. Everything you have seen so far has been a store that keeps history until told otherwise.

2. Add periodic auto-compaction to all three units, with a window short enough to watch:

   ```
     --auto-compaction-mode periodic \
     --auto-compaction-retention 1m \
   ```

   Then, **one member at a time**, waiting for each to rejoin:

   ```sh
   ssh zain@10.10.10.160 'sudo systemctl daemon-reload && sudo systemctl restart etcd'
   etcdctl endpoint health --cluster
   ```

3. Make history and mark a spot:

   ```sh
   etcdctl put /auto/k v0
   OLD=$(etcdctl endpoint status -w json | python3 -c 'import sys,json; print(json.load(sys.stdin)[0]["Status"]["header"]["revision"])')
   for i in $(seq 1 200); do etcdctl put /auto/k "v$i" > /dev/null; done
   etcdctl get /auto/k --rev=$OLD        # works
   ```

4. Wait, doing nothing at all, and retry the same read every 30 seconds:

   ```sh
   while true; do date; etcdctl get /auto/k --rev=$OLD; sleep 30; done
   ```

5. When it fails, find the evidence that something happened:

   ```sh
   ssh zain@10.10.10.160 'journalctl -u etcd --since "-10 min" --no-pager | grep -i compact'
   curl -s http://10.10.10.160:2379/metrics | grep -E 'compact'
   ```

6. Now the mode that behaves differently. Switch to `--auto-compaction-mode revision --auto-compaction-retention 100`, restart, and answer without running it first: with a cluster taking 10 writes a second, how much history does each mode keep? One of these two is a *time* window and one is a *count* window, and on a busy cluster they are wildly different amounts of history.

7. Put the units back the way [exercise 5](05-three-members-by-hand.md) had them, restart one at a time, and confirm.

**Observe** — step 4's read succeeds for a while and then, with nothing typed in between, starts failing with the same `required revision has been compacted` from [exercise 6](06-ten-writes-and-a-compaction.md) and [exercise 18](18-compact-under-a-live-watcher.md).

**Expect** — a compaction with no operator behind it. The log line exists but is unremarkable, and the read failure arrives at a client that did nothing wrong. That is the shape of the incident: a controller reconnects, asks to resume from a revision it saw ninety seconds ago, and is told that revision is gone — [and four layers up that is a full relist](19-the-chain-four-layers-up.md).

Step 6's contrast is the operational lesson worth keeping. A time-based retention keeps *N minutes* of history regardless of load, so a write storm shortens nothing in wall-clock terms but produces enormously more revisions inside the window. A revision-based retention keeps *N revisions* regardless of time, so the same storm can collapse the window to seconds. **The mode that protects you against a slow consumer is not the same as the mode that protects you against a full disk**, and you have to say which problem you are configuring for.

**Footprint note** — nothing added; three restarts. Restarting members one at a time with a health check between is the same discipline [exercise 21](21-defrag-frees-disk-and-blocks.md) required for defrag, and for the same reason: two of three is a quorum, one of three is not.

**Write down** — the two modes, what each keeps, and which failure each defends against — one sentence per mode. Then the one number worth carrying: with retention `R` and a client that can be offline for `D`, what must be true of `R` and `D` for the client to resume without a relist?

**Teardown** — `etcdctl del --prefix /auto/`, and **confirm all three unit files no longer carry the auto-compaction flags** — an auto-compaction you forgot about will delete the history [exercise 23](23-fill-the-quota.md) is trying to accumulate and you will not connect the two. **The topology stays.**
