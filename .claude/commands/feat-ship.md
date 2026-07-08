---
description: FABLE 5 convergence loop. Pairs with /goal to drive verify → validate → fix to completion autonomously. Human checkpoints (story/spec) are NOT affected — this only automates the mechanical tail after the build steps.
argument-hint: <slug>
---
Ship-convergence step for feature `$1` (FABLE 5 — pairs with the built-in `/goal`).

0. PRECONDITIONS — check all three, STOP with a pointer if any fails:
   - `<artifactsDir>/$1/brief.md` exists (the human-approved spec; ship never skips the ⏸ checkpoints).
   - Every enabled build step has run: `state.json` step is `backend`, `frontend`, `verify`, `validate`, or a fix/blocked state — not `new`/`research`/`story`/`spec`.
   - `/goal` is available in this session (it is part of the hooks system; with `disableAllHooks` set you lose BOTH scope enforcement and /goal — do not run the factory that way).

1. If no goal is active: print the following for the user to run verbatim (Claude cannot set goals; only the user can), then end this turn.

   /goal Feature $1 converged, following the cycle in .claude/commands/feat-ship.md: (1) <artifactsDir>/$1/verification.md shows every acceptance criterion passing, (2) <artifactsDir>/$1/validation.md exists with zero 🔴 and zero 🟠 findings, (3) `bash .claude/hooks/quality-gate.sh all` exited 0 — each of (1)(2)(3) proven by command/file output actually shown in this conversation, not by assistant claims. If state.json reaches `blocked` or `blocked-classifier`, or validation.md gains a ⛔ classifier-refusal section, the goal CANNOT be met — say so explicitly instead of continuing. Or stop after 12 turns.

   Notes to give the user with it:
   - The evaluator (a separate small model, default Haiku) judges ONLY what appears in the transcript — this is why the condition demands shown output, and why each cycle below must paste its evidence.
   - The 12-turn clause is advisory (model-judged, not a hard mechanical stop). The HARD stop remains `loopMaxRetries` inside /feat-fix — that cap is binding here exactly as in manual runs.

2. While the goal is active, iterate the pipeline's own steps IN ORDER — do not invent a different loop:
   a. VERIFY — follow `.claude/commands/feat-verify.md` for `$1`; show the test run output.
   b. VALIDATE — follow `.claude/commands/feat-validate.md` for `$1`; show the findings summary.
   c. If verification is all-pass AND validation is clean: run `bash .claude/hooks/quality-gate.sh all`, paste its output, restate conditions (1)(2)(3) each with its evidence, and let the evaluator close the goal. Then suggest `/feat-distill $1`.
   d. Otherwise FIX — follow `.claude/commands/feat-fix.md` for `$1`. Its rules are BINDING inside this loop: the FABLE 5 classifier guard (step 0) and the retry cap (step 2) apply unchanged. If it ends in `blocked` or `blocked-classifier`, report per the goal condition that the goal cannot be met, suggest `/feat-distill $1` to bank the open findings, and tell the user to run `/goal clear`.

3. Non-negotiables while converging (restated because autonomous loops drift):
   - Never weaken, skip, or delete a test to satisfy the goal — the condition is about the code meeting the story, not about the transcript looking green (Rule 7 anti-reward-hacking).
   - Never work around a hook block; scope enforcement via `.active` stays exactly as in manual runs.
   - Fail-Loud applies to every cycle: each turn ends with ✅ / ⚠️ / ❓ as usual.
