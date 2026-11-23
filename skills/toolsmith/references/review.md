# The review loop — plan, review, revise, accept, implement

A map is a **plan**, not a deliverable. Nothing gets built until the human has seen it, said what
is wrong, had every remark answered, and accepted a revised plan. This loop is where most of the
skill's value comes from: the human's remarks routinely change the plan (a bespoke flag becomes a
script, a handle moves to another layer, a card that looked useful turns out to be a test of the
wrong thing) — and an agent that builds before that loop builds the wrong things well.

## 1. Plan — write the map

Map mode, as in [map.md](map.md). The plan is the candidate cards; everything else in the map
(points, tools in place, the picture) is there so the human can judge them.

## 2. Present — the review page

Render the map into a page the human can act on, not a wall of Markdown:

```sh
$ python3 <skill>/scripts/review_page.py map.md -o review.html
review.html: 9 cards, 13 tools in place, 3 questions
```

One self-contained HTML file (no server, no network): the app with its handles by category, the
Lab drawn around the runtime, every card with its usage, the questions, the tools in place. The
human marks each item right / wrong / unsure, types notes and answers, and copies a Markdown
feedback block back to you.

Hand it over the best way the host allows: publish it as a page if your environment can
(an artifact, a static host the human already uses), otherwise give the file's absolute path to
open in a browser. Say in one line what to look at first (the cards) and how to send feedback
back (the copy button).

Then **stop and wait.** Do not start building while the review is open.

## 3. Answer every remark

When feedback comes back, answer **each** remark — every wrong, every unsure, every note and
question — individually, before changing anything. For each one:

- **What it is, concretely.** The human often marks "unsure" because the card did not say what
  would be built: a new CLI? an engine API? a script? where? Say it plainly, with the file or
  layer it lands in.
- **Why it was proposed** — the gap it closes, the evidence, the exemption that justified a
  dedicated handle instead of a script.
- **Your recommendation now**, which may be to drop it, merge it, move it to another layer or
  turn it into a script. Agreeing with a "wrong" is fine; defending a card is fine too, with the
  reason — but never silently.
- **The change to the plan**, if any.

Look across the remarks for **patterns** — three "why not a script?" are one rule the map broke,
not three cards. Name the pattern; it is often a change to how the next map is written.

Watch for **conflicts between layers**: two maps (an engine and its game, a runtime and its app)
proposing the same primitive. Keep one, at the lowest layer that can host it; the upper layer
contributes scripts and its own gate.

The human's answers to the grill questions are **decisions**: record them in the map's
**Decisions** section with the date, and apply them.

**Decisions outlive the map.** Write each one also to a project-level file the next agent reads
first — `toolsmith/decisions.md` at the root of the project, or of the parent folder when the
decision spans several repos (an engine and its game) — one dated line each, with the map it came
from. A decision recorded only in one map is lost to the next map of a related repo, which will
re-open it.

## 4. Revise — and present again

Update the map: change, merge, move or drop cards; add a **Revisions** entry (what changed and
which remark caused it); re-render the page. Present it again if the changes are more than
cosmetic. Repeat 3–4 until the human has no open remark.

## 5. Accept — the explicit go

Acceptance is an explicit statement from the human — "go for M1", "build these" — naming what to
build; milestones from the map's Roadmap are the natural unit.
Restate it as an ordered list (dependencies first: the primitive before its scripts, the fence
before the handle that needs it) with the decisions it rests on, and record it in the map under
**Accepted plan**; set **Status:** `accepted` (dated) on those cards and milestones. Silence, or approval of part of the map, is not acceptance of the rest.

## 6. Implement — one handle at a time, proven

For each accepted handle, in order:
1. build it, small, out of feature code, with its fence;
2. **run its usage example for real** and show the output — the card's usage block is the test;
3. **keep it alive**: add that usage example to the `doctor` script and to a CI job, so the handle
   fails loudly the day the app changes under it;
4. **configure the harness**: its permission (allow · ask · deny) and any guard its fence relies
   on (a hook, a wrapper) — so an agent can use it unattended;
5. move its card to **Delivered handles** with **Status:** `delivered` and a **Verified:** line at
   the level actually reached — `implemented`, `tested` or `demoed`, with the evidence and any
   caveat ("live demo deferred: <why>"); set the milestone's Status and Verified the same way, and
   never mark it demoed unless its Demo ran end to end and showed its Expect. Update the "How to reach the app" section of
   the agent files every harness loads at startup — keep **one source**: the section in `AGENTS.md`
   (read by GitHub Copilot, Codex, Cursor), imported from `CLAUDE.md` with `@AGENTS.md` (plus a
   one-line pointer at its top), and referenced from `.github/copilot-instructions.md`. The section
   says the command, what it does and refuses, and "use it before writing an ad-hoc script"; make the
   entry point list itself (`<tool>` with no argument prints every script and its usage); allow it
   in the harness's permissions; where an agent reaches for the raw path mid-task (`psql`), a
   pre-tool hook can point it to the handle;
6. **prove a future session finds it**: start a fresh, headless agent session in the project with
   an ordinary request the handle serves, and **no hint about the tooling** ("what time does the app
   think it is?", "how many members can a member see?"). It passes when the session reaches for the
   handle on its own, respects its fences, and does not fall back to the raw path. A handle the next
   session cannot find does not exist. Then run it **from a fresh git worktree** of the branch — no
   `node_modules`, no submodules, the shared stack still running — because parallel agents work
   there: discovery that only works in the main checkout (a CLI run inside a submodule, a path to
   the human's folder) is a handle half the agents cannot reach;
7. re-render the page so the human sees the picture fill in. When you hand it over after a build,
   say what was delivered and how far each piece was proven; ask for a go only on a milestone
   still `proposed` — never on one already accepted or delivered.

If building shows the plan was wrong (a handle needs something the map missed, a primitive is
cheaper than three scripts promised), stop and bring it back to step 3 — do not quietly redesign.

## What the human should never have to do

- Ask twice for an answer to a remark.
- Read the whole map to find what changed — the Revisions entry says it.
- Discover a handle was built that was not in the accepted plan.
