#!/usr/bin/env python3
"""Enforce the anchor contract described in strands/README.md.

Checks, across strands/ and phases/:
  * no strand doc publishes the same id twice
  * no two strand docs publish the same id (a cross-file collision is a link hazard)
  * every `foo.md#anchor` link resolves to an id that is actually published
  * every `foo.md` link points at a file that exists

Run from the repo root. Exits non-zero on the first category that fails, so it is
usable as a pre-commit or CI gate.
"""
import re, sys, pathlib, collections

ROOT = pathlib.Path(__file__).resolve().parent.parent
STRANDS, PHASES = ROOT / "strands", ROOT / "phases"

ANCHOR = re.compile(r'<a id="([^"]+)"></a>')
# ](target.md#anchor) or ](../strands/target.md#anchor), and the anchorless form
LINK = re.compile(r'\]\((?:\.\./strands/)?([A-Za-z0-9._-]+\.md)(?:#([^)]+))?\)')

published = {}
for f in sorted(STRANDS.glob("*.md")):
    ids = ANCHOR.findall(f.read_text())
    dupes = [i for i, n in collections.Counter(ids).items() if n > 1]
    published[f.name] = set(ids)
    if dupes:
        print(f"DUPLICATE id in {f.name}: {', '.join(dupes)}")

owner, collisions = {}, []
for name, ids in published.items():
    for i in ids:
        if i in owner:
            collisions.append((i, owner[i], name))
        owner[i] = name

sources = sorted(STRANDS.glob("*.md")) + sorted(PHASES.glob("*.md"))
broken = []
for f in sources:
    for target, anchor in LINK.findall(f.read_text()):
        rel = f.relative_to(ROOT)
        # resolve the target relative to the linking file's own directory
        path = (f.parent / target) if (f.parent / target).exists() else (STRANDS / target)
        if not path.exists():
            broken.append(f"{rel} -> {target} (no such file)")
        elif anchor and path.parent == STRANDS and anchor not in published.get(target, set()):
            broken.append(f"{rel} -> {target}#{anchor} (no such anchor)")

for i, a, b in collisions:
    print(f"COLLISION: id '{i}' published by both {a} and {b}")
for b in broken:
    print(f"BROKEN: {b}")

total_ids = sum(len(v) for v in published.values())
print(f"{len(published)} strand docs, {total_ids} anchors, "
      f"{len(sources)} files scanned, {len(broken) + len(collisions)} problems")
sys.exit(1 if broken or collisions else 0)
