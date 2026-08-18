<a id="what-sub-is-for"></a>
# The transaction that puts two revisions inside one

**Claim** — a single etcd transaction writing two keys produces two bbolt revisions with the **same `main` and different `sub`**, and the client API never shows you the `sub` at all — which is why the previous exercise had to reach for the raw bytes.

**Rests on** — [exercise 7](07-decode-a-bbolt-key.md)'s decoding, and the second half of [module 2.1's](../../phases/02-etcd.md#m2-1) `revision.go` question: *why does `sub` exist at all — what has more than one revision inside a single transaction?* Write your answer first. This exercise is the demonstration of it.

**Topology** — [`etcd-only`](../../strands/lab-topologies.md#etcd-only).

**Do**

1. Write two keys in one transaction:

   ```sh
   etcdctl txn <<'TXN'

   put /sub/a one
   put /sub/b two

   TXN
   ```

   (The blank lines are the compare block and the else block, both empty.)

2. Ask the API what revision each got:

   ```sh
   etcdctl get --prefix /sub/ -w json | python3 -m json.tool | grep -E 'key|mod_revision|create_revision'
   ```

   Both keys report the *same* `mod_revision`. There is no field anywhere in that JSON that distinguishes them by write order within the transaction.

3. Now look underneath:

   ```sh
   etcdctl snapshot save /tmp/sub.db
   ~/etcd-dump-db iterate-bucket /tmp/sub.db key --decode | grep -A1 'sub/'
   ```

   Two rows, same `main`, different `sub`.

4. Find out what breaks without it. In the clone, read what the encoding does when `sub` is zero versus non-zero, and what a range over the bucket would return if both writes shared one key:

   ```sh
   (cd ~/src/etcd && git grep -n 'sub' -- server/storage/mvcc/revision.go)
   ```

   State the answer as a property of the B+tree, not of etcd: two entries with the same key in a B+tree are not two entries.

5. Push it. Do a five-key transaction and check that `sub` counts `0..4` in the order you wrote them, then check whether a *failed* compare branch consumes a revision at all:

   ```sh
   etcdctl txn <<'TXN'
   value("/sub/a") = "wrong"

   put /sub/never here

   TXN
   etcdctl get /sub/never
   etcdctl endpoint status -w table   # did the revision move?
   ```

**Expect** — same `main`, sequential `sub`, and nothing in the client API that exposes it. Step 5 is the interesting one: the failed transaction still moves the cluster revision even though it wrote nothing you asked for, because the revision counter tracks *the log*, not *your keys*. That is the first concrete instance of the rule [exercise 10](10-linearizable-versus-serializable.md) states properly and that [P1 told you to defer](../01/06-resourceversion-moves.md) — a revision number is a position, and the distance between two of them means nothing.

**Write down** — one sentence: what `sub` is for, phrased so it is a claim about the storage engine rather than about etcd. If your sentence does not mention that bbolt keys must be unique, it is not yet the answer.

**Teardown** — `rm /tmp/sub.db`, `etcdctl del --prefix /sub/`. **The topology stays.**
