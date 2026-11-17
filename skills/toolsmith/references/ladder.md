# The reach ladder — probing a running app (task scope, full audits)

## Contents
- The reach ladder
- Process
- When NOT to run the full process

## The reach ladder

| # | Rung | The question |
|---|------|--------------|
| 1 | **Build** | Can I build / typecheck / lint, how long, and can my build tree exist without writing into the human's? |
| 2 | **Launch** | Can I start it myself, headless, isolated (ports, data dir, working dir)? How do I know the *state I need* is ready? Is there a lab where it need not launch at all? |
| 3a | **Observe** | Can I read its logs, errors, and — if it has a screen — **see** it, at the scale the human sees? Structured or scraped? |
| 3b | **Effects** | Can I see what it *touched* — rows read and written, HTTP calls, mails, files, messages — per operation, and compare with what it should touch? |
| 4 | **Reach** | Can I get to the exact state the task is about — behind login, on map 42, on day 3 of a trial, first-time/cold? |
| 5 | **Act** | Can I drive input there — click, call, command, enqueue, key press — safely (on the right thread)? |
| 6 | **Assert** | Can I check the outcome programmatically — pass/fail, a comparison between variants, or a measurement? |
| 7 | **Reset** | Can I go back to a known state, and run two of me in parallel without collisions? |
| 8 | **Cycle** | Edit → observe: how many seconds, *including how the edit reaches the running app* (rebuild, publish, hot-patch)? |

Every rung gets a **status**, a **cost** (wall seconds, steps, or "needs a human") and
**evidence** (the command run and what it printed — never "should work").

Statuses:
- `ok` — works, cheaply.
- `friction` — works, but slow, flaky, scraped, or racy.
- `human-only` — needs a person: a GUI click, a password, a physical device, a credential.
- `blocked (policy: <source>)` — possible, but a rule forbids it: the brief, the agent file, the
  project's guard. Name the source; the strictest layer wins.
- `attached` — a service that was already running and is not yours: probe it read-only, never restart it.
- `missing` — no way exists.
- `unknown` — not run. A rung you did not run is never `ok`.
- `n/a` — say why.

## Process

### 0. Trace the task

If a task triggered this, map it to code before anything else: which feature produces the
behaviour, **which repo or artifact owns that code**, and **how a change there reaches the
running app**. A task that maps to zero or two features ("the reminder email" — the email or
the in-app notice?) is grill question 1. A task naming a variant ("on raylib but not SFML",
"on Android", "at 2× scale") fixes the variants every rung is probed for.

### 1. Survey — answer from the repos first

Read before asking, and read **every place a run touches**: the repo you edit, the consumer that
runs it, the process's working directory, the user-data folders. For a library or engine, the
safety boundary usually lives in the consumer.

- Agent files (`CLAUDE.md`, `AGENTS.md`, …) — and **run** the commands they prescribe for this
  task; an agent file is a claim, and drift is a finding.
- Manifests and scripts (`package.json`, `Makefile`, `Rakefile`, `justfile`, `CMakePresets.json`,
  `docker-compose*`, Gradle), `.env*` files, schedulers (cron, pg_cron, job queues).
- CI tells you what is **gated**, not what exists: test files or checks CI never runs are a finding.
- Existing handles, which keyword lists miss. Grep for env flags (`getenv`, `ENV[`,
  `process.env`), ports and tokens in the README, `debug`, `console`, `eval`, `repl`, `seed`,
  `fixture`, `mock`, `stub`, `preview`, `profiler`, `--headless`, `hidden`, `storybook`,
  `scenario`, `lagoon`, `audit`, `ledger`, `trace`, `otel`, `mailpit`, `record`; run the app's own
  `help`; look for crash-replay files and boot-time script hooks; look for **paid or
  non-deterministic dependencies** (LLM SDKs, payment, SMS, paid APIs) and for **references** the
  output could be compared against (a previous version, a parity target, golden files). If the repo *is* developer or
  agent tooling, its own commands are your candidate handles.
- Audit each existing handle against the five criteria of step 5 — a dev clock gated only by an
  env flag, a mail stub that falls back to live sending, an eval console on a side thread are
  findings, not handles.

Locate the task's **points on the map** (or, with no map, the boundaries the task crosses —
[references/map.md](references/map.md) lists the boundary classes and how to find their points).

Classify the **shape(s)** — usually two or three ([references/shapes.md](references/shapes.md)).
A tool whose input is another project has **two loops** (the tool on fixtures; the tool against
its real consumer): climb the ladder for both.

### 1b. Verify the safety boundary — then ask once

Scope: what the agent's own probing and handles could trigger. This is a precondition for the
ladder, not an audit of the app.


Do not infer the boundary; check it with read-only probes:
- which env file would a launch load, and does it hold **live** third-party keys or production
  URLs? Does each stub fall back to the real service when unset?
- is the local database a production copy (real users, no seed users)? Are schedulers live in it?
- what user data does a run read or write (saves, profiles, uploads)?

Classify every probe you plan: **read-only** · **rolled-back** (transaction, throwaway clone) ·
**local write** · **inject** (code into a live process) · **external** (network, mail, device).
Then ask **one batched permission question** for the classes beyond read-only, before probing.

### 2. Probe — climb the ladder for real

Before the first probe: record `git status` of every repo involved and checksums of user data —
for a database, row counts or a schema dump of the tables in play, or run the probes against a
disposable database or branch.
After the last: compare, and list every file a run wrote. Point build caches and outputs at
scratch, and check that the build system really honours that (presets with fixed output paths
don't).

- Use the project's own entry points (its script, preset, make target).
- Build handles **on** the project's own build and task system — a CMake target, a rake or npm
  task, a make rule, a Gradle task — not as standalone scripts that re-implement how the project
  builds or launches: two ways to build drift apart, and the handle is the one that rots.
- Readiness is **the state you need being queryable** (`$scene.class == X`, a health URL
  returning the tenant), not a log line and never a fixed sleep.
- **Reach** the task's own state — and for a bug, report separately *state reachable* and *bug
  reproduced*. A bug that does not reproduce goes back to the human before anything else.
  Include cold / first-time states when the task says "first time".
- For interactive apps, Reach needs Act: probe them together.
- A probe that injects code into a live process is **Act**, not Observe: budget a Reset for each,
  first check the console's thread model (a console on a side thread is Observe-only until
  proven safe), and **stop after one crash**.
- Probe each rung once per variant the task names. A rung is `ok` only if ok for all of them.
- Stop apps through their own quit path — SIGTERM for servers and workers that handle it, the
  app's quit command otherwise; never a kill that trips a crash handler (crash handlers can
  write files). Clean up processes, port forwards, and temp dirs — yours and the app's.

### 3. Grill — only what probing could not answer

Interview the human **one question at a time**, each with your recommended answer and what you
already found. Never ask what the repo or a probe can answer. Stop when every rung has a status
and every `human-only` / `blocked` rung has an owner and a decision.
Question bank: [references/grill.md](references/grill.md).

### 4. Rank the gaps

    value = (how often tasks need it) × (time or human interruptions it costs each time)
    rank  = value ÷ (cost to build the handle)

A `human-only` rung on a frequent path beats any `friction`: an agent that must stop and ask
loses the whole loop, not seconds. Write the report from
[references/report-template.md](references/report-template.md).

### 5. Propose handles, review them with the human, build only the accepted plan

Propose as cards, then run the review loop ([references/review.md](references/review.md)):
present the page, answer every remark, revise, and build only after an explicit go.


From [references/handles.md](references/handles.md) — or, better, by finishing a handle the
project half-has. When an existing tool would do better, pick it by **fit, with evidence** —
[references/tools.md](references/tools.md): prerequisites visible on the map, the alternative
and its trade-off, the adoption cost, and disclosure of the skill author's own tools. Say which way each one is (live · lab · witness), and why that one. A
handle must be:

The eight criteria every handle meets are in [principles.md](principles.md), "What makes a good handle".

Keep each handle small and out of feature code.

### 6. Prove the rung moved, then persist

Re-run the probes each handle touched and show **before → after**. Then leave for the next
session: a `doctor` / `init` script that runs the fast checks and brings the app up
ready-to-reach; the "How to reach the app" section; the report. Only now start the task.

## When NOT to run the full process

- Trivial local change: rungs 1, 6, 8 only, in under a minute.
- A CLI or library whose unit suite runs in seconds: Build, Reach-by-fixture, Assert, Cycle —
  plus the consumer loop only if the report came from the consumer. Grill only on what is blocked.
- A reach section and doctor script already exist: run them, re-probe only what they skip.
- You are a subagent with a narrow brief: report the blocking rung to your caller.
