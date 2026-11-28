# Eval results

## A deep game bug, with and without the tooling — SmashAndDash (2026-11-28)

The case toolsmith is for: a bug the owner hit in play — **from the second battle of a session on, the
player's Pokemon is drawn off screen**. Root cause in the engine (`a29b29ae`, tangled into game
`0c126b1`): an image's texture was shared by every texture of its file, so the battle's team slot,
resizing its image, resized the sprites made from the same file. Task: game `641c3e4`, the engine just
before the fix. Judge: the fix's own engine test, hidden — 4 of 6 assertions fail before (8 == 15), 6/6
with the fix; any root-cause fix passes, a workaround in the battle screen does not (the owner: the only
fix is a texture lifecycle of its own in `Image.cpp`). Arms on the same commit: **tooled** — the
repository as it is (`sad-run`, `ska-console`, battle and party scripts, the "How to reach" section);
**bare** — that tooling removed (committed away, restored only for the judge). Sonnet 5.5, two runs each.

The game builds and runs in a cloud container (SDL 3.4 from source, Xvfb): ready in 5–8 s, battles
replayed deterministically (seed, fixed step, both sides played by the battle AI).

| Report given to the agent | Arm | Solved | Turns / time / cost | Tooling commands | Raw game launches |
|---|---|---|---|---|---|
| with the owner's diagnosis ("as if a sprite were reused") | tooled | 2/2 | 21, 17 · 148 s, 48 s · $0.43, $0.32 | 0 | 0 |
| | bare | 1/2 | 39, 33 · 135 s, 109 s · $0.70, $0.61 | — | 0 |
| symptom only (what the player saw) | tooled | 0/2 | 60 min (limit) · 37 min, gave up | 84 · 44 | 0 |
| | bare | 0/2 | 60 min (limit) · pending | — | 13 · pending |

- **With the diagnosis, nobody runs the game**: the cause is found by reading code; the tooled arm, with
  its agent docs, did it in about half the turns and cost.
- **With the symptom only, the tooled agent reaches the failing state with the tooling** (84 and 44
  commands) — and the bare agent rebuilds that by hand (13 raw launches under its own Xvfb, and edits to
  the repository's save files). **Neither finds the cause in an hour.**
- **Why, from how the bug was really found**: the owner's Opus session first asked for a debug view of
  a sprite's drawing state (sizes, scale, crop, offset — commit `641c3e4`); the owner reproduced the bug
  and sent a screenshot; the invalid integer in that view led to the engine in minutes. The view
  **draws** its values on screen; no script can read them. The agents could reach the second battle but
  could not see the one number that mattered. → the skill's rule **eyes return text, not only pixels**.
- **Checked once**: a tooling build with that rule (Sonnet, at the task's base) made a real text handle —
  `fighters.miniska`: every fighter's team, hit points, position, action, status — but not the drawing
  state (size, offset, scale, drawn) behind the existing debug window. That would not have exposed this
  bug, so the task was not run again on it. One build; and the rule was written from this very bug, so
  only a different deep bug can test it fairly.
- **Judge lessons, caught before any agent ran**: a replayed battle's outcome first looked like a judge
  for another fix (`bce53ad`), but the win came from later gameplay changes — the fix commit itself still
  lost, frame for frame; a group battle's 'flight' did not move either. Rendering bugs do not change a
  battle played by the AI: they need a judge on what is drawn, or the fix's own test.

## Task-based eval — does the tooling let an agent finish real work? (2026-11-27)

`evals/task_run.py`: real fixes and features from a project's history, started at the commit before,
described as a ticket would (interface named, no hint of the code), judged by the change's own tests,
hidden until the end. Arms: **bare** (the task alone) and **toolsmith** (one map-scope session per
project builds and proves M1 at the oldest task's commit; its patch is applied to every task; the skill
is removed before the task session). Recorded: solved, turns, time, cost, commands reaching state,
commands calling the tooling.

**Well-specified bugs, verified by the ordinary suite** (six tasks, fd and healthchecks, bare only):
solved 24/24 in about a minute each, $1.44 in all. Nothing for tooling to do: such tasks are left out of
what toolsmith claims.

**State-heavy work** (three healthchecks features — report summary over a downtime history, editing a
Shell integration behind a config switch, Gotify priorities and what is sent — a PostgreSQL-only bug,
and an fd feature as a control; Sonnet and Haiku, two runs each): bare 17/20, toolsmith 19/20, times
close task by task. **This run is not evidence about toolsmith**: the worktrees lived under /tmp, where
`claude -p` does not load a project's CLAUDE.md, so no toolsmith session ever saw the commands its
tooling build had documented. The harness now keeps worktrees under the home directory and checks, before
any session, that a codeword in AGENTS.md imported by CLAUDE.md reaches the agent.

**Recheck with the agent file loading** (the two most state-dependent features, one run per model,
reusing the same tooling builds): 4/4 solved, against 5/8 for bare on the same tasks. Both Sonnet
sessions called the tooling (`hcdev` to mail a report or post a form, `hcdev-doctor`); the Haiku sessions
did not — Haiku's tooling build had made handles but written only "run manage.py test" into CLAUDE.md.
Hence the skill's new step 11: every delivered handle's command must be in the text a session loads at
startup.

What this does and does not show:
- agents use the tooling when it is in the agent file, and not when it is not;
- on healthchecks the effect is small, because the project already gives agents cheap state through its
  test base class (users, projects, checks created for every test): the bare arm reaches state with
  `manage.py test` within a dozen tool calls;
- the case toolsmith is built for — reaching a state costs a login, seeded data and a flow — is not in
  this set. Running the same eval on such a project is the next measure (`evals/task-eval-on-your-machine.md`).

## v5 and two hold-out projects (2026-11-27)

v5 makes `either` name its evidence on both sides and adds worked examples of piece-level witness and
journey-level labs. It was frozen (`fdfe9a8`) **before** two hold-out projects were chosen —
healthchecks (Django service) and fd (Rust CLI) — whose keys were drafted blind from 28 and 27 fixed
bugs and sealed until their runs were scored. Two runs per cell, Sonnet and Haiku (40 v5 maps on the
ten scenarios, 24 on the hold-outs); judge self-agreement on M1 38/40 and 0.93 Jaccard on cells.

Designed proposals only:

| Keys | Arm | Recall | Precision |
|---|---|---|---|
| owner (4) | no skill | 37 % | 57 % |
| | v4 | 46 % | 64 % |
| | v5 | 46 % | 63 % |
| bug-grounded (6) | no skill | 44 % | 100 % |
| | v4 | 55 % | 99 % |
| | v5 | 56 % | 100 % |
| **hold-out (2)** | no skill | 33 % (20/60) | 95 % |
| | v4 | 37 % (22/60) | 100 % |
| | v5 | 35 % (21/60) | 95 % |

- **v5 changed nothing measurable.** Maps hedged as much (36 % `either` where the owner wrote
  `propose`, 39 % with v4), and some of the hedging moved to `leave` (8 % → 14 %) — the opposite of
  the intent. Fewer maps decided every cell (30/40 against 54/60). More prose rules have stopped
  moving the agents' decisions.
- **On the hold-outs the skill's margin shrinks**: 37 % against 33 % without the skill, where it was
  46 % against 37 % on the keys the rules were tuned against. Part of the earlier gain was tuning, and
  eight maps per arm is too few to tell the rest from noise. Precision stays at least as high, with
  half the proposals and nearly all of them designed (86–93 % against 37–47 %).
- **M1 in an accepted cell**: 0/8 without the skill, 0/8 with v4, 1/8 with v5 — no version puts the
  first milestone where the bugs were, here either.

## Each cell decided — v4 (2026-11-27)

v4 has the map end each grid cell with a decision — `→ propose` · `→ leave` · `→ either`, with why —
binds the cards to it, and makes a missing seam an explicit decision. Same ten scenarios, prompt and
judge; 60 maps, judged twice (M1 the same in 58/60, cells Jaccard 0.91). 54 of 60 maps decided
every cell. Judge outputs: `evals/results/2026-11-27-v4/`. Designed proposals only, loop rows counted:

| Keys | Arm | Proposals/map (designed) | Recall | Precision |
|---|---|---|---|---|
| owner (4 projects, 102 expected cells) | no skill | 12.2 (55 %) | 37 % | 57 % |
| | before the grid | 7.4 (97 %) | 45 % | 58 % |
| | v2 | 5.9 (94 %) | 42 % | 65 % |
| | v3 | 6.3 (92 %) | 40 % | 60 % |
| | **v4** | 6.3 (93 %) | **46 %** | **64 %** |
| bug-grounded (6 repos, 198) | no skill | 12.3 (53 %) | 44 % | 100 % |
| | before the grid | 10.8 (96 %) | 59 % | 99 % |
| | v2 | 7.5 (94 %) | 52 % | 100 % |
| | v3 | 7.7 (89 %) | 56 % | 100 % |
| | **v4** | 7.6 (90 %) | 55 % | 99 % |

- **On the owners' keys, v4 is the best version yet** — the most expected cells with something to run,
  with the second-best precision, and half the proposals of no skill. The margin over the skill
  before the grid is small (47 against 46 cells of 102): v4 recovers what v2 and v3 had lost in
  recall while keeping the grid's precision, rather than jumping ahead.
- **On the bug-grounded keys it stays below the skill before the grid** (55 % against 59 %).
- **The maps' own decisions against the owners'** — where an owner wrote `propose`, the map decided
  propose in 40 of 75 cells, `either` in 29, `leave` in 6; where an owner wrote `leave`, the map left
  it in 41 of 62 and proposed it in 8. Agents respect a leave; they **hedge** on a propose.
- **Where they miss**: `piece × witness` (missed 9 of 11 — what one piece writes or calls, which the
  skill's guidance barely illustrates), `journey × bring out` (6 of 6 — an end-to-end run with the
  outside world replaced), and `operation × witness` on the projects whose owner wanted it, while
  proposing it on one whose owner said leave.
- **Cost**: M1 is loop-only in 9/60 maps (v3 6/60, v2 4/60) — still far from 38/60 without the skill.

## Correction: count what the agent can call (2026-11-27)

The sections below counted a cell as reached when **any** proposal landed in it — a tool's name in a
list as much as a designed handle. Maps without the skill propose about 70 % more items, and about
half of those are names with no command, usage or design; maps with the skill design over 90 % of
theirs. Counted that way, "the skill does no better than no skill" was a property of the metric.
`judge.py` now leads with **recall and precision from designed proposals only**. Across all ten keys
(240 judged maps):

| Arm | Proposals per map | Designed | Recall, designed only | Precision |
|---|---|---|---|---|
| no skill | 12.3 | 54 % | 33 % | 85 % |
| before the grid | 9.4 | 97 % | 46 % | 84 % |
| v2 | 6.9 | 94 % | 44 % | 90 % |
| v3 | 7.2 | 91 % | 46 % | 88 % |

(Loop rows left out here; `judge.py`'s report counts them and reads a few points higher.) With about
half the proposals, the skill reaches more of the expected cells with something an agent can run, at
equal or better precision. What stays true below: no version of the skill yet reaches more expected
cells than the old skill did — targeting the right cells is the open work.

## Harnesses as handles — v3 (2026-11-27)

v3 makes a harness that renders a unit or piece testable a handle (a fake store, a one-phase runner,
a headless scene runner); individual tests stay out. Same ten scenarios, same prompt and judge, three
runs each on Sonnet and Haiku (60 maps; 240 maps judged twice in all, M1 the same in 208/240).
Judge outputs: `evals/results/2026-11-27-v3/` (private projects: in their own repositories).

| Keys | Arm | Expected cells reached | Leave cells proposed | M1 accepted | M1 loop-only |
|---|---|---|---|---|---|
| owner (4 projects) | no skill | 48/102 | 33/96 | 8/24 | 18/24 |
| | before the grid | 47/102 | 34/96 | 9/24 | 13/24 |
| | v2 | 44/102 | 23/96 | 12/24 | 3/24 |
| | **v3** | 44/102 | 28/96 | 9/24 | 1/24 |
| bug-grounded (6 repos) | no skill | 116/198 | 0/6 | 5/36 | 20/36 |
| | before the grid | 119/198 | 1/6 | 3/36 | 23/36 |
| | v2 | 108/198 | 0/6 | 6/36 | 1/36 |
| | **v3** | 116/198 | 0/6 | 7/36 | 5/36 |

On the unit and piece bring-out cells the keys expect, v3 recovers much of what v2 lost — jaffle-shop
unit 2 → 4/6 and piece 3 → 5/6, tps-demo piece 3 → 5/6, subscription-payments unit 2 → 4/6 — but stays
below no skill on most (miniflux unit 0/6 against 6/6; the private backend piece 1/6 against 5/6).

What it says:
- **v3 undoes v2's loss on the bug-grounded keys** (108 → 116, level with no skill) — **and does not
  move the owner keys** (44/102 for both; counting any proposal — see the correction above). On the independent measure, no version of the skill has
  yet reached more expected cells than no skill.
- **The bug keys lean toward bring out by construction** ("cheapest cell"), so any change toward
  harnesses reads well on them. The owner keys are the check, and they did not move.
- **miniflux unit 0/6 is a mismatch the skill gets right**: miniflux has a large unit suite; the key
  says `propose` because bugs escaped it, which asks for *more tests* — task work the skill rightly
  does not propose. A key that cannot be met by a handle is a key question.
- **Costs**: on Sonnet, M1 is loop-only again in 6/30 maps (3/30 with v2); leave cells proposed rise
  23 → 28 on the owner keys. Both are within or near judge noise.
- **What has held through every version**: M1 off the environment (v2/v3: 10/120 maps loop-only,
  against 38/60 without the skill and 36/60 before the grid), and witness at operation level where
  keys ask for it.

## Against owner-filled answer keys (2026-11-27)

Four projects whose owner filled the key — motu and assay (public; assay's key merges the owner's
sketch with a blind bug-grounded draft), and two private projects (a Next.js + Supabase app and its
Supabase backend, scored in their own repositories). Neutral prompt, Sonnet and Haiku, three runs
each, for the skill before the grid, the grid (v2), and no skill: 72 maps, each judged twice (M1 the
same in 63/72). Judge outputs for motu and assay: `evals/results/2026-11-27-owned/`.

| Arm | Model | Expected cells reached | Cells to leave, proposed anyway | M1 in an accepted cell | M1 loop-only |
|---|---|---|---|---|---|
| no skill | sonnet | 20/48 | 17/48 | 3/12 | 10/12 |
| no skill | haiku | 23/48 | 14/48 | 5/12 | 8/12 |
| before the grid | sonnet | 25/48 | 13/48 | 4/12 | 7/12 |
| before the grid | haiku | 20/48 | 13/48 | 5/12 | 6/12 |
| grid (v2) | sonnet | 19/48 | 14/48 | 6/12 | 2/12 |
| grid (v2) | haiku | 20/48 | 12/48 | 6/12 | 1/12 |

What holds across both kinds of key:
- **No arm reaches more of the expected cells** — 19 to 25 of 48 everywhere, within noise. The grid
  did not make maps match what the owner (or the bug history) asks for.
- **M1 off the environment holds again**: loop-only in 3/24 grid maps, 13/24 before, 18/24 without
  the skill. M1 in an accepted cell is slightly better with the grid (12/24 against 9/24 before,
  8/24 without) — within noise at this size.
- **The test gap repeats on the owners' keys**: where the owner expects a piece-level lab or harness,
  maps without the skill propose it and maps with it mostly do not (assay `piece × bring out`: grid
  2/6, no skill 6/6; the private backend `piece × bring out`: grid 0/6, no skill 5/6).
- **Where the skill aims, it lands**: operation-level reach in on the private backend (grid 5/6, no
  skill 2/6), operation-level bring out on assay (grid 6/6, before 2/6, no skill 3/6).
- **Most "leave" violations are one key against every arm**: on the private app, every map in every
  arm proposes `loop` (18/18) where the owner wrote `leave`, and the grid proposes
  `journey × reach in` 5/6 there. When all arms disagree with a key, the key is the first suspect —
  the repository has no per-agent environment and no unattended login.

## Against bug-grounded answer keys (2026-11-25)

The same 108 judged maps, scored against six answer keys drafted from each repository's fixed bugs
(evals/answer-keys/; 145 bugs across six repositories, every citation checked by
`evals/check_keys.py`, the classifications still to be checked by a person). A cell is expected
when ≥ 2 past bugs would have been caught there first.

| Arm | Model | Expected cells reached | M1 in an accepted cell |
|---|---|---|---|
| no skill | sonnet | 56/99 | 0/18 |
| no skill | haiku | 60/99 | 5/18 |
| before the grid | sonnet | 62/99 | 1/18 |
| before the grid | haiku | 57/99 | 2/18 |
| grid (v2) | sonnet | 60/99 | 4/18 |
| grid (v2) | haiku | 48/99 | 2/18 |

By expected cell, all models pooled (maps that reach it / maps whose key expects it):

| Expected cell | Before the grid | Grid | No skill |
|---|---|---|---|
| `piece × bring out` | 15/36 | 16/36 | **29/36** |
| `unit × bring out` | 6/24 | 6/24 | **19/24** |
| `operation × bring out` | 18/24 | 10/24 | 13/24 |
| `operation × reach in` | 20/24 | 16/24 | 8/24 |
| `operation × witness` | 10/18 | **12/18** | 1/18 |
| `journey × reach in` | 8/12 | 9/12 | 5/12 |
| `piece × reach in` | 7/12 | 6/12 | 5/12 |
| `piece × witness` | 0/12 | 0/12 | 0/12 |
| `loop` | 35/36 | 33/36 | 36/36 |

What it says:
- **Against where bugs were caught, the skill — either version — does no better than no skill** (counting any proposal, named or designed — see the correction above), and
  Haiku with the grid does worse. The grid did not move the skill toward the bugs.
- **The skill misses the cheapest cells — unit and piece tests.** Most past bugs in these
  repositories would have been caught by a test at the unit or piece level; maps without the skill
  propose those, maps with it mostly do not. The likely cause is the skill's own rule that a test or
  CI step "is not a handle" (principles.md) — so it proposes no harness that would make a piece
  testable either (miniflux's handlers have no fake store; tps-demo has no tests at all).
- **Where the skill aims, it delivers**: `operation × witness` 12/18 against 1/18 without it, and more
  reach in at operation and journey level.
- **Nobody proposes `piece × witness`** (what a scene, page or handler group did), in any arm.
- **M1 rarely lands where the most bugs were** (≤ 5/18 in every arm) — the task mix reads commit
  volume, not where things broke.

What it does not say: the keys measure **bug-catching**, not the friction an agent hits while
working (a login it cannot pass, a state it cannot reach), which leaves no commit behind and is
the skill's first purpose. "Cheapest cell" also leans toward bring out by construction. Read this as
one half of the picture; the owner-filled keys (motu, assay, the two private projects) are the
other.

## Neutral prompt, three runs per cell, judge checked (2026-11-25)

The 2026-11-24 runs left two doubts: the task prompt listed the reach-in steps ("launch it, log in,
reach a state, act, see the result") for every arm, and the judge counted every proposal, so one
script runner with eight scripts outweighed one lab. This pass removes both and repeats each run
three times: six scenarios × Sonnet and Haiku × 3 runs, for the skill before the grid (`0fecb1d`), the
grid (v2, `c5caeea`), and no skill — 108 maps. Shares are over the **cells each map reaches**, each
cell counted once per map, scripts included.

| Arm | Model | Maps | Cells by way: Bring out · Witness · Reach in | by level: Unit · Piece · Operation · Journey | Cells per map | M1 loop-only |
|---|---|---|---|---|---|---|
| no skill | sonnet | 18 | 74% · 3% · 22% | 26% · 38% · 15% · 19% | 3.5 | 10/18 |
| no skill | haiku | 18 | 61% · 11% · 26% | 23% · 23% · 32% · 19% | 4.2 | 10/18 |
| before | sonnet | 18 | 35% · 19% · 44% | 14% · 25% · 40% · 18% | 4.5 | 14/18 |
| before | haiku | 18 | 28% · 23% · 48% | 19% · 23% · 43% · 13% | 4.6 | 9/18 |
| **grid (v2)** | sonnet | 18 | 34% · 23% · 41% | 12% · 30% · 40% · 16% | 4.5 | **1/18** |
| **grid (v2)** | haiku | 18 | 25% · 29% · 44% | 6% · 27% · 46% · 18% | 3.2 | **0/18** |

Expected behaviours (keywords): grid 211/216, before 204/216, no skill 112/216. Author tools
proposed where they do not fit: 0 in all 108 maps.

**How far to trust the judge**: every map judged twice — M1's cell the same in 90/108 (83 %), cells
reached overlapping 0.82 (Jaccard), way shares differing by 0.10 at most on average. **Differences
under ~10 points in a share are judge noise**, before any run-to-run noise.

What this pass changes in the 2026-11-24 reading:
- **"Reach in dominates" was mostly the measurement.** With the neutral prompt and cells counted once,
  the grid's Sonnet maps are 41 % reach in, not 66 %. Both skill versions sit around 41–48 % — the
  difference between them is within judge noise. Without the skill, maps are ~75 % bring out: they
  propose test suites and little else. Whether ~45 % reach in is right for these repositories is a
  question for the answer keys, not for a target ratio.
- **The first milestone is the robust result**: loop-only (environments, launch) in 23/36 maps before,
  1/36 with the grid, 20/36 without the skill.
- **Witness**: 19–23 % of cells before, 23–29 % with the grid, 3–11 % without the skill. The grid's gain
  over the old skill is at the edge of judge noise; the skill's gain over no skill is not.
- **The level shift seen on 2026-11-24 does not hold**: journey was 42 % → 21 % under the old prompt;
  under the neutral prompt it is 13–18 % for both versions. That drop was the prompt's, not the grid's.
- **Breadth**: Haiku with the grid reaches fewer cells per map (3.2 against 4.6); Sonnet does not (4.5).
- **New problem — M1 is unstable run to run.** For the same repository and model, the three grid runs
  often put M1 in three different cells (CodeTriage on Haiku: unit × witness, journey × bring out,
  operation × witness). The judge agrees with itself on M1 83 % of the time, so most of that spread
  is the maps, not the judge. Reading the task mix is not yet reproducible.

Cost: grid $13.15 and old skill $11.11 for 36 runs each, no skill $3.66, judging 108 maps twice ~$4.

Next: the answer keys (evals/answer-keys/) and two human-labelled maps (evals/labels/) — then the
same judge outputs are re-scored against them at no cost.

## The evidence grid (2026-11-24)

The question: does the skill keep proposing the same thing — launch the app, log in, set up
environments — whatever the project? Keyword scores cannot see that, so `evals/judge.py` now has a
judge model (Sonnet) classify every proposal in every map by **way** (bring out · witness · reach in,
or loop-only) and **level** (unit · piece · operation · journey), plus the first milestone's cell and
whether motu or assay was proposed where the scenario says it does not fit.

Six scenarios (the five below plus subscription-payments, Next.js + Supabase + Stripe), Sonnet and
Haiku, one run per cell, same prompt for every version. Three versions of the skill: **before**
(`0fecb1d`), **v1** (the grid, `7939856`), **v2** (grades renamed, environments never a capability,
non-behavioural commits counted apart, `c5caeea`).

| Version | Model | Proposals in cells / loop-only | Bring out · Witness · Reach in | Unit · Piece · Operation · Journey | Busiest cell share | M1 on loop-only (envs, launch) |
|---|---|---|---|---|---|---|
| no skill | sonnet | 32 / 22 | 40% · 9% · 50% | 15% · 12% · 18% · 53% | 0.44 | 4/6 |
| no skill | haiku | 42 / 31 | 33% · 19% · 47% | 11% · 9% · 35% · 42% | 0.41 | 4/6 |
| before | sonnet | 45 / 15 | 28% · 17% · 53% | 4% · 15% · 37% · 42% | 0.45 | 4/6 |
| before | haiku | 47 / 16 | 8% · 17% · 74% | 8% · 12% · 36% · 42% | 0.49 | 3/6 |
| v1 | sonnet | 42 / 13 | 30% · 14% · 54% | 2% · 19% · 45% · 33% | 0.39 | 2/6 |
| v1 | haiku | 27 / 11 | 33% · 29% · 37% | 3% · 33% · 51% · 11% | 0.45 | 0/6 |
| **v2** | sonnet | 33 / 13 | 12% · 21% · 66% | 3% · 27% · 48% · 21% | 0.39 | **0/6** |
| **v2** | haiku | 33 / 17 | 27% · 21% · 51% | 9% · 27% · 42% · 21% | 0.34 | **0/6** |

M1's cell, all twelve skill maps: **before** — loop-only 7, journey × reach in 4, operation × reach in 1.
**v2** — piece 7 (bring out 4, reach in 3), operation 3 (reach in 2, witness 1), journey × reach in 2.

Keyword scores (the existing expected behaviours) did not regress: before 66/72, v1 69/72, v2 70/72
(no skill 46/72); a roadmap in 12/12; cited `file:line` resolving 93 % before and after.

What moved, what did not:
- **M1 follows the project now.** No v2 map starts with an environment or a launch-only milestone
  (7/12 before). The first milestone lands on the level the task mix points to — piece for the
  screen-heavy and game repos, operation for the backend ones — and journey × reach in only twice.
- **The level axis moved**: journey fell from ~42 % of proposals to 21 %; piece rose from ~13 % to 27 %.
  The busiest cell's share fell from 0.45–0.49 to 0.34–0.39.
- **The way axis moved less than hoped.** Witness rose modestly (17 % → 21 %), but reach in is still
  half to two thirds of the proposals, and on Sonnet more than before (53 % → 66 %): much of the
  piece row is filled by *reaching* the piece in the running app (a screenshot of a screen) rather
  than bringing it out. The prompt itself asks to "launch it, log in, reach a state, act, see the
  result" for every arm; whether that wording, not the skill, holds reach in up is the next thing to
  test (a neutral prompt, three runs per cell).
- **Fewer, more targeted proposals**: ~33 per six maps instead of ~46, and 6.2 usage examples per
  map instead of 8.4 — "a gap is not a proposal" works, and costs some breadth.
- **The author's tools**: proposed where they do not fit — 0 in every run, every version. Also
  never proposed where assay plausibly fits (subscription-payments): agents built the ledger pattern
  from the project's own seams instead. Under-recommending is the safe failure; it is reported,
  not corrected.
- **Noise**: one run per cell, and the judge is a model — it occasionally mislabels a stub as a
  witness. Read differences of a few points as noise; the M1 shift (7/12 → 0/12) is the robust one.

Cost: about $4 per twelve skill runs, ~$1.40 for twelve baseline runs, ~$1 to judge 48 maps.

What the first grid pass (v1) taught, fixed in v2: agents read the grade `seen` as "I ran it" (it
collided with the map's `(seen)` provenance marker) and `declared` as "written in the README"; and
four of six Sonnet maps promoted the per-run environment into a capability and its M1. Grades
became `observed` · `asserted` · `gated`, and an environment became the foundation of the milestone
whose demo needs it, never a capability.

## Keyword evals (2026-11-17)

`./evals/run.sh --model sonnet --model haiku` — five public repositories, one per shape, pinned to a
commit; each run is the Claude Code CLI headless, read-only, on the same task, **with the skill and
without it**. Scoring is format-agnostic (expected behaviours as keyword groups anywhere in the
output), plus runnable usage examples (`$ ` lines), a roadmap, and cited `file:line` that resolve.
One run per cell — expect some variance.

| Scenario | Model | With skill | Baseline | Usage examples (skill / base) | Roadmap (skill / base) | Evidence resolving (skill) |
|---|---|---|---|---|---|---|
| CodeTriage (Rails) | sonnet | 7/7 | 5/7 | 13 / 0 | yes / no | 41/46 |
| CodeTriage (Rails) | haiku | 7/7 | 6/7 | 8 / 0 | yes / no | 66/67 |
| miniflux (Go) | sonnet | 5/6 | 2/6 | 19 / 0 | yes / no | 20/26 |
| miniflux (Go) | haiku | 6/6 | 3/6 | 9 / 0 | yes / no | 51/65 |
| vue-realworld (SPA) | sonnet | 6/6 | 5/6 | 9 / 0 | yes / no | 40/44 |
| vue-realworld (SPA) | haiku | 6/6 | 5/6 | 2 / 0 | yes / no | 56/57 |
| jaffle-shop (dbt) | sonnet | 4/5 | 3/5 | 3 / 0 | yes / no | 54/57 |
| jaffle-shop (dbt) | haiku | 5/5 | 4/5 | 5 / 0 | yes / no | 35/35 |
| tps-demo (Godot) | sonnet | 6/6 | 4/6 | 13 / 0 | yes / no | 94/97 |
| tps-demo (Godot) | haiku | 5/6 | 3/6 | 9 / 0 | yes / no | 80/80 |
| **Total** | | **57/60 (95%)** | **40/60 (67%)** | **~9 per map / 0** | **10/10 / 0/10** | **537/574 (94%)** |

- The skill works on Haiku as well as Sonnet: ≥ 5/6 everywhere, a roadmap and resolving evidence every time.
- The gap is widest where depth matters (environment isolation, persona login, profiling and
  debugging, the live console of a game) and smallest on a SPA, where any agent names Playwright and
  MSW — there the difference is that the skill designs runnable handles instead of naming tools.
- Cost: about $4 for the 20 runs; a skill run takes ~2–2.5× the time of the plain prompt.
- The keyword score understates the gap (naming a tool counts like designing a handle); a stricter,
  judge-based "proposed as a handle vs merely mentioned" check is the next improvement.
- lobsters was dropped: its own agent files forbid all LLM contributions, and the agents rightly
  declined to map it. CodeTriage replaced it.
