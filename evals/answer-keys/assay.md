# Answer key — assay

**Repository:** https://github.com/Scorbutics/assay @ `0ac3b0f8fb81` · **Shape:** TypeScript effect-ledger CLI for Supabase backends (declarations, drive, gate) — developer tooling whose input is another project

**Author tools fit** (from `scenario.json`, used to flag a misfit proposal): none; using it on itself is borderline. Correct it there if wrong.

**Filled by:** merged — the owner's sketch and a bug-grounded draft (an agent blind to the skill, 17 fixed bugs below) · 2026-11-27
**M1 accepted:** `piece × bring out`, `operation × bring out`

How each row was decided: the owner's firm value stands unless the bug evidence contradicts it (then
`either`); where the owner was unsure, the bug evidence decides; both unsure is `either`. M1 is the
merged `propose` cells with the most bugs (4 each). The bug evidence is weak to moderate: five weeks
of history, one author, five bugs from one end-to-end session (2669bbe).

| Cell | Expect (`propose` · `leave` · `either`) | Why — owner, then bug evidence |
|---|---|---|
| `unit × bring out` | either | Owner: leave — "unit tests are fine". Bugs: propose — 6 fixed bugs had a unit test as their cheapest catch (dbb840a, cc5e9b6, e5dfa01, 2669bbe ×2, ee9d910). They contradict: either. |
| `unit × witness` | leave | Owner: leave — unit tests are fine. Bugs: silent. Owner stands. |
| `unit × reach in` | leave | Owner: leave (structural, as in the other keys). Bugs: silent. Owner stands. |
| `piece × bring out` | propose | Owner: unsure. Bugs: propose — 4 bugs, two of them wrong clean verdicts (fd661a4, 4145863, d054c39, eb30bae). |
| `piece × witness` | propose | Owner: unsure. Bugs: propose — 1 bug that destroyed consumer data: declare --write deleted every hand-written why: (2669bbe). |
| `piece × reach in` | either | Owner: unsure. Bugs: silent. |
| `operation × bring out` | propose | Owner: propose — "feed assay and observe the result". Bugs: propose — 4 bugs (76c5098, ee8ba24, 2669bbe, cf66c04). Agree. |
| `operation × witness` | propose | Owner: propose. Bugs: propose — 2 scratch-database faults (9174f9f, 2669bbe). Agree. |
| `operation × reach in` | propose | Owner: propose. Bugs: silent. Owner stands. |
| `journey × bring out` | either | Owner: unsure. Bugs: leave as "structural" — but that follows from a definition (journey = the real consumer), not from assay: driving the whole chain on a sample project is conceivable. Treated as either. |
| `journey × witness` | either | Owner: unsure. Bugs: silent (several bugs were discovered here, none needed it as their cheapest catch). |
| `journey × reach in` | either | Owner: unsure. Bugs: silent (where 2669bbe, fd661a4, dbb840a surfaced, not their cheapest catch). |
| `loop` | propose | Owner: unsure — "a lib alone has no loop"; it has one: drive needs a local Supabase stack. Bugs: propose — ≥ 8 bugs from Deno vs Node, CI vs local, consumer install layout, missing cron schema, GoTrue containers. |

## Evidence — fixed bugs

| Commit | What broke | Cheapest cell that would have caught it | Why that cell |
|---|---|---|---|
| `fd661a4` | `invariants`: `client.connect()` rejecting exited 1 ("contradicted") rather than 2 ("could not run"), so attest showed FAIL | `piece × bring out` | Run the subcommand with an unreachable DB URL and assert the exit code. No database is needed. |
| `76c5098` | drive, scratch and empty-state hardcoded the origin project's tables, project name and placeholder regex. An unresolved placeholder came back 400, which counted as "handled correctly" (a wrong pass). | `operation × bring out` | Only a second fixture project, with its own schema and vocabulary, exposes assumptions about the first one. |
| `9174f9f` | The scratch clone (`pg_dump \| psql`) silently dropped table rows and 3 of 100 FKs, and later operations then looked broken | `operation × witness` | Clone a fixture DB and compare table and FK counts against the source. The fix adds exactly that comparison. Needs a database. |
| `4145863` | empty-state minted a new account's token but sent the driving account's, so the sweep passed the INSERT branch without reaching it | `piece × bring out` | A stub route that echoes the caller's identity would show the wrong account. No test existed. |
| `dbb840a` | The seam read only `Deno.env` for its own Supabase host, so on Node it recorded its own DB calls as undeclared outbound calls (a false ERROR) | `unit × bring out` | Unit-test the host lookup in a Node runtime. The fix's Deno test passed with the fix reverted. |
| `cc5e9b6` | `rpc-map` emitted functions in pg_proc order, so two runs on the same schema gave byte-different files and the staleness check failed on every run | `unit × bring out` | Feed shuffled rows to the emitter and assert identical output. |
| `ee8ba24` | `import.meta.main` was false when the command was reached through a symlinked `node_modules` path, so `check --json` printed nothing | `operation × bring out` | Invoke the CLI through a symlinked install in a fixture layout. It passed locally and failed in CI. |
| `e5dfa01` | Every command module called a bare `main()`, so importing a helper ran the command, opened a pg connection and failed CI with an unhandled rejection | `unit × bring out` | Import each command module in a test and assert there are no side effects. |
| `2669bbe` (a) | `normalizePath` collapsed `client_invoices` to `{id}`, so the replay node never matched and the call reached the real provider | `unit × bring out` | A pure function. The existing `template_test.ts` covered `normalizePath` but had no snake_case word case, so it missed the bug. |
| `2669bbe` (b) | `storePayload` ignored the sink's 400 response, so the ledger said `intercepted:store` while nothing was stored (a false clean record) | `unit × bring out` | A fake sink returning 400 shows the ignored response. |
| `2669bbe` (c) | `declare --write` deleted every hand-written `why:` field and reordered the consumer's declaration file | `piece × witness` | Run `declare --write` on a fixture `operations.json` and diff what assay wrote. This destroyed consumer content. |
| `2669bbe` (d) | scratch moved Postgres but left GoTrue on the working DB, so created users landed in the wrong database and FKs rejected the inserts. `on` was also not re-runnable. | `operation × witness` | Run scratch on, then create a user, against a local stack, and check which database holds the row. |
| `2669bbe` (e) | `verify` spawned `<root>/assay/src/commands/*.ts`, which did not exist after the submodule move, so tier 2 never ran | `operation × bring out` | Run `verify` in a fixture consumer with the packaged layout. |
| `cf66c04` | tier1/expect spawned `static` through a consumer-repo path, so the step failed with "Module not found" while the exit code came from the other steps | `operation × bring out` | Same layout fault as (e). A partially run gate looked like a working one. |
| `ee9d910` | The seam's `find` took the first node for a target, so a scoped replay could silently get the unscoped CI fixture | `unit × bring out` | Call `find` with two nodes in both orders. |
| `d054c39` | The seam imported `node:async_hooks` at top level, so a Vite browser build of a consuming page failed | `piece × bring out` | Bundle the seam alone for a browser target. The fix adds a browser-substitute test. |
| `eb30bae` | `check` had no finding for a refused statement, so a corpus containing `permission denied for table members` passed with 0 errors | `piece × bring out` | Run `check` on a fixture corpus line with a privilege error. This was a wrong clean verdict. |

## Excluded candidates

057bbee — publish-from-CI failures (JSR self-reference resolution, a Deno lib type error that blocked `deno publish`): release/CI packaging, not tool behaviour
345b86b — release workflow fixes (install before publish, drop `baseUrl`): CI-only
31e2cc2 — dropped the deno lockfile that blocked releases: release/dependency tooling
