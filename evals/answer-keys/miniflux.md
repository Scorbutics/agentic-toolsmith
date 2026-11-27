# Answer key — miniflux

**Repository:** https://github.com/miniflux/v2 @ `fb04322` · **Shape:** Go service with workers and Postgres

**Filled by:** bug-grounded draft — an agent blind to the skill, from the fixed bugs below · 2026-11-25 — verify the citations
**M1 accepted:** `unit × bring out`

I examined the 60 most recent non-merge commits reachable from `fb04322` whose message matched fix/bug/regression/revert/hotfix/crash/panic/broken/wrong/error/issue (dependency bumps filtered out first). I kept 55 real behaviour bugs and excluded 5: 2 docs-only (70adb668, 5dadd25b), 1 feature (6333ca10), 1 performance index drop (ca241333) and 1 refactor follow-up (69756868). This evidence is strong in volume but skewed. The window (Jul–Nov 2026) is dominated by a security-hardening campaign (SSRF filter, open redirects, session handling, auth bypasses), and most fixes landed with Go unit tests next to pure functions (`internal/urllib`, `internal/validator`, `internal/config`, parsers). So `unit × bring out` wins by a wide margin. The repo already has a suite in that cell (`*_test.go`), and it missed many of these bugs (e.g. `url_test.go`, `client_ip_test.go` and `sanitizer_test.go` existed and missed). The repo also has a reach-in suite, `internal/api/api_integration_test.go` (it runs against a live server and is skipped unless configured). It missed 052409ef, a7f93d8b and c342187b. Several cell assignments between `piece` and `operation` are judgement calls, because handlers call `*storage.Storage` directly and there is no fake store. A handler-level check therefore usually needs Postgres, which pushes it to `operation`.

| Cell | Expect (`propose` · `leave` · `either`) | Why — what in the repository says so |
|---|---|---|
| `unit × bring out` | propose | 26 bugs: 9447aaec, 64bdc5fe, faecfa2f, df363735, 707d3c39, 400e6b6a, 3945f3da, 04fc79f7, 927e0e86, 97fa1d37, 238c5614, 214aca7d, 942ea1d9, c317f84b, 5c80660a, 589659ff, b79ba933, 3b5a7ee4, 6ed1006a, a694ee71, 1d10e7a0, 0e26f124, c8c414e8, 308e1f96, fbbff63f, 5c62899d (includes SSRF 64bdc5fe/3945f3da/238c5614, XSS 3b5a7ee4, open redirect 942ea1d9/b79ba933, auth bypass 589659ff) |
| `unit × witness` | either | 0 bugs had it as cheapest; the cell can exist (e.g. recording the SQL one storage function issues), there is just no evidence |
| `unit × reach in` | either | 0 bugs; nothing structural rules out observing one function or query inside the running app, but no fixed bug needed it |
| `piece × bring out` | propose | 10 bugs: b8da6886 (CSRF token leaked through public cache, security), b475d6bb, 5f5efd75, f17c8fd3 (SSRF via per-feed proxy, security), 249b340c, b683d3b4, cedbb394, b3039d6c, 2bc9f306, e4e7dc55 |
| `piece × witness` | propose | 6 bugs: 378ce7df, d5c529b9, bdd8087d, 030ecebf (unwanted web_sessions rows written by the middleware), 7833b224 (auth token written to logs, a credential sent to the wrong place), 82537616 (empty tag in the Raindrop payload) |
| `piece × reach in` | either | 0 bugs had it as cheapest; row missing from the agent's draft, added with the drafting rule's default |
| `operation × bring out` | either | 0 bugs; possible (e.g. a feed refresh against fixture servers outside the live app) but no fix fell here first |
| `operation × witness` | propose | 5 bugs: d57da7c7, a0cc2e44 (wrong DB writes from Fever mark requests), 229035a4 (sessions not revoked on password change, security), 0877d29e (feed cookie sent to third-party hosts, security and data sent to the wrong place), c342187b (no_media_player not stored) |
| `operation × reach in` | propose | 7 bugs: 052409ef, 752793f2 (admin password change without current password, auth bypass), 76889f08 (DISABLE_LOCAL_AUTH bypassed via API, auth bypass), a4c00331, c52bdef6, a7f93d8b, 2f9e07bd; existing `api_integration_test.go` is in this cell and missed 052409ef, a7f93d8b |
| `journey × bring out` | either | 0 bugs; a whole-app replica with fixture feeds is buildable, but no evidence |
| `journey × witness` | either | 0 bugs; possible, no evidence |
| `journey × reach in` | either | 1 bug: 106cdd09 (redirect_url lost after passkey login, browser flow); not security-class on its own |
| `loop` | propose | ≥ 2 bugs came from config/env differences: cedbb394 and b683d3b4 (HTTP_PROXY/HTTPS_PROXY env), 1d10e7a0 and 308e1f96 (config values rejected or accepted wrongly at startup), 76889f08 and 5f5efd75 (DISABLE_LOCAL_AUTH), f17c8fd3 (proxy opt-in flag) |

## Evidence — fixed bugs

| Commit | What broke | Cheapest cell that would have caught it | Why that cell |
|---|---|---|---|
| 9447aaec | Fever API key matched by plain SQL string comparison (timing side channel) | `unit × bring out` | Lies in one storage query; a unit check on the lookup (or a review of it) shows it. Ordinary tests are unlikely to catch timing |
| 64bdc5fe | IsNonPublicIP let 0.0.0.0/8 and 240.0.0.0/4 through (SSRF) | `unit × bring out` | Pure function; url_test.go existed and missed it |
| 052409ef | DELETE user returned 204 before deletion; deleted user's API keys kept working | `operation × reach in` | Seen only by calling the API, then reusing the key; api_integration_test.go existed and missed it |
| faecfa2f | CategoryByTitle was case-sensitive, so GReader/OPML hit "category not found" or created duplicates | `unit × bring out` | One query against a test DB with "News" vs "news" |
| df363735 | StreamType.String recursed infinitely on unknown values | `unit × bring out` | One method call |
| d57da7c7 | Fever mark group 0 as read ignored `before` and marked newer entries read | `operation × witness` | Effect is which entry rows were updated by the request |
| a0cc2e44 | Fever save/unsave toggled starred instead of setting it; repeated save unstarred | `operation × witness` | Repeated request; check stored state and integration pushes |
| 707d3c39 | Three translation keys used in code existed in no locale; raw key shown | `unit × bring out` | Check that every key referenced in code or templates exists in the catalog |
| 400e6b6a | Username format not validated on modification | `unit × bring out` | Validator function; user_test.go existed and missed it |
| b8da6886 | Shared entry page cached `public, immutable` with visitor's CSRF token | `piece × bring out` | Render share handler and view; inspect headers and body |
| 378ce7df | Every public route inserted a web_sessions row | `piece × witness` | Middleware with httptest; record session writes |
| b475d6bb | OIDC group claim read only from userinfo; admins lost admin role | `piece × bring out` | OIDC provider replaced by a mock returning the claim only in the ID token |
| 752793f2 | Admin could change own password via user edit without current password | `operation × reach in` | Log in as admin and POST own edit form |
| 229035a4 | Password change left other web sessions valid | `operation × witness` | After the request, the web_sessions rows are still there |
| 0877d29e | Feed cookie sent to every host (scraped articles, icons, discovery) | `operation × witness` | Record outbound requests during refresh or scrape; builder alone had no host context |
| 7833b224 | GR middleware logged raw malformed auth token | `piece × witness` | Capture log output from the middleware |
| 3945f3da | 6to4 and IPv4-compatible IPv6 bypassed SSRF filter | `unit × bring out` | Pure function; url_test.go existed |
| d5c529b9 | Sessions created for unauthenticated protected routes (24k junk rows) | `piece × witness` | Middleware writes recorded per request |
| 04fc79f7 | RFC 3339 dates with lower-case t/z failed to parse | `unit × bring out` | Parser function; parser_test.go existed |
| 5f5efd75 | WebAuthn button not enabled when the username field is absent (WebAuthn-only login) | `piece × bring out` | Run app.js init against the login template rendered without a username field (no JS test harness exists) |
| a4c00331 | Fever items returned without ORDER BY; clients could miss entries for good | `operation × reach in` | Call the endpoint on a populated DB and check the order |
| 030ecebf | Logged-out sessions kept as rows with copied prefs | `piece × witness` | Logout handler's session writes |
| bdd8087d | Media proxy requests created web_sessions rows | `piece × witness` | Middleware writes recorded per request |
| 927e0e86 | JSON feeds with UTF-8 BOM undetected or unparsed | `unit × bring out` | Fixture feed into format detection and the parser |
| 97fa1d37 | Client IP taken from spoofable left side of X-Forwarded-For | `unit × bring out` | Pure function; client_ip_test.go existed and encoded the wrong expectation |
| 238c5614 | Reserved IP ranges not blocked by SSRF filter | `unit × bring out` | Pure function |
| 214aca7d | Gotify nil feed dereference while logging | `unit × bring out` | Call SendMessages with a nil feed |
| 942ea1d9 | WebAuthn redirect accepted `//host` (open redirect) | `unit × bring out` | IsRelativePath function |
| f17c8fd3 | Per-feed proxy URL bypassed private-network restriction (SSRF) | `piece × bring out` | Request builder against a private proxy address |
| c317f84b | ACME challenge listener had no timeouts | `unit × bring out` | Construct the server and assert its timeouts |
| 5c80660a | Response encoding chosen by client order instead of server preference | `unit × bring out` | Encoding negotiation function |
| 249b340c | Karakeep failure reported content type, not HTTP status | `piece × bring out` | Client against a mock server returning HTML 502 |
| c52bdef6 | Feed/category page past end showed "no unread" with no pagination | `operation × reach in` | Request page with offset past end after mark-as-read |
| b683d3b4 | Redirect switching scheme dialled the env HTTPS_PROXY with the blocking dialer | `piece × bring out` | Fetcher with mock proxies and a redirect; env-driven |
| cedbb394 | Proxy set via HTTP_PROXY refused by private-network dialer | `piece × bring out` | Fetcher with env proxy on loopback; env-driven |
| 76889f08 | DISABLE_LOCAL_AUTH not enforced for API Basic auth and password changes | `operation × reach in` | Start with the config set and call the API with a password |
| 589659ff | GR token computable when stored password empty (auth bypass) | `unit × bring out` | Token lookup query with an empty password |
| b79ba933 | IsRelativePath accepted leading whitespace (open redirect) | `unit × bring out` | Pure function |
| a7f93d8b | Creating a feed with no categories panicked (API, OPML, GReader) | `operation × reach in` | API call after deleting the last category; api_integration_test.go existed and missed it |
| 106cdd09 | redirect_url dropped after passkey login | `journey × reach in` | Browser login flow across challenge, finish and reload |
| 2f9e07bd | GR /stream/items/ids capped at 1000 after fbbff63f (regression) | `operation × reach in` | Call endpoint without `n` on more than 1000 entries |
| b3039d6c | Documentation icon links had no accessible name | `piece × bring out` | Render templates and run an a11y check |
| 3b5a7ee4 | iframe allowlist accepted `javascript://youtube.com/...` (XSS) | `unit × bring out` | Sanitizer function; sanitizer_test.go existed and missed it |
| 6ed1006a | Existence-check helpers swallowed DB errors as "not found" | `unit × bring out` | Helper with a failing DB connection |
| 2bc9f306 | POST to static path panicked in CSRF middleware (nil session) | `piece × bring out` | Middleware chain with httptest |
| a694ee71 | `notyoutube.com` treated as YouTube and rewritten into embed | `unit × bring out` | Hostname check function |
| 1d10e7a0 | Config lists with spaces or trailing commas failed startup | `unit × bring out` | Option parser; config-driven |
| 0e26f124 | Concurrent locale loads hit fatal concurrent map writes | `unit × bring out` | Concurrent test under -race |
| e4e7dc55 | Proxy checkbox vanished on subscription-choose error re-render | `piece × bring out` | Render the handler's view after an error |
| c8c414e8 | Push to worker pool during shutdown panicked (closed channel) | `unit × bring out` | Pool test pushing after Shutdown |
| 82537616 | Raindrop payload carried an empty-string tag | `piece × witness` | Mock server records the outbound payload |
| 308e1f96 | SCHEDULER_ENTRY_FREQUENCY_FACTOR=0 accepted, then division-by-zero panic | `unit × bring out` | Config validator; config-driven |
| fbbff63f | limit=0 produced unbounded entry query | `unit × bring out` | Query builder output |
| c342187b | no_media_player dropped on feed creation | `operation × witness` | Create feed and inspect stored row; api_integration_test.go existed and missed it |
| 5c62899d | Feed proxy URL could never be cleared | `unit × bring out` | Validator; feed_test.go existed |

## Excluded candidates

70adb668 — docs only (man page)
5dadd25b — docs only (man page)
6333ca10 — feature (rewrite rule validation), not a bug fix
ca241333 — performance: drops redundant index, no behaviour bug
69756868 — refactor follow-up to 6ed1006a (signature change), the bug itself is counted under 6ed1006a
