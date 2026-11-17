# agentic-toolsmith

> Satellite tooling for coding agents: command-line access to a running project, from outside it.

`toolsmith` is a skill for coding agents. In Brooks's surgical team, the toolsmith builds the
instruments the surgeon operates with; this skill makes the agent the project's toolsmith.

Agent loops do their best inside the ecosystem they are given. The bigger lever is usually the
ecosystem itself: can an agent launch the app, log in as a persona, put it in a given state, look
inside its live process, read what it wrote and sent, screenshot a named state — **from the
command line, without a human?** Toolsmith maps what exists and what is missing, compiles it into a
roadmap, reviews it with you remark by remark, then builds and proves the handles you accept.

It changes the codebase only where a handle needs it — a hook, an API to expose, a fence. The heart
of the work is the tooling around the code, not the code.

**What it is not.** Repo-readiness checkers (Factory's Agent Readiness, AGENTS.md generators and
audits) score the repository's hygiene — instructions, tests, conventions. Toolsmith builds the
instruments around a running project. They are complementary; toolsmith writes only its own "How to
reach the app" section into the agent file and leaves the rest to them.

## Three scopes

- `/toolsmith map` — the whole app: every boundary, a roadmap, milestones.
- `/toolsmith task "<fix or feature>"` — the task as a use case: which **durable** handles would
  make tasks like it reachable and verifiable. It does not do the task, and builds nothing
  ephemeral — one-off helpers are the coding agent's inline work.
- `/toolsmith want "<capability>"` — "direct DB access from the CLI": the handle designed properly,
  or the request challenged when a safer, more useful shape exists.

Every scope writes into the same project map and roadmap.

## Map first, if you want

`/toolsmith map` is a planner pass with no task: the agent charts **every boundary of the app** —
UI, process, runtime, internal seams, state stores, egress, ingress, time, identity, platform,
delivery, telemetry, configuration — and at each inspection point, what an agent could **see,
steer, stub, freeze or check** there today. Candidate handles come first; safety only as the few fences those handles need. You get a diagram and a table of where tooling could apply, grilled with
you, before any tool is proposed. Later runs read the map instead of rediscovering it.

## Three ways up

| | How | Best for |
|---|---|---|
| **Reach in** — the live app | Handles into the running app: dev login, eval console, warp, deep links | Runtime, timing, integration, "only on device X" |
| **Bring out** — the lab | Rebuild a piece of the app in isolation so every declared state has its own address — no backend, no login | UI composition, screens with many states |
| **Witness** — the effects | Record what the app touched — DB statements, outbound HTTP, mail, files, messages — and compare it to what was declared | Anything that writes, sends or calls |

Most agents verify what the screen shows and never what the code touched. The skill makes the
third column a rung of its own.

Handles are shown in seven categories — launch & loop, ingress, runtime, state, egress, eyes & logs, and the lab around the runtime —
one picture of the app with what exists and what is missing. Every handle is also judged on two properties, whichever way up: **loop** (fast, isolated,
resettable) and **fence** (dev-only, fails closed). Together that is a classifier for any app's
agent harness: each handle gets a coordinate — **boundary × verb × way** — and a quality bar.

## Install — one command

```sh
curl -fsSL https://raw.githubusercontent.com/Scorbutics/agentic-toolsmith/main/install.sh | bash
```

Installs into `~/.claude/skills/toolsmith`. Options: `--project` (this project's `.claude/skills/`
only), `--dir DIR`, `--ref REF`, `--uninstall`. From a clone: `./install.sh`. With the skills CLI:
`npx skills add Scorbutics/agentic-toolsmith`.

Then, in any project, start your agent and type `/toolsmith map`.

## Test it — one command

```sh
git clone https://github.com/Scorbutics/agentic-toolsmith && cd agentic-toolsmith
./evals/run.sh --only vue-realworld          # one scenario, sonnet, with the skill and without
./evals/run.sh --model sonnet --model haiku  # every scenario, two models
```

Five public repositories, one per shape — a Rails monolith (lobsters), a Go service (miniflux), a
Vue SPA (vue-realworld), a dbt pipeline (jaffle-shop), a Godot game (tps-demo) — pinned to a commit.
Each runs the Claude Code CLI headless on the same task **with the skill and without it**, read-only,
and scores both outputs on the scenario's expected behaviours (did it pick the right primitive for
where the state lives? a mock API for the SPA? DuckDB as the lab for dbt?), the runnable usage
examples, the roadmap, and whether cited `file:line` references resolve. Results land in
`eval-runs/<timestamp>/results.md`. Needs `git`, `python3` and a logged-in `claude` CLI; each run is a
real agent session of several minutes.

## What it is not

- Not *Agent Experience* (AX) in Netlify's sense — that is about agents as **users of your
  product** (can an agent discover and call your API?). This is about agents as **developers
  of your product** (can an agent reach the app it is changing?).
- Not Browserbase's `agent-experience` skill — that grades how easily an outside agent onboards
  onto your docs/SDK. This measures the agent's reach into your running app and builds what's missing.
- Not an agent that writes its own tools at runtime ("LLMs as tool makers"). The tools are
  dev-only handles into *your app*, reviewed and committed like any other code.
- Not a product. The skill recommends whichever handle fits — often one your project half-has.

## Prior art

Research and practice:

- **SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering** — Yang et al.,
  NeurIPS 2024 ([arXiv:2405.15793](https://arxiv.org/abs/2405.15793)). The ACI term, and the
  evidence that interface design moves agent results.
- **Building effective agents** — Anthropic (2024): invest in the agent-computer interface as
  much as in human-computer interfaces.
- **Writing effective tools for agents** — Anthropic (2025): concise, meaningful, actionable output.
- **Effective harnesses for long-running agents** — Anthropic
  ([post](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)):
  an `init.sh` that starts the app and a basic end-to-end check *before* any feature work.
- **Harness engineering: leveraging Codex in an agent-first world** — OpenAI, Feb 2026
  ([post](https://openai.com/index/harness-engineering/)): make UI, logs and metrics directly
  legible to the agent; per-worktree observability.
- **Agent Experience (AX)** — Mathias Biilmann / Netlify, 2025
  ([page](https://www.netlify.com/agent-experience/)): agents as a first-class audience.
- **grill-me** — Matt Pocock ([skill](https://www.skills.sh/mattpocock/skills/grill-me)): one
  question at a time, look in the codebase before asking.
- **The Mythical Man-Month** — Fred Brooks (1975): the surgical team and its toolsmith.

Two tools by the same author, each the strong form of one "way up". The skill does not require
them: it recommends a tool — these, Storybook, Mailpit, OpenTelemetry or a few lines of project
code — only when the app's map shows it fits, with the alternative and the cost, and it always
discloses these two as the author's ([tools.md](skills/toolsmith/references/tools.md)):

- **[motu](https://github.com/Scorbutics/motu)** — *the lab.* Declare a screen region's state and
  owners; the lagoon renders every declared state at its own URL, with no backend and no login,
  and checks keep the lab and the page in agreement.
- **[assay](https://github.com/Scorbutics/assay)** — *the witness.* An effect ledger: what each
  backend operation actually touches (tables, procedures, outbound hosts, access-control bypass),
  and a gate that fails when it differs from what was declared.

## Layout

```
skills/toolsmith/
  SKILL.md                      the process: trace → survey → verify boundary → probe → grill → rank → build → prove
  references/map.md             map mode: 13 boundary classes × 5 verbs (see, steer, stub, freeze, check)
  references/map-template.md    the map, with its diagram
  references/shapes.md          what each rung means per project shape
  references/handles.md         handles by rung: reach in, lab, witness, assert, launch/reset
  references/tools.md           fitting an existing tool: evidence, alternative, cost, disclosure
  references/grill.md           question bank
  references/report-template.md the deliverable
  references/scopes.md          task and capability scopes
  references/review.md          the review loop: present, answer every remark, revise, accept, implement
  scripts/review_page.py        map.md → one self-contained HTML review page (stdlib only)
docs/trials.md                  dry runs on four project shapes, and what each changed
```

## Status

Draft v1, revised after dry runs on four project shapes (web app with accounts, game engine +
game, mobile app with an embedded runtime, CLI dev tool): see [docs/trials.md](docs/trials.md).
Feedback from other shapes is the most useful contribution.

## License

MIT
