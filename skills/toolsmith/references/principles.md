# Principles — what a handle is, the primitive, layers, criteria

## Contents
- The rule
- What a handle is — and is not
- What makes a good handle
- Anti-patterns

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
- individual tests — the test for one bug or one feature is the coding agent's work on that task;
- documentation, refactors, renames.

**A harness is a handle.** What makes a unit or a piece *testable* — and that an agent then calls,
task after task — is durable tooling, not a test: a fake or in-memory store behind the port a
handler already takes, a runner that executes one phase, job or Postgres function with its
surroundings faked, a headless runner for one scene, a model built on a local engine, a command that
runs the tests of one piece in seconds (`bun run test:piece process-payment`). Most bugs are cheapest
to catch at the unit and piece levels (grid.md); an agent that cannot reach those levels without
writing the scaffolding first will not reach them at all. Propose the harness — the tests written
with it come with each task. **An existing suite that nothing runs** (no script, no CI) is a harness
half-built: its card wires it into `doctor` and CI — the Alive criterion below.

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
- **State in the browser** — a single-page app whose backend is not in the repo: the primitive is
  a **browser runner** (Playwright driving the app, with scripts) plus a local mock of the API it
  calls.

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
- it runs the app's code *outside* the live app, in a lab or a harness (a component lab, a fake store, a scenario harness, a
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

## Data the human owns

A local copy of production data is common and legitimate. Whether an agent may read or change it is
the owner's call — ask once, record it where the handle reads it (a config file cited in
`toolsmith/decisions.md`), show it in every output header ("production copy"), and keep the fences
on what leaves the machine: mail, notifications, production URLs, payments, schedulers. Refusing the
data by default protects nothing the owner asked for; firing a side effect at real users does harm.

## What makes a good handle

A handle must be:

1. **Dev-only by construction** — absent from release builds, refuses non-loopback, fails closed;
   a stub never falls back to the live service. A login bypass that can ship is a vulnerability.
2. **Scriptable** — one command, shown with a usage example (the command and what it prints), machine-readable output, exit codes (0 holds, non-zero says
   why), no prompts, no TTY.
3. **Sized for an agent** — the agent reads every byte it prints. Summary first; `--json` with
   only the fields that matter; `--tail N` / `--grep` / `--since` on anything log-like; pages, not
   dumps; a diff rather than the whole state; a path to the big artifact (screenshot, trace,
   dump) rather than its bytes. A default output over a few hundred lines is a bug. State the agent
   needs to read comes back as **text**, never only drawn on a screen: a value visible only in an
   overlay or a debug window has to be photographed and read back by a person.
4. **Fast and deterministic** — seeded, time-controllable, parallel-safe (see parallel.md).
5. **Discoverable** — documented where the next agent looks first ("How to reach the app"
   in the agent file), with the exact command — in the text the harness loads at startup (CLAUDE.md,
   or AGENTS.md imported from it with `@AGENTS.md`), not behind a pointer the agent must follow. A
   handle built but not written there is never called.
6. **Honest** — a handle that looked at nothing does not report success.
7. **Alive** — its usage example runs in the `doctor` script and in CI, so it fails loudly the day
   the app changes under it. A handle nobody runs rots silently (a `--test` flag that parses to
   nothing, a seed script whose table was renamed) and the next agent finds out mid-task.
8. **Permissioned** — the agent's harness knows what it may run without asking: read-only and
   fenced handles pre-approved, destructive ones gated or denied (see guards.md).

Keep each handle small and out of feature code.

## Anti-patterns

- A rung marked `ok` from reading code, or from a probe of a different variant.
- Fixed sleeps, or a log line, as readiness.
- Asking the human to log in for you every session.
- A handle in feature code, or one that works in production.
- A screenshot without the state it shows, or at a scale the human never sees.
- Verifying what the screen shows and never what the code wrote, sent or called.
- A lab nobody checks against the live app: it drifts, and then it lies.
- Counting the unit suite and the e2e suite as "the lab" and proposing nothing between them — the
  piece level (grid.md) is where screens, scenes and models live.
- Capabilities that all sit in one cell of the grid — usually journey × reach in — without saying
  why the others do not matter here: the shape's habit, not this project.
- Scraping coloured, human-formatted output when one flag would give JSON.
- Restarting a service you did not start. Writing into the human's tree without listing it.
- Twenty questions at once. Questions the README answers.
- Building before the human has reviewed the plan, or leaving a remark unanswered.
- Two layers each proposing their own primitive (an eval socket in the engine *and* in the game).
- Fixing the task while "probing".
