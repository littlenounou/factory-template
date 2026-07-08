---
description: FABLE 5 memory layer. After a clean validation, distill verified lessons from this feature into the cross-feature MEMORY.md.
argument-hint: <slug>
---
Distill step for feature `$1` (FABLE 5 memory layer).

1. GUARD: read `<artifactsDir>/$1/validation.md`. If it does not exist, or still has open
   🔴/🟠 findings, STOP — distill only runs on validated features. Two exceptions, because
   failure lessons are the most valuable ones: a feature whose `state.json` step is
   `blocked` (fix loop hit its retry cap) or `blocked-classifier` MAY be distilled — its
   still-open findings go to the **Watchlist** as open risks, never to General rules as if
   they were resolved.
2. Write `docs $1` to `.claude/factory/.active`.
3. Use the **memory-distiller** subagent: read everything under `<artifactsDir>/$1/` plus the
   current `<artifactsDir>/MEMORY.md`, and update MEMORY.md per its entry contract.
4. Update `state.json` step to `distilled`. Remove `.claude/factory/.active`.
5. Report what changed in MEMORY.md: entries added / merged / dropped, or "no new lessons".
   This is the last factory step for a feature — the code itself is still yours to review
   and commit (this template does not auto-commit).
