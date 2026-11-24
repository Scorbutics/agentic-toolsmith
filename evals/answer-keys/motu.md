# Answer key — motu

**Repository:** https://github.com/Scorbutics/motu @ `6050e2faaf14` · **Shape:** TypeScript architecture framework and CLI for React screen regions (declarations, the lagoon renderer, checks) — developer tooling whose input is another project

Fill this in from what you know of the project, **before reading any map** an agent wrote for it
(rules: [README.md](README.md)). Empty rows are not scored. You are the expert here: the question for each
cell is "in a month of agent work on this project, would tooling in this cell catch or prevent
what actually goes wrong?" — answer from the bugs and the friction you remember.

**Author tools fit** (from `scenario.json`, used to flag a misfit proposal): none; using it on itself is borderline. Correct it there if wrong.

**Filled by:** <name> · <date>
**M1 accepted:** <the cells a good first milestone may land in, comma-separated — e.g. `operation × witness`, `piece × bring out` — or `any`>

| Cell | Expect (`propose` · `leave` · `either`) | Why — what you know of the project |
|---|---|---|
| `unit × bring out` | leave | Already covered it's basically running the unit tests |
| `unit × witness` | either | I don't see anything except assertions |
| `unit × reach in` | leave | That category probably does not make sense no? |
| `piece × bring out` | leave | I don't think we use Motu for Motu itself enough but it's there |
| `piece × witness` | either | partly covered by Motu but not a lot? |
| `piece × reach in` | propose | we might lack such a system |
| `operation × bring out` | propose | I don't think we have anything here |
| `operation × witness` | leave | the Seams and network tab of motu |
| `operation × reach in` | either | I can't picture any example of what a tool in this category would look like|
| `journey × bring out` | either | I think this category is generally answered by "Playwright" for web projects but I might be wrong |
| `journey × witness` | leave | access logging through server console |
| `journey × reach in` | either |  |
| `loop` | propose | I don't think we have anything related to the loop in Motu |
