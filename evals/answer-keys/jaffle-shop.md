# Answer key — jaffle-shop

**Repository:** https://github.com/dbt-labs/jaffle-shop @ `5beb145` · **Shape:** dbt data pipeline

**Filled by:** bug-grounded draft — an agent blind to the skill, from the fixed bugs below · 2026-11-25 — verify the citations
**M1 accepted:** `piece × bring out`, `operation × bring out`

The pinned history has only 126 non-merge commits. I examined 42 candidates: the 39 whose subject or body matched fix/bug/regression/revert/hotfix/broken/wrong/error/issue/#n, plus 3 fix-shaped commits that did not match the keywords (68815b8, 6cb4da0, e900cc5). I kept 13 real behaviour bugs. I excluded 29: 8 docs/typo/README, 8 lint/formatting or CI/tooling/profile-config-only, 4 dependency or dbt-version-syntax changes, 3 history-management reverts, 1 test-only fixture fix, and 5 features, duplicates or no-behaviour wiring. The evidence is moderate. 13 bugs is enough to rank cells, but every bug is small (one to four lines), and many are "works on adapter X, not on Y". So bugs where the environment underneath varies (`loop`) dominate. The cheapest cells cluster on the bring-out column. Only 2 bugs needed the real warehouse. Two bugs silently produced wrong numbers (ac0e57a, 2447e1b), and a third did so on Postgres only (13f0b77). No kept bug needed a witness-style check as its cheapest catch. 2447e1b's fix did add witness-style data tests (`expression_is_true`) as a second line of defence.

| Cell | Expect (`propose` · `leave` · `either`) | Why — what in the repository says so |
|---|---|---|
| `unit × bring out` | propose | 3 bugs: 13f0b77 (Postgres integer division in `cents_to_dollars` dropped cents silently), 68815b8 (default macro syntax invalid on Fabric), 29b7222 (`generate_schema_name` put schemas in the wrong place per target): each is one macro, checkable by rendering it alone on a local engine or a mocked target |
| `unit × witness` | leave | Structural: at unit level only a macro or one SQL unit test is present, and a dbt unit test materialises nothing in the warehouse. So there is no run output (rows, tables, schemas) to record and compare at this level. Witnessing starts once a model is built |
| `unit × reach in` | either | No kept bug needed it. All macro bugs (13f0b77, 68815b8, 29b7222) were cheaper to expose by rendering locally. Cell possible via `dbt run-operation` on a real target |
| `piece × bring out` | propose | 4 bugs: ac0e57a (`count` instead of `sum` made every order a food/drink order, silently wrong metrics; the fix added the first `orders` unit test), 2447e1b (fanout join multiplied `lifetime_spend` in `customers`, silently wrong numbers, issue #1), fe8ee95 (unbalanced `ref(` in products/supplies broke compile), 1d6d04d (metric named "Drink Orders" with a malformed filter). Unit tests existed for stg_locations/order_items (9283bcf, 576ea6e) but none covered orders/customers |
| `piece × witness` | either | No kept bug had it as cheapest. 2447e1b's fix also added `expression_is_true` invariants (subtotal + tax = total), which are witness-style, but a fixture unit test catches the fanout more cheaply |
| `piece × reach in` | either | No kept bug needed it |
| `operation × bring out` | propose | 4 bugs: 8285cfc (`to_date` in metricflow_time_spine does not exist on DuckDB/BigQuery, build fails), 1fb76d6 (semantic dimensions/measures referencing non-existent columns failed `dbt sl validate`), a75613b (`is_food_item = 1` on a boolean, metric SQL invalid on stricter dialects), e900cc5 (packages.yml lost, project cannot build). Each shows up on `dbt build --select <x>` (plus metric validation) on local DuckDB/Postgres |
| `operation × witness` | either | No kept bug had it as cheapest. The data tests added in 2447e1b (relationships, expression_is_true) live here and guard the seed-data issues that commit also fixed |
| `operation × reach in` | propose | 2 bugs: 67b108b (BigQuery will not compare datetime to timestamp in `truncate_timespan_to`), 11504ae (the BigQuery fix then broke Snowflake). Warehouse-specific type rules a local engine does not reproduce. The CI added in 558fe27 did not run both warehouses on 67b108b |
| `journey × bring out` | either | No kept bug needed the whole DAG. Each one was visible at a single model or macro |
| `journey × witness` | either | No kept bug needed it |
| `journey × reach in` | either | No kept bug needed it. The repo has full-run CI/CD jobs on BQ/SF/Postgres (558fe27, 9e622f7, 48b8699) |
| `loop` | propose | 8 of 13 bugs came from adapter/target/setup differences: 13f0b77, 68815b8, 29b7222, 8285cfc, a75613b, 67b108b, 11504ae, e900cc5 |

## Evidence — fixed bugs

| Commit | What broke | Cheapest cell that would have caught it | Why that cell |
|---|---|---|---|
| ac0e57a | `orders.count_food_items`/`count_drink_items` used `count(case … then 1 else 0)`, so every order counted as food and drink (wrong numbers downstream into food_orders/drink_orders metrics) | `piece × bring out` | A fixture unit test of `orders` with one non-food item shows it. The fix added exactly that unit test |
| 2447e1b | `customers` joined order_items to orders before summing `order_total`, fanning out lifetime spend (issue #1). The seed data was also inconsistent | `piece × bring out` | A unit test with one order of two items exposes the doubled total. No customers unit test existed |
| fe8ee95 | `{{ ref('stg_products' }}` / `ref('stg_supplies' }}`: missing paren, products and supplies marts fail to compile | `piece × bring out` | Compiling that one model locally fails immediately |
| 1d6d04d | Metric declared as `name: Drink Orders` (invalid name) with filter lacking `= true` | `piece × bring out` | Static semantic-manifest validation of that metric definition rejects it, no warehouse needed |
| 13f0b77 | `default__cents_to_dollars` on Postgres does integer `/100` before the cast, so cents are truncated (wrong amounts) | `unit × bring out` | Rendering and running the macro alone on a local Postgres with a value like 1999 shows 19.00 |
| 68815b8 | Default `cents_to_dollars` uses `::numeric` syntax, invalid on Fabric (T-SQL) | `unit × bring out` | The macro rendered alone and parsed or run for the Fabric dialect fails. One macro is the whole surface |
| 29b7222 | `generate_schema_name` produced `<default>_<custom>` for every target, putting prod relations in the wrong schemas | `unit × bring out` | A macro test with `target.name` = prod vs dev shows the wrong output without building anything |
| 8285cfc | `metricflow_time_spine` used `to_date('01/01/2000','mm/dd/yyyy')`, which does not exist on BigQuery/DuckDB, so the model fails to build | `operation × bring out` | `dbt build --select metricflow_time_spine` on local DuckDB fails, as the commit message confirms |
| 1fb76d6 | Semantic models referenced `opened_at` (column is `opened_date`) and a `count_distinct` measure with no column expr. `dbt sl validate` failed and downstream metric queries broke | `operation × bring out` | Build locations/customers locally, then validate the semantic configs against the built columns |
| a75613b | food_revenue/drink_revenue measure expr compared booleans with `= 1`, invalid SQL on strict dialects | `operation × bring out` | Running the compiled metric query against a local engine of the target dialect (e.g. Postgres) errors |
| e900cc5 | packages.yml lost, so `dbt deps`/build fails on dbt_utils/dbt_date references | `operation × bring out` | Any local `dbt deps && dbt build --select <model>` fails at once |
| 67b108b | `truncate_timespan_to` = `current_timestamp()` compared to a datetime column errors on BigQuery | `operation × reach in` | BigQuery-specific type rule. Building stg_orders against BigQuery is the cheapest place it appears |
| 11504ae | 67b108b's `cast(dbt_date.now() as datetime)` broke on Snowflake | `operation × reach in` | Snowflake-specific. Building stg_orders on Snowflake shows it. CI at the time did not run both warehouses |

## Excluded candidates

e9d17b1 — README wording, docs only
226b27a — README steps for loading data, docs only
9d2a113 — removes source freshness config as a workaround for a dbt-core bug (dbt-core #11506), config only, no model behaviour
2d4017d — package pin (audit-helper), dependency
2c6795c — `tests:` to `data_tests:` syntax migration for a new dbt version, no model behaviour change
72ebe7e — README typo
afda522 — README expansion, docs
e7c1860 — README typo
119adbc — README expansion, docs (duplicate of afda522)
47d9bc9 — README cleanup, docs
b232e30 — project restructure/feature (jafgen data generation, CD jobs), duplicate of a637a82 content
a637a82 — feature: replaces static seeds with generated data. Model changes are formatting only
9e622f7 — adds staging CD jobs, CI config
2044876 — catch-up merge of staging to main, duplicate of 2447e1b/11504ae content
cef41c2 — feature: saved queries and exports
558fe27 — adds CI/CD workflows, CI config
2eec48b — Taskfile/dev-flow tooling
ac611f0 — test-only: reduces timestamp precision in the stg_locations unit-test fixture
324d748 — adds audit-helper package, dependency
b0b6007 — re-adds profiles.yml for the SQLFluff templater and whitespace nits (one metric rename), tooling config and formatting
2021a64 — SQLFluff/pre-commit dependency updates
633a65d — revert batch (history management, non-unit-test changes)
278add9 — revert batch (history management)
0770575 — revert batch (history management)
c003c03 — whitespace in orders model
65c3b82 — default profile and dbt-metricflow version, config/dependency
c830af0 — linting fixes
5c1ed68 — link fixes, docs
6cb4da0 — semantic model pointed at pass-through `stg_products` instead of `products`. Identical data, naming/wiring only
