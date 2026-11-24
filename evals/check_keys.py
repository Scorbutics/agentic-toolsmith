#!/usr/bin/env python3
"""Check the bookkeeping of bug-grounded answer keys, so a person only has to judge the bugs.

    python3 evals/check_keys.py                      # every key in evals/answer-keys with an evidence table
    python3 evals/check_keys.py --private DIR ...     # also private keys (DIR holds scenario.json + answer-key.md)

For each key that has an "## Evidence — fixed bugs" table:
  - every commit cited anywhere in the key exists in the repository and is an ancestor of the pinned
    commit (a fix from after the pin cannot be evidence for it);
  - the evidence table, recounted per cell, agrees with each row's Expect under the drafting rule:
    `propose` needs ≥ 2 bugs in that cell, or 1 marked severe in the Why column — anything else is
    flagged for a look, not failed;
  - every `leave` row gives a structural reason (it must not rest on "no bug landed here").

Uses the eval cache (the clones run.py makes); clones a repository there if it is missing.
Exit 0: nothing to look at · 1: a citation is wrong (missing, or after the pin) · notes alone exit 0.
"""
import argparse, json, re, subprocess, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from run import CACHE, checkout  # noqa: E402  (same cache, same pinned checkout)

CELL = re.compile(r'`((?:unit|piece|operation|journey) × (?:bring out|witness|reach in)|loop)`')
HASH = re.compile(r'(?<![0-9a-f/])([0-9a-f]{7,40})(?![0-9a-f])')
SEVERE = re.compile(r'data loss|security|lost|money|wrong numbers|silently|crash|corrupt|sent wrongly|wrong data', re.I)


def git(repo, *args):
    return subprocess.run(['git', '-C', str(repo), *args], text=True, capture_output=True)


def check(key_path, sc):
    text = key_path.read_text()
    if '## Evidence' not in text:
        return None
    repo = CACHE / sc['name']
    if not (repo / '.git').exists():
        checkout(sc)
    pin = sc['commit']
    errors, notes = [], []
    evidence = text.split('## Evidence', 1)[1].split('## Excluded', 1)[0]
    cited = sorted(set(HASH.findall(text)) - {pin[:len(h)] for h in HASH.findall(text) if pin.startswith(h)})
    for h in cited:
        if git(repo, 'cat-file', '-e', f'{h}^{{commit}}').returncode:
            errors.append(f'{h}: no such commit')
        elif git(repo, 'merge-base', '--is-ancestor', h, pin).returncode:
            errors.append(f'{h}: not an ancestor of the pinned commit {pin[:7]}')
    per_cell, severe = Counter(), Counter()
    for line in evidence.splitlines():
        cols = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cols) >= 4 and HASH.search(cols[0]):
            m = CELL.search(cols[2])
            if m:
                per_cell[m.group(1)] += 1
                severe[m.group(1)] += bool(SEVERE.search(cols[1] + ' ' + cols[3]))
            else:
                notes.append(f'{cols[0]}: evidence row names no cell')
    for line in text.split('## Evidence', 1)[0].splitlines():
        cols = [c.strip() for c in line.strip().strip('|').split('|')]
        m = CELL.fullmatch(cols[0]) if cols else None
        if not m or len(cols) < 3:
            continue
        c, expect, why = m.group(1), cols[1].strip('` ').lower(), cols[2]
        n = per_cell[c]
        if c == 'loop':
            continue  # the loop row counts environment-caused bugs, which the table does not tag
        if expect == 'propose' and n < 2 and not severe[c] and not SEVERE.search(why):
            notes.append(f'{c}: propose on {n} bug(s), none marked severe — check')
        if expect in ('either', '') and n >= 2:
            notes.append(f'{c}: {n} bugs in the evidence but marked `{expect or "empty"}` — check')
        if expect == 'leave' and (n or re.search(r'no bug|none landed|no evidence', why, re.I)):
            notes.append(f'{c}: leave with {n} bug(s) / a reason that is absence of bugs — a leave must be structural')
    return {'cited': len(cited), 'bugs': sum(per_cell.values()), 'errors': errors, 'notes': notes}


def main():
    ap = argparse.ArgumentParser(description='Check the citations and counts of bug-grounded answer keys.')
    ap.add_argument('--private', action='append', type=Path, default=[], metavar='DIR')
    a = ap.parse_args()
    items = []
    for p in sorted((HERE / 'answer-keys').glob('*.md')):
        sp = HERE / 'scenarios' / f'{p.stem}.json'
        if sp.exists():
            items.append((p, json.loads(sp.read_text())))
    items += [(d / 'answer-key.md', json.loads((d / 'scenario.json').read_text())) for d in a.private]
    bad = 0
    for p, sc in items:
        r = check(p, sc)
        if r is None:
            continue
        bad += bool(r['errors'])
        print(f'{sc["name"]}: {r["cited"]} commits cited, {r["bugs"]} bugs in the evidence — '
              + ('citations OK' if not r['errors'] else f'{len(r["errors"])} citation error(s)'))
        for e in r['errors']:
            print(f'  ✗ {e}')
        for n in r['notes']:
            print(f'  · {n}')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
