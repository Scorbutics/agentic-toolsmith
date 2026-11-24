# Eval results

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
