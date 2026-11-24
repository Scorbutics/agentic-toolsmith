#!/usr/bin/env python3
"""Evaluate the toolsmith skill against a baseline, on public repositories, with any model.

    ./evals/run.sh                                   # all scenarios, sonnet, with skill + baseline
    ./evals/run.sh --only lobsters --model opus      # one scenario, one model
    ./evals/run.sh --no-baseline --model sonnet --model haiku
    ./evals/run.sh --judge                           # also: where the proposals fall on the evidence grid
    ./evals/run.sh --runs 3 --skill /tmp/old/skills/toolsmith   # three runs per cell, another version of the skill

For each scenario: clone the repository at a pinned commit (cached), then run the Claude Code CLI
headless twice on the same prompt — once with the skill installed in the project, once without —
and score both outputs on the scenario's expected behaviours (format-agnostic keyword groups), the
number of runnable usage examples, whether a roadmap exists, and whether cited file:line
references resolve. Runs are read-only on the repository; outputs land in eval-runs/<timestamp>/.
With --judge, evals/judge.py then classifies every proposal by level and way (distribution.md):
keyword scores cannot tell a map that covers the grid from one that repeats the same cell.

Needs: git, python3, and the `claude` CLI logged in. Each run is one agent session (several
minutes, real usage).
"""
import argparse, json, os, re, shutil, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent / 'skills' / 'toolsmith'
CACHE = Path(os.environ.get('XDG_CACHE_HOME', Path.home() / '.cache')) / 'toolsmith-evals' / 'repos'

READ_ONLY = ("Read-only: do not install, build, launch, use the network, query a database or modify the project. "
             "Write the result as Markdown to {out}.")
# `neutral` names no way of working; `ladder` is the prompt of the 2026-11-17 and early 2026-11-24 runs. It lists
# the reach-in steps (launch, log in, reach a state…) and so pushes every arm toward the live app — kept only to
# reproduce those numbers.
PROMPTS = {
    'neutral': ("Map this project's tooling for coding agents: what an agent working on this project can and cannot do "
                "today, from the command line, to understand it, change it and verify its own changes, and propose the "
                "tools to build, as a roadmap. " + READ_ONLY),
    'ladder': ("Map this project's tooling for coding agents: what an agent can and cannot do from the command line "
               "against the running project (launch it, log in, reach a state, act, see the result, check it, reset), "
               "and propose the tools to build, as a roadmap. " + READ_ONLY),
}
SKILL_PREFIX = ("Use the toolsmith skill in map scope (/toolsmith map). Nobody is available to answer questions: "
                "write them with your recommended answers. ")
TOOLS = ['Read', 'Grep', 'Glob', 'Skill', 'Bash(ls:*)', 'Bash(git log:*)', 'Bash(git status:*)', 'Bash(git ls-files:*)',
         'Bash(python3:*)', 'Bash(wc:*)', 'Bash(head:*)', 'Bash(find:*)']


def sh(cmd, **kw):
    return subprocess.run(cmd, check=True, text=True, capture_output=True, **kw)


def checkout(sc):
    """Clone once into the cache (blobless), then a clean worktree copy per run."""
    src = CACHE / sc['name']
    if not (src / '.git').exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        env = {**os.environ, 'GIT_LFS_SKIP_SMUDGE': '1'}
        print(f'  cloning {sc["repo"]} (once, cached in {src})', flush=True)
        sh(['git', 'clone', '--quiet', '--filter=blob:none', '--no-checkout', sc['repo'], str(src)], env=env)
    sh(['git', '-C', str(src), 'checkout', '--quiet', '--force', sc['commit']],
       env={**os.environ, 'GIT_LFS_SKIP_SMUDGE': '1'})
    return src


def run_agent(repo, out, prompt, model, with_skill, timeout, skill=SKILL):
    skills_dir = repo / '.claude' / 'skills'
    if skills_dir.exists():
        shutil.rmtree(repo / '.claude')
    if with_skill:
        skills_dir.mkdir(parents=True)
        shutil.copytree(skill, skills_dir / 'toolsmith', ignore=shutil.ignore_patterns('__pycache__'))
        excl = repo / '.git' / 'info' / 'exclude'
        if '.claude/' not in excl.read_text():
            excl.write_text(excl.read_text() + '\n.claude/\n')
    out.parent.mkdir(parents=True, exist_ok=True)
    # absolute paths in permission rules take a double leading slash (`//abs/path`)
    tools = TOOLS + [f'Write(/{out.parent}/**)', f'Edit(/{out.parent}/**)', f'Bash(mkdir -p {out.parent}:*)']
    cmd = ['claude', '-p', prompt.format(out=out), '--model', model, '--output-format', 'json',
           '--add-dir', str(out.parent), '--allowedTools', *tools]
    t0 = time.time()
    try:
        p = subprocess.run(cmd, cwd=repo, text=True, capture_output=True, timeout=timeout)
        meta = json.loads(p.stdout) if p.stdout.strip().startswith('{') else {'raw': p.stdout[-2000:], 'stderr': p.stderr[-2000:]}
    except subprocess.TimeoutExpired:
        meta = {'error': f'timeout after {timeout}s'}
    finally:
        if (repo / '.claude').exists():
            shutil.rmtree(repo / '.claude')
    meta['seconds'] = round(time.time() - t0)
    (out.parent / 'session.json').write_text(json.dumps(meta, indent=1))
    return meta


REF = re.compile(r'`?((?:[\w.\-]+/)*[\w.\-]+\.[A-Za-z0-9]+):(\d+)')


def score(sc, text, repo):
    low = text.lower()
    found = [any(k.lower() in low for k in e['any_of']) for e in sc['expected']]
    usages = len(re.findall(r'^\s*\$ \S', text, re.M))
    refs = REF.findall(text)
    ok = 0
    for path, line in refs:
        p = repo / path
        hits = [p] if p.is_file() else list(repo.glob('**/' + path))[:1]
        if hits and hits[0].is_file():
            n = sum(1 for _ in hits[0].open(errors='ignore'))
            ok += int(line) <= max(n, 1)
    return {
        'expected': f'{sum(found)}/{len(found)}', 'expected_ratio': round(sum(found) / len(found), 2),
        'missed': [e['behavior'] for e, f in zip(sc['expected'], found) if not f],
        'usage_examples': usages,
        'roadmap': bool(re.search(r'\bM1\b|milestone', text, re.I)),
        'evidence': f'{ok}/{len(refs)}', 'chars': len(text),
    }


def main():
    ap = argparse.ArgumentParser(description='Evaluate the toolsmith skill against a baseline.')
    ap.add_argument('--only', action='append', help='scenario name (repeatable); default: all')
    ap.add_argument('--model', action='append', help='model alias or id (repeatable); default: sonnet')
    ap.add_argument('--no-baseline', action='store_true', help='skip the run without the skill')
    ap.add_argument('--timeout', type=int, default=1500, help='seconds per agent run (default 1500)')
    ap.add_argument('--out', help='output directory (default: eval-runs/<timestamp>)')
    ap.add_argument('--judge', action='store_true', help='then judge the grid distribution (evals/judge.py)')
    ap.add_argument('--prompt', choices=sorted(PROMPTS), default='neutral',
                    help='task wording (default neutral; ladder reproduces the runs before 2026-11-25)')
    ap.add_argument('--runs', type=int, default=1, help='runs per scenario × model × arm (default 1); >1 writes r1, r2…')
    ap.add_argument('--skill', type=Path, default=SKILL, help='the skill directory to test (default: this checkout\'s)')
    a = ap.parse_args()
    if not (a.skill / 'SKILL.md').is_file():
        sys.exit(f'evals: no SKILL.md in {a.skill}')
    task = PROMPTS[a.prompt]
    if not shutil.which('claude'):
        sys.exit('evals: the `claude` CLI is required (and logged in)')
    scenarios = [json.loads(p.read_text()) for p in sorted((HERE / 'scenarios').glob('*.json'))]
    if a.only:
        scenarios = [s for s in scenarios if s['name'] in a.only]
    models = a.model or ['sonnet']
    out_root = Path(a.out or HERE.parent / 'eval-runs' / time.strftime('%Y%m%d-%H%M%S'))
    arms = [('skill', True)] + ([] if a.no_baseline else [('baseline', False)])
    out_root.mkdir(parents=True, exist_ok=True)
    (out_root / 'run.json').write_text(json.dumps({'prompt': a.prompt, 'task': task, 'skill': str(a.skill.resolve()),
                                                   'runs': a.runs, 'models': models}, indent=1))
    results = []
    for sc in scenarios:
        print(f'{sc["name"]} — {sc["shape"]}', flush=True)
        repo = checkout(sc)
        for model in models:
            for arm, with_skill in arms:
                for i in range(1, a.runs + 1):
                    out = out_root / sc['name'] / model / arm / (f'r{i}' if a.runs > 1 else '') / 'map.md'
                    print(f'  {model:8} {arm:8} r{i} running…', flush=True)
                    meta = run_agent(repo, out, (SKILL_PREFIX + task) if with_skill else task, model, with_skill,
                                     a.timeout, a.skill)
                    text = out.read_text(errors='ignore') if out.exists() else ''
                    if not text and len(meta.get('result') or '') > 2000:  # wrote nothing, but answered in full
                        text = meta['result']; out.write_text(text)
                    s = score(sc, text, repo) if text else {'expected': '0/%d' % len(sc['expected']), 'expected_ratio': 0,
                                                            'missed': ['no output written'], 'usage_examples': 0,
                                                            'roadmap': False, 'evidence': '0/0', 'chars': 0}
                    s.update({'scenario': sc['name'], 'model': model, 'arm': arm, 'run': i, 'prompt': a.prompt,
                              'seconds': meta.get('seconds'), 'cost_usd': meta.get('total_cost_usd')})
                    results.append(s)
                    print(f'  {model:8} {arm:8} r{i} expected {s["expected"]}  usage examples {s["usage_examples"]}  '
                          f'roadmap {"yes" if s["roadmap"] else "no"}  evidence {s["evidence"]}  {s["seconds"]}s', flush=True)
    (out_root / 'results.json').write_text(json.dumps(results, indent=1))
    lines = ['| Scenario | Model | Arm | Run | Expected | Usage examples | Roadmap | Evidence | Time |', '|---|---|---|---|---|---|---|---|---|']
    lines += [f'| {r["scenario"]} | {r["model"]} | {r["arm"]} | {r["run"]} | {r["expected"]} | {r["usage_examples"]} | '
              f'{"yes" if r["roadmap"] else "no"} | {r["evidence"]} | {r["seconds"]}s |' for r in results]
    (out_root / 'results.md').write_text('\n'.join(lines) + '\n')
    print('\n' + '\n'.join(lines) + f'\n\nresults: {out_root}')
    if a.judge:
        subprocess.run([sys.executable, str(HERE / 'judge.py'), str(out_root)], check=False)


if __name__ == '__main__':
    main()
