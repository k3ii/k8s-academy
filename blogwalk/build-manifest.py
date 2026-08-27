#!/usr/bin/env python3
"""Build blogwalk/manifest.tsv — the census's left-hand side.

One row per blog post in the pinned kubernetes/website corpus. This is the
worklist the census tickets triage against and the set check-census.py checks
every census row back to.

Re-create the corpus from the pin alone:

    git init website && cd website
    git remote add origin https://github.com/kubernetes/website.git
    git sparse-checkout init --cone
    git sparse-checkout set content/en/blog/_posts
    git fetch --depth 1 origin 7c76070faf9b19e6a417c446043dbafd10a7aa1d
    git checkout FETCH_HEAD

Then, from the repo root:

    python3 blogwalk/build-manifest.py <path-to-website>/content/en/blog/_posts

A post is any file under _posts carrying YAML frontmatter with a title. That
definition, not the file extension, is what matches Hugo: two 2022 posts have
no extension at all, one post opens with a UTF-8 BOM, two open with a blank
line, and one opens with six dashes instead of three. All six are published.
"""
import os, re, sys
from collections import Counter, defaultdict

PIN = "7c76070faf9b19e6a417c446043dbafd10a7aa1d"
PIN_DATE = "2026-08-26"

# Per-year post counts recorded on the map, asserted on every run so a moved
# pin or a broken parser is loud rather than silent.
# 2026 is 70, not the 69 the map's table records: 69 posts live in _posts/2026/ and
# one more, _posts/2026-03-20-etcd-370-beta.md, sits loose at the root of _posts with a
# frontmatter date of 2026-05-20. It is a real published post, so it counts, and it
# counts as 2026. Total at this pin is 767, of which 756 are published.
EXPECTED = {'2015': 44, '2016': 90, '2017': 53, '2018': 70, '2019': 52, '2020': 56,
            '2021': 53, '2022': 69, '2023': 78, '2024': 54, '2025': 78, '2026': 70}

ASSET_EXT = {'.png', '.svg', '.jpg', '.jpeg', '.gif', '.webp', '.pdf',
             '.xcf', '.drawio', '.mmd', '.mermaid', '.go', '.yaml', '.yml'}


def frontmatter(path):
    """Parse leading YAML frontmatter as Hugo tolerates it, or return None."""
    try:
        with open(path, encoding='utf-8-sig') as f:      # utf-8-sig strips the BOM
            lines = f.read().split('\n')
    except (UnicodeDecodeError, OSError):
        return None
    i = 0
    while i < len(lines) and not lines[i].strip():        # leading blank lines
        i += 1
    if i >= len(lines) or not re.fullmatch(r'-{3,}', lines[i].strip()):   # '---' or '------'
        return None
    fm, key = {}, None
    for line in lines[i + 1:]:
        if re.fullmatch(r'(-{3,}|\.{3})', line.strip()):
            break
        m = re.match(r'^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$', line)
        if m:
            key = m.group(1)
            fm[key] = m.group(2).strip()
        elif key and line.strip():                        # folded scalar, e.g. 'author: >'
            fm[key] = (fm[key] + ' ' + line.strip()).strip()
    return fm


def clean(v):
    v = (v or '').strip()
    if len(v) > 1 and v[0] in '"\'' and v[-1] == v[0]:
        v = v[1:-1]
    return re.sub(r'\s+', ' ', v).strip()


def collect(root):
    rows, notes = [], []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for fn in sorted(filenames):
            if os.path.splitext(fn)[1].lower() in ASSET_EXT:
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, root).replace(os.sep, '/')
            fm = frontmatter(full)
            if fm is None or 'title' not in fm:
                notes.append(('not-a-post', rel, 'no frontmatter title'))
                continue
            top = rel.split('/')[0]
            dir_year = top if re.fullmatch(r'\d{4}', top) else ''
            date = clean(fm.get('date'))
            date_year = date[:4] if re.match(r'^\d{4}', date) else ''
            if not dir_year:
                notes.append(('outside-year-dir', rel, f'date={date or "none"}'))
            elif date_year and dir_year != date_year:
                notes.append(('year-mismatch', rel, f'dir={dir_year} date={date_year}'))
            if not date:
                notes.append(('no-date', rel, ''))
            rows.append({
                'year': date_year or dir_year or '?',
                'date': date,
                'draft': 'true' if clean(fm.get('draft')).lower() == 'true' else 'false',
                'bytes': str(os.path.getsize(full)),
                'path': rel,
                'slug': clean(fm.get('slug')),
                'title': clean(fm.get('title')),
            })
    rows.sort(key=lambda r: (r['year'], r['date'] or '~', r['path']))
    dupes = {s for s, c in Counter(r['slug'] for r in rows if r['slug']).items() if c > 1}
    for r in rows:
        if r['slug'] in dupes:
            notes.append(('dup-slug', r['path'], r['slug']))
    return rows, notes


COLUMNS = ['year', 'date', 'draft', 'bytes', 'path', 'slug', 'title']


def write(rows, out):
    with open(out, 'w', encoding='utf-8') as f:
        f.write(f'# kubernetes/website @ {PIN} ({PIN_DATE})\n')
        f.write('# generated by blogwalk/build-manifest.py -- do not hand-edit\n')
        f.write('# consumers skip lines beginning with "#"\n')
        f.write('\t'.join(COLUMNS) + '\n')
        for r in rows:
            vals = [r[c] for c in COLUMNS]
            bad = next((c for c, v in zip(COLUMNS, vals) if '\t' in v), None)
            if bad:
                raise SystemExit(f'tab inside {bad} of {r["path"]}')
            f.write('\t'.join(vals) + '\n')


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    root = sys.argv[1]
    rows, notes = collect(root)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'manifest.tsv')
    write(rows, out)

    per_year = defaultdict(lambda: [0, 0])
    for r in rows:
        per_year[r['year']][0] += 1
        per_year[r['year']][1] += r['draft'] == 'true'

    print(f'{"year":<6}{"posts":>7}{"draft":>7}{"published":>11}{"expected":>10}')
    total = drafts = 0
    mismatches = []
    for y in sorted(per_year):
        n, d = per_year[y]
        total += n
        drafts += d
        exp = EXPECTED.get(y)
        flag = ''
        if exp is not None and exp != n:
            # the misplaced root-level post lands in its frontmatter year, not a directory
            flag = ' <-- differs from map'
            mismatches.append((y, n, exp))
        print(f'{y:<6}{n:>7}{d:>7}{n - d:>11}{str(exp or "-"):>10}{flag}')
    print(f'{"TOTAL":<6}{total:>7}{drafts:>7}{total - drafts:>11}')

    print('\nfindings')
    for kind, rel, note in sorted(set(notes)):
        print(f'  {kind:<17} {rel} {note}')
    print(f'\n{len(rows)} rows -> {out}')
    if mismatches:
        print('\nreview the differences above before trusting this manifest.')


if __name__ == '__main__':
    main()
