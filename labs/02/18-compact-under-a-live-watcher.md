<a id="compact-under-a-live-watcher"></a>
# Delete the history a watcher is still standing in

**Claim** — compacting past the revision a watcher still needs **terminates that watcher's stream with `ErrCompacted`**, while a watcher that is already caught up is untouched by the same compaction. The error is the same name as [exercise 6's](06-ten-writes-and-a-compaction.md) failed `--rev` read and it is a completely different event, and telling them apart is [the ticket that splits this module](../../phases/02-etcd.md#m2-3).

**Rests on** — [exercise 17](17-synced-unsynced-victim.md)'s three sets. The prediction to make first: of the two watchers you are about to open, say which dies and why, in terms of which set each is in.

**Topology** — [`etcd-only`](../../strands/lab-topologies.md#etcd-only).

**Setup**

```sh
etcdctl put /evict/anchor 0
A=$(etcdctl get /evict/anchor -w json | python3 -c 'import sys,json; print(json.load(sys.stdin)["header"]["revision"])')
for i in $(seq 1 2000); do etcdctl put /evict/k "$i" > /dev/null; done
N=$(etcdctl endpoint status -w json | python3 -c 'import sys,json; print(json.load(sys.stdin)[0]["Status"]["header"]["revision"])')
echo "old=$A now=$N"
```

**Do**

1. Open **two** watches, in two terminals, on the same prefix:

   ```sh
   etcdctl watch --prefix /evict/ --rev=$A        # terminal 1: behind
   etcdctl watch --prefix /evict/                 # terminal 2: current
   ```

   Terminal 1 will spend a while replaying. Do not wait for it to finish — that is the point.

2. In a third terminal, compact past the first watcher's position:

   ```sh
   etcdctl compact $((N - 10))
   ```

3. Read both terminals. One of them ends; one does not. Capture the exact text of the one that ends, character for character, and the exit status of `etcdctl`.

4. Repeat step 1's terminal 1 — try to *open* a watch from the now-compacted revision:

   ```sh
   etcdctl watch --prefix /evict/ --rev=$A
   ```

   Compare its failure to the failure in step 3: one is a stream that was torn down mid-flight, one is a request refused at open. The error string may be identical; the situations are not.

5. Confirm the boundary. Find the lowest revision that still opens a watch successfully, and check it against the revision you compacted to:

   ```sh
   for r in $((N-12)) $((N-11)) $((N-10)) $((N-9)); do
     echo -n "$r: "; timeout 2 etcdctl watch --prefix /evict/ --rev=$r 2>&1 | head -1
   done
   ```

6. Cite the site:

   ```sh
   (cd ~/src/etcd && git grep -n 'ErrCompacted' -- server/storage/mvcc/watchable_store.go server/storage/mvcc/kvstore.go)
   ```

**Observe** — terminal 2 keeps delivering events after the compaction and never notices it happened. Terminal 1 stops.

**Expect** — the current watcher survives because it needs no history: it is fed from the write path as writes happen, and compaction removes only the past. The behind watcher dies because the revisions it was still walking towards no longer exist, and there is nothing the server can do that is both honest and non-fatal — it cannot skip the missing events, because a client that silently misses events is worse than a client that is told to start over.

**That last sentence is the whole design, and it is why the Kubernetes translation is a *relist* and not a warning.** A watch that has lost history cannot be repaired; it can only be replaced by a fresh full read plus a fresh watch. [Exercise 19](19-the-chain-four-layers-up.md) is that sentence written out across four layers.

Step 5's boundary should be the compaction revision itself, matching [exercise 6](06-ten-writes-and-a-compaction.md)'s finding on `--rev` reads — one mechanism, two surfaces.

**Write down** — the exact error text from step 3, and one sentence distinguishing *the watcher eviction* from *the failed historical read*, both named `ErrCompacted`. Two different callers, two different consequences, one error value.

**Teardown** — `etcdctl del --prefix /evict/`, and stop any watch still running. **The topology stays.**
