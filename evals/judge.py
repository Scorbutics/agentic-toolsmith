#!/usr/bin/env python3
"""Judge where a map's proposals fall on the evidence grid — the metric keyword scoring cannot see.

    python3 evals/judge.py eval-runs/<timestamp>                    # one run
    python3 evals/judge.py before=runs/a after=runs/b               # compare two runs, side by side

For every map.md under each root (laid out <scenario>/<model>/<arm>/map.md by run.py), a judge
model reads the map and lists what it PROPOSES — not what it says exists, not what it rejects —
each with its way (bring out · witness · reach in · loop) and level (unit · piece · operation ·
journey), plus the first milestone's cell and whether the skill author's tools (motu, assay) were
proposed. The judge is told the definitions, never which answer is wanted.

Reported per arm and model:
  - way and level shares of the proposed handles (loop-only handles counted apart);
  - cells: how many distinct level × way cells the proposals reach, and the share of the busiest
    one (1.0 = everything in one cell — "it always suggests the same thing");
  - M1's cell;
  - author tools proposed where the scenario says they do not fit (`author_tools_fit`) — must be 0.

Writes judge.json next to each map and distribution.md / distribution.json at the first root.
Needs the `claude` CLI logged in. About 1–2 cents per map with sonnet.
"""
import argparse, json, re, subprocess, sys
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
WAYS = ['bring out', 'witness', 'reach in']
LEVELS = ['unit', 'piece', 'operation', 'journey']

PROMPT = """You are classifying the proposals in a document about developer tooling for coding agents.
The document is below, between <doc> tags. Read it and answer ONLY with one JSON object, in a ```json fence.

List every handle, tool, script or capability the document PROPOSES to build, adopt, finish or configure.
Do NOT list what it says already exists and is fine as is, nor what it explicitly rejects or says does not fit.
Merge duplicates (the same handle described twice is one entry).

For each proposal give:
- "name": short name as the document writes it
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
{"proposals": [{"name": "", "way": "", "level": "", "designed": true}], "m1": {"name": "", "way": "", "level": ""}, "author_tools": {"motu": "", "assay": ""}}

<doc>
{doc}
</doc>"""


def ask(text, model):
    p = subprocess.run(['claude', '-p', PROMPT.replace('{doc}', text[:150000]), '--model', model, '--output-format', 'json'],
                       text=True, capture_output=True, timeout=600)
    out = json.loads(p.stdout)['result']
    m = re.search(r'```json\s*(.*?)```', out, re.S)
    return json.loads(m.group(1) if m else out)


def norm(v, allowed):
    v = (v or '').lower().strip()
    return next((a for a in allowed if a in v), 'none')


def metrics(j, sc):
    props = j.get('proposals') or []
    loop = [p for p in props if norm(p.get('way'), WAYS + ['loop']) in ('loop', 'none')]
    cell = [(norm(p.get('way'), WAYS), norm(p.get('level'), LEVELS)) for p in props if p not in loop]
    cell = [c for c in cell if 'none' not in c]
    cc = Counter(cell)
    fit = set(sc.get('author_tools_fit', [])) | set(sc.get('author_tools_borderline', []))
    at = j.get('author_tools') or {}
    m1 = j.get('m1') or {}
    return {
        'proposals': len(props), 'loop_only': len(loop), 'in_cells': len(cell),
        'designed': sum(bool(p.get('designed')) for p in props),
        'ways': {w: sum(c[0] == w for c in cell) for w in WAYS},
        'levels': {lv: sum(c[1] == lv for c in cell) for lv in LEVELS},
        'cells_reached': len(cc), 'busiest_cell': (max(cc.values()) / len(cell)) if cell else None,
        'busiest': '%s × %s' % cc.most_common(1)[0][0] if cc else '',
        'm1': f'{norm(m1.get("level"), LEVELS)} × {norm(m1.get("way"), WAYS + ["loop"])}' if m1 else '—',
        'author_misfit': [t for t in ('motu', 'assay') if (at.get(t) or '').startswith('proposed') and t not in fit],
        'author': {t: at.get(t, 'absent') for t in ('motu', 'assay')},
    }


def collect(roots, model, jobs):
    scen = {json.loads(p.read_text())['name']: json.loads(p.read_text()) for p in (HERE / 'scenarios').glob('*.json')}
    todo = []
    for label, root in roots:
        for mp in sorted(Path(root).glob('**/map.md')):
            sc, mdl, arm = mp.parts[-4], mp.parts[-3], mp.parts[-2]
            todo.append((label, sc, mdl, arm, mp))

    def one(t):
        label, sc, mdl, arm, mp = t
        jp = mp.with_name('judge.json')
        if jp.exists():
            j = json.loads(jp.read_text())
        else:
            text = mp.read_text(errors='ignore')
            if not text.strip():
                return None
            try:
                j = ask(text, model)
            except Exception as e:  # a judge failure is reported, never scored as zero
                print(f'  judge failed on {mp}: {e}', file=sys.stderr)
                return None
            jp.write_text(json.dumps(j, indent=1))
        return {'label': label, 'scenario': sc, 'model': mdl, 'arm': arm, **metrics(j, scen.get(sc, {}))}
    with ThreadPoolExecutor(jobs) as ex:
        return [r for r in ex.map(one, todo) if r]


def table(rows):
    groups = defaultdict(list)
    for r in rows:
        groups[(r['label'], r['arm'], r['model'])].append(r)
    out = ['| Run | Arm | Model | Maps | Proposals (in cells / loop) | Bring out · Witness · Reach in | Unit · Piece · Operation · Journey | Cells reached (of 12) | Busiest cell share | M1 cells | Author tools misfit |',
           '|---|---|---|---|---|---|---|---|---|---|---|']
    for (label, arm, mdl), rs in sorted(groups.items()):
        n = sum(r['in_cells'] for r in rs) or 1
        ways = ' · '.join(f'{100 * sum(r["ways"][w] for r in rs) // n}%' for w in WAYS)
        lvls = ' · '.join(f'{100 * sum(r["levels"][lv] for r in rs) // n}%' for lv in LEVELS)
        bc = [r['busiest_cell'] for r in rs if r['busiest_cell'] is not None]
        m1 = Counter(r['m1'] for r in rs).most_common()
        mis = sum(len(r['author_misfit']) for r in rs)
        out.append(f'| {label} | {arm} | {mdl} | {len(rs)} | {sum(r["in_cells"] for r in rs)} / {sum(r["loop_only"] for r in rs)} | {ways} | {lvls} | '
                   f'{sum(r["cells_reached"] for r in rs) / len(rs):.1f} | {sum(bc) / len(bc):.2f} | '
                   f'{", ".join(f"{k} ×{v}" for k, v in m1)} | {mis} |')
    return '\n'.join(out)


def per_map(rows):
    out = ['| Run | Scenario | Model | Arm | Cells | Busiest | M1 | motu | assay |', '|---|---|---|---|---|---|---|---|---|']
    for r in sorted(rows, key=lambda r: (r['scenario'], r['model'], r['arm'], r['label'])):
        out.append(f'| {r["label"]} | {r["scenario"]} | {r["model"]} | {r["arm"]} | {r["cells_reached"]} | {r["busiest"]} '
                   f'({(r["busiest_cell"] or 0):.2f}) | {r["m1"]} | {r["author"]["motu"]} | {r["author"]["assay"]} |')
    return '\n'.join(out)


def main():
    ap = argparse.ArgumentParser(description='Judge where map proposals fall on the evidence grid.')
    ap.add_argument('roots', nargs='+', help='run directories, optionally label=path')
    ap.add_argument('--model', default='sonnet', help='judge model (default sonnet)')
    ap.add_argument('--jobs', type=int, default=6)
    a = ap.parse_args()
    roots = [tuple(r.split('=', 1)) if '=' in r else (Path(r).name, r) for r in a.roots]
    rows = collect(roots, a.model, a.jobs)
    if not rows:
        sys.exit('judge: no map.md judged')
    md = '## Distribution\n\n' + table(rows) + '\n\n## Per map\n\n' + per_map(rows) + '\n'
    first = Path(roots[0][1])
    (first / 'distribution.json').write_text(json.dumps(rows, indent=1))
    (first / 'distribution.md').write_text(md)
    print(md)


if __name__ == '__main__':
    main()
