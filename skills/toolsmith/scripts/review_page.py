#!/usr/bin/env python3
"""Render a toolsmith map (map.md) into one self-contained HTML review page.

    python3 review_page.py map.md [more-maps.md …] [-o review.html] [--title "…"]

Standard library only. The page shows the evidence grid — what an agent can prove at each level
(unit, piece, operation, journey) by each way (lab, witness, live), with every proposed card in its
cell — then the app with its handles by category (the Lab drawn around the six others), the roadmap grouped by capability — what the agent cannot do today — with its open cards (proposed · accepted · in progress) with each milestone's
dependencies, demo, expected result and verification level, then delivered and deferred handles in
their own panels — never as proposals — the tools already in place and the grill. Warnings on
stderr name what the map leaves ambiguous (no Status, no Depends on, delivered but not demoed).
The reviewer marks each item right / wrong / unsure with a note — kept in the browser — and copies
a Markdown feedback block back to the agent. No server, no network: the file works opened locally
or published as a static page.
"""
import argparse, html, json, re, sys
from pathlib import Path

CATS = ['launch', 'ingress', 'runtime', 'state', 'egress', 'eyes', 'lab']
LABELS = {'launch': 'Launch & loop', 'ingress': 'Ingress', 'runtime': 'Runtime', 'state': 'State',
          'egress': 'Egress', 'eyes': 'Eyes & logs', 'lab': 'Lab'}
HINT = {'launch': 'start · ready · reset · environments', 'ingress': 'drive it, as someone',
        'runtime': 'inside the live process', 'state': 'data and time', 'egress': 'what leaves',
        'eyes': 'screenshots · logs · traces', 'lab': 'the app brought out — a piece run outside it'}
CAT_RX = '|'.join(CATS)
GRID_LEVELS = ['unit', 'piece', 'operation', 'journey']
WAYS = ['bring', 'witness', 'reach']
WAY_LABELS = {'bring': 'Bring out — lab', 'witness': 'Witness — effects', 'reach': 'Reach in — live'}
GRADES = ('gated', 'asserted', 'observed', 'gap', 'n/a')


# ---------------------------------------------------------------- parsing

def sections(md):
    out, cur, buf = {}, '_pre', []
    for line in md.splitlines():
        if line.startswith('## '):
            out[cur] = '\n'.join(buf); cur, buf = line[3:].strip().lower(), []
        else:
            buf.append(line)
    out[cur] = '\n'.join(buf)
    return out


def find(secs, *keys):
    return next((v for k, v in secs.items() if any(k.startswith(x) for x in keys)), '')


def split_row(line):
    s = line.strip().strip('|')
    cells, cur, tick = [], '', False
    for i, c in enumerate(s):
        if c == '`':
            tick = not tick
        if c == '|' and not tick and not (i and s[i - 1] == '\\'):
            cells.append(cur.strip()); cur = ''
        else:
            cur += c
    cells.append(cur.strip())
    return cells


def tables(body):
    res, lines, i = [], body.splitlines(), 0
    while i < len(lines):
        if lines[i].lstrip().startswith('|') and i + 1 < len(lines) and re.match(r'^\s*\|[\s:|-]+\|\s*$', lines[i + 1]):
            hdr = [h.lower() for h in split_row(lines[i])]; rows = []; i += 2
            while i < len(lines) and lines[i].lstrip().startswith('|'):
                c = split_row(lines[i]); c += [''] * (len(hdr) - len(c)); rows.append(dict(zip(hdr, c))); i += 1
            res.append(rows)
        else:
            i += 1
    return res


def col(row, *names):
    for k, v in row.items():
        if any(k.startswith(n) for n in names):
            return v
    return ''


def bullets(body):
    items = []
    for line in body.splitlines():
        m = re.match(r'^\s*(?:[-*]|\d+\.)\s+(.*)', line)
        if m:
            items.append(m.group(1).strip())
        elif items and line.startswith('   ') and line.strip():
            items[-1] += ' ' + line.strip()
    return items


def field(text, name):
    m = re.search(r'\*\*' + name + r':\*\*\s*(.*)', text)
    return m.group(1).strip() if m else ''


LIFE = ('proposed', 'accepted', 'in progress', 'delivered', 'deferred')
ALIAS = {'built': 'delivered', 'done': 'delivered', 'shipped': 'delivered', 'in-progress': 'in progress',
         'building': 'in progress', 'wip': 'in progress', 'candidate': 'proposed', 'new': 'proposed'}
LEVELS = ('implemented', 'tested', 'demoed')


def lifecycle(text):
    """The status word a **Status:** line starts with, normalised; '' when absent or unknown."""
    t = re.sub(r'[`*]', '', text or '').strip().lower()
    for w in sorted(list(LIFE) + list(ALIAS), key=len, reverse=True):
        if t.startswith(w):
            return ALIAS.get(w, w)
    return ''


def level(text):
    """The verification level a **Verified:** line starts with: implemented · tested · demoed, or ''."""
    m = re.match(r'\s*[`*]*(implemented|tested|demoed)\b', (text or '').lower())
    return m.group(1) if m else ''


def cell_of(way, lvl=''):
    """(way, level) of the grid from a card's `<way> at <level>`, or from a tools row's Way and Level
    columns; None when either is missing or the handle is a loop-only one."""
    t = (way or '').lower()
    m = re.search(r'\bat\s+(' + '|'.join(GRID_LEVELS) + r')\b', t)
    lv = m.group(1) if m else next((x for x in GRID_LEVELS if x in (lvl or '').lower()), '')
    w = 'bring' if re.search(r'bring|\blab\b', t) else 'witness' if 'witness' in t else 'reach' if re.search(r'reach|live', t) else ''
    return (w, lv) if w and lv else None


def grade(text):
    t = re.sub(r'[`*_]', '', text or '').strip().lower()
    return next((g for g in GRADES if t.startswith(g)), '')


def decision(text):
    """The decision a grid cell ends with: `→ propose` · `→ leave` · `→ either` (also `->`), or ''."""
    m = re.search(r'(?:→|->)\s*`?(propose|leave|either)\b', text or '', re.I)
    return m.group(1).lower() if m else ''


def parse_grid(text):
    """The map's Evidence grid table: {level: {way: cell text}} with the level's own words kept."""
    rows = {}
    for tb in tables(text):
        for r in tb:
            head = col(r, 'level')
            lv = next((x for x in GRID_LEVELS if re.match(r'^\W*' + x, head.lower())), None)
            if not lv:
                continue
            rows[lv] = {'label': head, 'bring': col(r, 'bring', 'lab'), 'witness': col(r, 'witness', 'effects'),
                        'reach': col(r, 'reach', 'live')}
    return rows


def parse_cards(text, default):
    cards, cur, in_code = [], None, False
    for line in text.splitlines():
        if line.startswith('```'):
            in_code = not in_code
        m = None if in_code else re.match(r'^#{3,4}\s+(.*)$', line)
        if m and '·' in m.group(1) and re.search(r'(?: — |: )\s*(?:(?:' + CAT_RX + r')[^·]*·\s*)?B\d', m.group(1)):
            cur = {'head': m.group(1), 'body': []}; cards.append(cur)
        elif m:
            cur = None
        elif cur is not None:
            cur['body'].append(line)
    out_cards = []
    for c in cards:
        head = c['head']; body = '\n'.join(c['body'])
        name, _, meta = head.partition(' — ') if ' — ' in head else head.partition(': ')
        bits = [b.strip() for b in meta.split('·')]
        cat, also = 'launch', []
        if bits and re.match(CAT_RX, bits[0].lower()):
            first = bits.pop(0).lower(); cat = first.split()[0].rstrip('&')
            cat = next((x for x in CATS if cat.startswith(x)), 'launch')
            also = [x for x in re.findall(CAT_RX, first.partition('(')[2]) if x != cat]
        usage = re.search(r'```[a-z]*\n(.*?)```', body, re.S)
        fin = field(body, 'Finishes')
        scripts = []
        for rows in tables(body):
            for r in rows:
                if col(r, 'script'):
                    scripts.append((re.sub(r'[`*]', '', col(r, 'script')), col(r, 'usage')))
        for line in body.split('cards under', 1)[1].splitlines() if 'cards under' in body else []:
            ms = re.match(r'^\s*-\s+`([^`]+)`[^—]*—\s*(.*)', line)
            if ms:
                scripts.append((ms.group(1).split(' ')[0], ms.group(2)))
        way = next((b for b in bits if re.search(r'reach|bring|witness|lab|live|\bloop\b', b.lower())), '')
        status_line = field(body, 'Status')
        life = lifecycle(status_line)
        verified = field(body, 'Verified')
        out_cards.append({
            'name': re.sub(r'[`*]', '', name).strip(), 'cat': cat, 'also': also,
            'point': bits[0] if bits else '', 'way': way, 'cell': cell_of(way), 'cost': next((b for b in bits if b.lower().startswith('cost')), ''),
            'status': 'half' if fin and not re.match(r'\**new', fin, re.I) else 'missing',
            'life': life or default, 'life_stated': bool(life), 'status_line': status_line,
            'verified': verified, 'level': level(verified),
            'usage': usage.group(1).rstrip() if usage else '', 'scripts': scripts,
            'lines': [(k, field(body, k)) for k in ('Is', 'Finishes', 'Gives the agent', 'Needs', 'Uses', 'Not a script because', 'Fence',
                                                    'Parallel', 'Permission', 'Deferred because', 'Revisit when') if field(body, k)],
        })
    return out_cards


def subsections(text):
    """Split a section body on its ### / #### headings: [(title or None, body)]."""
    out, cur = [], [None, []]
    for line in text.splitlines():
        mh = re.match(r'^#{3,4}\s+(.*)$', line)
        if mh:
            out.append(cur); cur = [mh.group(1).strip(), []]
        else:
            cur[1].append(line)
    out.append(cur)
    return [(t, '\n'.join(b)) for t, b in out]


def parse_roadmap(road):
    foundations = [[col(r, 'foundation'), col(r, 'used by'), col(r, 'unlocks'), col(r, 'cost')] for rows in tables(road) for r in rows if col(r, 'foundation')]
    milestones, deferred = [], []
    for title, body in subsections(road):
        if title is None or re.match(r'^deferred\b', title, re.I):
            # the roadmap's Deferred: a `### Deferred` list, or `**Deferred:**` lines anywhere
            src = body if title else '\n'.join(l for l in body.splitlines() if l.startswith('**Deferred'))
            deferred += [b for b in bullets(src) if b] if title else []
            deferred += [field(l, 'Deferred') for l in src.splitlines() if field(l, 'Deferred')]
            continue
        lines = [l.strip() for l in body.splitlines() if l.strip()]
        deferred += [field(l, 'Deferred') for l in lines if l.startswith('**Deferred') and field(l, 'Deferred')]
        lines = [l for l in lines if not l.startswith('**Deferred')]
        # several **Field:** on one line are allowed: split them so each is read
        flat = [p for l in lines for p in re.split(r'(?<=\S)\s+(?=\*\*[A-Z][^*]{0,30}:\*\*)', l)]
        f = {k: field('\n'.join(flat), k) for k in ('Capability', 'Status', 'Builds', 'Depends on', 'Demo', 'Expect', 'Verified')}
        milestones.append({'title': title, 'body': flat, 'capability': f['Capability'], 'cap': '',
                           'status': lifecycle(f['Status']), 'status_line': f['Status'],
                           'builds': f['Builds'], 'depends': f['Depends on'], 'demo': f['Demo'], 'expect': f['Expect'],
                           'verified': f['Verified'], 'level': level(f['Verified'])})
    deferred = [d for d in deferred if not re.match(r'^\W*(none|nothing)\b', d, re.I)]
    # a name is deferred only if no milestone builds it: "Deferred: none — `x` is in M2" must not defer `x`
    built = {_norm(t) for m in milestones for t in re.findall(r'`([^`]+)`', m['builds'])}
    deferred_names = {_norm(n) for d in deferred for n in re.findall(r'`([^`]+)`', d.split(' — ')[0])} - built
    return {'foundations': foundations, 'milestones': milestones, 'deferred': deferred, 'deferred_names': deferred_names,
            'mermaid': (re.search(r'```mermaid\n(.*?)```', road, re.S) or [None, ''])[1] if '```mermaid' in road else ''}


def _norm(x):
    return re.sub(r'[^a-z0-9]+', '', x.lower())


def tool_key(name):
    """One key per tool however a row spells it: `bin/agent shot` (scripts/agent/shot.rb) → binagentshot."""
    n = re.sub(r'\([^)]*\)', '', name or '').split(' — ')[0]
    return _norm(n.replace('`', '').replace('*', ''))


def covered(tool, cards):
    """The card that draws this tool already: same name, or a card whose Finishes names it."""
    k = tool['key']
    for c in cards:
        if c['life'] == 'deferred':
            continue
        fin = dict(c['lines']).get('Finishes', '')
        if k == tool_key(c['name']) or (len(k) >= 4 and k in [tool_key(x) for x in re.findall(r'`([^`]+)`', fin)]):
            return c
    return None


def parse(md):
    secs = sections(md)
    title = (md.splitlines() or [''])[0].lstrip('# ').strip()
    pre = secs.get('_pre', '')
    summary = field(pre, 'In one paragraph')
    roadmap = parse_roadmap(find(secs, 'roadmap'))
    # each section gives its cards a default status; a card's own **Status:** line wins
    cards = (parse_cards(find(secs, 'delivered'), 'delivered') + parse_cards(find(secs, 'candidate'), 'proposed')
             + parse_cards(find(secs, 'deferred'), 'deferred'))
    for c in cards:
        if not c['life_stated'] and c['life'] == 'proposed' and _norm(c['name']) in roadmap['deferred_names']:
            c['life'] = 'deferred'
        if c['life'] == 'delivered':
            c['status'] = 'exists'
    cards = [c for c in cards if c['life'] != 'deferred'] + [c for c in cards if c['life'] == 'deferred']
    built = {tool_key(c['name']) for c in cards if c['life'] == 'delivered'}
    tools, by_key = [], {}
    for rows in tables(find(secs, 'tools already')):
        for r in rows:
            nm = re.sub(r'[`*]', '', col(r, 'tool')).strip()
            key = tool_key(col(r, 'tool'))
            if not nm or key in built:  # a delivered card listed here too is shown once, as its card
                continue
            c = (col(r, 'category') or '').lower()
            cat = next((x for x in CATS if c.startswith(x)), 'launch')
            if key in by_key:  # one row per verb is one tool: one node, its other categories as "+"
                t = by_key[key]
                if cat != t['cat'] and cat not in t['also']:
                    t['also'].append(cat)
                for f, v in (('way', col(r, 'way')), ('usage', col(r, 'usage'))):
                    if v and v not in t[f]:
                        t[f] = f'{t[f]} · {v}' if t[f] else v
                continue
            by_key[key] = {'name': nm, 'key': key, 'cat': cat, 'also': [], 'way': col(r, 'way'), 'usage': col(r, 'usage'), 'status': 'exists',
                           'cell': cell_of(col(r, 'way'), col(r, 'level'))}
            tools.append(by_key[key])
    par = find(secs, 'parallel agents')
    m = re.search(r'at once today:\s*\**\s*(\d+|[^*\n—]+)', par)
    parallel = {'count': m.group(1).strip() if m else '', 'line': '', 'rows': []}
    lm = re.search(r'at once today:[^\n]*?—\s*(.*)', par)
    parallel['line'] = lm.group(1).strip() if lm else ''
    for rows in tables(par):
        for r in rows:
            parallel['rows'].append([col(r, 'shared'), col(r, 'shared by'), col(r, 'what collides'), col(r, 'isolation'), col(r, 'proposal')])
    guards = [[col(r, 'rule'), col(r, 'guard'), col(r, 'kind')] for rows in tables(find(secs, 'rules')) for r in rows]
    patterns = [[col(r, 'pattern'), col(r, 'does'), col(r, 'evidence'), col(r, 'fits'), col(r, 'does not', 'not when', "doesn't"), col(r, 'here as', 'here')]
                for rows in tables(find(secs, 'transferable')) for r in rows if col(r, 'pattern')]
    capabilities = parse_capabilities(find(secs, 'capabilities'), roadmap)
    return {'title': title, 'summary': summary, 'task_mix': field(md, 'Task mix'), 'grid': parse_grid(find(secs, 'evidence grid')),
            'capabilities': capabilities, 'parallel': parallel, 'guards': guards, 'roadmap': roadmap, 'cards': cards, 'tools': tools,
            'patterns': patterns, 'grill': bullets(find(secs, 'grill')), 'unknowns': bullets(find(secs, 'unknowns'))}


def parse_capabilities(text, roadmap):
    """The map's Capabilities table, each linked to the milestones that deliver it and given a state
    derived from theirs: delivered (or delivered, not demoed) · in progress · accepted · planned ·
    deferred · no milestone."""
    caps = []
    for rows in tables(text):
        for r in rows:
            what = col(r, 'capability')
            if not what:
                continue
            cid = re.sub(r'[`*\s]', '', col(r, '#', 'id')) or f'C{len(caps) + 1}'
            caps.append({'id': cid, 'what': what, 'today': col(r, 'today'), 'evidence': col(r, 'evidence'), 'milestones': []})
    by_id = {_norm(c['id']): c for c in caps}
    for m in roadmap['milestones']:
        line = m['capability']
        mid = re.match(r'^\W*(C\d+)\b', line or '', re.I)
        c = by_id.get(_norm(mid.group(1))) if mid else None
        if c is None and line:  # named by its words, not its id
            head = _norm(line.split(' — ')[-1])[:24]
            c = next((x for x in caps if head and (_norm(x['what']).startswith(head) or head.startswith(_norm(x['what'])[:24]))), None)
        if c is not None:
            m['cap'] = c['id']; c['milestones'].append(m)
    deferred_ids = {_norm(x.group(1)) for d in roadmap['deferred'] for x in [re.match(r'^\W*(C\d+)\b', d, re.I)] if x}
    for c in caps:
        st = [m['status'] or 'proposed' for m in c['milestones']]
        lv = [m['level'] for m in c['milestones']]
        if not st:
            c['state'] = 'deferred' if _norm(c['id']) in deferred_ids else 'no milestone'
        elif all(x == 'delivered' for x in st):
            c['state'] = 'delivered' if all(x == 'demoed' for x in lv) else 'delivered, not demoed'
        elif any(x in ('in progress', 'delivered') for x in st):
            c['state'] = 'in progress'
        elif 'accepted' in st:
            c['state'] = 'accepted'
        else:
            c['state'] = 'planned'
        c['why'] = next((d for d in roadmap['deferred'] if re.match(r'^\W*' + re.escape(c['id']) + r'\b', d, re.I)), '')
    return caps


def lint(model):
    """What the map leaves ambiguous about status, dependencies and proof — printed by the CLI."""
    w, rm = [], model['roadmap']
    unstated = [c['name'] for c in model['cards'] if not c['life_stated'] and c['life'] == 'proposed']
    if unstated:
        w.append(f'{len(unstated)} card(s) without a **Status:** line, read as proposed: {", ".join(unstated[:6])}')
    for c in model['cards']:
        if c['life'] == 'delivered' and not c['level']:
            w.append(f'delivered card `{c["name"]}` has no **Verified:** level (implemented · tested · demoed)')
        if c['life_stated'] and c['life'] != 'deferred' and _norm(c['name']) in rm['deferred_names']:
            w.append(f'card `{c["name"]}` is listed as deferred in the roadmap but its Status is {c["life"]}')
    ms = [(m['title'].split(' — ')[0], m) for m in rm['milestones']]
    for test, what in ((lambda m: not m['depends'], 'no **Depends on:** — the numbers will be read as dependencies'),
                       (lambda m: not m['demo'], 'no **Demo:**'),
                       (lambda m: m['demo'] and not m['expect'], 'no **Expect:** — the demo has no observable result to check')):
        hit = [t for t, m in ms if test(m)]
        if hit:
            w.append(f'{", ".join(hit)}: {what}')
    caps = model['capabilities']
    if not caps:
        if ms:
            w.append('no **Capabilities** table — the roadmap is a list of handles with no direction')
    else:
        none = [t for t, m in ms if not m['capability']]
        if none:
            w.append(f'{", ".join(none)}: no **Capability:** — which capability does it deliver?')
        lost = [t for t, m in ms if m['capability'] and not m['cap']]
        if lost:
            w.append(f'{", ".join(lost)}: **Capability:** names none of {", ".join(c["id"] for c in caps)}')
        orphan = [c['id'] for c in caps if c['state'] == 'no milestone']
        if orphan:
            w.append(f'{", ".join(orphan)}: no milestone delivers it and it is not under Deferred')
    grid, open_cards = model.get('grid') or {}, [c for c in model['cards'] if c['life'] != 'deferred']
    if not grid:
        if caps or ms:
            w.append('no **Evidence grid** — nothing shows which levels and ways were looked at')
    else:
        lost = [f'{lv} × {WAY_LABELS[wy].split(" — ")[0].lower()}' for lv in GRID_LEVELS for wy in WAYS
                if not grade((grid.get(lv) or {}).get(wy, ''))]
        if lost:
            w.append(f'Evidence grid: no verdict (gated · asserted · observed · gap · n/a) in {", ".join(lost)}')
        nocell = [c['name'] for c in open_cards if not c['cell'] and not re.search(r'\bloop\b', c['way'].lower())]
        if nocell:
            w.append(f'{len(nocell)} card(s) name no cell (`<way> at <level>`): {", ".join(nocell[:6])}')
        name = lambda lv, wy: f'{lv} × {WAY_LABELS[wy].split(" — ")[0].lower()}'
        undecided, unmet, against = [], [], []
        for lv in GRID_LEVELS:
            for wy in WAYS:
                text = (grid.get(lv) or {}).get(wy, '')
                d = decision(text)
                if grade(text) and not d:
                    undecided.append(name(lv, wy))
                here = [c for c in model['cards'] if c['cell'] == (wy, lv)]
                if d == 'propose' and not here:
                    unmet.append(name(lv, wy))
                if d == 'leave':
                    against += [f'`{c["name"]}` in {name(lv, wy)}' for c in here if c['life'] != 'deferred']
        if undecided:
            w.append(f'Evidence grid: no decision (→ propose · leave · either) in {", ".join(undecided)}')
        if unmet:
            w.append(f'Evidence grid: decided propose but no card (or deferred card) in {", ".join(unmet)}')
        if against:
            w.append(f'Evidence grid: a card in a cell decided leave — {", ".join(against)}')
    if not model.get('task_mix') and (caps or ms):
        w.append('no **Task mix:** line — what comes first rests on the shape\'s habit, not this project')
    for t, m in ms:
        if m['status'] == 'delivered' and m['level'] != 'demoed':
            w.append(f'{t}: delivered but not demoed ({m["level"] or "no Verified line"}) — shown as such')
    return w


# ---------------------------------------------------------------- rendering

def esc(s):
    return html.escape(str(s or ''))


def md(s):
    s = esc(s)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    return re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)


SYM = {'exists': '●', 'half': '◐', 'missing': '◌'}
WORD = {'exists': 'exists', 'half': 'to finish', 'missing': 'missing'}


def node(h, anchor):
    life = h.get('life', '')
    state = (f'delivered · {h.get("level") or "no evidence"}' if life == 'delivered'
             else WORD[h['status']] + (f' · {life}' if life and life != 'proposed' else ''))
    tip = f'{h["name"]} — {state}' + (f' · {h["way"]}' if h.get('way') else '')
    also = ''.join(f'<span class="also">+{LABELS[a]}</span>' for a in h.get('also', []))
    sc = f'<span class="sc">{len(h["scripts"])} scripts</span>' if h.get('scripts') else ''
    inner = f'<span class="sym">{SYM[h["status"]]}</span><span class="nm">{esc(h["name"])}</span>{also}{sc}'
    data = f'class="node {h["status"]}" data-tip="{esc(tip)}" data-usage="{esc(h.get("usage", ""))}"'
    return f'<a {data} href="#{anchor}">{inner}</a>' if anchor else f'<span {data} tabindex="0">{inner}</span>'


def grid_panel(model, rid, k):
    grid = model.get('grid') or {}
    if not grid:
        return ''
    chips = {}
    for i, c in enumerate(model['cards']):
        if c['life'] != 'deferred' and c['cell']:
            st = 'exists' if c['life'] == 'delivered' else c['status']
            chips.setdefault(c['cell'], []).append(f'<a class="node {st}" href="#{rid}-card-{i}" data-tip="{esc(c["name"])} — {esc(c["life"])}">'
                                                   f'<span class="sym">{SYM[st]}</span><span class="nm">{esc(c["name"])}</span></a>')
    rows = []
    for lv in GRID_LEVELS:
        r = grid.get(lv)
        if not r:
            rows.append(f'<tr><th scope="row">{lv}</th>' + '<td class="g-none">no verdict</td>' * 3 + '</tr>')
            continue
        tds = ''
        for wy in WAYS:
            g = grade(r[wy]) or 'none'
            ch = chips.get((wy, lv), [])
            d = decision(r[wy])
            badge = f'<span class="dec dec-{d}">{d}</span>' if d else '<span class="dec dec-none">undecided</span>'
            tds += (f'<td class="g-{g.replace("/", "")}">{badge}{md(r[wy]) if r[wy] else "no verdict"}'
                    + (f'<div class="nodes">{"".join(ch)}</div>' if ch else '') + '</td>')
        rows.append(f'<tr><th scope="row">{md(r["label"])}</th>{tds}</tr>')
    tm = f'<p><strong>Task mix:</strong> {md(model["task_mix"])}</p>' if model.get('task_mix') else ''
    return (f'<section class="panel"><h3>Evidence grid</h3><p class="muted">What an agent can prove at each level, by each way — '
            f'gated · asserted · observed · gap · n/a — with each proposed card in the cell it would fill.</p>{tm}'
            f'<div class="tw"><table class="grid"><thead><tr><th>Level</th>' + ''.join(f'<th>{WAY_LABELS[w]}</th>' for w in WAYS)
            + f'</tr></thead><tbody>{"".join(rows)}</tbody></table></div>{verdict(k("grid:section"), "Evidence grid")}</section>')


def picture(model, rid, name):
    hs = ([(t, None) for t in model['tools'] if not covered(t, model['cards'])]
          + [(c, f'{rid}-card-{i}') for i, c in enumerate(model['cards']) if c['life'] != 'deferred'])
    order = {'exists': 0, 'half': 1, 'missing': 2}

    def box(cat, cls='cat'):
        items = sorted([x for x in hs if x[0]['cat'] == cat], key=lambda x: order[x[0]['status']])
        n = {s: sum(x[0]['status'] == s for x in items) for s in order}
        summ = ' · '.join(f'{n[s]} {WORD[s]}' for s in order if n[s]) or 'nothing — a gap'
        return (f'<div class="{cls}{" empty" if not items else ""}"><div class="head"><h4>{LABELS[cat]}</h4>'
                f'<span class="hint">{HINT[cat]}</span><span class="sum">{summ}</span></div>'
                f'<div class="nodes">{"".join(node(h, a) for h, a in items)}</div></div>')
    rows = (f'<div class="row">{"".join(box(c) for c in ("launch", "ingress", "runtime"))}</div>'
            f'<div class="hub"><strong>{esc(name)}</strong><span class="legend">● exists or delivered · ◐ to finish · ◌ missing · deferred cards not drawn</span></div>'
            f'<div class="row">{"".join(box(c) for c in ("eyes", "egress", "state"))}</div>')
    return f'<div class="labframe">{box("lab", "labhead")}{rows}</div>'


def verdict(key, label):
    return (f'<div class="verdict" data-key="{esc(key)}" data-label="{esc(label[:200])}">'
            '<button type="button" data-v="right">✓ Right</button><button type="button" data-v="wrong">✗ Wrong</button>'
            '<button type="button" data-v="unsure">? Unsure</button>'
            f'<input type="text" placeholder="Note, question or answer" aria-label="Note for {esc(label[:60])}"></div>')


def table(head, rows):
    trs = ''.join('<tr>' + ''.join(f'<td>{md(x)}</td>' for x in r) + '</tr>' for r in rows)
    return f'<div class="tw"><table><thead><tr>{"".join(f"<th>{h}</th>" for h in head)}</tr></thead><tbody>{trs}</tbody></table></div>'


def short_name(model):
    t = re.sub(r'^(agent map|map)\s*[—:-]\s*', '', model['title'], flags=re.I)
    return re.split(r'\s+@\s+|\s+\(', t)[0].strip() or model['title']


ACTIVE = ('proposed', 'accepted', 'in progress')


def life_badge(life):
    return f'<span class="life {life.replace(" ", "-")}">{esc(life)}</span>' if life else ''


def proof_badge(status, lvl, verified):
    """How far a delivered card or milestone was proven. Never rounds tested up to demoed."""
    if lvl == 'demoed':
        return '<span class="proof ok">✓ demoed end to end</span>'
    if status == 'delivered':
        return f'<span class="proof gap">{"⚠ " + esc(lvl) + " — not demoed" if lvl else "⚠ delivered without evidence"}</span>'
    if lvl:
        return f'<span class="proof part">{esc(lvl)} — not demoed yet</span>'
    return ''


def deps_tag(depends):
    d = re.sub(r'[`*.]', '', depends or '').strip().lower()
    if not d:
        return '<span class="deps unknown" title="No Depends on line: the number is an order, not a dependency">dependencies not stated</span>'
    if d.startswith('none') or d.startswith('nothing') or d.startswith('independent'):
        return '<span class="deps indep">independent</span>'
    return f'<span class="deps">depends on {md(depends.split(" — ")[0])}</span>'


def roadmap_panel(model, cards, k):
    """The proposed handles, compiled: foundations marked, open cards placed in the milestone that builds
    them, each milestone with its status, real dependencies, demo, expected result and how far it was
    proven. Delivered and deferred cards are not drawn as proposals here — they have their own panels."""
    rm = model['roadmap']
    mc = model['cards']
    names = [_norm(c['name']) for c in mc]
    active = [i for i, c in enumerate(mc) if c['life'] in ACTIVE]
    if not rm['milestones']:
        return (f'<section class="panel"><h3>Proposed handles ({len(active)})</h3><p class="muted">No roadmap in this map yet — '
                f'a flat list. Would you build it? Is the usage right?</p>{by_capability(model, [], k)}'
                f'<ul class="items">{"".join(cards[i] for i in active)}</ul></section>')
    found = {_norm(re.sub(r'\(.*?\)', '', f[0]).replace('`', '')) for f in rm['foundations']}
    script_names = {_norm(sn) for c in mc for sn, _ in c['scripts']}
    placed, groups = set(), []
    for m in rm['milestones']:
        builds = m['builds'] or ' '.join(m['body'])
        ticks = [_norm(t) for t in re.findall(r'`([^`]+)`', builds)]
        hit = lambda n: n and any(n == t or n in t or t in n for t in ticks if t)
        mine = [i for i in active if i not in placed and hit(names[i])]
        done = [i for i, c in enumerate(mc) if c['life'] == 'delivered' and hit(names[i])]
        placed.update(mine)
        added = [t for t in re.findall(r'`([^`]+)`', builds) if _norm(t) in script_names and _norm(t) not in names]
        groups.append((m, mine, done, added))
    rest = [i for i in active if i not in placed]

    def fmark(i):
        return '<span class="tag found">foundation</span>' if names[i] in found or any(names[i] and (names[i] in f or f in names[i]) for f in found if f) else ''
    known = re.compile(r'^\*\*(Capability|Status|Builds|Depends on|Demo|Expect|Verified):\*\*')
    ms_html = []
    for m, mine, done, added in groups:
        cards_html = ''.join(cards[i].replace('<div class="title">', '<div class="title">' + fmark(i), 1) for i in mine)
        done_html = ('<div class="muted">Already delivered: ' + ', '.join(
            f'<a href="#{k("").rstrip("|")}-card-{i}"><code>{esc(mc[i]["name"])}</code></a> ({esc(mc[i]["level"] or "no evidence")})' for i in done) + '</div>') if done else ''
        demo = (f'<div><strong>Demo:</strong> {md(m["demo"])}</div>' if m['demo'] else '<div class="warn">No demo — nothing shows this milestone works.</div>')
        expect = (f'<div><strong>Expect:</strong> {md(m["expect"])}</div>' if m['expect'] else
                  ('<div class="warn">No expected result — the demo has nothing to check against.</div>' if m['demo'] else ''))
        verified = f'<div><strong>Verified:</strong> {md(m["verified"])}</div>' if m['verified'] else ''
        other = ''.join(f'<div>{md(b)}</div>' for b in m['body'] if not known.match(b))
        badges = life_badge(m['status'] or 'proposed') + deps_tag(m['depends']) + proof_badge(m['status'], m['level'], m['verified'])
        ms_html.append(f'<div class="milestone ms-{(m["status"] or "proposed").replace(" ", "-")}"><div class="ms-head"><div class="ms-main">'
                        f'<h4>{md(m["title"])}</h4><div class="badges">{badges}</div>'
                        + (f'<div><strong>Builds:</strong> {md(m["builds"])}</div>' if m['builds'] else '')
                        + (f'<div><strong>Depends on:</strong> {md(m["depends"])}</div>' if m['depends'] else '')
                        + demo + expect + verified + other
                        + (f'<div class="muted">Scripts added: {", ".join(f"<code>{esc(a)}</code>" for a in added)}</div>' if added else '')
                        + done_html
                        + f'</div>{verdict(k("milestone:" + m["title"][:40]), m["title"])}</div>'
                        + (f'<ul class="items">{cards_html}</ul>' if cards_html else
                           ('' if done else '<p class="muted">No new card — scripts on existing foundations.</p>'))
                        + '</div>')
    html_groups = by_capability(model, ms_html, k)
    rest_html = ''
    if rest:
        rest_html = ('<div class="milestone"><div class="ms-head"><div class="ms-main"><h4>Not in a milestone</h4>'
                     '<div class="muted">Proposed but not placed by the roadmap — move it into one, defer it, or drop it.</div></div></div>'
                     f'<ul class="items">{"".join(cards[i] for i in rest)}</ul></div>')
    return ('<section class="panel"><h3>Roadmap' + (' — by capability' if model['capabilities'] else '') + '</h3><p class="muted">' + roadmap_intro(rm['milestones'], bool(rest)) + '</p>'
            + (f'<details><summary class="muted">Foundations and dependency graph</summary>'
               f'{table(["Foundation", "Used by", "Unlocks", "Cost"], rm["foundations"]) if rm["foundations"] else ""}'
               f'{(chr(60) + "pre class=" + chr(34) + "mermaid" + chr(34) + ">" + esc(rm["mermaid"]) + "</pre>") if rm["mermaid"] else ""}</details>')
            + html_groups + rest_html + '</section>')


CAP_CLASS = {'delivered': 'ok', 'delivered, not demoed': 'part', 'in progress': 'prog', 'accepted': 'prog', 'planned': 'plan',
             'deferred': 'muted', 'no milestone': 'gap'}


def by_capability(model, ms_html, k):
    """The roadmap's backbone: each capability — what the agent cannot do today — with the milestones
    that deliver it inside. Milestones naming no capability come last, flagged. Without a Capabilities
    table, the milestones as they are."""
    caps, mss = model['capabilities'], model['roadmap']['milestones']
    if not caps:
        return ''.join(ms_html)
    out = ''
    for c in caps:
        inner = ''.join(h for m, h in zip(mss, ms_html) if m['cap'] == c['id'])
        if not inner:
            inner = (f'<p class="muted">Deferred: {md(c["why"])}</p>' if c['state'] == 'deferred' else
                     '<p class="warn">No milestone delivers this capability — add one, or defer it with why.</p>')
        out += (f'<div class="cap"><div class="ms-head"><div class="ms-main"><h4><span class="capid">{esc(c["id"])}</span> '
                f'The agent can {md(c["what"])}</h4>'
                f'<div class="badges"><span class="capst {CAP_CLASS.get(c["state"], "")}">{esc(c["state"])}</span></div>'
                + (f'<div><strong>Today:</strong> {md(c["today"])}</div>' if c['today'] else '')
                + (f'<div class="muted"><strong>Evidence:</strong> {md(c["evidence"])}</div>' if c['evidence'] else '')
                + f'</div>{verdict(k("capability:" + c["id"]), c["id"] + " — " + c["what"])}</div>{inner}</div>')
    loose = ''.join(h for m, h in zip(mss, ms_html) if not m['cap'])
    if loose:
        out += ('<div class="cap orphan"><div class="ms-main"><h4>No capability named</h4><div class="warn">These milestones do not say '
                'which capability they deliver — name one on their <strong>Capability:</strong> line, or drop them.</div></div>' + loose + '</div>')
    return out


def ms_id(m):
    return m['title'].split(' — ')[0].split(' · ')[0].strip()


def next_milestone(milestones):
    """The first milestone still waiting for a go — never one already accepted, in progress or delivered."""
    return next((m for m in milestones if (m['status'] or 'proposed') == 'proposed'), None)


def roadmap_intro(milestones, unplaced=False):
    """What the reader is asked to do, from where the roadmap stands — a delivered roadmap asks for nothing."""
    st = [m['status'] or 'proposed' for m in milestones]
    nxt = next_milestone(milestones)
    done = [ms_id(m) for m, x in zip(milestones, st) if x == 'delivered']
    going = [ms_id(m) for m, x in zip(milestones, st) if x in ('accepted', 'in progress')]
    where = []
    if done:
        where.append(f'Delivered: {", ".join(done)} — each says how far it was proven.')
    if going:
        where.append(f'Accepted, being built: {", ".join(going)}.')
    lead = 'Foundations first; each milestone with the cards it builds, what it really depends on, and the demo that proves it. Numbers are an order, not a dependency.'
    if nxt:
        ask = f'Accept by milestone ("go for {esc(ms_id(nxt))}"); move or drop a card in its note.'
    elif unplaced:
        ask = 'Every milestone is accepted or delivered; the cards below in no milestone wait for a decision.'
    elif len(done) == len(milestones):
        return ' '.join([f'Every milestone on this roadmap is delivered ({", ".join(done)}); nothing here waits for a go. '
                         'Check what each one proved — a milestone not demoed says so.'])
    else:
        ask = 'Nothing waits for a go: the rest is accepted and being built.'
    return ' '.join([lead] + where + [ask])


def deferred_panel(model, cards, k):
    mc = model['cards']
    idx = [i for i, c in enumerate(mc) if c['life'] == 'deferred']
    have = {_norm(mc[i]['name']) for i in idx}
    loose = [d for d in model['roadmap']['deferred']
             if not any(_norm(n) in have for n in re.findall(r'`([^`]+)`', d.split(' — ')[0]))]
    if not idx and not loose:
        return ''
    return (f'<section class="panel deferred"><details><summary><h3 style="display:inline">Deferred ({len(idx) + len(loose)})</h3></summary>'
            '<p class="muted">Not planned this round, and not proposed: kept so the next map does not rediscover them. '
            'Say in a note if one should come back.</p>'
            + (f'<ul class="items">{"".join(cards[i] for i in idx)}</ul>' if idx else '')
            + (f'<ul class="plain">{"".join(f"<li>{md(d)}</li>" for d in loose)}</ul>' if loose else '')
            + '</details></section>')


def delivered_panel(model, cards):
    idx = [i for i, c in enumerate(model['cards']) if c['life'] == 'delivered']
    if not idx:
        return ''
    demoed = sum(model['cards'][i]['level'] == 'demoed' for i in idx)
    return (f'<section class="panel"><h3>Delivered ({len(idx)})</h3><p class="muted">Built since the map was made — available now, not '
            f'proposals. {demoed} of {len(idx)} demoed end to end; the rest say how far they were proven.</p>'
            f'<ul class="items">{"".join(cards[i] for i in idx)}</ul></section>')


def repo_section(model, rid, multi):
    name = short_name(model)
    k = lambda x: f'{rid}|{x}'
    cards = []
    for i, c in enumerate(model['cards']):
        lines = ''.join(f'<div><strong>{esc(a)}:</strong> {md(b)}</div>' for a, b in c['lines'])
        scripts = ('<div class="scripts"><strong>Scripts run through it</strong><ul>'
                   + ''.join(f'<li><code>{esc(n)}</code> — {md(u)}</li>' for n, u in c['scripts']) + '</ul></div>') if c['scripts'] else ''
        usage = f'<pre>{esc(c["usage"])}</pre>' if c['usage'] else '<p class="warn">No usage example.</p>'
        life = c['life']
        if life == 'delivered':
            st = '<span class="st exists">● delivered</span>' + proof_badge('delivered', c['level'], c['verified'])
            lines = (f'<div><strong>Verified:</strong> {md(c["verified"])}</div>' if c['verified'] else '') + lines
            group = 'delivered'
        elif life == 'deferred':
            st = '<span class="st deferred">deferred</span>'
            group = 'deferred'
        else:
            st = f'<span class="st {c["status"]}">{SYM[c["status"]]} {WORD[c["status"]]}</span>' + life_badge(life)
            lines += f'<div><strong>Verified:</strong> {md(c["verified"])}</div>' if c['verified'] else ''
            group = 'card'
        cards.append(f'<li class="item life-{life.replace(" ", "-")}" id="{rid}-card-{i}"><div class="main"><div class="title">{st} '
                     f'{esc(c["name"])} <span class="tag">{LABELS[c["cat"]]}</span>{"".join(f"<span class=tag>+{LABELS[a]}</span>" for a in c["also"])}'
                     f' <span class="tag way">{esc(c["way"])}</span> <span class="muted">{esc(c["cost"])}</span></div>'
                     f'{usage}{lines}{scripts}</div>{verdict(k(group + ":" + c["name"]), c["name"])}</li>')
    tools = ''.join(f'<li class="item"><div class="main"><div class="title"><span class="st exists">● exists</span> {md(t["name"])} '
                    f'<span class="tag">{LABELS[t["cat"]]}</span></div>{f"<div class=muted>{md(t["usage"])}</div>" if t["usage"] else ""}</div>'
                    f'{verdict(k("tool:" + t["name"]), t["name"])}</li>' for t in model['tools'])
    grill = ''.join(f'<li class="item"><div class="main"><div class="title">{md(q)}</div></div>{verdict(k(f"grill:{j + 1}"), q)}</li>'
                    for j, q in enumerate(model['grill']))
    parts = [f'<section class="panel"><h3>The app and its handles</h3><p class="muted">The Lab frames the runtime; hover a node for its '
             f'usage, click a proposed one to jump to its card.</p>{picture(model, rid, name)}</section>']
    pa = model['parallel']
    if pa['count'] or pa['rows']:
        parts.append(f'<section class="panel"><h3>Parallel agents</h3><p><strong class="big">{esc(pa["count"] or "?")}</strong> '
                     f'agent(s) can safely work at once today. {md(pa["line"])}</p>'
                     + (table(['Shared resource', 'Shared by', 'What collides', 'Isolation today', 'Proposal'], pa['rows']) if pa['rows'] else '')
                     + f'{verdict(k("parallel:section"), "Parallel agents analysis")}</section>')
    if model['guards']:
        parts.append(f'<section class="panel"><h3>Rules → guards</h3><p class="muted">Rules the agent files state in prose, and what would enforce each.</p>'
                     f'{table(["Rule", "Guard", "Kind"], model["guards"])}{verdict(k("guards:section"), "Rules to guards")}</section>')
    if model['patterns']:
        parts.append(f'<section class="panel"><h3>Transferable patterns</h3><p class="muted">Ideas another project could reuse — '
                     f'where each fits, and where it does not.</p>'
                     f'{table(["Pattern", "Does", "Evidence here", "Fits when", "Does not fit when", "Here as"], model["patterns"])}'
                     f'{verdict(k("patterns:section"), "Transferable patterns")}</section>')
    parts[1:1] = [x for x in (roadmap_panel(model, cards, k), delivered_panel(model, cards), deferred_panel(model, cards, k)) if x]
    g = grid_panel(model, rid, k)
    if g:
        parts.insert(0, g)
    if grill:
        parts.append(f'<section class="panel"><h3>Questions for you ({len(model["grill"])})</h3><p class="muted">Type your answer in the note.</p><ul class="items">{grill}</ul></section>')
    if tools:
        parts.append(f'<section class="panel"><details><summary><h3 style="display:inline">Already in place ({len(model["tools"])})</h3></summary><ul class="items">{tools}</ul></details></section>')
    parts.append(f'<section class="panel"><h3>What did it miss?</h3><textarea class="missed" data-repo="{rid}" rows="3" '
                 f'placeholder="A handle you use or want that is not on the picture" aria-label="What did it miss — {esc(name)}"></textarea></section>')
    head = (f'<header class="repo-head"><h2>{esc(name)}</h2>' if multi else f'<header><h1>{esc(name)}</h1>') + \
           f'<p class="muted">{esc(model["title"])}</p><p>{md(model["summary"])}</p></header>'
    return f'<article class="repo" id="{rid}" data-repo="{rid}" data-name="{esc(name)}">{head}{"".join(parts)}</article>'


def overview(models, rids):
    rows = []
    for m, rid in zip(models, rids):
        hs = [t for t in m['tools'] if not covered(t, m['cards'])] + [c for c in m['cards'] if c['life'] != 'deferred']
        cells = ''
        for c in CATS:
            x = [h for h in hs if h['cat'] == c]
            n = {s: sum(h['status'] == s for h in x) for s in ('exists', 'half', 'missing')}
            cells += ('<td class="gap">gap</td>' if not x else
                      '<td>' + ' '.join(f'{SYM[s]}{n[s]}' for s in n if n[s]) + '</td>')
        nx = next_milestone(m['roadmap']['milestones'])
        m1 = nx['title'] if nx else ('all delivered' if m['roadmap']['milestones'] and all(x['status'] == 'delivered' for x in m['roadmap']['milestones']) else '—')
        cp = m['capabilities']
        capc = f'{sum(c["state"] == "delivered" for c in cp)}/{len(cp)} delivered' if cp else '—'
        rows.append(f'<tr><th scope="row"><a href="#{rid}">{esc(short_name(m))}</a></th>{cells}'
                    f'<td>{esc(m["parallel"]["count"] or "—")}</td><td>{capc}</td><td>{md(m1)}</td></tr>')
    return ('<section class="panel"><h2>All repos</h2><p class="muted">Handles per category (● exists · ◐ to finish · ◌ missing), agents that can '
            'work at once today, capabilities delivered, and each roadmap\'s next milestone waiting for a go.</p><div class="tw"><table><thead><tr><th>Repo</th>'
            + ''.join(f'<th>{LABELS[c]}</th>' for c in CATS) + '<th>Parallel</th><th>Capabilities</th><th>Next milestone</th></tr></thead><tbody>'
            + ''.join(rows) + '</tbody></table></div></section>')


def render(models, title=None):
    if isinstance(models, dict):
        models = [models]
    multi = len(models) > 1
    rids = [f'r{i}' for i in range(len(models))]
    body = (overview(models, rids) if multi else '') + ''.join(repo_section(m, r, multi) for m, r in zip(models, rids))
    nav = ('<nav class="repos">' + ''.join(f'<a href="#{r}">{esc(short_name(m))}</a>' for m, r in zip(models, rids)) + '</nav>') if multi else ''
    title = title or (f'Toolsmith review — {len(models)} repos' if multi else short_name(models[0]))
    store_key = 'toolsmith-review:' + re.sub(r'\W+', '-', '|'.join(m['title'] for m in models))[:120]
    intro = ('<header><h1>' + esc(title) + '</h1><p class="muted">Review these plans: mark each item, add a note, question or answer, '
             'then copy the feedback back to the agent.</p>' + nav + '</header>') if multi else ''
    return (TEMPLATE.replace('{{TITLE}}', esc(title)).replace('{{INTRO}}', intro).replace('{{BODY}}', body)
            .replace('{{STORE}}', json.dumps(store_key)))


TEMPLATE = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{TITLE}}</title>
<style>
:root{--bg:#f6f7f9;--s:#fff;--s2:#eef1f5;--line:#dde2ea;--fg:#14171c;--fg2:#4a5260;--fg3:#6b7380;--acc:#2a78d6;--accs:#dbe8f8;
--ok:#0a7d0a;--oks:#dcf1dc;--half:#8a6100;--halfs:#f8ecd0;--bad:#c23434;--bads:#f8dede;--lab:#7a8a99;--labs:#f0f3f6}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#121418;--s:#1a1d22;--s2:#22262d;--line:#30353e;--fg:#eef0f3;--fg2:#b6bcc6;--fg3:#8d95a1;
--acc:#3987e5;--accs:#1d3350;--ok:#3cc23c;--oks:#17331a;--half:#f0b84a;--halfs:#3a2e12;--bad:#ef7070;--bads:#3d1c1d;--lab:#6f7d8b;--labs:#171a1f;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#121418;--s:#1a1d22;--s2:#22262d;--line:#30353e;--fg:#eef0f3;--fg2:#b6bcc6;--fg3:#8d95a1;
--acc:#3987e5;--accs:#1d3350;--ok:#3cc23c;--oks:#17331a;--half:#f0b84a;--halfs:#3a2e12;--bad:#ef7070;--bads:#3d1c1d;--lab:#6f7d8b;--labs:#171a1f;color-scheme:dark}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:0 48px}
.wrap{max-width:1120px;margin:0 auto;display:grid;gap:22px}
h1,h2,h3,h4{margin:0;text-wrap:balance} h1{font-size:24px;padding-top:20px} h2{font-size:21px} h3{font-size:17px} h4{font-size:14px}
code,pre{font-family:ui-monospace,"SFMono-Regular",Menlo,monospace;font-size:12.5px} code{background:var(--s2);padding:1px 5px;border-radius:4px;overflow-wrap:anywhere}
pre{background:var(--s2);padding:8px 10px;border-radius:6px;overflow-x:auto;margin:4px 0}
.muted{color:var(--fg3)} .warn{color:var(--bad)} .panel{background:var(--s);border:1px solid var(--line);border-radius:10px;padding:16px;min-width:0}
.repo{display:grid;gap:16px;scroll-margin-top:12px} .repo-head{border-top:3px solid var(--fg);padding-top:14px}
nav.repos{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px} nav.repos a{border:1px solid var(--line);border-radius:999px;padding:3px 10px;font-size:13px;color:var(--fg2);text-decoration:none;background:var(--s)}
.labframe{border:2px dashed var(--lab);border-radius:14px;padding:10px;display:grid;gap:10px;background:var(--labs)}
.row{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}
.cat,.labhead{border:1px solid var(--line);border-radius:10px;padding:10px 12px;background:var(--s);display:grid;gap:6px;align-content:start;min-width:0}
.labhead{background:transparent;border:0;padding:2px 4px}
.empty{border-color:var(--bad)} .labhead.empty{border:0} .empty .sum{color:var(--bad);font-weight:600}
.head{display:flex;flex-wrap:wrap;gap:2px 8px;align-items:baseline} .hint,.sum{font-size:12px;color:var(--fg3)}
.nodes{display:flex;flex-wrap:wrap;gap:6px}
.node{display:inline-flex;gap:5px;align-items:center;font-size:12.5px;border:1px solid var(--line);border-radius:6px;padding:3px 8px;color:var(--fg);text-decoration:none;background:var(--s);max-width:100%}
.node .nm{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:220px}
.node.exists{background:var(--oks);border-color:var(--ok)} .node.half{background:var(--halfs);border-color:var(--half)} .node.missing{border-style:dashed}
.also,.sc{font-size:10.5px;color:var(--fg3)} .sc{color:var(--acc);font-weight:600}
.hub{display:flex;flex-wrap:wrap;justify-content:space-between;gap:8px;padding:10px 14px;border-radius:10px;background:var(--fg);color:var(--bg)}
ul.items{list-style:none;margin:0;padding:0}
.item{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:8px 18px;padding:12px 0;border-top:1px solid var(--line);scroll-margin-top:16px}
.item:target{background:var(--accs);border-radius:8px;padding-inline:8px}
.main{min-width:0;display:grid;gap:4px;font-size:14px;color:var(--fg2)} .title{font-weight:600;color:var(--fg);overflow-wrap:anywhere}
.st{font-size:12px;border-radius:999px;padding:0 8px;margin-right:4px} .st.exists{background:var(--oks);color:var(--ok)} .st.half{background:var(--halfs);color:var(--half)} .st.missing{background:var(--s2)}
.tag{font-size:12px;background:var(--s2);border-radius:4px;padding:0 6px;margin-left:4px;font-weight:400} .tag.way{background:var(--accs)}
.scripts ul{margin:4px 0 0;padding-left:18px}
.milestone{border:1px solid var(--line);border-radius:10px;padding:12px 14px;margin-top:12px;background:var(--bg)}
.ms-head{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:8px 18px}.ms-main{display:grid;gap:4px;font-size:14px;color:var(--fg2);min-width:0}.ms-main h4{font-size:15px;color:var(--fg)}
.tag.found{background:var(--fg);color:var(--bg)}
.cap{border:1px solid var(--line);border-left:4px solid var(--acc);border-radius:10px;padding:12px 14px;margin-top:14px;background:var(--s)}
.cap.orphan{border-left-color:var(--bad)} .cap>.ms-head .ms-main h4{font-size:16px} .capid{font:600 12px ui-monospace,monospace;background:var(--fg);color:var(--bg);border-radius:4px;padding:1px 6px;margin-right:4px}
.capst{font-size:12px;border-radius:999px;padding:0 8px;border:1px solid var(--line)} .capst.ok{background:var(--oks);color:var(--ok);border-color:var(--ok)}
.capst.part{background:var(--halfs);color:var(--half);border-color:var(--half)} .capst.prog{background:var(--accs);border-color:var(--acc)} .capst.gap{background:var(--bads);color:var(--bad);border-color:var(--bad)} .capst.muted{color:var(--fg3)}
.badges{display:flex;flex-wrap:wrap;gap:6px}.life,.proof,.deps{font-size:12px;border-radius:999px;padding:0 8px;font-weight:500;border:1px solid var(--line);margin-right:4px}
.life.accepted,.life.in-progress{background:var(--accs);border-color:var(--acc)} .life.delivered{background:var(--oks);color:var(--ok);border-color:var(--ok)}
.proof.ok{background:var(--oks);color:var(--ok);border-color:var(--ok)} .proof.part{background:var(--halfs);color:var(--half);border-color:var(--half)}
.proof.gap{background:var(--bads);color:var(--bad);border-color:var(--bad)} .deps.indep{background:var(--s2)} .deps.unknown{color:var(--half);border-style:dashed}
.st.deferred{background:var(--s2);color:var(--fg3);text-decoration:line-through} .life-deferred .main{opacity:.75} ul.plain{margin:6px 0 0;padding-left:18px;color:var(--fg2)}
.milestone .item:first-child{border-top:1px solid var(--line)}
.verdict{display:flex;flex-wrap:wrap;gap:6px;justify-content:flex-end;max-width:330px;align-content:start}
.verdict button{font:500 13px system-ui,sans-serif;border:1px solid var(--line);background:var(--s);color:var(--fg2);border-radius:999px;padding:4px 10px;cursor:pointer}
.verdict button[aria-pressed=true][data-v=right]{background:var(--oks);border-color:var(--ok);color:var(--ok)}
.verdict button[aria-pressed=true][data-v=wrong]{background:var(--bads);border-color:var(--bad);color:var(--bad)}
.verdict button[aria-pressed=true][data-v=unsure]{background:var(--halfs);border-color:var(--half);color:var(--half)}
.verdict input,textarea{flex:1 1 100%;font:13px system-ui,sans-serif;color:var(--fg);background:var(--s2);border:1px solid var(--line);border-radius:6px;padding:5px 8px;box-sizing:border-box;width:100%}
button:focus-visible,input:focus-visible,textarea:focus-visible,.node:focus-visible,a:focus-visible{outline:2px solid var(--acc);outline-offset:2px}
.tip{position:fixed;z-index:9;pointer-events:none;background:var(--fg);color:var(--bg);font-size:12.5px;padding:6px 9px;border-radius:6px;max-width:min(460px,calc(100vw - 32px))}
.tip pre{background:transparent;color:inherit;padding:0;margin:4px 0 0;white-space:pre-wrap;max-height:200px;overflow:hidden}
.grid td{min-width:150px}.grid td.g-declared{background:var(--oks)}.grid td.g-checked{background:#eaf5ea}
.grid td.g-seen{background:var(--halfs)}.grid td.g-gap,.grid td.g-none{background:var(--bads)}.grid td.g-na{color:var(--fg3)}
.grid .nodes{margin-top:6px}
.dec{display:inline-block;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.04em;border-radius:4px;padding:0 5px;margin-right:6px;background:var(--s2);color:var(--fg2)}
.dec-propose{background:var(--accs);color:var(--acc)}.dec-leave{background:var(--s2);color:var(--fg3)}.dec-none{background:var(--bads);color:var(--bad)}
.big{font-size:22px}.tw{overflow-x:auto}table{border-collapse:collapse;min-width:640px;font-size:13.5px;width:100%}th,td{text-align:left;padding:6px 8px;border-bottom:1px solid var(--line);vertical-align:top}th{color:var(--fg3);font-size:12px;text-transform:uppercase;letter-spacing:.05em} td.gap{color:var(--bad);font-weight:600} th[scope=row] a{color:var(--fg);font-weight:600}
.copy{font:600 14px system-ui,sans-serif;background:var(--acc);color:#fff;border:0;border-radius:8px;padding:8px 14px;cursor:pointer}
@media (max-width:760px){.ms-head{grid-template-columns:1fr}.row{grid-template-columns:1fr}.item{grid-template-columns:1fr}.verdict{justify-content:flex-start;max-width:none}}
</style></head><body><div class="wrap">
{{INTRO}}
{{BODY}}
<section class="panel"><h2>Send the feedback</h2><p class="muted">Copy this block and paste it to the agent.</p>
<button class="copy" id="copy" type="button">Copy feedback</button> <span id="copied" class="muted"></span>
<textarea id="out" rows="10" readonly aria-label="Feedback to copy"></textarea></section>
</div><div class="tip" id="tip" hidden><span id="tt"></span><pre id="tu" hidden></pre></div>
<script>
(function(){
// Verdicts are kept in the browser. If the page is hosted somewhere that offers a shared store
// (a claude.ai artifact with the db capability), they are mirrored there too — nothing else changes.
const KEY={{STORE}};let st={};try{st=JSON.parse(localStorage.getItem(KEY)||'{}')}catch(e){}
let remote=null;const sid=k=>k.replace(/[^A-Za-z0-9_\-.~:@+]/g,'_').slice(0,180)+'-'+[...k].reduce((h,c)=>(h*31+c.charCodeAt(0))|0,7).toString(36).replace('-','n');
const save=k=>{try{localStorage.setItem(KEY,JSON.stringify(st))}catch(e){}if(remote&&k)remote(k)};
const boxes=[...document.querySelectorAll('.verdict')],missed=[...document.querySelectorAll('textarea.missed')],out=document.getElementById('out');
function paint(){boxes.forEach(b=>{const c=st[b.dataset.key]||{};b.querySelectorAll('button').forEach(x=>x.setAttribute('aria-pressed',String(c.v===x.dataset.v)));
 const i=b.querySelector('input');if(document.activeElement!==i)i.value=c.note||''});
 missed.forEach(t=>{if(document.activeElement!==t)t.value=(st[t.dataset.repo+'|_missed']||{}).note||''});out.value=feedback()}
function feedback(){const L=['# Toolsmith review feedback',''];const grp={capability:'Capabilities',milestone:'Roadmap milestones',card:'Proposed handles',delivered:'Delivered handles',deferred:'Deferred handles',grill:'Answers to the questions',parallel:'Parallel agents',guards:'Rules to guards',patterns:'Transferable patterns',tool:'Already in place'};
 document.querySelectorAll('article.repo').forEach(a=>{const rid=a.dataset.repo,mine=boxes.filter(b=>b.dataset.key.startsWith(rid+'|'));const sec=[];
  for(const g of Object.keys(grp)){const rows=mine.filter(b=>b.dataset.key.startsWith(rid+'|'+g+':')).map(b=>[b,st[b.dataset.key]||{}]).filter(([b,c])=>c.v||c.note);
   if(rows.length){sec.push('### '+grp[g]);rows.forEach(([b,c])=>sec.push(`- [${c.v||'note'}] ${b.dataset.label}${c.note?' — '+c.note:''}`))}}
  const m=(st[rid+'|_missed']||{}).note;if(m)sec.push('### Missed',m);if(sec.length)L.push('## '+a.dataset.name,...sec,'')});
 return L.join('\n')}
document.addEventListener('click',e=>{const x=e.target.closest('.verdict button');if(!x)return;const k=x.closest('.verdict').dataset.key;
 st[k]=st[k]||{};st[k].v=st[k].v===x.dataset.v?null:x.dataset.v;save(k);paint()});
let tmr={};const later=k=>{clearTimeout(tmr[k]);tmr[k]=setTimeout(()=>save(k),600)};
document.addEventListener('input',e=>{const b=e.target.closest('.verdict');if(b){const k=b.dataset.key;st[k]=st[k]||{};st[k].note=e.target.value;later(k);out.value=feedback()}
 if(e.target.classList.contains('missed')){const k=e.target.dataset.repo+'|_missed';st[k]={note:e.target.value};later(k);out.value=feedback()}});
document.getElementById('copy').addEventListener('click',()=>{const t=feedback();out.value=t;const done=m=>document.getElementById('copied').textContent=m;
 if(navigator.clipboard)navigator.clipboard.writeText(t).then(()=>done('Copied.'),()=>{out.select();done('Selected — copy it with your keyboard.')});else{out.select();done('Selected — copy it with your keyboard.')}});
const tip=document.getElementById('tip'),tt=document.getElementById('tt'),tu=document.getElementById('tu');
document.querySelectorAll('.node').forEach(n=>{const show=()=>{tt.textContent=n.dataset.tip;tu.textContent=n.dataset.usage||'';tu.hidden=!n.dataset.usage;tip.hidden=false;
 const r=n.getBoundingClientRect();tip.style.left=Math.max(8,Math.min(innerWidth-470,r.left))+'px';tip.style.top=(r.bottom+6)+'px'};
 n.addEventListener('mouseenter',show);n.addEventListener('focus',show);n.addEventListener('mouseleave',()=>tip.hidden=true);n.addEventListener('blur',()=>tip.hidden=true)});
paint();
(async()=>{try{const c=window.claude;if(!c||!c.use)return;const db=await c.use('db');if(!db)return;const col=db.collection('reviews');
 col.onSnapshot(s=>{s.docs.forEach(d=>{const x=d.data();if(x&&x.k)st[x.k]={v:x.v||null,note:x.note||''}});paint()},()=>{});
 remote=k=>{const v=st[k]||{};col.doc(sid(k)).set({k,v:v.v||null,note:v.note||'',label:(boxes.find(b=>b.dataset.key===k)||{dataset:{}}).dataset.label||'',at:new Date().toISOString()}).catch(()=>{})}}catch(e){}})();
})();
</script></body></html>'''


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('maps', nargs='+', help='one map.md, or several for one page with an overview')
    ap.add_argument('-o', '--out'); ap.add_argument('--title')
    a = ap.parse_args()
    models = [parse(Path(m).read_text(encoding='utf-8')) for m in a.maps]
    out = Path(a.out or Path(a.maps[0]).with_name('review.html'))
    out.write_text(render(models, a.title), encoding='utf-8')
    for m, path in zip(models, a.maps):
        by = {l: sum(c['life'] == l for c in m['cards']) for l in LIFE}
        life = ', '.join(f'{n} {l}' for l, n in by.items() if n)
        print(f'{path}: {len(m["cards"])} cards ({life or "none"}), {len(m["tools"])} tools in place, {len(m["grill"])} questions,'
              f' {len(m["roadmap"]["milestones"])} milestones')
        if not m['cards']:
            print(f'warning: no candidate cards in {path} — check the card headings follow the template', file=sys.stderr)
        for w in lint(m):
            print(f'warning: {path}: {w}', file=sys.stderr)
    print(f'-> {out}')


if __name__ == '__main__':
    main()
