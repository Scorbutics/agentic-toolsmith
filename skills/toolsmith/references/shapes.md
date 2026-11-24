# Project shapes

## Contents
- Web app with accounts (SPA / SSR / monolith)
- API / backend service, workers, queues
- Game / real-time app (engine, emulator, simulation)
- Embedded runtime / scripting host (a VM or engine inside a host app)
- Mobile app (native, cross-platform, WebView shell)
- Desktop app (Electron, Qt, native GUI)
- CLI tool / library / SDK
- Developer / agent tooling whose input is another project
- Data / ML / batch pipeline
- Infrastructure / IaC / deployment
- Embedded / hardware / device firmware
- Legacy / heavyweight stack (JSP, AngularJS, app servers, mainframe-adjacent)
- Cross-cutting concerns (check on every shape)
- Levels by shape

Most projects are several shapes at once (a game is also a native library; a SaaS is a web app
+ a worker + a database). Probe each shape's rungs. The table says what each rung *usually
means* there and where it usually breaks.

## Web app with accounts (SPA / SSR / monolith)
- **Launch**: dev server + local backing services (DB, auth emulator, queue). Readiness = health URL.
- **Observe**: server logs, browser console, network, screenshot via a headless browser.
- **Reach**: the login wall is the #1 gap. Then: tenant/role, feature flags, data volume, time.
- **Act**: browser automation, or call the API the page calls.
- **Assert**: API/DB query, DOM query, visual snapshot.
- **Reset**: per-run schema or seed script; never the shared dev DB.
- **Breaks on**: agent tools refuse to type passwords; magic links/OTP/SSO; real clock (trials, expiries).
- **Primitive**: a script runner over the app's own code and the local stack (state lives in the DB).
- **Also survey**: migrations and generated types; DB snapshot/branching; session/JWT minting for
  roles; inbound webhooks; background jobs; request tracing; API contract; SSR vs client (which
  code runs where, server-only env leaking to the client); cache/CDN; feature flags; tenants.
- **Variants**: viewport (phone/desktop), browser, locale, tenant, render mode (SSR/CSR/static),
  runtime (Node vs Edge).
- **Parallel**: a port per worktree breaks OAuth redirect allowlists and cookie host scoping —
  derive hostnames (`a1.localhost`) or register the callback range; say so on the login handle.

## API / backend service, workers, queues
- **Reach**: a job in a given state; a webhook from a third party; a specific tenant.
- **Act**: HTTP call, enqueue a message, trigger a cron by hand.
- **Observe**: structured logs and traces; queue depth; dead-letter queue.
- **Breaks on**: third-party dependencies with no stub; cron that only runs on schedule.
- **Primitive**: a script runner (`go run ./cmd/agent`, `rails runner`, a manage command) — the
  service runs as N workers; its state is in the DB and the queue.
- **Also survey**: migrations; job enqueue / run-now / drain; inbound webhooks; request tracing to
  SQL; the API contract as oracle.

## Game / real-time app (engine, emulator, simulation)
- **Launch**: windowed binary; needs a GPU/display (headless/offscreen/virtual display?).
- **Observe**: **the screen** (frame capture), the in-game console/log, FPS/frame time.
- **Reach**: warp to map / scene / battle, give items, set flags, load a save state.
- **Act**: inject input (key, pad, touch) or call the game API on the main thread.
- **Assert**: query game state; screenshot of a *named* state.
- **Reset**: save states, seeded RNG, fixed timestep.
- **Breaks on**: console bound to the launching TTY; state not thread-safe (commands must run
  between frames); nondeterministic timing.

Games, cont.:
- A console bound to the launching TTY is usually solved by a FIFO or pty on stdin — try that
  before building a socket handle. Its replies are rarely framed: count prompts, or frame them.
- Capture frames at the scale the human sees, not only the native render target — scaling bugs
  live between the two.
- Engine and game are often two repos: the safety boundary (saves, logs written to the working
  directory) lives in the game, while the edit lands in the engine.

## Embedded runtime / scripting host (a VM or engine inside a host app)
- Two processes, two sets of ports, debug abilities that depend on the content loaded (a
  compiled release may disable the debug menu).
- The code a task touches may be in the content, the runtime, or the host — trace it (step 0)
  before choosing where to probe.
- Look for the runtime's own desktop build as a fast-Cycle proxy, and say which bug classes it
  cannot reproduce (storage I/O, GPU driver, packaged asset access, device performance).

## Mobile app (native, cross-platform, WebView shell)
- **Launch**: emulator/simulator boot (slow — measure it), install, start.
- **Observe**: `adb logcat` / `xcrun simctl` logs, screenshots, view hierarchy.
- **Reach**: deep links, debug menu, launch arguments, pre-seeded app storage.
- **Act**: `adb shell input`, UI automation (Espresso/XCUITest/Maestro), deep links.
- **Breaks on**: physical-device-only features, signing, push notifications, store sign-in.

## Desktop app (Electron, Qt, native GUI)
- **Observe/Act**: remote debugging port (CDP for Electron), accessibility tree, screenshots.
- **Breaks on**: no automation hook; OS dialogs (file pickers) that block.

## CLI tool / library / SDK
- **Launch** is "run it on an input"; for a library, probe through its tests or an example consumer.
- **Reach**: a fixture that reproduces the case; golden files.
- **Cycle** is usually the real gap: can one test run alone, fast, with readable output?
- **Cycle** also means: how does the consumer pick up my edit (workspace link, submodule bump,
  publish)? Can I run my working copy against the consumer without publishing?
- **Reset** residue is temp dirs and caches, not a database — check the tests clean up.
- **Breaks on**: tests that need network/credentials; snapshots with no update command; tests
  that exist but no script or CI runs.

## Developer / agent tooling whose input is another project
- Two loops: the **inner** one (the tool on fixtures, usually fast and fully reachable) and the
  **outer** one (the tool against its real consumer, often blocked by the consumer's policies).
  They give different answers; report both.
- Its own commands are the candidate handles (dry-run modes, explain commands, report writers).
- The useful missing handle is often an **explain** command: why did the tool decide X.

## Data / ML / batch pipeline
- **Reach**: a *small* representative input (sampled dataset, tiny config) — the full one takes hours.
- **Assert**: schema checks, row counts, metric thresholds on the sample.
- **Breaks on**: cloud-only data, GPU-only steps, runs measured in hours.
- **dbt specifically**: `dbt build --select state:modified+ --defer` (only what changed, the rest
  read from a reference); `dbt compile` / `dbt show` to see SQL and rows without writing;
  `dbt run-operation` for macros; a per-agent dev schema or target as the isolation unit; seeds as
  fixtures; data tests and row-count oracles (an oracle against production data is a fence);
  lineage (`dbt ls --select +model+`) as the blast radius; warehouse cost per run as the paid
  dependency; a local engine (DuckDB) as the lab.

## Infrastructure / IaC / deployment
- **Act** is usually forbidden beyond `plan` / `diff` / dry-run — the safety boundary *is* the shape.
- **Reach**: local emulators (LocalStack, kind, compose).
- **Assert**: policy checks, plan diffs.

## Embedded / hardware / device firmware
- **Launch**: simulator or emulator (QEMU, vendor sim) vs. physical board.
- **Observe/Act**: serial console — a classic "console bound to a TTY" case.
- **Breaks on**: hardware-in-the-loop only; flashing requires a human.

## Legacy / heavyweight stack (JSP, AngularJS, app servers, mainframe-adjacent)
- **Launch** may take minutes; measure it, and look for a partial launch (one module, one page).
- **Reach**: session forging, server-side test login, direct URL to a page with a state param.
- **Breaks on**: everything shares one server; no seeds; behaviour lives in DB procedures.

## Cross-cutting concerns (check on every shape)
- **Time**: is "now" injectable (virtual clock, offset), or is the real clock hard-wired? An
  injectable clock can still be bypassed — grep the task's code path for direct clock reads.
  Record the timezone of every runtime: dev machine, test runner, container, DB, end user.
- **Variants**: backends, platforms, browsers, scales, locales — which ones does the task name?
- **Performance**: when the outcome is a duration, which clock, cold or warm, how many runs,
  on which device class? An emulator number is not a phone number.
- **Ownership**: which repo owns the code to change, and may the agent change it?
- **Randomness**: seedable?
- **Third parties**: stubbed, recorded/replayed, or live?
- **Parallelism**: can two agents (worktrees) run at once — ports, data dirs, caches, displays, build
  outputs, global rows in a shared store? (parallel.md)
- **Secrets**: can the agent run without production secrets? Which dev secrets exist?
- **Agent-tool constraints**: things the agent's own harness refuses (typing passwords, some
  domains, GUI-only actions) — a handle has to route around them, not fight them.

## Levels by shape

The four rows of the evidence grid (grid.md), in each shape's own words. Use these words in the
map; keep the four rows. The **piece** row is the one agents skip — and the **witness** column at
each level is the one they leave blank.

| Shape | unit | piece | operation | journey |
|---|---|---|---|---|
| Web app with accounts | function, query, SQL function | component, screen region | request, server action, RPC, job, webhook | a session as a persona, across screens |
| API / backend, workers | function | handler or module with its ports faked | one request or job, on a local stack | a scenario across requests, jobs and services |
| Game / real-time | function, system | scene, battle, entity in a harness | one command or input, a save and load | a playthrough or a recorded input run |
| Embedded runtime / scripting host | script function | scene or screen in the runtime's desktop build | one call across the host boundary | the packaged app on the device |
| Mobile / desktop app | function, view model | screen or view, in a preview or harness | one intent, IPC call or API call | a session on the emulator or device |
| CLI / library / SDK | function | module, subcommand | one invocation on a fixture | the real consumer using it |
| Dev / agent tooling | function | one rule or pass on a fixture | one command on a fixture project | the tool on its real consumer |
| Data / ML / batch | macro, SQL unit test | model, transform | one model or step built (`--select`) | the DAG or the pipeline run |
| Infrastructure / IaC | policy, module test | module | `plan` / `diff` of one stack | the environment brought up locally |
| Embedded / firmware | function on the host | driver on the simulator | one command over the serial console | the board running its program |
| Legacy / heavyweight | function, procedure | one page or module with a partial launch | one request or procedure call | a session through the app server |

Witness at each level, typically: **unit** — the rows or files a unit wrote, asserted in its test;
**piece** — the calls a piece makes (requests recorded by a mock, declared calls in a lab);
**operation** — what one operation wrote, called and bypassed (a ledger, statement logging, a
recording proxy); **journey** — what a whole run touched: the mail caught, the jobs enqueued, the
rows changed in the run's own environment, the hosts reached.
