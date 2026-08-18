<a id="the-sig-tour-in-call-order"></a>
# The tour the SIG wrote, read with the source open

**Artifact** — the call path from *"a pod appears"* to *"a node is chosen"*, written as a numbered list of functions in call order, each with the file it lives in, derived from `scheduling_code_hierarchy_overview.md` with the tree open beside it.

**Rests on** — nothing in this phase. This is the first thing to read and [the area says so twice](../../strands/source-reading.md#area-3-scheduler): the doc is a guided tour written for exactly this purpose, and reading `schedule_one.go` without it is the specific waste the area warns about.

**Topology** — none. A clone on [`forge`](../../strands/lab-topologies.md#build-guest) is all this needs.

**Setup**

```sh
ssh zain@10.10.10.125
ls ~/src/kubernetes || git clone --filter=blob:none https://github.com/kubernetes/kubernetes ~/src/kubernetes
cd ~/src/kubernetes && git rev-parse --short HEAD    # record this; every citation this phase belongs to it
ls pkg/scheduler
```

The clone convention and why the sha is recorded are [in the archaeology strand](../../strands/source-archaeology.md#clone); if a previous phase already made this clone, `git pull` and record the new sha rather than reusing an old one.

**Do**

1. Read the SIG doc top to bottom **once**, without the source, at reading speed. It is 22 KB and it is prose.
2. Read it again with `pkg/scheduler` open, and this time stop at every function it names and confirm the function exists where the doc says it does. Some will have moved.
3. Build the list. For each step: the function, its file, and one clause on what it does. Stop at the point where a node has been chosen — the bind is [a later exercise](13-why-the-bind-is-async.md).
4. Mark, in the margin, every place the doc names a path that is now wrong. Do not fix them silently — the count is the finding, and [one of them is this phase's canonical stale case](18-find-the-queue-yourself.md).

**Observe** — the shape of your own list. Count how many of its entries are in `schedule_one.go` and how many are somewhere else.

**Expect** — a list somewhere between fifteen and thirty steps, and the discovery that **the entry point is not where the interesting code is**. The scheduler's main loop is short; almost everything the doc walks through happens either in the queue (which is a whole module of its own) or inside plugins that the framework calls by interface.

Expect one or two stale paths. A tour written against a moving tree ages, and the doc is still the best thing available — which is a useful calibration for the whole phase: **the SIG docs are accurate about structure and unreliable about paths**, so take the narrative from them and the paths from the tree.

**Write down** — the list, the sha it was derived against, and the stale paths you found with the current location beside each.

**Footprint note** — a blobless clone of k/k and no cluster anywhere. [`forge` is 1536MB](../../strands/build-mechanics.md#forge) and reading costs nothing; [the first thing in this phase that does not fit](07-fifteen-thirty-six-will-not-link-a-scheduler.md) is four exercises away.

**Teardown** — nothing to delete. Keep the clone; every exercise in this directory reads from it. **No topology to release** — none has been provisioned yet, and [none is until exercise 6](06-three-rejections-three-plugins.md).
