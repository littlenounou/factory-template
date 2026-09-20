---
description: Maintenance — read-only deletion-test sweep for shallow modules; writes sweep-report.md with ranked deepening candidates.
argument-hint: [path] (default: the enabled tracks' dirs)
---
Sweep the codebase for shallow modules and report deepening candidates. Target: `$1`
(default: the `dirs` of every enabled track in `.claude/factory/project.json`).

This is a MAINTENANCE command, not a pipeline step: it has no slug and no `state.json`.
It reads code and writes one file: `<artifactsDir>/sweep-report.md`. `.active`,
`state.json`, and `MEMORY.md` stay exactly as they are, so it is safe to run while a
feature is mid-flight. Any refactor it suggests enters the line through `/feat-new`, chosen
by the human.

1. SCOPE — decide where to look before looking. Deepening pays off where change keeps
   happening, so rank the target's files by how often they changed in recent history
   (`git log --since="3 months ago" --name-only --format=`) and spend the exploration
   there first. A `$1` the user named is taken as given.

2. CONTEXT — read root `CLAUDE.md`, `<artifactsDir>/MEMORY.md` (if present), and the
   previous `<artifactsDir>/sweep-report.md` (if present). A convention documented in
   `CLAUDE.md` overrides this sweep's judgement. A `[durable]` decision in MEMORY.md is
   settled — a module shaped by one is reported only with new evidence, and says so.

3. EXPLORE — use the built-in **Explore** subagent (read-only) to walk the scope and note
   friction: understanding one concept means bouncing between many small modules; an
   interface nearly as complex as its implementation; pass-through layers that only
   forward calls; logic extracted for testability while the real bugs live in how it is
   called. Apply the **deletion test** to every suspect: if inlining the module into its
   callers would make the code clearer, it is shallow — keep it as a candidate. If
   inlining would scatter real complexity across the callers, the module is deep — drop it.

4. REPORT — overwrite `<artifactsDir>/sweep-report.md` (English). Header: date, scope,
   `git rev-parse --short HEAD`. Then at most 7 candidates, strongest first, each with:
   - **Title** and strength: `Strong` (deletion test passes clearly, friction is real) /
     `Worth exploring` (payoff depends on where the code is going) / `Speculative`
     (listed for completeness).
   - `new` or `repeat` (it appeared in the previous report).
   - **Files** — every module involved, cited `path:line`.
   - **Friction** — what you observed, in one or two sentences.
   - **Deepening** — the proposed shape in plain English: what moves behind which interface.
   - **Benefit** — what gets easier to change or to test.
   - A paste-ready line: `/feat-new <slug> <one-line description>`.
   Close with **Top recommendation**: the one candidate to tackle first, and why.
   When no suspect passes the deletion test, say so explicitly — a clean sweep is a
   valid result, and a padded report costs the next reader more than an empty one.

5. Tell the user to review and commit `sweep-report.md` (its git history is the trend),
   and that a chosen candidate starts with its `/feat-new` line. The choice and the timing
   are theirs.

End with the Fail-Loud block: ✅ Verified (scope walked, suspects tested, candidates kept) /
⚠️ Skipped-Uncertain (areas not explored, suspects you could not judge) / ❓ Needs-human-input.
