# Source archaeology

Every file path in this repository is a claim, and every claim has an expiry date. This
document teaches you the skill for checking one. It also lists the paths that are already
known to have moved.

**The problem is not that paths move. The problem is that stale paths fail silently.** Take a
blog post from 2021 that says "the scheduling queue lives in
`pkg/scheduler/internal/queue/`". That sentence does not error. It sends the reader to a
directory that no longer exists. The most common response is to conclude that the subsystem
was removed. The worse response is to find a *similar* file and read the wrong thing. Most of
the Kubernetes-internals writing on the internet was accurate when it was published, and that
is exactly why it is so convincing now.

So here is the rule. **Never trust a path without being able to date it.** That rule includes
the roughly 180 paths in [`source-reading.md`](source-reading.md). That document was verified
against `kubernetes/kubernetes@master` on 2026-08-17, and it began to rot immediately after.

## Which phase uses this

| Phase | Occasion |
|---|---|
| P2 — etcd | The `mvcc/` move in etcd, and the extraction of the Raft library into a separate repo. That pair confuses anyone who reads older etcd material. |
| P3 — API machinery | `cacher.go` became a package. Also, `contributors/devel` lives in a *different repo* than everyone cites. |
| P5 — Scheduler | Two moves inside the scheduler in living memory. One of them removed a version segment that older code samples still import. |
| P7 — Networking | kube-proxy grew a third backend, and it lost its first one. |
| P8 — Storage | `pkg/controller/volume/scheduling/` no longer exists, and the reason that it moved *is* the delayed-binding lesson. |

The shape recurs: **a path move is usually a design decision that leaves a trace.** Delayed
volume binding was not relocated for tidiness. It moved out of the controller manager and
into the scheduler, because the decision has to be made where the node is chosen. Reading the
commit that moved it is reading the argument.

<a id="method"></a>
## The method

Five techniques, in the order that you usually reach for them.

### 1. Search for the symbol, not the path

This is the highest-yield move, and it is the one that people skip. Function names and type
names survive refactors far more often than directory layouts do. Here is why. Renaming a
symbol breaks compilation across the tree, and moving a package breaks nothing that a
reviewer will notice.

```sh
git grep -n 'func (sched \*Scheduler) scheduleOne'      # in a clone
git grep -n 'type PriorityQueue struct'
```

If GitHub code search is quicker for you, then use it. It is the same idea. Fall back to
history only when the symbol has genuinely gone.

### 2. `git log --follow` — where did this file go

```sh
git log --follow --oneline -- pkg/scheduler/internal/queue/scheduling_queue.go
```

`--follow` tracks the file across renames, so the log continues past the move. Learn its
limitation now, rather than discovering it later. It follows **one** path. So if a directory
was split across several new packages, then it shows you one of the pieces only.

### 3. `--diff-filter=D` — when was this deleted, and by whom

```sh
git log --diff-filter=D --oneline -- pkg/controller/volume/scheduling/
```

The commit that deleted a path is the best single document about where its responsibility
went. The reason is that the PR that it belongs to had to justify the move. **Read the commit
message, and then read the PR.** Use `gh pr list --search <sha>`, or use the commit page in
the GitHub UI, which links the PR.

### 4. The pickaxe — where did this code go

```sh
git log -S 'FindPodVolumes' --oneline            # commits changing the count of a string
git log -G 'volumeBinding.*Filter' --oneline     # same, but a regex on the diff
```

`-S` is the tool for one job: this function existed, it does not exist now, and you want the
commit that moved it. This is how you rescue a symbol search that came back empty. `-S` looks
inside historical diffs, rather than inside the current tree.

### 5. GitHub blame, walked backwards

Open any file view, and select **Blame**. Then use the "View blame prior to this change"
arrow beside a hunk. This is the interactive form of techniques 3 and 4, and it is often
faster for a single line than composing the right `git log` is. It is also the only one of
the five techniques that works without a clone.

<a id="clone"></a>
### A note on cloning k/k for this

Archaeology needs **history**. So `--depth 1` is exactly the wrong shortcut, because it makes
techniques 2, 3 and 4 impossible. But a full k/k clone is large enough to matter on a 25G
build guest. The right compromise is a **blobless** clone:

```sh
git clone --filter=blob:none https://github.com/kubernetes/kubernetes.git
```

You get the full commit history and the full tree history. File contents are fetched lazily,
on checkout or on demand. `git log`, `--follow`, `--diff-filter` and blame all work. `-S` and
`-G` fetch blobs as they scan, so they are slower the first time. Keep the clone on
[`forge`](build-mechanics.md#forge), so that it survives lab teardowns. Remember also that it
counts against that guest's 25G, alongside `GOMODCACHE`.

<a id="kep-status"></a>
## Dating a feature, not just a path

The same skepticism applies to maturity claims, and there is one specific trap.

**A KEP's `status:` field lags reality, and sometimes it just stays wrong.** KEP-268, which
covers priority and preemption, has been GA for years. Its `kep.yaml` still reads
`implementable`. Nothing forces an author to return and update that field after graduation.
So `status:` records what the *proposal* was, and not what shipped.

Here are better signals, in descending order of reliability.

1. **The served API version.** If the type is in `v1`, then that is not an opinion. A feature
   that is still behind `v1beta1` has not graduated, whatever any document claims.
2. **The feature gate's own entry** in `pkg/features/kube_features.go`. It records the stage,
   and the version in which the gate reached that stage. It also tells you whether the gate
   still exists at all. A gate that has been *removed* is the strongest possible GA signal,
   because the code path is now unconditional.
3. **The KEP's `milestone:` and `latest-milestone:` fields.** They are maintained more often
   than `status:` is.
4. **The release CHANGELOG** for the version in question. Search it for the KEP number.

Only after those four signals does the prose of the KEP matter. And when the prose and the
status field disagree, **trust the content over the status field**, per
[`source-reading.md`](source-reading.md#soft-spots).

<a id="stale-paths"></a>
## The seven known moves

These were verified on **2026-08-17**, against the trees named in the header of
[`source-reading.md`](source-reading.md). Each move invalidates a large body of third-party
material, so each one is worth recognising on sight.

| Was | Is | What it breaks |
|---|---|---|
| `pkg/scheduler/internal/queue/` | **`pkg/scheduler/backend/queue/`** | Nearly every scheduler-internals article written before the move. |
| `pkg/scheduler/framework/v1alpha1/` | **`pkg/scheduler/framework/`** — no version segment | Framework-plugin tutorials. It breaks their *import paths*, so the sample code does not compile. |
| `pkg/controller/volume/scheduling/` | **`pkg/scheduler/framework/plugins/volumebinding/`** — the old path is gone entirely | Delayed-binding explanations that place the logic in the controller manager. The move is the lesson: the decision belongs where the node is picked. |
| `staging/src/k8s.io/apiserver/pkg/storage/cacher.go` | **`.../storage/cacher/`** — a package, split across `cacher.go`, `watch_cache.go` and `delegator.go` | Watch-cache walkthroughs that cite line numbers in a single file. |
| etcd `mvcc/` | **`server/storage/mvcc/`** | Most etcd storage-layer writing. |
| The Raft library inside `etcd-io/etcd` | **its own repo, `etcd-io/raft`** | Anything that expects to read Raft and etcd's storage in one clone. It is two clones now. |
| `pkg/proxy/userspace` | **gone** — there are three backends now: `iptables`, `ipvs` and `nftables` | Comparisons framed as "userspace vs iptables", which is most of the historical kube-proxy corpus. |

There is one more case. It is not a move, but a repo confusion, and it produces the same dead
end:

> **`contributors/devel/` and the API conventions doc live in
> [`kubernetes/community`](https://github.com/kubernetes/community), and not in
> `kubernetes/kubernetes`.** This is the most common miscitation in the ecosystem. There is
> more. `contributors/design-proposals/` in that repo is now a stub README. The real corpus
> is a separate repo,
> [`kubernetes/design-proposals-archive`](https://github.com/kubernetes/design-proposals-archive).

**This table is expected to grow.** When a path in
[`source-reading.md`](source-reading.md) turns out to be stale, the fix is two edits in one
commit: correct the path there, and add a row here. That practice is what keeps the strand
docs living, instead of turning them into a second frozen record. See
[`README.md`](README.md#provenance).

<a id="drills"></a>
## Drills

Each drill is short and self-contained. Each one produces an answer that you can check
against the table above, so a wrong method is visible immediately.

1. **Find the commit that deleted `pkg/controller/volume/scheduling/`**, and read its PR
   description. Then state, in one sentence, why the code moved into the scheduler. Use
   technique 3, and then read the PR. This drill belongs to P8, and it is the cheapest
   possible introduction to delayed binding.
2. **Date the scheduler-queue move.** Which release first shipped
   `pkg/scheduler/backend/queue/`? Answer the question two ways, with `--follow` and with the
   CHANGELOG. Then note which way was faster.
3. **Pickaxe a symbol that you cannot find.** Pick any function that a pre-2023 scheduler or
   storage article names, and that is not in the tree today. Then use `git log -S` to find
   where it went. If it was renamed rather than moved, then technique 1 on the *new* name
   should confirm that.
4. **Catch a KEP status field lying.** Verify for yourself that KEP-268 reads `implementable`.
   Then establish its real maturity from the served API version and from the feature gate.
   This drill exists to teach distrust of the one field that is most convenient to quote.
5. **Walk one line of `cacher.go` backwards** with GitHub blame, until the line is in the
   pre-split single file. The point of the drill is the arrow, and not the line.

A drill is passed when the answer is a **`file:line` or a commit sha**. A hostile reader must
be able to check that answer and find it wrong. This is the same standard that the tier-2
gates of the build track use. See [`build-mechanics.md`](build-mechanics.md#gates).
