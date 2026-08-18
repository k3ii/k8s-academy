#!/usr/bin/env python3
"""Enforce the anchor contract described in strands/README.md.

Checks, across strands/, phases/ and labs/:
  * no document publishes the same id twice
  * no two strand docs publish the same id (a cross-file collision is a link hazard)
  * every `foo.md#anchor` link resolves to an id that is actually published
  * every `foo.md` link points at a file that exists
  * every same-file `](#anchor)` link resolves too — which is what catches a GitHub
    heading slug written in place of an explicit id
  * **coverage, both directions**: every `### Module N.N` has an exercise, every
    exercise is linked, and `labs/NN/README.md` lists the whole directory

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

**Coverage is the anchor contract one level up.** Link integrity says every link
resolves; it says nothing about a module that quietly got no exercise, or an exercise
file no phase links to. So, for each `phases/NN-*.md` that has a `labs/NN/`:

  * *forward* — every `### Module N.N` block carries a `**Labs**` line pointing into
    `../labs/NN/`, **or** an explicit `**No lab` marker;
  * *backward* — every exercise file is linked **from the phase file**, and listed in
    `labs/NN/README.md`. Both, not either: the phase link is what routes a learner to
    the exercise, the index is what makes the directory readable on its own. #36
    proposed *phase or index*; both prototypes already satisfied the stronger form for
    all 42 exercises, and under *or* the phase check would almost never fire, since an
    exercise missing from the index fails the index rule first.

A module that is genuinely reading-only declares itself with a **line-start bolded
`**No lab`** — P8's module 8.1, P0's 0.6 and P1's 1.6 already do, in three wordings
(`**No lab** —`, `**No lab.**`, `**No lab of its own.**`), all of which the marker
accepts. The declaration lives in the phase file, where a reader sees it, rather than
in a list inside this script, where nobody would. Adding a module without either a
`**Labs**` line or that marker is a break.

The index needing to list "nothing that is not there" needs no separate rule: a README
linking a file that does not exist is already a broken link above.

Run from the repo root. Exits non-zero on the first category that fails, so it is
usable as a pre-commit or CI gate. **A phase whose `labs/NN/` does not exist yet is
*pending*, not broken** — the same treatment, and the same word, the script already
gives a phase file that is linked but unwritten.
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
MODULE = re.compile(r"^### Module (\d+)\.(\d+)\b")
HEADING = re.compile(r"^#{2,3} ")
LABS_LINE = re.compile(r"^\*\*Labs\*\*")
NO_LAB = re.compile(r"^\*\*No lab")          # the explicit reading-only declaration
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

def links_to(f):
    """The set of repo-relative paths f links at, resolved from f's own directory."""
    out = set()
    for target, _ in LINK.findall(prose(f)):
        path = (f.parent / target)
        if path.exists():
            out.add(str(path.resolve().relative_to(ROOT)))
    return out

uncovered, pending_labs = [], set()
n_exercises = n_modules = n_with_labs = 0
for pf in sorted(PHASES.glob("*.md")):
    nn = pf.name[:2]
    labdir = LABS / nn
    if not labdir.is_dir():
        pending_labs.add(nn)
        continue

    # forward: walk each ### Module block to its next heading
    block, blocks = None, []
    for line in pf.read_text().split("\n"):
        m = MODULE.match(line)
        if m:
            block = (f"{m.group(1)}.{m.group(2)}", [])
            blocks.append(block)
        elif block is not None and HEADING.match(line):
            block = None
        if block is not None:
            block[1].append(line)
    for mid, body in blocks:
        n_modules += 1
        labs = any(LABS_LINE.match(l) for l in body) and f"../labs/{nn}/" in "\n".join(body)
        if labs:
            n_with_labs += 1
        elif not any(NO_LAB.match(l) for l in body):
            uncovered.append(f"module {mid} in {pf.relative_to(ROOT)} has neither a "
                             f"`**Labs**` line into labs/{nn}/ nor a `**No lab` declaration")

    # backward: every exercise reachable from the phase file or the index
    readme = labdir / "README.md"
    if not readme.exists():
        uncovered.append(f"labs/{nn}/ has no README.md index")
    from_phase = links_to(pf)
    from_index = links_to(readme) if readme.exists() else set()
    for ex in sorted(labdir.glob("*.md")):
        if ex.name == "README.md":
            continue
        n_exercises += 1
        rel = str(ex.relative_to(ROOT))
        if rel not in from_phase:
            uncovered.append(f"{rel} is not linked from phases/{pf.name}")
        if rel not in from_index:
            uncovered.append(f"labs/{nn}/README.md does not list {ex.name}")

for i, a, b in collisions:
    print(f"COLLISION: id '{i}' published by both {a} and {b}")
for u in uncovered:
    print(f"UNCOVERED: {u}")
for b in broken:
    print(f"BROKEN: {b}")

if pending:
    print(f"pending phase files, linked but not yet written: {', '.join(sorted(pending))}")
if pending_labs:
    print(f"pending lab directories, phase written but exercises not yet generated: "
          f"{', '.join(sorted(pending_labs))}")

total_ids = sum(len(v) for v in published.values())
n_labs = len(list(LABS.glob("**/*.md")))
print(f"{len(strand_files)} strand docs, {total_ids} anchors, {len(sources)} files scanned "
      f"({n_labs} in labs/), {n_exercises} exercises covering {n_with_labs}/{n_modules} "
      f"modules, {len(broken) + len(collisions) + len(uncovered) + dupes_found} problems")
sys.exit(1 if broken or collisions or uncovered or dupes_found else 0)
