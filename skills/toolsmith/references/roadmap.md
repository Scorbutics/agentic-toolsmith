# Roadmap — compile, order, prioritise

Cards are a list; a team builds a roadmap. After proposing cards, run one more pass over them:

1. **Compile.** For each card, write what it builds on. A base used by two or more cards is a
   **foundation** — built once, listed first. A card that turns out to be "a foundation plus a
   snippet" becomes a script under it. This is the pass that catches a missing primitive: when
   four cards each need "a way to run code in the live app", that is one foundation, not four
   handles.
2. **Order.** Draw the dependencies: foundations → handles → scripts; a fence before the handle
   that needs it. Record only **real** dependencies — "B needs A's primitive", "B's demo logs in
   with A's handle". Tracks that do not need each other stay independent, whatever their numbers.
3. **Rank.** Mark each foundation and handle by what it unlocks — categories it fills, human-only
   steps it removes, how often the project's typical tasks need it — against its cost. The ones
   that unlock the most are **keystones**.
4. **Cut into milestones.** **M1 is the walking skeleton**: the smallest set that gives an agent an
   unattended loop — launch, reach a state, see it, check it. Each milestone ends on a **demo the
   agent can run end to end** once it is built, and an **Expect** line: what the agent observes when
   the demo works, concrete enough to fail. Later milestones add reach and depth. Each milestone
   states **Depends on:** — the milestones it really needs, or `none`. Cards in no milestone move
   to Deferred handles, with why, and are listed under the roadmap's **Deferred**.

The human accepts milestones, not a pick list: "go for M1" is a complete instruction.

## Keeping status honest

The roadmap is read again after building; it must never overstate what was proven. Each milestone
and card carries a **Status** (`proposed` · `accepted` · `in progress` · `delivered`, or
`deferred`) and, once anything is built, a **Verified** level — `implemented`, `tested`, `demoed` —
with its caveats. A milestone whose demo did not run end to end is not demoed, however green its
tests: write `tested — <what passed>; live demo deferred: <why>`. Grammar: map-template.md.
