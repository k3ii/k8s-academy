# Labs — Phase 2, etcd internals

Twenty-nine exercises in the order they are meant to run. Each states one claim to test or
one artifact to produce, links its [topology](../../strands/lab-topologies.md) rather than
restating a footprint, and ends with a teardown that does two things: **deletes what that
exercise created**, then says whether the topology stays or goes. Here it almost always
stays — one cluster runs the whole phase.

The framing — why each module exists, what to read and the question to answer from it —
stays in [`phases/02-etcd.md`](../../phases/02-etcd.md). These files hold only what you type
and what you should see.

| # | Exercise | Why it exists |
|---|---|---|
| 1 | [Two clones, and an entry point that resolves](01-two-blobless-clones.md) | The tree every citation for the next month is true against, plus the sha that makes it checkable. |
| 2 | [The release that moved `mvcc/` under `server/`](02-date-the-mvcc-move.md) | `git log --follow` across a rename, cross-checked from the other end so one technique is not one result. |
| 3 | [Raft is a second repository](03-prove-the-raft-extraction.md) | `--diff-filter=D` finds the commit that deleted a path — the only commit the current tree will never show you. |
| 4 | [Break one published citation, on purpose](04-refute-a-published-path.md) | The pickaxe, and the first time the required answer is a sha rather than a paragraph. |
| 5 | [Three members, wired together by hand](05-three-members-by-hand.md) | The flags the restore drill turns on, met three weeks early as "the flags that made it start". |
| 6 | [Predict which historical reads survive a compaction](06-ten-writes-and-a-compaction.md) | **[Gate condition 3](../../phases/02-etcd.md#gate).** The prediction is the exercise; the run only marks it. |
| 7 | [One raw bbolt key, decoded](07-decode-a-bbolt-key.md) | Where the bbolt key turns out to be the revision and the value carries the user key — the reverse of the usual assumption. |
| 8 | [The transaction that puts two revisions inside one](08-what-sub-is-for.md) | `sub` is invisible to the API, which is why the previous exercise had to reach for raw bytes. |
| 9 | [The index is in memory, and it is not free](09-what-a-read-consults-first.md) | Deleting keys does not return the memory. Compaction is the only thing that does. |
| 10 | [A stale read you caused on purpose](10-linearizable-versus-serializable.md) | **Closes the question [P1 deferred](../01/06-resourceversion-moves.md)** — and shows a wrong answer arriving with no error attached. |
| 11 | [One leader, three logs, and a handover you asked for](11-find-the-leader-and-move-it.md) | The gap between committed and applied, which every later module lives in. |
| 12 | [An election you did not ask for](12-kill-the-leader-read-the-term.md) | A failed write is not a write that did not happen — consistent is not exactly-once. |
| 13 | [What the library obliges its caller to do, in order](13-the-ready-advance-contract.md) | No disk, no network, no clock. The library counts ticks, and that is why slow clusters elect. |
| 14 | [The leader write path, with the `fsync` in the right place](14-where-the-fsync-sits.md) | Why a leader may send before it syncs and a follower may not — the sharpest thing in module 2.2. |
| 15 | [2.C5 — cut one member off the peer port](15-partition-one-member.md) | A member that is healthy, answering, and refusing to serve. The client-side network is the one segment that works. |
| 16 | [A watch that starts in the past](16-resume-a-watch-from-a-revision.md) | Nothing marks the boundary between replay and live — which is why informers list before they watch. |
| 17 | [Three sets a watcher can be in](17-synced-unsynced-victim.md) | Catching up is *slower per event* than being live, which is the opposite of most intuitions. |
| 18 | [Delete the history a watcher is still standing in](18-compact-under-a-live-watcher.md) | Two callers, two consequences, one error value — and the split this module was written to force. |
| 19 | [One compaction, four layers, and the relist at the top](19-the-chain-four-layers-up.md) | **[Gate condition 1](../../phases/02-etcd.md#gate).** The only exercise in the curriculum graded on recall. |
| 20 | [Compaction moves one number and not the other](20-compaction-frees-no-disk.md) | "We compacted and the disk is still full" is not a bug in any layer. |
| 21 | [Defrag returns the disk and stops the member](21-defrag-frees-disk-and-blocks.md) | One writer at a time means there is no incremental version of it. Never `--cluster`. |
| 22 | [History that disappears while you are not looking](22-auto-compaction-runs-without-you.md) | The configuration a real cluster ships with, and the reason `ErrCompacted` is usually nobody's fault. |
| 23 | [2.C4 — drive it into `NOSPACE` and get it back](23-fill-the-quota.md) | A delete is a write, so a delete is refused. The recovery has exactly one correct order. |
| 24 | [Three kinds of file, and which one you cannot lose](24-the-on-disk-trio.md) | A member that cannot be repaired is removed and re-added, not fixed. |
| 25 | [Predict which timing this hardware breaks](25-what-this-disk-violates.md) | **"etcd is slow" is not a claim until it names a histogram.** The 35 W box fails the way production does. |
| 26 | [2.C1 — write garbage into one page](26-corrupt-a-member.md) | The quiet corruption is the dangerous one: healthy, elected, and serving different answers. |
| 27 | [2.C2 — stop two of three](27-lose-quorum.md) | `--force-new-cluster` is not a repair; it is an operator stepping outside the protocol. |
| 28 | [2.C3 — put the cluster back, and count what you lost](28-restore-from-snapshot.md) | A restore is a rollback of the whole keyspace, with no error naming what went. |
| 29 | [The capstone — one sitting, two artifacts, four citations](29-the-capstone-writeup.md) | Graded as much on whether the `file:line` references survive checking as on whether the cluster came back. |

**One cluster runs exercises 5 through 29.**
[`etcd-only`](../../strands/lab-topologies.md#etcd-only) comes up at exercise 5 and is
destroyed at exercise 29, which ends the phase. It is **3.0GB of a
[9.5GB budget](../../strands/lab-topologies.md#ceiling)** and there is **no Kubernetes
anywhere in this phase** — no kubelet, no CNI, no controllers. That is the whole reason the
plan calls this the best depth-per-MB month in the curriculum, and it is why a phase this
long fits a 35 W homelab at all.

**Exercises 1–4 and 13 need no topology.** They run on
[`forge`](../../strands/lab-topologies.md#build-guest), which is up regardless, and the two
blobless clones they create live there for the whole phase and outlive the cluster — every
`file:line` in the capstone is a claim about a sha in one of them.

**The cluster is deliberately unencrypted**, which is [a stated deviation with its reasoning
in exercise 5](05-three-members-by-hand.md): everything here is one `--cacert/--cert/--key`
triple short of the command you would run against a kubeadm cluster's etcd.

Three exercises leave the store deliberately dirty for the next one —
[17](17-synced-unsynced-victim.md) keeps its keys for [20](20-compaction-frees-no-disk.md),
and [20](20-compaction-frees-no-disk.md) keeps its inflated `db` for
[21](21-defrag-frees-disk-and-blocks.md), because a compaction with nothing to compact
measures nothing. Their teardown lines say so; do not tidy past them.
