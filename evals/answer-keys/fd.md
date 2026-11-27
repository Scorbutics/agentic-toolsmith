# Answer key — fd

**Repository:** https://github.com/sharkdp/fd @ `2e8648f10fe5` · **Shape:** Rust command-line tool (a find alternative): argument parsing, a parallel directory walker, filters, output formatting

**Filled by:** bug-grounded draft — an agent blind to the skill, from the fixed bugs below · 2026-11-27 — hold-out: drafted after the skill was frozen
**M1 accepted:** `piece × bring out`

The 60 most recent non-merge commits reachable from `2e8648f10fe5` whose subject matched fix/bug/regression/revert/crash/panic/broken/wrong/error/issue (dependabot bumps pre-filtered) were examined; 27 are kept as real behaviour bugs. The 33 exclusions: 12 docs/man/README/changelog/help-text/typo commits, 5 CI or release/packaging-config only, 5 test-only or formatting/lint, 1 refactor, 1 feature (`e9dcfd2`), and 9 fixes made inside the still-unmerged PR that introduced the defect (never shipped: the pattern-refactor PR #2191, the broken-symlink PR's review iterations, the `-u` override PR #2193, the Windows verbatim PR #2208, the `--ignore-contain` and `--full-path` PRs). Evidence strength: **moderate**. There are enough bugs to show a clear shape: 12 of 27 sit in option parsing, filter or walker logic on fixture trees, and 7 more in single pure functions such as the size and time parsers, smart-case detection and path/URL builders. The operation, journey and platform cells rest on 2 bugs each, so their `propose` values meet the threshold only just. Several fixes are small and came from first-time or AI-assisted contributors. No bug touched user files or ran the wrong `--exec` command. Two crashed: a `--threads` overflow (`89d10fc`) and an invalid cwd with `--full-path` (`d3a500a`). One was a security-relevant omission: terminal escape injection through filenames (`92c54d3`).

| Cell | Expect (`propose` · `leave` · `either`) | Why — what in the repository says so |
|---|---|---|
| `unit × bring out` | propose | 7 kept bugs: overflowing size multiplier (`8b6d754`), panicking `@` timestamp (`5becb9d`), a time-filter error message that hid the range cause (`f85a73a`), smart-case confused by `(?i)` (`e422fc3`), Windows verbatim-prefix stripping (`d96ed27`), the Windows `file://` host (`cd8fedc`), jemalloc dropped from default features (`1765d08`). All are pure functions or build cfg. `hyperlink.rs` already had a unit test that covered encoding but not the `host()` on Windows. |
| `unit × witness` | either | No kept bug; a single formatter writing into a byte buffer can be witnessed, so the cell can exist. |
| `unit × reach in` | leave | Structural: a function taken alone is by definition not in real use, so nothing can observe it in a real terminal or shell. Once it is observed in real use, the check is no longer at unit level. |
| `piece × bring out` | propose | 12 kept bugs, the most of any cell. Option parsing as a whole: `-u` override halves (`8e7a1ab`), missing `--exact`/`--fixed-strings` conflict (`d642c44`), hyphen-leading `--format` treated as a flag (`b422e5d`), path-separator diagnostic missing for `/` and for `--and` (`ed47664`, `6aac84e`). Filters and walker on a fixture tree: `--type executable` intersecting instead of uniting (`2c9a0c9`), broken-symlink depth under `--min-depth` and overlapping roots (`350b33a`, `b3a8ff6`). Completion scripts drifting from the clap definition (`80b135d`, `3ace616`, `15417fb`, `2c26069`). The integration tests in `tests/tests.rs` covered `-u` and `--type` and missed these combinations. |
| `piece × witness` | either | No kept bug; the exec module's spawned commands could be recorded on fixture paths. |
| `piece × reach in` | either | No kept bug; the walker could be observed on a real filesystem. |
| `operation × bring out` | propose | 2 crashes of a full invocation: `-j` huge panics on channel capacity (`89d10fc`), and `--full-path` in a deleted cwd hits an `.expect` panic (`d3a500a`). Both need the whole binary run on a fixture dir with exit-code checks. |
| `operation × witness` | propose | 2 kept bugs about what was written outward: piped `--format` output replaced invalid UTF-8 with U+FFFD and broke `xargs -0` (`3dcff92`), and error messages on stderr carried unsanitized paths (`24198d9`). The harness has `assert_output_raw` and stderr checks, but no test held these cases. |
| `operation × reach in` | propose | 2 kept bugs visible only when the stream is a real terminal (sanitizing depends on `is_terminal`): raw escape sequences from filenames reached the tty (`92c54d3`), and the fix then escaped newlines in tty error messages (`a3942db`). The test env has no pty. |
| `journey × bring out` | propose | 2 kept bugs in what consumers load: a zsh completion syntax error (`b1c6c2e`, which needs zsh to parse the file) and `fdfind` completions missing from the deb package (`247a517`, which needs the packaged install). |
| `journey × witness` | either | No kept bug; recording a shell or pipeline consuming fd's output is possible. |
| `journey × reach in` | either | No kept bug; real-shell/editor use across platforms is possible (hyperlinks in a Windows terminal, `cd8fedc`, came from users, but a unit check is cheaper). |
| `loop` | propose | At least 4 kept bugs came from platform or filesystem differences: Windows verbatim paths (`d96ed27`), the Windows hyperlink host (`cd8fedc`), Debian `fdfind` packaging (`247a517`), and invalid-UTF-8 filenames on unix (`3dcff92`). |

## Evidence — fixed bugs

| Commit | What broke | Cheapest cell that would have caught it | Why that cell |
|---|---|---|---|
| `f85a73a` | Out-of-range date/duration in time filters reported only "wrong format", hiding the real cause (#2053) | `unit × bring out` | `TimeFilter::from_str` error text is a pure-function result |
| `89d10fc` | Huge `--threads` value aborted with capacity overflow / thread-spawn failure (#2078) | `operation × bring out` | Panic arises at walker startup from the full invocation; assert exit code and error |
| `2c9a0c9` | `--type executable`/`empty` combined with another type filtered out the other type instead of uniting | `piece × bring out` | `FileTypes` filter over a fixture tree with mixed entry types; existing `--type` tests missed the combination |
| `3dcff92` | Piped `--format` output replaced invalid UTF-8 with U+FFFD, breaking `xargs -0` (#2189) | `operation × witness` | Bytes written to non-tty stdout must be compared raw; `assert_output_raw` existed but no `--format` case |
| `b1c6c2e` | zsh completion had invalid syntax around `--format` (#2216) | `journey × bring out` | Only zsh parsing the script (`zsh -n`/compinit) shows it |
| `d96ed27` | `--absolute-path` turned verbatim `\\?\` search paths into relative ones on Windows (#2207) | `unit × bring out` | `strip_verbatim_prefix` is a pure path function, run on Windows CI |
| `8b6d754` | Size filter multiplication overflowed on large quantities | `unit × bring out` | `SizeFilter::from_string` boundary inputs |
| `8e7a1ab` | `--ignore`/`--no-hidden` after `-u` overrode all of `-u`, not their half (#2192) | `piece × bring out` | Option parsing as a whole; flag-order combinations |
| `e422fc3` | Inline `(?i)` in one pattern made other `--and` patterns case-sensitive (#2184) | `unit × bring out` | Uppercase detection on one pattern string |
| `80b135d` | zsh completion lacked repeatable `--and`, `--exact`, `--ignore-contain`, aliases | `piece × bring out` | Compare completion script with `Opts::command()` args |
| `3ace616` | zsh completion missing `--format` and hidden `--literal` alias | `piece × bring out` | Same completion-vs-clap comparison |
| `15417fb` | zsh completion did not offer accepted `--type` alias `dir` | `piece × bring out` | Completion values vs clap possible values |
| `2c26069` | zsh completion completed `--and` as a path instead of a pattern | `piece × bring out` | Completion action vs clap value hint |
| `24198d9` | Error messages printed unsanitized paths with control characters (#2119) | `operation × witness` | Check stderr of an invocation on a fixture with a control-char filename |
| `b422e5d` | `--format -...` (space-separated, leading hyphen) parsed as a new flag (#2126) | `piece × bring out` | Option parsing as a whole |
| `1765d08` | Default build lost jemalloc (feature dropped in `92c54d3`) | `unit × bring out` | A one-line `cfg!(feature = "use-jemalloc")` test in the default build |
| `a3942db` | Newlines in error messages escaped as `\x0a` on a terminal (regression from `92c54d3`, #2104) | `operation × reach in` | Sanitizing ran only when stderr is a tty; the pipe-based test harness cannot see it |
| `b3a8ff6` | Broken symlink under overlapping search roots dropped by `--min-depth` | `piece × bring out` | Walker on a fixture tree with overlapping roots |
| `350b33a` | Broken symlinks with `--follow` always dropped by `--min-depth` (#1017) | `piece × bring out` | Walker on a fixture tree with a dangling link |
| `5becb9d` | Out-of-range `@timestamp` panicked instead of erroring (#2081) | `unit × bring out` | `TimeFilter` parse of an extreme value |
| `6aac84e` | Path-separator diagnostic not fired for `--and` patterns; silent zero results (#1873) | `piece × bring out` | Validation over all parsed patterns |
| `d642c44` | `--exact` did not conflict with `--fixed-strings` | `piece × bring out` | clap conflict definitions as a whole |
| `ed47664` | Pattern with `/` that did not name an existing directory silently matched nothing (#1873) | `piece × bring out` | Pattern validation on parsed options |
| `92c54d3` | Filenames with escape sequences injected control codes into the terminal | `operation × reach in` | The harm exists only on a real tty; a pty-driven run is needed |
| `d3a500a` | `--full-path` with an invalid working directory panicked on `.expect` (#1900) | `operation × bring out` | Whole binary run with a deleted cwd; assert graceful exit |
| `247a517` | `fdfind` alias in the deb package had no bash/zsh/fish completions (#1888) | `journey × bring out` | Only an install of the built deb shows it |
| `cd8fedc` | Windows hyperlinks broken for paths with spaces (`file://C:` lacked a third slash) (#1843) | `unit × bring out` | `host()` / URL build on Windows; the existing hyperlink unit test covered encoding only |

## Excluded candidates

70e44e7 — man page typo
4f75753 — review refactor inside unmerged PR #2208 (same as d96ed27)
19731c1 — stray debug eprintln removed inside unmerged pattern-refactor PR #2191; never shipped
e0a9ba5 — regression fixed inside unmerged pattern-refactor PR #2191; never shipped
90f6ada — regression fixed inside unmerged pattern-refactor PR #2191; never shipped
2b9d4cf — changelog only
7c885ef — changelog only
cffdbfe — review iteration inside PR #2193 (same bug as 8e7a1ab)
dd7fa4d — man page spacing
d2061da — test-only
ec5f8eb — completion description wording (typo)
86f0bb3 — completion description text only
c7f023e — help text punctuation
3a11690 — cargo-binstall metadata in Cargo.toml (packaging config only)
e9dcfd2 — feature (allow --strip-cwd-prefix with paths), listed under Features
acc64aa — clippy in tests
cd755e2 — README
f898e95 — refactor
2fbecc9 — help text wording
66be848 — rustfmt
8f5a167 — test-only
4f4900b — test-only
078f5d1 — code comment typo
45646e2 — CI
5008de5 — CI attestation
f8baea8 — CONTRIBUTING docs
647ced8 — review follow-up inside the --full-path PR (with d3a500a)
b87d919 — CI
bb3d57c — CI
4ba10c7 — changelog only
1993c76 — review iteration on the unshipped --ignore-contain feature
68edfde — review iteration inside the broken-symlink PR (with 350b33a)
4a89aff — review iteration inside the broken-symlink PR (with 350b33a)
