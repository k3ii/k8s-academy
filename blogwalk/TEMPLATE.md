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

Ratified in [#57](https://github.com/k3ii/k8s-academy/issues/57) against both prototypes:

```
Post → As written → As it runs now → The diff, and why → [The ladder]
     → Topology → Do → Expect → [Read on] → Teardown
```

Bracketed sections are conditional: *The ladder* and *Read on* are both **required** for a
release-feature exercise and optional otherwise. Everything else is mandatory in every file.


**Filename** `NN-slug.md`, where `slug` is the post's slug from
[`manifest.tsv`](manifest.tsv) and `NN` numbers the year's `walk` posts in publication order —
so the numbers are contiguous and the gaps between them are the year's rejects.

**`<a id="slug">`** on line 1, matching the filename, so the year README can link into it.

**`# Title`** — the exercise's own title, an assertion in the present tense, not the post's
title. The post's title is in the next line and repeating it wastes the only line a reader
always reads.

**Post** — a link to the post on kubernetes.io, its date, and the Kubernetes version it
targets. The URL is copied **verbatim from `manifest.tsv`'s `url` column** and never assembled
from year, month, day and slug: 205 posts override the site-wide permalink, eleven of them with
a capitalisation the slug does not carry. The version is the thing that makes the rest of the file legible: *"v0.15, three
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

On a post that **still works** — most of them, from 2019 on — this section is one line: the post
is still true, still the default, and needs no correction. Say that and stop. Padding it is the
failure mode, and the 2024 prototype measured the collapse: 8 lines where behaviour had
changed, 2 where it had not. The section stays anyway, because the one thing a reader cannot
check for themselves is whether anybody checked.

**The diff, and why** — the payload, and on a modern post the section that carries the whole
exercise. It has two cases:

- The post **broke**: what changed, the release it changed in, and one sentence naming the
  pressure that moved it.
- The post is **still right**: what it could not yet know, and which release settled it. This is
  the common case in the later years, and it is a diff between what the post knew and what the
  pin knows rather than a diff of behaviour.

Cite [`research/blog-era-translation.md`](../research/blog-era-translation.md) rather than
re-deriving the release history. Removal releases come from the source tree at the release tag,
never from the note that announced the removal — *the announcement is not the event.* "It was
replaced" is not a why.

**The ladder**, a table inside *The diff, and why*, **required for any release-feature
exercise**. Fixed columns, so twelve years of them are comparable and greppable:

```
| stage | default | releases |
|---|---|---|
| alpha  | `false` | v1.31 – v1.32 |
| beta   | `false` | v1.33 – v1.34 |
| beta   | `true`  | v1.35 |
| stable | `true`  | v1.36 – |
```

A **release-feature exercise** is one whose subject is a single feature climbing the gate
ladder — the `"1.31: X Graduates to Beta"` genre. That is the case the required table serves.
An exercise about a *transition* rather than a promotion is not one:
[`2024/10-websocket-transition.md`](2024/10-websocket-transition.md) is about a protocol swap
whose own default switch had no ladder worth tabling, and its two-gate status table is ordinary
prose evidence, not a ladder. If the exercise has one gate and one feature, the ladder is
required; if it has several, table them however the argument needs.

Read it out of the pinned docs at
`content/en/docs/reference/command-line-tools-reference/feature-gates/<Gate>.md`, whose
frontmatter carries the full `stages:` ladder — never paraphrased from the post, which by
definition reflects only its own release. The table is evidence, not the argument: the prose beside
it has to say what the ladder means. The example above is real, and what it means is that
`ImageVolume`'s beta shipped **off by default for two releases**, so a v1.34 cluster following a
"now in beta" post gets a silent empty mount.

**Topology** — a link to a [`strands/lab-topologies.md`](../strands/lab-topologies.md) anchor
and the provision steps, never a restated footprint. This is blogwalk's only link out of the
tree; do not add a second.

**Do** — numbered steps, imperative, on a modern cluster. Where it is cheap, have the reader
apply the 2015 manifest *first* and watch it fail, then fix it. The failure is the exercise;
being told about the failure is not.

**Expect** — what the terminal should say, precisely enough that a reader who gets something
else has learned something rather than gotten stuck. Name the error string when there is one.

**Read on** — the KEP, the design proposal, or the commit that settled the argument, each with
a question to answer from it. Never a bare link. Optional in general; **required for a
release-feature exercise**, where the KEP is always the source that settled it.

**Teardown** — always present, always last. Says whether the cluster stays up for the next
exercise or goes away.

## Conventions this tree inherits

- No bare source-reading links: every source pointer carries a question, so reading has a
  target.
- The words *understand* and *know* appear in no objective, step or expectation. Everything is
  a command, an output, or a claim that could be publicly wrong.
- A fact lives in exactly one place. The pin, the verdicts and the budget live in
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
Or, if the post still works: still true, still the default, no correction needed.

**The diff, and why** — what changed and the pressure that moved it, or what the post could not
yet know and which release settled it.

| stage | default | releases |
|---|---|---|
| alpha | `false` | vX.Y – vX.Z |
| beta | `true` | vX.Z+1 – |

**Topology** — [`name`](../../strands/lab-topologies.md#name), fresh. Bring it up with
[the five provision steps](../../strands/lab-topologies.md#provision), substituting
`topology=name`.

**Do**

1. ...

**Expect** — the output, named precisely.

**Read on** — [KEP-NNNN](https://github.com/kubernetes/enhancements/tree/master/keps/...): the
question to answer from it.

**Teardown** — what happens to the cluster.
```
