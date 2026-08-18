<a id="synced-unsynced-victim"></a>
# Three sets a watcher can be in, and how it moves between them

**Claim** — a watcher lives in the **synced** set, the **unsynced** set, or the victim list; you can name what puts it in each, cite the `watchable_store.go` functions that move it, and drive a live member into producing a watcher in each of the three states.

**Rests on** — [module 2.3's](../../phases/02-etcd.md#m2-3) `watcher_group.go`, `watcher.go` and `watchable_store.go` reading questions — the ⭐ of the module. Read `syncWatchers` before you run anything; this exercise is the demonstration of a path you should already be able to draw.

**Topology** — [`etcd-only`](../../strands/lab-topologies.md#etcd-only).

**Do**

1. Cite the three sets and the functions that move a watcher between them:

   ```sh
   cd ~/src/etcd
   git grep -n 'synced\|unsynced\|victim' -- server/storage/mvcc/watchable_store.go | head -40
   git grep -n 'func (s \*watchableStore) syncWatchers' -A 30 -- server/storage/mvcc/watchable_store.go
   ```

   Answer from the code, with `file:line`: what condition puts a new watcher in `unsynced` rather than `synced`? What does `syncWatchers` do on each pass, and how often is it called?

2. Find what the watcher group indexes and why it is an interval tree rather than a map:

   ```sh
   git grep -n 'func (wg \*watcherGroup)' -- server/storage/mvcc/watcher_group.go
   ```

   State the query it has to answer on every write: given one changed key, which watchers care? Then say why a map from key to watchers does not answer it.

3. Watch the gauges while you do the rest:

   ```sh
   while true; do
     curl -s http://10.10.10.160:2379/metrics \
       | grep -E '^etcd_debugging_mvcc_(watcher_total|slow_watcher_total|pending_events_total|watch_stream_total)'
     echo; sleep 2
   done
   ```

4. **Make a synced watcher.** Open a plain watch with no `--rev` and confirm `watcher_total` rises and `slow_watcher_total` does not.

5. **Make an unsynced watcher by construction.** Give it a large history to catch up on first:

   ```sh
   for b in $(seq 0 199); do
     { echo; for i in $(seq 0 99); do echo "put /sync/$b/$i x"; done; echo; } | etcdctl txn > /dev/null
   done
   etcdctl watch --prefix /sync/ --rev=1
   ```

   Watch the gauges during the catch-up. The watcher is in `unsynced` for as long as it takes `syncWatchers` to walk it forward, and the gauge says so.

6. **Make a slow watcher.** Open a watch whose reader never reads, so the stream's flow-control window closes and the server cannot hand events over:

   ```sh
   etcdctl watch --prefix /slow/ > /tmp/slow.out &
   sleep 1
   kill -STOP %1                       # the client is alive and not reading
   for i in $(seq 1 20000); do etcdctl put /slow/$i x > /dev/null; done
   ```

   Watch `slow_watcher_total` and `pending_events_total`.

7. Let it go and see whether it recovers:

   ```sh
   kill -CONT %1
   ```

**Observe** — three distinct gauge signatures. A synced watcher moves `watcher_total` only. Catch-up moves it and leaves `slow_watcher_total` at zero or briefly non-zero. A blocked reader moves `slow_watcher_total` and pushes `pending_events_total` up and up.

**Expect** — the sets are not states a watcher chooses; they are where the server has put it based on whether it is keeping up. A watcher in `unsynced` is being fed from the store by a periodic sweep rather than from the write path directly, which is why catching up is *slower per event* than being live — the opposite of most people's intuition, and the reason a client that reconnects during a storm can take a long time to get current.

The victim list is the state you cannot reach by being merely behind: it is where a watcher goes when the server has given up trying to deliver to it in the normal path. Step 6 pushes toward it; [the next exercise](18-compact-under-a-live-watcher.md) is what happens when the history it still needs is deleted underneath it.

**Footprint note** — step 5 writes 20,000 keys and step 6 writes 20,000 more on a 1024MB guest. That is fine for RAM and it inflates the `db` file, which is wanted: [exercise 20](20-compaction-frees-no-disk.md) needs a store with something in it, so **leave these keys in place** and do not compact yet.

**Write down** — the path *synced → unsynced → victim → `ErrCompacted`* with the function name from `watchable_store.go` at each arrow. That is [the checklist's](../../phases/02-etcd.md#checklist) slow-watcher artifact and half of [gate condition 1](../../phases/02-etcd.md#gate); [exercise 19](19-the-chain-four-layers-up.md) supplies the other half.

**Teardown** — `kill %1; rm -f /tmp/slow.out`, and `etcdctl del --prefix /slow/`. **Keep `/sync/`** — [exercise 20](20-compaction-frees-no-disk.md) wants the bytes. **The topology stays.**
