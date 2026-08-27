# The blogwalk exercise template

Forked from [`labs/`](../labs/00/), not reused. `labs/` stays untouched.

The two spines are different and bending one into the other loses the point:

| | spine |
|---|---|
| `labs/NN/` | **Claim → test it.** One sentence that could be publicly wrong, then the commands that settle it. |
| `blogwalk/YYYY/` | **Then → Now → Why.** What the post told you to type, what happens if you type it today, and the decision that moved it. |

A `labs/` exercise rests on a phase module and feeds a gate. A blogwalk exercise rests on a
**post**, and what it feeds is the argument in *The diff, and why* — which is the section
everything else exists to set up. If a draft's diff section is thin, the post was a `read` or a
`dated` and the census row was wrong.

## Sections, in order

**Filename** `NN-slug.md`, where `slug` is the post's slug from
[`manifest.tsv`](manifest.tsv) and `NN` numbers the year's `walk` posts in publication order —
so the numbers are contiguous and the gaps between them are the year's rejects.

**`<a id="slug">`** on line 1, matching the filename, so the year README can link into it.

**`# Title`** — the exercise's own title, an assertion in the present tense, not the post's
title. The post's title is in the next line and repeating it wastes the only line a reader
always reads.

**Post** — a link to the post on kubernetes.io, its date, and the Kubernetes version it
targets. The version is the thing that makes the rest of the file legible: *"v0.15, three
months before 1.0"* tells you how much to expect to break.

**As written** — what the post actually tells you to do, in its own idiom, quoted closely
enough that the reader can see the era. Fenced, if it was fenced. This section does **not**
apologise for the post or foreshadow the breakage; the whole exercise turns on the reader
believing the post first.

**As it runs now** — what happens when you do that today, stated concretely enough to be
checkable: which command errors, which one succeeds and does nothing, which field is still
accepted by the API and fails an hour later on a node. **Distinguish these three**, because
they are the entire difficulty of reading old Kubernetes documentation, and only the first
one is honest with you.

**The diff, and why** — the payload. What changed, the release it changed in, and one sentence
naming the pressure that moved it. Cite
[`research/blog-era-translation.md`](../research/blog-era-translation.md) rather than
re-deriving the release history. Removal releases come from the source tree at the release tag,
never from the note that announced the removal — *the announcement is not the event.* "It was
replaced" is not a why.

**Topology** — a link to a [`strands/lab-topologies.md`](../strands/lab-topologies.md) anchor
and the provision steps, never a restated footprint. This is blogwalk's only link out of the
tree; do not add a second.

**Do** — numbered steps, imperative, on a modern cluster. Where it is cheap, have the reader
apply the 2015 manifest *first* and watch it fail, then fix it. The failure is the exercise;
being told about the failure is not.

**Expect** — what the terminal should say, precisely enough that a reader who gets something
else has learned something rather than gotten stuck. Name the error string when there is one.

**Teardown** — always present, always last. Says whether the cluster stays up for the next
exercise or goes away.

Optional, when the post earns it:

**Read on** — the KEP, the design proposal, or the commit that settled the argument, each with
a question to answer from it. Never a bare link.

## Conventions this tree inherits

- No bare source-reading links: every source pointer carries a question, so reading has a
  target.
- The words *understand* and *know* appear in no objective, step or expectation. Everything is
  a command, an output, or a claim that could be publicly wrong.
- A fact lives in exactly one place. The pin, the verdicts and the yield band live in
  [`README.md`](README.md); the release history lives in
  [`research/blog-era-translation.md`](../research/blog-era-translation.md); an exercise file
  restates neither.

Paths in the skeleton below are written from inside a year directory — `../../strands/...`,
`../../research/...` — because that is where the copy lands. They do not resolve from this file.

## Skeleton

```markdown
<a id="the-post-slug"></a>
# An assertion, in the present tense

**Post** — [Title of the post](https://kubernetes.io/blog/YYYY/MM/the-post-slug/), YYYY-MM-DD,
Kubernetes vX.Y.

**As written** — what the post tells you to do, in its own idiom.

**As it runs now** — what happens today: errors, silent no-ops, and late failures, told apart.

**The diff, and why** — what changed, the release, and the pressure that moved it.

**Topology** — [`name`](../../strands/lab-topologies.md#name), fresh. Bring it up with
[the five provision steps](../../strands/lab-topologies.md#provision), substituting
`topology=name`.

**Do**

1. ...

**Expect** — the output, named precisely.

**Teardown** — what happens to the cluster.
```
