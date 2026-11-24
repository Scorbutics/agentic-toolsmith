# Answer key — codetriage

**Repository:** https://github.com/codetriage/CodeTriage @ `d1868f8` · **Shape:** Rails monolith with OAuth login, Sidekiq jobs and mailers

**Filled by:** bug-grounded draft — an agent blind to the skill, from the fixed bugs below · 2026-11-25 — verify the citations
**M1 accepted:** `operation × bring out`

I examined the 60 most recent non-merge commits reachable from `d1868f8` whose subject or body matched fix/bug/regression/revert/hotfix/crash/broken/wrong/error/issue #. Those commits run from 2020-05 to 2026-09. I kept 18 real behaviour bugs and excluded 42: 16 dependency bumps, upgrades or bisects (including the Puma memory bisect series), 8 lint/formatting commits, 6 typo/docs/template commits, 6 test-only or CI-only fixes, 4 debugging scaffolds, 2 preventive changes with no observed failure (`8b31eaa`, `331eadd`), 1 revert whose reason lives only in an off-repo PR comment (`9271b15`), 1 product decision (`12001f0`) and 1 duplicate fix (`f5e6f08`). The breakdown adds up to more than 42 because some commits fall into two groups. The evidence is moderate. 18 bugs is enough to rank cells, but the history is thin: many commits are dependency upgrades, and several kept bugs only appear in production (Heroku Redis TLS, production-only asset compression, production bundle on a new Ruby), which is why `loop` is strong. The pattern is clear: most bugs are a job, rake task, migration, build command or request that nobody ran end to end before shipping. The existing Minitest suite already has the right shape for that cell (functional controller tests, job tests), but it missed these paths. Its job test calls `BackgroundInactiveEmailJob` directly rather than through the scheduler that enqueues it. It has no anonymous-user request for the users and topics pages, and no test for `doc_methods#show`.

| Cell | Expect (`propose` · `leave` · `either`) | Why — what in the repository says so |
|---|---|---|
| `unit × bring out` | propose | 1 bug, a security hole: `3e77748` (shell injection via crafted clone URL in `GithubFetcher::Repo#clone`; the fix added a unit test) |
| `unit × witness` | either | 0 bugs cheapest here; the cell is possible (e.g. recording the shell/HTTP calls a fetcher makes) |
| `unit × reach in` | either | 0 bugs cheapest here; no structural reason it cannot exist (e.g. calling a query from a console on the running app) |
| `piece × bring out` | propose | 5 bugs: `16cf5d2`, `b6a002f`, `9712260`, `0c498ae`, `dac994d` |
| `piece × witness` | either | 0 bugs cheapest here; a mailer piece check is possible (mailer previews exist in `test/mailers/previews`) |
| `piece × reach in` | propose | 2 bugs: `2b3db89` (homepage JS toggled every language dropdown), `bc3d004` (University code blocks rendered wrong) |
| `operation × bring out` | propose | 8 bugs: `e81a7fd`, `0ca4af2`, `7213f4b`, `7bc8db2`, `683ba04`, `f8a8a1d`, `b173235`, `3d6b082` |
| `operation × witness` | either | 0 bugs cheapest here; `e81a7fd` (inactive-user email never sent) would also show up by checking that the mail was sent |
| `operation × reach in` | propose | 2 bugs: `2c0a5af` (Sidekiq could not reach Heroku Redis over self-signed TLS), `47fdcb2` (Puma `nakayoshi_fork` silently not running) |
| `journey × bring out` | either | 0 bugs cheapest here; Rails integration tests exist (`test/integration/*`) so the cell exists |
| `journey × witness` | either | 0 bugs cheapest here; possible (e.g. sign-up, then the daily triage mail) |
| `journey × reach in` | either | 0 bugs cheapest here; the OAuth login regressions (`683ba04`, `0c498ae`) would also show up in a real browser login journey, but a cheaper cell catches them |
| `loop` | propose | ≥ 2 bugs from dev/prod or version differences: `f8a8a1d` and `b173235` (asset minifier runs only in production), `2c0a5af` and `b6a002f` (production Redis TLS; the first fix ran only outside production), `3d6b082` (`matrix` missing from the production bundle on Ruby 3.1), `7213f4b` (migration "validated locally" failed on deploy) |

## Evidence — fixed bugs

| Commit | What broke | Cheapest cell that would have caught it | Why that cell |
|---|---|---|---|
| `3e77748` | Repo clone interpolated the clone URL into a shell, so a crafted URL could run arbitrary commands or use `file://`/`ext::` transports | `unit × bring out` | One method given a malicious URL shows it; the fix shipped exactly that unit test |
| `e81a7fd` | Inactive-user email job crashed: the scheduler passed `min_issue_count`/`min_subscriber_count` but the job required `repos_by_need_ids:`, and the mailer called an undefined `repo.where` | `operation × bring out` | Running the schedule task, which enqueues and performs the job, in the test env raises at once. The job test calls the job directly, so it never exercised the caller's arguments |
| `0ca4af2` | `PERCENTILE_CONT` returned the float `"1.0"`, which was passed into an integer SQL parameter, so the poke-inactive mail failed with `PG::InvalidTextRepresentation` | `operation × bring out` | Only fails when the rake task runs against real Postgres; the commit body quotes a local schedule-rake test that is not in the tree |
| `7213f4b` | Migration called a nonexistent `safety_assured`, so the deploy aborted all migrations | `operation × bring out` | Running `db:migrate` from a clean DB, rather than loading `schema.rb`, fails at once; the author says it "worked locally" |
| `16cf5d2` | `PopulateIssuesJob` failed with `integer out of range` once issue-assignment ids passed 2^31 | `piece × bring out` | A model-level check that inserts an id above int4 (or a schema check for int PKs/FKs) shows it; real-scale data only exists in prod |
| `7bc8db2` | Topics page broke for signed-out users (`@repos` only set when signed in), and the nav showed no Topics link to them | `operation × bring out` | One anonymous GET request to `/topics/:name`; `cc84a7e` then added that controller test |
| `683ba04` | After the OmniAuth 2 upgrade (`4719819`), GET on user edit while logged out gave a 404 "Authentication passthru" | `operation × bring out` | One anonymous GET request to `users#edit`; `users_controller_test.rb` existed and missed it |
| `0c498ae` | Sign-up link on the About page used GET to the OmniAuth path, so it hit the passthru 404 after OmniAuth 2 | `piece × bring out` | Rendering the view and asserting that OmniAuth links are POST shows it; the same fix landed again in `f5e6f08` |
| `9712260` | `doc_methods#show` crashed with ``undefined method `encode' for URI:Module`` (removed in Ruby 3) | `piece × bring out` | Rendering that one view fails; `doc_methods_controller_test.rb` tests only `click_method_redirect`, never `show` |
| `dac994d` | Two homepage language lists shared cache key `:language_list`, so the covid section showed links with the wrong query param | `piece × bring out` | Rendering the page with caching on shows the second list reusing the first's fragment (test env uses no cache store) |
| `f8a8a1d` | Production asset precompile aborted: Uglifier could not parse modern JS (`Unexpected token: punc (.)`) | `operation × bring out` | Running `RAILS_ENV=production rake assets:precompile` (the build command) fails; dev/test never minify (env difference) |
| `b173235` | Production precompile aborted on ES6 `const` in a JS dependency (Uglifier without harmony mode) | `operation × bring out` | Same build command in production mode; production-only compressor |
| `3d6b082` | Deploy failed: `prawn` required `matrix`, which Ruby 3.1 no longer bundles, so `rake -P` could not load | `operation × bring out` | Booting the app or running `bundle exec rake -P` on the production Ruby/bundle fails at once |
| `2c0a5af` | Sidekiq could not connect to the upgraded Heroku Redis 7: TLS with self-signed certs failed validation | `operation × reach in` | Only visible against the real hosted Redis; dev Redis has no TLS |
| `b6a002f` | The TLS fix in `2c0a5af` was placed under `unless Rails.env.production?`, so production still failed | `piece × bring out` | Loading the Sidekiq initializer under `RAILS_ENV=production` and inspecting `redis` config shows `ssl_params` missing |
| `47fdcb2` | Puma `nakayoshi_fork` was declared without its argument, so it never ran (lost copy-on-write memory savings) | `operation × reach in` | Only visible by launching the real server and reading its boot output or memory |
| `2b3db89` | Homepage language dropdown JS used global selectors, so clicking one filter toggled and relabelled every filter box | `piece × reach in` | jQuery behaviour on the rendered page; needs a browser driving that one screen |
| `bc3d004` | University pages' code blocks rendered broken (CSS) | `piece × reach in` | Purely visual; a screenshot of one page shows it, and no test asserts on styling |

## Excluded candidates

- `e9abcab` — test-only fix (missing VCR stub)
- `cc84a7e` — test-only (adds tests after `7bc8db2`)
- `c8b0e4d` — test-only fix (removing spring, schema bumps)
- `c197bb5` — CI workflow only
- `1216525` — issue template, no app behaviour
- `9f78305` — lint (standardrb)
- `65550f4` — lint (rubocop)
- `4f9265f` — lint (rubocop)
- `f5a7525` — lint (rubocop)
- `ec302f0` — typo in a heading
- `a0c82b5` — typo
- `aceb39f` — typo
- `c3257aa` — README typo
- `f5e6f08` — duplicate of the `0c498ae` OmniAuth link fix, plus content link edits
- `092e10c` — Rails/Ruby upgrade (dependency bump)
- `097c271` — dependency loosening, scout_apm upgrade
- `3b65d2f` — dependency bump
- `c8af62e` — dependency bump (VCR)
- `2a00a5e` — dependency bump (bootsnap)
- `4719819` — OmniAuth 2 dependency upgrade (its regressions are kept as `683ba04` and `0c498ae`)
- `dcde3f9` — dependency bump
- `5dd08dd` — dependency bump (security)
- `fcab3e1` — dependency bump
- `2dd05cf` — dependency bump (security)
- `a2e76d6` — dependency bump (security)
- `a7d35ee` — dependency bump (Gemfile.lock only, code fences)
- `83a8059` — dependency bump (faraday deprecation warnings)
- `c9534b7` — dependency bump (web-console)
- `39ca1dc` — Puma version bisect (dependency pin)
- `4123191` — Puma version bisect (dependency pin)
- `4d38927` — Puma version bisect (dependency pin)
- `eb5fc66` — Puma version bisect (dependency pin)
- `27b6ba3` — Puma version bisect (dependency pin)
- `1e49ee1` — removes debugging scaffolding
- `b9f9bd8` — debugging scaffolding
- `a2956ea` — debugging scaffolding
- `d5bcafc` — debugging scaffolding
- `c1d9703` — debugging scaffolding
- `12001f0` — product decision (remove COVID homepage), not a bug
- `9271b15` — revert of the clear-button feature; the failure reason is only in an off-repo PR comment
- `8b31eaa` — preventive bigint migration for other columns; no observed failure (the observed one is kept as `16cf5d2`)
- `331eadd` — preventive: makes a mailer kwarg required; no observed wrong send
