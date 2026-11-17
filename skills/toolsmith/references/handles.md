# Handles catalog

When an existing tool would do a handle's job better than project code, choose it with
[tools.md](tools.md): fit shown with evidence, alternative and cost stated, no fit no mention.

A handle is the smallest dev-only piece of tooling that turns a `human-only` / `missing` /
`friction` rung into `ok`. Prefer what the project half-has: a debug menu, a seed script, a
test helper, an admin route — extend it before adding a new mechanism.

Every handle: dev-only by construction (fails closed in release), one command, machine-readable
output, documented in the agent file.

## Reach

### Login without a password
The agent should never type a password, and many agent harnesses refuse to.
- **Dev session mint**: a dev-only route/command `dev-login --as <persona>` that creates a
  session for a seeded user and prints the cookie/token (or redirects with it set). Gate:
  route not registered unless `NODE_ENV=development` *and* a local-only flag; refuse non-loopback.
- **Token into the DB / auth emulator**: create the user + session row directly through the
  auth provider's admin API on the local stack, then hand the token to the browser.
- **Browser storage state**: log in once (script, not human), save the browser storage state
  (cookies + localStorage) to a git-ignored file, start every browser with it. Re-mint on expiry.
- **Personas**: a fixed, named set (`admin`, `member`, `stranger`, `expired-trial`) seeded the
  same way every time — so "as a stranger" is a parameter, not a setup chore.

### Direct to the state
- **Deep links / state URLs**: every interesting screen addressable by URL with its state
  (`/dev/state/checkout-with-3-items`), or an app deep link on mobile.
- **Warp / goto** (games, simulations): `warp(map, x, y)`, `start_battle(id)`, `load_state(name)`.
- **Scenario seeds**: `seed <scenario>` writes the rows a state needs, idempotently, through the
  same code path the app uses (call the operation that writes the table, don't hand-craft rows).
- **Virtual clock**: one `now()` the whole app reads, with a dev-only offset
  (`clock set +47h`). Trials, expiries, schedules and reminders become reachable.
- **Feature-flag override**: per-session flag forcing, dev-only.

### Scenario in a transaction
For behaviour that lives in the database (time windows, triggers, sweeps): one transaction that
sets the clock, inserts the fixture, runs the function, asserts on the result, and rolls back.
Reach, Act, Assert and Reset in one command, touching nothing shared.

### Lab — every declared state at its own address
The opposite of reaching into the live app: bring a piece of the app *out* and make each of its
states addressable — no backend, no session, no login. Strongest form: a region/state renderer
driven by a declaration of the region's state and backend asks, so the lab cannot invent a
state the app cannot be in (e.g. motu's lagoon: every declared state of a region at its own
URL, flows that drive it, checks that the declaration and the page still agree). Weaker forms:
component labs (Storybook, Ladle, Histoire), a scene harness for a game, a screen-per-fixture
route. The fastest Reach + Observe for UI; requirements:
- fixtures come from the app (typed against its real types), never invented to make a frame render;
- something checks the lab against the live app (an integration check, a placed-vs-rendered
  test) — a lab that drifts lies;
- each state's URL is printable by a command, so the agent can enumerate them.

### Boot-time script hook / crash replay
A flag that loads an arbitrary script at startup without editing the app (`--util=<file>`,
`-r`, `--require`, an init hook) turns any scenario into a scratch file. Crash-replay files (a
saved battle, a request dump) are free save states — find them in the survey.

### Variant launcher
One command that runs the same scenario on each variant (backend, platform, scale) side by side
in separate build trees and working dirs.

## Act / Observe at runtime

### Live console (eval / command socket)
The app opens a local socket (Unix socket `0600` in the user runtime dir; loopback TCP + token
where Unix sockets are not available) and accepts commands. Requests are queued and executed
**on the app's main loop** (between frames / on the event loop), never on the socket thread.
Each reply is framed: `{id, ok, value, stdout, error, backtrace, ms}`.
- Fits: games, REPL-driven apps (Rails, Django, Elixir, Clojure), long-running daemons.
- Generic fallback when the app cannot be changed: launch it under a pty broker that owns
  stdin/stdout and exposes the same socket (framing becomes prompt-regex/idle-timeout heuristics).
- See the `handle` CLI (separate project) for a ready implementation.
- Before building one, look for an existing console (remote eval, debugger port, REPL) and
  **audit its thread model and re-entrancy**. A console that evaluates on a side thread is
  Observe-only until it gets a "run on the main loop" mode — driving state through it crashes.
- Cheapest first step when the console reads stdin: a FIFO or pty on stdin. The socket and the
  framing are the upgrade, when prompt-counting gets flaky.

### Eyes
- **Screenshot of a named state**: the handle returns the image path *and* the state it shows
  (route, scene, frame number). A screenshot you cannot attribute is noise. Capture at the
  scale and resolution the human sees.
- Web: headless browser screenshot. Game: frame capture from the render target. Mobile:
  `adb exec-out screencap` / `simctl io screenshot`. Desktop: CDP / OS capture.

### Logs, structured
- One flag for JSON logs; one known file path per run (`.run/<id>/app.log`), not a terminal.
- A per-run (per-worktree) local observability stack when the system is distributed.
- Errors carry an identifier the agent can grep for; no swallowed exceptions in dev.

### Input injection
- Web: browser automation. Mobile: `adb shell input` / UI automation. Game: synthetic input
  events fed to the input system, or game-level commands via the console.

## Assert
- **State query**: a read-only command returning the relevant state as JSON (`state player`,
  `GET /dev/state/order/42`).
- **Named checks**: `check <thing>` with exit code 0 / non-zero and a reason — a check that
  examined nothing must say so and not exit 0.
- **Visual baselines** only when the state is pinned (seeded data, frozen clock, fixed fonts).
- **A/B differential snapshot**: the same scenario on two variants, cropped to the element's
  bounds (taken from a state query, not hard-coded), pixel diff with a threshold, exit code.
  The Assert for every "differs on X but not on Y" task.
- **Profile**: a measurement handle for performance tasks — profiler zone or in-app monotonic
  timer around the operation, cold/warm switch, repeat N, prints median and spread as JSON,
  names the device class it ran on.
- **Explain**: for tools that decide (linters, gates, rule engines), `explain <case>` prints
  which input produced the verdict.

## Launch / Reset / Cycle
- **Doctor / init script**: one command that verifies the toolchain, starts the stack, waits
  for a real readiness signal, and prints the URLs/sockets. The next agent runs it first.
- **Isolation**: ports and data dirs derived from the worktree/run id; no shared mutable state.
- **Per-run working directory**: logs, crash files, saves written by a run land in
  `.run/<id>/`, never in the human's tree; user data is copied in, never used in place.
- **Safe serve wrapper**: starts the backend with stub drivers forced (mail, payments, push) and
  local URLs, and refuses to start if a live key would be used.
- **Reset**: per-run database/schema/save directory; a reset that is *safe* to run (never the
  one the human uses) — if the project forbids a reset command, give the agent a scoped one.
- **Fast path**: incremental build target; a single-test command; hot reload where it exists.
- **Headless/offscreen** mode for anything that needs a display.

## Witness — effects

What the app *touched*, recorded per operation and compared with what it should touch. The
handle family agents miss most: the screen can be right while the code wrote the wrong table,
emailed a real person or called production.

### Effect ledger
A declaration, per operation (route, function, job), of what it may read and write, which
procedures it calls, which hosts it reaches, whether it bypasses access control — plus a
recorder that logs what it actually did, and a gate that fails on the difference (e.g. assay:
a seam records each statement's table and the *shape* of outbound payloads, never values; the
gate diffs against the declaration; the declaration diff is the review surface). Doubles as the
**safety map** for step 1b: the tables an operation writes tell you which other operations a
change affects. Know its limits and say them: a ledger checks categories of effect, not values.

### Cheaper witnesses, by channel
- **Database**: statement logging on the local DB (`log_statement`, query logs), per-run
  schemas, an audit trigger on the tables the task touches.
- **Outbound HTTP**: a recording proxy or mock server (mitmproxy, WireMock, Mock Service
  Worker, Prism) with a "what was called" query; deny-by-default egress in dev.
- **Mail / SMS / push**: a catcher with an API (Mailpit, MailHog, a preview table) — never a
  stub that falls back to the live provider when unset.
- **Files**: per-run working directory plus a before/after listing; a file watcher for the run.
- **Messages / jobs**: the queue's own inspection command; a dead-letter view.
- **Traces**: OpenTelemetry to a local collector, one trace per agent action.

## Third parties
- Stub or record/replay (payments, email, push, OAuth providers). Expose the stub's inbox
  ("last email sent to X") as a state query — that is how a magic link becomes reachable.
