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

**A fourth thing belongs here and is not a behaviour**: where the pinned documentation disagrees
with **itself**. One page giving a resource three different maturities, a stated field count
contradicted further down by the page's own field list, a comparison against a feature gate
deleted releases ago — none of these is a diff between the post and the pin, so none of them is a
case in the next section, where every case is a statement about the *post*. This one is a
statement about the *pin*, and it is the diff a reader trusting today's documentation actually
walks into. Cite both halves and say they disagree; do not pick a winner unless a command settles
it, and if one does, that command belongs in *Do*
([#100](https://github.com/k3ii/k8s-academy/issues/100), `blogwalk/2018/09`).

On a post that **still works** — most of them, from 2019 on — this section is one line: the post
is still true, still the default, and needs no correction. Say that and stop. Padding it is the
failure mode, and the 2024 prototype measured the collapse: 8 lines where behaviour had
changed, 2 where it had not. The section stays anyway, because the one thing a reader cannot
check for themselves is whether anybody checked.

**What this exercise does not cover, and where it lives** — an *optional* bolded paragraph
closing this section, for a post whose subject is partly owned elsewhere. Name what the exercise
gives up and where the fact already lives, then stop: a backward link if the owner is written, a
bare pointer to the year and subject if it is not, and no link at all to a forward row, because
[references point backward only](#conventions-this-tree-inherits). This is the shape that makes
*a fact lives in exactly one place* enforceable rather than aspirational, and it earns its place
by frequency — it appears in four of 2018's nine files and none of the 35 before them, because
it is a symptom of the corpus getting dense, which only continues. Skip it when nothing collides;
a paragraph saying "nothing was ceded" is padding.

**The diff, and why** — the payload, and on a modern post the section that carries the whole
exercise. It has **seven cases**, and they are **not exclusive**: an exercise names the ones that
land, and several landing in one post is a finding rather than indecision — four have landed in
one post (`blogwalk/2017/07`). Naming several is not hedging; the hedge is naming none. The first
two were ratified in [#57](https://github.com/k3ii/k8s-academy/issues/57); the third, fourth and
fifth are the failure modes the census met and the verdict vocabulary cannot name, ruled in
[#78](https://github.com/k3ii/k8s-academy/issues/78) as cases here rather than as new verdicts —
the census is closed and its 767 rows are immutable, so a fifth verdict would be a value no row
could ever carry. All three already sat in the `walk` set; what they lacked was a way to be
written. The sixth arrived the same way and by the same test: three exercises across two years
wrote the shape without a name for it, and
[#100](https://github.com/k3ii/k8s-academy/issues/100) ratified the name they had improvised. The
seventh is the first ratified on **two** instances rather than three, in
[#102](https://github.com/k3ii/k8s-academy/issues/102), because the survey that found them also
bounds the shape: the pinned tree cites 23 of the 767 posts by name from `content/en/docs`, only
four of those carry a `walk`, and two of the four are further-reading bullets. Recurrence is what
the bar was proxying for, and a measured population settles it better than a third instance.

- The post **broke**: what changed, the release it changed in, and one sentence naming the
  pressure that moved it.
- The post is **still right**: what it could not yet know, and which release settled it. This is
  the common case in the later years, and it is a diff between what the post knew and what the
  pin knows rather than a diff of behaviour.
- The post was **wrong when it was published**: the diff is a *correction*, not a translation,
  and it comes first — the reader fixes the manifest before anything else can run. Say plainly
  that the post never worked, because a reader who assumes it did will blame their cluster. Both
  instances found in the sweep are 2019 posts printing typographic quotes inside code fences
  ([#67](https://github.com/k3ii/k8s-academy/issues/67)), and both earned walks.
- The post describes a **plan the project abandoned**: there is no then-state to translate,
  because the post is not describing an old world but a future that did not happen. Name the
  forecast, quote it, and name the reversal. *Scaling Kubernetes Networking With EndpointSlices*
  says the Endpoints API "is not going away"; the pin's reference for it opens *Deprecated: this
  API is deprecated in v1.33+* ([#68](https://github.com/k3ii/k8s-academy/issues/68)).
- The post has been **overtaken by stasis**: the subject did not move, and *that* is the finding.
  A gate alpha since 1.21 with no later stage says something about the project's priorities that
  a promotion never does. This case usually has no observable failure at the lab ceiling, so the
  argument carries the whole exercise and *Do* has to be honest about what it cannot show
  ([#69](https://github.com/k3ii/k8s-academy/issues/69),
  [#73](https://github.com/k3ii/k8s-academy/issues/73)).
- The post was **retired by being agreed with**: the forecast came true, and that is *why* the
  instructions fail. The project adopted the argument so completely that the thing the post tells
  you to install stopped being a separate thing — no package, no version, no repository, no
  documentation page, because it is not an alternative any more but the default or a field. It is
  the fourth case's mirror and must not be filed under it: an abandoned plan is a forecast
  reversed, this is a forecast honoured, and the wrong verb produces an exercise that reads the
  outcome backwards. Say what the post asked for, name the release where it landed, and say what
  the reader does *instead* — because the reader's problem is that correct instructions became
  obsolete by succeeding, and no error message will ever tell them that. Ratified in
  [#100](https://github.com/k3ii/k8s-academy/issues/100) on three instances across two years
  (`blogwalk/2017/08` containerd, `2018/02` CSI at beta, `2018/07` gRPC health checking) after the
  shape recurred; a single instance stays a *Read on* question.
- The post was **never absorbed**: the feature shipped, the post is still right, and the project
  never wrote the post's content down — so the post is not a record of how the mechanism used to
  work but the pin's only copy of part of how it works now. It is the sixth case's mirror in turn:
  there the project adopted the argument so completely that the post stopped being needed, here it
  adopted the feature and left the explanation where the post put it. **Two tests, in order, and
  both are greps.** Does a pinned page cite the post *inline and load-bearing* —
  `reference/using-api/deprecation-guide.md:392` says *"Use [client warnings, metrics, and audit
  information available in 1.19+]"* and links a 2020 post — and does the post name an identifier
  that occurs **nowhere else under `content/en`**? A bullet under `## {{% heading "whatsnext" %}}`
  is **not** evidence: further reading is what a healthy page does, and two of the four cited `walk`
  posts are exactly that. **The identifier test has one false positive and `blogwalk/2019/06` is
  it**: `preserveUnknownProperties` occurs on exactly two lines of that post and nowhere else in the
  pinned checkout because the post *invented* it, misspelling in prose a field the API has never
  had. An identifier the post is alone in naming is evidence of this case only once the identifier
  is shown to be real; otherwise it is the third case, and the reader needs a correction rather than
  a source. Do not confuse this with the pin disagreeing with itself, which is a statement about the
  pin and belongs in *As it runs now*; this is a statement about the post, and what it says is that
  the post is load-bearing. It almost always lands together with *still right*, and **naming only
  *still right* is the failure it exists to prevent** — a reader told the post holds will not learn
  that it is the only thing that holds. Ratified in
  [#102](https://github.com/k3ii/k8s-academy/issues/102) on two instances, both 2020:
  `blogwalk/2020/07`, where six identifiers each occur in exactly one file in the whole of
  `content/en` and that file is the post, and `2020/09`, whose five-line fence is
  `security-context.md:383-389` byte for byte while the one reference cell covering the post's other
  half says to refer to values it does not list.

Cite [`research/blog-era-translation.md`](../research/blog-era-translation.md) rather than
re-deriving the release history. Removal releases come from the source tree at the release tag,
never from the note that announced the removal — *the announcement is not the event.* "It was
replaced" is not a why.

**The ladder**, a table inside *The diff, and why*, **required for any release-feature
exercise**. Fixed columns, so twelve years of them are comparable and greppable — and the
columns are fixed at exactly the fields the gate file carries, because **the table is a lossless
transcription of the gate file's `stages:` list, transposed, and nothing else**. Anything that is
not in that list is not in the table.

```
| stage | default | locked | releases |
|---|---|---|---|
| alpha  | `false` | —      | v1.31 – v1.32 |
| beta   | `false` | —      | v1.33 – v1.34 |
| beta   | `true`  | —      | v1.35 |
| stable | `true`  | —      | v1.36 – |
```

`stage` takes one of **four** values — `alpha`, `beta`, `stable`, `deprecated`. The fourth is not
decoration: 48 of the 487 gate files use it, and it is how the pinned tree records a feature
being taken *away*, so a ladder that only ever climbs is a misreading rather than a simplification
([#66](https://github.com/k3ii/k8s-academy/issues/66)). `default` is the stage's `defaultValue`.
`locked` is the stage's `locked` field — 49 gates set it true and 2 set it false — and it is `—`
everywhere else, which is most rows; it stays a column rather than a suffix inside `default`
because a convention buried in a code-formatted cell is what drifts across seventy files and
cannot be grepped. `releases` is `fromVersion – toVersion`, open-ended when there is no
`toVersion`, and it is **text**: two gates carry a patch-level boundary
(`MaxUnavailableStatefulSet`'s beta splits at v1.35.0–v1.35.3 / v1.35.4) and the cell simply says
so ([#70](https://github.com/k3ii/k8s-academy/issues/70)).

A repeated stage is **two rows, not a mistake**: 34 files repeat one, and what the repeat marks is
a change of `defaultValue`, not of stage. So *"X moves to Beta"* in a post title does not mean the
gate was on, and the two-row shape is exactly what makes that visible
([#71](https://github.com/k3ii/k8s-academy/issues/71)).

**File-level facts go in a sentence beneath the table, never as a row**, because they are not
stages:

- **`removed: true`** — 230 of the 487 files declare it, and it is *declared, not inferred*. Do
  not read removal off a terminal `toVersion`: the two readings disagree on
  `DynamicProvisioningScheduling`, whose `deprecated` stage never closes while the file says
  removed ([#72](https://github.com/k3ii/k8s-academy/issues/72)).
- **`former_titles:`** — exactly one file carries it, so a rename is otherwise undetectable by
  reading the tree; you find it by noticing a name has gone to zero.

**The ladder is per *gate*, not per feature.** Where an exercise's subject spans gates, it tables
each one and the prose says how they relate — the relationship *is* the argument and will not
reconcile into one monotonic table. IPVS is the case that proves it: `SupportIPVSProxyMode` runs
alpha v1.8 → beta/`false` v1.9 → beta/`true` v1.10 → stable v1.11–v1.20, `removed: true`, while
`KubeProxyIPVS` is a **different file** holding a single `deprecated` stage from **v1.37**, whose
purpose is to let you re-enable a mode being withdrawn. Read alone, the second says "deprecated
months after it appeared", which inverts the story; the dates for the withdrawal itself (disabled
by default v1.40) are in `virtual-ips.md` prose and in neither gate file.

A **release-feature exercise** is one whose subject is a single feature climbing the gate
ladder — the `"1.31: X Graduates to Beta"` genre. That is the case the required table serves.
An exercise about a *transition* rather than a promotion is not one:
[`2024/10-websocket-transition.md`](2024/10-websocket-transition.md) is about a protocol swap
whose own default switch had no ladder worth tabling, and its two-gate status table is ordinary
prose evidence, not a ladder.

### Where the ladder is read from

In this order, and never from the post, which by definition reflects only its own release:

1. **`content/en/docs/reference/command-line-tools-reference/feature-gates/<Gate>.md`**, whose
   frontmatter carries the `stages:` list. There are **487** gate files, not 488 — the extra entry
   is the directory's `index.md` — and `feature-gates-removed/` is a *generated view* of the same
   files filtered on `removed: true`, not a second store.
   **Parse the frontmatter as YAML. Do not grep it.** This is not fastidiousness: two files
   (`PreferSameTrafficDistribution`, `PreventStaticPodAPIReferences`) indent their stage list two
   spaces rather than four, `APIResponseCompression` quotes its stage value, and many carry
   trailing whitespace. A regex pass over the directory — the instrument every census used —
   miscounts `locked` gates, miscounts the self-contradicting files, and misses those two files
   entirely. Install `pyyaml` in a scratch venv for the read; this repo's own scripts stay
   stdlib-only and no parser is committed here until authoring shows it is needed
   ([#74](https://github.com/k3ii/k8s-academy/issues/74)'s lesson about throwaways that become
   load-bearing).
2. **`kubeadm-init.md`'s two tables**, for the nine gates in kubeadm's own namespace, which have
   no files under `feature-gates/` at all. They are **transposed** — one row per gate, stages as
   columns — and the two tables do not even share a column set: the active one is
   `Feature | Default | Alpha | Beta | GA | Deprecated`, the removed one
   `Feature | Alpha | Beta | GA | Removed`. Transcribe into this template's column shape and say
   which table it came from. `EtcdLearnerMode`'s complete ladder — alpha 1.27, beta 1.29, GA 1.32,
   removed 1.33 — exists only there ([#71](https://github.com/k3ii/k8s-academy/issues/71)).
3. **No gate at all** — see *No gate*, below.

Where the frontmatter and a prose page disagree, **cite both and say they disagree.** They do:
the published v1.37 announcement says Storage Version Migration graduates to stable and on by
default, while `StorageVersionMigrator.md` at the same commit stops at `beta`,
`defaultValue: false`, from v1.35 ([#73](https://github.com/k3ii/k8s-academy/issues/73)). *The
announcement is not the event* binds on the ladder, not only on removal claims.

The table is evidence, not the argument: the prose beside it has to say what the ladder means. The
example above is real, and what it means is that `ImageVolume`'s beta shipped **off by default for
two releases**, so a v1.34 cluster following a "now in beta" post gets a silent empty mount.

**No gate** — required in place of the ladder when the subject has none, and it is a named source,
not a shrug. Never synthesise a ladder out of prose; manufacturing evidence is the failure
[`research/blog-era-translation.md`](../research/blog-era-translation.md) exists to prevent. State
which instrument you used and what it disagrees with, because these cases are where the
documentation is thinnest:

- The **Metrics API** sat at beta from v1.8 to v1.36 — 29 releases, longer than any beta the gate
  directory records — and has no gate file, an aggregated API having none. Its history reads off
  the API reference, which is itself split: the only reference page is `metrics.v1beta1`, while the
  prose under `content/en/docs` writes `metrics.k8s.io/v1` nine times, `v1beta1` nine times and
  `v1beta2` four times.
- The **cgroup v1 → v2 CPU conversion change** has no gate *and no Kubernetes version*: adoption
  depends solely on the OCI runtime (runc ≥ 1.3.2, crun ≥ 1.23), so the version that matters is
  not a Kubernetes one at all ([#73](https://github.com/k3ii/k8s-academy/issues/73)).

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
- **References point backward only** — an earlier year, or a lower `NN` in the same year, never
  a later one — and a reference is a pointer, never a prerequisite. The rule and the reason are
  in [Where to start](README.md#where-to-start); this is the line that binds an author.

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
Or, if the post still works: still true, still the default, no correction needed. And where the
pin contradicts itself, both halves cited.

**What this exercise does not cover, and where it lives.** *(optional)* What is ceded, and to
which earlier exercise or which unwritten year.

**The diff, and why** — what changed and the pressure that moved it, or what the post could not
yet know and which release settled it.

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | vX.Y – vX.Z |
| beta | `true` | — | vX.Z+1 – |

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
