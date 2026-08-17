# Phase 2 — etcd internals

> **4–5 weeks.** The brief singled this phase out as worth a month, and [the capacity plan](https://github.com/k3ii/k8s-academy/issues/8) calls it the best depth-per-MB in the curriculum — it needs **no Kubernetes at all**, so a 35 W homelab can run the real thing and watch it degrade honestly.
> The range is planning information. **The gate at the bottom decides when the phase is finished.**

| | |
|---|---|
| **Prerequisites** | [P1](01-operate-shallow.md) — you watched `resourceVersion` move on an object and were told *why* was deferred to here. This is here. The [Go primer](01-operate-shallow.md) shipped in P1's last module because **this is the first phase that opens Go source in anger.** |
| **Unlocks** | [P3](03-api-machinery.md) reads the apiserver's storage layer *down onto* this — the encode/decode, the `cacher`, the storage `Interface`. [P4](04-controllers.md)'s informer is the other end of the watch you trace here. And the `"too old resource version"` every operator eventually hits gets its true name — `ErrCompacted` — in module 2.3. |
| **Source area** | [Area 1 — etcd](../strands/source-reading.md#area-1-etcd), entry point `server/storage/mvcc/key_index.go`. Two repos now, not one — the Raft library was [extracted to `etcd-io/raft`](../strands/source-archaeology.md#stale-paths). |
| **Language** | Go, read not written. **The source-archaeology method lands here** ([module 2.0](#module-20)) because this is the first real source phase — verifying a cited path against the live tree becomes a taught, graded skill from now on. |
| **Strands** | [source reading](../strands/source-reading.md#area-1-etcd) · [source archaeology](../strands/source-archaeology.md#method) · [talks](../strands/talks.md#etcd) · [chaos](../strands/chaos.md#cannot-express) |

---

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

## 2. Modules

Reading is [Area 1](../strands/source-reading.md#area-1-etcd), sequenced approachable → hard and interleaved with labs that give each file something to point at. **No fact from the strand is restated here** — each item below carries only a *question to answer from the source*, which is the phase-specific part.

<a id="module-20"></a>
### Module 2.0 — Source archaeology, the method (~first week, runs alongside 2.1)

This is where the curriculum stops trusting citations. Every later phase inherits the standard set here: a path is not real until you have seen it in the tree you are actually reading.

**Read** — [the method](../strands/source-archaeology.md#method) (five techniques) and [the seven known moves](../strands/source-archaeology.md#stale-paths). **Two of those seven are yours this phase:** etcd `mvcc/` → `server/storage/mvcc/`, and the Raft library extracted out of `etcd-io/etcd` into its own `etcd-io/raft` repo.

**Do**
1. **Blobless clones on [`forge`](../strands/source-archaeology.md#clone), both repos:** `git clone --filter=blob:none https://github.com/etcd-io/etcd` and the same for `etcd-io/raft`. `--depth 1` is the wrong shortcut — techniques 2–4 need history. Two clones, because Raft is two repos now.
2. **Verify the entry point.** Confirm `server/storage/mvcc/key_index.go` resolves in the live tree, then `git log --follow` it back through the `mvcc/` move. Answer: which release first shipped the `server/storage/` path?
3. **Prove the extraction.** Establish, with a commit or a `go.mod` line, that `etcd-io/raft` is genuinely separate and when it split — so that any article expecting to read Raft and the store in one clone is dated on sight.

**Break it** — take a paragraph from any pre-2023 etcd storage blog, pick a path or symbol it cites, and **break its claim**: show with `git log -S` or blame where that symbol actually lives now, or that it is gone. A wrong method fails loudly here, which is the point.

**Write down** — for each of your two moves, the `Was → Is` row and the sha or release that made it. This is the archaeology receipt the checklist asks for.

> **Standard, inherited by every later phase:** a drill is passed when its answer is a `file:line` or a commit sha a hostile reader could check and find wrong — [the build track's tier-2 bar](../strands/source-archaeology.md#drills).

### Module 2.1 — MVCC and revisions (~1 week)

The entry point, and the module that makes `resourceVersion` stop being magic.

**Read** — [Area 1](../strands/source-reading.md#area-1-etcd), with a question to answer from each:

| Item | Answer from it |
|---|---|
| `key_index.go` (item 4, ⭐) | What does a *generation* contain, and what exactly does `compact(rev)` remove from a keyIndex versus leave behind? |
| `revision.go` (item 5) | How are `main` and `sub` packed into the bbolt key bytes — and why does `sub` exist at all (what has more than one revision inside a single transaction)? |
| `data_model` + `api_guarantees` docs (items 1, 3) | From `api_guarantees`: what is a client **forbidden** from inferring from a revision number? This is the upstream root of the `resourceVersion` opacity rule you met in [P1](01-operate-shallow.md). |
| `index.go` (item 9) | The in-memory B-tree over keyIndexes — what does a read consult *before* it ever touches bbolt? |

**Do** — single member, `etcdctl`. Write one key ten times; `get --rev` at each historical revision; `compact` in the middle; watch the older `--rev` reads flip to `ErrCompacted`. Dump the db with `tools/etcd-dump-db` and find your key's revisions as raw bytes.

**Break it** — `compact` to a revision, then request one below it. The error you get **is** objective 1, and its name reappears in module 2.3 as the watcher failure and in [P3](03-api-machinery.md) as the apiserver relist trigger.

**Write down** — the generations of your ten-write key before and after compaction, and the one-sentence `resourceVersion = etcd revision` mapping with the guarantee it does *not* carry.

### Module 2.2 — Raft, the library versus the server (~1 week)

Consensus, read as the two-layer thing it actually is: an algorithm (the paper) and a *state machine with no disk, network, or clock* (the library).

**Read**

| Item | Answer from it |
|---|---|
| Raft paper, Figure 2 (item 6) | Non-negotiable first. What are the three sub-problems, and which single rule makes a committed entry safe forever? |
| `raft/design.md` + `raft/doc.go` (items 7, 8) | The library is a state machine, not a server. What are you — the caller — obligated to do with a `Ready`, and in what **strict order** must you persist entries, hard state, and snapshot before you `Advance()`? |
| `etcdserver/raft.go` (item 18) | The server side of that contract: where in `raftNode.start()` does the **WAL `fsync`** happen relative to sending messages and applying committed entries? |
| `write_workflow_leader.png` (item 24) | The one-picture check on your mental model of the above. |

**Do** — three members. `etcdctl endpoint status` to find the leader; `move-leader`; watch a follower's log index track the leader's. Kill the leader, watch an election, read the term change.

**Break it** — chaos drill [2.C2](#4-chaos-drills): partition one member off the peer port (2380) and watch a *minority* member go unavailable for writes while the majority carries on — the safety rule from Figure 2 made operational.

**Write down** — the leader write path as a sequence, with the `fsync` placed correctly, citing the function in `etcdserver/raft.go` where it happens.

### Module 2.3 — Watch (~4–5 days)

The mechanism the entire Kubernetes control plane is a client of. This is the module [P4](04-controllers.md) picks up from the other side.

**Read**

| Item | Answer from it |
|---|---|
| `watcher_group.go` + `watcher.go` (item 10) | What distinguishes the **synced** from the **unsynced** watcher set, and what is the interval tree indexing? |
| `watchable_store.go` (item 11, ⭐ of this module) | Follow `syncWatchers` and the **victim list**: what happens to a watcher too slow to keep up, and what error does it ultimately receive? |
| `api` doc (item 2) | The `Watch` gRPC surface with `WithRev` — how does a client *resume* a watch, and what does it pass? |

**Do** — open a watch from an old revision with `etcdctl watch --rev=<old>`; then `compact` past it in another terminal and watch the stream terminate.

**Break it** — force the failure deliberately: start a watch, compact aggressively, and capture the exact error. **Name it `ErrCompacted`, then name what a Kubernetes client sees when this reaches it: `"too old resource version"` → a full relist.** This single causal chain — etcd compaction → watcher eviction → apiserver 410 → client-go relist — is the spine of module 2.3 and a load-bearing fact for [P4](04-controllers.md).

**Write down** — the slow-watcher path (synced → unsynced → victim → `ErrCompacted`) with the `watchable_store.go` function names, and its Kubernetes-facing translation.

### Module 2.4 — Compaction, defrag, and bbolt (~4–5 days)

The two space problems operators conflate, separated for good.

**Read**

| Item | Answer from it |
|---|---|
| `kvstore_compaction.go` + `kvstore.go` (item 12) | Compaction is a **batched bbolt delete loop**. Why does deleting revisions free *logical* space but return **no disk to the filesystem**? |
| `backend.go` + `batch_tx.go` (item 16) | The bbolt layer — batch transactions and commit intervals. Where does `Defrag()` actually run, and why must it **block**? |
| `maintenance` doc (item 13) | Auto-compaction modes, the space quota, and the `NOSPACE` alarm. What state is the cluster in once the alarm fires? |

**Do** — fill a member with churn (write-delete loops) to inflate the db; `compact`; measure `db size` — unchanged. Then `defrag`; measure again — now it drops. This before/after pair is the capstone's core.

**Break it** — chaos drill [2.C4](#4-chaos-drills): drive the db past its `--quota-backend-bytes` and meet the `NOSPACE` alarm and the read-only cluster it produces; recover with compact + defrag + `alarm disarm`, in that order.

**Write down** — the two measurements (post-compact size, post-defrag size) and one sentence each on *why* compaction did not move the first number and defrag did. **Read the shape, not the magnitude** — absolute bytes on this disk mean nothing.

### Module 2.5 — Failure, corruption, and recovery (~1 week)

Where the phase's chaos lives. On-disk reality first, then break it and put it back.

**Read**

| Item | Answer from it |
|---|---|
| `persistent-storage-files` doc (item 17) | The on-disk trio — WAL segments, snapshot files, `db`. What is each *for*, and which one can be rebuilt from the others? |
| `performance` + `hardware` docs (item 15) | `fsync` latency and the `--heartbeat-interval`/`--election-timeout` derivation from RTT. **`factory` is a 35 W i5 with contended disk** — predict which of these etcd will violate, and be able to explain the resulting log lines. |
| v3.5 data-inconsistency postmortem (item 19) + `corrupt.go` (item 20) | A real correctness bug root-caused in public, and the corruption detector it produced. What signal does `corrupt.go` compare across members, and what would a `dd` to one member's `db` do to it? |

**Do** — the three recovery drills below (2.C1, 2.C2, 2.C3), by hand, in order.

**Break it** — every drill in this module *is* a Break-it; that is the shape of the phase's chaos, which is why it stays [manual](../strands/chaos.md#manual-drills). The snapshot save/restore procedure here is **banked toward CKA** (etcd backup/restore is a CKA cluster-maintenance competency) — you are producing the exam skill as a by-product of doing it for real, not drilling it separately.

**Write down** — the ordered restore procedure (snapshot → fresh `--data-dir` → new `--initial-cluster-token` → fix the static-pod manifest → verify), and the corruption signal `corrupt.go` uses.

---

## 3. Chaos drills

**Every one manual, and not because tooling is missing but because it would hide the mechanism** — [neither chaos tool has an etcd-aware fault](../strands/chaos.md#cannot-express), and control-plane quorum loss [cannot be scripted honestly](../strands/chaos.md#cannot-express) (a `PodKill` on a static etcd pod is undone by the kubelet — a lesson about static pods, not quorum). These are [the manual etcd drills](../strands/chaos.md#manual-drills), 1–3, plus the defrag measurement.

| # | Drill | By hand | What you must produce afterwards |
|---|---|---|---|
| 2.C1 | **Corrupt a member and recover** | `dd` a page of `member/snap/db`, meet `etcdctl check` / consistency-index mismatch, recover | The bbolt-page-level account of what "corrupt" means to a Raft log, and the signal `corrupt.go` caught it with |
| 2.C2 | **Lose quorum (2 of 3) → read-only** | stop two members (VM stop, not `PodKill`); observe writes blocked, reads served-or-not; recover with `--force-new-cluster` | Why the minority cannot serve writes — Figure 2's safety rule, operational |
| 2.C3 | **Restore from snapshot** | `etcdctl snapshot save`; restore to a fresh `--data-dir`; fix the manifest; watch it return | The ordered procedure — **and the sinking realisation of what a stale snapshot means for everything created since** |
| 2.C4 | **Fill the quota, then defrag** | churn past `--quota-backend-bytes`; `NOSPACE`; compact + defrag + disarm | The before/after size curve with its **shape** defended, not its magnitude |

2.C3 is the capstone's restore step; 2.C4 is its defrag measurement.

---

## 4. Talks

Full entries with runtimes under [etcd](../strands/talks.md#etcd) — the densest area in the talk index. Watch in this order:

- **Understanding Distributed Consensus in etcd and Kubernetes** (Frank) — Raft from the problem statement, *before* any maintainer deep dive. Pairs with module 2.2's paper reading.
- **Deep Dive: etcd** (Li & Zhang) — the storage engine, MVCC, watch and compaction from a co-creator. Module 2.1 / 2.3 companion.
- **Debugging etcd** (Betz & Hu) — reading the metrics and logs to tell a disk-`fsync` stall from network latency from election churn. This is the talk that makes *"etcd is slow"* a falsifiable claim — exactly module 2.5's goal on `factory`.
- **Secrets of Running Etcd** (Siarkowicz) — the modern operational counterpart: why etcd is disk-latency-sensitive and what breaks at scale. Watch it while your homelab member is misbehaving.
- **Lessons Learned From Etcd the Data Inconsistency Issues** (Siarkowicz & Wang) — the maintainer postmortem of the v3.5 correctness bug. Pair it directly with module 2.5's `corrupt.go` reading; it teaches distrust of your own storage layer.

---

## 5. Ecosystem

**etcd itself**, treated for its internals rather than re-installed.

- **Hands-on:** the whole phase — you run the real thing, standalone, and break it.
- **Internals note:** the storage engine underneath is **bbolt** (a fork of `boltdb`), a single-file B+tree with **one writer at a time**. That single-writer constraint is *why* defrag must block and *why* `fsync` latency dominates etcd's performance — the object of module 2.4 is really bbolt wearing etcd's clothes. Dump a `db` file with `tools/etcd-dump-db` and read the buckets directly.
- **Maturity:** CNCF **graduated**, and the **only** supported Kubernetes datastore — there is no second implementation to hedge against, which is exactly why a month spent here pays off across every phase below.

---

## 6. Capstone

**Induce quorum loss on a three-member cluster, restore to a known revision, and produce a before/after defrag measurement — with the shape of the curve read correctly rather than the magnitude.** Reading the shape *is* the assessed skill; absolute numbers on a 35 W i5 with contended disk are meaningless and claiming them would be the failure.

Three artifacts, one write-up:

1. **The quorum-loss recovery** (drill 2.C2 + 2.C3): stop two of three members, demonstrate the cluster is read-only/unavailable for writes, restore from a snapshot to a fresh data dir, and bring it back — with the **ordered** procedure written so another person could follow it.
2. **The defrag curve** (drill 2.C4): the churn → compact (no disk freed) → defrag (disk freed) sequence, plotted or tabulated, with the shape explained from mechanism.
3. **The write-up must cite `file:line`** a hostile reader could check — at minimum:
   - the batched-delete loop in `server/storage/mvcc/kvstore_compaction.go` that frees revisions without freeing disk;
   - where `Defrag()` runs in the `server/storage/backend/` bbolt layer and why it blocks;
   - the `ErrCompacted` site in `server/storage/mvcc/watchable_store.go`;
   - the `revision{main, sub}` encoding in `server/storage/mvcc/revision.go`.
   Every path stated here is one you must first have verified live in [module 2.0](#module-20) — a citation you have not confirmed against the tree does not count.

This is the phase where the citation standard becomes real: the write-up is graded as much on whether its `file:line` references survive checking as on whether the cluster came back.

---

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

## 8. Gate

You may advance to [P3](03-api-machinery.md) when:

1. **The single causal chain is reflexive:** etcd compaction → watcher eviction (`ErrCompacted`) → apiserver `410 Gone` → client-go relist. If you cannot state this without notes, **stay here** — [P3](03-api-machinery.md) and [P4](04-controllers.md) both assume it as a primitive, and it is the one fact this whole month exists to install.
2. **The capstone's `file:line` citations survive checking.** A cluster that came back but a write-up whose paths do not resolve in the live tree is a *fail* — the archaeology standard is not optional from this phase onward.
3. **You can predict compaction's effect before running it** — given a write history and a compaction revision, which reads survive and which get `ErrCompacted`, derived from `key_index.go`'s generations rather than by trying it.

The month is justified by what sits on it: every phase below reads or writes *through* etcd, and none of them re-teach it. When [P3](03-api-machinery.md) opens the apiserver's storage layer, the store it encodes into is one you have already broken and repaired by hand.
