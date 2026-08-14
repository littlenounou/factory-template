---
description: Interview the human about the feature plan until shared understanding, then write decisions.md. Runs after /feat-research; /feat-story is gated on its output.
argument-hint: <slug>
---
Grill step for feature `$1`. This step runs in the MAIN session — subagents cannot hold a
multi-turn interview.

1. Write `docs $1` to `.claude/factory/.active`.
2. Read `<artifactsDir>/$1/idea.md`, `research.md` (if present), and `<artifactsDir>/MEMORY.md` (if present).
3. Map the open decisions as a DESIGN TREE — each decision branches into the decisions
   that hang off it — then interview the user round by round until the tree is resolved:
   - The FRONTIER is every decision whose prerequisites are already settled. Ask the
     whole frontier as ONE numbered round, then recompute the frontier from the answers
     and ask the next round. A question whose answer depends on a still-open question
     belongs to a later round. The session ends when the frontier is empty.
   - Every question uses this fixed shape, so the user can answer by number
     ("Q1 agree, Q2 agree, Q3 change to ..."):

     ❓ **Q<n>** — **<title>**: <body; include the choices if it is multiple-choice>
     ➡️ <your recommended answer>

   - If a question can be answered from `research.md` or by reading the codebase
     (read-only), read instead of asking. Dispatch such fact-finding to the built-in
     Explore subagent IN THE BACKGROUND so it never blocks a round: only the questions
     downstream of a running exploration wait for it — ask the rest of the frontier now.
   - If the user asks for one question at a time, honour that for the rest of the session.
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
- Every question carries a recommended answer. A round is a scannable numbered list —
  never a wall of prose, and never a question whose prerequisite is still open.
- This step reads code and writes one file: `decisions.md`.
- decisions.md records settled decisions only; idea.md already holds the request.
