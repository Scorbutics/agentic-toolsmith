# Rules as guards

Agent files are full of rules in prose — "NEVER run `db reset`", "do not push to main", "always
use the service layer". Prose is a request; an agent under pressure can miss it. Where the
harness allows it, turn each rule into something **enforced**:

- a **pre-tool hook** or command wrapper that blocks the forbidden call and says why;
- a **permission list** for the harness: the read-only and fenced handles allowed without a
  prompt (so the agent never stalls on approval for `state` or `shot`), destructive commands
  gated or denied;
- a **lint rule or CI check** for rules about code (the project's own linter usually has a way).

In map mode, list the prose rules found in agent files with the guard each could become (map
section "Rules → guards"). Every card carries a **Permission:** line — allow · ask · deny — so
the accepted plan comes with the harness configuration that lets an agent use it unattended.
The guards are not handles (the agent does not call them); they are how the fences hold.
