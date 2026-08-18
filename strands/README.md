# Strands

Cross-cutting material that several phases consume. A phase file links into a strand
doc and never restates its content — if a fact appears in both, the phase file is
wrong and the phase file is what gets edited.

| Doc | What phases link into it for |
|---|---|
| [`source-reading.md`](source-reading.md) | The k/k, etcd, CNI, CSI and KEP corpus, per depth area, with an entry point and a difficulty marker per item. |
| [`talks.md`](talks.md) | The 73 verified conference talks, per topic, with exact runtimes. |
| [`chaos.md`](chaos.md) | Which fault to inject, with which tool, by which Linux primitive — and which faults no tool can express. |
| [`certs.md`](certs.md) | CKAD / CKA / CKS domain weights, exam mechanics, practice-resource verdicts, speed tactics. |
| [`build-mechanics.md`](build-mechanics.md) | How the eleven build-track artifacts are compiled, shipped, identified, sized and gated. |
| [`lab-topologies.md`](lab-topologies.md) | The eight named guest layouts at per-node resolution, their addresses, and how one is provisioned, reached and torn down. |
| [`source-archaeology.md`](source-archaeology.md) | How to date a path that has moved, and the six refactors that make older third-party material wrong. |

<a id="anchors"></a>
## Anchors are the contract

**Every link target in these documents is an explicit `<a id="...">` tag, never a
heading-derived slug.** Phase files link to those ids. A heading can then be
reworded, retitled or demoted without silently breaking a link, and the ids are
greppable:

```sh
grep -rn '<a id=' strands/          # every anchor this repo publishes
grep -rno 'strands/[a-z-]*\.md#[a-z0-9-]*' phases/   # every anchor consumed
python3 strands/check-anchors.py    # both sides, cross-checked; non-zero on a break
```

[`check-anchors.py`](check-anchors.py) is the enforceable form of this section: it
fails on a duplicate id, on the same id published by two different docs, and on any
link — from `strands/` or `phases/` — to a file or anchor that does not exist.

Heading slugs were rejected because GitHub's slugger is not the obvious function.
`## Area 6 — Storage` slugs to `area-6--storage`, not `area-6-storage` — the em dash
is deleted and leaves the two surrounding spaces to become two hyphens. The first
phase file drafted had already written `#area-6-storage` and would have shipped a
dead link. Explicit ids remove the class of bug rather than the instance.

**Adding an anchor is free. Renaming or removing one is a breaking change** — grep
`phases/` first, and change both sides in the same commit.

<a id="provenance"></a>
## Provenance

Each strand doc names the file in [`../research/`](../research/) it derives from.
The distinction is lifecycle, not content:

- **`research/` is the dated record.** What was verified, against which tree, on
  which date, by which method — including what could *not* be verified. It is not
  edited to stay current; a stale research doc is still an accurate record.
- **`strands/` is the living form.** Paths move, KEPs graduate, tools release. This
  is the copy that gets corrected, and the one phases link into.

Where a strand doc has already diverged from its research source, it says so inline.
