#!/usr/bin/env python3
"""Enforce the anchor contract described in strands/README.md.

Checks, across strands/, phases/ and labs/:
  * no document publishes the same id twice
  * no two strand docs publish the same id (a cross-file collision is a link hazard)
  * every `foo.md#anchor` link resolves to an id that is actually published
  * every `foo.md` link points at a file that exists
  * every same-file `](#anchor)` link resolves too — which is what catches a GitHub
    heading slug written in place of an explicit id

**Id scoping.** Strand ids are global: two strand docs publishing the same id is a
break, because a phase file writes `](certs.md#cka)` and the reader has to know which
doc owns `cka` without looking. Ids in phases/ and labs/ are scoped **per file**
instead — every link into them carries the path (`../labs/08/02-predict-the-bind.md#lab-8-2`),
so `lab-8-2` in one phase's directory cannot be confused with anything in another's.
Requiring the ~100 exercise files of thirteen phases to agree on a global id namespace
would buy nothing and collide constantly. A duplicate id *within a single file* is
still a break everywhere, since that genuinely is ambiguous.

**Link resolution is strictly relative to the linking file.** There is no fallback
search path: a link from labs/08/ into the strands is `../../strands/foo.md`, and
writing `../strands/foo.md` from that depth is a break, because that is what GitHub
would do with it.

Run from the repo root. Exits non-zero on the first category that fails, so it is
usable as a pre-commit or CI gate. `labs/` not existing yet is not a failure.
"""
import re, sys, pathlib, collections

ROOT = pathlib.Path(__file__).resolve().parent.parent
STRANDS, PHASES, LABS = ROOT / "strands", ROOT / "phases", ROOT / "labs"

ANCHOR = re.compile(r'<a id="([^"]+)"></a>')
# ](any/relative/target.md) and ](target.md#anchor); external URLs are not ours to check
LINK = re.compile(r'\]\((?!https?://)([^)#\s]+\.md)(?:#([^)\s]+))?\)')
# ](#anchor) — a link into the *same* file. These were invisible until #35: the regex
# above requires a `.md`, so a GitHub heading slug written same-file was neither
# resolved nor rejected, and 66 of them had accumulated across the phase files.
SAMEFILE = re.compile(r'\]\(#([^)\s]+)\)')
FENCE  = re.compile(r"^```.*?^```", re.S | re.M)
INLINE = re.compile(r"`[^`\n]*`")

def prose(f):
    """File text with code removed. A link pattern inside a fence or a backtick span
    is an *example* of a link, not one — these docs quote the syntax at each other."""
    return INLINE.sub("", FENCE.sub("", f.read_text()))

def ids_in(f):
    found = ANCHOR.findall(f.read_text())
    dupes = [i for i, n in collections.Counter(found).items() if n > 1]
    if dupes:
        print(f"DUPLICATE id in {f.relative_to(ROOT)}: {', '.join(dupes)}")
    return set(found), bool(dupes)

strand_files = sorted(STRANDS.glob("*.md"))
scoped_files = sorted(PHASES.glob("*.md")) + sorted(LABS.glob("**/*.md"))

# strand ids are global and keyed by filename; phase/lab ids are keyed by repo-relative path
published, dupes_found = {}, False
for f in strand_files:
    published[f.name], d = ids_in(f)
    dupes_found |= d
for f in scoped_files:
    published[str(f.relative_to(ROOT))], d = ids_in(f)
    dupes_found |= d

owner, collisions = {}, []
for f in strand_files:
    for i in published[f.name]:
        if i in owner:
            collisions.append((i, owner[i], f.name))
        owner[i] = f.name

sources = strand_files + scoped_files
UNWRITTEN = re.compile(r"^\d\d-[a-z-]+\.md$")   # a phase file that does not exist yet
broken, pending = [], set()
for f in sources:
    text = prose(f)
    for target, anchor in LINK.findall(text):
        rel = f.relative_to(ROOT)
        path = f.parent / target
        if not path.exists():
            # forward references between phase files are fog, not breakage: the
            # phase is planned and unwritten. A missing strand doc is breakage.
            if f.parent == PHASES and UNWRITTEN.match(target):
                pending.add(target)
            else:
                broken.append(f"{rel} -> {target} (no such file)")
        elif anchor:
            resolved = path.resolve()
            # a strand doc is addressed globally by name; anything else by its path
            key = (resolved.name if resolved.parent == STRANDS
                   else str(resolved.relative_to(ROOT)))
            if key in published and anchor not in published[key]:
                broken.append(f"{rel} -> {target}#{anchor} (no such anchor)")
    key = (f.name if f.parent == STRANDS else str(f.relative_to(ROOT)))
    for anchor in SAMEFILE.findall(text):
        if anchor not in published[key]:
            broken.append(f"{f.relative_to(ROOT)} -> #{anchor} (no such anchor, same file)")

for i, a, b in collisions:
    print(f"COLLISION: id '{i}' published by both {a} and {b}")
for b in broken:
    print(f"BROKEN: {b}")

if pending:
    print(f"pending phase files, linked but not yet written: {', '.join(sorted(pending))}")

total_ids = sum(len(v) for v in published.values())
n_labs = len(list(LABS.glob("**/*.md")))
print(f"{len(strand_files)} strand docs, {total_ids} anchors, {len(sources)} files scanned "
      f"({n_labs} in labs/), {len(broken) + len(collisions) + dupes_found} problems")
sys.exit(1 if broken or collisions or dupes_found else 0)
