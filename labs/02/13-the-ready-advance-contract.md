<a id="the-ready-advance-contract"></a>
# What the library obliges its caller to do, in order

**Claim** — you can state the strict ordering a caller must obey between receiving a `Ready` and calling `Advance()`, cite it by `file:line` in `etcd-io/raft`, and name what breaks if each step is done out of order. The library has **no disk, no network and no clock**; every one of those is the caller's obligation, and this exercise is the list.

**Rests on** — [module 2.2's](../../phases/02-etcd.md#m2-2) `raft/design.md` and `raft/doc.go` reading questions. Read at the version pinned in etcd's `go.mod` — the one you recorded in [exercise 3](03-prove-the-raft-extraction.md) — not at `main`, or your citations describe a library this cluster is not running.

**Topology** — none. This is [`forge`](../../strands/lab-topologies.md#build-guest) and the `~/src/raft` clone from [exercise 1](01-two-blobless-clones.md). It is deliberately placed between two live-cluster exercises: the contract is what makes [exercise 14](14-where-the-fsync-sits.md)'s measurements mean something.

**Do**

1. Check out the version the cluster is actually running:

   ```sh
   cd ~/src/etcd && grep 'go.etcd.io/raft' go.mod server/go.mod 2>/dev/null
   cd ~/src/raft && git checkout <that-version-tag>
   ```

2. Find the contract in prose and cite it:

   ```sh
   grep -n 'Ready' doc.go | head -40
   ```

   Extract the ordered list. There are four things a caller does with a `Ready` — write, send, apply, and one more that is easy to miss because it is not a verb the paper uses. Name all four and the order.

3. Find the type, so the prose has a struct behind it:

   ```sh
   git grep -n 'type Ready struct' -A 40
   ```

   For each field, say who consumes it: the disk, the network, the state machine, or the library itself on the next tick.

4. **Answer the ordering question three times, once per failure.** For each of these, say what a reader could observe afterwards:

   - messages sent **before** the entries and hard state are persisted;
   - `Advance()` called before the entries are persisted;
   - committed entries applied before the hard state is persisted.

   One of these three is the one that can lose a committed entry across a crash. Say which, and why the other two are merely wrong rather than unsafe.

5. Check whether the contract has an exception in the version you checked out. Search `doc.go` and the option struct for anything that permits the writes to happen asynchronously, and if there is one, say what the caller must do instead:

   ```sh
   grep -n -iE 'async|storage write|MustSync' doc.go raft.go node.go | head -20
   ```

6. Find where the "no clock" claim is enforced. The library does not sleep; something else drives it:

   ```sh
   git grep -n 'func (n \*node) Tick\|Tick()' -- '*.go' | head
   ```

   Then say what unit `--heartbeat-interval` is measured in from the library's point of view, and what that implies for a caller whose ticks are late — which is [module 2.5's](../../phases/02-etcd.md#m2-5) subject on a contended disk.

**Expect** — `doc.go` states the ordering explicitly and in one place, which is unusual enough to be worth noticing: this is a library whose correctness depends on its caller, so it documents the caller's obligations as normative text rather than as advice. The unsafe reordering is the one that lets a peer act on a promise the promiser has not written down.

Step 6's answer is the bridge to the rest of the phase. The library counts ticks, not milliseconds. If the process is stalled — in `fsync`, in GC, in a swapped page — the ticks are late, the election timeout expires in *fewer real milliseconds of health* than configured, and a cluster that is merely slow starts electing. That is the mechanism behind every "etcd is flapping" report, and you will produce it deliberately in [exercise 25](25-what-this-disk-violates.md).

**Write down** — the four-step ordering with a `file:line` for each claim, and the answer to step 4. This is half of [the checklist's](../../phases/02-etcd.md#checklist) *leader write path* item; [exercise 14](14-where-the-fsync-sits.md) is the other half, and it is the half that says where the `fsync` goes.

**Teardown** — `cd ~/src/raft && git checkout main` when you are done, or leave it on the tag and note that you did. Nothing else was created; no topology was involved.
