# Answer key — healthchecks

**Repository:** https://github.com/healthchecks/healthchecks @ `c1039ad23395` · **Shape:** Django service: cron-job monitoring, a web UI and an API, alert integrations, background sendalerts loop

**Filled by:** bug-grounded draft — an agent blind to the skill, from the fixed bugs below · 2026-11-27 — hold-out: drafted after the skill was frozen
**M1 accepted:** unit × bring out, piece × bring out

60 candidate commits examined (the 60 most recent non-merge commits reachable from `c1039ad23395` matching fix/bug/regression/revert/crash/broken/wrong/error/issue #, out of 998 matches overall). 34 commits kept, forming 28 distinct bugs: the seven `update_fields` commits (1d8e6187, f2cade29, 6187c982, 88d39a28, a6bd60c3, b2c68011, a5cdc033) fix one lost-update race across seven views and are counted as one bug. 26 excluded: 14 type/lint/ruff/mypy-only, 3 test-only, 3 docs/comment/changelog/link-text, 1 dependency bump (5a183c3a), 2 packaging/features (dae1f892, 3b453a77), 1 revert of a feature with no stated defect (9b9e6f96), and 2 refactors with no observable misbehaviour (d36ab8fe, a8541502). The evidence is moderate. Almost every kept fix comes with a Django regression test, so the cheapest cell can be read from the code and not guessed. But the window is about four months from a single maintainer, it is dominated by email-transport parsing and input validation, and several fixes (the bounce classification, the Matrix join) were found from real-world traffic that no in-repo fixture reproduced. Three bugs depend on the database engine (NUL bytes and an over-long varchar are rejected by PostgreSQL but accepted by SQLite), and one is a Docker launch failure. That is why `loop` is `propose`.

| Cell | Expect (`propose` · `leave` · `either`) | Why — what in the repository says so |
|---|---|---|
| `unit × bring out` | propose | 7 bugs: email-transport sanitizer crashes on octet-stream, invalid-charset, nested-multipart and utf16 ping bodies (cf8c7e95, 236f6a55, 0c9c4a04, 4b0fd38b), so alerts were not sent; webhook header CR/LF injection (ff4fba48); shell command injection (ca8b9c03); bounce signature over the 64-char local-part limit (17b60843). Each one is a pure function fed a crafted input. The existing tests in `hc/integrations/email/tests/test_notify.py` covered this cell and missed the inputs. |
| `unit × witness` | either | No kept bug was cheapest here. Nothing structural prevents it, for example recording a function's emitted header bytes. |
| `unit × reach in` | leave | Structural: reach-in acts on the real running app, and a unit (one function or query alone) has no running app to act on. |
| `piece × bring out` | propose | 7 bugs: TOTP replay via Unicode digits (c51c7125, a security hole; `test_login_totp.py` existed and missed it); a Telegram POST with no querystring creates a channel with value "null" (cb5c9764); over-long schedules accepted (1a04fecb); log cleanup skipped when new records exist (8bae8607); wrong report type in `sendreports` output (3addc677); an SMTP connection error crashes the email alert (69aac3a4); webhook form errors concatenated (b1b865be). |
| `piece × witness` | propose | 4 bugs, including mail sent wrongly and data loss: the Matrix join sent no JSON body, and the test mocked `curl.post` without checking the payload (0413d5f6); URLs left clickable in invite and transfer emails (253e7594, 14008860; caught by checking the rendered `mail.outbox`); full-row `save()` overwrote concurrent ping state in seven views (1d8e6187 et al.), which is visible by witnessing the UPDATE's column list. |
| `piece × reach in` | either | No kept bug was cheapest here. A view can be driven in a running app, so the cell exists. |
| `operation × bring out` | propose | 3 bugs: NUL bytes in a list-checks query or API fields, and tags over 500 chars, each gave a 500 on PostgreSQL (ac59dec9, f6c46b59, e623fa3b). Each needs one API request against the real database engine. |
| `operation × witness` | propose | 2 bugs, both causing alerts not to be sent: the bounce handler classed "No usable MXs" and "MX lookup error" as permanent and so disabled email channels (425ee006, 255075ce). This is seen only by recording real bounce payloads and the resulting channel state. |
| `operation × reach in` | propose | 3 bugs: a concurrent `Profile.for_user()` violates a unique constraint (59caeef5); `manage.py smtpd` ignored SIGTERM/SIGINT (49c9797e); keyboard focus outline missing on the project selector (3dfb0b97, #1324, needs a browser). All three need the real running process, concurrency or a browser. |
| `journey × bring out` | propose | 1 security bug: the email verification link was not bound to the address, so add, then edit the address, then click the old link verified an address the user does not control (6b634df1). It needs a multi-operation user sequence. |
| `journey × witness` | either | No kept bug was cheapest here. The cell exists (a full signup-to-alert journey checked through outbox and DB rows). |
| `journey × reach in` | either | No kept bug was cheapest here. The cell exists (a browser or HTTP journey against a deployed instance). |
| `loop` | propose | At least 2 bugs came from environment differences: 3 PostgreSQL-vs-SQLite differences (ac59dec9, f6c46b59, e623fa3b), plus the Docker image failing to launch because `CMD ["run.sh"]` was not on PATH (de5a6330). |

## Evidence — fixed bugs

| Commit | What broke | Cheapest cell that would have caught it | Why that cell |
|---|---|---|---|
| ac59dec9 | NUL byte in `tag`/`slug` query param of List Checks API gave a 500 | operation × bring out (+loop) | PostgreSQL rejects NUL and SQLite does not; one API request against the real engine shows it |
| c51c7125 | TOTP replay protection bypassed by Unicode digits that normalize to ASCII | piece × bring out | A form/view test that reuses a code in Unicode-digit form; `test_login_totp.py` covered the cell and missed it |
| 4b0fd38b | Email alert crashed on a ping body with a utf16 charset (`b"dummy".decode` fails) | unit × bring out | `bytes_to_sanitized_message` on one crafted input; the existing `test_notify.py` covered the cell and missed it |
| 0c9c4a04 | Nested multipart ping bodies were not rewrapped or sanitized in email alerts | unit × bring out | Pure function on a nested MIME fixture |
| cb5c9764 | Telegram add POST without querystring created a channel with value "null", breaking JSON consumers | piece × bring out | A view test with a malformed POST |
| 236f6a55 | Ping body with an invalid charset raised in the email transport, so no alert was sent | unit × bring out | Pure function on a crafted email; `test_notify.py` existed |
| 425ee006 | Bounce with "No usable MXs" treated as permanent, so the email channel was disabled | operation × witness | Only real bounce payloads and the resulting channel state reveal which diagnostics occur |
| 255075ce | Bounce with "MX lookup error" treated as permanent, so the email channel was disabled | operation × witness | Same as above |
| 0413d5f6 | Matrix join API call sent no JSON body, so real homeservers rejected it (#1366) | piece × witness | Witness the outbound request against the Matrix API contract; the test mocked `curl.post` and did not check the body |
| cf8c7e95 | Email transport raised `set_bytes_content()` on an octet-stream ping body | unit × bring out | Pure function on one crafted input |
| 1a04fecb | Schedule preview/validation accepted very long cron/OnCalendar expressions | piece × bring out | A form/view test with an over-long input; `test_validate_schedule.py` covered the cell and missed it |
| f6c46b59 | Management API accepted NUL characters in text fields, which failed in the DB | operation × bring out (+loop) | Fails only on PostgreSQL; one API call against the real engine |
| ff4fba48 | Webhook header injection via CR/LF in a check name (security) | unit × bring out | `Webhook.prepare(..., is_header=True)` on a crafted name |
| 59caeef5 | Race in `Profile.for_user()`: concurrent creation hit a unique constraint | operation × reach in | Needs concurrent requests against the running app and a real DB |
| de5a6330 | Docker image `CMD ["run.sh"]` not on PATH, so the container did not start | loop | A launch/environment defect, seen only by starting the image |
| 49c9797e | `manage.py smtpd` did not stop gracefully on SIGINT/SIGTERM | operation × reach in | Needs the real process and a signal |
| ca8b9c03 | Shell integration command injection through placeholder substitution (security) | unit × bring out | Transport with a crafted check name/tags, checking what is executed |
| e623fa3b | Tags over 500 chars were accepted by the API/forms, then failed in the DB | operation × bring out (+loop) | SQLite does not enforce varchar length and PostgreSQL does |
| 8bae8607 | `sendlogs` deleted old records only when there were no new ones | piece × bring out | A management command test with old and new records |
| 3addc677 | `sendreports` logged "monthly" for weekly and daily reports | piece × bring out | A management command stdout test |
| 69aac3a4 | SMTP connection errors crashed alert delivery and were not recorded as a transport error (#1346) | piece × bring out | Transport test with a faked SMTP failure |
| 14008860 | Transfer-request email rendered URLs in project names as clickable links (phishing abuse) | piece × witness | Check the rendered mail in the outbox |
| 253e7594 | Project invite email rendered URLs in project names as clickable links (phishing abuse) | piece × witness | Check the rendered mail in the outbox |
| 6b634df1 | Email verification token did not depend on the address, so a user could verify an address they do not own (security) | journey × bring out | Needs the sequence add, edit address, then use the old link |
| 17b60843 | Signed bounce IDs exceeded the 64-char email local-part limit | unit × bring out | Assert the length of `sign_bounce_id` output |
| b1b865be | Webhook form error messages joined without a separator | piece × bring out | Render the form template with several errors |
| 1d8e6187, f2cade29, 6187c982, 88d39a28, a6bd60c3, b2c68011, a5cdc033 (one bug) | Full-row `check.save()` in update_name, filtering_rules, pause/resume, clear_events, update_timeout, transfer and the API update overwrote concurrent ping updates (status, n_pings) — data loss | piece × witness | Witness the UPDATE statement's columns in a view test; no concurrency needed |
| 3dfb0b97 | Project selector had no visible keyboard-focus outline (#1324) | operation × reach in | Only visible in a browser on the rendered page |

## Excluded candidates

3e9e4f94 — type-warning fix only
9fdd0394 — mypy warning only
fabc5f18 — test-only (f-string in a test)
51a50353 — CHANGELOG only
5a183c3a — dependency bump (minismtpd 0.3 to 0.5)
3b453a77 — feature (configurable gunicorn port), not a bug fix
b29ed302 — comment in Dockerfile
dae1f892 — packaging change (uWSGI to gunicorn), infra/feature
9cd51df0 — test-only
9b9e6f96 — revert of a feature (log deletion) with no stated defect
94d215ce — mypy warning only
6c4998e4 — ruff warnings only
69dbd2a0 — type warning only
9b0b7ea2 — link text http to https in templates (doc-like)
a2f0af2d — mypy warning only
bcdb1dba — ruff warning only
fafac59e — ruff warnings only
79173a5d — ruff warning refactor
6a72a46a — test-only
f13692d5 — type annotation only
5086d282 — ruff warnings only
d36ab8fe — mutable default argument refactor, no observable misbehaviour stated
a8541502 — logging-call refactor
707502c5 — file-handle close in a dev-only command (lint)
1584b3d2 — type warning only
75660e7a — refactor (removeprefix)
