# Strands

This directory holds the cross-cutting material that several phases consume. A phase file
links into a strand doc, and it never restates the content of that doc. If a fact appears in
both places, then the phase file is wrong, and the phase file is what gets edited.

| Doc | What phases link into it for |
|---|---|
| [`source-reading.md`](source-reading.md) | The k/k, etcd, CNI, CSI and KEP corpus, per depth area. Each item has an entry point and a difficulty marker. |
| [`talks.md`](talks.md) | The 73 verified conference talks, per topic, with exact runtimes. |
| [`chaos.md`](chaos.md) | Which fault to inject, with which tool, by which Linux primitive. It also names the faults that no tool can express. |
| [`certs.md`](certs.md) | CKAD, CKA and CKS domain weights, exam mechanics, practice-resource verdicts, and speed tactics. |
| [`build-mechanics.md`](build-mechanics.md) | How the eleven build-track artifacts are compiled, shipped, identified, sized and gated. |
| [`lab-topologies.md`](lab-topologies.md) | The nine named guest layouts, at per-node resolution, with their addresses. It also says how one is provisioned, reached and torn down. |
| [`source-archaeology.md`](source-archaeology.md) | How to date a path that has moved, and the six refactors that make older third-party material wrong. |

<a id="anchors"></a>
## Anchors are the contract

**Every link target in these documents is an explicit `<a id="...">` tag. It is never a
heading-derived slug.** Phase files link to those ids. You can then reword, retitle or demote
a heading without silently breaking a link. The ids are also greppable:

```sh
grep -rn '<a id=' strands/          # every anchor this repo publishes
grep -rno 'strands/[a-z-]*\.md#[a-z0-9-]*' phases/   # every anchor consumed
python3 strands/check-anchors.py    # both sides, cross-checked; non-zero on a break
```

[`check-anchors.py`](check-anchors.py) is the enforceable form of this section. It fails on
three things: a duplicate id, the same id published by two different docs, and any link to a
file or anchor that does not exist. It checks the links in `strands/`, in `phases/` and in
`labs/`. **It checks same-file `](#id)` links as well.**

Same-file links were not checked until [#35](https://github.com/k3ii/k8s-academy/issues/35).
Here is what went wrong. The link pattern required a `.md`, so a heading slug written
same-file was neither resolved nor rejected. Sixty-six of them had accumulated across the
phase files. They worked on GitHub that day, and each one died silently the first time that a
section was renumbered.

The script also enforces **coverage**, and coverage is this section's standard one level up.
Link integrity says that every link resolves. It says nothing about a module that quietly got
no exercise. So the script requires two more things:

- Every `### Module N.N` in a phase file must carry a `**Labs**` line into its `labs/NN/`. If
  the module is reading-only, then it must declare that with a line-start bolded `**No lab`.
- Every exercise file must be linked from its phase **and** listed in `labs/NN/README.md`.

Both, and not either. The phase link is what routes a learner to the exercise. The index is
what makes the directory readable on its own. A phase whose `labs/NN/` does not exist yet is
reported as *pending*, and not as broken. That is the same word that this script already uses
for a phase file that is linked but unwritten.

Heading slugs were rejected because GitHub's slugger is not the obvious function. `## Area 6 —
Storage` slugs to `area-6--storage`, and not to `area-6-storage`. The em dash is deleted, and
the two spaces around it become two hyphens. The first phase file drafted had already written
`#area-6-storage`, and it would have shipped a dead link. Explicit ids remove the class of
bug, rather than the instance.

**Adding an anchor is free. Renaming or removing one is a breaking change.** Grep `phases/`
first, and change both sides in the same commit.

<a id="provenance"></a>
## Provenance

Each strand doc names the file in [`../research/`](../research/) that it derives from. The
distinction is lifecycle, and not content:

- **`research/` is the dated record.** It says what was verified, against which tree, on
  which date, and by which method. It also says what could *not* be verified. It is not
  edited to stay current, and a stale research doc is still an accurate record.
- **`strands/` is the living form.** Paths move, KEPs graduate, and tools release. This is the
  copy that gets corrected, and it is the copy that phases link into.

Where a strand doc has already diverged from its research source, it says so inline.
