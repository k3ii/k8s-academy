#!/usr/bin/env python3
"""Enforce the drill contract for cka/, decided in the sprint's t05 ticket.

This is deliberately **not** strands/check-anchors.py. That script's substance is
phase-shaped -- every exercise linked from its phase and listed in its phase README,
every module carrying a `**Labs**` line -- and cka/ has no phases, no modules and no
phase README, so two of its three checks have no analogue here. A new top-level cka/
is outside check-anchors.py by construction: it globs only strands/, phases/ and
labs/, so nothing in this tree can turn that gate red whatever it contains.

Four checks, and no more:

  1. **Exactly one topology per drill file**, written as a link to a
     lab-topologies.md#<row> anchor. Zero is an error; two or more is an error. A
     drill that does not say which cluster it needs cannot be scheduled, and one
     that names two is really two drills.
  2. **Exactly one index entry per drill file, in both directions.** Every drill is
     linked once from cka/drills/README.md; every drill link in that index points at
     a file that exists. Neither orphans nor phantoms survive. Unwritten drills are
     listed in the index as a bare id in plain text, which is not a link and so is
     not an entry -- that is how the index can hold all 66 objects while the tree
     holds fewer, and still be checked.
  3. **Every drill carries a time target and a band** from {Pinned, Core, Optional}.
  4. **Every relative link resolves** -- the file exists, and the anchor, if any, is
     published there -- reusing check-anchors.py's LINK and ANCHOR regexes rather
     than reinventing them. Links are resolved strictly relative to the linking file,
     with no fallback search path, which is what GitHub does with them.

**Not enforced: the body format.** The 357 lab exercises run
Claim / Rests on / Do / Observe / Expect. `Rests on` is the phase-chaining mechanism,
and drills are deliberately unchained, so requiring it would import exactly the
coupling the sprint ruled out. Drill files share a dialect by convention and the
convention is not a gate.

All four checks are satisfiable by a drill file that exists at all, so there is no
window in which red is legitimate. Run from anywhere; exits non-zero on any problem.
"""
import re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
CKA = ROOT / "cka"
DRILLS = CKA / "drills"
INDEX = DRILLS / "README.md"

ANCHOR = re.compile(r'<a id="([^"]+)"></a>')
LINK = re.compile(r'\]\((?!https?://)([^)#\s]+\.md)(?:#([^)\s]+))?\)')
FENCE = re.compile(r"^```.*?^```", re.S | re.M)
INLINE = re.compile(r"`[^`\n]*`")

TOPOLOGY = re.compile(r'\]\(([^)\s]*lab-topologies\.md)#([^)\s]+)\)')
# A topology *row* publishes itself as <a id="pair"></a>**`pair`**. Any other anchor in
# that file -- #addresses, #teardown -- is an ordinary reference, not a declaration.
TOPO_ROW = re.compile(r'<a id="([^"]+)"></a>\*\*`\1`\*\*')
BAND = re.compile(r"\*\*(Pinned|Core|Optional)\*\*")
TIME = re.compile(r"\*\*(\d+)\s*(min|h)\*\*")

def prose(text):
    """Drop fenced blocks and inline code: an example is not a link."""
    return INLINE.sub("``", FENCE.sub("", text))

ROWS = set(TOPO_ROW.findall((ROOT / "strands" / "lab-topologies.md").read_text()))

broken, problems = [], []

drill_files = sorted(p for p in DRILLS.glob("*/*.md") if p.name != "README.md")
if not drill_files:
    print("no drill files under cka/drills/*/ -- nothing to check")
    sys.exit(0)

# Every .md under cka/ publishes ids; collect them for check 4, plus the trees the
# drills link out into, since a dead ../strands/ anchor is just as broken.
published = {}
for f in list(CKA.glob("**/*.md")) + list((ROOT / "strands").glob("*.md")) + \
         list((ROOT / "phases").glob("*.md")):
    published[f.resolve()] = set(ANCHOR.findall(f.read_text()))

# --- checks 1 and 3: the metadata line -------------------------------------------
for f in drill_files:
    rel = f.relative_to(ROOT)
    text = f.read_text()
    body = prose(text)

    topos = [t for t in TOPOLOGY.findall(body) if t[1] in ROWS]
    if len(topos) == 0:
        problems.append(f"{rel}: no topology -- expected one link to lab-topologies.md#<row>")
    elif len(topos) > 1:
        names = ", ".join(sorted({t[1] for t in topos}))
        problems.append(f"{rel}: {len(topos)} topology links ({names}) -- a drill names exactly one")

    # The metadata line is the first non-heading, non-anchor, non-blank line.
    meta = ""
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#") or s.startswith("<a id="):
            continue
        meta = s
        break
    if not BAND.search(meta):
        problems.append(f"{rel}: no band on the metadata line -- one of **Pinned**, **Core**, **Optional**")
    if not TIME.search(meta):
        problems.append(f"{rel}: no time target on the metadata line -- e.g. **10 min** or **4 h**")

# --- check 2: the index, both directions -----------------------------------------
index_text = INDEX.read_text() if INDEX.exists() else ""
if not index_text:
    problems.append("cka/drills/README.md is missing -- the index is half of this contract")

indexed = []
for target, _ in LINK.findall(prose(index_text)):
    p = (INDEX.parent / target).resolve()
    try:
        p.relative_to(DRILLS)
    except ValueError:
        continue                      # a link out of the tree, checked by check 4
    if p.name != "README.md":
        indexed.append(p)

for p in sorted(set(indexed)):
    if indexed.count(p) > 1:
        problems.append(f"cka/drills/README.md links {p.relative_to(ROOT)} {indexed.count(p)} times -- exactly one entry")
    if not p.exists():
        problems.append(f"cka/drills/README.md: phantom entry, {p.relative_to(ROOT)} does not exist")

for f in drill_files:
    if f.resolve() not in {p for p in indexed}:
        problems.append(f"{f.relative_to(ROOT)}: orphan, not linked from cka/drills/README.md")

# --- check 4: every relative link resolves ---------------------------------------
for f in sorted(CKA.glob("**/*.md")):
    body = prose(f.read_text())
    for target, anchor in LINK.findall(body):
        p = (f.parent / target).resolve()
        if not p.exists():
            broken.append(f"{f.relative_to(ROOT)} -> {target} (no such file)")
        elif anchor and anchor not in published.get(p, set()):
            broken.append(f"{f.relative_to(ROOT)} -> {target}#{anchor} (no such id)")

for b in broken:
    print(f"BROKEN: {b}")
for p in problems:
    print(f"DRILL: {p}")

n_md = len(list(CKA.glob("**/*.md")))
print(f"{len(drill_files)} drill files in {n_md} cka/ documents, "
      f"{len(set(indexed))} indexed, {len(broken) + len(problems)} problems")
sys.exit(1 if broken or problems else 0)
