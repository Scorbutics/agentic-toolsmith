# The evidence grid — levels × ways, grades, loop and fence

## Contents
- The grid
- Four levels
- Three ways
- Grading a cell
- The declared boundary — the strong form of a cell
- Two properties — loop and fence
- Seven categories — the diagram's grouping only

The grid answers the question the rest of the map serves: **at each level of this app, what can
an agent prove, and by which way?** Most agents fill one cell — the whole app, reached live — and
call the rest covered because unit tests and an e2e suite exist. The grid makes each cell answer
for itself.

## The grid

|  | Bring out — a lab | Witness — the effects | Reach in — the live app |
|---|---|---|---|
| **unit** | unit tests, SQL transaction tests | what a unit wrote, asserted in its test | — usually `n/a` |
| **piece** | a component or region lab, a scene harness, a model on a local engine | the calls a piece makes, recorded and compared | a screenshot of the piece in the running app |
| **operation** | one operation driven alone, on a local stack | what one operation wrote, called and bypassed | call it on the running app, as a persona |
| **journey** | e2e on a local stack with the outside world replaced | what a whole session touched: mail, jobs, rows, hosts | launch, log in as a persona, reach the state, see it |

Every cell gets a **verdict** in the map, as every boundary class does — an empty cell is a defect
of the map, not of the app:

- `gated:` · `asserted:` · `observed:` — filled, by what (the command), at that grade (below);
- `gap:` — nothing here, and what a task loses for it;
- `n/a:` — why this cell cannot exist or never matters here.

**The unit and piece rows of the bring-out column are filled by harnesses**, not by tests:
"`asserted:` by `go test`" is the verdict only where the suite *can reach* the code that changes —
a handler that calls the real database directly, with no fake behind it, is a `gap:` at piece level
however large the suite (handles.md, "Harnesses").

**Then decide each cell**, after its verdict, as `→ propose`, `→ leave` or `→ either`, with why:

| Decision | Means | Ask |
|---|---|---|
| `→ propose` | a map that left this cell empty would miss something real here | "Would a reviewer mark this map wrong for proposing nothing here?" |
| `→ leave` | a card here would be wasted or wrong — the cell cannot exist, is covered well enough, or would not repay its cost | "Would a reviewer push back on a card here?" |
| `→ either` | the evidence points neither way — say which evidence, both sides | "Can I name what argues for a card here, and what argues against?" |

**`→ either` is not the safe default.** Maps hedge: where an owner says a cell matters, a map most
often answers `either`, not `leave`. So `either` needs its reason on both sides ("one fix in the mix
lands here, but the piece harness already reaches it"). When a task in this project would fail
silently, or need a human, at this cell — and nothing else on the map covers it — the decision is
`→ propose`. "No card needed" without that reason is not a decision.

Decide from this project's evidence, never the shape's habit: the task mix (map.md, step 0b), what
a task in the agent files keeps doing by hand, the rules agents trip on, what the verdict says a task
loses. A `gap:` is not automatically `→ propose` — "gap — no task in the mix lands here → either" is
honest — and `asserted:` is not automatically `→ leave`: a suite that cannot reach the code that
changes is a gap with a fine-looking verdict.

The decisions bind the rest of the map:
- every `→ propose` cell gets a card (or a deferred one, with why); a capability is a group of them;
- no card lands in a `→ leave` cell;
- **a missing seam is always decided**: a `gap:` in the unit or piece row of the bring-out column
  whose cause is a seam the code lacks — a handler that builds its own database client, a phase that
  constructs its own payment client, a scene that only runs inside the full game — is `→ propose` with
  a harness card (handles.md, "Harnesses"), or `→ leave` with the reason it does not pay here.

No way is worth more than another: a map whose `propose` cells all fall in lab and witness is as
lopsided as one whose cards all fall in journey × reach in. The grid is there so that each cell is
*decided*, not so that each is filled.

Each card names its cell: `<way> at <level>` in its heading (map-template.md).

## Four levels

The level is **how much of the app is present** when the agent gets its verdict:

- **unit** — code alone: a function, a query, a macro, a shader. Present today as the unit suite.
- **piece** — one part the human sees or a downstream reads, with its own state: a component, a
  screen region, a scene or a battle, a dbt model, a CLI subcommand. Between the unit suite and the
  e2e suite; **the level agents miss**, because the cells on both sides look filled.
- **operation** — one entry into the backend or the core: a request, a server action, an RPC, a
  job, a webhook, a command — whatever writes or sends on behalf of a caller.
- **journey** — the whole app, as someone, across operations: a user session, a playthrough, a
  pipeline run end to end.

What each level is called in each shape: shapes.md, "Levels by shape". Use the shape's words in
the map; keep the four rows.

## Three ways

Know all three before proposing anything — the best handle is often not the one the shape suggests.
Classify a handle by **where the agent stands**:

- **Bring out — a lab.** Run a piece of the app *outside* the live app so that every state it can be
  in is declared and has its own address — no backend, no session, no login: a component or region
  lab, a scene harness, a transaction scenario, a model on a local engine, a mock server standing in
  for the outside world. Every state is one command away; but a lab shows only what was declared, so
  **pair every lab with a tie to the live app** — a check that the lab and the page still agree, a
  contract test for a mock. A lab nobody ties back drifts, and then it lies.
- **Witness — the effects.** Record what the app did *outward* — database statements, procedures
  called, access control bypassed, outbound HTTP, mail, files, messages, jobs — and compare it with
  what it should have done. Most agents verify what the screen shows and never what the code
  touched; effects are where the dangerous bugs are, and a declaration of them doubles as the safety
  map and the blast radius. Witness is not "egress": a row written is an effect that never leaves.
- **Reach in — the live app.** Handles into the running app: a dev login, a script runner, an eval
  console, a warp, a deep link. Full fidelity; each state costs steps to reach.

Rule of thumb: many-state composition → bring out; runtime, timing, integration, "only on device
X" → reach in; anything that writes, sends or calls → witness, *in addition to* whichever of the
other two you use. A tool may sit in several cells; list each.

## Grading a cell

The grade is **whether the evidence can fail against something written down**:

| Grade | Means | Example |
|---|---|---|
| `observed` | the agent can observe; nothing says what it should be | logs, a screenshot, a trace, statement logging |
| `asserted` | an assertion that fails | a test, a `--expect` on a script, a row-count oracle |
| `gated` | a written declaration the run is diffed against; the declaration's diff is what a human reviews | an effect ledger and its gate; a lab whose states and calls come from a region declaration checked against the placed page; an OpenAPI contract test |

`observed` → `asserted` → `gated` is a ladder of cost as well as value. Declare only the boundaries
agents cross often and where a wrong result is silent (a write nobody sees, a state nobody reaches by
hand). Most cells are fine at `asserted`.

For a **bring-out** cell, the grade includes its tie to the live app: a lab with no tie is at most
`observed`, however many assertions run inside it.

**The grade is what the tooling can do, not how you know it.** A test suite you only read is
`asserted` all the same; mark how you know with `(seen)` or `(docs)`, as everywhere in the map. A
command written in a README is not `gated` — `gated` needs a declaration the run is diffed against,
and a gate that fails. A cell whose only tool needs credentials or a service the agent does not
have is a `gap:` that says so.

## The declared boundary — the strong form of a cell

The same shape recurs at every level, whatever the stack:

1. **Declare** the boundary: the states a piece can be in and the calls it makes; the tables, procedures
   and hosts an operation may touch; who may see what.
2. **Run every declared state in isolation** — the lab's job, each state at an address.
3. **Witness** what actually happened during the run.
4. **Gate** on the difference: an undeclared state, write, call or host fails.
5. **Review the declaration's diff**, not the code's: it says what changed in consequence.
6. **Tie it back** to the live app, so the declaration cannot drift from it.

Propose it as a pattern the project can implement — a few hundred lines over its own seams, or an
existing tool when one fits (tools.md: fit with evidence, alternative, cost, disclosure). When
it does *not* fit: few states, a boundary agents rarely cross, a stack where the run cannot be
recorded cheaply. Then `asserted` is the right grade, and saying so is part of the verdict.

## Two properties — loop and fence

Every handle, in any cell, is also judged on:

- **Loop** — fast, **parallel-safe**, resettable. Parallel-safe has a test: *two agents can run it
  at the same time without seeing each other's effects.* **Environments live here**: a per-run
  environment, a container image, a local stack, a virtual display (Xvfb), an emulator — they make
  a cell repeatable and parallel; they are not a way and not a lab. A card that only isolates or
  launches is judged by the cells it makes loopable. **An environment is never a capability of
  its own**: it is the foundation of the milestone whose demo needs it — "replay a webhook and see
  what it wrote" with `envs up` underneath, not "start an isolated stack" as a milestone.
  (Ladder rungs 7 and 8; parallel.md.)
- **Fence** — dev-only by construction, fails closed. A handle that can reach production, or a stub
  that falls back to the live service, removes safety instead of adding access.

| | Reach in | Bring out | Witness |
|---|---|---|---|
| **Loop** | hot reload, per-run working dir, `envs up` | renders with no backend | per-run trace, diffable log |
| **Fence** | no eval in release | fixtures from the app, never real data | a stub never falls back to live |

Any handle gets a coordinate — **cell (level × way) · point · verb** — with loop and fence as its
quality bar. The boundary classes of map mode (map.md) are how you *find* points; the verbs (see,
steer, stub, freeze, check) are what the agent does there; the grid is how you *judge* coverage.

## Seven categories — the diagram's grouping only

The review page draws the app with its handles grouped by where they attach. Cards carry one
category for that drawing; it does not decide anything else.

| Category | Holds |
|---|---|
| **launch** — launch & loop | run/up with readiness, `doctor`, reset, hot reload, **environments** (per-run, container, compose, Xvfb, emulator, `envs up`) |
| **ingress** — drive it | routes and API calls, CLI commands, input injection, deep links, dev login and personas |
| **runtime** — inside the live process | remote eval, remote debug, profiler |
| **state** — data and time | seeds and scenarios, queries and dumps, snapshots, save states, virtual clock, RNG seed |
| **egress** — what leaves | mail catcher, HTTP stub or recorder, queue inspection |
| **eyes** — eyes & logs | screenshots of a named state, logs, traces, crash reports |
| **lab** — the app brought out | a piece of the app run outside it: component or region labs, scene and battle harnesses, transaction scenarios, a model on a local engine |

One main category per card, others in parentheses (`runtime (+ ingress)`). An effect ledger is drawn
under state or egress, whichever it mostly records; its *way* is witness either way.

**Eyes are not optional.** For anything with a screen, a screenshot of a named state is often
the only way to verify — a headless browser, the engine's framebuffer readback, the emulator, the
desktop app's debugging protocol — at the scale the human sees. A screenshot handle returns the
image *and* the state it shows.
