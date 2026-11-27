## Distribution (cells reached; each cell counted once per map)

| Run | Arm | Model | Maps | Cards · scripts · loop-only | Cells reached, by way: Bring out · Witness · Reach in | by level: Unit · Piece · Operation · Journey | Cells reached per map (of 12) | Busiest cell share (mean ± sd) | M1 loop-only | M1 cells | Author misfit |
|---|---|---|---|---|---|---|---|---|---|---|---|
| before | skill | haiku | 24 | 125 · 84 · 44 | 32% · 21% · 46% | 19% · 24% · 41% · 15% | 4.1 | 0.46 ± 0.16 | 11/24 | loop ×11, journey × reach in ×4, operation × bring out ×2, piece × reach in ×2, unit × bring out ×2, piece × bring out ×2, operation × reach in ×1 | 0 |
| before | skill | sonnet | 24 | 121 · 125 · 43 | 39% · 19% · 42% | 16% · 26% · 41% · 17% | 4.2 | 0.49 ± 0.16 | 18/24 | loop ×18, journey × bring out ×1, operation × bring out ×1, piece × reach in ×1, journey × reach in ×1, unit × bring out ×1, piece × bring out ×1 | 0 |
| v2 | baseline | haiku | 24 | 318 · 5 · 165 | 60% · 12% · 27% | 22% · 26% · 31% · 20% | 4.0 | 0.46 ± 0.17 | 12/24 | loop ×12, unit × bring out ×7, operation × bring out ×2, piece × bring out ×2, piece × reach in ×1 | 0 |
| v2 | baseline | sonnet | 24 | 254 · 4 · 100 | 76% · 5% · 18% | 26% · 37% · 18% · 17% | 3.3 | 0.53 ± 0.14 | 16/24 | loop ×16, piece × bring out ×3, unit × bring out ×3, journey × bring out ×2 | 0 |
| v2 | skill | haiku | 24 | 87 · 51 · 28 | 31% · 27% · 41% | 8% · 25% · 44% · 21% | 3.1 | 0.50 ± 0.18 | 1/24 | piece × bring out ×7, operation × witness ×3, operation × bring out ×3, piece × reach in ×3, journey × bring out ×2, unit × witness ×1, operation × reach in ×1, journey × witness ×1, unit × bring out ×1, loop ×1, journey × reach in ×1 | 0 |
| v2 | skill | sonnet | 24 | 93 · 94 · 32 | 40% · 23% · 35% | 13% · 30% · 41% · 14% | 4.0 | 0.45 ± 0.13 | 1/24 | unit × bring out ×5, piece × bring out ×5, operation × witness ×4, operation × bring out ×3, piece × reach in ×3, operation × reach in ×2, loop ×1, journey × bring out ×1 | 0 |
| v3 | skill | haiku | 24 | 103 · 43 · 39 | 35% · 28% · 35% | 7% · 22% · 44% · 25% | 3.4 | 0.41 ± 0.14 | 0/24 | piece × bring out ×7, unit × bring out ×4, operation × witness ×4, journey × reach in ×4, piece × reach in ×2, operation × bring out ×1, operation × reach in ×1, journey × witness ×1 | 0 |
| v3 | skill | sonnet | 24 | 104 · 86 · 39 | 50% · 21% · 28% | 16% · 28% · 36% · 18% | 4.0 | 0.41 ± 0.11 | 5/24 | unit × bring out ×5, loop ×5, operation × bring out ×4, operation × witness ×4, piece × bring out ×2, piece × reach in ×2, journey × reach in ×1, journey × bring out ×1 | 0 |

## Against the answer keys

| Run | Arm | Model | Maps | Proposals per map (designed) | **Recall, designed** | **Precision, designed** | Recall, all proposals | Precision, all | M1 in an accepted cell |
|---|---|---|---|---|---|---|---|---|---|
| before | skill | haiku | 24 | 8.7 (96%) | 52% (65/126) | 97% (65/67) | 52% (66/126) | 97% (66/68) | 4/24 |
| before | skill | sonnet | 24 | 10.2 (95%) | 59% (74/126) | 96% (74/77) | 61% (77/126) | 96% (77/80) | 2/24 |
| v2 | baseline | haiku | 24 | 13.5 (48%) | 42% (53/126) | 96% (53/55) | 59% (74/126) | 97% (74/76) | 7/24 |
| v2 | baseline | sonnet | 24 | 10.8 (58%) | 44% (55/126) | 95% (55/58) | 54% (68/126) | 94% (68/72) | 0/24 |
| v2 | skill | haiku | 24 | 5.8 (92%) | 44% (56/126) | 97% (56/58) | 48% (60/126) | 97% (60/62) | 5/24 |
| v2 | skill | sonnet | 24 | 7.8 (93%) | 55% (69/126) | 96% (69/72) | 56% (71/126) | 96% (71/74) | 6/24 |
| v3 | skill | haiku | 24 | 6.1 (85%) | 46% (58/126) | 95% (58/61) | 51% (64/126) | 96% (64/67) | 4/24 |
| v3 | skill | sonnet | 24 | 7.9 (91%) | 58% (73/126) | 94% (73/78) | 60% (75/126) | 94% (75/80) | 6/24 |

Keys used: assay, codetriage, jaffle-shop, miniflux, motu, subscription-payments, tps-demo, vue-realworld. **Recall** = expected (`propose`) cells the map reaches; **precision** = those hits ÷ (hits + `leave` cells it reaches anyway). **Designed** counts only proposals with a command or usage the agent could run — the headline, since a named tool gives the agent nothing to call.

## Run to run

| Run | Scenario | Arm | Model | Runs | M1 cells across runs | Busiest share per run |
|---|---|---|---|---|---|---|
| before | assay | skill | haiku | 3 | unit × bring out, unit × bring out, piece × bring out | 0.33, 0.33, 0.75 |
| before | assay | skill | sonnet | 3 | unit × bring out, loop, piece × bring out | 0.33, 0.33, 0.33 |
| before | codetriage | skill | haiku | 3 | loop, loop, loop | 0.29, 0.43, 0.42 |
| before | codetriage | skill | sonnet | 3 | loop, loop, loop | 0.33, 0.64, 0.42 |
| before | jaffle-shop | skill | haiku | 3 | operation × reach in, operation × bring out, operation × bring out | 0.50, 0.38, 0.40 |
| before | jaffle-shop | skill | sonnet | 3 | loop, journey × bring out, operation × bring out | 0.50, 0.70, 0.45 |
| before | miniflux | skill | haiku | 3 | loop, loop, loop | 0.30, 0.27, 0.56 |
| before | miniflux | skill | sonnet | 3 | loop, loop, loop | 0.56, 0.40, 0.45 |
| before | motu | skill | haiku | 3 | piece × bring out, loop, loop | 0.33, 0.50, 0.40 |
| before | motu | skill | sonnet | 3 | loop, loop, loop | 0.33, 0.20, 0.75 |
| before | subscription-payments | skill | haiku | 3 | loop, loop, loop | 0.57, 0.43, 0.57 |
| before | subscription-payments | skill | sonnet | 3 | loop, loop, loop | 0.55, 0.47, 0.30 |
| before | tps-demo | skill | haiku | 3 | journey × reach in, journey × reach in, journey × reach in | 0.75, 0.75, 0.78 |
| before | tps-demo | skill | sonnet | 3 | loop, loop, loop | 0.83, 0.60, 0.70 |
| before | vue-realworld | skill | haiku | 3 | piece × reach in, piece × reach in, journey × reach in | 0.29, 0.43, 0.30 |
| before | vue-realworld | skill | sonnet | 3 | piece × reach in, loop, journey × reach in | 0.56, 0.56, 0.50 |
| v2 | assay | baseline | haiku | 3 | unit × bring out, piece × bring out, unit × bring out | 0.43, 0.80, 0.43 |
| v2 | assay | baseline | sonnet | 3 | loop, loop, loop | 0.40, 0.50, 0.50 |
| v2 | assay | skill | haiku | 3 | operation × bring out, operation × bring out, unit × bring out | 0.50, 0.50, 0.29 |
| v2 | assay | skill | sonnet | 3 | piece × bring out, unit × bring out, unit × bring out | 0.50, 0.67, 0.50 |
| v2 | codetriage | baseline | haiku | 3 | loop, loop, loop | 0.22, 0.43, 0.29 |
| v2 | codetriage | baseline | sonnet | 3 | piece × bring out, loop, loop | 0.55, 0.75, 0.67 |
| v2 | codetriage | skill | haiku | 3 | unit × witness, journey × bring out, operation × witness | 0.75, 0.33, 0.57 |
| v2 | codetriage | skill | sonnet | 3 | operation × bring out, unit × bring out, operation × witness | 0.60, 0.38, 0.25 |
| v2 | jaffle-shop | baseline | haiku | 3 | operation × bring out, loop, loop | 0.40, 0.40, 0.43 |
| v2 | jaffle-shop | baseline | sonnet | 3 | loop, journey × bring out, journey × bring out | 0.44, 0.57, 0.75 |
| v2 | jaffle-shop | skill | haiku | 3 | piece × bring out, operation × bring out, piece × reach in | 0.33, 0.33, 0.33 |
| v2 | jaffle-shop | skill | sonnet | 3 | loop, piece × bring out, operation × bring out | 0.40, 0.33, 0.43 |
| v2 | miniflux | baseline | haiku | 3 | loop, unit × bring out, loop | 0.38, 0.40, 0.30 |
| v2 | miniflux | baseline | sonnet | 3 | loop, loop, loop | 0.62, 0.50, 0.83 |
| v2 | miniflux | skill | haiku | 3 | operation × witness, operation × reach in, operation × witness | 0.40, 0.67, 0.71 |
| v2 | miniflux | skill | sonnet | 3 | operation × reach in, operation × witness, operation × reach in | 0.38, 0.50, 0.62 |
| v2 | motu | baseline | haiku | 3 | piece × reach in, loop, loop | 0.80, 0.57, 0.50 |
| v2 | motu | baseline | sonnet | 3 | loop, loop, loop | 0.60, 0.50, 0.43 |
| v2 | motu | skill | haiku | 3 | loop, journey × reach in, piece × bring out | 0.50, 0.50, 0.33 |
| v2 | motu | skill | sonnet | 3 | piece × bring out, operation × bring out, unit × bring out | 0.67, 0.50, 0.50 |
| v2 | subscription-payments | baseline | haiku | 3 | unit × bring out, unit × bring out, unit × bring out | 0.40, 0.57, 0.71 |
| v2 | subscription-payments | baseline | sonnet | 3 | loop, loop, piece × bring out | 0.50, 0.25, 0.50 |
| v2 | subscription-payments | skill | haiku | 3 | piece × bring out, piece × bring out, piece × bring out | 0.29, 0.43, 0.43 |
| v2 | subscription-payments | skill | sonnet | 3 | operation × witness, unit × bring out, operation × witness | 0.33, 0.25, 0.50 |
| v2 | tps-demo | baseline | haiku | 3 | operation × bring out, piece × bring out, loop | 0.40, 0.40, 0.57 |
| v2 | tps-demo | baseline | sonnet | 3 | unit × bring out, loop, piece × bring out | 0.40, 0.38, 0.38 |
| v2 | tps-demo | skill | haiku | 3 | piece × reach in, piece × bring out, piece × reach in | 0.50, 0.29, 0.67 |
| v2 | tps-demo | skill | sonnet | 3 | piece × bring out, piece × bring out, piece × reach in | 0.33, 0.57, 0.57 |
| v2 | vue-realworld | baseline | haiku | 3 | loop, loop, unit × bring out | 0.33, 0.17, 0.75 |
| v2 | vue-realworld | baseline | sonnet | 3 | loop, unit × bring out, unit × bring out | 0.43, 0.56, 0.62 |
| v2 | vue-realworld | skill | haiku | 3 | journey × bring out, journey × witness, piece × bring out | 0.75, 0.50, 1.00 |
| v2 | vue-realworld | skill | sonnet | 3 | piece × reach in, journey × bring out, piece × reach in | 0.25, 0.38, 0.40 |
| v3 | assay | skill | haiku | 3 | unit × bring out, unit × bring out, unit × bring out | 0.67, 0.33, 0.33 |
| v3 | assay | skill | sonnet | 3 | unit × bring out, unit × bring out, piece × bring out | 0.25, 0.50, 0.67 |
| v3 | codetriage | skill | haiku | 3 | operation × witness, unit × bring out, operation × witness | 0.33, 0.25, 0.50 |
| v3 | codetriage | skill | sonnet | 3 | loop, unit × bring out, loop | 0.50, 0.38, 0.29 |
| v3 | jaffle-shop | skill | haiku | 3 | operation × bring out, piece × bring out, piece × bring out | 0.25, 0.33, 0.25 |
| v3 | jaffle-shop | skill | sonnet | 3 | operation × bring out, operation × bring out, operation × bring out | 0.38, 0.43, 0.29 |
| v3 | miniflux | skill | haiku | 3 | operation × witness, journey × reach in, operation × reach in | 0.75, 0.50, 0.29 |
| v3 | miniflux | skill | sonnet | 3 | operation × witness, operation × witness, loop | 0.29, 0.45, 0.50 |
| v3 | motu | skill | haiku | 3 | journey × reach in, journey × reach in, piece × bring out | 0.50, 0.50, 0.50 |
| v3 | motu | skill | sonnet | 3 | unit × bring out, piece × bring out, operation × bring out | 0.33, 0.33, 0.33 |
| v3 | subscription-payments | skill | haiku | 3 | operation × witness, piece × bring out, piece × bring out | 0.50, 0.33, 0.29 |
| v3 | subscription-payments | skill | sonnet | 3 | unit × bring out, operation × witness, operation × witness | 0.44, 0.40, 0.43 |
| v3 | tps-demo | skill | haiku | 3 | piece × bring out, piece × bring out, piece × reach in | 0.60, 0.60, 0.29 |
| v3 | tps-demo | skill | sonnet | 3 | journey × reach in, loop, loop | 0.25, 0.43, 0.50 |
| v3 | vue-realworld | skill | haiku | 3 | journey × witness, journey × reach in, piece × reach in | 0.40, 0.33, 0.33 |
| v3 | vue-realworld | skill | sonnet | 3 | piece × reach in, journey × bring out, piece × reach in | 0.60, 0.29, 0.50 |

## Per map

| Run | Scenario | Model | Arm | # | Cards | Cells | Busiest | M1 | motu | assay |
|---|---|---|---|---|---|---|---|---|---|---|
| v2 | assay | haiku | baseline | 1 | 11 | 4 | piece × bring out (0.43) | unit × bring out | absent | absent |
| v2 | assay | haiku | baseline | 2 | 9 | 2 | piece × bring out (0.80) | piece × bring out | absent | proposed |
| v2 | assay | haiku | baseline | 3 | 17 | 4 | piece × bring out (0.43) | unit × bring out | absent | proposed |
| before | assay | haiku | skill | 1 | 5 | 3 | unit × bring out (0.33) | unit × bring out | absent | absent |
| before | assay | haiku | skill | 2 | 4 | 3 | unit × bring out (0.33) | unit × bring out | absent | absent |
| before | assay | haiku | skill | 3 | 4 | 2 | piece × bring out (0.75) | piece × bring out | absent | proposed |
| v2 | assay | haiku | skill | 1 | 4 | 2 | operation × bring out (0.50) | operation × bring out | absent | absent |
| v2 | assay | haiku | skill | 2 | 3 | 2 | operation × bring out (0.50) | operation × bring out | absent | absent |
| v2 | assay | haiku | skill | 3 | 9 | 5 | operation × witness (0.29) | unit × bring out | absent | proposed |
| v3 | assay | haiku | skill | 1 | 3 | 2 | unit × bring out (0.67) | unit × bring out | absent | absent |
| v3 | assay | haiku | skill | 2 | 3 | 3 | unit × bring out (0.33) | unit × bring out | absent | absent |
| v3 | assay | haiku | skill | 3 | 4 | 3 | unit × bring out (0.33) | unit × bring out | absent | absent |
| v2 | assay | sonnet | baseline | 1 | 10 | 3 | unit × bring out (0.40) | loop | absent | absent |
| v2 | assay | sonnet | baseline | 2 | 11 | 3 | operation × bring out (0.50) | loop | absent | absent |
| v2 | assay | sonnet | baseline | 3 | 10 | 2 | operation × bring out (0.50) | loop | absent | absent |
| before | assay | sonnet | skill | 1 | 4 | 3 | unit × bring out (0.33) | unit × bring out | absent | proposed |
| before | assay | sonnet | skill | 2 | 3 | 3 | operation × bring out (0.33) | loop | absent | absent |
| before | assay | sonnet | skill | 3 | 4 | 3 | piece × bring out (0.33) | piece × bring out | absent | absent |
| v2 | assay | sonnet | skill | 1 | 8 | 3 | operation × bring out (0.50) | piece × bring out | absent | rejected |
| v2 | assay | sonnet | skill | 2 | 3 | 3 | operation × bring out (0.67) | unit × bring out | absent | absent |
| v2 | assay | sonnet | skill | 3 | 2 | 3 | operation × bring out (0.50) | unit × bring out | absent | absent |
| v3 | assay | sonnet | skill | 1 | 5 | 4 | unit × bring out (0.25) | unit × bring out | absent | absent |
| v3 | assay | sonnet | skill | 2 | 4 | 3 | piece × bring out (0.50) | unit × bring out | absent | absent |
| v3 | assay | sonnet | skill | 3 | 4 | 2 | piece × bring out (0.67) | piece × bring out | absent | absent |
| v2 | codetriage | haiku | baseline | 1 | 15 | 6 | piece × bring out (0.22) | loop | absent | absent |
| v2 | codetriage | haiku | baseline | 2 | 14 | 5 | piece × bring out (0.43) | loop | absent | absent |
| v2 | codetriage | haiku | baseline | 3 | 16 | 5 | operation × witness (0.29) | loop | absent | absent |
| before | codetriage | haiku | skill | 1 | 6 | 6 | journey × reach in (0.29) | loop | absent | absent |
| before | codetriage | haiku | skill | 2 | 6 | 5 | operation × reach in (0.43) | loop | absent | absent |
| before | codetriage | haiku | skill | 3 | 8 | 7 | operation × reach in (0.42) | loop | absent | absent |
| v2 | codetriage | haiku | skill | 1 | 5 | 2 | operation × witness (0.75) | unit × witness | absent | absent |
| v2 | codetriage | haiku | skill | 2 | 4 | 3 | journey × bring out (0.33) | journey × bring out | absent | absent |
| v2 | codetriage | haiku | skill | 3 | 5 | 4 | operation × reach in (0.57) | operation × witness | absent | absent |
| v3 | codetriage | haiku | skill | 1 | 4 | 3 | operation × witness (0.33) | operation × witness | absent | absent |
| v3 | codetriage | haiku | skill | 2 | 3 | 4 | unit × bring out (0.25) | unit × bring out | absent | absent |
| v3 | codetriage | haiku | skill | 3 | 4 | 2 | operation × witness (0.50) | operation × witness | absent | absent |
| v2 | codetriage | sonnet | baseline | 1 | 14 | 4 | piece × bring out (0.55) | piece × bring out | absent | absent |
| v2 | codetriage | sonnet | baseline | 2 | 9 | 2 | piece × bring out (0.75) | loop | absent | absent |
| v2 | codetriage | sonnet | baseline | 3 | 12 | 3 | piece × bring out (0.67) | loop | absent | absent |
| before | codetriage | sonnet | skill | 1 | 7 | 6 | piece × reach in (0.33) | loop | absent | absent |
| before | codetriage | sonnet | skill | 2 | 5 | 4 | operation × reach in (0.64) | loop | absent | absent |
| before | codetriage | sonnet | skill | 3 | 5 | 6 | operation × reach in (0.42) | loop | absent | absent |
| v2 | codetriage | sonnet | skill | 1 | 5 | 5 | operation × reach in (0.60) | operation × bring out | absent | absent |
| v2 | codetriage | sonnet | skill | 2 | 4 | 5 | operation × reach in (0.38) | unit × bring out | absent | absent |
| v2 | codetriage | sonnet | skill | 3 | 2 | 4 | operation × reach in (0.25) | operation × witness | absent | absent |
| v3 | codetriage | sonnet | skill | 1 | 3 | 2 | operation × witness (0.50) | loop | absent | absent |
| v3 | codetriage | sonnet | skill | 2 | 5 | 5 | operation × reach in (0.38) | unit × bring out | absent | absent |
| v3 | codetriage | sonnet | skill | 3 | 4 | 5 | operation × reach in (0.29) | loop | absent | absent |
| v2 | jaffle-shop | haiku | baseline | 1 | 10 | 4 | operation × bring out (0.40) | operation × bring out | absent | absent |
| v2 | jaffle-shop | haiku | baseline | 2 | 9 | 3 | operation × bring out (0.40) | loop | absent | absent |
| v2 | jaffle-shop | haiku | baseline | 3 | 12 | 4 | piece × bring out (0.43) | loop | absent | absent |
| before | jaffle-shop | haiku | skill | 1 | 3 | 4 | operation × reach in (0.50) | operation × reach in | absent | absent |
| before | jaffle-shop | haiku | skill | 2 | 5 | 5 | operation × reach in (0.38) | operation × bring out | absent | absent |
| before | jaffle-shop | haiku | skill | 3 | 3 | 4 | piece × witness (0.40) | operation × bring out | absent | absent |
| v2 | jaffle-shop | haiku | skill | 1 | 2 | 3 | piece × bring out (0.33) | piece × bring out | absent | absent |
| v2 | jaffle-shop | haiku | skill | 2 | 1 | 3 | operation × bring out (0.33) | operation × bring out | absent | absent |
| v2 | jaffle-shop | haiku | skill | 3 | 1 | 3 | piece × reach in (0.33) | piece × reach in | absent | absent |
| v3 | jaffle-shop | haiku | skill | 1 | 3 | 4 | operation × witness (0.25) | operation × bring out | absent | absent |
| v3 | jaffle-shop | haiku | skill | 2 | 6 | 3 | piece × bring out (0.33) | piece × bring out | absent | absent |
| v3 | jaffle-shop | haiku | skill | 3 | 5 | 4 | piece × bring out (0.25) | piece × bring out | absent | absent |
| v2 | jaffle-shop | sonnet | baseline | 1 | 14 | 4 | piece × bring out (0.44) | loop | absent | absent |
| v2 | jaffle-shop | sonnet | baseline | 2 | 10 | 4 | piece × bring out (0.57) | journey × bring out | absent | absent |
| v2 | jaffle-shop | sonnet | baseline | 3 | 13 | 2 | piece × bring out (0.75) | journey × bring out | absent | absent |
| before | jaffle-shop | sonnet | skill | 1 | 5 | 3 | operation × bring out (0.50) | loop | absent | absent |
| before | jaffle-shop | sonnet | skill | 2 | 5 | 4 | piece × bring out (0.70) | journey × bring out | absent | absent |
| before | jaffle-shop | sonnet | skill | 3 | 3 | 4 | piece × bring out (0.45) | operation × bring out | absent | absent |
| v2 | jaffle-shop | sonnet | skill | 1 | 3 | 4 | unit × bring out (0.40) | loop | absent | absent |
| v2 | jaffle-shop | sonnet | skill | 2 | 1 | 3 | piece × bring out (0.33) | piece × bring out | absent | absent |
| v2 | jaffle-shop | sonnet | skill | 3 | 1 | 4 | piece × bring out (0.43) | operation × bring out | absent | absent |
| v3 | jaffle-shop | sonnet | skill | 1 | 2 | 5 | operation × bring out (0.38) | operation × bring out | absent | absent |
| v3 | jaffle-shop | sonnet | skill | 2 | 4 | 4 | piece × bring out (0.43) | operation × bring out | absent | absent |
| v3 | jaffle-shop | sonnet | skill | 3 | 2 | 4 | operation × bring out (0.29) | operation × bring out | absent | absent |
| v2 | miniflux | haiku | baseline | 1 | 15 | 5 | piece × bring out (0.38) | loop | absent | absent |
| v2 | miniflux | haiku | baseline | 2 | 17 | 3 | unit × bring out (0.40) | unit × bring out | absent | absent |
| v2 | miniflux | haiku | baseline | 3 | 16 | 6 | unit × bring out (0.30) | loop | absent | absent |
| before | miniflux | haiku | skill | 1 | 8 | 5 | unit × reach in (0.30) | loop | absent | absent |
| before | miniflux | haiku | skill | 2 | 8 | 6 | piece × reach in (0.27) | loop | absent | absent |
| before | miniflux | haiku | skill | 3 | 5 | 5 | operation × reach in (0.56) | loop | absent | absent |
| v2 | miniflux | haiku | skill | 1 | 2 | 4 | operation × bring out (0.40) | operation × witness | absent | absent |
| v2 | miniflux | haiku | skill | 2 | 3 | 3 | operation × reach in (0.67) | operation × reach in | absent | absent |
| v2 | miniflux | haiku | skill | 3 | 5 | 2 | operation × reach in (0.71) | operation × witness | absent | absent |
| v3 | miniflux | haiku | skill | 1 | 2 | 2 | operation × reach in (0.75) | operation × witness | absent | absent |
| v3 | miniflux | haiku | skill | 2 | 6 | 3 | operation × witness (0.50) | journey × reach in | absent | absent |
| v3 | miniflux | haiku | skill | 3 | 1 | 5 | operation × reach in (0.29) | operation × reach in | absent | absent |
| v2 | miniflux | sonnet | baseline | 1 | 9 | 3 | piece × bring out (0.62) | loop | absent | absent |
| v2 | miniflux | sonnet | baseline | 2 | 11 | 3 | unit × bring out (0.50) | loop | absent | absent |
| v2 | miniflux | sonnet | baseline | 3 | 9 | 2 | piece × bring out (0.83) | loop | absent | absent |
| before | miniflux | sonnet | skill | 1 | 7 | 5 | operation × reach in (0.56) | loop | absent | absent |
| before | miniflux | sonnet | skill | 2 | 5 | 5 | operation × reach in (0.40) | loop | absent | absent |
| before | miniflux | sonnet | skill | 3 | 6 | 5 | operation × reach in (0.45) | loop | absent | absent |
| v2 | miniflux | sonnet | skill | 1 | 3 | 5 | piece × reach in (0.38) | operation × reach in | absent | absent |
| v2 | miniflux | sonnet | skill | 2 | 5 | 5 | operation × reach in (0.50) | operation × witness | absent | absent |
| v2 | miniflux | sonnet | skill | 3 | 4 | 3 | operation × reach in (0.62) | operation × reach in | absent | absent |
| v3 | miniflux | sonnet | skill | 1 | 3 | 5 | piece × reach in (0.29) | operation × witness | absent | absent |
| v3 | miniflux | sonnet | skill | 2 | 9 | 4 | operation × reach in (0.45) | operation × witness | absent | absent |
| v3 | miniflux | sonnet | skill | 3 | 4 | 4 | operation × reach in (0.50) | loop | absent | absent |
| v2 | motu | haiku | baseline | 1 | 11 | 2 | piece × bring out (0.80) | piece × reach in | absent | absent |
| v2 | motu | haiku | baseline | 2 | 12 | 4 | piece × bring out (0.57) | loop | absent | absent |
| v2 | motu | haiku | baseline | 3 | 11 | 3 | piece × bring out (0.50) | loop | proposed | absent |
| before | motu | haiku | skill | 1 | 6 | 3 | operation × reach in (0.33) | piece × bring out | proposed | absent |
| before | motu | haiku | skill | 2 | 4 | 2 | journey × reach in (0.50) | loop | absent | absent |
| before | motu | haiku | skill | 3 | 4 | 4 | operation × reach in (0.40) | loop | absent | absent |
| v2 | motu | haiku | skill | 1 | 4 | 2 | journey × reach in (0.50) | loop | absent | absent |
| v2 | motu | haiku | skill | 2 | 4 | 2 | journey × reach in (0.50) | journey × reach in | absent | absent |
| v2 | motu | haiku | skill | 3 | 4 | 3 | piece × bring out (0.33) | piece × bring out | proposed | absent |
| v3 | motu | haiku | skill | 1 | 3 | 2 | journey × reach in (0.50) | journey × reach in | absent | absent |
| v3 | motu | haiku | skill | 2 | 9 | 2 | journey × reach in (0.50) | journey × reach in | absent | absent |
| v3 | motu | haiku | skill | 3 | 6 | 3 | piece × bring out (0.50) | piece × bring out | absent | absent |
| v2 | motu | sonnet | baseline | 1 | 10 | 3 | piece × bring out (0.60) | loop | proposed | absent |
| v2 | motu | sonnet | baseline | 2 | 10 | 2 | piece × bring out (0.50) | loop | proposed | absent |
| v2 | motu | sonnet | baseline | 3 | 10 | 4 | piece × bring out (0.43) | loop | proposed | absent |
| before | motu | sonnet | skill | 1 | 10 | 3 | piece × reach in (0.33) | loop | absent | absent |
| before | motu | sonnet | skill | 2 | 6 | 5 | unit × bring out (0.20) | loop | proposed | absent |
| before | motu | sonnet | skill | 3 | 4 | 2 | piece × bring out (0.75) | loop | absent | absent |
| v2 | motu | sonnet | skill | 1 | 4 | 2 | piece × bring out (0.67) | piece × bring out | absent | absent |
| v2 | motu | sonnet | skill | 2 | 2 | 2 | operation × bring out (0.50) | operation × bring out | proposed | absent |
| v2 | motu | sonnet | skill | 3 | 3 | 2 | unit × bring out (0.50) | unit × bring out | absent | absent |
| v3 | motu | sonnet | skill | 1 | 5 | 3 | unit × bring out (0.33) | unit × bring out | absent | absent |
| v3 | motu | sonnet | skill | 2 | 2 | 3 | piece × bring out (0.33) | piece × bring out | absent | absent |
| v3 | motu | sonnet | skill | 3 | 4 | 3 | operation × bring out (0.33) | operation × bring out | absent | absent |
| v2 | subscription-payments | haiku | baseline | 1 | 19 | 6 | unit × bring out (0.40) | unit × bring out | absent | absent |
| v2 | subscription-payments | haiku | baseline | 2 | 16 | 4 | unit × bring out (0.57) | unit × bring out | absent | absent |
| v2 | subscription-payments | haiku | baseline | 3 | 12 | 2 | unit × bring out (0.71) | unit × bring out | absent | absent |
| before | subscription-payments | haiku | skill | 1 | 2 | 3 | operation × reach in (0.57) | loop | absent | absent |
| before | subscription-payments | haiku | skill | 2 | 6 | 4 | unit × witness (0.43) | loop | absent | absent |
| before | subscription-payments | haiku | skill | 3 | 3 | 3 | operation × reach in (0.57) | loop | absent | absent |
| v2 | subscription-payments | haiku | skill | 1 | 6 | 6 | operation × reach in (0.29) | piece × bring out | absent | absent |
| v2 | subscription-payments | haiku | skill | 2 | 4 | 4 | operation × reach in (0.43) | piece × bring out | absent | absent |
| v2 | subscription-payments | haiku | skill | 3 | 3 | 5 | operation × reach in (0.43) | piece × bring out | absent | absent |
| v3 | subscription-payments | haiku | skill | 1 | 5 | 4 | operation × reach in (0.50) | operation × witness | absent | absent |
| v3 | subscription-payments | haiku | skill | 2 | 4 | 3 | operation × reach in (0.33) | piece × bring out | absent | absent |
| v3 | subscription-payments | haiku | skill | 3 | 5 | 6 | operation × witness (0.29) | piece × bring out | absent | absent |
| v2 | subscription-payments | sonnet | baseline | 1 | 9 | 3 | operation × reach in (0.50) | loop | absent | absent |
| v2 | subscription-payments | sonnet | baseline | 2 | 10 | 4 | unit × bring out (0.25) | loop | absent | absent |
| v2 | subscription-payments | sonnet | baseline | 3 | 11 | 4 | piece × bring out (0.50) | piece × bring out | absent | absent |
| before | subscription-payments | sonnet | skill | 1 | 4 | 4 | operation × reach in (0.55) | loop | absent | absent |
| before | subscription-payments | sonnet | skill | 2 | 6 | 6 | unit × reach in (0.47) | loop | absent | absent |
| before | subscription-payments | sonnet | skill | 3 | 4 | 6 | unit × reach in (0.30) | loop | absent | absent |
| v2 | subscription-payments | sonnet | skill | 1 | 4 | 6 | operation × reach in (0.33) | operation × witness | absent | absent |
| v2 | subscription-payments | sonnet | skill | 2 | 7 | 4 | unit × bring out (0.25) | unit × bring out | absent | absent |
| v2 | subscription-payments | sonnet | skill | 3 | 6 | 4 | operation × reach in (0.50) | operation × witness | absent | absent |
| v3 | subscription-payments | sonnet | skill | 1 | 7 | 5 | operation × reach in (0.44) | unit × bring out | absent | absent |
| v3 | subscription-payments | sonnet | skill | 2 | 3 | 4 | operation × bring out (0.40) | operation × witness | absent | absent |
| v3 | subscription-payments | sonnet | skill | 3 | 4 | 5 | operation × reach in (0.43) | operation × witness | absent | absent |
| v2 | tps-demo | haiku | baseline | 1 | 9 | 4 | unit × bring out (0.40) | operation × bring out | absent | absent |
| v2 | tps-demo | haiku | baseline | 2 | 9 | 3 | piece × bring out (0.40) | piece × bring out | absent | absent |
| v2 | tps-demo | haiku | baseline | 3 | 12 | 4 | unit × bring out (0.57) | loop | absent | absent |
| before | tps-demo | haiku | skill | 1 | 6 | 3 | journey × reach in (0.75) | journey × reach in | absent | absent |
| before | tps-demo | haiku | skill | 2 | 6 | 3 | journey × reach in (0.75) | journey × reach in | absent | absent |
| before | tps-demo | haiku | skill | 3 | 8 | 3 | journey × reach in (0.78) | journey × reach in | absent | absent |
| v2 | tps-demo | haiku | skill | 1 | 2 | 3 | piece × reach in (0.50) | piece × reach in | absent | absent |
| v2 | tps-demo | haiku | skill | 2 | 5 | 4 | piece × bring out (0.29) | piece × bring out | absent | absent |
| v2 | tps-demo | haiku | skill | 3 | 3 | 3 | piece × reach in (0.67) | piece × reach in | absent | absent |
| v3 | tps-demo | haiku | skill | 1 | 5 | 4 | operation × reach in (0.60) | piece × bring out | absent | absent |
| v3 | tps-demo | haiku | skill | 2 | 6 | 2 | piece × reach in (0.60) | piece × bring out | absent | absent |
| v3 | tps-demo | haiku | skill | 3 | 5 | 5 | operation × reach in (0.29) | piece × reach in | absent | absent |
| v2 | tps-demo | sonnet | baseline | 1 | 13 | 4 | piece × bring out (0.40) | unit × bring out | absent | absent |
| v2 | tps-demo | sonnet | baseline | 2 | 7 | 5 | piece × bring out (0.38) | loop | absent | absent |
| v2 | tps-demo | sonnet | baseline | 3 | 9 | 4 | piece × bring out (0.38) | piece × bring out | absent | absent |
| before | tps-demo | sonnet | skill | 1 | 5 | 3 | journey × reach in (0.83) | loop | absent | absent |
| before | tps-demo | sonnet | skill | 2 | 4 | 3 | journey × reach in (0.60) | loop | absent | absent |
| before | tps-demo | sonnet | skill | 3 | 5 | 4 | journey × reach in (0.70) | loop | absent | absent |
| v2 | tps-demo | sonnet | skill | 1 | 5 | 6 | operation × reach in (0.33) | piece × bring out | absent | absent |
| v2 | tps-demo | sonnet | skill | 2 | 3 | 4 | operation × reach in (0.57) | piece × bring out | absent | absent |
| v2 | tps-demo | sonnet | skill | 3 | 7 | 5 | journey × reach in (0.57) | piece × reach in | absent | absent |
| v3 | tps-demo | sonnet | skill | 1 | 4 | 5 | journey × reach in (0.25) | journey × reach in | absent | absent |
| v3 | tps-demo | sonnet | skill | 2 | 7 | 5 | piece × bring out (0.43) | loop | absent | absent |
| v3 | tps-demo | sonnet | skill | 3 | 6 | 5 | operation × reach in (0.50) | loop | absent | absent |
| v2 | vue-realworld | haiku | baseline | 1 | 15 | 3 | operation × bring out (0.33) | loop | absent | absent |
| v2 | vue-realworld | haiku | baseline | 2 | 15 | 6 | operation × witness (0.17) | loop | absent | absent |
| v2 | vue-realworld | haiku | baseline | 3 | 16 | 3 | unit × bring out (0.75) | unit × bring out | absent | absent |
| before | vue-realworld | haiku | skill | 1 | 5 | 5 | piece × reach in (0.29) | piece × reach in | absent | absent |
| before | vue-realworld | haiku | skill | 2 | 5 | 5 | piece × reach in (0.43) | piece × reach in | absent | absent |
| before | vue-realworld | haiku | skill | 3 | 5 | 6 | piece × reach in (0.30) | journey × reach in | absent | absent |
| v2 | vue-realworld | haiku | skill | 1 | 3 | 2 | piece × reach in (0.75) | journey × bring out | absent | absent |
| v2 | vue-realworld | haiku | skill | 2 | 2 | 3 | journey × reach in (0.50) | journey × witness | absent | absent |
| v2 | vue-realworld | haiku | skill | 3 | 3 | 1 | piece × bring out (1.00) | piece × bring out | absent | absent |
| v3 | vue-realworld | haiku | skill | 1 | 3 | 4 | journey × bring out (0.40) | journey × witness | absent | absent |
| v3 | vue-realworld | haiku | skill | 2 | 4 | 4 | journey × reach in (0.33) | journey × reach in | absent | absent |
| v3 | vue-realworld | haiku | skill | 3 | 4 | 4 | journey × reach in (0.33) | piece × reach in | absent | absent |
| v2 | vue-realworld | sonnet | baseline | 1 | 10 | 4 | unit × bring out (0.43) | loop | absent | absent |
| v2 | vue-realworld | sonnet | baseline | 2 | 13 | 4 | unit × bring out (0.56) | unit × bring out | absent | absent |
| v2 | vue-realworld | sonnet | baseline | 3 | 10 | 4 | unit × bring out (0.62) | unit × bring out | absent | absent |
| before | vue-realworld | sonnet | skill | 1 | 5 | 5 | piece × reach in (0.56) | piece × reach in | absent | absent |
| before | vue-realworld | sonnet | skill | 2 | 6 | 4 | piece × reach in (0.56) | loop | absent | absent |
| before | vue-realworld | sonnet | skill | 3 | 3 | 4 | piece × reach in (0.50) | journey × reach in | absent | absent |
| v2 | vue-realworld | sonnet | skill | 1 | 4 | 4 | piece × reach in (0.25) | piece × reach in | absent | absent |
| v2 | vue-realworld | sonnet | skill | 2 | 4 | 5 | piece × reach in (0.38) | journey × bring out | absent | absent |
| v2 | vue-realworld | sonnet | skill | 3 | 3 | 5 | piece × reach in (0.40) | piece × reach in | absent | absent |
| v3 | vue-realworld | sonnet | skill | 1 | 4 | 3 | piece × reach in (0.60) | piece × reach in | absent | absent |
| v3 | vue-realworld | sonnet | skill | 2 | 6 | 4 | journey × reach in (0.29) | journey × bring out | absent | absent |
| v3 | vue-realworld | sonnet | skill | 3 | 3 | 4 | piece × reach in (0.50) | piece × reach in | absent | absent |
