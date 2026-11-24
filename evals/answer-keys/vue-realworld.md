# Answer key — vue-realworld

**Repository:** https://github.com/mutoe/vue3-realworld-example-app @ `741c215` · **Shape:** Vue 3 SPA against a remote API

**Filled by:** bug-grounded draft — an agent blind to the skill, from the fixed bugs below · 2026-11-25 — verify the citations
**M1 accepted:** `operation × witness`

I examined the 60 most recent non-merge candidates reachable from `741c215` whose message matched fix/bug/regression/revert/hotfix/crash/broken/wrong/error/issue/#N. The window runs from `dd34ba9` back to `32bdf9c`. I kept 18 real behaviour bugs and excluded 42. Of the excluded: 13 were CI, pipeline, lint, tsconfig or IDE configuration; 9 were test-only or test-tooling fixes; 6 were dependency bumps or upgrade migrations; 4 were refactors or build analysis; 3 were docs, fixtures or comments; 7 were other chores with no change to app behaviour. The evidence is moderate. There are 18 bugs, but they are small, mostly one-line diffs from a single maintainer. Several share a root cause. `606cb8e`, the swagger-client migration, produced `275cadd` and `45dea6f`, and arguably `e59d1d5`, `98d7f38` and `0b5c47e`. The cluster at `operation × witness` is the clearest signal. Seven bugs were requests that went out wrong: wrong payload, wrong method, wrong header, a call that should never have been made, or a stale token left in storage. Four of these sent wrong data to the API. Three fixes come from remote-environment drift: a retired API host twice, and a dead remote stylesheet. Only a run against the live app would have shown them.

| Cell | Expect (`propose` · `leave` · `either`) | Why — what in the repository says so |
|---|---|---|
| `unit × bring out` | either | 1 bug: `aeb56e4` (pure error-mapper ignored 403). Not data loss or a security hole. |
| `unit × witness` | either | 0 bugs cheapest here. The cell can exist (for example a store action that writes localStorage), but `5ce52d1` is better seen at operation level. |
| `unit × reach in` | either | 0 bugs. No structural bar. |
| `piece × bring out` | propose | 4 bugs: `ece4466`, `98d7f38`, `34aa39b`, `76c7405`. These are form error display and stale state on Settings, Login and Register, plus a layout overflow on Article. |
| `piece × witness` | either | 0 bugs cheapest here. Component specs with `cy.intercept` already exist (`bb00003` spec), but the request itself is the operation. |
| `piece × reach in` | either | 0 bugs. No structural bar. |
| `operation × bring out` | propose | 3 bugs: `c08135c`, `4125239` (route guards on navigation) and `e59d1d5` (responses not parsed as JSON, seen against a mock API). |
| `operation × witness` | propose | 7 bugs: `e2e0b45`, `45dea6f`, `275cadd`, `0b5c47e`, `bb00003`, `19bd81f`, `5ce52d1`. Four sent wrong data to the API: `e2e0b45`, `45dea6f`, `275cadd`, `0b5c47e`. |
| `operation × reach in` | either | 0 bugs. No structural bar (the remote API is public). |
| `journey × bring out` | either | 0 bugs. A full app on a mock API is possible (msw/fixtures exist), but nothing landed here. |
| `journey × witness` | either | 0 bugs. No structural bar. |
| `journey × reach in` | propose | 3 bugs: `c9ec36a` and `b360009` (API host retired) and `c75a0b2` (remote main.css returned 403). Only the live app against real remotes shows these. |
| `loop` | propose | 3 bugs came from environment drift, not code: `c9ec36a`, `b360009`, `c75a0b2`. Wrong preview port `46b92e7` (excluded, test launch only) points the same way. |

## Evidence — fixed bugs

| Commit | What broke | Cheapest cell that would have caught it | Why that cell |
|---|---|---|---|
| `4125239` | A logged-in user going to /login or /register had navigation silently cancelled, not redirected home. Unknown paths had no 404 page. | `operation × bring out` | A router test of a single navigation with a stubbed auth state shows the cancelled route. `router.spec.ts` was added only in the fix. |
| `c75a0b2` | The app loaded its stylesheet from `demo.realworld.io/main.css`, which started returning 403, so the app rendered unstyled. | `journey × reach in` | External resource drift. Only loading the real app in a browser and looking at it reveals it. |
| `c9ec36a` | The API host `api.realworld.io` was retired, so every call failed. | `journey × reach in` | Environment drift. Every mock or fixture still passes, and only the live app against the real remote shows it. |
| `b360009` | The API domain changed (#75), so the app pointed at a dead host. | `journey × reach in` | Same as above: a `.env` change only, and only visible live. |
| `5ce52d1` | On a 401 the stale token stayed in localStorage, so the user was bounced to login with a dead token forever. The Authorization header casing was also changed. | `operation × witness` | Simulate one 401 and witness storage and headers: the token is not removed. `use-async.spec.ts` existed and missed it. |
| `ece4466` | Settings swallowed API validation errors, so no message was shown to the user (#58). | `piece × bring out` | Mount Settings with a mocked error response and check that messages render. `Settings.spec.ts` existed and did not test the error path. |
| `e59d1d5` | The generated client lacked `format: 'json'`, so response bodies were not parsed and `data` was empty. Login also lost non-fetch errors. | `operation × bring out` | One call against a mock API, then check what the app does with the response. |
| `0b5c47e` | After swagger regeneration, requests went out without a JSON `content-type` header and the tags call used a renamed method. | `operation × witness` | A recorded request shows the missing header. This is wrong data sent to the API. |
| `98d7f38` | The new client throws on non-2xx, but Login and Register still checked `result.ok`, so validation errors never showed. | `piece × bring out` | Mount the page with a mocked 422 and check the error list. `Login.spec.ts` and `Register.spec.ts` existed and missed it. |
| `45dea6f` | The Settings new-password field was bound to `form.token`, so the password was never sent and could not be changed. | `operation × witness` | The witnessed PUT /user body has `token`, not `password`. This is wrong data sent to the API. |
| `76c7405` | The Article page overflowed horizontally (`.row` margin). | `piece × bring out` | A component-lab screenshot of the page with the app CSS shows the scrollbar. |
| `275cadd` | Login's password input was bound to `form.token`, so login sent no password. The auth plugin also called the removed `setAuthorizationHeader`. | `operation × witness` | The witnessed login request body lacks `password`. Introduced by `606cb8e`. This is wrong data sent to the API. |
| `bb00003` | Follow/unfollow were inverted, so clicking Follow sent DELETE and Unfollow sent POST. | `operation × witness` | The witnessed method on one click is wrong. `ArticleDetailMeta.spec.ts` intercepted these calls and still did not stop it shipping. |
| `34aa39b` | Login and Register kept stale error messages from a previous submit. | `piece × bring out` | Mount the form, submit twice with mocked responses, and check the old errors are cleared. |
| `aeb56e4` | `mapValidationResponse` treated a 403 as an unexpected error, so login failures threw instead of showing a message. | `unit × bring out` | A pure function: a unit test with a 403 input shows it. The spec existed but covered only 422. |
| `c08135c` | Logged-in users could open the login and register pages. | `operation × bring out` | A test of one route navigation with an authorized store. |
| `e2e0b45` | The `putProfile` payload lacked the `{ user: … }` wrapper, so the profile update was rejected or ignored by the API. | `operation × witness` | The witnessed PUT /user body has the wrong shape. This is wrong data sent to the API. |
| `19bd81f` | `useProfile` called the profile API with a null username (`/profiles/null`). | `operation × witness` | The witnessed request log shows a call that should not exist. |

## Excluded candidates

- dd34ba9 — docs (CLAUDE.md, README badge)
- 689960d — test-only (localStorage polyfill in test setup)
- 15df59c — config/lint (playwright tsconfig)
- ef5e121 — test-only (removed e2e tests)
- 0e8dbe6 — test-only (snapshots, test config)
- 506395f — test-only (test interceptor)
- f1c9026 — test tooling (playwright/utils/prettify.ts sanitization; not app code)
- bdbdd47 — lint
- 630ea92 — CI pipeline
- 4afa0f4 — tsconfig only
- 0485060 — cypress tsconfig only
- 46b92e7 — package scripts: wrong preview/e2e port (test launch config, no app behaviour)
- e73cb0a — CI pipeline script
- d83176b — test utils after msw upgrade
- 09f3818 — test-only
- ab11d70 — git hooks
- 1570e38 — dependency bump
- 71c7e4e — dependency bump
- 6d528ff — dependency bump
- f418145 — dependency bump (marked)
- de94150 — CI
- 56276a9 — test-only (cypress)
- 8e2d90c — tsconfig only
- 718eca6 — CI cache
- 5173b4a — CI cache
- 7bbca09 — CI arguments
- 44279eb — e2e test types
- 0735877 — code comment only
- a8bd160 — IDE type declaration (env.d.ts)
- 954df75 — tsconfig lib
- 70a23f0 — lint
- 951f2ce — eslint config
- daaaa48 — husky executable
- 569f47c — lint script on Windows (dev tooling)
- 969dd43 — docs/fixtures domain update
- b553647 — test-only (async component tests)
- 1747d93 — upgrade migration to Vue 3.2 syntax (no reported bug)
- 6bb66be — lint refactor
- 32fa6ad — test-only (cypress intercept)
- 06956dc — dependency bump
- fd07df0 — refactor (remove deepmerge, bundle size #39)
- 32bdf9c — build analyzer tooling
