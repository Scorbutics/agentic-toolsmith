# Answer key — subscription-payments

**Repository:** https://github.com/vercel/nextjs-subscription-payments @ `bdd0813206e4` · **Shape:** Next.js 14 + Supabase + Stripe SaaS starter (webhooks write through a service-role client)

**Filled by:** bug-grounded draft — an agent blind to the skill, from the fixed bugs below · 2026-11-25 — verify the citations
**M1 accepted:** `unit × bring out`

Examined the 60 most recent of 86 non-merge commits reachable from `bdd0813` that matched fix|bug|regression|revert|hotfix|crash|broken|wrong|error|issue|#N (145 non-merge commits in total). Because squash-merge subjects carry `(#NNN)`, the pattern matched nearly every PR, so most of the 60 are not fixes. Kept 14 real behaviour bugs. Excluded 46: 20 README/docs/typo/link changes, 9 dependency bumps or framework migrations, 9 features, 8 refactors, cleanups or config-only chores. The evidence is moderate. 14 bugs clears the 5-bug bar, but most are one-line fixes. The repository has no test suite to show which check was missing. Four kept bugs are cosmetic or form-state UI issues. The money-relevant bugs are only two, both in the webhook (`23c4b0d`, `ffcca46`). The 26 older candidates outside the window were not examined, among them `bce3a81` "Fix billing interval on account page", `21ac9c0` and `a6a1e36`, so earlier webhook and pricing bugs are missing from this key.

| Cell | Expect (`propose` · `leave` · `either`) | Why — what in the repository says so |
|---|---|---|
| `unit × bring out` | propose | 5 bugs: `85c0e0c`, `96eb869` and `93a86e2` (`getURL` built a wrong or scheme-less URL from env values), `a4719c4` (admin upsert errors logged as `[object Object]`), `80f6515` (`schema.sql` invalid and a migration that drops `prices.description`/`metadata`, i.e. data loss). Most bugs; contains a data-loss bug |
| `unit × witness` | either | 0 bugs. Can exist: SQL triggers such as user-row copying on auth signup (`82fe379`) write rows that could be witnessed |
| `unit × reach in` | either | 0 bugs. No structural barrier |
| `piece × bring out` | propose | 4 bugs: `208273f` (pricing cards offset at xs–sm), `442420c` (login/signup not vertically aligned), `b27f9fa` (sign-in/sign-up enabled with empty email/password), `d732ebf` (pricing page threw when Supabase was not set up yet, breaking deploy) |
| `piece × witness` | either | 0 bugs. Can exist: forms post to server actions or routes, and those calls can be recorded |
| `piece × reach in` | either | 1 bug: `0cafcc3` (nav still showed signed-in links after sign-out until refresh) |
| `operation × bring out` | propose | 1 money bug: `23c4b0d` (webhook returned 200 when the DB write failed, so Stripe never retried and the subscription change was lost) |
| `operation × witness` | either | 0 bugs. Can exist: the webhook writes `subscriptions`/`prices` rows through the service-role admin client (`utils/supabase/admin.ts`, `a4719c4`) |
| `operation × reach in` | propose | 1 money bug: `ffcca46` (webhook read `Stripe-Signature` through `next/headers` inside the route handler; fixed to `req.headers`, so deliveries depended on Next runtime behaviour) |
| `journey × bring out` | either | 0 bugs. Can exist: whole app against a Stripe mock/fixtures (`00ab2d4`) |
| `journey × witness` | either | 0 bugs. Can exist |
| `journey × reach in` | propose | 2 bugs: `e7e0427` (OAuth/magic-link `redirectTo` skipped `/auth/callback`, so sign-in never finished), `c1a8214` (local email/password signup broken under PKCE with confirmations off) |
| `loop` | propose | 5 bugs came from environment differences: `96eb869` (dev, empty `VERCEL_URL`), `85c0e0c` (empty vs unset `URL`/`VERCEL_URL`), `93a86e2` (host-only `NEXT_PUBLIC_SITE_URL`/`VERCEL_URL` on deploy), `c1a8214` (local `supabase/config.toml`), `d732ebf` (deploy before Supabase was set up) |

## Evidence — fixed bugs

| Commit | What broke | Cheapest cell that would have caught it | Why that cell |
|---|---|---|---|
| `208273f` | Pricing cards had a vertical offset at screen widths between xs and sm (`space-y-4` combined with `gap-6`) | `piece × bring out` | Rendering the Pricing component alone at a narrow viewport shows it |
| `a4719c4` | Every admin/webhook DB error was logged as `[object Object]`, not as its message | `unit × bring out` | Call an admin helper with a stubbed Supabase error and read the thrown message |
| `93a86e2` | `getURL` stopped adding `https://` after the a138bf7 rewrite, so a host-only env URL gave broken redirect, callback and checkout URLs | `unit × bring out` | Pure function of env vars; one table-driven test |
| `80f6515` | `schema.sql` contained a stray diff-hunk line (invalid SQL), and a migration added in a138bf7 dropped `prices.description`/`metadata` and rewrote RLS policies | `unit × bring out` | Applying the schema/migrations to a throwaway DB fails or shows dropped columns |
| `0cafcc3` | After sign-out, server-rendered nav links stayed (`router.push` without refresh) | `piece × reach in` | Only a real session plus the server-component cache shows the stale navbar |
| `ffcca46` | Webhook route read the signature through `next/headers` `headers()`, not the request, so verification depended on the Next runtime | `operation × reach in` | A signed Stripe delivery (`stripe trigger`) against the running route shows the failure; a harness without the Next runtime would not reproduce it faithfully |
| `e7e0427` | Auth UI `redirectTo` pointed to the site root, not `/auth/callback`, so the code was never exchanged and sign-in did not finish | `journey × reach in` | Crosses link request → provider/mail → callback → session; visible only when the whole sign-in is run |
| `c1a8214` | Local Supabase config left `enable_confirmations=false`, which broke PKCE email/password signup locally | `journey × reach in` | Signing up on the local stack is what fails; no single function is wrong |
| `d732ebf` | `getActiveProductsWithPrices` threw when Supabase was not configured yet, so the pricing page and deploy failed | `piece × bring out` | Rendering the pricing page against an empty or unconfigured backend shows the throw |
| `23c4b0d` | Webhook handler errors returned 200 with a JSON body, so Stripe treated failed deliveries as delivered and subscription rows were lost | `operation × bring out` | Invoke the handler with a fixture event and a failing DB stub, then assert the status is not 2xx |
| `85c0e0c` | `getURL` operator precedence (`URL ?? VERCEL_URL === '' ? …`) chose the wrong URL | `unit × bring out` | Pure function; env-matrix test |
| `96eb869` | In development (empty `VERCEL_URL`), `getURL` returned `https://` with no host | `unit × bring out` | Pure function; env-matrix test |
| `b27f9fa` | Sign-in and sign-up buttons were enabled with an empty email or password (#48) | `piece × bring out` | Render the form in isolation and check the disabled state |
| `442420c` | Login and signup pages were not vertically aligned under the header | `piece × bring out` | Screenshot of the page component in a lab |

## Excluded candidates

1623fb9 — README deploy link revert
c2954c7 — README only
25a1950 — README only
808c318 — dependency bump plus refactor to `queries.ts`/React `cache()`, no bug fixed
6d162b6 — README only
0efb17c — docs diagram
c433067 — package.json dev script commands (tooling config only)
b7eb56b — removes unused CSS class/file (cleanup)
4965281 — README URL
73b020a — README only
954aefe — README URL
2ba52c6 — onboarding chore: config.toml, setup script, debug `console.log` removal
80193d7 — dependency bump / lockfile
a138bf7 — Next.js 14 + Supabase SSR migration (feature; introduced bugs fixed in 93a86e2 and 80f6515)
c7867b2 — README only
17a4324 — README typo
e1faf14 — feature: deploy button
ce74f66 — docs and `.env.local.example`
f1c2246 — app-router refactor (Promise.all, cache, useRouter); performance and style, no reported bug
64fe5b8 — chore: disable Google OAuth (product choice)
3efdfb4 — typing refactor
8697790 — feature: app directory migration
e51b170 — README
0f2204b — Next.js 13 and dependency bump
9628c7b — README
87b47f5 — README
294fd40 — README
07a7cd1 — README
ef885be — README
1c03b09 — chore: `getURL` refactor to a new env var (feature, no reported bug)
1abcadf — feature: Supabase auth UI
bbb4032 — dependency upgrade (supabase-js v2)
776292b — dependency migration (auth-helpers)
3a0df90 — dependency bump
f020868 — feature: longer session cookie
64fdf3b — chore: logout API route
a181738 — feature: supabase-auth-helpers
2227985 — dependency bump / Tailwind config
1c86d75 — TypeScript conversion
00ab2d4 — feature: Stripe fixtures
857941d — README / deploy button image
d83d7dc — README
5953c9a — refactor of `buffer`
909fbed — code cleanup
c965ea8 — comment typo and trailing newline in schema
0e7f20b — README links
