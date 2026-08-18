<a id="kill-the-leader-read-the-term"></a>
# An election you did not ask for

**Claim** — killing the leader costs one election, the term increases by at least one, writes fail for the duration and then resume, and **no committed write is lost** — which is the safety rule from Figure 2, observed rather than read.

**Rests on** — [exercise 11](11-find-the-leader-and-move-it.md), and the Figure 2 answer you wrote there. The contrast between the two exercises is the exercise: `move-leader` is a handover with no gap; this is a failure with one.

**Topology** — [`etcd-only`](../../strands/lab-topologies.md#etcd-only).

**Setup**

Instrument the gap before you cause it. In one terminal on `.160`, run a writer that records what it believes it wrote:

```sh
i=0; while true; do
  i=$((i+1))
  if etcdctl put "/elect/$i" "$i" >/dev/null 2>&1; then echo "$i ok"; else echo "$i FAIL"; fi
  sleep 0.1
done | tee /tmp/writes.log
```

In another, `while true; do etcdctl endpoint status --cluster -w table | grep -E 'true|false'; sleep 0.5; done`.

**Do**

1. Note the current leader and its term. Then kill it hard — not a graceful stop, which would hand leadership over the way [exercise 11](11-find-the-leader-and-move-it.md) did:

   ```sh
   ssh zain@10.10.10.16X 'sudo systemctl kill -s SIGKILL etcd'
   ```

2. Watch the second terminal. Time how long until a new `true` appears in the `IS LEADER` column, and read the new term.

3. Read the election from the logs of a *surviving* member:

   ```sh
   ssh zain@10.10.10.16Y 'journalctl -u etcd -n 60 --no-pager | grep -iE "elect|term|vote|leader"'
   ```

   Find the line where it became a candidate, the line where it counted votes, and the line where it became leader. Match them to Figure 2's `RequestVote` rules.

4. Bring the dead member back and watch it catch up:

   ```sh
   ssh zain@10.10.10.16X 'sudo systemctl start etcd'
   etcdctl endpoint status --cluster -w table
   ```

5. **Audit the writer.** Stop it, then check every write it believed succeeded:

   ```sh
   grep ' ok$' /tmp/writes.log | wc -l
   etcdctl get --prefix /elect/ --keys-only | grep -c elect
   grep FAIL /tmp/writes.log | head
   ```

6. Now the case that matters more than the happy path. Look at the *last* `ok` before the first `FAIL` and the *first* `ok` after the last one, and check both keys are present. Then consider a `FAIL` line: is that write absent, present, or is it unknowable from the client's side alone?

**Observe** — the term goes up; the leader changes; `etcdctl put` fails for a window of a few seconds; the restarted member rejoins in the *new* term without an election of its own.

**Expect** — every write the client saw succeed is present. That is the guarantee, and it is the one thing worth being certain of. Writes during the gap fail with a context deadline or `no leader`.

The subtle answer is step 6's last question: **a failed write is not a write that did not happen.** A `put` that timed out may have been committed by the leader and lost only the response, which is why every client that matters — including the apiserver — is written to retry idempotently and why `resourceVersion` exists as a concurrency token at all. Check whether any `FAIL` key is present in the store. If one is, you have just demonstrated at-least-once delivery on a system that markets consistency, and the distinction between *consistent* and *exactly-once* is worth writing down in your own words.

**Footprint note** — a SIGKILLed member restarts by replaying its WAL. With the store small this is instant; after [exercise 9](09-what-a-read-consults-first.md) taught you what a large store costs at startup, do this drill on a *small* store, or budget the wait.

**Write down** — the term before and after, the write-failure window in seconds, and the answer to step 6. The failure window is a number [module 2.5](../../phases/02-etcd.md#m2-5) revisits: it is roughly the election timeout, and the election timeout is derived from RTT in the `hardware` doc.

**Teardown** — `etcdctl del --prefix /elect/`, `rm /tmp/writes.log`, and confirm all three members are back with `etcdctl endpoint health --cluster`. **The topology stays.**
