<a id="decode-a-bbolt-key"></a>
# One raw bbolt key, decoded back to `revision{main, sub}`

**Artifact** — a byte string copied out of a `tools/etcd-dump-db` dump, and its decoding into a `main` and a `sub`, with the line of `revision.go` that defines the layout cited by `file:line`.

**Rests on** — [module 2.1's](../../phases/02-etcd.md#m2-1) `revision.go` reading question: how `main` and `sub` are packed into the bbolt key bytes. **[The checklist](../../phases/02-etcd.md#checklist) asks for this as a timed item** — point at one key's revisions as raw bytes and decode one — so the aim here is to do it once slowly enough that you can do it later quickly.

**Topology** — [`etcd-only`](../../strands/lab-topologies.md#etcd-only). `etcd-dump-db` was built and copied to `.160` in [exercise 5](05-three-members-by-hand.md).

**Setup**

Write a key whose revisions you can find, and give it a value long enough to spot by eye:

```sh
etcdctl put /decode/me AAAAAAAAAAAA
etcdctl put /decode/me BBBBBBBBBBBB
etcdctl put /decode/me CCCCCCCCCCCC
etcdctl get /decode/me -w json | python3 -m json.tool   # note mod_revision
```

Take a consistent copy of the database. **Do not dump the live file** — bbolt is being written under you and a torn read produces bytes that decode to nonsense you will spend an hour on:

```sh
etcdctl snapshot save /tmp/dump.db
```

**Do**

1. See what is in the file at all:

   ```sh
   ~/etcd-dump-db list-bucket /tmp/dump.db
   ```

   Note how few buckets there are, and that one of them holds everything you think of as "the data".

2. Iterate the key bucket and find your writes:

   ```sh
   ~/etcd-dump-db iterate-bucket /tmp/dump.db key --decode | grep -n 'AAAA\|BBBB\|CCCC'
   ```

   Then run it again **without** `--decode` and find the same rows. The decoded form is the tool doing for you exactly what this exercise asks you to do by hand; the undecoded form is the artifact.

3. Take one raw key from the undecoded output — 17 or 18 bytes — and split it by hand. Read `revision.go` for the layout rather than guessing from the shape:

   ```sh
   (cd ~/src/etcd && git grep -n 'func revToBytes\|func bytesToRev' -- server/storage/mvcc/revision.go)
   ```

   Then follow the function bodies: which slice indices carry `main`, which carry `sub`, what byte order, and what the trailing byte is when it is present.

4. Decode it arithmetically and check yourself against `mod_revision` from the setup:

   ```sh
   python3 -c 'import struct,binascii; b=binascii.unhexlify("<your hex>"); print(struct.unpack(">q", b[0:8])[0], struct.unpack(">q", b[9:17])[0])'
   ```

5. Answer the question the layout is designed to answer: given that the bucket is a B+tree ordered by these byte strings, **what does big-endian buy that little-endian would lose?** Say it in terms of what a range scan over revisions costs.

**Expect** — the raw key is `main` and `sub` as fixed-width big-endian integers with a separator byte between them, and a trailing marker on tombstones. Your decoded `main` equals the `mod_revision` `etcdctl` reported, which is the check that you split it in the right place. `sub` is `0` for all three of these writes, and [the next exercise](08-what-sub-is-for.md) exists because that is not always true.

The value bytes next to the key are a protobuf-encoded `mvccpb.KeyValue`, not your string — your `CCCC` is *inside* it, with the key name and the three revision fields around it. That is worth seeing once: the bbolt key is the revision and the bbolt value carries the user key, which is the reverse of the arrangement most people assume.

**Write down** — the hex, the two integers, and the `revision.go` `file:line` for the encoding. That citation is one of the four [the capstone](../../phases/02-etcd.md#capstone) requires, and it is the easiest of them to get right, so get it right now.

**Teardown** — `rm /tmp/dump.db`, `etcdctl del /decode/me`. **The topology stays.**
