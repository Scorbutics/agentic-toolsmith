# Grill — question bank

Rules (after Matt Pocock's *grill-me*):
- **One question at a time.** Wait for the answer before the next. The one exception is the
  batched permission question before probing (step 1b).
- **Recommend an answer** with every question, so the human can just say "yes".
- **Never ask what the repo or a probe can answer.** Look it up, run it, then ask only about
  what remains — and say what you already found.
- Stop when every rung has a status and every `human-only` / `blocked` rung has an owner and a decision.

Pick by rung; skip the ones the probes settled. Ask task questions first: they decide what
every other answer is for.

## The task (ask first when step 0 was ambiguous)
- "This maps to two features — [A] and [B]. Which one is wrong?"
- "Where did you see it — which screen, run, device, file? Can you send the artifact?"
- "What is the *correct* output — which variant is the reference?"
- "What counts as fixed? (for performance: which metric, measured how, cold or warm, under what number?)"
- "My probe reaches the state but does not reproduce the bug: [evidence]. What differs on your side?"

## Permissions (one batched question, before probing)
- "Beyond read-only probes I plan: [rolled-back: …], [local writes: …], [code injection: …],
  [external: …]. Which may I run?"
- "May I install [tool] (version) to measure this?"

## Shape, ownership and boundary
- "Is this the whole system, or does it talk to services elsewhere? Which can I run locally?"
- "The code to change lives in [repo/artifact]. May a fix land there, and how does it reach the app?"
- "What must I never touch, even locally — prod data, payments, emails to real people, pushes, saves, a destructive reset?"
- "Is there a release gate I can hang dev-only tooling on (env, build flag, config)?"

## Environments, webhooks, schedules (web stacks)
- "Which preview / staging environments exist, and which may an agent use — read-only, or not at all?"
- "Which inbound webhooks and scheduled jobs exist, and which may fire during an agent run?"

## Launch / Observe
- "How do *you* start it day to day — IDE button, script, a recipe you never wrote down?"
- "Is anything visible only on screen, never in a log? At which window scale / device?"

## Reach
- "What do you do by hand, every time, before you can even see the bug?"
- "Which states do your tasks land in most often?" (ranks the Reach gaps)
- "Which content / save / tenant / persona shows it?"
- "How does login work locally — password, magic link, SSO, OTP? Is there a seeded test user?"
- "Does anything depend on the date, elapsed time, or timezone?"
- "Is there a debug menu / cheat console / admin page I should know about?"

## Act / Assert
- "Besides what the screen shows, what must this change *not* touch — tables, hosts, mails, files? Is that written down anywhere?"
- "Is there a lab (component/state renderer, scene harness) where this state already exists, and is it kept in sync with the app?"
- "When you check that something works, what exactly do you look at?"
- "Is there a state only real hardware, a real device, or a third party can produce?"

## Reset / Cycle
- "How do you get back to a clean state? Is that safe for me to run?"
- "How long from saving a file to seeing the change? What is the slowest part?"

## Prioritisation (end)
- "Gaps ranked by my estimate: [...]. Which do we close now, before the task?"
- "Who owns the `human-only` ones I can't close (a device, a credential, a vendor)?"
