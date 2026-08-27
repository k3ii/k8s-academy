# Blogwalk — eleven years of kubernetes.io/blog as a walkable archive

767 blog posts, March 2015 to August 2026, censused one by one. Some of them are still
exercises you can run. Most of them broke, and the ones that broke are the valuable ones.

This is **supplementary**. It gates no phase; [P0–P12](../README.md) are complete without it.
It has its own reading order and links into `phases/` nowhere.

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
git sparse-checkout set content/en/blog/_posts
git fetch --depth 1 origin 7c76070faf9b19e6a417c446043dbafd10a7aa1d
git checkout FETCH_HEAD
```

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

Rows live in `YYYY/README.md`, columns: post, date, the Kubernetes version it targets, verdict,
topic, and one line of why. Verdicts:

| verdict | means |
|---|---|
| `walk` | earns an exercise file |
| `read` | worth reading, nothing to do — a concept or an argument that outlived its commands, or a technique another exercise already carries |
| `dated` | *was* hands-on and would still be, but it does not fit the lab — hardware or scale beyond the [9.5GB ceiling](../strands/lab-topologies.md#ceiling) |
| `skip` | no learning content — hangouts, launch parties, video roundups, recruiting, pure PR |

`dated` is deliberately the narrowest verdict, and the only one decided by a fact rather than a
judgement: *does this fit on hopper?* A post whose technique is real but redundant, or whose
tool is abandoned, is a `read` — worth your eyes, not your cluster. Without that line `dated`
becomes the bin for anything awkward, and the census stops meaning anything.

Topic, from a fixed vocabulary of twelve: `api` `sched` `net` `storage` `security` `nodes`
`etcd` `obs` `tooling` `ecosystem` `history` `meta`. `obs` is monitoring, logging, metrics and
tracing — posts about *seeing* the cluster, which otherwise scatter across the subsystem each
one happens to instrument.

### Three genres with a rule, because they are most of the corpus

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

**Release announcements** — `skip` unless a specific line in the post is load-bearing for an
exercise elsewhere; then `read`, and the `why` column names that line. This keeps the verdict
earned against a fact instead of awarded to a genre — which matters most in the later years,
where this genre is the majority of the corpus. Either way a release post is evidence of an
**announcement, never of an event**: version numbers in an exercise come from the source tree
at the release tag. See [`research/blog-era-translation.md`](../research/blog-era-translation.md)
for why that distinction is not pedantry.

Triage is **title + frontmatter + first screen**. The corpus is ~5.6MB of markdown, roughly
1.4M tokens; it cannot be read in full by anyone, ever. Full reads are spent on `walk`
candidates only. A first-screen digest of a whole year costs about **31%** of reading that year
end-to-end — measured on 2015: 44 posts, 299KB of source, a 93KB digest, ~530 tokens a post.

## Yield

Soft band: **8–15 `walk` verdicts per year** — roughly 100–180 exercises against
[`labs/`](../labs/)'s 357. No hard cap. Each year's README states its yield out loud, and a
year outside the band argues for itself in one line. The band is friction to keep the rubric
honest, not a number that overrides judgement on a genuinely dense year.

## The one link out

Exercises cite [`strands/lab-topologies.md`](../strands/lab-topologies.md) for topologies and
for provision and teardown steps, rather than restating them. That is the *only* coupling in
either direction. Duplicating the [9.5GB ceiling](../strands/lab-topologies.md#ceiling) into a
second tree is how you end up with two contradictory answers to "how much RAM do I have".

[`strands/check-anchors.py`](../strands/check-anchors.py) is not extended to this tree.
`blogwalk/check-census.py` is this sweep's only gate, and it checks census rows
against `manifest.tsv`.

## Layout

```
blogwalk/README.md          this file — method
blogwalk/TEMPLATE.md        the exercise template, forked from labs/
blogwalk/manifest.tsv       one row per post at the pin
blogwalk/build-manifest.py  regenerates the manifest, asserts the counts
blogwalk/check-census.py    the gate (not written yet — issue #58)
blogwalk/YYYY/README.md     that year's full census
blogwalk/YYYY/NN-slug.md    one exercise per `walk` post, numbered in publication order
```
