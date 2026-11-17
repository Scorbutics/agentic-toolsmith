# Map mode — the boundaries of the app and where tooling can apply

## Contents
- The boundary classes
- The five verbs
- Procedure
- Grill the map
- Keeping it alive

A planner pass, independent of any task: **every place the app meets something else**, and at
each one, **what an agent could do there** — see, steer, stub, freeze — and what exists today.
The human sees the whole territory before choosing where tooling goes; the ladder later probes
points of this map instead of rediscovering them.

Read-only by construction: reading code, configs, docs, read-only commands (`--help`, listing,
`git log`), and **SELECT-only queries against a local stack that is already running** — never
ask the human what one read-only query answers. No launches, nothing that writes. The ladder is
where things run.

Env files are evidence by **class, never by value**: `KEY → local | remote | live | test | unset`
(read the prefix or host, print nothing else). The same for secrets found anywhere else (config
files, committed credentials): name the file and the class, never the value.

**Read, docs, seen.** In map mode most cells come from reading code. Mark a cell `(seen)` only
when a read-only command showed it, and `(docs)` when it comes from the tool's or engine's own
documentation rather than this repo (a Godot CLI flag, a `debug` gem env var); everything else is
read. Version checks are not always read-only: `pnpm`/`yarn` through corepack, asdf/mise shims and
some wrappers download on first call — prefer reading the version pin in the repo. A missing
toolchain (no `node_modules`, wrong language version, no engine binary) is a finding for the
Launch and Build rungs, not a reason to stop: map from the code and say what could not be
confirmed.

**Check every citation before you write it.** Open the file at the line you cite and confirm it
says what you claim; a line number from memory is a guess. (One map found about thirty of its
first citations wrong this way.)

**Evidence is a full path** — repo-relative when the map covers one repo, **absolute** when it
spans several (an engine and its game, an app and its runtime), so every reference opens as is:
`scripts/4 Systems/106 Save Load/3 GamePlay/400 Save.rb:7`, never `Save.rb:7`. A bare file name
is ambiguous in any repo with repeated names, and the next agent cannot open it. No abbreviations either (`L/…` for a repo root): write the path out.

**Agent files' rules.** Collect every rule written in prose in the agent files (`CLAUDE.md`,
`AGENTS.md`, …) — "never", "always", "do not" — for the "Rules → guards" section.

**Shared resources.** While locating points, note every resource two agents would share
(database, ports, display, build outputs, working folders, caches, queues, schedules, external
test accounts, devices) and every **global row inside a shared store**. They fill the map's
"Parallel agents" section.

**Size.** Aim for 25–45 points. Past that, aggregate alike crossings; a map nobody finishes
reading has no effect.

## The boundary classes

Walk all of them. A class with no point is still listed — "none found (looked at: …)" is a
finding; a silent omission is not. A point may belong to two classes (a cron job is time,
ingress and egress; an RPC layer is both an internal seam and ingress): list it once under its
primary class and cross-reference it from the others.

| # | Boundary | Where the app meets… | Typical inspection points |
|---|---|---|---|
| B1 | **Human UI** | the screen and the input devices | render target / DOM, input system, accessibility tree, window scale, routes/scenes |
| B2 | **Process** | the OS that launches it | args, env vars, stdin/stdout/stderr, signals, exit code, working dir, ports |
| B3 | **Runtime** | its own execution | main/event loop or frame hook, eval/REPL, debugger port, profiler, hot reload, boot-script hook |
| B4 | **Internal seams** | itself, module to module | component/region boundaries, service interfaces, plugin APIs, FFI/bindings, backend abstraction layers |
| B5 | **State stores** | what it remembers | database, cache, files, saves, browser storage, cookies/sessions |
| B6 | **Egress** | services it calls | HTTP APIs, mail, push, payments, storage buckets, webhooks out |
| B7 | **Ingress** | what calls it | routes, RPC, webhooks in, sockets, queues/topics consumed, CLI commands |
| B8 | **Time & chance** | the clock and randomness | `now()` reads, timers, schedulers/cron, timezones, RNG seeds, frame timing |
| B9 | **Identity** | who the caller is | login flows, sessions/tokens, roles/personas, access-control policies |
| B10 | **Platform** | hardware and OS services | GPU/display, device APIs, file pickers/dialogs, sensors, emulators/simulators |
| B11 | **Delivery** | how code reaches the runtime | build outputs, packaging, publish/submodule/vendoring, deploy, release gates |
| B12 | **Telemetry** | what it already reports | logs, metrics, traces, crash reports/dumps, error screens |
| B13 | **Configuration** | the switches that select behaviour | env-selected drivers (mail: live/preview), feature flags, role-dependent gates, build flags, "dev mode" checks |

## The five verbs

At each point, ask what an agent could do there:

- **See** — read what crosses it (observe, record, screenshot, log).
- **Steer** — push something across it (inject input, call, eval, deep link, seed).
- **Stub** — replace the other side (mock server, mail catcher, fake device, recorded replay).
- **Freeze** — make it deterministic (virtual clock, seed, fixed timestep, pinned data).
- **Check** — compare what crossed with what was *declared*, including what must be **denied**
  (an effect ledger's gate, a lab-vs-page integration check, "a stranger gets nothing" for
  access policies). Seeing is not checking: a check can fail.

Per point, also note the two properties every handle is judged on (categories.md):
**loop** — can it be reset, isolated per run/worktree, repeated fast? — and **fence** — is it
dev-only, does it fail closed?

Every handle in [handles.md](handles.md) is one or more verbs at one point. A point where no verb
is possible for an agent is a `human-only` point; say who holds it.

## Procedure

-1. **Read the decisions.** Before anything, read `toolsmith/decisions.md` in the project and in
   its parent folder (reading those is part of the job, even when told to stay in the project), and the latest map of any related repo (a lower or upper layer) if there is
   one. Do not re-open what is decided there; cite it.
0. **Choose the primitive.** Before any card, decide where the state lives. Outside the process
   (database, cache, queue — most web stacks): the primitive is a script runner over the app's own
   code (`rails runner`, `go run ./cmd/agent`, a `scripts/agent/` entry point). In memory (a game,
   a desktop app, a daemon): a live eval, at the lowest layer with a per-frame or per-request hook
   every host goes through (it may be a library function the host calls, not a loop the layer owns). That is where the generic primitive goes (principles.md). Everything after is written against it: scripts under it, the
   capabilities those scripts need as Needs lines, dedicated cards only with an exemption.
1. **Locate.** For each class, find the points in the code — grep for the crossing itself
   (`fetch(`, `http.`, `smtp`, `Date.now`, `new Date`, `getenv`, `STDIN`, `Thread.new`,
   `rand`, `cron`, `listen(`, route registrations, FFI declarations…), plus configs and agent
   files. Every point carries **evidence**: `file:line`, the config key, or — for a family of
   alike crossings — the command that counts them (`67 route handlers: find app -name route.ts`).
   Aggregate alike crossings into one point; split only where the verbs differ. No evidence, no
   point — put it under "unknown" instead.
2. **Inventory what exists.** For each point and verb: an existing handle (name it, and score it
   on the five criteria of principles.md, "What makes a good handle"), a human-only path, possible-but-missing, or
   impossible. Note the way: reach in · bring out · witness. A **tool** often climbs several
   ways — list it as `tool → verb → way` rows (an effect ledger that also replays calls and
   clones the database is witness + bring out + loop), never one label per tool.
3. **Mark the fences.** Flag the points an agent's probes or handles could trigger with real
   consequences: live keys or production URLs a local launch would use, a production default
   target, a prod-copy database, user data a run would write, scripts that contradict the agent
   file. They become **"Fences to set first"** — at most five one-liners, placed *after* the
   candidate handles, because they are preconditions for using them. Security bugs in the app
   itself (a debug route that ships, a listener on all interfaces) are not the map's job: list
   them in one "Noticed in passing" line at the end, or leave them out — **unless the point is, or
   should become, a handle**: an always-on debug port is a half-built remote-debug handle, and its
   exposure goes in that card's Fence line, not in passing.
4. **Grill the map** — see below.
5. **Write it** with [map-template.md](map-template.md), including the diagram, then render the
   review page (`scripts/review_page.py`) and start the review loop ([review.md](review.md)).
6. **Propose, don't build.** List candidate handles *on the map* — project code or an existing
   tool chosen by fit ([tools.md](tools.md)). Every candidate is something the agent *calls* (principles.md) and shows **how it would be used**: the
   exact command (or call, or URL) and a few lines of what it prints. A handle you cannot write a
   usage example for is not designed yet. For a runtime-shaped app, the candidates include remote
   debug and remote eval into the live process (handles.md, "Runtime-shaped apps"). Each card
   names its **category** (launch · ingress · runtime · state · egress · eyes · lab — categories.md), its point, verb, way and rough cost.
7. **Compile the roadmap** (roadmap.md): foundations shared by several cards, the
   dependency order, keystones, and milestones — M1 the walking skeleton — each ending on a demo
   the agent can run. Re-read the cards after compiling: a card that is a foundation plus a
   snippet becomes a script, and a capability several cards need becomes a foundation. Every card
   must appear, by its exact name in backticks, in one milestone's **Builds:** line or in
   **Deferred** — the review page places cards by that name.

## Grill the map

Same rules as [grill.md](grill.md): one question at a time, a recommended answer, never what the
code answers. **In map mode, at most three questions, and only those whose answer changes which
handle gets built** (or where it lives). Questions about safety, priorities or ownership wait for
task mode, where a human is there to answer them. The map changes the questions — you now ask about **crossings**, showing what you
found:

- "I found these egress points: [list with evidence]. Is anything missing — a call made from
  elsewhere (a cron box, a vendor SDK, a database function)?"
- "Which of these crossings must an agent never trigger, even locally?"
- "These points have no agent verb at all: [list]. Which of them do your tasks hit most?"
- "This internal seam [X] looks like where a lab could cut the app: true?"
- "I could not tell whether [point] is live in dev or stubbed. Which?"

Stop when every class has points or a "none found", and every unknown has an answer or an owner.

## Keeping it alive

Write the map where the next agent looks (`docs/agent-map.md`, linked from the agent file),
stamped with the commit it was made at. A full run reads the map first and only re-maps the
classes whose evidence lines changed since (`git diff <stamp> -- <evidence files>`).
