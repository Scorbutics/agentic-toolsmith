# Parallel agents

Several agents — or an agent and its human — will work on the project at once, each in its own
worktree. That is not a category: it is a question the whole map answers and a property every
handle has.

**The map answers: how many agents can safely work at once today, and what do they collide on?**
List every **shared resource** — a database, a port, a display, a build output path, a working
folder, a cache, a queue, a cron schedule, an external test account, a device — with who shares
it, what collides, and how it is isolated today. The hidden ones are **global rows inside a shared
store** (a settings row, a virtual-clock row, a sequence, a schedule): namespacing the rest does
not fix them.

**Three isolation levels** — propose the cheapest that removes the collisions:
1. **Shared infrastructure, namespaced data** — one database, N app servers; every write carries
   the environment (schema, tenant, key prefix). Cheap; fails on global rows.
2. **Per-environment processes on shared infrastructure** — a database per environment inside
   one server, a port range per environment, a display per environment.
3. **Fully separate** — a container or VM per environment. Costly; nothing leaks.

**The environment registry** is the Lab handle that makes it usable: named environments
(`envs list`, `envs up <name>`, `envs down <name>`), and **every other handle takes `--env`**,
defaulting to the worktree's own — so a run never lands on the human's environment by accident.

Every card carries a **Parallel:** line — how it isolates (`--env`, a run id, a port derived from
the worktree), or "single-agent only" and why.

**The process registry** sits next to it: everything a run starts (servers, emulators, displays,
watchers, port forwards) is recorded under its run id, so `envs ps` shows what is alive and
`envs stop <run>` ends it through the app's own clean exit (its quit command; SIGTERM for servers
and workers that handle it) — never a signal that trips a crash
handler, never a process or a temp folder left behind.

**Leases, when sharing cannot be avoided.** One physical device, one GPU, one vendor sandbox
account cannot be duplicated per environment. Give each a lease (`envs claim device --ttl 10m`,
renewed while in use, released on stop) so agents queue instead of colliding — and say in the map
which resources need one.
