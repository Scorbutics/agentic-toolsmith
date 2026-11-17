# Map mode — the boundaries of the app and where tooling can apply

A planner pass, independent of any task: **every place the app meets something else**, and at
each one, **what an agent could do there** — see, steer, stub, freeze — and what exists today.
The human sees the whole territory before choosing where tooling goes; the ladder later probes
points of this map instead of rediscovering them.

Read-only by construction: reading code, configs, docs, read-only commands (`--help`, listing,
`git log`), and **SELECT-only queries against a local stack that is already running** — never
ask the human what one read-only query answers. No launches, nothing that writes. The ladder is
where things run.

Env files are evidence by **class, never by value**: `KEY → local | remote | live | test | unset`
(read the prefix or host, print nothing else).

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

Per point, also note the two properties every handle is judged on (SKILL.md, "Three ways up"):
**loop** — can it be reset, isolated per run/worktree, repeated fast? — and **fence** — is it
dev-only, does it fail closed?

Every handle in [handles.md](handles.md) is one or more verbs at one point. A point where no verb
is possible for an agent is a `human-only` point; say who holds it.

## Procedure

1. **Locate.** For each class, find the points in the code — grep for the crossing itself
   (`fetch(`, `http.`, `smtp`, `Date.now`, `new Date`, `getenv`, `STDIN`, `Thread.new`,
   `rand`, `cron`, `listen(`, route registrations, FFI declarations…), plus configs and agent
   files. Every point carries **evidence**: `file:line`, the config key, or — for a family of
   alike crossings — the command that counts them (`67 route handlers: find app -name route.ts`).
   Aggregate alike crossings into one point; split only where the verbs differ. No evidence, no
   point — put it under "unknown" instead.
2. **Inventory what exists.** For each point and verb: an existing handle (name it, and score it
   on the five criteria of SKILL.md step 5), a human-only path, possible-but-missing, or
   impossible. Note the way up: reach in · bring out · witness. A **tool** often climbs several
   ways — list it as `tool → verb → way` rows (an effect ledger that also replays calls and
   clones the database is witness + bring out + loop), never one label per tool.
3. **Mark the boundary.** Points that cross the safety boundary (live keys, prod URLs, real user
   data, irreversible actions, listeners on all interfaces, dev tools that ship to production,
   scripts that contradict the agent file) are flagged — and go **first** in the map, under
   "Safety findings". They are usually the most valuable output of a map.
4. **Grill the map** — see below.
5. **Write it** with [map-template.md](map-template.md), including the diagram.
6. **Propose, don't build.** List candidate handles *on the map* (which point, which verb, which
   way up, rough cost), grouped by boundary. Ranking needs a task or the human's priorities; ask
   for them, or leave the list unranked.

## Grill the map

Same rules as [grill.md](grill.md): one question at a time, a recommended answer, never what the
code answers. The map changes the questions — you now ask about **crossings**, showing what you
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
