# Roadmap — compile, order, prioritise

Cards are a list; a team builds a roadmap. The roadmap is organised by **capability** — what the
agent cannot do today and will be able to do once a milestone lands (map-template.md,
Capabilities) — and the handles are the means. After proposing cards, run one more pass over them:

1. **Compile.** For each card, write what it builds on. A base used by two or more cards is a
   **foundation** — built once, listed first. A card that turns out to be "a foundation plus a
   snippet" becomes a script under it. This is the pass that catches a missing primitive: when
   four cards each need "a way to run code in the live app", that is one foundation, not four
   handles.
2. **Order.** Draw the dependencies: foundations → handles → scripts; a fence before the handle
   that needs it. Record only **real** dependencies — "B needs A's primitive", "B's demo logs in
   with A's handle". Tracks that do not need each other stay independent, whatever their numbers.
3. **Rank.** Rank the capabilities first — human-only steps they remove, how often the project's
   typical tasks need them (the task mix, not the shape's habit) — then, within each, the foundations and handles by what they unlock
   against their cost. The ones that unlock the most are **keystones**.
4. **Cut into milestones, by capability.** Each milestone delivers one capability, or a deeper
   step of one, and names it on its **Capability:** line; two capabilities that need nothing from
   each other are two independent tracks. **M1 is the walking skeleton of the most frequent kind
   of task** (the map's **Task mix:** line): the shortest unattended loop in which the agent changes
   that kind of code and gets a verdict that can fail. Where most commits change screens, that may
   be a piece lab with no launch at all; where most change what operations write, a witness loop on
   one operation; launching the whole app and logging in is M1 only when journeys dominate the mix,
   or nothing smaller can give the verdict. Its demo may still need a launch or a local stack — the
   capability is what the demo *proves*; the environment is a foundation it builds, never the
   capability itself. Write **Why first:** with the share of the mix it serves.
   Each milestone ends on a **demo the
   agent can run end to end** that proves the capability, not just that its handles run, and an **Expect** line: what the agent observes when
   the demo works, concrete enough to fail. Later milestones add reach and depth. Each milestone
   states **Depends on:** — the milestones it really needs, or `none`. Cards in no milestone move
   to Deferred handles, with why, and are listed under the roadmap's **Deferred**; so is a
   capability no milestone delivers. A card no capability needs is not on the roadmap at all.

The human accepts milestones, not a pick list: "go for M1" is a complete instruction.

## Keeping status honest

The roadmap is read again after building; it must never overstate what was proven. Each milestone
and card carries a **Status** (`proposed` · `accepted` · `in progress` · `delivered`, or
`deferred`) and, once anything is built, a **Verified** level — `implemented`, `tested`, `demoed` —
with its caveats. A milestone whose demo did not run end to end is not demoed, however green its
tests: write `tested — <what passed>; live demo deferred: <why>`. Grammar: map-template.md.
