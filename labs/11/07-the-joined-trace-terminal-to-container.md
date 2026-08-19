<a id="the-joined-trace-terminal-to-container"></a>
# Capstone 1 — the three sub-paths joined into one cited trace, terminal to container, checkable by a hostile reader

**Artifact** — one continuous trace, `kubectl` to running container, every seam a `file:line` at a single stated commit sha:

`kubectl` → request filters → `handlers/create.go` → admission chain → `registry/generic/registry/store.go` → `storage/etcd3/store.go` → etcd `Txn` → watch cache → scheduler informer → `schedule_one.go` → **Binding** → kubelet `config/apiserver.go` → `pod_workers.go` → `computePodActions` → **CRI** → **CNI** → the [P0](../../phases/00-linux-primitives.md) namespaces and cgroups.

This is [trace #1's spec](../../strands/source-reading.md#trace-pod-create), and the deliverable is the *citations*, not the diagram. It is attempted only now, after every area is behind you — and [named in P0 as the visible target from week one](../../phases/00-linux-primitives.md), so producing it closes the loop the curriculum opened.

**Rests on** — the three sub-paths, each already cited on its own: [Seam A](02-seam-a-client-apiserver-etcd.md), [Seam B](04-seam-b-watch-cache-scheduler-binding.md), [Seam C](05-seam-c-kubelet-cri-cni-the-syscalls.md); and [the paper map](01-the-paper-trace-before-the-cluster.md) this finally either vindicates or overwrites in red. This capstone adds no new mechanism — it joins three artifacts and pins them to one sha.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), still up from the seams, so you can re-walk any hop you are unsure of. This is the last exercise that needs it before the postmortem block; it does not release it.

**Read** — [the capstone spec in the phase](../../phases/11-synthesis.md#capstone) and [trace #1](../../strands/source-reading.md#trace-pod-create). Nothing new is read here; every file was opened in an earlier phase, and what is new is the *order* — the order a single pod-create visits them, which no single phase could show.

> **Question to answer against the whole trace:** at one stated commit sha, does every one of the six seams resolve to a line a stranger can open — or does at least one collapse to a description? A described seam is an unentered area wearing a citation's clothes. Name it, and the phase behind it.

**Build** — assemble the three sub-paths into one document. Pick one commit sha and re-confirm every cited line still says what your notes claim at *that* sha — a citation valid at last week's sha and wrong at this one is worse than none. Join the seams into a single arrow-by-arrow path from terminal to container.

**Verify from outside** — a hostile reader clones `k/k` at your sha and opens every line in order. Each must land where the trace says. "The apiserver validates it" fails; `create.go:NNN` at `abc123` passes. This is [the gate the whole curriculum was built to reach](../../phases/11-synthesis.md#gate): if any seam is a description, [go back to that phase, not forward](../../phases/11-synthesis.md#gate).

**Expect** — one document, one sha, every arrow a checkable line, and — if the phases landed — no gaps. Expect the weakest seam to be the one whose phase you moved through fastest; that is the diagnostic the whole descent was pointing at.

**Write down** — the joined trace with the sha at its head. This is [checklist item "the three sub-paths joined"](../../phases/11-synthesis.md#checklist) and the first of the two capstone deliverables; [the second](11-the-upgrade-that-drops-nothing.md) proves you can operate the machine without stopping it.

**Footprint note** — [`pair` at 5.0GB](../../strands/lab-topologies.md#pair), unchanged; a reading-and-writing exercise on a cluster already up.

**Teardown** — nothing new was created. **The topology stays** — [the DNS postmortem's conntrack drill](09-11c3-a-rolling-update-under-conntrack-watch.md) and [the rollout rehearsal](10-11c2-a-botched-rollout-and-the-incident-note.md) run on this same `pair`, which is released only when [the upgrade capstone](11-the-upgrade-that-drops-nothing.md) replaces it with `workhorse`.
