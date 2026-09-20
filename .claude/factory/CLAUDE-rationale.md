# Why the rules are what they are (human reading — NOT loaded by the agent)

Companion to the root `CLAUDE.md` and to `CONVENTIONS.md`. Every rule there once carried an
inline *Why* note; those notes are here instead, together with the design history of the
factory's mechanisms (moved out of `CONVENTIONS.md` on 2026-09-20, because each factory
agent reloads that file on every run). Nothing in this file instructs the agent — it is not
`@import`ed and no pointer reaches it, so it costs no context load. Read it when you are
deciding whether a rule still earns its place, or when onboarding someone who is about to
ask "why can't I just…".

Rules are tools, not scripture. If a rule fails in practice, open a PR against `CLAUDE.md`
and update the matching entry here.

---

## Rule 0 — Fail Loud

The single most important rule in the contract. Silent failure is the biggest risk of AI
collaboration — errors get smuggled into production. Better to be noisy about uncertainty
than quiet about delivery.

## Rule 1 — Pick a Side, Flag the Other

"Average" code that satisfies two contradictory standards is harder to maintain than
either original — it leaves future engineers permanently unsure which direction is
correct.

## Rule 2 — Read Before You Write

Without context, AI is most likely to make changes that look reasonable on the surface but
violate the existing design. Reading first is the cheapest line of defense.

## Rule 3 — Think Before Coding

AI's most common failure mode is filling in blanks without confirmation. This rule forces
explicit reasoning.

## Rule 4 — Simplicity First, With Room for Reasonable Preparation

Over-engineering is AI's most common side effect when writing code. But forbidding
abstraction outright kills legitimate architectural preparation. "Known vs imagined" is
the dividing line.

## Rule 5 — Surgical Changes, With Disclosure

Surgical changes keep PRs clean and reviewable. But pretending you didn't see it lets
technical debt accumulate forever — disclosure is the necessary compromise.

## Rule 6 — Goal-Driven Execution

Strong success criteria let AI loop independently to completion. Weak criteria ("make it
work") require constant clarification.

## Rule 7 — Tests Verify Intent, Not Just Behavior

When you tell AI "write tests and make them pass", there are two mathematical paths to
success — actually verify business logic (right path), or write empty tests that always
pass (wrong path). This rule is the structural defense against reward-hacking.

## Rule 8 — Match Conventions, Surface Anti-Patterns

Blind compliance lets AI propagate bad habits. But unilateral "improvement" fragments
style and breaks team consistency. Surfacing without acting is the lowest-impact
compromise.

## Rule 9 — Use the Model Only for Judgment Calls

AI is good at interpretation work, not guarantee work. Putting AI in the wrong slot makes
systems hard to debug and hard to trust.

## Rule 10 — Checkpoint After Every Significant Step

The most dangerous failure in long tasks is stacking on top of errors. Checkpoints catch
errors early and prevent contamination of later steps.

## Context Health — phase boundaries

Three generations of this section, and why it landed where it did:

1. **Hard token budgets** ("4000 tokens per task") — unenforceable, because the model
   cannot reliably count its own usage. They became performative.
2. **Distress signals → `/compact`** — observable triggers, but the prescription treated
   the symptom with the one tool that destroys evidence. Compacting mid-diagnosis is how
   you get a session that is confidently wrong about whatever the summary flattened.
3. **Phase boundaries (current)** — the decision moves to the seam between chunks of
   work, and walks an ordered ladder. It uses structure the factory already has: the
   artifacts dir is the standing handoff, the builders are the subagents, Implementation
   slices are the splitter. `/compact` is reserved for the case nothing else covers.

The signals survived from generation 2, demoted from triggers to symptoms — they are
still the things the agent can actually observe.

## EXPLORE Mode

Exploration needs *more* honesty than production work, not less: a misleading prototype
conclusion poisons every decision built on it. That is why Rules 0, 1, 2 and 9 cannot be
switched off in any mode, while the test and scope discipline can be.

Promotion from prototype to production is an explicit decision, not a silent upgrade —
hence the exit procedure that makes the agent list what it skipped.

## Why the factory is always Default Mode

The factory is for features the team has committed to ship. Prototype / spike / POC work
does not go through `/feat-*` at all. This resolves the only real tension between this
contract and the pipeline: Rule 7's test discipline always applies inside the factory,
and EXPLORE Mode never reaches it.

---

## Provenance

Rules adapted from [Andrej Karpathy's observations](https://x.com/karpathy/status/2015883857489522876)
and [forrestchang/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills),
layered for our team's needs. The pipeline's grill / slices / smells / prompt-style
material comes from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT) — see
"Pocock provenance" below.

---

# Factory mechanisms

## Why commands + hooks, not a natural-language orchestrator
- **Order** = a human invoking discrete commands, not a model deciding the sequence.
- **Scope** = hooks (`scope-track.sh`) hard-block writes; a `tools:` list is only a hint.
- **Loop** = `/feat-fix` increments `retries` and stops at `loopMaxRetries` (default 3).
  Re-entry after a stop is itself a command (`/feat-unblock`), never a silent state edit.
- **Hand-off** = files on disk: cheap, reviewable, resumable — never re-pasted context.
  Each subagent starts with a fresh, isolated context and shares only the filesystem.

## Blocked handling
`/feat-fix` increments `retries` BEFORE checking, so with `loopMaxRetries = 3` the 1st–3rd
runs fix and the 4th stops. At the cap it writes the open findings, sets `blocked`, and
removes `.active` so the human regains normal editing. `retries` persists, and nothing
used to reset it: after a manual fix the next `/feat-fix` computed `4 > 3` and re-blocked
at once. `/feat-unblock` is the audited way back — it shows the evidence, records how the
block was handled in `unblock.md` (the distiller later reads the human's own diagnosis),
and resets the budget. Blocks are often spec problems rather than code problems, so a
second block on the same feature pushes the human upstream (revise the ⏸ gates, or split
the slug) instead of resetting again. Distill-before-unblock keeps open findings in the
Watchlist while the trail is warm. Unblocking stays outside any `/goal` loop: it is a
judgment call, not a convergence step.

## Fable 5 addendum
Applies when the orchestrating session runs Claude Fable 5; on other models it is inert:
the `model:` fields are plain subagent routing and the refusal path never triggers.
- **Model routing.** The main session carries the expensive model; every factory agent is
  pinned to `sonnet` in its frontmatter, with the reason in a comment beside it. The
  validator's value is independence (a different context), not cheapness; the
  test-verifier writes real tests, so it is an author, not a Haiku-grade grader.
  Security-sensitive work (an Off-Limits area) is the most classifier-prone: switch that
  builder to `model: opus` for the feature, or keep the work outside the factory.
- **Classifier refusals.** A loop that cannot tell "the classifier said no" from "my code
  is wrong" burns its retry budget rephrasing a refusal — hence the separate token, the ⛔
  heading, and `blocked-classifier` outside the retry count. The API's fallback to another
  model is opt-in, not automatic.
- **Memory layer.** `MEMORY.md` holds verified facts, general rules, and a dated
  Watchlist. `/feat-distill` closes a feature — after `/feat-docs`, straight after a clean
  validate, or after a block (open findings go to the Watchlist, never to General rules).
  Only evidence-backed entries, capped near 150 lines, English, version-controlled: review
  its diffs like code.
- **Convergence loop.** `/feat-ship` + `/goal` automates only the mechanical tail; the two
  ⏸ checkpoints stay human. The goal text follows three constraints: every condition is
  provable from output shown in the transcript (the evaluator, default Haiku, sees only
  the conversation); it carries its own turn cap (`/goal` has no hard iteration limit);
  and it names `blocked`, `blocked-classifier` and ⛔ as goal-cannot-be-met, so a refusal
  or a capped loop ends loudly. `loopMaxRetries` stays the binding stop.
- **References.** Motivated by 0xCodez's self-improving-agent thread
  (https://x.com/0xCodez/status/2065089060104720776) and its BlockTempo zh-TW translation
  (https://www.blocktempo.com/self-improving-agent-fable-5-2/). Inspiration, not
  specification: every product-behaviour claim was re-verified against Anthropic's
  official documentation before adoption.

## Maintenance commands
- `/feat-recomment`'s `--check` is deliberately not wired into `quality-gate.sh`: comment
  style is not a build failure. The script only reorders lines, so the migration diff is
  mechanical and reviewable, and it refuses a dirty tree so the change lands as one commit.
- `/feat-sweep` reports shallow modules only; the smells baseline stays with the
  validator, on per-feature diffs. Cadence is the human's; no step prompts for it.

## Pocock provenance
Adapted from mattpocock/skills (MIT), verified against the repo and the author's own posts
(2026-07) before adoption: the grill step, Implementation slices, the validator's smells
baseline and deletion test, and the prompt-style rules.
- v1.2.0 re-sync (2026-08): grill moved to round-by-round frontier interviewing; the cache
  test joined the prompt style; the smells baseline grew 8 → 12; Context Health was
  rebuilt around the phase-boundary ladder (continue → clear → hand off → subagent →
  compact).
- v1.2.3 re-sync (2026-09): Evidence & redaction, from `diagnosing-bugs`' Redact section —
  the transferable part is redact-before-you-show, which pasted evidence makes
  load-bearing the same way.
- `/feat-sweep` (2026-09) from `improve-codebase-architecture`; `/feat-epic` (2026-09) from
  `/wayfinder` as read on main 2026-09-20 — kept the destination, map-as-index, decision
  tickets, blocking frontier, fog of war and plan-don't-do; dropped the issue tracker,
  ticket claims, and the `task` type.
- `writing-for-agents` re-sync (2026-09-20): `WRITING-FOR-AGENTS.md` now carries the full
  current reference (context pointers, the two loads, the information hierarchy,
  completion criteria, sprawl, single source of truth, sediment), disclosed behind a
  pointer instead of imported.
- Deliberately NOT adopted: CONTEXT.md (covered by MEMORY.md plus per-slug decisions.md,
  keeping the single writer), the setup skill (covered by `/feat-init` + `project.json`),
  and v1.2.3's harness-portability pass — this template is Claude Code only by design,
  since model routing, hooks and `.active` are Claude Code mechanisms.
