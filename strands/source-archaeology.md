# Source archaeology

Every file path in this repository is a claim with an expiry date. This is the skill
for checking one, and the list of the ones already known to have moved.

**The problem is not that paths move — it is that stale paths fail silently.** A blog
post from 2021 that says "the scheduling queue lives in
`pkg/scheduler/internal/queue/`" does not error; it sends the reader to a directory
that no longer exists, and the most common response is to conclude the subsystem was
removed, or worse, to find a *similar* file and read the wrong thing. Most of the
Kubernetes-internals writing on the internet was accurate when published, which is
precisely why it is so convincing now.

So: **never trust a path, including the ~180 in
[`source-reading.md`](source-reading.md), without being able to date it.** That
document was verified against `kubernetes/kubernetes@master` on 2026-08-17 and will
begin rotting immediately.

## Which phase uses this

| Phase | Occasion |
|---|---|
| P2 — etcd | etcd's `mvcc/` move, and the Raft library's extraction to a separate repo — the most confusing pair for anyone reading older etcd material. |
| P3 — API machinery | `cacher.go` becoming a package; `contributors/devel` living in a *different repo* than everyone cites. |
| P5 — Scheduler | Two moves inside the scheduler in living memory, one of them removing a version segment that older code samples still import. |
| P7 — Networking | kube-proxy grew a third backend and lost its first. |
| P8 — Storage | `pkg/controller/volume/scheduling/` no longer exists, and the reason it moved *is* the delayed-binding lesson. |

The recurring shape: **a path move is usually a design decision leaving a trace.**
Delayed volume binding did not get relocated for tidiness — it moved out of the
controller manager and into the scheduler because the decision has to be made where
the node is chosen. Reading the commit that moved it is reading the argument.

<a id="method"></a>
## The method

Five techniques, in the order they are usually reached for.

### 1. Search for the symbol, not the path

The single highest-yield move, and the one people skip. Function and type names
survive refactors far more often than directory layouts, because renaming a symbol
breaks compilation across the tree while moving a package does not break anything a
reviewer will notice.

```sh
git grep -n 'func (sched \*Scheduler) scheduleOne'      # in a clone
git grep -n 'type PriorityQueue struct'
```

If GitHub code search is quicker for you, it is the same idea. Only fall back to
history when the symbol has genuinely gone.

### 2. `git log --follow` — where did this file go

```sh
git log --follow --oneline -- pkg/scheduler/internal/queue/scheduling_queue.go
```

`--follow` tracks the file across renames, so the log continues past the move. Its
limitation is worth knowing rather than discovering: it follows **one** path, so a
directory that was split across several new packages will only show you one of the
pieces.

### 3. `--diff-filter=D` — when was this deleted, and by whom

```sh
git log --diff-filter=D --oneline -- pkg/controller/volume/scheduling/
```

The commit that deleted a path is the best single document about where its
responsibility went, because the PR it belongs to had to justify the move. **Read the
commit message and then the PR** — `gh pr list --search <sha>` or the GitHub UI's
commit page, which links it.

### 4. The pickaxe — where did this code go

```sh
git log -S 'FindPodVolumes' --oneline            # commits changing the count of a string
git log -G 'volumeBinding.*Filter' --oneline     # same, but a regex on the diff
```

`-S` is the tool for "this function existed, now it doesn't, find the commit that
moved it". This is how a symbol search that came back empty gets rescued: `-S` looks
inside historical diffs rather than the current tree.

### 5. GitHub blame, walked backwards

On any file view, **Blame** → the "View blame prior to this change" arrow beside a
hunk. This is the interactive form of 3 and 4 and is often faster for a single line
than composing the right `git log`. It is also the only one of the five that works
without a clone.

<a id="clone"></a>
### A note on cloning k/k for this

Archaeology needs **history**, so `--depth 1` is exactly the wrong shortcut — it makes
techniques 2, 3 and 4 impossible. A full k/k clone is large enough to matter on a 25G
build guest. The right compromise is a **blobless** clone:

```sh
git clone --filter=blob:none https://github.com/kubernetes/kubernetes.git
```

Full commit and tree history, file contents fetched lazily on checkout or on demand.
`git log`, `--follow`, `--diff-filter` and blame all work; `-S`/`-G` will fetch blobs
as they scan and are correspondingly slower the first time. Keep the clone on
[`forge`](build-mechanics.md#forge) so it survives lab teardowns, and remember it
counts against that guest's 25G alongside `GOMODCACHE`.

<a id="kep-status"></a>
## Dating a feature, not just a path

The same skepticism applies to maturity claims, and there is one specific trap.

**A KEP's `status:` field lags reality and sometimes just stays wrong.** KEP-268
(priority and preemption) has been GA for years and its `kep.yaml` still reads
`implementable`. Nothing forces an author to return and update it after graduation, so
`status:` records what the *proposal* was, not what shipped.

Better signals, in descending order of reliability:

1. **The served API version.** If the type is in `v1`, that is not an opinion. A
   feature still behind `v1beta1` has not graduated regardless of what any document
   claims.
2. **The feature gate's own entry** in `pkg/features/kube_features.go`, which records
   the stage and the version it reached it in — and whether the gate still exists at
   all. A gate that has been *removed* is the strongest possible GA signal: the code
   path is now unconditional.
3. **The KEP's `milestone:` / `latest-milestone:`** fields, which are maintained more
   often than `status:`.
4. **The release CHANGELOG** for the version in question, searched for the KEP number.

Only after those does the prose of the KEP matter — and per
[`source-reading.md`](source-reading.md#soft-spots), **trust the content over the
status field** when they disagree.

<a id="stale-paths"></a>
## The seven known moves

Verified against the trees named in
[`source-reading.md`](source-reading.md)'s header on **2026-08-17**. Each of these
invalidates a large body of third-party material, so each is worth recognising on
sight.

| Was | Is | What it breaks |
|---|---|---|
| `pkg/scheduler/internal/queue/` | **`pkg/scheduler/backend/queue/`** | Nearly every scheduler-internals article written before the move. |
| `pkg/scheduler/framework/v1alpha1/` | **`pkg/scheduler/framework/`** — no version segment | Framework-plugin tutorials, including their *import paths*, so the sample code does not compile. |
| `pkg/controller/volume/scheduling/` | **`pkg/scheduler/framework/plugins/volumebinding/`** — the old path is gone entirely | Delayed-binding explanations that place the logic in the controller manager. The move is the lesson: the decision belongs where the node is picked. |
| `staging/src/k8s.io/apiserver/pkg/storage/cacher.go` | **`.../storage/cacher/`** — a package, split across `cacher.go`, `watch_cache.go`, `delegator.go` | Watch-cache walkthroughs that cite line numbers in a single file. |
| etcd `mvcc/` | **`server/storage/mvcc/`** | Most etcd storage-layer writing. |
| The Raft library inside `etcd-io/etcd` | **its own repo, `etcd-io/raft`** | Anything that expects to read Raft and etcd's storage in one clone. Two clones now. |
| `pkg/proxy/userspace` | **gone** — three backends now: `iptables`, `ipvs`, `nftables` | Comparisons framed as "userspace vs iptables", i.e. most of the historical kube-proxy corpus. |

And one that is not a move but a repo confusion, which produces the same dead end:

> **`contributors/devel/` and the API conventions doc are in
> [`kubernetes/community`](https://github.com/kubernetes/community), not
> `kubernetes/kubernetes`.** This is the most common miscitation in the ecosystem.
> Further, `contributors/design-proposals/` in that repo is now a stub README — the
> real corpus is the separate
> [`kubernetes/design-proposals-archive`](https://github.com/kubernetes/design-proposals-archive)
> repo.

**This table is expected to grow.** When a path in
[`source-reading.md`](source-reading.md) turns out to be stale, the fix is two edits
in one commit: correct it there, and add a row here. That is what keeps the strand
docs living rather than a second frozen record — see
[`README.md`](README.md#provenance).

<a id="drills"></a>
## Drills

Short, self-contained, and each one produces an answer that can be checked against
the table above — so a wrong method is visible immediately.

1. **Find the commit that deleted `pkg/controller/volume/scheduling/`** and read its
   PR description. State, in one sentence, why the code moved into the scheduler.
   (Technique 3, then the PR.) This is P8's, and it is the cheapest possible
   introduction to delayed binding.
2. **Date the scheduler-queue move.** Which release first shipped
   `pkg/scheduler/backend/queue/`? Answer it two ways — `--follow` and the CHANGELOG —
   and note which was faster.
3. **Pickaxe a symbol you cannot find.** Pick any function named in a pre-2023
   scheduler or storage article that is not in the tree today, and use `git log -S` to
   find where it went. If it was renamed rather than moved, technique 1 on the *new*
   name should confirm it.
4. **Catch a KEP status field lying.** Verify for yourself that KEP-268 reads
   `implementable`, then establish its real maturity from the served API version and
   the feature gate. This drill exists because it teaches distrust of exactly the
   field that is most convenient to quote.
5. **Walk one line of `cacher.go` backwards** with GitHub blame until it is in the
   pre-split single file. The point is the arrow, not the line.

A drill is passed when the answer is a **`file:line` or a commit sha** that a hostile
reader could check and find wrong — the same standard the build track's tier-2 gates
use ([`build-mechanics.md`](build-mechanics.md#gates)).
