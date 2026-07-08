---
description: Route validation/verification failures back to the right builder, with a bounded retry cap.
argument-hint: <slug>
---
Fix loop for feature `$1`.

0. FABLE 5 GUARD — classifier refusals are not defects. Before touching `retries`, scan `validation.md`, `verification.md`, and any builder reports for `classifier-refusal` markers (incl. the validator's ⛔ section). Set those findings aside: they were declined by the model's safety classifier, not caused by broken code, so they must NOT consume retries and must NOT be retried by rephrasing.
   - If ALL open findings are classifier refusals: set `state.json` step to `blocked-classifier`, remove `.claude/factory/.active`, list the refused items, and tell the user to either (a) re-run that specific step with the owning agent's `model` switched to `opus`, or (b) handle those items manually. END HERE — do not increment retries.
   - Otherwise, continue below with the remaining (normal) findings only; carry the refused items forward untouched in your final report.

1. Read `state.json` and `project.json`. Increment `retries` by 1.
2. STOP CONDITION: if `retries` now exceeds `loopMaxRetries` (default 3), do NOT fix. Write a short summary of the still-open findings, set `state.json` step to `blocked`, remove `.claude/factory/.active`, and tell the user the loop hit its cap and needs human judgement. FABLE 5: also suggest `/feat-distill $1` — a blocked feature's open findings belong in MEMORY.md's Watchlist so the next feature doesn't rediscover them. End here.
3. Otherwise, read `validation.md` + `verification.md`. For each 🔴/🟠 finding and each failing test, identify the owning track. For each owning track in turn:
   - write `<track> $1` to `.claude/factory/.active`;
   - delegate the specific fixes to that track's builder (backend-builder / frontend-builder), changing only what the finding requires (surgical);
   - run `bash .claude/hooks/quality-gate.sh <track>`.
4. Save `state.json`. Tell the user to re-run `/feat-verify $1` then `/feat-validate $1` to confirm the fixes.
