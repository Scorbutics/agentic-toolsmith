## Distribution (cells reached; each cell counted once per map)

| Run | Arm | Model | Maps | Cards · scripts · loop-only | Cells reached, by way: Bring out · Witness · Reach in | by level: Unit · Piece · Operation · Journey | Cells reached per map (of 12) | Busiest cell share (mean ± sd) | M1 loop-only | M1 cells | Author misfit |
|---|---|---|---|---|---|---|---|---|---|---|---|
| before | skill | haiku | 18 | 98 · 82 · 35 | 28% · 23% · 48% | 19% · 23% · 43% · 13% | 4.6 | 0.47 ± 0.17 | 9/18 | loop ×9, journey × reach in ×4, operation × bring out ×2, piece × reach in ×2, operation × reach in ×1 | 0 |
| before | skill | sonnet | 18 | 90 · 119 · 27 | 35% · 19% · 44% | 14% · 25% · 40% · 18% | 4.5 | 0.53 ± 0.13 | 14/18 | loop ×14, journey × bring out ×1, operation × bring out ×1, piece × reach in ×1, journey × reach in ×1 | 0 |
| v2 | baseline | haiku | 18 | 247 · 0 · 126 | 61% · 11% · 26% | 23% · 23% · 32% · 19% | 4.2 | 0.42 ± 0.15 | 10/18 | loop ×10, unit × bring out ×5, operation × bring out ×2, piece × bring out ×1 | 0 |
| v2 | baseline | sonnet | 18 | 193 · 4 · 64 | 74% · 3% · 22% | 26% · 38% · 15% · 19% | 3.5 | 0.54 ± 0.15 | 10/18 | loop ×10, piece × bring out ×3, unit × bring out ×3, journey × bring out ×2 | 0 |
| v2 | skill | haiku | 18 | 59 · 51 · 18 | 25% · 29% · 44% | 6% · 27% · 46% · 18% | 3.2 | 0.52 ± 0.20 | 0/18 | piece × bring out ×6, operation × witness ×3, piece × reach in ×3, journey × bring out ×2, unit × witness ×1, operation × bring out ×1, operation × reach in ×1, journey × witness ×1 | 0 |
| v2 | skill | sonnet | 18 | 71 · 89 · 26 | 34% · 23% · 41% | 12% · 30% · 40% · 16% | 4.5 | 0.42 ± 0.12 | 1/18 | operation × witness ×4, piece × bring out ×3, piece × reach in ×3, operation × bring out ×2, unit × bring out ×2, operation × reach in ×2, loop ×1, journey × bring out ×1 | 0 |

## Against the answer keys

No answer key filled yet (evals/answer-keys/) — nothing scored against one. Each map is scored once a key exists; judge outputs are cached, so filling a key later costs nothing to score.

## Run to run

| Run | Scenario | Arm | Model | Runs | M1 cells across runs | Busiest share per run |
|---|---|---|---|---|---|---|
| before | codetriage | skill | haiku | 3 | loop, loop, loop | 0.29, 0.43, 0.42 |
| before | codetriage | skill | sonnet | 3 | loop, loop, loop | 0.33, 0.64, 0.42 |
| before | jaffle-shop | skill | haiku | 3 | operation × reach in, operation × bring out, operation × bring out | 0.50, 0.38, 0.40 |
| before | jaffle-shop | skill | sonnet | 3 | loop, journey × bring out, operation × bring out | 0.50, 0.70, 0.45 |
| before | miniflux | skill | haiku | 3 | loop, loop, loop | 0.30, 0.27, 0.56 |
| before | miniflux | skill | sonnet | 3 | loop, loop, loop | 0.56, 0.40, 0.45 |
| before | subscription-payments | skill | haiku | 3 | loop, loop, loop | 0.57, 0.43, 0.57 |
| before | subscription-payments | skill | sonnet | 3 | loop, loop, loop | 0.55, 0.47, 0.30 |
| before | tps-demo | skill | haiku | 3 | journey × reach in, journey × reach in, journey × reach in | 0.75, 0.75, 0.78 |
| before | tps-demo | skill | sonnet | 3 | loop, loop, loop | 0.83, 0.60, 0.70 |
| before | vue-realworld | skill | haiku | 3 | piece × reach in, piece × reach in, journey × reach in | 0.29, 0.43, 0.30 |
| before | vue-realworld | skill | sonnet | 3 | piece × reach in, loop, journey × reach in | 0.56, 0.56, 0.50 |
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

## Per map

| Run | Scenario | Model | Arm | # | Cards | Cells | Busiest | M1 | motu | assay |
|---|---|---|---|---|---|---|---|---|---|---|
| v2 | codetriage | haiku | baseline | 1 | 15 | 6 | piece × bring out (0.22) | loop | absent | absent |
| v2 | codetriage | haiku | baseline | 2 | 14 | 5 | piece × bring out (0.43) | loop | absent | absent |
| v2 | codetriage | haiku | baseline | 3 | 16 | 5 | operation × witness (0.29) | loop | absent | absent |
| before | codetriage | haiku | skill | 1 | 6 | 6 | journey × reach in (0.29) | loop | absent | absent |
| before | codetriage | haiku | skill | 2 | 6 | 5 | operation × reach in (0.43) | loop | absent | absent |
| before | codetriage | haiku | skill | 3 | 8 | 7 | operation × reach in (0.42) | loop | absent | absent |
| v2 | codetriage | haiku | skill | 1 | 5 | 2 | operation × witness (0.75) | unit × witness | absent | absent |
| v2 | codetriage | haiku | skill | 2 | 4 | 3 | journey × bring out (0.33) | journey × bring out | absent | absent |
| v2 | codetriage | haiku | skill | 3 | 5 | 4 | operation × reach in (0.57) | operation × witness | absent | absent |
| v2 | codetriage | sonnet | baseline | 1 | 14 | 4 | piece × bring out (0.55) | piece × bring out | absent | absent |
| v2 | codetriage | sonnet | baseline | 2 | 9 | 2 | piece × bring out (0.75) | loop | absent | absent |
| v2 | codetriage | sonnet | baseline | 3 | 12 | 3 | piece × bring out (0.67) | loop | absent | absent |
| before | codetriage | sonnet | skill | 1 | 7 | 6 | piece × reach in (0.33) | loop | absent | absent |
| before | codetriage | sonnet | skill | 2 | 5 | 4 | operation × reach in (0.64) | loop | absent | absent |
| before | codetriage | sonnet | skill | 3 | 5 | 6 | operation × reach in (0.42) | loop | absent | absent |
| v2 | codetriage | sonnet | skill | 1 | 5 | 5 | operation × reach in (0.60) | operation × bring out | absent | absent |
| v2 | codetriage | sonnet | skill | 2 | 4 | 5 | operation × reach in (0.38) | unit × bring out | absent | absent |
| v2 | codetriage | sonnet | skill | 3 | 2 | 4 | operation × reach in (0.25) | operation × witness | absent | absent |
| v2 | jaffle-shop | haiku | baseline | 1 | 10 | 4 | operation × bring out (0.40) | operation × bring out | absent | absent |
| v2 | jaffle-shop | haiku | baseline | 2 | 9 | 3 | operation × bring out (0.40) | loop | absent | absent |
| v2 | jaffle-shop | haiku | baseline | 3 | 12 | 4 | piece × bring out (0.43) | loop | absent | absent |
| before | jaffle-shop | haiku | skill | 1 | 3 | 4 | operation × reach in (0.50) | operation × reach in | absent | absent |
| before | jaffle-shop | haiku | skill | 2 | 5 | 5 | operation × reach in (0.38) | operation × bring out | absent | absent |
| before | jaffle-shop | haiku | skill | 3 | 3 | 4 | piece × witness (0.40) | operation × bring out | absent | absent |
| v2 | jaffle-shop | haiku | skill | 1 | 2 | 3 | piece × bring out (0.33) | piece × bring out | absent | absent |
| v2 | jaffle-shop | haiku | skill | 2 | 1 | 3 | operation × bring out (0.33) | operation × bring out | absent | absent |
| v2 | jaffle-shop | haiku | skill | 3 | 1 | 3 | piece × reach in (0.33) | piece × reach in | absent | absent |
| v2 | jaffle-shop | sonnet | baseline | 1 | 14 | 4 | piece × bring out (0.44) | loop | absent | absent |
| v2 | jaffle-shop | sonnet | baseline | 2 | 10 | 4 | piece × bring out (0.57) | journey × bring out | absent | absent |
| v2 | jaffle-shop | sonnet | baseline | 3 | 13 | 2 | piece × bring out (0.75) | journey × bring out | absent | absent |
| before | jaffle-shop | sonnet | skill | 1 | 5 | 3 | operation × bring out (0.50) | loop | absent | absent |
| before | jaffle-shop | sonnet | skill | 2 | 5 | 4 | piece × bring out (0.70) | journey × bring out | absent | absent |
| before | jaffle-shop | sonnet | skill | 3 | 3 | 4 | piece × bring out (0.45) | operation × bring out | absent | absent |
| v2 | jaffle-shop | sonnet | skill | 1 | 3 | 4 | unit × bring out (0.40) | loop | absent | absent |
| v2 | jaffle-shop | sonnet | skill | 2 | 1 | 3 | piece × bring out (0.33) | piece × bring out | absent | absent |
| v2 | jaffle-shop | sonnet | skill | 3 | 1 | 4 | piece × bring out (0.43) | operation × bring out | absent | absent |
| v2 | miniflux | haiku | baseline | 1 | 15 | 5 | piece × bring out (0.38) | loop | absent | absent |
| v2 | miniflux | haiku | baseline | 2 | 17 | 3 | unit × bring out (0.40) | unit × bring out | absent | absent |
| v2 | miniflux | haiku | baseline | 3 | 16 | 6 | unit × bring out (0.30) | loop | absent | absent |
| before | miniflux | haiku | skill | 1 | 8 | 5 | unit × reach in (0.30) | loop | absent | absent |
| before | miniflux | haiku | skill | 2 | 8 | 6 | piece × reach in (0.27) | loop | absent | absent |
| before | miniflux | haiku | skill | 3 | 5 | 5 | operation × reach in (0.56) | loop | absent | absent |
| v2 | miniflux | haiku | skill | 1 | 2 | 4 | operation × bring out (0.40) | operation × witness | absent | absent |
| v2 | miniflux | haiku | skill | 2 | 3 | 3 | operation × reach in (0.67) | operation × reach in | absent | absent |
| v2 | miniflux | haiku | skill | 3 | 5 | 2 | operation × reach in (0.71) | operation × witness | absent | absent |
| v2 | miniflux | sonnet | baseline | 1 | 9 | 3 | piece × bring out (0.62) | loop | absent | absent |
| v2 | miniflux | sonnet | baseline | 2 | 11 | 3 | unit × bring out (0.50) | loop | absent | absent |
| v2 | miniflux | sonnet | baseline | 3 | 9 | 2 | piece × bring out (0.83) | loop | absent | absent |
| before | miniflux | sonnet | skill | 1 | 7 | 5 | operation × reach in (0.56) | loop | absent | absent |
| before | miniflux | sonnet | skill | 2 | 5 | 5 | operation × reach in (0.40) | loop | absent | absent |
| before | miniflux | sonnet | skill | 3 | 6 | 5 | operation × reach in (0.45) | loop | absent | absent |
| v2 | miniflux | sonnet | skill | 1 | 3 | 5 | piece × reach in (0.38) | operation × reach in | absent | absent |
| v2 | miniflux | sonnet | skill | 2 | 5 | 5 | operation × reach in (0.50) | operation × witness | absent | absent |
| v2 | miniflux | sonnet | skill | 3 | 4 | 3 | operation × reach in (0.62) | operation × reach in | absent | absent |
| v2 | subscription-payments | haiku | baseline | 1 | 19 | 6 | unit × bring out (0.40) | unit × bring out | absent | absent |
| v2 | subscription-payments | haiku | baseline | 2 | 16 | 4 | unit × bring out (0.57) | unit × bring out | absent | absent |
| v2 | subscription-payments | haiku | baseline | 3 | 12 | 2 | unit × bring out (0.71) | unit × bring out | absent | absent |
| before | subscription-payments | haiku | skill | 1 | 2 | 3 | operation × reach in (0.57) | loop | absent | absent |
| before | subscription-payments | haiku | skill | 2 | 6 | 4 | unit × witness (0.43) | loop | absent | absent |
| before | subscription-payments | haiku | skill | 3 | 3 | 3 | operation × reach in (0.57) | loop | absent | absent |
| v2 | subscription-payments | haiku | skill | 1 | 6 | 6 | operation × reach in (0.29) | piece × bring out | absent | absent |
| v2 | subscription-payments | haiku | skill | 2 | 4 | 4 | operation × reach in (0.43) | piece × bring out | absent | absent |
| v2 | subscription-payments | haiku | skill | 3 | 3 | 5 | operation × reach in (0.43) | piece × bring out | absent | absent |
| v2 | subscription-payments | sonnet | baseline | 1 | 9 | 3 | operation × reach in (0.50) | loop | absent | absent |
| v2 | subscription-payments | sonnet | baseline | 2 | 10 | 4 | unit × bring out (0.25) | loop | absent | absent |
| v2 | subscription-payments | sonnet | baseline | 3 | 11 | 4 | piece × bring out (0.50) | piece × bring out | absent | absent |
| before | subscription-payments | sonnet | skill | 1 | 4 | 4 | operation × reach in (0.55) | loop | absent | absent |
| before | subscription-payments | sonnet | skill | 2 | 6 | 6 | unit × reach in (0.47) | loop | absent | absent |
| before | subscription-payments | sonnet | skill | 3 | 4 | 6 | unit × reach in (0.30) | loop | absent | absent |
| v2 | subscription-payments | sonnet | skill | 1 | 4 | 6 | operation × reach in (0.33) | operation × witness | absent | absent |
| v2 | subscription-payments | sonnet | skill | 2 | 7 | 4 | unit × bring out (0.25) | unit × bring out | absent | absent |
| v2 | subscription-payments | sonnet | skill | 3 | 6 | 4 | operation × reach in (0.50) | operation × witness | absent | absent |
| v2 | tps-demo | haiku | baseline | 1 | 9 | 4 | unit × bring out (0.40) | operation × bring out | absent | absent |
| v2 | tps-demo | haiku | baseline | 2 | 9 | 3 | piece × bring out (0.40) | piece × bring out | absent | absent |
| v2 | tps-demo | haiku | baseline | 3 | 12 | 4 | unit × bring out (0.57) | loop | absent | absent |
| before | tps-demo | haiku | skill | 1 | 6 | 3 | journey × reach in (0.75) | journey × reach in | absent | absent |
| before | tps-demo | haiku | skill | 2 | 6 | 3 | journey × reach in (0.75) | journey × reach in | absent | absent |
| before | tps-demo | haiku | skill | 3 | 8 | 3 | journey × reach in (0.78) | journey × reach in | absent | absent |
| v2 | tps-demo | haiku | skill | 1 | 2 | 3 | piece × reach in (0.50) | piece × reach in | absent | absent |
| v2 | tps-demo | haiku | skill | 2 | 5 | 4 | piece × bring out (0.29) | piece × bring out | absent | absent |
| v2 | tps-demo | haiku | skill | 3 | 3 | 3 | piece × reach in (0.67) | piece × reach in | absent | absent |
| v2 | tps-demo | sonnet | baseline | 1 | 13 | 4 | piece × bring out (0.40) | unit × bring out | absent | absent |
| v2 | tps-demo | sonnet | baseline | 2 | 7 | 5 | piece × bring out (0.38) | loop | absent | absent |
| v2 | tps-demo | sonnet | baseline | 3 | 9 | 4 | piece × bring out (0.38) | piece × bring out | absent | absent |
| before | tps-demo | sonnet | skill | 1 | 5 | 3 | journey × reach in (0.83) | loop | absent | absent |
| before | tps-demo | sonnet | skill | 2 | 4 | 3 | journey × reach in (0.60) | loop | absent | absent |
| before | tps-demo | sonnet | skill | 3 | 5 | 4 | journey × reach in (0.70) | loop | absent | absent |
| v2 | tps-demo | sonnet | skill | 1 | 5 | 6 | operation × reach in (0.33) | piece × bring out | absent | absent |
| v2 | tps-demo | sonnet | skill | 2 | 3 | 4 | operation × reach in (0.57) | piece × bring out | absent | absent |
| v2 | tps-demo | sonnet | skill | 3 | 7 | 5 | journey × reach in (0.57) | piece × reach in | absent | absent |
| v2 | vue-realworld | haiku | baseline | 1 | 15 | 3 | operation × bring out (0.33) | loop | absent | absent |
| v2 | vue-realworld | haiku | baseline | 2 | 15 | 6 | operation × witness (0.17) | loop | absent | absent |
| v2 | vue-realworld | haiku | baseline | 3 | 16 | 3 | unit × bring out (0.75) | unit × bring out | absent | absent |
| before | vue-realworld | haiku | skill | 1 | 5 | 5 | piece × reach in (0.29) | piece × reach in | absent | absent |
| before | vue-realworld | haiku | skill | 2 | 5 | 5 | piece × reach in (0.43) | piece × reach in | absent | absent |
| before | vue-realworld | haiku | skill | 3 | 5 | 6 | piece × reach in (0.30) | journey × reach in | absent | absent |
| v2 | vue-realworld | haiku | skill | 1 | 3 | 2 | piece × reach in (0.75) | journey × bring out | absent | absent |
| v2 | vue-realworld | haiku | skill | 2 | 2 | 3 | journey × reach in (0.50) | journey × witness | absent | absent |
| v2 | vue-realworld | haiku | skill | 3 | 3 | 1 | piece × bring out (1.00) | piece × bring out | absent | absent |
| v2 | vue-realworld | sonnet | baseline | 1 | 10 | 4 | unit × bring out (0.43) | loop | absent | absent |
| v2 | vue-realworld | sonnet | baseline | 2 | 13 | 4 | unit × bring out (0.56) | unit × bring out | absent | absent |
| v2 | vue-realworld | sonnet | baseline | 3 | 10 | 4 | unit × bring out (0.62) | unit × bring out | absent | absent |
| before | vue-realworld | sonnet | skill | 1 | 5 | 5 | piece × reach in (0.56) | piece × reach in | absent | absent |
| before | vue-realworld | sonnet | skill | 2 | 6 | 4 | piece × reach in (0.56) | loop | absent | absent |
| before | vue-realworld | sonnet | skill | 3 | 3 | 4 | piece × reach in (0.50) | journey × reach in | absent | absent |
| v2 | vue-realworld | sonnet | skill | 1 | 4 | 4 | piece × reach in (0.25) | piece × reach in | absent | absent |
| v2 | vue-realworld | sonnet | skill | 2 | 4 | 5 | piece × reach in (0.38) | journey × bring out | absent | absent |
| v2 | vue-realworld | sonnet | skill | 3 | 3 | 5 | piece × reach in (0.40) | piece × reach in | absent | absent |
