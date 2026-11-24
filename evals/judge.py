#!/usr/bin/env python3
"""Judge where a map's proposals fall on the evidence grid — the metric keyword scoring cannot see.

    python3 evals/judge.py eval-runs/<timestamp>                    # one run
    python3 evals/judge.py before=runs/a after=runs/b               # compare runs, side by side
    python3 evals/judge.py runs/a --agreement                       # judge every map twice: how stable is the judge?
    python3 evals/judge.py --label-sheet runs/a/x/sonnet/skill/map.md   # a sheet for a human to label one map

For every map.md under each root (laid out <scenario>/<model>/<arm>[/r<N>]/map.md by run.py), a judge
model reads the map and lists what it PROPOSES — not what it says exists, not what it rejects —
each as a card or as a script run through another proposal, with its way (bring out · witness ·
reach in · loop) and level (unit · piece · operation · journey), plus the first milestone's cell and
whether the skill author's tools (motu, assay) were proposed. The judge is told the definitions,
never which answer is wanted.

Reported per run label, arm and model (all repeats pooled):
  - the cells each map REACHES — a cell counts once however many proposals land in it, scripts
    under a primitive included — and those cells by way and level. Counting proposals instead lets
    one runner with eight scripts outweigh one lab; counting cards only hides a map whose substance
    is scripts under one primitive, which is the design the skill asks for;
  - the busiest cell's share of all proposals (1.0 = everything in one cell);
  - M1's cell, and how often it is loop-only (environments, launch);
  - author tools proposed where the scenario says they do not fit — must be 0;
  - against the answer keys (evals/answer-keys/<scenario>.md), when filled: the expected cells a map
    reached, the cells it should have left alone and did not, and whether M1 is an accepted cell.

--agreement judges each map a second time (judge.2.json) and reports how often the two judgments
agree. A labels.md filled by a human (--label-sheet) is compared with the judge the same way.

Writes judge.json next to each map and distribution.md / distribution.json at the first root.
Needs the `claude` CLI logged in. About 1–2 cents per map with sonnet.
"""
import argparse, json, re, statistics, subprocess, sys
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
KEYS = HERE / 'answer-keys'
WAYS = ['bring out', 'witness', 'reach in']
LEVELS = ['unit', 'piece', 'operation', 'journey']
VERSION = 2  # bump when PROMPT changes: older judge.json files are judged again

PROMPT = """You are classifying the proposals in a document about developer tooling for coding agents.
The document is below, between <doc> tags. Read it and answer ONLY with one JSON object, in a ```json fence.

List every handle, tool, script or capability the document PROPOSES to build, adopt, finish or configure.
Do NOT list what it says already exists and is fine as is, nor what it explicitly rejects or says does not fit.
Merge duplicates (the same handle described twice is one entry).

For each proposal give:
- "name": short name as the document writes it
- "kind": "script" if it is a script, subcommand or verb run THROUGH another proposed runner, console or
          primitive (e.g. `agent run clock` under an `agent run` runner); otherwise "card"
- "way": where the agent stands when it uses it —
    "reach in"  = it acts on or observes the real running app (log in, call it, eval in it, screenshot it, drive the browser against it);
    "bring out" = it runs a piece of the app, or a replica of it or of its surroundings, outside the live app
                  (unit or component tests, a component/story lab, a scene harness, a mock server, a fixture-driven run, a local engine);
    "witness"   = it records what the app wrote, sent or called (database writes, outbound HTTP, mail, jobs, files) to inspect or check it;
    "loop"      = it only launches, isolates, resets or parallelises (environments, containers, displays, ports, doctor scripts, CI wiring)
- "level": how much of the app is present when it gives its result —
    "unit" = a function or query alone; "piece" = one component, screen, scene, model or subcommand;
    "operation" = one request, job, webhook, command or model build; "journey" = the whole app across operations, as a user;
    "none" for loop-only proposals
- "designed": true if the document gives a concrete command, call or URL showing how an agent would use it

Also give:
- "m1": the first milestone or first priority, as {"name": ..., "way": ..., "level": ...} (null if there is no ordering)
- "author_tools": for each of "motu" and "assay": "proposed", "rejected" (named but said not to fit or not chosen), or "absent"

JSON shape:
{"proposals": [{"name": "", "kind": "card", "way": "", "level": "", "designed": true}], "m1": {"name": "", "way": "", "level": ""}, "author_tools": {"motu": "", "assay": ""}}

<doc>
{doc}
</doc>"""


def ask(text, model):
    p = subprocess.run(['claude', '-p', PROMPT.replace('{doc}', text[:150000]), '--model', model, '--output-format', 'json'],
                       text=True, capture_output=True, timeout=600)
    out = json.loads(p.stdout)['result']
    m = re.search(r'```json\s*(.*?)```', out, re.S)
    j = json.loads(m.group(1) if m else out)
    j['v'] = VERSION
    return j


def norm(v, allowed):
    v = (v or '').lower().strip()
    return next((a for a in allowed if a in v), 'none')


def cell(p):
    """'<level> × <way>' for a proposal, 'loop' for loop-only ones, None when unclassifiable."""
    w, lv = norm(p.get('way'), WAYS + ['loop']), norm(p.get('level'), LEVELS)
    if w == 'loop':
        return 'loop'
    return f'{lv} × {w}' if 'none' not in (w, lv) else None


# ---------------------------------------------------------------- answer keys

def read_key(name):
    """evals/answer-keys/<name>.md → {'cells': {cell: propose|leave|either}, 'm1': [cells] or ['any'], 'by': str}
    — None while nobody has filled it in. Blank rows are not scored."""
    p = KEYS / f'{name}.md'
    if not p.exists():
        return None
    text = p.read_text()
    cells = {}
    for line in text.splitlines():
        m = re.match(r'^\|\s*`?([a-z]+ × [a-z ]+|loop)`?\s*\|\s*`?(propose|leave|either)?`?\s*\|', line.strip(), re.I)
        if m and m.group(2):
            cells[m.group(1).strip().lower()] = m.group(2).lower()
    m1 = re.search(r'\*\*M1 accepted:\*\*\s*(.*)', text)
    m1 = [x.strip().strip('`').lower() for x in re.split(r',|;', m1.group(1))] if m1 and m1.group(1).strip() and '<' not in m1.group(1) else []
    by = re.search(r'\*\*Filled by:\*\*\s*(.*)', text)
    by = by.group(1).strip() if by and '<' not in by.group(1) else ''
    return {'cells': cells, 'm1': [x for x in m1 if x], 'by': by} if (cells or m1) else None


def against_key(reached, m1, key):
    if not key:
        return None
    want = [c for c, e in key['cells'].items() if e == 'propose']
    avoid = [c for c, e in key['cells'].items() if e == 'leave']
    return {'hit': sum(c in reached for c in want), 'want': len(want),
            'false': sum(c in reached for c in avoid), 'avoid': len(avoid),
            'm1_ok': (None if not key['m1'] else ('any' in key['m1'] or m1 in key['m1']))}


# ---------------------------------------------------------------- metrics

def metrics(j, sc, key):
    props = j.get('proposals') or []
    cards = [p for p in props if (p.get('kind') or 'card').lower() != 'script']
    cells = [cell(p) for p in props]
    in_cells = [c for c in cells if c and c != 'loop']
    cc = Counter(in_cells)
    distinct = sorted(cc)
    fit = set(sc.get('author_tools_fit', [])) | set(sc.get('author_tools_borderline', []))
    at = j.get('author_tools') or {}
    m1 = cell(j.get('m1') or {}) if j.get('m1') else None
    reached = set(in_cells) | ({'loop'} if 'loop' in cells else set())
    return {
        'cards': len(cards), 'scripts': len(props) - len(cards), 'loop_only': cells.count('loop'), 'in_cells': len(distinct),
        'ways': {w: sum(c.endswith(w) for c in distinct) for w in WAYS},
        'levels': {lv: sum(c.startswith(lv) for c in distinct) for lv in LEVELS},
        'cells': sorted(reached), 'cells_reached': len(cc),
        'busiest_cell': (max(cc.values()) / len(in_cells)) if in_cells else None,  # share of all proposals in cells
        'busiest': cc.most_common(1)[0][0] if cc else '',
        'm1': m1 or '—',
        'author_misfit': [t for t in ('motu', 'assay') if (at.get(t) or '').startswith('proposed') and t not in fit],
        'author': {t: at.get(t, 'absent') for t in ('motu', 'assay')},
        'key': against_key(reached, m1, key),
    }


def agreement(a, b):
    """How far two classifications of one map agree: M1's cell, the set of cells reached, way shares."""
    ca, cb = set(a['cells']), set(b['cells'])
    share = lambda m: [m['ways'][w] / (m['in_cells'] or 1) for w in WAYS]
    return {'m1_same': a['m1'] == b['m1'], 'cells_jaccard': len(ca & cb) / len(ca | cb) if ca | cb else 1.0,
            'way_share_gap': max(abs(x - y) for x, y in zip(share(a), share(b)))}


def where(mp):
    """(scenario, model, arm, run) from <scenario>/<model>/<arm>[/r<N>]/map.md."""
    parts = mp.parts
    if re.fullmatch(r'r\d+', parts[-2]):
        return parts[-5], parts[-4], parts[-3], int(parts[-2][1:])
    return parts[-4], parts[-3], parts[-2], 1


def collect(roots, model, jobs, twice):
    scen = {json.loads(p.read_text())['name']: json.loads(p.read_text()) for p in (HERE / 'scenarios').glob('*.json')}
    # a run directory holds map.md files; a committed result set may hold only their judge.json
    todo = [(label, jp.with_name('map.md')) for label, root in roots
            for jp in sorted({*Path(root).glob('**/map.md'), *Path(root).glob('**/judge.json')}, key=str)
            if jp.name == 'map.md' or not jp.with_name('map.md').exists()]

    def judged(mp, name):
        jp = mp.with_name(name)
        if jp.exists():
            j = json.loads(jp.read_text())
            if j.get('v') == VERSION:
                return j
        if not mp.exists():  # judge outputs without the map: nothing to judge again
            return None
        text = mp.read_text(errors='ignore')
        if not text.strip():
            return None
        try:
            j = ask(text, model)
        except Exception as e:  # a judge failure is reported, never scored as zero
            print(f'  judge failed on {mp}: {e}', file=sys.stderr)
            return None
        jp.write_text(json.dumps(j, indent=1))
        return j

    def one(t):
        label, mp = t
        sc, mdl, arm, run = where(mp)
        j = judged(mp, 'judge.json')
        if j is None:
            return None
        key = read_key(sc)
        row = {'label': label, 'scenario': sc, 'model': mdl, 'arm': arm, 'run': run, **metrics(j, scen.get(sc, {}), key)}
        if twice:
            j2 = judged(mp, 'judge.2.json')
            if j2 is not None:
                row['agreement'] = agreement(row, metrics(j2, scen.get(sc, {}), key))
        human = read_labels(mp.with_name('labels.md'))
        if human:
            row['human'] = human_agreement(j, human)
        return row
    with ThreadPoolExecutor(jobs) as ex:
        return [r for r in ex.map(one, todo) if r]


# ---------------------------------------------------------------- human labels

def label_sheet(mp, model):
    """Write labels.md beside a map: the judge's classification of each proposal, with empty columns for a human."""
    j = json.loads(mp.with_name('judge.json').read_text()) if mp.with_name('judge.json').exists() else ask(mp.read_text(), model)
    rows = '\n'.join(f'| {p.get("name", "").replace("|", "/")} | {p.get("kind", "card")} | {norm(p.get("way"), WAYS + ["loop"])} | '
                     f'{norm(p.get("level"), LEVELS)} |  |  |  |' for p in j.get('proposals') or [])
    m1 = j.get('m1') or {}
    out = mp.with_name('labels.md')
    out.write_text(f"""# Labels — {mp}

Read the map yourself, then fill the three right-hand columns: **your kind** (card · script), **your
way** (bring out · witness · reach in · loop), **your level** (unit · piece · operation · journey · none).
Leave a cell empty to agree with the judge. Add a row for anything the judge missed; strike a row
(`~~name~~`) for anything it listed that the map does not propose. Definitions: evals/judge.py, PROMPT.

**Judge's M1:** {cell(m1) or '—'} ({m1.get('name', '')}) · **Your M1:**

| Proposal | Judge kind | Judge way | Judge level | Your kind | Your way | Your level |
|---|---|---|---|---|---|---|
{rows}
""")
    return out


def read_labels(p):
    if not p.exists():
        return None
    rows, m1 = [], None
    for line in p.read_text().splitlines():
        if line.startswith('**Judge\'s M1:**'):
            m = re.search(r'\*\*Your M1:\*\*\s*(.*)', line)
            m1 = m.group(1).strip() if m and m.group(1).strip() else None
        c = [x.strip() for x in line.strip().strip('|').split('|')]
        if len(c) == 7 and c[0] and not c[0].startswith(('Proposal', '---')):
            rows.append(c)
    filled = [r for r in rows if any(r[4:]) or r[0].startswith('~~')]
    return {'rows': rows, 'm1': m1} if (filled or m1) else None


def human_agreement(j, human):
    """Share of the judge's proposals whose cell the human left unchanged; M1 agreement when given."""
    same = total = 0
    for r in human['rows']:
        if r[0].startswith('~~'):
            total += 1
            continue
        total += 1
        same += not any(r[4:]) or (norm(r[5] or r[2], WAYS + ['loop']) == norm(r[2], WAYS + ['loop'])
                                   and norm(r[6] or r[3], LEVELS) == norm(r[3], LEVELS))
    judge_m1 = cell(j.get('m1') or {})
    return {'cells_same': same / total if total else None,
            'm1_same': None if not human['m1'] else human['m1'].lower().replace('x', '×') == (judge_m1 or '')}


# ---------------------------------------------------------------- report

def pct(n, d):
    return f'{100 * n // d}%' if d else '—'


def table(rows):
    groups = defaultdict(list)
    for r in rows:
        groups[(r['label'], r['arm'], r['model'])].append(r)
    out = ['| Run | Arm | Model | Maps | Cards · scripts · loop-only | Cells reached, by way: Bring out · Witness · Reach in | by level: Unit · Piece · Operation · Journey '
           '| Cells reached per map (of 12) | Busiest cell share (mean ± sd) | M1 loop-only | M1 cells | Author misfit |',
           '|---|---|---|---|---|---|---|---|---|---|---|---|']
    for (label, arm, mdl), rs in sorted(groups.items()):
        n = sum(r['in_cells'] for r in rs)
        bc = [r['busiest_cell'] for r in rs if r['busiest_cell'] is not None]
        sd = f' ± {statistics.stdev(bc):.2f}' if len(bc) > 1 else ''
        m1 = Counter(r['m1'] for r in rs).most_common()
        out.append(f'| {label} | {arm} | {mdl} | {len(rs)} | {sum(r["cards"] for r in rs)} · {sum(r["scripts"] for r in rs)} · {sum(r["loop_only"] for r in rs)} | '
                   f'{" · ".join(pct(sum(r["ways"][w] for r in rs), n) for w in WAYS)} | '
                   f'{" · ".join(pct(sum(r["levels"][lv] for r in rs), n) for lv in LEVELS)} | '
                   f'{sum(r["cells_reached"] for r in rs) / len(rs):.1f} | {(sum(bc) / len(bc)) if bc else 0:.2f}{sd} | '
                   f'{sum(r["m1"] == "loop" for r in rs)}/{len(rs)} | {", ".join(f"{k} ×{v}" for k, v in m1)} | '
                   f'{sum(len(r["author_misfit"]) for r in rs)} |')
    return '\n'.join(out)


def key_table(rows):
    keyed = [r for r in rows if r['key']]
    if not keyed:
        return ('No answer key filled yet (evals/answer-keys/) — nothing scored against one. Each map is scored '
                'once a key exists; judge outputs are cached, so filling a key later costs nothing to score.')
    groups = defaultdict(list)
    for r in keyed:
        groups[(r['label'], r['arm'], r['model'])].append(r)
    out = ['| Run | Arm | Model | Maps scored | Expected cells reached | Cells to leave, proposed anyway | M1 in an accepted cell |',
           '|---|---|---|---|---|---|---|']
    for (label, arm, mdl), rs in sorted(groups.items()):
        k = [r['key'] for r in rs]
        m1 = [x['m1_ok'] for x in k if x['m1_ok'] is not None]
        out.append(f'| {label} | {arm} | {mdl} | {len(rs)} | {sum(x["hit"] for x in k)}/{sum(x["want"] for x in k)} | '
                   f'{sum(x["false"] for x in k)}/{sum(x["avoid"] for x in k)} | {sum(m1)}/{len(m1)} |' if m1 else
                   f'| {label} | {arm} | {mdl} | {len(rs)} | {sum(x["hit"] for x in k)}/{sum(x["want"] for x in k)} | '
                   f'{sum(x["false"] for x in k)}/{sum(x["avoid"] for x in k)} | — |')
    keys = sorted({r['scenario'] for r in keyed})
    return '\n'.join(out) + f'\n\nKeys used: {", ".join(keys)}.'


def stability_table(rows):
    """Run-to-run spread: for each scenario × arm × model with several runs, does M1 land in the same cell?"""
    groups = defaultdict(list)
    for r in rows:
        groups[(r['label'], r['scenario'], r['arm'], r['model'])].append(r)
    multi = {k: v for k, v in groups.items() if len(v) > 1}
    if not multi:
        return ''
    out = ['| Run | Scenario | Arm | Model | Runs | M1 cells across runs | Busiest share per run |', '|---|---|---|---|---|---|---|']
    for (label, sc, arm, mdl), rs in sorted(multi.items()):
        rs = sorted(rs, key=lambda r: r['run'])
        out.append(f'| {label} | {sc} | {arm} | {mdl} | {len(rs)} | {", ".join(r["m1"] for r in rs)} | '
                   f'{", ".join(f"{(r["busiest_cell"] or 0):.2f}" for r in rs)} |')
    return '\n'.join(out)


def agreement_table(rows):
    out = []
    a = [r['agreement'] for r in rows if 'agreement' in r]
    if a:
        out.append(f'**Judge vs itself** ({len(a)} maps judged twice): M1 cell the same in {sum(x["m1_same"] for x in a)}/{len(a)}; '
                   f'cells reached overlap (Jaccard) {statistics.mean(x["cells_jaccard"] for x in a):.2f} on average; '
                   f'largest way-share gap {statistics.mean(x["way_share_gap"] for x in a):.2f} on average.')
    h = [r['human'] for r in rows if 'human' in r]
    if h:
        cs = [x['cells_same'] for x in h if x['cells_same'] is not None]
        m1 = [x['m1_same'] for x in h if x['m1_same'] is not None]
        out.append(f'**Judge vs human** ({len(h)} maps labelled): proposals in the same cell {statistics.mean(cs):.0%}'
                   + (f'; M1 the same in {sum(m1)}/{len(m1)}' if m1 else '') + '.')
    return '\n\n'.join(out)


def per_map(rows):
    out = ['| Run | Scenario | Model | Arm | # | Cards | Cells | Busiest | M1 | motu | assay |', '|---|---|---|---|---|---|---|---|---|---|---|']
    for r in sorted(rows, key=lambda r: (r['scenario'], r['model'], r['arm'], r['label'], r['run'])):
        out.append(f'| {r["label"]} | {r["scenario"]} | {r["model"]} | {r["arm"]} | {r["run"]} | {r["cards"]} | {r["cells_reached"]} | '
                   f'{r["busiest"]} ({(r["busiest_cell"] or 0):.2f}) | {r["m1"]} | {r["author"]["motu"]} | {r["author"]["assay"]} |')
    return '\n'.join(out)


def main():
    ap = argparse.ArgumentParser(description='Judge where map proposals fall on the evidence grid.')
    ap.add_argument('roots', nargs='*', help='run directories, optionally label=path')
    ap.add_argument('--model', default='sonnet', help='judge model (default sonnet)')
    ap.add_argument('--jobs', type=int, default=6)
    ap.add_argument('--agreement', action='store_true', help='judge every map a second time and report agreement')
    ap.add_argument('--label-sheet', type=Path, metavar='MAP', help='write labels.md beside MAP for a human to fill, and stop')
    a = ap.parse_args()
    if a.label_sheet:
        print(label_sheet(a.label_sheet, a.model))
        return
    if not a.roots:
        ap.error('give at least one run directory')
    roots = [tuple(r.split('=', 1)) if '=' in r else (Path(r).name, r) for r in a.roots]
    rows = collect(roots, a.model, a.jobs, a.agreement)
    if not rows:
        sys.exit('judge: no map.md judged')
    parts = ['## Distribution (cells reached; each cell counted once per map)', table(rows),
             '## Against the answer keys', key_table(rows)]
    st = stability_table(rows)
    if st:
        parts += ['## Run to run', st]
    ag = agreement_table(rows)
    if ag:
        parts += ['## How far to trust the judge', ag]
    parts += ['## Per map', per_map(rows)]
    md = '\n\n'.join(parts) + '\n'
    first = Path(roots[0][1])
    (first / 'distribution.json').write_text(json.dumps(rows, indent=1))
    (first / 'distribution.md').write_text(md)
    print(md)


if __name__ == '__main__':
    main()
