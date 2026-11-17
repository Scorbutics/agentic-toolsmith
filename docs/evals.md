# Eval results (2026-11-17)

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
