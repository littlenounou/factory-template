---
description: Interview the human about the feature plan until shared understanding, then write decisions.md. Runs after /feat-research; /feat-story is gated on its output.
argument-hint: <slug>
---
Grill step for feature `$1`. This step runs in the MAIN session — subagents cannot hold a
multi-turn interview.

1. Write `docs $1` to `.claude/factory/.active`.
2. Read `<artifactsDir>/$1/idea.md`, `research.md` (if present), and `<artifactsDir>/MEMORY.md` (if present).
3. Interview the user relentlessly about every aspect of this plan until you reach a shared
   understanding. Walk down each branch of the design tree, resolving dependencies between
   decisions one-by-one. For each question, provide your recommended answer. Ask the
   questions one at a time, waiting for feedback before continuing. If a question can be
   answered from `research.md` or by reading the codebase (read-only), read instead of asking.
4. If idea + research leave no open decisions, say so and converge immediately — an empty
   grill is a valid outcome for small features.
5. On consensus, write `<artifactsDir>/$1/decisions.md` (English), sections:
   - **Decisions** — one line each: `- [D#] decision — rationale`. Mark genuinely
     hard-to-reverse ones `[durable]` (candidates for MEMORY.md; only `/feat-distill` may
     write MEMORY.md — never write it here).
   - **Glossary** — canonical terms settled during the grill (`term: definition`). Omit if none.
   - **Declined alternatives** — options considered and rejected, with why. Omit if none.
6. Update `state.json` step to `grill`.
7. Tell the user the next step is `/feat-story $1`.

Rules:
- Never batch questions; one per turn, each with a recommended answer.
- Do not write or modify source code in this step.
- decisions.md records settled decisions only — do not restate idea.md.
