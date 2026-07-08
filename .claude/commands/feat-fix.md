---
description: Route validation/verification failures back to the right builder, with a bounded retry cap.
argument-hint: <slug>
---
Fix loop for feature `$1`.

1. Read `state.json` and `project.json`. Increment `retries` by 1.
2. STOP CONDITION: if `retries` now exceeds `loopMaxRetries` (default 3), do NOT fix. Write a short summary of the still-open findings, set `state.json` step to `blocked`, remove `.claude/factory/.active`, and tell the user the loop hit its cap and needs human judgement. End here.
3. Otherwise, read `validation.md` + `verification.md`. For each 🔴/🟠 finding and each failing test, identify the owning track. For each owning track in turn:
   - write `<track> $1` to `.claude/factory/.active`;
   - delegate the specific fixes to that track's builder (backend-builder / frontend-builder), changing only what the finding requires (surgical);
   - run `bash .claude/hooks/quality-gate.sh <track>`.
4. Save `state.json`. Tell the user to re-run `/feat-verify $1` then `/feat-validate $1` to confirm the fixes.
