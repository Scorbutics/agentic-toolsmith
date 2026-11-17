# Dry-run trials (2026-11-17) — draft v0, then named agent-interface

Four fresh agents ran draft v0 (survey + probe for real, grill and handles written down, not
executed) on four project shapes. Each got the skill and a realistic task, not the author's
reasoning. What each changed in v1:

| Project shape | Task | What it broke in v0 | Folded into v1 |
|---|---|---|---|
| Web app with accounts (Next.js + Supabase, prod-copy local DB) | Reminder 47 h ahead shows the wrong time | Safety boundary *inferred* missed a live mail key with a stub that falls back to live sending; task mapped to two features; existing handles (rollback SQL tests, preview mailer, test clock, state-URL renderer) absent from catalog; clock injectable but bypassed | Step 0 (trace the task), step 1b (verify the boundary, classify probes, one batched permission question), `attached` status, git status before/after, transaction scenario + state-URL renderer + safe-serve handles, timezone per runtime |
| Game engine + game in two repos (C++/Ruby, two render backends) | HP bar shifted on raylib, not SFML | Safety boundary lived in the consumer repo (run wrote crash files there); no notion of variants; readiness log line fired before the scene existed; signals triggered a crash handler; captures at native scale miss scaling bugs; build preset wrote into the human's output dir | Survey every place a run touches, variants per rung, readiness = state queryable, quit via the app, capture at human scale, A/B differential snapshot, boot-time script hook / crash replay, FIFO before socket, build isolation question, proceed without waiting when nothing blocks |
| Mobile app embedding a script runtime (Android) | 2 s freeze on first bag open | Assert assumed pass/fail (task is a duration); code lived in another repo; existing remote eval ran on a side thread and the probe crashed the game twice; no cold/first-time state | Assert = pass/fail · comparison · measurement, Profile handle, ownership + "how a change reaches the app" in Cycle, inject probes are Act with a Reset budget and stop-after-one-crash, console thread-model audit, embedded-runtime shape, cold states |
| CLI / dev tool whose input is another project | False "undeclared write" | One ladder where two loops exist (fixtures vs. real consumer); "state reachable" vs "bug reproduced" conflated; layered policies with no status; CI read as truth while 12 test files ran nowhere; agent-file commands never run (one had drifted) | Two-loop rule + dev-tooling shape, Reach 4a/4b split, `blocked (policy: <source>)`, "CI says what is gated", run the agent file's commands, shortened process for fast-suite CLIs, explain handle |

Common to all four: the question bank covered only 1–2 of each agent's 6 real questions. v1
adds the task, permission, ownership and "which output is correct?" questions that were missing.

## Map mode (2026-11-17)

One fresh agent ran map mode, read-only, on the web-app project above: 45 points across all
twelve classes, ~15 existing handles of which ~8 failed a criterion, 6 unknowns. Changes:

- **Classes**: points may belong to two classes (primary + cross-reference); **B13
  Configuration** added (env-selected drivers, flags, gates fit neither Process nor Identity).
- **Verbs**: **check** added — comparing against a declaration, including denial, had no verb
  ("see" understated an effect ledger's gate). Reset/isolation became the **loop** property,
  not a verb.
- **Evidence**: aggregate alike crossings into one point with a counting command (otherwise
  ingress alone exceeded 200 points); env files as classes, never values; SELECT-only queries on
  an already-running local stack count as read-only, so the grill stops asking what one query answers.
- **Diagram**: one node per class (worst colour, counts) — per-point nodes broke past ~20.
- **Tools climb several ways**: one "way up" label per tool misclassified both in-house tools
  (a ledger that also replays and clones; a lab that also records fixtures and reports
  coverage) → `tool → verb → way` rows.
- **Safety findings first**: the most valuable output, previously buried in a column.
