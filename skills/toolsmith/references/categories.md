# Categories, ways and properties

## Contents
- Seven places a handle lives
- Three ways up

## Seven places a handle lives

Every handle — existing or proposed — sits in one of seven categories. They are what the human
sees first: one picture of the app with its handles around it, solid where they exist, dashed
where they are missing.

| Category | What it gives the agent | Typical handles |
|---|---|---|
| **Launch & loop** | start it, know it is ready, isolate it, reset it, turn the loop fast | run/up scripts with readiness, per-run dirs and ports, `doctor`, reset, hot reload |
| **Ingress** — drive it | push input in, as someone | routes and API calls, CLI commands, input injection, deep links, dev login and personas |
| **Runtime** — inside the live process | look and act inside the running app | remote eval, remote debug, profiler |
| **State** — data and time | put the app in a state, read it back | seeds and scenarios, queries and dumps, snapshots, save states, virtual clock, RNG seed |
| **Egress** — what leaves | replace or record the outside world | mail catcher, HTTP stub or recorder, effect ledger, queue inspection |
| **Eyes & logs** | see what happened | screenshots of a named state, logs, traces, crash reports |
| **Lab** — the environment around the runtime | a place where the app, or a piece of it, runs outside the human's setup | a virtual display (Xvfb), a container or VM image, an emulator or simulator, a local stack (compose), a harness hosting a piece of the app outside the live process (component lab, state renderer such as motu's lagoon, scene or battle harness), the environment registry (`envs up <name>`) |

**One card per handle, one main category, optional secondary ones.** Some handles are two sides
of the same coin — a live eval is runtime *and* ingress; a remote debugger is runtime and part of
the launch. Give such a handle one card, its main category first and the others in parentheses
(`runtime (+ ingress)`), and merge cards that turn out to be the same handle seen from two
categories (a "scenario" card that is really `run` with a scene argument is one card).

The Lab is drawn *around* the other six: it is what contains the runtime. It is also where the
*bring out* way happens — running a piece of the app in a lab rather than reaching into the live one.
Look for it explicitly; it is the category agents forget, because its pieces sit outside the
code (a Dockerfile, an AVD, a display server) or look like tests.

Identity lives in Ingress (who is driving); time and randomness live in State (they make a state
reachable). The boundary classes of map mode are how you *find* handles; the six categories are
how you *show* them.

**Eyes are not optional.** For anything with a screen, a screenshot of a named state is often
the only way to verify — and the source depends on the shape: a headless browser (Playwright),
the game's own framebuffer readback (`glReadPixels`, the engine's snapshot call, a viewport
texture), the emulator (`adb exec-out screencap`, `simctl io screenshot`), the desktop app's
debugging protocol (CDP). A screenshot handle returns the image *and* the state it shows.

## Three ways up

A rung can be climbed three ways. Know all three before proposing anything — the best handle is
often not the one the shape suggests.

- **Reach in — the live app.** Handles into the running app: a dev login, an eval console, a
  warp command, a deep link. Full fidelity; each state costs steps to reach.
- **Bring out — into a lab.** Run a piece of the app in isolation, in a lab, so that every state it can be
  in is *declared* and has its own address — no backend, no session, no login (a region/state
  renderer such as motu's lagoon; component labs; a scene harness for a game; a transaction
  scenario for SQL). Every state is one URL away; but the lab only shows what was declared, so
  pair it with a check that the lab and the live app still agree.
- **Witness — the effects.** Record what the app does *outward* — database statements, outbound
  HTTP, emails, files, messages — and compare it to what was declared (an effect ledger such as
  assay; a mail catcher; an HTTP recording proxy; statement logging). Most agents verify what the
  screen shows and never what the code *touched*; effects are where the dangerous bugs are, and
  the declaration doubles as the safety map.

Rule of thumb: composition and many-state UI → **lab**; runtime, timing, integration, "only on
device X" → **live**; anything that writes, sends or calls → **witness**, whichever of the other
two you use.

Classify a handle by **where the agent stands**: inside the running app (reach in), in a replica
of the app or of its surroundings (bring out — a mock server returning canned answers is a
replica of the outside world), or at the edges watching what leaves (witness). A tool may climb
several ways; list each.

### …and two properties

Every handle, whichever way, is also judged on:

- **Loop** — is it fast, **parallel-safe**, resettable? Parallel-safe has a test: *two agents can
  run it at the same time without seeing each other's effects.* Access you cannot repeat cheaply
  or run twice at once is access for one attempt. (Ladder rungs 7 and 8; see "Parallel agents".)
- **Fence** — is it dev-only by construction, does it fail closed? A handle that can reach
  production, or a stub that falls back to the live service, removes safety instead of adding
  access.

| | Reach in | Bring out | Witness |
|---|---|---|---|
| **Access** — see · steer · stub · freeze · check | console, warp, dev login | lab, scenario, mock | ledger, catcher, traces |
| **Loop** — fast · parallel-safe · resettable | hot reload, per-run working dir | renders with no backend | per-run trace, diffable log |
| **Fence** — dev-only, fails closed | no eval in release | fixtures from the app, never real data | stub never falls back to live |

Any handle in any app gets a coordinate: **category × verb × way** — *where* it lives (one of the
six places above), *what* it lets the agent do (see, steer, stub, freeze, check), *how* the agent
stands (reach in, bring out, witness) — with loop and fence as its quality bar. The boundary
classes of map mode are how you find it. That is the vocabulary of the map, the report and the
proposals.
