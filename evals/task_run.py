#!/usr/bin/env python3
"""Task-based eval: does the tooling toolsmith builds let an agent finish a real task, unattended?

    python3 evals/task_run.py validate                          # every task: hidden tests fail before the fix, pass after
    python3 evals/task_run.py run --arm bare --arm toolsmith    # every task, both arms, sonnet
    python3 evals/task_run.py run --only fd-type-union --model sonnet --runs 2 --out <dir>
    python3 evals/task_run.py report <dir>

A task (evals/tasks/<name>.json) is a real bug fixed in a project's history: the agent starts at the
commit before the fix, gets the bug described as an issue would (symptom and expected behaviour, no
hint of the fix), and succeeds when the fix commit's own tests — hidden until the end — pass.

Arms:
  bare       — one session: the task.
  toolsmith  — two sessions. First, with the skill installed: `/toolsmith task "<task>"`, M1 taken as
               accepted, its handles built and proven — durable tooling only, the task NOT done. The
               skill is then removed (what it built stays: scripts, agent-file section). Second, a fresh
               session gets the same task prompt as `bare`.
  (--skill DIR tests another version of the skill.)

Recorded per run: success (hidden tests pass), contaminated (the tooling session already made them
pass — reported apart, never counted as a toolsmith success), cost and turns of each session, and
whether the task session called anything the tooling session created.

Runs happen in git worktrees of the eval cache, never in a person's checkout. The agent gets Read,
Edit, Write, Glob, Grep and Bash inside that worktree. Needs the `claude` CLI logged in.
"""
import argparse, json, os, re, shutil, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent / 'skills' / 'toolsmith'
CACHE = Path(os.environ.get('XDG_CACHE_HOME', Path.home() / '.cache')) / 'toolsmith-evals'
TOOLS = ['Read', 'Edit', 'Write', 'Glob', 'Grep', 'Bash', 'Skill']

TASK_PREFIX = ("You are working in this repository. Fix the bug below. Verify your fix the way you see fit before "
               "you finish; do not ask questions — nobody will answer.\n\n")
TOOLING_PROMPT = ("Use the toolsmith skill in task scope: /toolsmith task \"{task}\"\n\n"
                  "Nobody is available to answer: write your questions with your recommended answers and take them as "
                  "answered. Treat the first milestone (M1) of your roadmap as accepted by the human: build its handles "
                  "now, prove each one by running its usage example, and document them where the next agent looks "
                  "first (the agent file's \"How to reach the app\" section). Build durable tooling only — do NOT fix "
                  "the bug: another agent will do the task with what you build.")


def sh(cmd, cwd=None, timeout=1800, env=None):
    return subprocess.run(cmd, cwd=cwd, shell=isinstance(cmd, str), text=True, capture_output=True,
                          timeout=timeout, env=env)


def load(name=None):
    tasks = [json.loads(p.read_text()) for p in sorted((HERE / 'tasks').glob('*.json'))]
    return [t for t in tasks if not name or t['name'] in name]


def repo_cache(task):
    src = CACHE / 'repos' / task['project']
    if not (src / '.git').exists():
        src.parent.mkdir(parents=True, exist_ok=True)
        sh(['git', 'clone', '--quiet', '--filter=blob:none', '--no-checkout', task['repo'], str(src)])
    return src


def env_for(task):
    """Shared, prepared dependencies outside the worktree (a Python venv), exported to setup commands."""
    env = dict(os.environ)
    if task['project'] == 'healthchecks':
        venv = CACHE / 'venvs' / 'healthchecks'
        if not (venv / 'bin' / 'python').exists():
            sh([sys.executable, '-m', 'venv', str(venv)])
            for f in ('requirements.txt', 'requirements-dev.txt'):  # the tests need the dev requirements too
                req = sh(['git', '-C', str(repo_cache(task)), 'show', f"{task['fix']}:{f}"]).stdout
                (venv / f).write_text(req.replace('-r requirements.txt', ''))
            r = sh([str(venv / 'bin' / 'pip'), 'install', '-q', '-r', str(venv / 'requirements.txt'),
                    '-r', str(venv / 'requirements-dev.txt')], timeout=1800)
            if r.returncode:
                sys.exit(f'venv for healthchecks failed:\n{r.stderr[-2000:]}')
        env['TOOLSMITH_EVAL_VENV'] = str(venv)
    return env


def worktree(task, dest):
    """A fresh worktree at the commit before the fix, with the task's setup run."""
    src = repo_cache(task)
    if dest.exists():
        sh(['git', '-C', str(src), 'worktree', 'remove', '--force', str(dest)])
        shutil.rmtree(dest, ignore_errors=True)
    dest.parent.mkdir(parents=True, exist_ok=True)
    r = sh(['git', '-C', str(src), 'worktree', 'add', '--quiet', '--detach', str(dest), f"{task['fix']}^"])
    if r.returncode:
        sys.exit(r.stderr)
    s = sh(task['setup'], cwd=dest, env=env_for(task), timeout=3600)
    return s.stdout + s.stderr


def hidden_tests(task, dest):
    """Run the fix commit's tests against the worktree as it stands, then put the files back as they were."""
    saved = {f: (dest / f).read_bytes() if (dest / f).exists() else None for f in task['hidden']}
    try:
        sh(['git', 'checkout', task['fix'], '--', *task['hidden']], cwd=dest)
        r = sh(task['test'], cwd=dest, env=env_for(task), timeout=1800)
        return r.returncode == 0, (r.stdout + r.stderr)[-1500:]
    finally:
        for f, b in saved.items():
            if b is None:
                (dest / f).unlink(missing_ok=True)
            else:
                (dest / f).write_bytes(b)


def validate(tasks, root):
    ok = True
    for t in tasks:
        dest = root / 'validate' / t['name']
        worktree(t, dest)
        before, out_b = hidden_tests(t, dest)
        changed = [f for f in sh(['git', 'show', '--name-only', '--format=', t['fix']], cwd=dest).stdout.split() if f]
        sh(['git', 'checkout', t['fix'], '--', *changed], cwd=dest)
        after, out_a = hidden_tests(t, dest)
        good = (not before) and after
        ok &= good
        print(f"{t['name']:28} before fix: {'pass' if before else 'fail'} · after fix: {'pass' if after else 'fail'} — "
              f"{'valid' if good else 'INVALID'}", flush=True)
        if not good:
            print('  ' + (out_b if before else out_a)[-600:].replace('\n', '\n  '))
        sh(['git', '-C', str(repo_cache(t)), 'worktree', 'remove', '--force', str(dest)])
    return ok


def agent(prompt, cwd, model, timeout, log):
    """One headless session; the stream of events saved to `log`. Returns (result event, bash commands)."""
    cmd = ['claude', '-p', prompt, '--model', model, '--output-format', 'stream-json', '--verbose', '--allowedTools', *TOOLS]
    t0 = time.time()
    try:
        p = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, timeout=timeout)
        out = p.stdout
    except subprocess.TimeoutExpired as e:
        out = e.stdout or ''
        if isinstance(out, bytes):
            out = out.decode(errors='ignore')
    log.write_text(out)
    result, bash = {}, []
    for line in out.splitlines():
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if ev.get('type') == 'result':
            result = ev
        for c in (ev.get('message') or {}).get('content') or [] if ev.get('type') == 'assistant' else []:
            if isinstance(c, dict) and c.get('type') == 'tool_use' and c.get('name') == 'Bash':
                bash.append(c.get('input', {}).get('command', ''))
    result['seconds'] = round(time.time() - t0)
    return result, bash


def created_by(dest, base_files):
    """Paths the tooling session added (untracked or new), for spotting their use in the task session."""
    st = sh(['git', 'status', '--porcelain', '--untracked-files=all'], cwd=dest).stdout.splitlines()
    return sorted({l[3:].strip() for l in st if l[:2] in ('??', 'A ')} - base_files)


def run_one(t, arm, model, i, root, skill, timeouts):
    tag = f"{t['name']}/{model}/{arm}/r{i}"
    out = root / tag
    out.mkdir(parents=True, exist_ok=True)
    dest = root / 'work' / tag.replace('/', '-')
    worktree(t, dest)
    rec = {'task': t['name'], 'project': t['project'], 'arm': arm, 'model': model, 'run': i}
    tool_files = []
    if arm == 'toolsmith':
        mine = dest / '.claude' / 'skills' / 'toolsmith'
        mine.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(skill, mine, ignore=shutil.ignore_patterns('__pycache__'))
        base_files = {l[3:].strip() for l in sh(['git', 'status', '--porcelain', '--untracked-files=all'], cwd=dest).stdout.splitlines()}
        res, _ = agent(TOOLING_PROMPT.format(task=t['prompt']), dest, model, timeouts[0], out / 'tooling.jsonl')
        shutil.rmtree(mine, ignore_errors=True)
        tool_files = [f for f in created_by(dest, base_files) if not f.startswith('.claude/skills/toolsmith')]
        rec['tooling'] = {k: res.get(k) for k in ('total_cost_usd', 'num_turns', 'seconds', 'is_error')}
        rec['tooling_files'] = tool_files
        rec['contaminated'], _ = hidden_tests(t, dest)
        sh(['git', 'diff', '--stat'], cwd=dest)
        (out / 'tooling.diff').write_text(sh(['git', 'diff'], cwd=dest).stdout)
    res, bash = agent(TASK_PREFIX + t['prompt'], dest, model, timeouts[1], out / 'task.jsonl')
    rec['task_session'] = {k: res.get(k) for k in ('total_cost_usd', 'num_turns', 'seconds', 'is_error')}
    names = {Path(f).stem for f in tool_files if Path(f).stem not in ('README', 'index', 'mod', '__init__')}
    rec['used_tooling'] = sorted({n for n in names for c in bash if re.search(r'\b' + re.escape(n) + r'\b', c)})
    rec['success'], rec['test_tail'] = hidden_tests(t, dest)
    (out / 'task.diff').write_text(sh(['git', 'diff'], cwd=dest).stdout)
    (out / 'record.json').write_text(json.dumps(rec, indent=1))
    sh(['git', '-C', str(repo_cache(t)), 'worktree', 'remove', '--force', str(dest)])
    return rec


def report(root):
    recs = [json.loads(p.read_text()) for p in sorted(Path(root).glob('**/record.json'))]
    by = {}
    for r in recs:
        by.setdefault((r['arm'], r['model']), []).append(r)
    lines = ['| Arm | Model | Runs | Solved | Contaminated (tooling already solved it) | Task session: turns / cost | Tooling: cost | Task session used the tooling |',
             '|---|---|---|---|---|---|---|---|']
    for (arm, model), rs in sorted(by.items()):
        clean = [r for r in rs if not r.get('contaminated')]
        ts = [r['task_session'] for r in rs]
        cost = lambda xs: sum((x or {}).get('total_cost_usd') or 0 for x in xs)
        lines.append(f"| {arm} | {model} | {len(rs)} | {sum(r['success'] for r in clean)}/{len(clean)} | "
                     f"{sum(bool(r.get('contaminated')) for r in rs)} | "
                     f"{sum((x.get('num_turns') or 0) for x in ts) / len(rs):.0f} / ${cost(ts) / len(rs):.2f} | "
                     + (f"${cost([r.get('tooling') for r in rs]) / len(rs):.2f}" if arm == 'toolsmith' else '—') + ' | '
                     + (f"{sum(bool(r.get('used_tooling')) for r in rs)}/{len(rs)}" if arm == 'toolsmith' else '—') + ' |')
    lines += ['', '| Task | ' + ' | '.join(f'{a} · {m}' for a, m in sorted(by)) + ' |', '|---|' + '---|' * len(by)]
    for name in sorted({r['task'] for r in recs}):
        cells = []
        for k in sorted(by):
            rs = [r for r in by[k] if r['task'] == name]
            cells.append(' '.join('C' if r.get('contaminated') else ('✓' if r['success'] else '✗') for r in rs) or '—')
        lines.append(f'| {name} | ' + ' | '.join(cells) + ' |')
    md = '\n'.join(lines) + '\n\n✓ solved · ✗ not solved · C the tooling session already solved it (not counted)\n'
    (Path(root) / 'report.md').write_text(md)
    print(md)


def main():
    ap = argparse.ArgumentParser(description='Task-based eval of the toolsmith skill.')
    ap.add_argument('command', choices=['validate', 'run', 'report'])
    ap.add_argument('dir', nargs='?', help='report: the run directory')
    ap.add_argument('--only', action='append', help='task name (repeatable)')
    ap.add_argument('--arm', action='append', choices=['bare', 'toolsmith'])
    ap.add_argument('--model', action='append')
    ap.add_argument('--runs', type=int, default=1)
    ap.add_argument('--skill', type=Path, default=SKILL)
    ap.add_argument('--out', type=Path, default=HERE.parent / 'eval-runs' / ('tasks-' + time.strftime('%Y%m%d-%H%M%S')))
    ap.add_argument('--timeout', type=int, nargs=2, default=[2400, 1800], metavar=('TOOLING', 'TASK'))
    a = ap.parse_args()
    if a.command == 'report':
        return report(a.dir or a.out)
    tasks = load(a.only)
    if a.command == 'validate':
        sys.exit(0 if validate(tasks, a.out) else 1)
    if not shutil.which('claude'):
        sys.exit('the `claude` CLI is required (and logged in)')
    for t in tasks:
        for model in a.model or ['sonnet']:
            for arm in a.arm or ['bare', 'toolsmith']:
                for i in range(1, a.runs + 1):
                    if (a.out / f"{t['name']}/{model}/{arm}/r{i}/record.json").exists():
                        continue  # resume: a finished run is kept
                    print(f"{t['name']:28} {model:7} {arm:9} r{i} …", flush=True)
                    r = run_one(t, arm, model, i, a.out, a.skill, a.timeout)
                    print(f"{'':28} {'':7} {'':9}    success {r['success']}"
                          + (f" · contaminated {r['contaminated']} · used tooling {r['used_tooling']}" if arm == 'toolsmith' else ''), flush=True)
    report(a.out)


if __name__ == '__main__':
    main()
