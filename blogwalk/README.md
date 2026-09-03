# Blogwalk — eleven years of kubernetes.io/blog as a walkable archive

767 blog posts, March 2015 to August 2026, censused one by one. Some of them are still
exercises you can run. Most of them broke, and the ones that broke are the valuable ones.

This is **supplementary**. It gates no phase; [P0–P12](../README.md) are complete without it.
It has [its own reading order](#where-to-start) and links into `phases/` nowhere.

## Where to start

**Chronologically: [2015](2015/) first, then each year in turn, exercise `01` upward inside
it.** The [twelve years](#the-twelve-years) below is the index. That order is not a preference;
it is the order the tree is already in. Exercise numbering *is* publication order, checked by
[the gate](#the-gate), and it runs the same direction as the archive's references to itself.
From 2018 on, the commonest reason a post lost its `walk` was that **an earlier year's exercise
already carries its diff** — four of 2018's largest announcements, all four of 2023's Gateway
API posts, twenty of 2025's 78 rows. The dependencies point backward in time because backward
in time is where the diffs were first walked.

Exercises **stand alone and run alone**, as in [`labs/`](../labs/), so the order is recommended
and not enforced. An exercise may point at any exercise **earlier in this spine** — an earlier
year, or a lower `NN` in the same year — and **never at a later one**; and such a pointer is
always a pointer, never a prerequisite. Nothing here waits on an exercise you have not done, so
a reader arriving in the middle can always follow a link back and will never find it unwritten.

**By topic instead.** The `topic` column of the twelve censuses is the index, and the whole
mechanism is a grep:

```sh
grep '`walk` | `api`' blogwalk/*/README.md
```

Nine of the twelve tags carry an exercise at all — `api` 28, `nodes` 23, `net` and `storage` 17,
`security` 15, `tooling` 13, `sched` 11, `obs` 10, and `etcd` exactly **1** — while `ecosystem`,
`history` and `meta` carry none, the first by the [vendor rule](#four-genres-with-a-rule-because-they-are-most-of-the-corpus)
and the other two by their nature. So this is a route over nine tags of very uneven size, one of
which is a single file, and it crosses the grain of the backward references above rather than
running with it. The rule in the paragraph above is what makes it safe to take anyway.

**Or start at [2021](2021/)**, if ten years of archaeology before your first exercise that runs
as written is too long a wait. 2021 is where the blog reorganises around the release train — the
reject rate halves to 21%, and 62% of the year's posts land in the three release months — and the
76 walks from there on are mostly release-feature exercises, where the diff is a feature gate's
graduation rather than a broken command. The door is real and this file will not pretend
otherwise. But taking it costs you the argument the whole tree is built on: **a post that still
works teaches you 2015; a post that broke teaches you what changed and why.** The ones that broke
are the valuable ones, and at that entrance nearly all of them are behind you.

## The pin

The corpus is `kubernetes/website` at
**[`7c76070faf9b19e6a417c446043dbafd10a7aa1d`](https://github.com/kubernetes/website/commit/7c76070faf9b19e6a417c446043dbafd10a7aa1d)**
(2026-08-26), frozen for the whole sweep. The newest Kubernetes at that pin is **v1.37
"Garhwal"**, released on the pin date itself. "767 posts" is a true number only against a
commit, and a census gate that reads a moving target is red every Monday for reasons that
have nothing to do with the census.

Re-create it:

```sh
git init website && cd website
git remote add origin https://github.com/kubernetes/website.git
git sparse-checkout init --cone
git sparse-checkout set content/en/blog/_posts content/en/docs content/en/examples
git fetch --depth 1 origin 7c76070faf9b19e6a417c446043dbafd10a7aa1d
git checkout FETCH_HEAD
```

The census itself reads only `_posts`. The other two paths are in the checkout because the
exercises measure the pinned documentation and example trees against the posts, and an exercise
that cites a `file:line` is citing that commit.

Then, from the root of this repo:

```sh
python3 blogwalk/build-manifest.py <path-to-website>/content/en/blog/_posts
```

That regenerates [`manifest.tsv`](manifest.tsv) — one row per post, the worklist every census
row is checked back to — and asserts all twelve per-year counts on the way. If the assertion
fires, the pin moved; the manifest did not drift quietly.

**A post is any file under `_posts` whose frontmatter carries a `title`.** Not any file ending
`.md`: two published posts have no extension at all and take their slug from their title, one
opens with a UTF-8 BOM, two open with a blank line, one opens with six dashes. 130 posts are
page bundles at `<slug>/index.md`, over half of 2024–2025, so a glob of `<year>/*.md` silently
misses them. **`path` is the key, not `slug`** — 19 rows collide on 12 slugs, six of them on
`weekly-kubernetes-community-hangout` inside 2015 alone.

Of the 767, **756 are published**; 11 are `draft: true`, the v1.37 feature-blog queue, still
unpublished at the pin because v1.37 shipped that day. They carry a `draft` column rather than
a deletion.

**A post's URL is resolved, not derived**, which is why the manifest carries a `url` column and
why no census may build a link by hand. Only 552 posts take the site-wide permalink from
`hugo.toml`, `/:section/:year/:month/:day/:slug/`. **205 carry a per-post `url:` override in
the month-only form** — all of 2015, 2016 and 2017, twelve of 2018, six of 2020 — and eleven of
those are hand-written literal paths whose capitalisation is not the slug's, so
`weekly-kubernetes-community-hangout` is served at
`/blog/2015/03/Weekly-Kubernetes-Community-Hangout/`. Ten of the eleven drafts are undated, so
nothing resolves for them and their `url` is empty; the eleventh is dated, so a permalink does
resolve and the manifest records one the site answers with 404. 757 URLs, no collisions. Hugo's precedence — per-post override first,
site template second, literal used as written — is implemented once in
[`build-manifest.py`](build-manifest.py) and nowhere else.

**2026 is partial as of the pin** (70 posts, to 2026-08). Refreshing to a later pin is a
separate, cheap job once the census exists: it is a diff against a file listing.

## Then → Now: what an exercise here actually is

Nothing from 2015 runs as written. v1beta3, ReplicationControllers, no RBAC, `createExternalLoadBalancer`, Kubernetes 0.15. So an exercise does the post's **intent** on a modern cluster,
and the payload is the diff and the argument behind it. `strong-simple-ssl-for-kubernetes`
becomes cert rotation. `introducing-kubernetes-v1beta3` becomes why the API is versioned at
all. RC → Deployment is a live argument about who owns a rollout.

This inverts the problem: **a post that still works teaches you its own year; a post that
broke teaches you what changed and why.** It is the move
[`strands/source-archaeology.md`](../strands/source-archaeology.md) makes for file paths —
*a path move is usually a design decision leaving a trace* — applied to prose instead of paths.

The release history each exercise argues from is
[`research/blog-era-translation.md`](../research/blog-era-translation.md): 198 rows of *what
the post says / what is true at the pin / changed in / the decision behind it*. Exercises cite
it rather than re-deriving eleven years of releases and each getting it slightly differently.

**One warning that record earns, restated here because every exercise depends on it:**
Kubernetes' own CHANGELOGs and deprecation notices misstate their own removals, in both
directions. The dockershim removal was announced for 1.22 and landed in 1.24. `CHANGELOG-1.28`
announces the `azureFile` removal that was reverted and actually happened in v1.30.
`kubectl run-container` was announced dead in v1.8 and died in v1.13. So no exercise may
source a removal release from the note that announced it — only from the source tree at the
release tag. **The announcement is not the event.**

## The census

Every post gets a row. All eleven of 2015's weekly-hangout notes, every launch party, every
video roundup. A census that silently drops the noise is indistinguishable from one that
*missed* it, and a reject costs one clause.

Rows live in `YYYY/README.md`, one file per year. The table shape is **frozen** so that twelve
years of them concatenate without editing:

```
| post | date | k8s | verdict | topic | why |
|---|---|---|---|---|---|
```

`post` is the post's title, linked to its live URL, taken **verbatim from `manifest.tsv`'s
`url` column** and never assembled by hand — see [the pin](#the-pin) for why that column
exists. `date` is `MM-DD`; the year is the file. `k8s` is the version the post targets, or `—`
where it predates versioned releases. A row's link never changes once written, which is what
lets a census pass emit its table and never revisit it; the exercise file is linked from the
year's **Exercises** table instead, alongside its `written`/`pending` state.

**An unpublished draft still gets a row.** The eleven `draft: true` posts — 2026 only, the
v1.37 queue — are post files at the pin, and *every post gets a row* does not carve out the ones
the pin caught mid-flight. Their `post` cell carries the title unlinked followed by `(draft)`,
and the row is verdict-eligible like any other. **`draft: true` is what decides that, not
whether a URL resolved** (ratified in #73): ten of the eleven are undated and resolve to no
permalink, but the eleventh carries a date, so the template resolves a URL for it that the site
returns 404 for. An unlinked row is the honest one. Ten of the eleven also carry no publication
date, so they sort last — in the manifest and in the census — and the exercise numbering counts
them last too. The reason to keep them is that the pin will move: when they publish, their rows
are already written and the refresh is a link, not a census.

Verdicts:

| verdict | means |
|---|---|
| `walk` | earns an exercise file |
| `read` | worth reading, nothing to do — a concept or an argument that outlived its commands, or a technique another exercise already carries |
| `dated` | *was* hands-on and would still be, but it does not fit the lab — hardware or scale beyond the [9.5GB ceiling](../strands/lab-topologies.md#ceiling) |
| `skip` | no learning content — hangouts, launch parties, video roundups, recruiting, pure PR |

`dated` is deliberately the narrowest verdict, and the only one that says *the lab is why, not
the post*. It takes **two** tests, both of which must hold:

1. The post is itself a **walkthrough** — something a reader could follow end to end on bigger
   hardware.
2. What it needs is beyond the [9.5GB ceiling](../strands/lab-topologies.md#ceiling).

The second test alone is not enough, and this is the correction the 2024 census forced. Eleven
of that year's `read` rows also fail on the lab — they want a CSI driver implementing
`ModifyVolume`, or snapshots, or group snapshots; a real OIDC issuer; CRI-O instead of
containerd; Windows nodes; NUMA or SMT topology; load a 4-vCPU guest cannot generate. None of
them is a walkthrough. They are announcements with a snippet, so they are `read`: there is
nothing to walk even on a bigger machine. Without test 1, `dated` swallows a third of every
modern year and stops distinguishing anything.

A post whose technique is real but redundant, or whose tool is abandoned, is likewise a `read` —
worth your eyes, not your cluster. Across the first two years censused, `dated` is **5 rows in
98**. That is the right size for it.

Topic, from a **fixed vocabulary of twelve**: `api` `sched` `net` `storage` `security` `nodes`
`etcd` `obs` `tooling` `ecosystem` `history` `meta`. `obs` is monitoring, logging, metrics and
tracing — posts about *seeing* the cluster, which otherwise scatter across the subsystem each
one happens to instrument.

Two years of real triage, 98 posts, settled three things about this list:

**`meta` is the reject tag, and it is about a third of every year.** Measured: 35 of 98. It is
not one thing — it is hangout minutes, maintainer interviews, release announcements, and
promo. It stays one tag anyway, because a topic tag exists to answer *"show me everything about
storage across eleven years"*, and that query is only ever run against `walk` and `read` rows.
Splitting `meta` would buy three tags that appear almost exclusively on `skip` rows: cost, no
query.

**A topic earning zero rows in a year is expected**, not evidence against the slot. `obs`
matched four posts in 2015 and none in 2024 — the blog stopped covering observability *as*
observability and scattered it into whichever subsystem is being instrumented. `sched` at 2
rows and `etcd` at 1 are not underused tags either; they are a 13% sample that happens to miss
the years those subsystems got their attention. Twelve slots exist to make twelve years
greppable, not to be evenly filled.

**No tag went unused.** Every one of the twelve earned at least one row across the two eras,
which is the evidence that the list is neither too fine nor too coarse.

### Four genres with a rule, because they are most of the corpus

**Vendor and ecosystem posts** — `skip` unless the post documents a decision *and* the
alternatives it rejected; then `read`. Never `walk`. The test is answerable from the first
screen, which is all the triage budget allows, and the bar on `walk` is the important half: an
exercise that depends on a company staying in business is an exercise with an expiry date.

**Weekly hangout notes** — `skip`, as a class, all of them, in every year. Minutes carry a
*trace* of an argument, not the argument; an exercise built on a trace has to supply the
reasoning itself, at which point the note is a citation rather than a source.

Seeds are not lost by this: the row's `why` column names the seed, which is what makes it
findable later. 2015's minutes record the `kubectl exec` demo entered via `nsenter`, and
"treating rcs as pets vs. cattle" — the argument that produced the Deployment object — and both
are written into their rows. Neither year has an exercise to footnote them in yet; when one is
written, in any year, the note becomes its citation. A seed with no exercise to serve is still
not a reason to promote the note.

**Beta-graduation posts** — the `"Kubernetes 1.31: X Graduates to Beta"` genre, 22 of 2024's
54 posts and the majority of every year from 2019 on. `walk` iff **either**:

- the feature's ladder has a **discontinuity** — a beta that shipped off by default, a withdrawn
  alpha, a permission that moved, a field that was renamed — **or**
- the failure the feature fixes is **observable in the lab**.

Otherwise `read`. A feature that marched alpha → beta → GA with nothing surprising in it has
nothing an exercise can teach that the reference docs do not already say better.

The discontinuity clause is first because it is the clause that makes this archive worth
having. A post that was right and stayed right teaches you its own year. A post that was right
and then got quietly overtaken is the whole thesis — and the ladder is where you see it, which
is why every exercise in this genre builds the ladder table the
[template](TEMPLATE.md) specifies, out of the pinned docs' feature-gate frontmatter rather than
out of the post.

**Maintainer interviews** — the *Spotlight on SIG X* genre, 9 of 2024's 54. `read` when the
interviewee **owns code**, `skip` otherwise. The hangout-note rule above does not transfer:
minutes are a trace *because nobody was explaining*, whereas an interview is a maintainer
explaining a decision on the record, which is a source. "Owns code" is answerable from the
title — a technical SIG on one side, a book club or a working group on the other. Never `walk`:
an interview has no commands in it.

**Release announcements** — `skip` unless a specific line in the post is load-bearing for an
exercise elsewhere; then `read`, and the `why` column names that line. This keeps the verdict
earned against a fact instead of awarded to a genre — which matters most in the later years,
where this genre is the majority of the corpus. Either way a release post is evidence of an
**announcement, never of an event**: version numbers in an exercise come from the source tree
at the release tag. See [`research/blog-era-translation.md`](../research/blog-era-translation.md)
for why that distinction is not pedantry.

Triage is **title + frontmatter + first screen**. The corpus is **7.22MB of post markdown,
roughly 2.0M tokens** — summed from `manifest.tsv`'s `bytes` column, so it moves only when the
pin does. It cannot be read in full by anyone, ever. Full reads are spent on `walk` candidates
only.

A first-screen digest of a whole year costs between a sixth and a tenth of reading that year
end-to-end. Measured across the whole corpus by [`digest.py`](digest.py) — one instrument, one
900-character cut, so the years are comparable with each other:

| year | posts | source | digest | cost of a digest |
|---|---|---|---|---|
| 2015 | 44 | 292KB | 47KB | **16%** |
| 2016 | 90 | 681KB | 100KB | **15%** |
| 2017 | 53 | 460KB | 58KB | **13%** |
| 2018 | 70 | 714KB | 76KB | **11%** |
| 2019 | 52 | 551KB | 57KB | **10%** |
| 2020 | 56 | 587KB | 61KB | **10%** |
| 2021 | 53 | 582KB | 58KB | **10%** |
| 2022 | 69 | 638KB | 75KB | **12%** |
| 2023 | 78 | 709KB | 85KB | **12%** |
| 2024 | 54 | 568KB | 59KB | **10%** |
| 2025 | 78 | 777KB | 85KB | **11%** |
| 2026 | 70 | 832KB | 76KB | **9%** |

Whole corpus: 767 posts, **7.22MB of source, 837KB of digest, 11%** — the same 7.22MB
the paragraph above counts, because the script reads its source sizes from `manifest.tsv`
rather than measuring them a second time. The estimate the sweep was budgeted against —
579 posts and 5.71MB left after the first three passes, digesting to **631KB at 11%** — held
to the end: every remaining year fitted one pass, and the last and cheapest, 2026, came in
at 9%.

The ratio drifts down because the cut is a constant and the posts are not — a 2026 post averages
1.8× the length of a 2015 one, so a fixed first screen is a smaller slice of it. That is
arithmetic about the instrument, not a finding about the blog. The finding about the blog is a
different one, and it concerns triage *quality* rather than cost: the modern genre is fixed —
*what it was, what it is now, which gate, how to try it* — so a later post's first screen
predicts the rest of it far better than an early post's does. The census is still cut one year
per pass rather than two, for the file-shape reason rather than the cost one — see
[the twelve years](#the-twelve-years).

## Known defects in the rubric

Five defects the twelve passes found in the rules above. All five are **flagged and not
applied**, and that is a ruling rather than a backlog: each of them binds on *verdicts*, verdicts
are immutable under [#57](https://github.com/k3ii/k8s-academy/issues/57), and the only sitting
that could act on them is a re-pin, which [#52](https://github.com/k3ii/k8s-academy/issues/52)
puts out of scope. They are written down because a reader who finds one of them for themselves
should find it already named, not think the sweep missed it. Ruled in
[#78](https://github.com/k3ii/k8s-academy/issues/78).

The first four are rubric questions — the rules would need rewriting before a verdict could
change:

- **`ecosystem` and `tooling` are not distinguished anywhere, and the boundary decides
  eligibility**, because the vendor rule bars an `ecosystem` post from `walk`. Filing Helm as a
  project's tool rather than a company's product is what let *Helm Charts* take an exercise. The
  case that shows the seam is Stern, whose company died and whose tool outlived it.
  ([#64](https://github.com/k3ii/k8s-academy/issues/64))
- **The rules are ordered and nothing says in what order.** `dated` requires a walkthrough, and
  the vendor rule reaches its candidates first; applied in that order it cost `dated` its only row
  in both 2017 and 2021. Reverse the two and those years read differently.
  ([#65](https://github.com/k3ii/k8s-academy/issues/65),
  [#69](https://github.com/k3ii/k8s-academy/issues/69))
- **The release-announcement rule's "load-bearing line" escape hatch cannot fire on a version
  fact**, because [#54](https://github.com/k3ii/k8s-academy/issues/54) forbids sourcing a version
  from an announcement. In practice the genre has collapsed to a class-wide `skip`, and the rule
  should say so rather than describe an exception that cannot be taken.
  ([#65](https://github.com/k3ii/k8s-academy/issues/65))
- **The maintainer-interview rule tests *owns code*, where the test actually applied was *process
  versus engineering*.** SIG Node's spotlight interviewees own the kubelet and the post is pure
  process, so the written rule and the applied rule disagree on the exact case the rule exists
  for. ([#66](https://github.com/k3ii/k8s-academy/issues/66),
  [#69](https://github.com/k3ii/k8s-academy/issues/69),
  [#73](https://github.com/k3ii/k8s-academy/issues/73))

The fifth is not a rubric question. It is a **reader-visible defect in a shipped artifact**:

- **The spotlight rule was applied inconsistently across five years.** 2024 and 2026 follow what
  is written; 2020, 2021, 2022, 2023 and 2025 skipped every spotlight they met. So two
  spotlight posts of comparable substance can carry different verdicts for no reason a reader can
  recover from the rules, and the census file is where they will meet it. Recorded here rather
  than repaired, on the same immutability rule as the four above.
  ([#73](https://github.com/k3ii/k8s-academy/issues/73))

## The budget

**8–15 `walk` verdicts per year** — roughly 100–180 exercises against [`labs/`](../labs/)'s 357.
No hard cap. Each year's README states what it spent, and a year outside the band argues for
itself in one line.

It was a **budget, not a yield**, and all twelve years have now spent it: **135 `walk` across
767 rows**. Both ends were reached — the floor of 8 in 2017 and 2019, the ceiling of 15 in 2016
— and in twelve passes the band **never once cut a post the rubric would otherwise have kept**.
Every low year was low because its posts were release notes; every high year was high because
its posts were walkthroughs. So the band described the corpus for twelve years and never
disciplined it. The `walk` set is closed, which means it now binds on nothing: what follows is
a premise the authoring passes inherit, not an open question.

The band is deliberately **not** re-cut per era or per release. Its whole function is friction
against a rubric that will drift generous over twelve passes, and a band that flexes with the
year's density stops being friction.

## The twelve years

Twelve census passes, one per year, all closed. Each row links that year's full census; the
`walks` column is what the year owes in exercise files, and the last is what the year *is* —
which is how to choose an entrance if [chronological](#where-to-start) is not what you want.

| year | posts | walks | what the year is |
|---|---|---|---|
| [2015](2015/) | 44 | 10 | Nothing runs as written. No RBAC, no Deployment, no kubeadm, no CRI, and `kubectl apply` does not exist yet |
| [2016](2016/) | 90 | 15 | The largest year, and the one whose nouns all still exist meaning something else — PetSet arrives and is renamed StatefulSet nine months later |
| [2017](2017/) | 53 | 8 | The security defaults move: RBAC beta in 1.6 and GA in 1.8, NetworkPolicy stable in 1.7, containerd a real option under CRI |
| [2018](2018/) | 70 | 9 | The storage stack rebuilt in public — CSI runs alpha, beta and GA inside twelve months |
| [2019](2019/) | 52 | 8 | Where the archive starts going wrong in a new way: posts that were broken on the day they were published |
| [2020](2020/) | 56 | 9 | Where it starts arguing with itself — a post promising an API "is not going away" that the pin marks deprecated |
| [2021](2021/) | 53 | 11 | The blog reorganises around the release train. The genre changes here, and this is the [second entrance](#where-to-start) |
| [2022](2022/) | 69 | 13 | The year that proves the ladder is not one-way — three of its alphas are replaced rather than promoted, and their gate ladders restart |
| [2023](2023/) | 78 | 13 | The most evenly spread year in the archive, and the one that found a second feature-gate registry inside kubeadm's own docs |
| [2024](2024/) | 54 | 13 | Almost everything still runs, which is the opposite problem — the diff is a gate's graduation, not a broken command |
| [2025](2025/) | 78 | 12 | The first year whose largest topic is the software rather than the project; 63% of its titles name a version |
| [2026](2026/) | 70 | 14 | Two-thirds of a year — the pin cuts it at 2026-08-26 — and eleven of its rows are unpublished drafts |

**A pass is one year because a census file is one year.** The map originally cut these as five
two-year eras of 109–148 posts, and the prototypes proved that wrong by censusing 44 and 54: an
era is 2.0–2.7× anything anyone had run, and a pass that runs out of room at post 110 of 147
leaves a half-filled `YYYY/README.md` in a state no other pass can pick up. Cutting by post
count instead was rejected for the same reason — it puts a file boundary inside a pass. Whoever
[refreshes the pin](#the-pin) inherits that constraint, and a thirteenth year with it.

**Authoring progress is not recorded here.** It lives in each year's `## Exercises` table, one
`written` or `pending` per row, which is the copy [the gate](#the-gate) checks against the files
on disk in both directions — so the gate's own run is where you read how far along the tree is.
A second table in this file would be a copy nothing checks.

## The one link out

Exercises cite [`strands/lab-topologies.md`](../strands/lab-topologies.md) for topologies and
for provision and teardown steps, rather than restating them. That is the *only* coupling in
either direction. Duplicating the [9.5GB ceiling](../strands/lab-topologies.md#ceiling) into a
second tree is how you end up with two contradictory answers to "how much RAM do I have".

[`strands/check-anchors.py`](../strands/check-anchors.py) is not extended to this tree.
`blogwalk/check-census.py` is this sweep's only gate, and it checks census rows
against `manifest.tsv`.

## The gate

```
python3 blogwalk/check-census.py
```

Run it from the repo root before closing a census pass. It is the sibling of
[`strands/check-anchors.py`](../strands/check-anchors.py) — same invocation style, same exit
codes, green in **both** directions — and it exists because at 767 rows, *swept* and *feels
swept* are indistinguishable by eye.

`manifest.tsv` is the authority. Every row is matched back to a manifest row, so a post nobody
censused and a row for a post that does not exist are equally loud, and the match is on the
**`url` column byte-for-byte** — a case-only difference in one of the eleven literal
permalinks fails. It also reads the four verdicts, the twelve topics and the budget band out
of *this file*, so the rubric lives here and not in a second copy inside the checker; if it
cannot parse them it fails rather than checking nothing.

It reports **authoring progress and does not judge it**: the per-year table carries `written`
and `pending` beside `walk`, counted from each year's `## Exercises` table — the same cells
classes 3 and 4 already cross-check against the files on disk — and a closing line states how
many of the 135 exercises exist. Nothing here fails because an exercise is unwritten, on the
same reasoning as the pending year below; but the map's authoring condition, *every `walk`
verdict has its exercise file*, is visible from nowhere else, so the gate says it outright
rather than leaving the last authoring pass to work out that it was the last one.

**An uncensused year is *pending*, not broken.** The gate was green with ten years still to
sweep, which is what made it usable as a gate while the sweep ran, and it is green now with
none left. Read the per-year
table it prints: `posts` comes from the manifest, `rows` from the census, and a year whose
`walk` count leaves the [budget](#the-budget) is flagged on the run rather than on inspection.

The one judgement it cannot make is `dated`. That verdict takes two tests and only the second
— beyond the [9.5GB ceiling](../strands/lab-topologies.md#ceiling) — is mechanically visible
at all, so a `dated` row whose *why* cites no hardware and no scale is reported as a
**warning**: it asks a human to look, and does not decide.

## Layout

```
blogwalk/README.md          this file — method
blogwalk/TEMPLATE.md        the exercise template, forked from labs/
blogwalk/manifest.tsv       one row per post at the pin
blogwalk/build-manifest.py  regenerates the manifest, asserts the counts
blogwalk/check-census.py    the gate — run it before closing any census pass
blogwalk/digest.py          builds a year's triage digest; the reading budget, made mechanical
blogwalk/YYYY/README.md     that year's full census
blogwalk/YYYY/NN-slug.md    one exercise per `walk` post, numbered in publication order
```
