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
# Worktrees live under the home directory: `claude -p` does not load a project's CLAUDE.md under /tmp, and
# a session that never reads the agent file cannot use the tooling it describes (measured: 2026-11-27).
WORK = CACHE / 'work'

TASK_PREFIX = ("You are working in this repository. Fix the bug below. Verify your fix the way you see fit before "
               "you finish; do not ask questions — nobody will answer.\n\n")
TOOLING_PROMPT = ("Use the toolsmith skill in task scope: /toolsmith task \"{task}\"\n\n"
                  "Nobody is available to answer: write your questions with your recommended answers and take them as "
                  "answered. Treat the first milestone (M1) of your roadmap as accepted by the human: build its handles "
                  "now, prove each one by running its usage example, and document them where the next agent looks "
                  "first (the agent file's \"How to reach the app\" section). Build durable tooling only — do NOT fix "
                  "the bug: another agent will do the task with what you build.")


PROJECT_TOOLING_PROMPT = ("Use the toolsmith skill in map scope: /toolsmith map\n\n"
    "Agents will next implement features and fix bugs in this project, one task at a time. Nobody is available to "
    "answer: write your questions with your recommended answers and take them as answered. Treat the first milestone "
    "(M1) of your roadmap as accepted by the human: build its handles now, prove each one by running its usage "
    "example, and document them where the next agent looks first (the agent file's \"How to reach the app\" section). "
    "Build durable tooling only; do not change the application's behaviour.")
# commands that reach or set up application state, rather than read or edit code
REACH = re.compile(r'manage\.py (shell|runserver|createsuperuser|loaddata|migrate|dumpdata|sendreports|sendalerts)|'
                   r'curl\b[^|]*(localhost|127\.0\.0\.1)|\bpsql\b|\bsqlite3\b|django\.setup\(|DJANGO_SETTINGS_MODULE|'
                   r'objects\.create|\bmkdir -p .*fixture|\btouch\b|\bln -s')


def sh(cmd, cwd=None, timeout=1800, env=None):
    return subprocess.run(cmd, cwd=cwd, shell=isinstance(cmd, str), text=True, capture_output=True,
                          timeout=timeout, env=env)


TASK_DIRS = [HERE / 'tasks']  # --tasks adds more (a private project keeps its tasks in its own repository)


def load(name=None):
    tasks = [json.loads(p.read_text()) for d in TASK_DIRS for p in sorted(Path(d).glob('*.json'))]
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
        reqs = ''.join(sh(['git', '-C', str(repo_cache(task)), 'show', f"{task['fix']}:{f}"]).stdout
                       for f in ('requirements.txt', 'requirements-dev.txt'))
        import hashlib  # one venv per set of requirements: the tasks span commits with different pins
        venv = CACHE / 'venvs' / ('healthchecks-' + hashlib.sha1(reqs.encode()).hexdigest()[:10])
        if not (venv / 'bin' / 'python').exists():
            sh([sys.executable, '-m', 'venv', str(venv)])
            for f in ('requirements.txt', 'requirements-dev.txt'):  # the tests need the dev requirements too
                req = sh(['git', '-C', str(repo_cache(task)), 'show', f"{task['fix']}:{f}"]).stdout
                # mysqlclient needs MySQL build headers; the eval runs on SQLite and PostgreSQL only
                (venv / f).write_text('\n'.join(l for l in req.replace('-r requirements.txt', '').splitlines()
                                                 if not l.lower().startswith('mysqlclient')))
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
    r = sh(['git', '-C', str(src), 'worktree', 'add', '--quiet', '--detach', str(dest), task.get('base') or f"{task['fix']}^"])
    if r.returncode:
        sys.exit(r.stderr)
    s = sh(task['setup'], cwd=dest, env=env_for(task), timeout=3600)
    return s.stdout + s.stderr


def ablate(task, dest):
    """Bare arm of a task whose project already HAS agent tooling: remove it, and commit the removal so the
    session sees a clean tree (no 'deleted: tools/...' in git status). restore() puts it back for the judge."""
    ab = task.get('ablate') or {}
    subs = list((ab.get('submodules') or {}).items())
    # submodules first, then the project WITH their new pointers: else `git status` shows ' M <submodule>'
    for repo, paths in subs + [('.', ab.get('paths', []))]:
        d = dest / repo
        for p in paths:
            sh(['git', 'rm', '-r', '-q', '--ignore-unmatch', '--', p], cwd=d)
        for f, text in ((ab.get('agent_files') or {}).get(repo) or {}).items():
            (d / f).write_text(text)
            sh(['git', 'add', '--', f], cwd=d)
        if repo == '.':
            sh(['git', 'add', '--', *[r for r, _ in subs]], cwd=d)
        sh(['git', '-c', 'user.name=eval', '-c', 'user.email=eval@localhost', 'commit', '-q', '-m', 'wip'], cwd=d)
    left = sh(['git', 'status', '--porcelain'], cwd=dest).stdout.strip()
    assert not left, f'ablation left the tree dirty: {left}'


def restore(task, dest):
    """Put the removed tooling back (from the commit before the removal), for the judge only."""
    ab = task.get('ablate') or {}
    for repo, paths in [('.', ab.get('paths', []))] + list((ab.get('submodules') or {}).items()):
        d = dest / repo
        for p in paths + list(((ab.get('agent_files') or {}).get(repo) or {})):
            sh(['git', 'checkout', 'HEAD~1', '--', p], cwd=d)  # the commit before the removal
        sh(['git', 'reset', '-q'], cwd=d)


def hidden_tests(task, dest):
    """Run the fix commit's tests against the worktree as it stands, then put the files back as they were.
    A task with no hidden test files is judged by its `test` command alone (e.g. a replay in the live game)."""
    if not task.get('hidden'):
        r = sh(task['test'], cwd=dest, env=env_for(task), timeout=3600)
        return r.returncode == 0, (r.stdout + r.stderr)[-1500:]
    sub = task.get('fix_in')  # the fix (and its tests) live in a submodule: {"repo": path, "commit": sha}
    repo, commit = (dest / sub['repo'], sub['commit']) if sub else (dest, task['fix'])
    saved = {f: (repo / f).read_bytes() if (repo / f).exists() else None for f in task['hidden']}
    try:
        sh(['git', 'checkout', commit, '--', *task['hidden']], cwd=repo)
        r = sh(task['test'], cwd=dest, env=env_for(task), timeout=1800)
        return r.returncode == 0, (r.stdout + r.stderr)[-1500:]
    finally:
        for f, b in saved.items():
            if b is None:
                (repo / f).unlink(missing_ok=True)
            else:
                (repo / f).write_bytes(b)
        # `git checkout <fix> -- files` also staged the hidden tests: unstage them, or the next session
        # would find them in `git status` / `git diff --cached`
        sh(['git', 'reset', '-q', '--', *task['hidden']], cwd=repo)
        staged = set(sh(['git', 'diff', '--cached', '--name-only'], cwd=repo).stdout.split())
        assert not staged & set(task['hidden']), f'hidden tests left staged: {staged & set(task["hidden"])}'


def preflight(model):
    """Fail before any session if a worktree's CLAUDE.md would not reach the agent."""
    d = WORK / 'preflight'
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True)
    sh(['git', 'init', '-q'], cwd=d)
    (d / 'CLAUDE.md').write_text('@AGENTS.md\n')  # the import the skill writes
    (d / 'AGENTS.md').write_text('The project codeword is HERON-17.\n')
    r = sh(['claude', '-p', "Without using any tool: what is this project's codeword? Reply with it or 'unknown'.",
            '--model', model, '--output-format', 'json'], cwd=d, timeout=300)
    shutil.rmtree(d, ignore_errors=True)
    if 'HERON-17' not in r.stdout:
        sys.exit(f'preflight: a session in {WORK} does not see CLAUDE.md (and its @AGENTS.md import); not running')


def validate(tasks, root):
    ok = True
    for t in tasks:
        dest = root / 'validate' / t['name']
        worktree(t, dest)
        before, out_b = hidden_tests(t, dest)
        sub = t.get('fix_in')
        repo, commit = (dest / sub['repo'], sub['commit']) if sub else (dest, t['fix'])
        changed = [f for f in sh(['git', 'show', '--name-only', '--format=', commit], cwd=repo).stdout.split()
                   if f and f not in t['hidden']]
        sh(['git', 'checkout', commit, '--', *changed], cwd=repo)
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


def project_tooling(project, model, i, root, skill, timeout):
    """Build the project's tooling once — map scope, M1 built and proven — at the OLDEST task's starting commit,
    so it can never see a later fix. Saved as a patch that run_one applies to each task's worktree."""
    out = root / 'tooling' / project / model / f'r{i}'
    patch = out / 'tooling.patch'
    if patch.exists():
        return json.loads((out / 'record.json').read_text()), patch
    tasks = [t for t in load() if t['project'] == project]
    src = repo_cache(tasks[0])
    when = lambda t: int(sh(['git', '-C', str(src), 'log', '-1', '--format=%ct', t.get('base') or f"{t['fix']}^"]).stdout.strip() or 0)
    t0 = min(tasks, key=when)
    out.mkdir(parents=True, exist_ok=True)
    dest = WORK / f'tooling-{project}-{model}-r{i}'
    worktree(t0, dest)
    mine = dest / '.claude' / 'skills' / 'toolsmith'
    mine.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(skill, mine, ignore=shutil.ignore_patterns('__pycache__'))
    res, _ = agent(PROJECT_TOOLING_PROMPT, dest, model, timeout, out / 'tooling.jsonl')
    shutil.rmtree(mine, ignore_errors=True)
    sh(['git', 'add', '-A', '--', '.', ':!.venv', ':!target', ':!*.sqlite', ':!.claude/skills/toolsmith'], cwd=dest)
    patch.write_text(sh(['git', 'diff', '--cached', '--binary', 'HEAD'], cwd=dest).stdout)
    rec = {'project': project, 'model': model, 'run': i, 'built_at': t0.get('base') or f"{t0['fix']}^",
           'files': sh(['git', 'diff', '--cached', '--name-only', 'HEAD'], cwd=dest).stdout.split(),
           **{k: res.get(k) for k in ('total_cost_usd', 'num_turns', 'seconds', 'is_error')}}
    (out / 'record.json').write_text(json.dumps(rec, indent=1))
    sh(['git', '-C', str(src), 'worktree', 'remove', '--force', str(dest)])
    return rec, patch


def run_one(t, arm, model, i, root, skill, timeouts):
    tag = f"{t['name']}/{model}/{arm}/r{i}"
    out = root / tag
    out.mkdir(parents=True, exist_ok=True)
    dest = WORK / tag.replace('/', '-')
    worktree(t, dest)
    rec = {'task': t['name'], 'project': t['project'], 'arm': arm, 'model': model, 'run': i}
    tool_files = []
    if arm == 'toolsmith-shared':
        trec, patch = project_tooling(t['project'], model, i, root, skill, timeouts[0])
        ap = sh(['git', 'apply', '--3way', '--whitespace=nowarn', str(patch)], cwd=dest) if patch.read_text().strip() else None
        rec['tooling'] = {'shared': True, 'total_cost_usd': trec.get('total_cost_usd'), 'num_turns': trec.get('num_turns')}
        rec['tooling_applied'] = bool(ap is None or ap.returncode == 0)
        if ap is not None and ap.returncode:
            rec['tooling_apply_error'] = ap.stderr[-800:]
        sh(['git', 'reset', '-q'], cwd=dest)  # applied changes as plain edits, nothing staged for the task session
        tool_files = trec.get('files', [])
        rec['tooling_files'] = tool_files
        rec['contaminated'], _ = hidden_tests(t, dest)
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
        (out / 'tooling.diff').write_text(sh(['git', 'diff', 'HEAD'], cwd=dest).stdout)
    if arm == 'bare' and t.get('ablate'):
        ablate(t, dest)
    res, bash = agent(TASK_PREFIX + t['prompt'], dest, model, timeouts[1], out / 'task.jsonl')
    if arm == 'bare' and t.get('ablate'):
        restore(t, dest)
    rec['task_session'] = {k: res.get(k) for k in ('total_cost_usd', 'num_turns', 'seconds', 'is_error')}
    names = {Path(f).stem for f in tool_files if Path(f).stem not in ('README', 'index', 'mod', '__init__')}
    rec['used_tooling'] = sorted({n for n in names for c in bash if re.search(r'\b' + re.escape(n) + r'\b', c)})
    rec['commands'] = len(bash)
    rec['reach_commands'] = sum(bool(REACH.search(c)) for c in bash)
    rec['tooling_commands'] = sum(any(re.search(r'\b' + re.escape(n) + r'\b', c) for n in names) for c in bash)
    rec['success'], rec['test_tail'] = hidden_tests(t, dest)
    (out / 'task.diff').write_text(sh(['git', 'diff', 'HEAD'], cwd=dest).stdout)
    (out / 'record.json').write_text(json.dumps(rec, indent=1))
    sh(['git', '-C', str(repo_cache(t)), 'worktree', 'remove', '--force', str(dest)])
    return rec


def handles(files):
    """The commands the tooling created — executables under bin/, scripts/ or tools/ — not every file it touched
    (matching any file name counted `settings` from .claude/settings.json as tooling use)."""
    out = set()
    for f in files:
        parts = Path(f).parts
        if parts and parts[0] in ('bin', 'scripts', 'tools') and Path(f).name not in ('__init__.py', 'README.md'):
            out.add(parts[1] if parts[0] == 'tools' and len(parts) > 2 else Path(f).stem)
    return out


def tooling_use(rec, log):
    """Bash commands in the task session that invoked one of the tooling's commands."""
    names = handles(rec.get('tooling_files') or [])
    if not names or not log.exists():
        return 0, []
    used, n = set(), 0
    for line in log.read_text().splitlines():
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        for c in (ev.get('message') or {}).get('content') or [] if ev.get('type') == 'assistant' else []:
            if isinstance(c, dict) and c.get('type') == 'tool_use' and c.get('name') == 'Bash':
                cmd = c.get('input', {}).get('command', '')
                hit = {x for x in names if re.search(r'(^|[\s/;&|(])' + re.escape(x) + r'(\.py|\.sh)?\b', cmd)}
                n += bool(hit); used |= hit
    return n, sorted(used)


def report(root):
    recs = []
    for p in sorted(Path(root).glob('**/record.json')):
        r = json.loads(p.read_text())
        if 'task' not in r:  # a project tooling build
            continue
        if r['arm'].startswith('toolsmith'):
            r['tooling_commands'], r['used_tooling'] = tooling_use(r, p.with_name('task.jsonl'))
        recs.append(r)
    by = {}
    for r in recs:
        by.setdefault((r['arm'], r['model']), []).append(r)
    lines = ['| Arm | Model | Runs | Solved | Contaminated | Task session: turns · time · cost | Commands (reaching state · via tooling) | Tooling cost | Used the tooling |',
             '|---|---|---|---|---|---|---|---|---|']
    for (arm, model), rs in sorted(by.items()):
        clean = [r for r in rs if not r.get('contaminated')]
        ts = [r['task_session'] for r in rs]
        cost = lambda xs: sum((x or {}).get('total_cost_usd') or 0 for x in xs)
        avg = lambda f: sum(f(r) or 0 for r in rs) / len(rs)
        tooled = arm.startswith('toolsmith')
        shared = {(r['project'], r['run']): (r.get('tooling') or {}).get('total_cost_usd') or 0 for r in rs} if arm == 'toolsmith-shared' else {}
        tcost = (f"${sum(shared.values()):.2f} for {len(shared)} project build(s)" if shared
                 else f"${cost([r.get('tooling') for r in rs]) / len(rs):.2f}/task" if tooled else '—')
        lines.append(f"| {arm} | {model} | {len(rs)} | {sum(r['success'] for r in clean)}/{len(clean)} | "
                     f"{sum(bool(r.get('contaminated')) for r in rs)} | "
                     f"{avg(lambda r: r['task_session'].get('num_turns')):.0f} · {avg(lambda r: r['task_session'].get('seconds')):.0f}s · "
                     f"${cost(ts) / len(rs):.2f} | {avg(lambda r: r.get('commands')):.0f} ({avg(lambda r: r.get('reach_commands')):.1f} · "
                     f"{avg(lambda r: r.get('tooling_commands')):.1f}) | {tcost} | "
                     + (f"{sum(bool(r.get('used_tooling')) for r in rs)}/{len(rs)}" if tooled else '—') + ' |')
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
    ap.add_argument('--tasks', action='append', type=Path, default=[], metavar='DIR',
                    help='another directory of task files, e.g. a private project\'s toolsmith/eval/tasks (repeatable)')
    ap.add_argument('--arm', action='append', choices=['bare', 'toolsmith', 'toolsmith-shared', 'tooled'])
    ap.add_argument('--model', action='append')
    ap.add_argument('--runs', type=int, default=1)
    ap.add_argument('--skill', type=Path, default=SKILL)
    ap.add_argument('--out', type=Path, default=HERE.parent / 'eval-runs' / ('tasks-' + time.strftime('%Y%m%d-%H%M%S')))
    ap.add_argument('--timeout', type=int, nargs=2, default=[2400, 1800], metavar=('TOOLING', 'TASK'))
    a = ap.parse_args()
    TASK_DIRS.extend(a.tasks)
    if a.command == 'report':
        return report(a.dir or a.out)
    tasks = load(a.only)
    if not tasks:
        sys.exit(f'no task matched (looked in {", ".join(map(str, TASK_DIRS))}) — nothing checked, nothing run')
    if a.command == 'validate':
        sys.exit(0 if validate(tasks, a.out) else 1)
    if not shutil.which('claude'):
        sys.exit('the `claude` CLI is required (and logged in)')
    preflight((a.model or ['sonnet'])[0])
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
