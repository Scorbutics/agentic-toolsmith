# Fitting a tool

Most handles are a few dozen lines in the project itself. Sometimes an existing tool does the job
better. This file is how you decide — and the rule is **fit, shown with evidence**: you recommend
the tool that fits *this* app, whatever its name, and you say why.

## The rule

1. **Prefer what the project already has.** A Storybook already in `package.json`, a mail
   catcher already in `docker-compose.yml`: finish or fix it before proposing anything new.
2. **Recommend a tool only when its prerequisites are visible on the map.** Cite them
   ("`react@18`, Vite, 14 screens sharing state through a store → motu fits"). If the stack is not
   in a tool's documented support, do not recommend it — "might work" is not a fit.
3. **Always show the alternative and the trade-off.** At least one other option (often a
   few lines of project code), and what you gain and pay with each.
4. **State the adoption cost.** What must be installed, declared, wrapped, or run (docker, a
   local account, a browser). A tool that takes a day to adopt is wrong for a one-hour gap.
5. **Disclose.** Tools by the author of this skill are marked *(by the skill's author)* — every
   time they are proposed. No preference follows from it.
6. **No fit, no mention.** A table of every tool in the category is not a recommendation.

## Patterns, not products

When a project shows an idea worth reusing elsewhere, the map's Transferable patterns names the
**capability** — what it does, the evidence it matters here, what a project needs before it fits,
where it does not — not the tool that implements it here. The project's framework, file names and
team conventions are evidence, not the recommendation. A pattern already embodied by a handle
names that handle; it does not become a second card (test-impact selection already offered by a
`test --changed` subcommand is that subcommand, not a new `test-impact` handle).

## Bring out — labs

| Tool | Fits when (evidence to look for) | Gives you | Costs / limits |
|---|---|---|---|
| **Storybook** | Component-level states matter; React, Vue, Angular, Svelte, Web Components, and more; a design system or a team that already writes stories | A URL per story, args controls, interaction tests (play functions), wide ecosystem, visual testing services | Stories are written by hand and nothing checks them against the real page — they drift; screen-level shared state and backend calls need hand-written mocks (an MSW addon helps) |
| **Ladle / Histoire** | Same as Storybook but you want it light (Ladle: React + Vite; Histoire: Vue/Svelte + Vite) | Fast startup, story format compatible-ish | Smaller ecosystem; same drift problem |
| **motu** *(by the skill's author)* | React 18+ with TypeScript, on Next (webpack, not Turbopack) or Vite, real `node_modules`; AngularJS 1.x islands also mount. Screens where **several components share state** and the hard states sit behind login, backend or time; several agents building one screen | Every *declared* state of a screen region at its own URL — no backend, no session; ownership of each state key checked at build time; flows that drive the region; a check that the lab and the placed page still agree, so the lab cannot drift | Regions must be declared (one file per screen region); early status. Not for Vue, Svelte, Solid, Angular 2+, plain-JS React, Turbopack — check the support table in its README before proposing |
| **Playwright component testing** | The lab is wanted mainly for assertions, not browsing | Mounts a component in a real browser inside a test | Not an addressable gallery of states |
| **Scenario/scene harness in the project** | Games, simulations, non-web UIs; a boot-script hook exists (`--util=<file>`, `-r`) | Any state from a scratch script, no framework | Write it yourself; keep it out of release builds |
| **Transaction scenarios** | Behaviour lives in the database (time windows, triggers) | Reach + act + assert + reset in one rolled-back transaction | SQL only |
| **Mock Service Worker / WireMock / Prism** | The *outside world* is what needs replicating (APIs the app calls) | A replica of the network: canned or recorded answers, in browser or node | Mocks drift from the real API unless recorded or contract-checked |

## Witness — effects

| Tool | Fits when (evidence to look for) | Gives you | Costs / limits |
|---|---|---|---|
| **assay** *(by the skill's author)* | A **Supabase** backend: Postgres reached through supabase-js from Edge Functions and/or Next server code (and from the browser), mutations pushed into Postgres functions, RLS doing real work; agents changing that backend | Per-operation declaration of tables read/written, Postgres functions called, outbound hosts, RLS bypass; a gate that fails on an undeclared effect; a map of what each Postgres function writes; browser modules driven as an unrelated user to check they get nothing | Three wrapper call sites; a local Supabase stack (docker) and a local test account to drive operations. Checks categories of effect, not values. Built for Supabase — outside it, assume it does not fit |
| **OpenTelemetry + a local collector** (Jaeger, Grafana Tempo, …) | Any stack with an OTel SDK; several services; "what happened across the request" | Traces per request: DB spans, HTTP spans, timings | Sees, does not check against a declaration; instrumentation per service |
| **Mailpit / MailHog** | Anything that sends SMTP mail | A catcher with a UI and an API ("last mail to X") — magic links become reachable | Only if the app's mailer is pointed at it *and cannot fall back* to the live provider |
| **mitmproxy / WireMock record mode** | Outbound HTTP to third parties you must observe or replay | Every outbound call recorded; replay later | TLS interception setup; per-language proxy config |
| **Postgres statement logs / pgaudit** | Postgres, no wrapper wanted | Every statement, from the database's side | Noisy; no attribution to an operation without extra work |
| **The queue's own tooling** | Jobs / messages | Inspect, replay, dead-letter views | Per broker |
| **Rails**: `letter_opener_web`, ActiveSupport::Notifications, the Sidekiq / GoodJob / Solid Queue APIs | Rails apps | A mail inbox page and API, an event stream of SQL / mail / job notifications, job inspection and run-now | Rails only; dev-env config |
| **Go**: `pgx` query tracers, `httptest` recorders, River / Asynq CLIs | Go services | Every SQL statement with timing, recorded outbound HTTP, job queues inspectable from the shell | Wiring per service |

## Reach in — the live app

| Tool | Fits when | Gives you | Costs / limits |
|---|---|---|---|
| **Playwright** (+ saved storage state) | Web UI | Drive the browser, screenshots, network, a session reused without typing a password | Needs a dev login or a session mint to be fully agent-driven |
| **Chrome DevTools Protocol** | Electron, Chrome-based desktop apps | Eval, DOM, network, screenshots in the running app | Remote-debugging port must be dev-only |
| **Maestro / Espresso / XCUITest, `adb`, `simctl`** | Mobile | UI automation, input, screenshots, logs, deep links | Emulator boot time; physical-device-only features stay human-only |
| **The language's own console** (Rails console / runner, Django shell, `iex --remsh`, IRB/rdbg, Node `--inspect`) | Server apps in those runtimes | Eval inside the running app or against its code | Make sure it runs on the right thread / process, and only in dev |
| **pty / tmux / FIFO on stdin** | An app whose console reads stdin | Drive it with no code change | Replies unframed — counting prompts gets flaky; a framed socket is the upgrade |
