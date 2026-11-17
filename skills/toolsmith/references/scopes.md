# Scoped runs — through a task, for a capability

Both scopes follow the same process as a whole-app map (SKILL.md, "Scopes"),
on a narrower survey. Both produce **durable** handles only — never tooling for one task.

## Before anything

Read `toolsmith/decisions.md` (the project's and its parent folder's — reading those is part of
the job, not a step outside the project) and the project's existing map. A scoped run **adds to**
that map: new cards, new roadmap entries, new decisions. If there is no map yet, create one with
only what this run surveyed, and say it is partial.

## Through a task — `/toolsmith task "<fix or feature>"`

1. **Trace the task** to the code that produces the behaviour, the repo that owns it, and how a
   change reaches the running app (ladder.md, step 0).
2. **List the loop this task needs**: reach the state it is about, act there, see the result,
   check it, reset, repeat. Each step that today needs a human, a guess or minutes of setup is a
   gap.
3. **Generalise before proposing.** For each gap, the card answers for *the class of task*, not
   this one: not "seed an order in state X for this bug" but "`seed <scenario>` and a scenario
   library". If the only thing that would help is specific to this one task, it is inline work
   for the coding agent — write it in the report as such, not as a card.
4. **Check the map first**: an existing card or roadmap milestone may already cover the gap — then
   this task is evidence for its priority (`Seen in: task "<…>"`), not a new card.
5. **Rank** by how often tasks like this one come back, and by whether the gap blocks the task
   now (a human-only step) or only slows it.
6. **Review** (inline for up to three cards), then: the human decides what to build *before* the
   task; Toolsmith builds and proves those, writes the rest to the roadmap, and hands over. It does
   not do the task.

## For a capability — `/toolsmith want "<capability>"`

1. **Restate the capability as an outcome** ("read and change rows of the local DB from the
   shell, as the agent, safely").
2. **Survey only the points it touches** — for DB access: state stores, identity and access
   policies, environments, fences, the local stack.
3. **Find what exists**: a CLI the stack ships (`psql`, `supabase`, `rails dbconsole`), a script
   that half does it, a service layer the project requires for data access.
4. **Design the durable handle** with every card line — Is, usage sized for an agent, Fence,
   Parallel, Permission — and **challenge the request** when the literal ask is the unsafe or
   less useful shape: raw `psql` on a production-copy database with policies bypassed is worse than
   `app-dev run sql "<query>"`, read-only by default, on the agent's own environment, writes behind
   an explicit flag, output paged. Say why, and offer the literal version only if the human still
   wants it after the reason.
5. **When the answer is a script** under a primitive the map already has (or proposes), it is not
   a card: write it as a **row of that primitive's script table**, with its usage and Needs, and
   say which milestone it joins. The mandatory card lines apply to cards only.
6. **Review** (inline), build after the go, prove with the usage example, keep it alive.
