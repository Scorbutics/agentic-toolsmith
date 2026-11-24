# Scoped runs — through a task, for a capability

Both scopes follow the same process as a whole-app map (SKILL.md, "Scopes"),
on a narrower survey. Both produce **durable** handles only — never tooling for one task.

## Before anything

Read `toolsmith/decisions.md` (the project's and its parent folder's — reading those is part of
the job, not a step outside the project) and the project's existing map. A scoped run **adds to**
that map: new cards, new roadmap entries, new decisions. Every new card serves a **capability**
of the map — an existing one, or a new row in its Capabilities table with this run as evidence. If there is no map yet, create one with
only what this run surveyed, and say it is partial.

## Through a task — `/toolsmith task "<fix or feature>"`

1. **Trace the task** to the code that produces the behaviour, the repo that owns it, and how a
   change reaches the running app (ladder.md, step 0).
2. **List the loop this task needs**: reach the state it is about, act there, see the result,
   check it, reset, repeat. Each step that today needs a human, a guess or minutes of setup is a
   gap. Place the task on the evidence grid (grid.md): **which level** it changes, and for that
   row, which way gives the verdict cheapest — a piece lab may show every state of the screen
   without a launch; an operation witness may prove what the fix wrote. Reaching the live app is
   one of three ways, not the default. If the task writes or sends anything, its loop needs a
   witness cell whatever else it uses.
3. **Generalise before proposing.** For each gap, the card answers for *the class of task*, not
   this one: not "seed an order in state X for this bug" but "`seed <scenario>` and a scenario
   library". If the only thing that would help is specific to this one task, it is inline work
   for the coding agent — write it in the report as such, not as a card.
4. **Check the map first**: an existing capability, card or milestone may already cover the gap —
   then this task is evidence for its priority (`Seen in: task "<…>"`), not a new card. A gap no
   capability covers is a new capability first (what the agent could not do), then its card.
5. **Rank** by how often tasks like this one come back, and by whether the gap blocks the task
   now (a human-only step) or only slows it.
6. **Review** (inline for up to three cards), then: the human decides what to build *before* the
   task; Toolsmith builds and proves those, writes the rest to the roadmap, and hands over. It does
   not do the task.

## For a capability — `/toolsmith want "<capability>"`

1. **Restate the capability as an outcome** ("read and change rows of the local DB from the
   shell, as the agent, safely") — it becomes, or joins, a row of the map's Capabilities, and the
   handle is the means to it.
2. **Survey only the points it touches** — for DB access: state stores, identity and access
   policies, environments, fences, the local stack.
3. **Find what exists**: a CLI the stack ships (`psql`, `supabase`, `rails dbconsole`), a script
   that half does it, a service layer the project requires for data access.
4. **Design the durable handle** with every card line — Is, usage sized for an agent, Fence,
   Parallel, Permission — and **challenge the request** when the literal ask is the unsafe or
   less useful shape. A local production copy is **the owner's decision, not a blocker** — ask once,
   record it (a project config the handle reads, cited in `toolsmith/decisions.md`), and fence what
   actually leaves the machine (live mail, production URLs, schedulers) rather than the data. Raw
   `psql` with policies bypassed and unbounded output is still worse than
   `app-dev run sql "<query>"`, read-only by default, on the agent's own environment, writes behind
   an explicit flag, output paged. Say why, and offer the literal version only if the human still
   wants it after the reason.
5. **When the answer is a script** under a primitive the map already has (or proposes), it is not
   a card: write it as a **row of that primitive's script table**, with its usage and Needs, and
   say which milestone it joins. The mandatory card lines apply to cards only.
6. **Review** (inline), build after the go, prove with the usage example, keep it alive.
