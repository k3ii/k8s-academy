# Phase 2 — etcd internals

> **4–5 weeks.** The brief singled this phase out as worth a month, and [the capacity plan](https://github.com/k3ii/k8s-academy/issues/8) calls it the best depth-per-MB in the curriculum — it needs **no Kubernetes at all**, so a 35 W homelab can run the real thing and watch it degrade honestly.
> The range is planning information. **The gate at the bottom decides when the phase is finished.**

| | |
|---|---|
| **Prerequisites** | [P1](01-operate-shallow.md) — you watched `resourceVersion` move on an object and were told *why* was deferred to here. This is here. The [Go primer](01-operate-shallow.md) shipped in P1's last module because **this is the first phase that opens Go source in anger.** |
| **Unlocks** | [P3](03-api-machinery.md) reads the apiserver's storage layer *down onto* this — the encode/decode, the `cacher`, the storage `Interface`. [P4](04-controllers.md)'s informer is the other end of the watch you trace here. And the `"too old resource version"` every operator eventually hits gets its true name — `ErrCompacted` — in module 2.3. |
| **Source area** | [Area 1 — etcd](../strands/source-reading.md#area-1-etcd), entry point `server/storage/mvcc/key_index.go`. Two repos now, not one — the Raft library was [extracted to `etcd-io/raft`](../strands/source-archaeology.md#stale-paths). |
| **Language** | Go, read not written. **The source-archaeology method lands here** ([module 2.0](#m2-0)) because this is the first real source phase — verifying a cited path against the live tree becomes a taught, graded skill from now on. |
| **Strands** | [source reading](../strands/source-reading.md#area-1-etcd) · [source archaeology](../strands/source-archaeology.md#method) · [talks](../strands/talks.md#etcd) · [chaos](../strands/chaos.md#cannot-express) |

---

<a id="objectives"></a>
## 1. Objectives

Every one is falsifiable — an artifact, a timed production, or a claim a hostile reader could check against source or a running cluster. *understand* and *know* appear nowhere.

By the end you can:

1. **Predict compaction's effect from `key_index.go`.** Given a key written *N* times then compacted at revision *r*, say from the generations structure which `Range --rev=k` calls still return and which now give `ErrCompacted` — then show it against a live member.
2. **Decode a raw bbolt key** back to its `revision{main, sub}` using the byte layout in `revision.go`, from a `tools/etcd-dump-db` dump.
3. **Close the P1 question.** State what `resourceVersion` upstream *is* (an etcd revision), and from `api_guarantees.md` exactly what linearizable-vs-serializable reads do and do not promise a client — the thing [P1](01-operate-shallow.md) told you to defer.
4. **Draw the leader write path** and name where the **WAL `fsync` sits relative to apply**, from `raft/doc.go`'s ordering rules and `etcdserver/raft.go`'s `Ready()`/`Advance()` loop — not from the paper alone, which has no disk.
5. **Trace a slow watcher** from the synced set → unsynced → the victim list → `ErrCompacted` in `watchable_store.go`, and name it as the direct upstream cause of the apiserver's `"too old resource version"`.
6. **Separate the two space problems:** show that compaction frees *revisions but not disk*, and defrag frees *disk but blocks writes* — each with a before/after measurement whose **curve shape you can defend** (magnitude on this disk is meaningless).
7. **Recover from quorum loss and from a corrupted member**, naming every step's *ordering* and why it is ordered so — the procedure is the skill, not the commands.
8. **Verify or refute any etcd path** cited in a pre-2023 article against the current tree, answering with a `file:line` or a commit sha a hostile reader could check.

---

<a id="modules"></a>
## 2. Modules

Reading is [Area 1](../strands/source-reading.md#area-1-etcd), sequenced approachable → hard and interleaved with labs that give each file something to point at. **No fact from the strand is restated here** — each item below carries only a *question to answer from the source*, which is the phase-specific part.

<a id="m2-0"></a>
### Module 2.0 — Source archaeology, the method (~first week, runs alongside 2.1)

This is where the curriculum stops trusting citations. Every later phase inherits the standard set here: a path is not real until you have seen it in the tree you are actually reading.

**Read** — [the method](../strands/source-archaeology.md#method) (five techniques) and [the seven known moves](../strands/source-archaeology.md#stale-paths). **Two of those seven are yours this phase:** etcd `mvcc/` → `server/storage/mvcc/`, and the Raft library extracted out of `etcd-io/etcd` into its own `etcd-io/raft` repo.

**Labs** — [Two clones, and an entry point that resolves](../labs/02/01-two-blobless-clones.md) · [The release that moved `mvcc/` under `server/`](../labs/02/02-date-the-mvcc-move.md) · [Raft is a second repository](../labs/02/03-prove-the-raft-extraction.md) · [Break one published citation, on purpose](../labs/02/04-refute-a-published-path.md)

**No cluster of its own.** All four run on [`forge`](../strands/lab-topologies.md#build-guest) against two blobless clones, which is why this module can occupy the first week while [2.1](#m2-1) is bringing a cluster up.

> **Standard, inherited by every later phase:** a drill is passed when its answer is a `file:line` or a commit sha a hostile reader could check and find wrong — [the build track's tier-2 bar](../strands/source-archaeology.md#drills).

<a id="m2-1"></a>
### Module 2.1 — MVCC and revisions (~1 week)

The entry point, and the module that makes `resourceVersion` stop being magic.

**Read** — [Area 1](../strands/source-reading.md#area-1-etcd), with a question to answer from each:

| Item | Answer from it |
|---|---|
| `key_index.go` (item 4, ⭐) | What does a *generation* contain, and what exactly does `compact(rev)` remove from a keyIndex versus leave behind? |
| `revision.go` (item 5) | How are `main` and `sub` packed into the bbolt key bytes — and why does `sub` exist at all (what has more than one revision inside a single transaction)? |
| `data_model` + `api_guarantees` docs (items 1, 3) | From `api_guarantees`: what is a client **forbidden** from inferring from a revision number? This is the upstream root of the `resourceVersion` opacity rule you met in [P1](01-operate-shallow.md). |
| `index.go` (item 9) | The in-memory B-tree over keyIndexes — what does a read consult *before* it ever touches bbolt? |

**Labs** — [Three members, wired together by hand](../labs/02/05-three-members-by-hand.md) · [Predict which historical reads survive a compaction](../labs/02/06-ten-writes-and-a-compaction.md) · [One raw bbolt key, decoded](../labs/02/07-decode-a-bbolt-key.md) · [The transaction that puts two revisions inside one](../labs/02/08-what-sub-is-for.md) · [The index is in memory, and it is not free](../labs/02/09-what-a-read-consults-first.md) · [A stale read you caused on purpose](../labs/02/10-linearizable-versus-serializable.md)

`ErrCompacted` is met here for the first time, as a failed historical read. Its name reappears in [module 2.3](#m2-3) as the *watcher* failure and in [P3](03-api-machinery.md) as the apiserver relist trigger — three surfaces, one error value.

<a id="m2-2"></a>
### Module 2.2 — Raft, the library versus the server (~1 week)

Consensus, read as the two-layer thing it actually is: an algorithm (the paper) and a *state machine with no disk, network, or clock* (the library).

**Read**

| Item | Answer from it |
|---|---|
| Raft paper, Figure 2 (item 6) | Non-negotiable first. What are the three sub-problems, and which single rule makes a committed entry safe forever? |
| `raft/design.md` + `raft/doc.go` (items 7, 8) | The library is a state machine, not a server. What are you — the caller — obligated to do with a `Ready`, and in what **strict order** must you persist entries, hard state, and snapshot before you `Advance()`? |
| `etcdserver/raft.go` (item 18) | The server side of that contract: where in `raftNode.start()` does the **WAL `fsync`** happen relative to sending messages and applying committed entries? |
| `write_workflow_leader.png` (item 24) | The one-picture check on your mental model of the above. |

**Labs** — [One leader, three logs, and a handover you asked for](../labs/02/11-find-the-leader-and-move-it.md) · [An election you did not ask for](../labs/02/12-kill-the-leader-read-the-term.md) · [What the library obliges its caller to do, in order](../labs/02/13-the-ready-advance-contract.md) · [The leader write path, with the `fsync` in the right place](../labs/02/14-where-the-fsync-sits.md) · [2.C5 — cut one member off the peer port](../labs/02/15-partition-one-member.md)

<a id="m2-3"></a>
### Module 2.3 — Watch (~4–5 days)

The mechanism the entire Kubernetes control plane is a client of. This is the module [P4](04-controllers.md) picks up from the other side.

**Read**

| Item | Answer from it |
|---|---|
| `watcher_group.go` + `watcher.go` (item 10) | What distinguishes the **synced** from the **unsynced** watcher set, and what is the interval tree indexing? |
| `watchable_store.go` (item 11, ⭐ of this module) | Follow `syncWatchers` and the **victim list**: what happens to a watcher too slow to keep up, and what error does it ultimately receive? |
| `api` doc (item 2) | The `Watch` gRPC surface with `WithRev` — how does a client *resume* a watch, and what does it pass? |

**Labs** — [A watch that starts in the past](../labs/02/16-resume-a-watch-from-a-revision.md) · [Three sets a watcher can be in](../labs/02/17-synced-unsynced-victim.md) · [Delete the history a watcher is still standing in](../labs/02/18-compact-under-a-live-watcher.md) · [One compaction, four layers, and the relist at the top](../labs/02/19-the-chain-four-layers-up.md)

The single causal chain — etcd compaction → watcher eviction → apiserver 410 → client-go relist — is the spine of this module, a load-bearing fact for [P4](04-controllers.md), and [gate condition 1](#gate). The last of the four labs is the only exercise in the curriculum graded on recall.

<a id="m2-4"></a>
### Module 2.4 — Compaction, defrag, and bbolt (~4–5 days)

The two space problems operators conflate, separated for good.

**Read**

| Item | Answer from it |
|---|---|
| `kvstore_compaction.go` + `kvstore.go` (item 12) | Compaction is a **batched bbolt delete loop**. Why does deleting revisions free *logical* space but return **no disk to the filesystem**? |
| `backend.go` + `batch_tx.go` (item 16) | The bbolt layer — batch transactions and commit intervals. Where does `Defrag()` actually run, and why must it **block**? |
| `maintenance` doc (item 13) | Auto-compaction modes, the space quota, and the `NOSPACE` alarm. What state is the cluster in once the alarm fires? |

**Labs** — [Compaction moves one number and not the other](../labs/02/20-compaction-frees-no-disk.md) · [Defrag returns the disk and stops the member](../labs/02/21-defrag-frees-disk-and-blocks.md) · [History that disappears while you are not looking](../labs/02/22-auto-compaction-runs-without-you.md) · [2.C4 — drive it into `NOSPACE` and get it back](../labs/02/23-fill-the-quota.md)

The before/after pair from the first two is [the capstone's](#capstone) core measurement. **Read the shape, not the magnitude** — absolute bytes on this disk mean nothing, and claiming them is the stated failure.

<a id="m2-5"></a>
### Module 2.5 — Failure, corruption, and recovery (~1 week)

Where the phase's chaos lives. On-disk reality first, then break it and put it back.

**Read**

| Item | Answer from it |
|---|---|
| `persistent-storage-files` doc (item 17) | The on-disk trio — WAL segments, snapshot files, `db`. What is each *for*, and which one can be rebuilt from the others? |
| `performance` + `hardware` docs (item 15) | `fsync` latency and the `--heartbeat-interval`/`--election-timeout` derivation from RTT. **`factory` is a 35 W i5 with contended disk** — predict which of these etcd will violate, and be able to explain the resulting log lines. |
| v3.5 data-inconsistency postmortem (item 19) + `corrupt.go` (item 20) | A real correctness bug root-caused in public, and the corruption detector it produced. What signal does `corrupt.go` compare across members, and what would a `dd` to one member's `db` do to it? |

**Labs** — [Three kinds of file, and which one you cannot lose](../labs/02/24-the-on-disk-trio.md) · [Predict which timing this hardware breaks](../labs/02/25-what-this-disk-violates.md) · [2.C1 — write garbage into one page](../labs/02/26-corrupt-a-member.md) · [2.C2 — stop two of three](../labs/02/27-lose-quorum.md) · [2.C3 — put the cluster back, and count what you lost](../labs/02/28-restore-from-snapshot.md)

Every drill in this module *is* a Break-it; that is the shape of the phase's chaos, which is why it stays [manual](../strands/chaos.md#manual-drills). **The snapshot procedure is not CKA preparation** — *Implement etcd backup and restore* was [removed from the CKA curriculum in v1.32](../strands/certs.md#cka-changes), which the strand calls the single biggest trap in that revision. It is here at full length as operational skill and as [the capstone's](#capstone) first artifact, billed as internals rather than as exam prep.

---

<a id="chaos"></a>
## 3. Chaos drills

**Every one manual, and not because tooling is missing but because it would hide the mechanism** — [neither chaos tool has an etcd-aware fault](../strands/chaos.md#cannot-express), and control-plane quorum loss [cannot be scripted honestly](../strands/chaos.md#cannot-express) (a `PodKill` on a static etcd pod is undone by the kubelet — a lesson about static pods, not quorum). These are [the manual etcd drills](../strands/chaos.md#manual-drills), 1–3, plus the defrag measurement.

| # | Drill | By hand | What you must produce afterwards |
|---|---|---|---|
| 2.C1 | **[Corrupt a member and recover](../labs/02/26-corrupt-a-member.md)** | `dd` a page of `member/snap/db`, meet the cross-member hash mismatch, recover | The bbolt-page-level account of what "corrupt" means to a Raft log, and the signal `corrupt.go` caught it with |
| 2.C2 | **[Lose quorum (2 of 3) → read-only](../labs/02/27-lose-quorum.md)** | stop two members (VM stop, not `PodKill`); observe writes blocked, reads served-or-not; recover with `--force-new-cluster` | Why the minority cannot serve writes — Figure 2's safety rule, operational |
| 2.C3 | **[Restore from snapshot](../labs/02/28-restore-from-snapshot.md)** | `etcdctl snapshot save`; restore to a fresh `--data-dir`; fix the manifest; watch it return | The ordered procedure — **and the sinking realisation of what a stale snapshot means for everything created since** |
| 2.C4 | **[Fill the quota, then defrag](../labs/02/23-fill-the-quota.md)** | churn past `--quota-backend-bytes`; `NOSPACE`; compact + defrag + disarm | The before/after size curve with its **shape** defended, not its magnitude |
| 2.C5 | **[Partition one member off the peer port](../labs/02/15-partition-one-member.md)** | `iptables -j DROP` on 2380 both directions; the isolated member serves stale serializable reads and nothing else | The same safety rule one member short of 2.C2 — and a failure whose only broken segment is the one nobody suspects |

2.C3 is the capstone's restore step; 2.C4 is its defrag measurement.

**2.C5 is new, and it is a correction.** [Module 2.2](#m2-2) originally cited the single-member partition as *2.C2*, which is a different drill from the two-member quorum loss this table has always numbered 2.C2 — one leaves the cluster fully available, the other leaves it unable to decide anything. Both are wanted, so the partition was given its own number rather than renumbering a drill the [capstone](#capstone) refers to by name.

---

<a id="talks"></a>
## 4. Talks

Full entries with runtimes under [etcd](../strands/talks.md#etcd) — the densest area in the talk index. Watch in this order:

- **Understanding Distributed Consensus in etcd and Kubernetes** (Frank) — Raft from the problem statement, *before* any maintainer deep dive. Pairs with module 2.2's paper reading.
- **Deep Dive: etcd** (Li & Zhang) — the storage engine, MVCC, watch and compaction from a co-creator. Module 2.1 / 2.3 companion.
- **Debugging etcd** (Betz & Hu) — reading the metrics and logs to tell a disk-`fsync` stall from network latency from election churn. This is the talk that makes *"etcd is slow"* a falsifiable claim — exactly module 2.5's goal on `factory`.
- **Secrets of Running Etcd** (Siarkowicz) — the modern operational counterpart: why etcd is disk-latency-sensitive and what breaks at scale. Watch it while your homelab member is misbehaving.
- **Lessons Learned From Etcd the Data Inconsistency Issues** (Siarkowicz & Wang) — the maintainer postmortem of the v3.5 correctness bug. Pair it directly with module 2.5's `corrupt.go` reading; it teaches distrust of your own storage layer.

---

<a id="ecosystem"></a>
## 5. Ecosystem

**etcd itself**, treated for its internals rather than re-installed.

- **Hands-on:** the whole phase — you run the real thing, standalone, and break it.
- **Internals note:** the storage engine underneath is **bbolt** (a fork of `boltdb`), a single-file B+tree with **one writer at a time**. That single-writer constraint is *why* defrag must block and *why* `fsync` latency dominates etcd's performance — the object of module 2.4 is really bbolt wearing etcd's clothes. What the buckets actually contain is [the labs'](../labs/02/07-decode-a-bbolt-key.md) to answer.
- **Maturity:** CNCF **graduated**, and the **only** supported Kubernetes datastore — there is no second implementation to hedge against, which is exactly why a month spent here pays off across every phase below.

---

<a id="capstone"></a>
## 6. Capstone

**Induce quorum loss on a three-member cluster, restore to a known revision, and produce a before/after defrag measurement — with the shape of the curve read correctly rather than the magnitude.** Reading the shape *is* the assessed skill; absolute numbers on a 35 W i5 with contended disk are meaningless and claiming them would be the failure.

Three artifacts, one write-up:

1. **The quorum-loss recovery** (drill 2.C2 + 2.C3): stop two of three members, demonstrate the cluster is read-only/unavailable for writes, restore from a snapshot to a fresh data dir, and bring it back — with the **ordered** procedure written so another person could follow it.
2. **The defrag curve** (drill 2.C4): the churn → compact (no disk freed) → defrag (disk freed) sequence, plotted or tabulated, with the shape explained from mechanism.

**Lab** — [the capstone, in one sitting](../labs/02/29-the-capstone-writeup.md), with the rule that makes it a capstone rather than a repetition: notes are allowed, the exercise files are not.
3. **The write-up must cite `file:line`** a hostile reader could check — at minimum:
   - the batched-delete loop in `server/storage/mvcc/kvstore_compaction.go` that frees revisions without freeing disk;
   - where `Defrag()` runs in the `server/storage/backend/` bbolt layer and why it blocks;
   - the `ErrCompacted` site in `server/storage/mvcc/watchable_store.go`;
   - the `revision{main, sub}` encoding in `server/storage/mvcc/revision.go`.
   Every path stated here is one you must first have verified live in [module 2.0](#m2-0) — a citation you have not confirmed against the tree does not count.

This is the phase where the citation standard becomes real: the write-up is graded as much on whether its `file:line` references survive checking as on whether the cluster came back.

---

<a id="checklist"></a>
## 7. Checklist

Concrete, demonstrable, and grouped by evidence type. No item says *understand* or *know*.

**Timed / live against a running member:**
- [ ] Reproduce `ErrCompacted` on a historical `--rev` read within 2 minutes of a cold start.
- [ ] From a `tools/etcd-dump-db` dump, point at one key's revisions as raw bytes and decode one to `revision{main, sub}`.
- [ ] Drive a member to `NOSPACE` and recover it (compact → defrag → disarm) from memory.

**Written artifacts (each is a module's Write-down):**
- [ ] The ten-write key's generations before and after compaction (2.1).
- [ ] The leader write path with the WAL `fsync` placed correctly, citing `etcdserver/raft.go` (2.2).
- [ ] The slow-watcher path (synced → unsynced → victim → `ErrCompacted`) and its `"too old resource version"` translation (2.3).
- [ ] The two space measurements with the why-each sentence, shape not magnitude (2.4).
- [ ] The ordered restore procedure and the `corrupt.go` signal (2.5).
- [ ] The capstone: quorum-loss recovery + defrag curve + the `file:line` citations.

**Archaeology (`file:line` or sha a hostile reader could check):**
- [ ] The two `Was → Is` rows (mvcc move, Raft extraction) with the sha/release for each (2.0).
- [ ] One broken pre-2023 citation refuted, with where the symbol actually lives now.

**Falsifiable claims — write, then verify against source or a member:**
- [ ] What `resourceVersion` upstream *is*, and the one thing `api_guarantees` forbids inferring from it.
- [ ] Why compaction frees revisions but not disk, and defrag frees disk but blocks.
- [ ] Why a minority member cannot serve writes.

---

<a id="gate"></a>
## 8. Gate

You may advance to [P3](03-api-machinery.md) when:

1. **The single causal chain is reflexive:** etcd compaction → watcher eviction (`ErrCompacted`) → apiserver `410 Gone` → client-go relist. If you cannot state this without notes, **stay here** — [P3](03-api-machinery.md) and [P4](04-controllers.md) both assume it as a primitive, and it is the one fact this whole month exists to install.
2. **The capstone's `file:line` citations survive checking.** A cluster that came back but a write-up whose paths do not resolve in the live tree is a *fail* — the archaeology standard is not optional from this phase onward.
3. **You can predict compaction's effect before running it** — given a write history and a compaction revision, which reads survive and which get `ErrCompacted`, derived from `key_index.go`'s generations rather than by trying it.

The month is justified by what sits on it: every phase below reads or writes *through* etcd, and none of them re-teach it. When [P3](03-api-machinery.md) opens the apiserver's storage layer, the store it encodes into is one you have already broken and repaired by hand.
