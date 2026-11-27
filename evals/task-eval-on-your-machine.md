# Running the task eval on your own project

The task eval measures what toolsmith is for: once the tooling exists, does an agent reach a verified
result with less effort? It needs a project where reaching a state is expensive — a login, seeded data,
a flow — and such projects usually need a local stack (a database, Docker) that a cloud container may
not have. Run it on your machine.

## 1. Pick two to four tasks from the project's history

Good tasks: a **feature** (or a bug) whose verification needs application state — a page as a logged-in
member, a report after some history, a notification after a status change — and whose commit came with
tests. Avoid one-line fixes verified by an ordinary unit test: a bare agent solves those in a minute.

## 2. Describe each task as a ticket

One file per task, `evals/tasks/<name>.json` (or in your project's `toolsmith/eval/tasks/` if it is
private — pass the directory with `--tasks`, below):

```json
{
 "name": "myapp-feat-session-reminder",
 "project": "myapp",
 "repo": "git@github.com:you/myapp.git",
 "kind": "feature",
 "state": "heavy",
 "fix": "<full sha of the commit that delivered it>",
 "hidden": ["path/to/the/test/file/it/added.test.ts"],
 "setup": "bun install --frozen-lockfile && supabase start",
 "test": "bunx vitest run path/to/the/test/file/it/added.test.ts",
 "prompt": "Feature: … what a ticket would say: the behaviour, the interface its tests use (route, function, copy, field names), no hint of where the code goes."
}
```

- `hidden` — the test files the commit added or changed; they stay out of sight until the end.
- `setup` — whatever makes a fresh worktree runnable; it runs once per worktree.
- `prompt` — name what the hidden tests check (exact copy, field names, status codes), as a ticket would.

## 3. Validate, then run

```sh
python3 evals/task_run.py validate --only myapp-feat-session-reminder
#   must print: before fix: fail · after fix: pass — valid

python3 evals/task_run.py run --arm bare --arm toolsmith-shared \
    --model sonnet --runs 2 --only myapp-feat-session-reminder --out eval-runs/myapp
python3 evals/task_run.py report eval-runs/myapp
```

The run starts with a preflight: it stops if a session would not load the worktree's CLAUDE.md (and
its `@AGENTS.md` import) — without that, the tooling is invisible and the toolsmith arm measures nothing.
Worktrees live in `~/.cache/toolsmith-evals/work`, never in your checkout.

## 4. Read it

`report.md` gives, per arm: solved, turns, time and cost of the task session, how many commands reached
or set up state, how many called the tooling, and what the tooling build cost per project. The claim to
check is the second column against the first — fewer turns and less time to a passing result, with the
tooling actually called.
