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

## 4. Revise — and present again

Update the map: change, merge, move or drop cards; add a **Revisions** entry (what changed and
which remark caused it); re-render the page. Present it again if the changes are more than
cosmetic. Repeat 3–4 until the human has no open remark.

## 5. Accept — the explicit go

Acceptance is an explicit statement from the human — "go for M1", "build these" — naming what to
build; milestones from the map's Roadmap are the natural unit.
Restate it as an ordered list (dependencies first: the primitive before its scripts, the fence
before the handle that needs it) with the decisions it rests on, and record it in the map under
**Accepted plan**. Silence, or approval of part of the map, is not acceptance of the rest.

## 6. Implement — one handle at a time, proven

For each accepted handle, in order:
1. build it, small, out of feature code, with its fence;
2. **run its usage example for real** and show the output — the card's usage block is the test;
3. **keep it alive**: add that usage example to the `doctor` script and to a CI job, so the handle
   fails loudly the day the app changes under it;
4. **configure the harness**: its permission (allow · ask · deny) and any guard its fence relies
   on (a hook, a wrapper) — so an agent can use it unattended;
5. move its status in the map (missing → exists), update the "How to reach the app" section of
   the agent file;
6. re-render the page so the human sees the picture fill in.

If building shows the plan was wrong (a handle needs something the map missed, a primitive is
cheaper than three scripts promised), stop and bring it back to step 3 — do not quietly redesign.

## What the human should never have to do

- Ask twice for an answer to a remark.
- Read the whole map to find what changed — the Revisions entry says it.
- Discover a handle was built that was not in the accepted plan.
