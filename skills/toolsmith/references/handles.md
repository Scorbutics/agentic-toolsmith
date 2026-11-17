# Handles catalog

Every entry below is something the agent **calls** and reads back. Hardening, guards and
hygiene are not handles — they are the Fence or Needs lines of the handle they serve (SKILL.md,
"What a handle is").

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

### Repro bundle — the bug report as a state
Most tasks start as "it broke when I did X". The handle that changes the most turns that into one
replayable artifact, captured where the bug happens, replayed where the agent works:
- web: the user's session recording (rrweb) or a HAR, plus the data state (a scoped DB dump);
- game: the recorded inputs, the save, the RNG seed, the build;
- backend: the request(s) plus a snapshot of the rows they touched;
- any app: version, config, flags, clock — whatever makes the replay deterministic.
`repro capture` on the human's side, `repro play <bundle>` on the agent's; the replay ends on a
state the agent can query and screenshot. Look for half-built ones: crash dumps, saved battle
states, error reports with request ids. Category: state (+ ingress).

### Variant launcher
One command that runs the same scenario on each variant (backend, platform, scale) side by side
in separate build trees and working dirs.

## Act / Observe at runtime

### Runtime-shaped apps: remote debug AND remote eval

When the app runs on a VM or an interpreter (Ruby, Python, Node, JVM, BEAM, Lua, GDScript, an
embedded VM), the agent's strongest reach-in is into the **live process**, and there are two
distinct handles — propose both, they coexist:

- **Remote debug** — pause, step, inspect, through the runtime's own protocol. Usually one flag
  away; the gap is that nobody turned it on or wrote down how to attach.
- **Remote eval** — run a line in the live process *without pausing it*, and get the result back.
  Rarely built in; this is the one to build.

| Runtime | Remote debug (built in) | Remote eval into the live process |
|---|---|---|
| Ruby / Rails | `debug` gem: `RUBY_DEBUG_OPEN=true RUBY_DEBUG_PORT=… bin/rails s`, then `rdbg --attach` (or a DAP client) | Not built in — `rails console` / `rails runner` are a *separate* process (same code and DB, not the server's memory). Build the socket console below |
| Python | `debugpy --listen 127.0.0.1:5678` (DAP) | `manhole` (socket REPL into the running process), or the socket console below |
| Node / Electron | `--inspect=127.0.0.1:9229` (CDP) | Built in: CDP `Runtime.evaluate` on the same port |
| JVM | JDWP `-agentlib:jdwp=transport=dt_socket,address=127.0.0.1:5005,server=y,suspend=n` | JShell over JDI, or an app-level console (Spring Boot: an actuator endpoint, dev profile only) |
| Erlang / Elixir | — | Built in: `iex --remsh` / `erl -remsh` |
| Go (no VM) | Delve: `dlv attach <pid>` / `dlv debug --headless --listen=127.0.0.1:2345` | None; expose a dev-only command endpoint instead |
| Godot | Built in: `--remote-debug tcp://127.0.0.1:6007` (the editor's debugger, remote scene tree) | Not built in — a dev-only console autoload evaluating `Expression`, gated by `OS.is_debug_build()` |
| Embedded VM in a host app | Whatever the VM's debugger offers (e.g. the `debug` gem's DAP for an embedded Ruby) | The socket console below, opened by the host |

**Profilers over a socket** belong next to them — the third live-process handle, and one that
must run from *outside* the app's loop:
- Tracy (a native client in the app, `tracy-capture -a 127.0.0.1 -p <port>` to record headless);
- Go pprof over HTTP (`go tool pprof http://127.0.0.1:6060/debug/pprof/profile?seconds=10`);
- CDP's `Profiler` domain for Node / Electron; JFR / async-profiler for the JVM;
- sampling profilers that attach by process id: `rbspy`, `py-spy`, `perf`.
A profiler handle prints a file the agent can read (a trace, a flamegraph's folded stacks, a
top-N table) — not only a GUI.

### Live console (eval / command socket)

Reference implementation for an embedded Ruby VM, by the skill's author: `remote_eval.rb` in
[embedded-ruby-vm](https://github.com/Scorbutics/embedded-ruby-vm) — the pattern transfers to
any runtime:
- loopback by default, and a **shared token** sent first (`S: rubyvm-eval/1 token?` → `C: <token>`);
- `nc`-friendly line protocol with a prompt; multi-line input until the parser accepts it;
- **scopes**: the app registers bindings (`expose(:scene, binding)`) and the client `attach`es to
  one, so a line runs against the object that matters, not only the top level;
- coexists with the remote debugger, each on its own port, both dev-only and opened by the host.

Add what an agent needs on top of a human's console: **framed replies** (one JSON line per
request with value / stdout / error / ms) and a **main-loop mode** for anything that touches
state — see below.
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
- Sources by shape:
  - **web**: headless browser — Playwright `page.screenshot()`, after the state is queryable;
  - **game / native renderer**: read the framebuffer the game draws into — the engine's
    snapshot call (`Graphics.snap_to_bitmap`, `get_viewport().get_texture().get_image()`),
    `glReadPixels` on the GL surface, a GPU readback of the render target — offscreen or hidden
    window when there is no display; capture both the native frame and the scaled one;
  - **mobile**: `adb exec-out screencap -p`, `xcrun simctl io booted screenshot`;
  - **desktop / Electron**: CDP `Page.captureScreenshot`, or the OS capture as a last resort.
- A comparison handle (A/B between variants, before/after an edit) is the usual next step once
  one screenshot is attributable.

#### Two levels of eyes for a native renderer

A game, an engine or any app with its own renderer needs **two** capture handles, because the
in-app one is blind exactly when it is needed most:

1. **In-app, named state** — the app's own snapshot call (`Graphics.snap_to_bitmap`, a viewport
   texture read). Cheap, knows which state it shows. But it is triggered by the app's own code on
   its own loop: useless when that loop is frozen, when the bug is in the code path that produces
   the image, or when the question is "what did the player actually see".
2. **Out-of-band, the presented frame** — what reached the window, captured without asking the
   app's scripting layer:
   - an engine-level hook driven from outside: an env var or signal that makes the renderer dump
     the frame it presents (after scaling, shaders, post-processing), every N frames or on demand —
     `glReadPixels` / the backend's screen read right before the buffer swap;
   - a GPU-level tool: RenderDoc (frame capture, every draw call and texture), apitrace (record
     and replay the GL stream, dump any frame), Mesa's `GALLIUM_HUD` for counters;
   - an `LD_PRELOAD` shim on the swap call (`glXSwapBuffers`, `eglSwapBuffers`) that reads the
     back buffer — works on a binary you cannot change;
   - the display server: run under Xvfb and grab the window (`xwd`, ImageMagick `import -window`);
     on Android `screencap` already reads the composited surface.

Their ways differ, and the card says so: level 1 is **reach in** (the app snapshots itself, on
request); level 2 is **witness** (the frame as it left the app, captured without its cooperation).

Propose level 2 whenever the renderer is native, there is more than one backend or scaling path,
or a freeze or crash is a plausible bug class. The two captures of the same frame, side by side,
also tell you *which layer* a visual bug is in.

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
- **Oracle — compare against a reference**: many outcomes have no absolute "correct" (is this
  pixel right? is this ranking right?), only "same as the reference". Name the reference and make
  the comparison a command: a previous release, a parity target (the old runtime a new one must
  match), a production response recorded once, golden files with an update command, a slower but
  obviously-correct implementation. `oracle diff <case>` prints what differs and exits non-zero.
  The map asks: *what is the reference here?*
- **Explain**: for tools that decide (linters, gates, rule engines), `explain <case>` prints
  which input produced the verdict.

## Launch / Reset / Cycle
- **Doctor / init script**: one command that verifies the toolchain, starts the stack, waits
  for a real readiness signal, and prints the URLs/sockets. The next agent runs it first.
- **Isolation**: ports and data dirs derived from the worktree/run id; no shared mutable state.
- **Process registry**: every process a run starts is recorded under its run id — `envs ps`,
  `envs stop <run>` through the app's clean exit; nothing left running, no crash files from signals.
- **Leases** for what cannot be duplicated (a device, a GPU, a sandbox account):
  `envs claim <resource> --ttl 10m`, renewed while used, released on stop.
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

### Paid and non-deterministic dependencies
When the app itself calls an LLM, a payment provider, an SMS gateway or any metered API, agent
runs cost money and give a different answer each time. Give each one:
- **record / replay** — recorded responses keyed by request (a cassette per scenario), live only
  when explicitly re-recording;
- **a budget cap per run** and a counter the agent can read (`envs cost <run>`);
- a **fence**: never live in agent runs unless the run says so; a missing cassette fails loudly
  rather than calling out.
For LLM calls specifically, also pin model, temperature and seed where the API allows it, and log
prompt + response per call — they are the app's least deterministic boundary.

## Third parties
- Stub or record/replay (payments, email, push, OAuth providers). Expose the stub's inbox
  ("last email sent to X") as a state query — that is how a magic link becomes reachable.
