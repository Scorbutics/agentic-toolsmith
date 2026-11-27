# Eval results

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
- **Against where bugs were caught, the skill — either version — does no better than no skill**, and
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
