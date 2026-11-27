---
name: toolsmith
description: Builds satellite tooling so coding agents can reach a running app from the command line — launch and reset it, drive it as a persona, look inside its live process and data, screenshot named states — see a piece of it in a lab, and witness what its code wrote and sent. Maps what exists and what is missing on an evidence grid (unit, piece, operation, journey × lab, witness, live), compiles a roadmap led by the project's own task mix, reviews it with the human remark by remark, then builds and proves only the accepted handles. Three scopes — the whole app (/toolsmith map), a task as a use case for durable tooling (/toolsmith task "..."), or a named capability (/toolsmith want "..."). Use on an unfamiliar project, when an agent cannot reproduce, see or verify something ("I can't see the screen", "I need you to log in"), when asked to improve the tooling for agents or find the right tooling for a fix or feature, or for asks like "give me direct access to the database from the CLI".
---

# toolsmith

In Brooks's surgical team, the toolsmith builds the instruments the surgeon operates with. This
skill makes the agent the project's toolsmith: it builds **satellite tooling** — command-line access
to a running project, from outside it — so every later agent can reach, see and verify the app
instead of guessing. It changes the codebase only where a handle needs it (a hook, an API to
expose, a fence); the heart of the work is the tooling around the code.

A **handle** is something an agent *calls* and reads back: `bin/dev-login --as stranger`,
`app-dev run state order 42`, `curl -s localhost:3000/api/dev/state?order=42`, a socket into a
game's live process. Hardening, lint rules and docs are not handles. Full definition, the primitive
rule and the criteria: [references/principles.md](references/principles.md).

## Scopes

Toolsmith builds **durable** tooling only — handles the next agent, on the next task, will call
again. A one-off script to poke at today's bug is the coding agent's inline work, never a card.

| Scope | Invocation | Covers | Procedure |
|---|---|---|---|
| Whole app | `/toolsmith map` | every boundary; a roadmap of milestones | [map.md](references/map.md) |
| Through a task | `/toolsmith task "<fix or feature>"` | the boundaries one task crosses — as a **use case** for durable handles; toolsmith does not do the task | [scopes.md](references/scopes.md) |
| For a capability | `/toolsmith want "<capability>"` | the points one capability touches; design it properly or challenge an unsafe ask | [scopes.md](references/scopes.md) |

Every scope reads the same inputs and writes into the same project map and roadmap, so scoped
runs accumulate.

## The process

Copy this checklist and work through it in order:

```
Toolsmith progress:
- [ ] 1. Read decisions — toolsmith/decisions.md (project and parent folder), the existing map, agent files
- [ ] 2. Survey — the boundaries in scope; existing handles and test suites; agent-file rules; shared resources
- [ ] 2b. Task mix — sort recent commits by level; it decides what comes first, not the shape's habit
- [ ] 3. Choose the primitive — where the state lives decides it (principles.md)
- [ ] 3a. Fill the evidence grid — a verdict in each of the 12 cells (grid.md)
- [ ] 3b. Name the capabilities — 2–5 things the agent cannot do today, from the grid's gaps weighted
      by the task mix, with evidence; the roadmap's backbone
- [ ] 4. Cards — each with Status, usage, Is, Not a script because, Origin, Fence, Parallel, Permission
- [ ] 5. Roadmap — milestones cut by capability (M1 = the loop of the most frequent task), foundations, real
      dependencies, keystones; each milestone with Capability, Depends on, Demo and Expect;
      deferred cards in their own section
- [ ] 6. Present — render the review page; wait
- [ ] 7. Answer every remark — revise; record decisions
- [ ] 8. Explicit go — "go for M1"; record the accepted plan
- [ ] 9. Build — one handle at a time, on the project's build system
- [ ] 10. Prove — run each usage example for real; add it to doctor and CI; configure permissions;
      document it in the agent file; check a fresh session with no hint finds and uses it; move the
      card to Delivered with its Verified level (implemented · tested · demoed) — never rounded up
```

Steps 1–5 are the map ([map.md](references/map.md), written with
[map-template.md](references/map-template.md)); 6–10 are the review loop
([review.md](references/review.md)). Render the page with the bundled script — run it, don't read it:

```sh
python3 <skill>/scripts/review_page.py map.md -o review.html            # one map
python3 <skill>/scripts/review_page.py a/map.md b/map.md -o review.html # several repos, one page
```

## Core rules

- **Where the state lives decides the primitive.** In a database or queue (most web stacks): a
  script runner over the app's own code (`rails runner`, `go run ./cmd/agent`). In memory (games,
  desktop apps, daemons): a live eval into the process. In the browser (SPAs): a browser runner.
  Then most needs are **scripts** under that one primitive — not bespoke flags.
  [principles.md](references/principles.md)
- **Handles belong to their layer.** An engine's handles work for any consumer; a primitive goes on
  the lowest layer present in every targeted variant and safe to run code in.
  [principles.md](references/principles.md)
- **The evidence grid: four levels × three ways.** Unit, piece, operation, journey — by bring out
  (a lab), witness (the effects), reach in (the live app). Every cell gets a verdict graded
  `observed` · `asserted` · `gated`, or `gap` / `n/a` with why; a gap becomes a card only when a
  capability needs it. The unit and e2e suites fill two cells, not "the lab"; the piece row and the
  witness column are where maps go blank. A **harness** that makes a unit or piece testable is a
  handle (a fake store, a one-phase runner, a headless scene runner); individual tests are not. Every handle is also judged on loop (fast,
  parallel-safe, resettable — environments live here) and fence (dev-only, fails closed).
  [grid.md](references/grid.md)
- **Tooling, not a security audit.** Safety only as the few fences an agent's own runs need; app
  security bugs get one line in passing. If the agent file refuses AI work, stop at the map.
- **Parallel agents.** Say how many agents can work at once today and what they collide on;
  environments, `--env` on every handle, a process registry, leases.
  [parallel.md](references/parallel.md)
- **Rules as guards.** Prose rules in agent files become hooks, permission lists, lint rules.
  [guards.md](references/guards.md)
- **Capabilities first, then handles.** Name what the agent cannot do today; cut the roadmap
  into milestones that each deliver one capability, proven by a demo the agent can run. Handles
  are the means. [roadmap.md](references/roadmap.md)
- **Review before building.** Answer every remark individually; build only after an explicit go;
  record decisions in `toolsmith/decisions.md` so the next map does not re-open them.
  [review.md](references/review.md)

## References

| File | Read it when |
|---|---|
| [principles.md](references/principles.md) | designing any card — what a handle is, the primitive, layers, criteria, anti-patterns |
| [grid.md](references/grid.md) | placing a handle — levels × ways, grading a cell, the declared boundary, loop and fence, the diagram's categories |
| [map.md](references/map.md) | running the whole-app scope |
| [map-template.md](references/map-template.md) | writing the map — exact card grammar the review page reads |
| [scopes.md](references/scopes.md) | running the task or capability scope |
| [review.md](references/review.md) | presenting, answering remarks, accepting, building, proving |
| [roadmap.md](references/roadmap.md) | compiling cards into milestones |
| [parallel.md](references/parallel.md) | analysing shared resources and isolation |
| [guards.md](references/guards.md) | turning agent-file rules into enforced guards |
| [handles.md](references/handles.md) | looking for a handle family — reach in, lab, witness, web, runtime, eyes |
| [tools.md](references/tools.md) | choosing an existing tool (with fit evidence) over project code |
| [shapes.md](references/shapes.md) | knowing what each rung means for this kind of project |
| [ladder.md](references/ladder.md) | probing a running app rung by rung (task scope, audits) |
| [grill.md](references/grill.md) | choosing the few questions worth asking |
| [report-template.md](references/report-template.md) | writing a ladder report |
