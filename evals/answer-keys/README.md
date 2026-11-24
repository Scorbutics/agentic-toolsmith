# Answer keys

Two kinds, and each key says which in its **Filled by** line:

- **Bug-grounded** (codetriage, jaffle-shop, miniflux, subscription-payments, tps-demo, vue-realworld):
  drafted by an agent that never saw the skill or any map, from the repository's fixed bugs — for
  each bug, the cheapest cell that would have caught it before it shipped; a cell is `propose` with
  ≥ 2 such bugs (or 1 severe), `leave` only when it cannot exist in the project. Every row cites
  commits. `python3 evals/check_keys.py` checks the bookkeeping (each cited commit exists and
  predates the pin; counts agree with the rule) — **a person checks the bugs**: is each one a real
  behaviour bug, and is its cell right? That needs no knowledge of the code beyond the diff.
  What these keys measure: **where past bugs would have been caught**. Not friction an agent hits
  while working, which leaves no commit behind.
- **Owner-filled** (motu, assay, and private scenarios kept in their own repository): filled by the
  person who knows the project, from the bugs and the friction they remember.

What a good map *should* propose for each eval repository, written by a person who read the
repository, so that `evals/judge.py` can score maps against it instead of against a global ratio.
Without a key, "66 % of the proposals are reach in" cannot be called right or wrong: it depends on
the repository.

## Rules

1. **Fill a key before reading any map of that repository.** A key written after reading the skill's
   output grades the skill against itself.
2. **Not by the agent that changed the skill.** The skill and its exam must not come from the same
   mind. A key the skill's author fills is the right compromise; a key an agent filled is not one.
3. **Work from the repository at the pinned commit**: its code, tests, CI, README, issues and commit
   history. Cite what decided each row in **Why** (a path, a count, a commit subject).
4. **Score the project, not the skill's habits.** Ask: if an agent worked on this repository for a
   month, which cells would it actually need tooling in?

## The cells

A **level** is how much of the app is present when an agent gets its verdict: **unit** (a function,
a query), **piece** (a component, screen, scene, model, subcommand), **operation** (a request, job,
webhook, command, model build), **journey** (the whole app, as a user, across operations). A **way**
is where the agent stands: **bring out** (a piece run outside the live app: tests, a lab, a harness,
a mock), **witness** (a record of what the app wrote, sent or called), **reach in** (acting on the
running app). **loop** is the environments, launch and reset underneath, with no cell of its own.

## The values

- `propose` — a good map proposes at least one card here. A map that proposes nothing here misses.
- `leave` — a good map proposes nothing here (the cell is covered well enough, does not exist in this
  project, or would not repay its cost). A card here counts as a false positive.
- `either` — no strong view. Not scored. Use it freely: a key with five honest rows beats one with
  twelve guesses.

**M1 accepted** lists the cells a good first milestone may land in, or `any`.

The judge counts **cards**, not scripts run through a primitive. A cell is "reached" when at least
one card lands in it.

## Scoring

    python3 evals/judge.py runs/<a> runs/<b>

prints, per run and model, **expected cells reached** (`propose` rows hit), **cells to leave,
proposed anyway** (`leave` rows hit) and **M1 in an accepted cell**. Judge outputs are cached next
to each map, so filling or changing a key never needs new agent runs.
