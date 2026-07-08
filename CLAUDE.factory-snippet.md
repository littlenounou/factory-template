<!-- =================================================================== -->
<!-- HOW TO USE THIS FILE                                                 -->
<!-- • NEW project (no CLAUDE.md yet): rename this file to CLAUDE.md      -->
<!--   as-is. You get the full behavioural contract + factory rules.      -->
<!-- • EXISTING CLAUDE.md: do NOT overwrite it. Lift only the two blocks  -->
<!--   marked  <<< FEATURE FACTORY >>>  into your own file:               -->
<!--     (1) the @import line near the top, and                          -->
<!--     (2) the "### Feature Factory" subsection under Project-Specific. -->
<!-- Then fill in Tech Stack + Test and Build Commands (or run /feat-init).-->
<!-- =================================================================== -->

# CLAUDE.md

> This file is the **behavioral contract** between this project and AI coding assistants (Claude Code). All code modifications made through AI must comply with this contract.
>
> Rules are inspired by [Andrej Karpathy's observations](https://x.com/karpathy/status/2015883857489522876) and [forrestchang/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills), adapted and layered for our team's needs. Each rule includes a **why** note so team members understand the design rationale rather than following blindly.

<!-- <<< FEATURE FACTORY (1/2): import shared pipeline conventions >>> -->
@.claude/factory/CONVENTIONS.md
<!-- <<< /FEATURE FACTORY (1/2) >>> -->

---

## How to Read This File

- **Bold == action**: what AI must do or avoid
- *Italic == rationale*: design reasoning for humans; AI reads it but doesn't act on it directly
- Rules are split into two tiers: **Always-On** (every context) + **Default Mode** (standard development)
- Exploratory work has its own **EXPLORE Mode**, activated explicitly by the user

**Mode-switching triggers:**
- User explicitly says `explore mode` / `prototype` / `spike` / `let's try it out` / `let's do a POC` → switch to EXPLORE Mode
- User says `ok let's commit to this direction` / `let's do this properly` → return to Default Mode
- All other situations: Default Mode

---

## Always-On Rules (active in every mode, cannot be disabled)

### Rule 0 — Fail Loud

If you cannot fully verify that something worked, **say so explicitly**. Do not use vague words like "complete", "tests pass", or "feature works" to mask uncertainty.

**Forbidden:**
- Skipping some tests yet reporting "tests pass"
- Skipping edge cases yet reporting "feature complete"
- Reporting "migration successful" when some records failed
- Filling unknowns with guesses without flagging them as guesses

**Required:** End your response with three explicit sections:
- ✅ **Verified**: [what you actually verified]
- ⚠️ **Skipped / Uncertain**: [what you didn't verify, and why]
- ❓ **Needs human input**: [what requires user judgment]

*Why: This is the single most important rule in this file. Silent failure is the biggest risk of AI collaboration — errors get smuggled into production. Better to be noisy about uncertainty than quiet about delivery.*

---

### Rule 1 — Surface Conflicts, Don't Average Them

When the codebase contains two contradictory patterns (naming, architecture, error handling, etc.):

1. **Pick one side**: prefer the more recent, better-tested, or documented-as-standard version
2. **Explain why you picked it**
3. **Flag the other for cleanup** (note it in the commit message or PR description)
4. **Absolutely forbidden**: writing a hybrid version that tries to satisfy both

*Why: "Average" code that satisfies two contradictory standards is harder to maintain than either original — it leaves future engineers permanently unsure which direction is correct.*

---

### Rule 2 — Read Before You Write

Before modifying any file larger than 50 lines, first read:

1. The file's exports / public API
2. At least one direct caller
3. Relevant shared utilities (if obviously imported)

For small files (< 50 lines) or leaf modules (no callers), this rule is relaxed.

**Forbidden phrase:** "Looks orthogonal to me, I'll just add it." This is usually wrong.

*Why: Without context, AI is most likely to make changes that look reasonable on the surface but violate the existing design. Reading first is the cheapest line of defense.*

---

## Default Mode Rules (standard development, bug fixes, production-bound work)

### Rule 3 — Think Before Coding

Before implementing:

- **State your assumptions explicitly** (especially ambiguous parts)
- **If multiple reasonable interpretations exist, list them and let the user choose** — don't silently pick one
- **If a simpler alternative exists, propose it**
- **If confused, stop and ask** — don't guess

*Why: AI's most common failure mode is "filling in blanks without confirmation". This rule forces explicit reasoning.*

---

### Rule 4 — Simplicity First, With Room for Reasonable Preparation

Default posture: solve **the current problem** with the **minimum** amount of code.

**Forbidden:**
- Abstraction layers for "future possible needs"
- Frameworks built around single-use code
- Unrequested "flexibility" or "configurability"
- Error handling for scenarios that cannot occur

**Exception (reasonable preparation, allowed):**
- Requirements **explicitly state** multiple variants (e.g., "support providers A, B, and C") → abstraction is reasonable
- Connecting to a defined extension point in an existing system

**Test: "Is this abstraction responding to a known need, or an imagined one?"** Former is OK, latter is forbidden.

*Why: Over-engineering is AI's most common side effect when writing code. But forbidding abstraction outright kills legitimate architectural preparation. "Known vs imagined" is the dividing line.*

---

### Rule 5 — Surgical Changes, With Disclosure

Touch only code **directly related** to the current requirement.

**Forbidden:**
- "Improving" adjacent code, comments, or formatting in passing
- Refactoring things that aren't broken
- Deleting pre-existing dead code (unless it became dead because of your current change)

**Required (surface, don't act):**
- If you spot dead code, obvious bugs, or potential security issues nearby → **list them in your response**, but do not modify them
- Let the user decide whether to open a separate task

*Why: Surgical changes keep PRs clean and reviewable. But "pretending you didn't see it" lets technical debt accumulate forever — disclosure is the necessary compromise.*

---

### Rule 6 — Goal-Driven Execution

Transform tasks into **verifiable concrete goals**:

| Weak instruction | Strong instruction |
|------------------|---------------------|
| "Add validation" | "Write tests for invalid inputs, then make them pass" |
| "Fix this bug" | "Write a test that reproduces the bug, then make it pass" |
| "Refactor X" | "All tests pass before and after the refactor" |

For multi-step tasks, state the plan first:

```
1. [step] → verify: [check]
2. [step] → verify: [check]
3. [step] → verify: [check]
```

*Why: Strong success criteria let AI loop independently to completion. Weak criteria ("make it work") require constant clarification.*

---

### Rule 7 — Tests Verify Intent, Not Just Behavior

Every test must answer **WHY** the behavior matters, not just **WHAT** it does.

**Test: "If the business logic changes, will this test fail?"**
- Yes → good test
- No → worthless test (e.g., hardcoded return values or hardcoded IDs that always pass but verify nothing)

**Mandatory:**
- Test names must include **business language**: `test('VIP customers receive 10% discount')` ✅, not `test('getDiscount')` ❌
- At least one **counter-example test**: under what conditions should the behavior **not** occur
- Reject tautological tests where the test name is just a restatement of the function name

*Why: When you tell AI "write tests and make them pass", there are two mathematical paths to success — actually verify business logic (right path), or write empty tests that always pass (wrong path). This rule is the structural defense against reward-hacking.*

---

### Rule 8 — Match Conventions, But Don't Copy Anti-Patterns

**Default:** follow the codebase's existing conventions for naming, architecture, and error handling.
- Existing code uses snake_case → use snake_case
- Existing code uses class components → don't silently switch to hooks
- Existing code uses a particular error-handling pattern → match it

**Exception:** if the existing convention is a widely-recognized anti-pattern (global mutable state, empty catch, callback hell, God Object, SQL-injection-prone patterns, etc.):
- **Do not silently copy it**
- **Surface it and let the human decide**
- Whether to refactor is a separate conversation, but don't pretend not to see it

**Test: "Is this a deliberate team choice, or accumulated team debt?"** Follow the former; surface the latter.

*Why: Blind compliance lets AI propagate bad habits. But unilateral "improvement" fragments style and breaks team consistency. Surfacing without acting is the lowest-impact compromise.*

---

### Rule 9 — Use the Model Only for Judgment Calls

**Use AI for:** classification, drafting, summarization, extraction from unstructured text, naming suggestions, code review feedback, documentation generation.

**Do NOT use AI for:**
- Deterministic transforms (status code → error type mappings, etc.)
- API routing / dispatch
- Retry logic
- Anything expressible as `if-else` or a lookup table

If a task can be handled by plain code with deterministic logic, do not delegate it to AI — AI's stochasticity makes production behavior unpredictable, undebuggable, and non-reproducible.

*Why: AI is good at "interpretation" work, not "guarantee" work. Putting AI in the wrong slot makes systems hard to debug and hard to trust.*

---

### Rule 10 — Checkpoint After Every Significant Step

In multi-step tasks, after **each completed step**, report:

- ✅ **Done**: [what was completed]
- ✅ **Verified**: [how it was verified]
- ⏳ **Remaining**: [what's left]

**Forbidden:** continuing from a state you cannot describe back. If you've lost context, **stop and restate** — don't push through.

*Why: The most dangerous failure in long tasks is "stacking on top of errors". Checkpoints catch errors early and prevent contamination of later steps.*

---

## Context Health (replaces the original Rule 6 token budget)

AI cannot reliably count its own token usage, but **some signals are observable**. When the following occur, proactively suggest action to the user:

1. **Same error attempted ≥ 3 times without resolution** → "We might be heading the wrong way. Want me to `/compact` and replan, or can you give me a hint?"
2. **Catching yourself repeating questions already answered** → suggest `/compact` to consolidate context
3. **Task scope has clearly drifted from the original** → "Scope has shifted. Want to commit what's done and start a new session for the new requirement?"
4. **Execution plan exceeds 5 major steps** → suggest splitting into multiple PRs / sessions
5. **More than 10 files require modification** → suggest doing the most critical ones first, in batches

*Why: Original "4000 tokens per task" hard numbers cannot be reliably enforced by AI — they become performative. But "same error 3 times" or "task drift" are signals AI can actually observe and act on.*

---

## EXPLORE Mode

**Activation triggers:** user explicitly says `explore mode` / `prototype` / `spike` / `let's try it out` / `let's do a POC` / `let's see if this is feasible` or similar phrasing.

**Rule adjustments when active:**

| Rule | Behavior in EXPLORE Mode |
|------|--------------------------|
| Rule 3 (Think Before Coding) | **Weakened**: stop and ask only for architecture-affecting decisions; decide small things yourself |
| Rule 4 (Simplicity First) | **Weakened**: allow quick scaffolding now, simplify later |
| Rule 5 (Surgical Changes) | **Disabled**: free to make broad changes during exploration |
| Rule 6 (Goal-Driven Execution) | **Weakened**: "it runs" counts as success; full test criteria not required |
| Rule 7 (Tests Verify Intent) | **Disabled**: no tests required during exploration |
| Rule 8 (Match Conventions) | **Weakened**: experimentation with new styles OK inside `prototype/`, but conventions still apply elsewhere |
| Rule 10 (Checkpoint) | **Weakened**: report only when a demoable milestone is reached |

**Still active (cannot be disabled):**

- **Rule 0 (Fail Loud)** — exploration requires more honesty, not less; misleading conclusions poison later decisions
- **Rule 1 (Surface Conflicts)** — style fragmentation is harmful even in prototypes
- **Rule 2 (Read Before Write)** — touching existing code still requires understanding it
- **Rule 9 (Use AI for Judgment)** — never use AI as a substitute for deterministic code, regardless of mode

**Leaving EXPLORE Mode:** when user says "let's commit to this direction" / "let's do this properly" or similar:

1. Return to Default Mode
2. **Proactively list what was skipped during EXPLORE Mode** (tests, edge cases, documentation, error handling, etc.)
3. Let the user decide what to backfill and what to abandon
4. Promotion from prototype to production should be an explicit decision, not a silent upgrade

---

## Project-Specific Rules

> This section is filled in by the team and applies alongside the universal rules. **If they conflict, this section takes precedence.**

<!-- <<< FEATURE FACTORY (2/2): pipeline rules for this repo >>> -->
### Feature Factory (project-specific)

- **Running any `/feat-*` command == Default Mode.** The factory is for features we have
  committed to ship. Prototype / spike / POC work does not go through the factory, so it
  is unaffected by EXPLORE Mode. (This resolves the only real tension between this contract
  and the pipeline: Rule 7's test discipline always applies inside the factory.)
- **Track config lives in `.claude/factory/project.json`** (run `/feat-init` once). Agents,
  commands, and hooks read it; do not hardcode paths or commands elsewhere.
- **Scope is hook-enforced** via `.claude/factory/.active`; do not work around a blocked
  write — it is intentional (aligns with Rule 5: surgical, in-track changes only).
- **Every factory agent ends with Fail-Loud** ✅ / ⚠️ / ❓ (Rule 0).
- **Deterministic flow control (order, branching, the fix loop) lives in commands + hooks,
  not in the model's judgement** (Rule 9). The pipeline sequence is driven by you invoking
  one `/feat-*` command per step.
<!-- <<< /FEATURE FACTORY (2/2) >>> -->

### Tech Stack

- [Fill in, or let `/feat-init` detect — e.g., TypeScript 5.x strict mode, React 19, Vitest, Postgres 16]

### Mandatory Conventions

- [Fill in, e.g., all API endpoints must have tests]
- [E.g., error handling goes through the Result type in `src/utils/errors.ts`]
- [E.g., no `any`; use `unknown` + type guard when necessary]
- [E.g., all database migrations must be reversible]

### Off-Limits Areas

- [Fill in, e.g., `legacy/` directory requires review before modification]
- [E.g., `migrations/` already-deployed files are append-only; changes go in new files]
- [E.g., any change to `src/security/` requires security team approval]

### Test and Build Commands

- Tests: `[fill in]`
- Type-check: `[fill in]`
- Lint: `[fill in]`
- Local dev: `[fill in]`

### Domain Knowledge (optional)

- [If the project has specific business terminology, abbreviations, or domain models, list them here]

---

## Changelog

| Date | Author | Change |
|------|--------|--------|
| 2026-05-20 | Robert | Initial version: 12-rule framework with EXPLORE Mode layering |
| 2026-06-05 | Robert | Merged Feature Factory pipeline (@import CONVENTIONS + project-specific block) |
| 2026-07-06 | (fill in) | Fable 5 upgrade: agent model routing, classifier-refusal handling (`blocked-classifier`), memory layer (`/feat-distill` + MEMORY.md), convergence loop (`/feat-ship` + `/goal`). Marked FABLE5 throughout; inert on other models. |

---

*This file is a contract between the team and AI, not a unilateral instruction from AI. If team members find a rule failing in practice or causing harm, open a PR to modify this file — **rules are tools, not scripture**.*
