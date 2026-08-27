#!/usr/bin/env python3
"""Enforce the blogwalk census contract. Green in both directions, no silent passes.

`blogwalk/` is standalone, so [`strands/check-anchors.py`](../strands/check-anchors.py) is
not extended to it and does not cover it. At 767 rows nobody checks by eye, and without a
gate "swept" and "feels swept" are indistinguishable. This is that gate. Its whole interface
is

    python3 blogwalk/check-census.py

run from the repo root. Exit 1 on any failure; warnings never fail.

**manifest.tsv is the authority, not the tree.** Every census row is matched back to a
manifest row, so a post nobody censused and a row for a post that does not exist are both
loud. A row is matched **by its URL, byte-identical to the manifest's `url` column** — never
by rebuilding one. Only 552 of 767 posts take `hugo.toml`'s permalink; 205 override it and
eleven of those are hand-written literals whose capitalisation is not the slug's, so a
checker that resolves URLs itself is wrong on 27% of the corpus. The ten unpublished drafts
resolve to no permalink at all, carry an empty `url`, and are matched on their title.

**The vocabularies are read out of `blogwalk/README.md`**, not restated here: the four
verdicts from its verdict table, the twelve topics from its vocabulary line, the budget from
its budget section. A gate carrying its own copy of the rubric is a second source of truth,
and the copy is always the one that drifts. If any of the three fails to parse that is
itself a failure — a gate that silently checks nothing is worse than no gate.

**The walk-to-exercise join is positional**, because nothing else ties them. An exercise
filename is a hand-written abbreviation — `10-websocket-transition.md` belongs to a post
whose slug is `websockets-transition` — so there is no key to join on. The Nth `walk` row in
publication order is exercise NN. That holds only if the census really is in publication
order, so date order and every date cell are checked against the manifest *first*: a census
sorted any other way would silently mis-attribute every exercise it has.

**A year with no `README.md` is pending, not broken** — the same treatment, and the same
word, `check-anchors.py` gives a phase whose `labs/NN/` does not exist yet. The sweep is ten
passes from finished, and a gate that is red for an uncensused year is not usable as a gate.

Failure classes, as ratified in #58:

  1. a post in the manifest with no census row, in a year that has been censused
  2. a post with more than one census row
  3. a `walk` row with no matching row in that year's Exercises table
  4. an exercise file with no `walk` row, or whose row carries a different verdict, or
     whose state disagrees with what is on disk — checked in both directions
  5. a post link not byte-identical to that post's `url` column
  6. a verdict or a topic outside the ratified vocabulary
  7. a row missing its k8s version or its one-line why
  8. *warning only* — a `dated` row whose why cites no hardware and no scale. `dated` takes
     two tests after #57 and only the second is mechanically checkable at all, so this
     prompts a human instead of deciding anything
  9. a census row out of publication order, or a date cell disagreeing with the manifest
"""
import re, sys, pathlib, collections

ROOT = pathlib.Path(__file__).resolve().parent.parent
BLOGWALK = ROOT / "blogwalk"
MANIFEST = BLOGWALK / "manifest.tsv"
METHOD = BLOGWALK / "README.md"

CENSUS_HEADER = ["post", "date", "k8s", "verdict", "topic", "why"]
EXERCISE_HEADER = ["#", "exercise", "state"]
STATES = ("written", "pending")

LINKED = re.compile(r"^\[(?P<title>.+)\]\((?P<url>[^)\s]+)\)$")
DRAFT = re.compile(r"^(?P<title>.+?)\s+\(draft\)$")
EX_FILE = re.compile(r"^(\d\d)-[a-z0-9-]+\.md$")
# class 8 is a prompt, not a proof: does the why cite hardware or scale at all?
SCALE = re.compile(r"ceiling|bare metal|\bnodes?\b|\bRAM\b|memory|hardware|load balancer|"
                   r"\d+\s?(?:GB|GiB)|not fit|far past|physical|\bGPUs?\b|control planes",
                   re.I)

problems, warnings = [], []


def fail(cls, msg):
    problems.append(f"[{cls}] {msg}")


def table(text, heading, header):
    """Rows of the markdown table under `## heading`, as lists of stripped cells.

    Returns None when the section is absent, so a missing section is distinguishable
    from an empty one. The header row must match exactly: a census whose columns have
    drifted is not a census the twelve year tables concatenate.
    """
    m = re.search(r"^## " + re.escape(heading) + r"\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not m:
        return None
    out = []
    for line in m.group(1).split("\n"):
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if all(set(c) <= set("-: ") and c for c in cells):
            continue                                  # the |---|---| separator
        out.append(cells)
    if not out:
        return []
    if out[0] != header:
        fail("table", f"{heading} header is {out[0]}, expected {header}")
        return []
    return out[1:]


def bare(cell):
    """A cell's token, with the bolding and backticks the census uses for emphasis off."""
    return re.sub(r"[*`]", "", cell).strip()


def vocabulary():
    """Verdicts, topics and the budget band, read out of the method file.

    Parsed rather than restated, so `blogwalk/README.md` stays the single source of
    truth for the rubric this script enforces.
    """
    text = METHOD.read_text()
    verdicts, topics, band = [], [], None
    m = re.search(r"^\| verdict \| means \|\n\|[-|]+\|\n((?:\|.*\n)+)", text, re.M)
    if m:
        verdicts = re.findall(r"^\|\s*`([a-z]+)`", m.group(1), re.M)
    # up to the first full stop: the sentence after the list glosses `obs`, and a
    # paragraph-wide match would read that gloss back in as a thirteenth topic
    m = re.search(r"fixed vocabulary of twelve\*\*:(.*?)\.\s", text, re.S)
    if m:
        topics = re.findall(r"`([a-z]+)`", m.group(1))
    m = re.search(r"\*\*(\d+)–(\d+) `walk` verdicts per year\*\*", text)
    if m:
        band = (int(m.group(1)), int(m.group(2)))
    if len(verdicts) != 4:
        fail("rubric", f"could not read the verdict table from {METHOD.name} (got {verdicts})")
    if len(topics) != 12:
        fail("rubric", f"could not read the twelve topics from {METHOD.name} (got {topics})")
    if band is None:
        fail("rubric", f"could not read the budget band from {METHOD.name}")
    return set(verdicts), set(topics), band or (0, 10 ** 6)


def manifest():
    """The pinned corpus, keyed by year. Drafts keep their empty url."""
    lines = [l for l in MANIFEST.read_text().split("\n") if l and not l.startswith("#")]
    cols = lines[0].split("\t")
    by_year = collections.defaultdict(list)
    for line in lines[1:]:
        row = dict(zip(cols, line.split("\t")))
        by_year[row["year"]].append(row)
    return by_year


VERDICTS, TOPICS, (BAND_LO, BAND_HI) = vocabulary()
POSTS = manifest()

censused, pending = [], []
for year in sorted(POSTS):
    (censused if (BLOGWALK / year / "README.md").exists() else pending).append(year)

report = []
for year in censused:
    ydir = BLOGWALK / year
    text = (ydir / "README.md").read_text()
    rel = f"blogwalk/{year}/README.md"
    posts = POSTS[year]
    by_url = {p["url"]: p for p in posts if p["url"]}
    by_title = {p["title"]: p for p in posts if not p["url"]}

    rows = table(text, "Census", CENSUS_HEADER)
    if rows is None:
        fail("table", f"{rel} has no `## Census` section")
        rows = []

    seen = collections.Counter()
    matched, walks = [], []
    for n, cells in enumerate(rows, 1):
        where = f"{rel} census row {n}"
        if len(cells) != len(CENSUS_HEADER):
            fail("table", f"{where} has {len(cells)} cells, expected {len(CENSUS_HEADER)}")
            continue
        post, date, k8s, verdict, topic, why = cells
        verdict, topic = bare(verdict), bare(topic)

        # 5 — the link, byte-identical to the manifest, or an unlinked draft by title
        link = LINKED.match(post)
        entry = None
        if link:
            url = link.group("url")
            if url in by_url:
                entry = by_url[url]
            elif any(url == p["url"] for ps in POSTS.values() for p in ps if p["url"]):
                fail(5, f"{where}: {url} is a {year} row but that post is not in {year}")
            else:
                fail(5, f"{where}: {url} matches no `url` in manifest.tsv")
        elif DRAFT.match(post):
            title = DRAFT.match(post).group("title")
            if title in by_title:
                entry = by_title[title]
            else:
                fail(5, f"{where}: draft {title!r} matches no unpublished post in {year}")
        else:
            fail(5, f"{where}: post cell is neither a link nor a `Title (draft)`: {post!r}")

        if entry is not None:
            seen[entry["path"]] += 1
            matched.append((n, entry))
            # 9 — the date cell, which the positional exercise join depends on
            if date != entry["date"][5:10]:
                fail(9, f"{where}: date {date} but manifest says {entry['date'][5:10]}")

        # 6 — vocabularies
        if verdict not in VERDICTS:
            fail(6, f"{where}: verdict {verdict!r} is not one of {sorted(VERDICTS)}")
        if topic not in TOPICS:
            fail(6, f"{where}: topic {topic!r} is not one of the twelve")
        # 7 — the two cells that carry the judgement
        if not k8s:
            fail(7, f"{where}: no k8s version (use — where the post predates versioning)")
        if not why:
            fail(7, f"{where}: no why")
        # 8 — warning
        if verdict == "dated" and not SCALE.search(why):
            warnings.append(f"[8] {where}: `dated` but the why cites no hardware or scale")

        if verdict == "walk":
            walks.append((n, entry))

    # 1 and 2 — both directions against the manifest
    for p in posts:
        if seen[p["path"]] == 0:
            fail(1, f"{rel}: no row for {p['path']}")
        elif seen[p["path"]] > 1:
            fail(2, f"{rel}: {seen[p['path']]} rows for {p['path']}")

    # 9 — publication order, which is what makes the exercise numbering mean anything
    # day granularity: 2024 stamps six posts with a time and a timezone offset, and
    # ordering two posts published the same day in different offsets is not a thing this
    # gate can adjudicate. A day going backwards is unambiguous, and is what it checks.
    dates = [e["date"][:10] for _, e in matched]
    if dates != sorted(dates):
        bad = next(i for i in range(1, len(dates)) if dates[i] < dates[i - 1])
        fail(9, f"{rel}: census is not in publication order — row {matched[bad][0]} "
                f"({dates[bad]}) follows {dates[bad - 1]}")

    # 3 and 4 — the Exercises table against the walk rows and against the files on disk
    ex = table(text, "Exercises", EXERCISE_HEADER)
    if ex is None:
        if walks:
            fail(3, f"{rel} has {len(walks)} `walk` rows and no `## Exercises` section")
        ex = []
    files = {}
    for f in sorted(ydir.glob("*.md")):
        if f.name == "README.md":
            continue
        m = EX_FILE.match(f.name)
        if not m:
            fail(4, f"blogwalk/{year}/{f.name} is not named NN-slug.md")
        else:
            files[int(m.group(1))] = f.name

    if len(ex) != len(walks):
        fail(3, f"{rel}: {len(walks)} `walk` rows but {len(ex)} exercise rows")
    for i, cells in enumerate(ex, 1):
        where = f"{rel} exercise row {i}"
        if len(cells) != len(EXERCISE_HEADER):
            fail("table", f"{where} has {len(cells)} cells, expected 3")
            continue
        num, title, state = cells
        if num != f"{i:02d}":
            fail(3, f"{where}: numbered {num!r}, expected {i:02d} — exercises are numbered "
                    f"in publication order with no gaps")
            continue
        if state not in STATES:
            fail(4, f"{where}: state {state!r} is not one of {STATES}")
            continue
        link = LINKED.match(title)
        ondisk = files.pop(i, None)
        if state == "written":
            if not link:
                fail(4, f"{where}: marked written but the title links nothing")
            elif link.group("url") != ondisk:
                fail(4, f"{where}: links {link.group('url')!r} but the file on disk is "
                        f"{ondisk!r}")
        else:
            if link:
                fail(4, f"{where}: marked pending but links {link.group('url')!r}")
            if ondisk:
                fail(4, f"{where}: marked pending but {ondisk} exists")
    for num, name in sorted(files.items()):
        fail(4, f"blogwalk/{year}/{name} has no row {num:02d} in the Exercises table")

    nwalk = len(walks)
    report.append((year, len(posts), len(rows), nwalk,
                   "" if BAND_LO <= nwalk <= BAND_HI else "  <- outside the budget"))

for w in warnings:
    print(w)
for p in problems:
    print(p)
if problems or warnings:
    print()

print(f"{'year':>6} {'posts':>6} {'rows':>6} {'walk':>6}")
tp = tr = tw = 0
for year, np_, nr, nw, flag in report:
    tp, tr, tw = tp + np_, tr + nr, tw + nw
    print(f"{year:>6} {np_:>6} {nr:>6} {nw:>6}{flag}")
print(f"{'':>6} {'-' * 6:>6} {'-' * 6:>6} {'-' * 6:>6}")
print(f"{'':>6} {tp:>6} {tr:>6} {tw:>6}   censused")
total = sum(len(v) for v in POSTS.values())
print(f"{'':>6} {total:>6}{'':>14}   pinned")

if pending:
    print(f"\npending years, in the manifest but not yet censused: {', '.join(pending)} "
          f"({total - tp} posts)")
print(f"\n{len(censused)}/{len(censused) + len(pending)} years censused, "
      f"{tw} walk against a budget of {BAND_LO}–{BAND_HI} a year, "
      f"{len(problems)} problems, {len(warnings)} warnings")
sys.exit(1 if problems else 0)
