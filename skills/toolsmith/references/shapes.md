# Project shapes

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

## API / backend service, workers, queues
- **Reach**: a job in a given state; a webhook from a third party; a specific tenant.
- **Act**: HTTP call, enqueue a message, trigger a cron by hand.
- **Observe**: structured logs and traces; queue depth; dead-letter queue.
- **Breaks on**: third-party dependencies with no stub; cron that only runs on schedule.

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
- **Parallelism**: can two agents (worktrees) run at once — ports, data dirs, caches?
- **Secrets**: can the agent run without production secrets? Which dev secrets exist?
- **Agent-tool constraints**: things the agent's own harness refuses (typing passwords, some
  domains, GUI-only actions) — a handle has to route around them, not fight them.
