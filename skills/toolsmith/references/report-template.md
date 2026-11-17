# Reach report — <project> (<date>)

**Task:** <the fix/feature, or "audit"> → **maps to:** <feature, file, owning repo>
**Shape(s):** <e.g. web app with accounts + worker + Postgres>
**Variants probed:** <e.g. phone + desktop viewport, or raylib + sfml> · **Loops:** <inner / outer, if a tool>
**Safety boundary (verified):** <live keys, prod-copy data, user data; strictest policy layer>
**Permissions granted:** read-only · rolled-back · local write · inject · external

## Ladder

| # | Rung | Status | Cost | Evidence |
|---|------|--------|------|----------|
| 1 | Build | ok / friction / human-only / blocked (policy: …) / attached / missing / unknown / n/a | 42 s | `cmd` → excerpt |
| 2 | Launch | | | |
| 3a | Observe | | | |
| 3b | Effects — DB · HTTP · mail · files · messages | | | |
| 4a | Reach — state reachable: <target state> | | <n steps / human> | |
| 4b | Reach — bug reproduced | | | |
| 5 | Act | | | |
| 6 | Assert — <pass/fail · comparison · measurement> | | | |
| 7 | Reset | | | |
| 8 | Cycle — edit reaches the app via <rebuild / publish / hot-patch> | | edit→observe in N s | |

One column per variant when the task names variants.

## Side effects of probing
`git status` / user-data checksums before → after; every file a run wrote; processes, ports,
forwards cleaned up.

## Existing handles found (and how they score on the five criteria)

## Gaps, ranked

For each proposed handle, say which way: live · lab · witness.

| Rank | Rung | Gap | Frequency × cost | Proposed handle (live / lab / witness) | Build cost |
|------|------|-----|------------------|----------------------------------------|------------|

## Decisions (from the grill)
- <question> → <answer>, by <who>

## Built
| Handle | Command | Gate (why it cannot ship) | Rung before → after |
|--------|---------|---------------------------|---------------------|

## Left open
- <gap>, owner, why not now
