# Roadmap — compile, order, prioritise

Cards are a list; a team builds a roadmap. After proposing cards, run one more pass over them:

1. **Compile.** For each card, write what it builds on. A base used by two or more cards is a
   **foundation** — built once, listed first. A card that turns out to be "a foundation plus a
   snippet" becomes a script under it. This is the pass that catches a missing primitive: when
   four cards each need "a way to run code in the live app", that is one foundation, not four
   handles.
2. **Order.** Draw the dependencies: foundations → handles → scripts; a fence before the handle
   that needs it.
3. **Rank.** Mark each foundation and handle by what it unlocks — categories it fills, human-only
   steps it removes, how often the project's typical tasks need it — against its cost. The ones
   that unlock the most are **keystones**.
4. **Cut into milestones.** **M1 is the walking skeleton**: the smallest set that gives an agent an
   unattended loop — launch, reach a state, see it, check it. Each milestone ends on a **demo the
   agent can run end to end** once it is built. Later milestones add reach and depth. Cards in no
   milestone are listed as deferred, with why.

The human accepts milestones, not a pick list: "go for M1" is a complete instruction.
