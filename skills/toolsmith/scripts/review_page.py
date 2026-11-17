#!/usr/bin/env python3
"""Render a toolsmith map (map.md) into one self-contained HTML review page.

    python3 review_page.py map.md [more-maps.md …] [-o review.html] [--title "…"]

Standard library only. The page shows the app with its handles by category (the Lab drawn around
the six others), every proposed card with its usage, the tools already in place and the grill.
The reviewer marks each item right / wrong / unsure with a note — kept in the browser — and copies
a Markdown feedback block back to the agent. No server, no network: the file works opened locally
or published as a static page.
"""
import argparse, html, json, re, sys
from pathlib import Path

CATS = ['launch', 'ingress', 'runtime', 'state', 'egress', 'eyes', 'lab']
LABELS = {'launch': 'Launch & loop', 'ingress': 'Ingress', 'runtime': 'Runtime', 'state': 'State',
          'egress': 'Egress', 'eyes': 'Eyes & logs', 'lab': 'Lab'}
HINT = {'launch': 'start · ready · isolate · reset', 'ingress': 'drive it, as someone',
        'runtime': 'inside the live process', 'state': 'data and time', 'egress': 'what leaves',
        'eyes': 'screenshots · logs · traces', 'lab': 'the environment around the runtime'}
CAT_RX = '|'.join(CATS)


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


def parse(md):
    secs = sections(md)
    title = (md.splitlines() or [''])[0].lstrip('# ').strip()
    pre = secs.get('_pre', '')
    summary = field(pre, 'In one paragraph')
    cards, cur, in_code = [], None, False
    for line in find(secs, 'candidate').splitlines():
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
        way = next((b for b in bits if re.search(r'reach|bring|witness|lab|live', b.lower())), '')
        out_cards.append({
            'name': re.sub(r'[`*]', '', name).strip(), 'cat': cat, 'also': also,
            'point': bits[0] if bits else '', 'way': way, 'cost': next((b for b in bits if b.lower().startswith('cost')), ''),
            'status': 'half' if fin and not re.match(r'\**new', fin, re.I) else 'missing',
            'usage': usage.group(1).rstrip() if usage else '', 'scripts': scripts,
            'lines': [(k, field(body, k)) for k in ('Is', 'Finishes', 'Gives the agent', 'Needs', 'Uses', 'Not a script because', 'Fence', 'Parallel', 'Permission') if field(body, k)],
        })
    tools = []
    for rows in tables(find(secs, 'tools already')):
        for r in rows:
            nm = re.sub(r'[`*]', '', col(r, 'tool')).strip()
            if not nm:
                continue
            c = (col(r, 'category') or '').lower()
            cat = next((x for x in CATS if c.startswith(x)), 'launch')
            tools.append({'name': nm, 'cat': cat, 'way': col(r, 'way'), 'usage': col(r, 'usage'), 'status': 'exists'})
    par = find(secs, 'parallel agents')
    m = re.search(r'at once today:\s*\**\s*(\d+|[^*\n—]+)', par)
    parallel = {'count': m.group(1).strip() if m else '', 'line': '', 'rows': []}
    lm = re.search(r'at once today:[^\n]*?—\s*(.*)', par)
    parallel['line'] = lm.group(1).strip() if lm else ''
    for rows in tables(par):
        for r in rows:
            parallel['rows'].append([col(r, 'shared'), col(r, 'shared by'), col(r, 'what collides'), col(r, 'isolation'), col(r, 'proposal')])
    guards = [[col(r, 'rule'), col(r, 'guard'), col(r, 'kind')] for rows in tables(find(secs, 'rules')) for r in rows]
    road = find(secs, 'roadmap')
    foundations = [[col(r, 'foundation'), col(r, 'used by'), col(r, 'unlocks'), col(r, 'cost')] for rows in tables(road) for r in rows if col(r, 'foundation')]
    milestones, cur = [], None
    for line in road.splitlines():
        mh = re.match(r'^#{3,4}\s+(.*)$', line)
        if mh:
            cur = {'title': mh.group(1).strip(), 'body': []}; milestones.append(cur)
        elif cur is not None and line.strip() and not line.startswith('**Deferred'):
            cur['body'].append(line.strip())
    deferred = field(road, 'Deferred')
    roadmap = {'foundations': foundations, 'milestones': milestones, 'deferred': deferred,
               'mermaid': (re.search(r'```mermaid\n(.*?)```', road, re.S) or [None, ''])[1] if '```mermaid' in road else ''}
    return {'title': title, 'summary': summary, 'parallel': parallel, 'guards': guards, 'roadmap': roadmap, 'cards': out_cards, 'tools': tools,
            'grill': bullets(find(secs, 'grill')), 'unknowns': bullets(find(secs, 'unknowns'))}


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
    tip = f'{h["name"]} — {WORD[h["status"]]}' + (f' · {h["way"]}' if h.get('way') else '')
    also = ''.join(f'<span class="also">+{LABELS[a]}</span>' for a in h.get('also', []))
    sc = f'<span class="sc">{len(h["scripts"])} scripts</span>' if h.get('scripts') else ''
    inner = f'<span class="sym">{SYM[h["status"]]}</span><span class="nm">{esc(h["name"])}</span>{also}{sc}'
    data = f'class="node {h["status"]}" data-tip="{esc(tip)}" data-usage="{esc(h.get("usage", ""))}"'
    return f'<a {data} href="#{anchor}">{inner}</a>' if anchor else f'<span {data} tabindex="0">{inner}</span>'


def picture(model, rid, name):
    hs = [(t, None) for t in model['tools']] + [(c, f'{rid}-card-{i}') for i, c in enumerate(model['cards'])]
    order = {'exists': 0, 'half': 1, 'missing': 2}

    def box(cat, cls='cat'):
        items = sorted([x for x in hs if x[0]['cat'] == cat], key=lambda x: order[x[0]['status']])
        n = {s: sum(x[0]['status'] == s for x in items) for s in order}
        summ = ' · '.join(f'{n[s]} {WORD[s]}' for s in order if n[s]) or 'nothing — a gap'
        return (f'<div class="{cls}{" empty" if not items else ""}"><div class="head"><h4>{LABELS[cat]}</h4>'
                f'<span class="hint">{HINT[cat]}</span><span class="sum">{summ}</span></div>'
                f'<div class="nodes">{"".join(node(h, a) for h, a in items)}</div></div>')
    rows = (f'<div class="row">{"".join(box(c) for c in ("launch", "ingress", "runtime"))}</div>'
            f'<div class="hub"><strong>{esc(name)}</strong><span class="legend">● exists · ◐ to finish · ◌ missing</span></div>'
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


def repo_section(model, rid, multi):
    name = short_name(model)
    k = lambda x: f'{rid}|{x}'
    cards = []
    for i, c in enumerate(model['cards']):
        lines = ''.join(f'<div><strong>{esc(a)}:</strong> {md(b)}</div>' for a, b in c['lines'])
        scripts = ('<div class="scripts"><strong>Scripts run through it</strong><ul>'
                   + ''.join(f'<li><code>{esc(n)}</code> — {md(u)}</li>' for n, u in c['scripts']) + '</ul></div>') if c['scripts'] else ''
        usage = f'<pre>{esc(c["usage"])}</pre>' if c['usage'] else '<p class="warn">No usage example.</p>'
        cards.append(f'<li class="item" id="{rid}-card-{i}"><div class="main"><div class="title"><span class="st {c["status"]}">{SYM[c["status"]]} {WORD[c["status"]]}</span> '
                     f'{esc(c["name"])} <span class="tag">{LABELS[c["cat"]]}</span>{"".join(f"<span class=tag>+{LABELS[a]}</span>" for a in c["also"])}'
                     f' <span class="tag way">{esc(c["way"])}</span> <span class="muted">{esc(c["cost"])}</span></div>'
                     f'{usage}{lines}{scripts}</div>{verdict(k("card:" + c["name"]), c["name"])}</li>')
    tools = ''.join(f'<li class="item"><div class="main"><div class="title"><span class="st exists">● exists</span> {md(t["name"])} '
                    f'<span class="tag">{LABELS[t["cat"]]}</span></div>{f"<div class=muted>{md(t["usage"])}</div>" if t["usage"] else ""}</div>'
                    f'{verdict(k("tool:" + t["name"]), t["name"])}</li>' for t in model['tools'])
    grill = ''.join(f'<li class="item"><div class="main"><div class="title">{md(q)}</div></div>{verdict(k(f"grill:{j + 1}"), q)}</li>'
                    for j, q in enumerate(model['grill']))
    parts = [f'<section class="panel"><h3>The app and its handles</h3><p class="muted">The Lab frames the runtime; hover a node for its '
             f'usage, click a proposed one to jump to its card.</p>{picture(model, rid, name)}</section>']
    rm = model['roadmap']
    if rm['foundations'] or rm['milestones']:
        ms = ''.join(f'<li class="item"><div class="main"><div class="title">{md(m["title"])}</div>'
                     + ''.join(f'<div>{md(b)}</div>' for b in m['body']) + f'</div>{verdict(k("milestone:" + m["title"][:40]), m["title"])}</li>'
                     for m in rm['milestones'])
        parts.append('<section class="panel"><h3>Roadmap</h3><p class="muted">Foundations first, then milestones — accept them by milestone ("go for M1").</p>'
                     + (f'<h4>Foundations</h4>{table(["Foundation", "Used by", "Unlocks", "Cost"], rm["foundations"])}' if rm['foundations'] else '')
                     + (f'<pre class="mermaid">{esc(rm["mermaid"])}</pre>' if rm['mermaid'] else '')
                     + (f'<ul class="items">{ms}</ul>' if ms else '')
                     + (f'<p class="muted"><strong>Deferred:</strong> {md(rm["deferred"])}</p>' if rm['deferred'] else '') + '</section>')
    pa = model['parallel']
    if pa['count'] or pa['rows']:
        parts.append(f'<section class="panel"><h3>Parallel agents</h3><p><strong class="big">{esc(pa["count"] or "?")}</strong> '
                     f'agent(s) can safely work at once today. {md(pa["line"])}</p>'
                     + (table(['Shared resource', 'Shared by', 'What collides', 'Isolation today', 'Proposal'], pa['rows']) if pa['rows'] else '')
                     + f'{verdict(k("parallel:section"), "Parallel agents analysis")}</section>')
    if model['guards']:
        parts.append(f'<section class="panel"><h3>Rules → guards</h3><p class="muted">Rules the agent files state in prose, and what would enforce each.</p>'
                     f'{table(["Rule", "Guard", "Kind"], model["guards"])}{verdict(k("guards:section"), "Rules to guards")}</section>')
    parts.append(f'<section class="panel"><h3>Proposed handles ({len(model["cards"])})</h3><p class="muted">Would you build it? Is the usage right? '
                 f'Is it in the right place?</p><ul class="items">{"".join(cards)}</ul></section>')
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
        hs = m['tools'] + m['cards']
        cells = ''
        for c in CATS:
            x = [h for h in hs if h['cat'] == c]
            n = {s: sum(h['status'] == s for h in x) for s in ('exists', 'half', 'missing')}
            cells += ('<td class="gap">gap</td>' if not x else
                      '<td>' + ' '.join(f'{SYM[s]}{n[s]}' for s in n if n[s]) + '</td>')
        m1 = next((ms['title'] for ms in m['roadmap']['milestones']), '—')
        rows.append(f'<tr><th scope="row"><a href="#{rid}">{esc(short_name(m))}</a></th>{cells}'
                    f'<td>{esc(m["parallel"]["count"] or "—")}</td><td>{md(m1)}</td></tr>')
    return ('<section class="panel"><h2>All repos</h2><p class="muted">Handles per category (● exists · ◐ to finish · ◌ missing), agents that can '
            'work at once today, and each roadmap\'s first milestone.</p><div class="tw"><table><thead><tr><th>Repo</th>'
            + ''.join(f'<th>{LABELS[c]}</th>' for c in CATS) + '<th>Parallel</th><th>First milestone</th></tr></thead><tbody>'
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
.verdict{display:flex;flex-wrap:wrap;gap:6px;justify-content:flex-end;max-width:330px;align-content:start}
.verdict button{font:500 13px system-ui,sans-serif;border:1px solid var(--line);background:var(--s);color:var(--fg2);border-radius:999px;padding:4px 10px;cursor:pointer}
.verdict button[aria-pressed=true][data-v=right]{background:var(--oks);border-color:var(--ok);color:var(--ok)}
.verdict button[aria-pressed=true][data-v=wrong]{background:var(--bads);border-color:var(--bad);color:var(--bad)}
.verdict button[aria-pressed=true][data-v=unsure]{background:var(--halfs);border-color:var(--half);color:var(--half)}
.verdict input,textarea{flex:1 1 100%;font:13px system-ui,sans-serif;color:var(--fg);background:var(--s2);border:1px solid var(--line);border-radius:6px;padding:5px 8px;box-sizing:border-box;width:100%}
button:focus-visible,input:focus-visible,textarea:focus-visible,.node:focus-visible,a:focus-visible{outline:2px solid var(--acc);outline-offset:2px}
.tip{position:fixed;z-index:9;pointer-events:none;background:var(--fg);color:var(--bg);font-size:12.5px;padding:6px 9px;border-radius:6px;max-width:min(460px,calc(100vw - 32px))}
.tip pre{background:transparent;color:inherit;padding:0;margin:4px 0 0;white-space:pre-wrap;max-height:200px;overflow:hidden}
.big{font-size:22px}.tw{overflow-x:auto}table{border-collapse:collapse;min-width:640px;font-size:13.5px;width:100%}th,td{text-align:left;padding:6px 8px;border-bottom:1px solid var(--line);vertical-align:top}th{color:var(--fg3);font-size:12px;text-transform:uppercase;letter-spacing:.05em} td.gap{color:var(--bad);font-weight:600} th[scope=row] a{color:var(--fg);font-weight:600}
.copy{font:600 14px system-ui,sans-serif;background:var(--acc);color:#fff;border:0;border-radius:8px;padding:8px 14px;cursor:pointer}
@media (max-width:760px){.row{grid-template-columns:1fr}.item{grid-template-columns:1fr}.verdict{justify-content:flex-start;max-width:none}}
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
function feedback(){const L=['# Toolsmith review feedback',''];const grp={milestone:'Roadmap milestones',card:'Proposed handles',grill:'Answers to the questions',parallel:'Parallel agents',guards:'Rules to guards',tool:'Already in place'};
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
        print(f'{path}: {len(m["cards"])} cards, {len(m["tools"])} tools in place, {len(m["grill"])} questions,'
              f' {len(m["roadmap"]["milestones"])} milestones')
        if not m['cards']:
            print(f'warning: no candidate cards in {path} — check the card headings follow the template', file=sys.stderr)
    print(f'-> {out}')


if __name__ == '__main__':
    main()
