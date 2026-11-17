#!/usr/bin/env python3
"""Render a toolsmith map (map.md) into one self-contained HTML review page.

    python3 review_page.py map.md [-o review.html]

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
    return {'title': title, 'summary': summary, 'parallel': parallel, 'guards': guards, 'cards': out_cards, 'tools': tools,
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


def picture(model):
    hs = [(t, None) for t in model['tools']] + [(c, f'card-{i}') for i, c in enumerate(model['cards'])]
    order = {'exists': 0, 'half': 1, 'missing': 2}

    def box(cat, cls='cat'):
        items = sorted([x for x in hs if x[0]['cat'] == cat], key=lambda x: order[x[0]['status']])
        n = {s: sum(x[0]['status'] == s for x in items) for s in order}
        summ = ' · '.join(f'{n[s]} {WORD[s]}' for s in order if n[s]) or 'nothing — a gap'
        return (f'<div class="{cls}{" empty" if not items else ""}"><div class="head"><h4>{LABELS[cat]}</h4>'
                f'<span class="hint">{HINT[cat]}</span><span class="sum">{summ}</span></div>'
                f'<div class="nodes">{"".join(node(h, a) for h, a in items)}</div></div>')
    rows = (f'<div class="row">{"".join(box(c) for c in ("launch", "ingress", "runtime"))}</div>'
            f'<div class="hub"><strong>{esc(model["title"])}</strong><span class="legend">● exists · ◐ to finish · ◌ missing</span></div>'
            f'<div class="row">{"".join(box(c) for c in ("eyes", "egress", "state"))}</div>')
    return f'<div class="labframe">{box("lab", "labhead")}{rows}</div>'


def verdict(key, label):
    return (f'<div class="verdict" data-key="{esc(key)}" data-label="{esc(label[:200])}">'
            '<button type="button" data-v="right">✓ Right</button><button type="button" data-v="wrong">✗ Wrong</button>'
            '<button type="button" data-v="unsure">? Unsure</button>'
            f'<input type="text" placeholder="Note, question or answer" aria-label="Note for {esc(label[:60])}"></div>')


def render(model):
    cards = []
    for i, c in enumerate(model['cards']):
        lines = ''.join(f'<div><strong>{esc(k)}:</strong> {md(v)}</div>' for k, v in c['lines'])
        scripts = ('<div class="scripts"><strong>Scripts run through it</strong><ul>'
                   + ''.join(f'<li><code>{esc(n)}</code> — {md(u)}</li>' for n, u in c['scripts']) + '</ul></div>') if c['scripts'] else ''
        usage = f'<pre>{esc(c["usage"])}</pre>' if c['usage'] else '<p class="warn">No usage example.</p>'
        cards.append(f'<li class="item" id="card-{i}"><div class="main"><div class="title"><span class="st {c["status"]}">{SYM[c["status"]]} {WORD[c["status"]]}</span> '
                     f'{esc(c["name"])} <span class="tag">{LABELS[c["cat"]]}</span>{"".join(f"<span class=tag>+{LABELS[a]}</span>" for a in c["also"])}'
                     f' <span class="tag way">{esc(c["way"])}</span> <span class="muted">{esc(c["cost"])}</span></div>'
                     f'{usage}{lines}{scripts}</div>{verdict(f"card:{c["name"]}", c["name"])}</li>')
    tools = ''.join(f'<li class="item"><div class="main"><div class="title"><span class="st exists">● exists</span> {md(t["name"])} '
                    f'<span class="tag">{LABELS[t["cat"]]}</span></div>{f"<div class=muted>{md(t["usage"])}</div>" if t["usage"] else ""}</div>'
                    f'{verdict(f"tool:{t["name"]}", t["name"])}</li>' for t in model['tools'])
    grill = ''.join(f'<li class="item"><div class="main"><div class="title">{md(q)}</div></div>{verdict(f"grill:{j + 1}", q)}</li>'
                    for j, q in enumerate(model['grill']))
    pa = model['parallel']
    par_html = ''
    if pa['count'] or pa['rows']:
        trs = ''.join('<tr>' + ''.join(f'<td>{md(x)}</td>' for x in r) + '</tr>' for r in pa['rows'])
        par_html = (f'<section class="panel"><h2>Parallel agents</h2><p><strong class="big">{esc(pa["count"] or "?")}</strong> '
                    f'agent(s) can safely work at once today. {md(pa["line"])}</p>'
                    + (f'<div class="tw"><table><thead><tr><th>Shared resource</th><th>Shared by</th><th>What collides</th>'
                       f'<th>Isolation today</th><th>Proposal</th></tr></thead><tbody>{trs}</tbody></table></div>' if trs else '')
                    + f'{verdict("parallel:section", "Parallel agents analysis")}</section>')
    if model['guards']:
        trs = ''.join(f'<tr><td>{md(a)}</td><td>{md(b)}</td><td>{md(c)}</td></tr>' for a, b, c in model['guards'])
        par_html += (f'<section class="panel"><h2>Rules → guards</h2><p class="muted">Rules your agent files state in prose, '
                     f'and what would enforce each.</p><div class="tw"><table><thead><tr><th>Rule</th><th>Guard</th><th>Kind</th></tr></thead>'
                     f'<tbody>{trs}</tbody></table></div>{verdict("guards:section", "Rules to guards")}</section>')
    store_key = 'toolsmith-review:' + re.sub(r'\W+', '-', model['title'])[:80]
    return TEMPLATE.replace('{{TITLE}}', esc(model['title'])).replace('{{SUMMARY}}', md(model['summary'])) \
        .replace('{{PICTURE}}', picture(model)).replace('{{PARALLEL}}', par_html).replace('{{CARDS}}', ''.join(cards)) \
        .replace('{{NCARDS}}', str(len(model['cards']))).replace('{{TOOLS}}', tools) \
        .replace('{{NTOOLS}}', str(len(model['tools']))).replace('{{GRILL}}', grill) \
        .replace('{{NGRILL}}', str(len(model['grill']))).replace('{{STORE}}', json.dumps(store_key))


TEMPLATE = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Toolsmith review</title>
<style>
:root{--bg:#f6f7f9;--s:#fff;--s2:#eef1f5;--line:#dde2ea;--fg:#14171c;--fg2:#4a5260;--fg3:#6b7380;--acc:#2a78d6;--accs:#dbe8f8;
--ok:#0a7d0a;--oks:#dcf1dc;--half:#8a6100;--halfs:#f8ecd0;--bad:#c23434;--bads:#f8dede;--lab:#7a8a99;--labs:#f0f3f6}
@media (prefers-color-scheme:dark){:root{--bg:#121418;--s:#1a1d22;--s2:#22262d;--line:#30353e;--fg:#eef0f3;--fg2:#b6bcc6;--fg3:#8d95a1;
--acc:#3987e5;--accs:#1d3350;--ok:#3cc23c;--oks:#17331a;--half:#f0b84a;--halfs:#3a2e12;--bad:#ef7070;--bads:#3d1c1d;--lab:#6f7d8b;--labs:#171a1f;color-scheme:dark}}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif;padding:0 16px 48px}
.wrap{max-width:1120px;margin:0 auto;display:grid;gap:22px}
h1,h2,h3,h4{margin:0;text-wrap:balance} h1{font-size:24px;padding-top:20px} h2{font-size:18px} h4{font-size:14px}
code,pre{font-family:ui-monospace,"SFMono-Regular",Menlo,monospace;font-size:12.5px} code{background:var(--s2);padding:1px 5px;border-radius:4px;overflow-wrap:anywhere}
pre{background:var(--s2);padding:8px 10px;border-radius:6px;overflow-x:auto;margin:4px 0}
.muted{color:var(--fg3)} .warn{color:var(--bad)} .panel{background:var(--s);border:1px solid var(--line);border-radius:10px;padding:16px}
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
button:focus-visible,input:focus-visible,textarea:focus-visible,.node:focus-visible{outline:2px solid var(--acc);outline-offset:2px}
.tip{position:fixed;z-index:9;pointer-events:none;background:var(--fg);color:var(--bg);font-size:12.5px;padding:6px 9px;border-radius:6px;max-width:min(460px,calc(100vw - 32px))}
.tip pre{background:transparent;color:inherit;padding:0;margin:4px 0 0;white-space:pre-wrap;max-height:200px;overflow:hidden}
.big{font-size:22px}.tw{overflow-x:auto}table{border-collapse:collapse;min-width:640px;font-size:13.5px}th,td{text-align:left;padding:6px 8px;border-bottom:1px solid var(--line);vertical-align:top}th{color:var(--fg3);font-size:12px;text-transform:uppercase;letter-spacing:.05em}
.copy{font:600 14px system-ui,sans-serif;background:var(--acc);color:#fff;border:0;border-radius:8px;padding:8px 14px;cursor:pointer}
@media (max-width:760px){.row{grid-template-columns:1fr}.item{grid-template-columns:1fr}.verdict{justify-content:flex-start;max-width:none}}
</style></head><body><div class="wrap">
<header><h1>{{TITLE}}</h1><p class="muted">Review this plan: mark each item, add a note, question or answer, then copy the feedback back to the agent.</p><p>{{SUMMARY}}</p></header>
<section class="panel"><h2>The app and its handles</h2><p class="muted">The Lab frames the runtime; hover a node for its usage, click a proposed one to jump to its card.</p>{{PICTURE}}</section>
{{PARALLEL}}
<section class="panel"><h2>Proposed handles ({{NCARDS}})</h2><p class="muted">Would you build it? Is the usage right? Is it in the right place?</p><ul class="items">{{CARDS}}</ul></section>
<section class="panel"><h2>Questions for you ({{NGRILL}})</h2><p class="muted">Type your answer in the note.</p><ul class="items">{{GRILL}}</ul></section>
<section class="panel"><details><summary><h2 style="display:inline">Already in place ({{NTOOLS}})</h2></summary><ul class="items">{{TOOLS}}</ul></details></section>
<section class="panel"><h2>What did it miss?</h2><textarea id="missed" rows="3" placeholder="A handle you use or want that is not on the picture"></textarea></section>
<section class="panel"><h2>Send the feedback</h2><p class="muted">Copy this block and paste it to the agent.</p>
<button class="copy" id="copy" type="button">Copy feedback</button> <span id="copied" class="muted"></span>
<textarea id="out" rows="10" readonly></textarea></section>
</div><div class="tip" id="tip" hidden><span id="tt"></span><pre id="tu" hidden></pre></div>
<script>
(function(){
const KEY={{STORE}};let st={};try{st=JSON.parse(localStorage.getItem(KEY)||'{}')}catch(e){}
const save=()=>{try{localStorage.setItem(KEY,JSON.stringify(st))}catch(e){}};
const boxes=[...document.querySelectorAll('.verdict')],missed=document.getElementById('missed'),out=document.getElementById('out');
function paint(){boxes.forEach(b=>{const c=st[b.dataset.key]||{};b.querySelectorAll('button').forEach(x=>x.setAttribute('aria-pressed',String(c.v===x.dataset.v)));
 const i=b.querySelector('input');if(document.activeElement!==i)i.value=c.note||''});if(document.activeElement!==missed)missed.value=st._missed||'';out.value=feedback()}
function feedback(){const L=['# Toolsmith review feedback','',`Plan: ${document.querySelector('h1').textContent}`,''];
 const grp={card:'Proposed handles',grill:'Answers to the questions',parallel:'Parallel agents',guards:'Rules to guards',tool:'Already in place'};
 for(const g of ['card','grill','parallel','guards','tool']){const rows=boxes.filter(b=>b.dataset.key.startsWith(g+':')).map(b=>[b,st[b.dataset.key]||{}]).filter(([b,c])=>c.v||c.note);
  if(!rows.length)continue;L.push('## '+grp[g]);rows.forEach(([b,c])=>L.push(`- [${c.v||'note'}] ${b.dataset.label}${c.note?' — '+c.note:''}`));L.push('')}
 if(st._missed)L.push('## Missed',st._missed,'');return L.join('\n')}
document.addEventListener('click',e=>{const x=e.target.closest('.verdict button');if(!x)return;const k=x.closest('.verdict').dataset.key;
 st[k]=st[k]||{};st[k].v=st[k].v===x.dataset.v?null:x.dataset.v;save();paint()});
document.addEventListener('input',e=>{const b=e.target.closest('.verdict');if(b){st[b.dataset.key]=st[b.dataset.key]||{};st[b.dataset.key].note=e.target.value;save();out.value=feedback()}
 if(e.target===missed){st._missed=missed.value;save();out.value=feedback()}});
document.getElementById('copy').addEventListener('click',()=>{const t=feedback();out.value=t;
 const done=m=>document.getElementById('copied').textContent=m;
 if(navigator.clipboard)navigator.clipboard.writeText(t).then(()=>done('Copied.'),()=>{out.select();done('Selected — copy it with your keyboard.')});else{out.select();done('Selected — copy it with your keyboard.')}});
const tip=document.getElementById('tip'),tt=document.getElementById('tt'),tu=document.getElementById('tu');
document.querySelectorAll('.node').forEach(n=>{const show=()=>{tt.textContent=n.dataset.tip;tu.textContent=n.dataset.usage||'';tu.hidden=!n.dataset.usage;tip.hidden=false;
 const r=n.getBoundingClientRect();tip.style.left=Math.max(8,Math.min(innerWidth-470,r.left))+'px';tip.style.top=(r.bottom+6)+'px'};
 n.addEventListener('mouseenter',show);n.addEventListener('focus',show);n.addEventListener('mouseleave',()=>tip.hidden=true);n.addEventListener('blur',()=>tip.hidden=true)});
paint()})();
</script></body></html>'''


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('map'); ap.add_argument('-o', '--out')
    a = ap.parse_args()
    model = parse(Path(a.map).read_text(encoding='utf-8'))
    out = Path(a.out or Path(a.map).with_name('review.html'))
    out.write_text(render(model), encoding='utf-8')
    print(f'{out}: {len(model["cards"])} cards, {len(model["tools"])} tools in place, {len(model["grill"])} questions')
    if not model['cards']:
        print('warning: no candidate cards found — check the card headings follow the template', file=sys.stderr)


if __name__ == '__main__':
    main()
