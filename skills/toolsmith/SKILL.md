---
name: toolsmith
description: Before fixing or building anything in a project, measure how well YOU (the agent) can reach the running app — build, launch, observe it and its effects, get to the right state, act, assert, reset — then grill the human only on what probing could not answer, rank the gaps, and build the missing handles (dev login, eval console, warp, seed, state lab, effect ledger, screenshot, virtual clock, profiler…) before the feature work. Use at the start of work on an unfamiliar project, when asked to "audit the agent setup", "what's stopping you from seeing it", "improve the dev ecosystem for agents", or when a fix loop stalls (two attempts without a way to verify, "I can't reproduce", "I can't see the screen", "I need you to log in"). Also a planner MAP mode, with no task: list every boundary of the app (UI, process, runtime, internal seams, state stores, egress, ingress, time, identity, platform, delivery, telemetry, configuration) and the inspection points on each, showing where tooling could apply — use when asked to "map the app's boundaries", "where could tooling help", "plan the agent tooling", or `/toolsmith map`.
---

# toolsmith

In Brooks's surgical team, the toolsmith builds the instruments the surgeon operates with.
Before you operate on this app, be its toolsmith: your app has a UI for humans — find out
whether it has one for **you** (the agent-computer interface, ACI), and build the missing
pieces before anyone asks you to fix or ship something through it.

These are tools for **the app**, not for the model: ways to reach it, see it, and watch what it
touches — not new function-calling tools for yourself.

The premise, measured repeatedly (SWE-agent, OpenAI's harness engineering, Anthropic's
long-running harnesses): **the interface moves results more than the effort spent inside it.**
An agent that cannot see the screen, reach the page behind login, or reset the data spends its
budget guessing. One hour spent on a handle pays back on every later task.

## Two modes

- **Map** (planner, no task, read-only) — chart every boundary of the app and the inspection
  points on each: what an agent could **see, steer, stub, freeze or check** there, and what exists
  today. Output: a map with a diagram and unranked candidate handles, so the human sees *where*
  tooling can apply before choosing any. Procedure: [references/map.md](references/map.md).
  Use it on `/toolsmith map`, on "where could tooling help", or before the first full run on a
  large project.
- **Full** (a task, or an audit) — the process below. If a map exists, read it first: step 1
  becomes "re-map only the classes whose evidence changed", and the probes target points of the
  map. If none exists, the survey produces the parts of it the task needs.

## The loop — both modes end the same way

**Plan → present → answer every remark → revise → accept → implement.** A map (or a reach report)
is a plan, not the deliverable. Render it into a review page the human can mark up
(`scripts/review_page.py map.md`), hand it over, and **wait**. When feedback comes back, answer
every remark individually — what the card concretely is, why it was proposed, what you now
recommend, what changes — revise the map and present it again until no remark is open. Build
only after an explicit go, in the accepted order, proving each handle by running its usage
example for real. Full procedure: [references/review.md](references/review.md).

## The rule

**Ask what the ecosystem lacks before doing what the task asks.** Produce a reach report first.
Then:
- if some rung is `human-only` or `blocked`, or reaching the task's state costs more than about
  a minute: stop, and let the human pick which gaps to close before the task;
- otherwise: write the report, propose the handles, and start the task without waiting.

If the human says "skip, just do the task", record the gaps and do the task — the report is
still the deliverable that outlives this session.

**The deliverable is tooling, not a security audit.** Safety matters here only where it touches
the agent's loop: what the agent's own probes or handles could trigger (a live mail key on a
local serve, a production default target, a prod-copy database), and the fence every proposed
handle needs. Security bugs in the app itself are noted in one line in passing, never the
headline — on a well-tooled project, a page of security findings buries the tooling.

**If the agent file refuses agent work** (an `AGENTS.md` / `CLAUDE.md` that forbids AI-written
code or tooling), stop at the map: write it outside the repo, mark in-repo handles `blocked
(policy: <file>)`, and make "may an agent build anything here, and where?" grill question 1.

## What a handle is — and is not

A **handle is something the agent calls**: a command, a URL, a socket, a launch flag, a query, a
console verb — and it answers with something the agent can read. The test is the usage example:
you can write `$ <what the agent types>` and the lines it prints back, with the agent as the
caller. `bin/dev-login --as stranger` is a handle. `bin/rails runner scripts/agent/state.rb --tenant acme` is a
handle. `curl -s localhost:3000/api/dev/state?order=42 | jq .status` is a handle. `game --seed 42 --scene battle`
is a handle.
`nc 127.0.0.1 7778` into a live console is a handle.

These are **not handles**, however useful:
- hardening and hygiene — untrack a file, default a flag to off, bind to loopback, rotate a key;
- guards *as a change to make* — add a lint rule, a CI step, a type check, a pre-commit hook.
  (A guard that already exists and that the agent can run and read back — `rake lint`,
  `bun run typecheck` — passes the usage test: list it under tools in place, usually Launch &
  loop.)
- documentation, refactors, renames.

Where they go instead:
- needed to make a handle safe → that handle's **Fence** line ("gate the existing `/dev/login_as`
  on development + loopback" is the fence of the `dev-login` handle, not a candidate of its own);
- needed before an agent can safely run anything at all → **Fences to set first** (≤ 5);
- needed to make a handle *possible* (replace four `randomize()` calls so `--seed` works) → that
  handle's **Needs** line;
- none of these → not the skill's output. Mention it in passing or leave it out.

`fence` is a property of a handle, never a verb: the verbs are see, steer, stub, freeze, check.

### One generic primitive, then scripts

Do not turn every need into its own command. Once the app has — or you propose — **one generic
way to run the app's own code on demand**, most handles are **scripts run through it**, kept in
the repo and named.

**Where the state lives decides the primitive:**
- **State outside the process** — in a database, a cache, a queue; the app runs as N workers or
  serverless functions (most web stacks): the primitive is a **script runner** over the app's own
  code and the local stack — `rails runner`, `go run ./cmd/agent`, `bun scripts/agent/x.ts`,
  `python manage.py shell -c` — wrapped in one entry point. An eval socket would reach one
  arbitrary worker and miss the state anyway.
- **State in memory** — a game loop, a desktop app, a long-lived daemon with in-memory caches or
  websocket hubs: the primitive is a **live eval** into the running process (a socket console).

```sh
$ app-dev run clock +47h              # scripts/agent/clock.ts — moves the dev clock, prints it
$ app-dev run state order 42          # scripts/agent/state.ts — {"status":"paid","items":3}
$ app-dev run sweep reminders --now   # scripts/agent/sweep.ts — runs the job synchronously
$ app-eval run warp battle 12         # a game's live eval: scripts/agent/warp.rb
```

One primitive to build and fence, then a growing folder of scripts anyone can read and add to —
not a dozen bespoke flags (`--replay`, `--seed`, `--clock`) each with its own code path. A
proposed handle that is just "run this snippet in the app" is a **script card** under the
primitive, not a new handle.

**Choose the primitive before anything else, at the lowest layer that can host it** — for a
script runner, that is usually the app itself (its framework's runner); for a live eval, lowest
among the layers that are **present in every variant you target** (a socket in a runtime the app
only sometimes runs on is not a base) and **where running code is safe** (the right thread, the
interpreter lock held, the graphics context current — if the per-frame hook runs without them,
drain the requests at the layer's own safe point instead). Hosting does
not require owning the loop: a library or engine whose host calls one of its functions every
frame or every request (`update`, `tick`, `render`, a middleware) can drain a request queue there,
and then **every** host gets the primitive for free. Prefer that over one primitive per consumer.
Upper layers contribute scripts and their own gate, not a second socket.

**A capability is not a handle.** When a script needs something the primitive cannot do alone —
injecting input into a private event queue, reading a GPU buffer, resetting an internal cache —
that is an API to add underneath, written as the script's **Needs:** line (`press` — Needs: an
input-injection API in the engine, bound for scripts). It becomes a card of its own only if the
agent calls it directly, outside the primitive.

A **dedicated** handle is justified only where the generic primitive cannot reach:
- the app's loop is frozen or crashed (level-2 eyes, a watchdog, a core dump);
- before the primitive exists in the process (boot flags, launch, a per-run directory);
- out-of-band by nature (an effect ledger, a mail catcher, a GPU capture);
- it must not run inside the app (a profiler sampling it from outside);
- it runs the app's code *outside* the live app, in a lab (a component lab, a scenario harness, a
  headless scene runner);
- it must cross the **real auth boundary** to be faithful — driving the app as a persona through
  HTTP, sessions and access policies, not as a superuser script that bypasses them;
- it runs **in the browser**, which a server-side primitive cannot reach (client state, storage,
  service workers, what was rendered).

### Handles belong to the layer they live in

An engine's, a runtime's or a library's handles must work for **any** consumer and carry the
engine's name (`litergss-shot`, not `psdk-shot`). A handle specific to one consumer — its scenes,
its saves, its scripts — belongs in **that consumer's** map, even when you found it while mapping
the engine. When mapping a library, the consumer is where you probe; it is not what you equip.

## Seven places a handle lives

Every handle — existing or proposed — sits in one of seven categories. They are what the human
sees first: one picture of the app with its handles around it, solid where they exist, dashed
where they are missing.

| Category | What it gives the agent | Typical handles |
|---|---|---|
| **Launch & loop** | start it, know it is ready, isolate it, reset it, turn the loop fast | run/up scripts with readiness, per-run dirs and ports, `doctor`, reset, hot reload |
| **Ingress** — drive it | push input in, as someone | routes and API calls, CLI commands, input injection, deep links, dev login and personas |
| **Runtime** — inside the live process | look and act inside the running app | remote eval, remote debug, profiler |
| **State** — data and time | put the app in a state, read it back | seeds and scenarios, queries and dumps, snapshots, save states, virtual clock, RNG seed |
| **Egress** — what leaves | replace or record the outside world | mail catcher, HTTP stub or recorder, effect ledger, queue inspection |
| **Eyes & logs** | see what happened | screenshots of a named state, logs, traces, crash reports |
| **Lab** — the environment around the runtime | a place where the app, or a piece of it, runs outside the human's setup | a virtual display (Xvfb), a container or VM image, an emulator or simulator, a local stack (compose), a harness hosting a piece of the app outside the live process (component lab, state renderer such as motu's lagoon, scene or battle harness), the environment registry (`envs up <name>`) |

**One card per handle, one main category, optional secondary ones.** Some handles are two sides
of the same coin — a live eval is runtime *and* ingress; a remote debugger is runtime and part of
the launch. Give such a handle one card, its main category first and the others in parentheses
(`runtime (+ ingress)`), and merge cards that turn out to be the same handle seen from two
categories (a "scenario" card that is really `run` with a scene argument is one card).

The Lab is drawn *around* the other six: it is what contains the runtime. It is also where the
*bring out* way happens — running a piece of the app in a lab rather than reaching into the live one.
Look for it explicitly; it is the category agents forget, because its pieces sit outside the
code (a Dockerfile, an AVD, a display server) or look like tests.

Identity lives in Ingress (who is driving); time and randomness live in State (they make a state
reachable). The boundary classes of map mode are how you *find* handles; the six categories are
how you *show* them.

**Eyes are not optional.** For anything with a screen, a screenshot of a named state is often
the only way to verify — and the source depends on the shape: a headless browser (Playwright),
the game's own framebuffer readback (`glReadPixels`, the engine's snapshot call, a viewport
texture), the emulator (`adb exec-out screencap`, `simctl io screenshot`), the desktop app's
debugging protocol (CDP). A screenshot handle returns the image *and* the state it shows.

## Parallel agents

Several agents — or an agent and its human — will work on the project at once, each in its own
worktree. That is not a category: it is a question the whole map answers and a property every
handle has.

**The map answers: how many agents can safely work at once today, and what do they collide on?**
List every **shared resource** — a database, a port, a display, a build output path, a working
folder, a cache, a queue, a cron schedule, an external test account, a device — with who shares
it, what collides, and how it is isolated today. The hidden ones are **global rows inside a shared
store** (a settings row, a virtual-clock row, a sequence, a schedule): namespacing the rest does
not fix them.

**Three isolation levels** — propose the cheapest that removes the collisions:
1. **Shared infrastructure, namespaced data** — one database, N app servers; every write carries
   the environment (schema, tenant, key prefix). Cheap; fails on global rows.
2. **Per-environment processes on shared infrastructure** — a database per environment inside
   one server, a port range per environment, a display per environment.
3. **Fully separate** — a container or VM per environment. Costly; nothing leaks.

**The environment registry** is the Lab handle that makes it usable: named environments
(`envs list`, `envs up <name>`, `envs down <name>`), and **every other handle takes `--env`**,
defaulting to the worktree's own — so a run never lands on the human's environment by accident.

Every card carries a **Parallel:** line — how it isolates (`--env`, a run id, a port derived from
the worktree), or "single-agent only" and why.

**The process registry** sits next to it: everything a run starts (servers, emulators, displays,
watchers, port forwards) is recorded under its run id, so `envs ps` shows what is alive and
`envs stop <run>` ends it through the app's own clean exit (its quit command; SIGTERM for servers
and workers that handle it) — never a signal that trips a crash
handler, never a process or a temp folder left behind.

**Leases, when sharing cannot be avoided.** One physical device, one GPU, one vendor sandbox
account cannot be duplicated per environment. Give each a lease (`envs claim device --ttl 10m`,
renewed while in use, released on stop) so agents queue instead of colliding — and say in the map
which resources need one.

## Roadmap — compile, order, prioritise

Cards are a list; a team builds a roadmap. After proposing cards, run one more pass over them:

1. **Compile.** For each card, write what it builds on. A base used by two or more cards is a
   **foundation** — built once, listed first. A card that turns out to be "a foundation plus a
   snippet" becomes a script under it. This is the pass that catches a missing primitive: when
   four cards each need "a way to run code in the live app", that is one foundation, not four
   handles.
2. **Order.** Draw the dependencies: foundations → handles → scripts; a fence before the handle
   that needs it.
3. **Rank.** Mark each foundation and handle by what it unlocks — categories it fills, human-only
   steps it removes, how often the project's typical tasks need it — against its cost. The ones
   that unlock the most are **keystones**.
4. **Cut into milestones.** **M1 is the walking skeleton**: the smallest set that gives an agent an
   unattended loop — launch, reach a state, see it, check it. Each milestone ends on a **demo the
   agent can run end to end** once it is built. Later milestones add reach and depth. Cards in no
   milestone are listed as deferred, with why.

The human accepts milestones, not a pick list: "go for M1" is a complete instruction.

## Rules as guards

Agent files are full of rules in prose — "NEVER run `db reset`", "do not push to main", "always
use the service layer". Prose is a request; an agent under pressure can miss it. Where the
harness allows it, turn each rule into something **enforced**:

- a **pre-tool hook** or command wrapper that blocks the forbidden call and says why;
- a **permission list** for the harness: the read-only and fenced handles allowed without a
  prompt (so the agent never stalls on approval for `state` or `shot`), destructive commands
  gated or denied;
- a **lint rule or CI check** for rules about code (the project's own linter usually has a way).

In map mode, list the prose rules found in agent files with the guard each could become (map
section "Rules → guards"). Every card carries a **Permission:** line — allow · ask · deny — so
the accepted plan comes with the harness configuration that lets an agent use it unattended.
The guards are not handles (the agent does not call them); they are how the fences hold.

## Three ways up

A rung can be climbed three ways. Know all three before proposing anything — the best handle is
often not the one the shape suggests.

- **Reach in — the live app.** Handles into the running app: a dev login, an eval console, a
  warp command, a deep link. Full fidelity; each state costs steps to reach.
- **Bring out — into a lab.** Run a piece of the app in isolation, in a lab, so that every state it can be
  in is *declared* and has its own address — no backend, no session, no login (a region/state
  renderer such as motu's lagoon; component labs; a scene harness for a game; a transaction
  scenario for SQL). Every state is one URL away; but the lab only shows what was declared, so
  pair it with a check that the lab and the live app still agree.
- **Witness — the effects.** Record what the app does *outward* — database statements, outbound
  HTTP, emails, files, messages — and compare it to what was declared (an effect ledger such as
  assay; a mail catcher; an HTTP recording proxy; statement logging). Most agents verify what the
  screen shows and never what the code *touched*; effects are where the dangerous bugs are, and
  the declaration doubles as the safety map.

Rule of thumb: composition and many-state UI → **lab**; runtime, timing, integration, "only on
device X" → **live**; anything that writes, sends or calls → **witness**, whichever of the other
two you use.

Classify a handle by **where the agent stands**: inside the running app (reach in), in a replica
of the app or of its surroundings (bring out — a mock server returning canned answers is a
replica of the outside world), or at the edges watching what leaves (witness). A tool may climb
several ways; list each.

### …and two properties

Every handle, whichever way up, is also judged on:

- **Loop** — is it fast, **parallel-safe**, resettable? Parallel-safe has a test: *two agents can
  run it at the same time without seeing each other's effects.* Access you cannot repeat cheaply
  or run twice at once is access for one attempt. (Ladder rungs 7 and 8; see "Parallel agents".)
- **Fence** — is it dev-only by construction, does it fail closed? A handle that can reach
  production, or a stub that falls back to the live service, removes safety instead of adding
  access.

| | Reach in | Bring out | Witness |
|---|---|---|---|
| **Access** — see · steer · stub · freeze · check | console, warp, dev login | lab, scenario, mock | ledger, catcher, traces |
| **Loop** — fast · parallel-safe · resettable | hot reload, per-run working dir | renders with no backend | per-run trace, diffable log |
| **Fence** — dev-only, fails closed | no eval in release | fixtures from the app, never real data | stub never falls back to live |

Any handle in any app gets a coordinate: **category × verb × way** — *where* it lives (one of the
six places above), *what* it lets the agent do (see, steer, stub, freeze, check), *how* the agent
stands (reach in, bring out, witness) — with loop and fence as its quality bar. The boundary
classes of map mode are how you find it. That is the vocabulary of the map, the report and the
proposals.

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
and its trade-off, the adoption cost, and disclosure of the skill author's own tools. Say which way up each one is (live · lab · witness), and why that one. A
handle must be:

1. **Dev-only by construction** — absent from release builds, refuses non-loopback, fails closed;
   a stub never falls back to the live service. A login bypass that can ship is a vulnerability.
2. **Scriptable** — one command, shown with a usage example (the command and what it prints), machine-readable output, exit codes (0 holds, non-zero says
   why), no prompts, no TTY.
3. **Sized for an agent** — the agent reads every byte it prints. Summary first; `--json` with
   only the fields that matter; `--tail N` / `--grep` / `--since` on anything log-like; pages, not
   dumps; a diff rather than the whole state; a path to the big artifact (screenshot, trace,
   dump) rather than its bytes. A default output over a few hundred lines is a bug.
4. **Fast and deterministic** — seeded, time-controllable, parallel-safe (see "Parallel agents").
5. **Discoverable** — documented where the next agent looks first ("How to reach the app"
   in the agent file), with the exact command.
6. **Honest** — a handle that looked at nothing does not report success.
7. **Alive** — its usage example runs in the `doctor` script and in CI, so it fails loudly the day
   the app changes under it. A handle nobody runs rots silently (a `--test` flag that parses to
   nothing, a seed script whose table was renamed) and the next agent finds out mid-task.
8. **Permissioned** — the agent's harness knows what it may run without asking: read-only and
   fenced handles pre-approved, destructive ones gated or denied (see "Rules as guards").

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

## Anti-patterns

- A rung marked `ok` from reading code, or from a probe of a different variant.
- Fixed sleeps, or a log line, as readiness.
- Asking the human to log in for you every session.
- A handle in feature code, or one that works in production.
- A screenshot without the state it shows, or at a scale the human never sees.
- Verifying what the screen shows and never what the code wrote, sent or called.
- A lab nobody checks against the live app: it drifts, and then it lies.
- Scraping coloured, human-formatted output when one flag would give JSON.
- Restarting a service you did not start. Writing into the human's tree without listing it.
- Twenty questions at once. Questions the README answers.
- Building before the human has reviewed the plan, or leaving a remark unanswered.
- Two layers each proposing their own primitive (an eval socket in the engine *and* in the game).
- Fixing the task while "probing".
