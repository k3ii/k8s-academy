#!/usr/bin/env python3
"""Build a year's triage digest — the census's reading budget, made mechanical.

A census pass triages on "title + frontmatter + first screen only". That is a
rule a reader drifts on and a script cannot, which is the whole reason this
exists: the digest is not a convenience, it is the budget enforced.

    python3 blogwalk/digest.py <year> <path-to-website>/content/en/blog/_posts

Writes to stdout. Redirect it somewhere outside the repo — a digest is derived
from the manifest and the pinned corpus, and 767 posts of it is not an artifact
worth versioning. See build-manifest.py's docstring for how to re-create the
corpus from the pin alone.

manifest.tsv is the authority for path, date, url and title, exactly as it is
for check-census.py. Nothing about a post is first written down here.

Posts are emitted in **publication order — sorted by (date, path)** — because
that is the order a census table is written in, and check-census.py joins walk
rows to exercise files positionally against it. The bracketed index is what a
triager uses to refer to a post while working; it is not a stable identifier
and it is not the exercise number.

One wrinkle, and it is the corpus's rather than the script's: 10 of the 11
`draft: true` posts carry no date at all, so an empty sort key puts them ahead
of every published post in their year. All 10 are in 2026. They are emitted
first, dated `(undated)`, and flagged `DRAFT` — grouped rather than scattered,
which is what a triager wants, but it means "publication order" describes the
dated tail of a year and not its head. The 11th draft is the interesting one:
2026/csi-changed-block-tracking-beta.md is `draft: true` and yet carries a full
date, so build-manifest.py derived a permalink for it and it sorts into the
dated run like any published post. Whether kubernetes.io actually serves that
URL is untested here and a draft is precisely what Hugo does not publish, so
the manifest may well be advertising a 404. Either way the census's drafts rule
says a draft has no permalink, and this row has one; it is 2026's problem to
settle, not this script's.


The body cut is a character count, and that is a decision

"First screen" has three plausible mechanical readings. Measured across all 767
posts at the pin:

  - **N characters** (this script): the same budget for every post, every year.
  - **First N paragraphs**: a 3-paragraph cut runs 435 characters at the 10th
    percentile and 1429 at the 90th — a 3.3x spread — and 7915 at worst.
  - **Up to the first heading**: 172 posts (22%) contain no markdown heading
    anywhere, and 38 more open with one at character 0. So 27% of the corpus
    needs a fallback rule, which means the rule is two rules.

Both structural cuts make "first screen" mean something different for different
posts. A budget that varies per post is not a budget, so the constant wins.

N defaults to 900 and is overridable. 900 was chosen to approximate one screen
and has been exercised on one full year: 2016's 90 posts all took a verdict and
a topic, with no post the rubric could not classify. That is evidence it is
sufficient, not that it is optimal.


The leading editor's note is stripped, not charged to the budget

45 posts (6%) open with a paragraph of the form "_Editor's note: today's post is
by ..._". It is masthead, not content, and it costs a median 16% of a 900-
character budget, 33% at the 90th percentile and 48% at worst. The cost is
concentrated where it does the most damage: 24 of the 45 are in 2016 and 13 in
2017, two adjacent years holding a fifth of the corpus.

Stripping it is not an exception to the constant. It removes a per-post tax that
would otherwise vary the *effective* budget by up to half. Only a leading
editor's-note paragraph is stripped; the same phrase further down is body text.

Consequence worth stating: **2016 was censused before this, from a digest that
charged the note to the budget.** 24 of its 90 posts therefore saw a median 151
characters less body than this script gives. 2016 is not byte-reproducible from
here — but the difference only ever adds body, never removes it.


Markdown heading markers are stripped from the body

Because the body is collapsed to a single line, a post opening with "### Intro"
would produce a line starting with "### " — indistinguishable from this file's
own "### [NN]" post headers, and a false header to anything parsing the digest.
38 posts open with a heading at character 0, and stripping the editor's note
promotes more of them there. A "####" is noise once the line breaks around it
are gone, so the markers go and the heading text stays.


Not a gate, and not run by one

check-census.py stays the sweep's only gate. This is an input to a human pass; a
broken digest fails by being obviously wrong to read.
"""
import os, re, sys, pathlib

MANIFEST = pathlib.Path(__file__).resolve().parent / "manifest.tsv"
BODY_CHARS = 900

FRONTMATTER = re.compile(r"^-{3,}\s*\n.*?\n-{3,}\s*\n", re.S)
COMMENT = re.compile(r"<!--.*?-->", re.S)
EDITORS_NOTE = re.compile(r"editor.{0,3}s\s+note", re.I)
ATX_HEADING = re.compile(r"(?m)^\s{0,3}#{1,6}[ \t]+")


def manifest(year):
    """Rows for one year, in publication order. The manifest is the authority.

    Undated drafts sort first on an empty date key; see the module docstring.
    """
    lines = [l for l in MANIFEST.read_text().split("\n")
             if l and not l.startswith("#")]
    cols = lines[0].split("\t")
    rows = [dict(zip(cols, l.split("\t"))) for l in lines[1:]]
    rows = [r for r in rows if r["year"] == year]
    rows.sort(key=lambda r: (r["date"], r["path"]))
    return rows


def body(raw):
    """Post text with frontmatter, HTML comments and a leading editor's note gone."""
    text = FRONTMATTER.sub("", raw.lstrip("﻿").lstrip("\n"), count=1)
    text = COMMENT.sub(" ", text).strip()
    blocks = [b for b in re.split(r"\n\s*\n", text) if b.strip()]
    if blocks and EDITORS_NOTE.search(blocks[0]):
        blocks = blocks[1:]
    text = ATX_HEADING.sub("", "\n\n".join(blocks))
    return re.sub(r"\s+", " ", text).strip()


def digest(year, posts, chars=BODY_CHARS):
    rows = manifest(year)
    if not rows:
        sys.exit(f"no posts for year {year} in {MANIFEST}")
    out = []
    # Source size comes from the manifest's `bytes` column, not from len() of the
    # decoded text: the latter counts characters, and the corpus carries 13,622
    # bytes of non-ASCII that a character count silently loses. The manifest is
    # the authority for what is at the pin, size included.
    source = sum(int(r["bytes"]) for r in rows)
    for i, r in enumerate(rows, 1):
        raw = (posts / r["path"]).read_text(errors="replace")
        text = body(raw)
        out.append(
            f"### [{i:02d}] {r['date'][:10] or '(undated)'} | {r['path']} | {r['bytes']}B"
            + (" | DRAFT" if r["draft"] == "true" else "")
            + f"\nTITLE: {r['title']}"
            + f"\nURL: {r['url'] or '(none — unpublished draft)'}\n"
            + text[:chars] + ("…" if len(text) > chars else ""))
    text = "\n\n".join(out)
    size = len(text.encode())
    header = (f"# {year} digest — {len(rows)} posts, {source}B source, "
              f"{size}B digest ({round(100 * size / source)}%), "
              f"first {chars} chars of each body\n")
    return header + "\n" + text


def main():
    if len(sys.argv) not in (3, 4):
        sys.exit(f"usage: {sys.argv[0]} <year> <path-to-_posts> [body-chars]")
    year, posts = sys.argv[1], pathlib.Path(sys.argv[2])
    chars = int(sys.argv[3]) if len(sys.argv) == 4 else BODY_CHARS
    if not posts.is_dir():
        sys.exit(f"not a directory: {posts}")
    try:
        print(digest(year, posts, chars))
        sys.stdout.flush()
    except BrokenPipeError:
        # Piping into head/grep is normal; die quietly rather than on stderr.
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        sys.exit(0)


if __name__ == "__main__":
    main()
