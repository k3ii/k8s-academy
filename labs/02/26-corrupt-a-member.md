<a id="corrupt-a-member"></a>
# 2.C1 — write garbage into one page and find out who notices

**Claim** — a member whose `db` has been corrupted mid-file **starts normally and serves reads**, and nothing detects it until something compares hashes across members; a member whose `db` has been corrupted in its first pages fails to open at all. Two corruptions, two entirely different failure shapes, and the dangerous one is the quiet one.

**Rests on** — [module 2.5's](../../phases/02-etcd.md#m2-5) `corrupt.go` and v3.5-postmortem reading question: what signal does `corrupt.go` compare across members, and what would a `dd` to one member's `db` do to it? Answer both before running this. This is [drill 2.C1](../../phases/02-etcd.md#chaos) and [manual drill 2](../../strands/chaos.md#manual-drills).

**Topology** — [`etcd-only`](../../strands/lab-topologies.md#etcd-only), three healthy members. `.162` is the victim; `.160` and `.161` carry the cluster.

**Setup**

Put something identifiable in the store and take the cluster's hashes while everything is honest:

```sh
for i in $(seq 1 500); do etcdctl put /corrupt/k$i "value-$i" > /dev/null; done
etcdctl endpoint hashkv --cluster -w table
```

All three hashes agree. That agreement is the signal; write down what it is a hash *of*, from `corrupt.go`, before you break it.

**Do**

1. Stop the victim and note its file size:

   ```sh
   ssh zain@10.10.10.162 'sudo systemctl stop etcd; ls -l /var/lib/etcd/member/snap/db'
   ```

2. **Corruption A — a page in the middle.** Pick an offset well inside the file, aligned to a page, and overwrite exactly one page:

   ```sh
   ssh zain@10.10.10.162 'sudo dd if=/dev/urandom of=/var/lib/etcd/member/snap/db \
     bs=4096 seek=200 count=1 conv=notrunc'
   ```

   `conv=notrunc` matters: without it you have truncated the file rather than corrupted it, which is a different and much more obvious fault.

3. Start it and watch what does **not** happen:

   ```sh
   ssh zain@10.10.10.162 'sudo systemctl start etcd'
   etcdctl endpoint health --cluster
   etcdctl endpoint status --cluster -w table
   ```

4. Now go looking for it:

   ```sh
   etcdctl endpoint hashkv --cluster -w table
   ssh zain@10.10.10.162 'journalctl -u etcd -n 60 --no-pager | grep -iE "corrupt|mismatch|hash|panic"'
   ```

5. Turn the detector on and restart the victim, so it checks itself at boot:

   ```sh
   ssh zain@10.10.10.162 'sudo etcd --help 2>&1 | grep -i corrupt'
   ```

   **Read that output rather than trusting any document, including this one.** [The chaos strand](../../strands/chaos.md#manual-drills) names the flag as `--experimental-initial-corrupt-check`; experimental flags graduate and get renamed, and which spelling this binary takes is a fact about the release you installed in [exercise 5](05-three-members-by-hand.md). This is [the archaeology standard](../../strands/source-archaeology.md#drills) applied to a flag instead of a path, and it is the cheapest possible instance of it.

   Add the flag the binary actually accepts to `.162`'s unit and restart.

6. **Corruption B — the first page.** Restore the member first via [the remove-and-re-add procedure](24-the-on-disk-trio.md), then corrupt page 0:

   ```sh
   ssh zain@10.10.10.162 'sudo systemctl stop etcd; sudo dd if=/dev/urandom of=/var/lib/etcd/member/snap/db bs=4096 seek=0 count=1 conv=notrunc; sudo systemctl start etcd'
   ssh zain@10.10.10.162 'journalctl -u etcd -n 30 --no-pager'
   ```

   Say why this one is caught immediately and the other was not, in terms of what bbolt reads first.

7. Recover: remove the member, wipe its data dir, add it back, start it with `--initial-cluster-state existing`, and confirm the hashes agree again.

**Observe** — after corruption A the member is `healthy`, its endpoint status is normal, and `hashkv` disagrees with the other two. After corruption B it does not start.

**Expect** — the quiet failure is the whole drill. A corrupted page in the middle of a B+tree damages whatever keys happen to live in it and nothing else; the member answers every other read correctly, participates in Raft, votes, and can be elected leader. **A cluster in that state is serving different answers depending on which member you reach**, which is precisely the class of bug the v3.5 postmortem is about, and it is why the detector exists as a periodic cross-member hash comparison rather than as a checksum on the read path.

**One correction to make explicitly, because [the phase file's drill table](../../phases/02-etcd.md#chaos) invites the wrong command:** `etcdctl check` is `check perf` and `check datascale` — a benchmark, not a corruption check. The corruption tooling is `etcdctl endpoint hashkv`, the corrupt-check flags from step 5, and the alarm `corrupt.go` raises. Note the distinction in your write-up; it is the kind of thing that costs an hour during an incident.

**Footprint note** — no resource cost. The remove-and-re-add in step 7 re-replicates the whole store to `.162`, which on a small store is seconds; had you done this drill before [exercise 23](23-fill-the-quota.md)'s teardown it would have been minutes, which is a real consideration on a real cluster and the reason recovery plans state a store size.

**Write down** — what `corrupt.go` compares and how often, the two failure shapes with what detected each, and the flag spelling your binary actually accepts. [The checklist](../../phases/02-etcd.md#checklist) asks for the corruption signal; the two-shapes contrast is what makes it memorable.

**Teardown** — `etcdctl del --prefix /corrupt/`, remove the corrupt-check flag from `.162`'s unit if you want all three identical again, confirm `hashkv --cluster` agrees on all three. **The topology stays** — [the quorum-loss drill](27-lose-quorum.md) needs all three healthy to start.
