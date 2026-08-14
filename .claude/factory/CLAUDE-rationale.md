# Why the rules are what they are (human reading — NOT loaded by the agent)

Companion to the root `CLAUDE.md`. Every rule there once carried an inline *Why* note;
those notes are here instead. Nothing in this file instructs the agent — it is not
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
the provenance notes in `CONVENTIONS.md`.
