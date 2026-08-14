---
description: Human-authorized resume after a blocked or blocked-classifier stop. Shows the open findings, records how the block was handled, resets the retry budget, and re-enters at verify. Runs in the main session.
argument-hint: <slug>
---
Unblock step for feature `$1`. `retries` persists in `state.json` and this command is what
resets it (see CONVENTIONS.md, Blocked handling).

0. GUARD — read `<artifactsDir>/$1/state.json`. Proceed if `step` is `blocked` or
   `blocked-classifier`, or if `step` is `distilled` while `validation.md` still has open
   🔴/🟠 findings or a ⛔ section (distill-after-block is the recommended order, and it
   overwrites `step`). Otherwise STOP and report the current step.

1. SHOW THE EVIDENCE — the human decides with the facts in front of them. Print the open
   🔴/🟠 findings from `validation.md`, the failing tests from `verification.md`, any ⛔
   classifier-refusal items, the current `retries`, and any existing `unblock.md` entries.

2. ASK — one question, in this main session (a subagent cannot interview):
   **"How was this block handled?"** Wait for the answer; it determines step 7.

   | Answer | Meaning | Step 7 becomes |
   |---|---|---|
   | (a) Fixed manually | the human changed the code | `/feat-verify $1` → `/feat-validate $1` |
   | (b) Story/spec revised | root cause was upstream; a ⏸ artifact changed | re-approve the ⏸ artifact, re-run the affected build step, then verify → validate |
   | (c) Accepted as risk | findings stand, with a stated justification | `/feat-verify $1` → `/feat-validate $1` |
   | (d) Classifier route | refused step re-runs on `model: opus`, or was handled outside the factory | re-run that step first, then verify → validate |

3. DISTILL FIRST — if `/feat-distill $1` has not run for this block, recommend it and stop
   here: open findings belong in MEMORY.md's Watchlist while the trail is warm. The human
   may decline and continue.

4. ESCALATION — if `unblock.md` already has an entry, warn loudly: a feature that blocks
   twice has an upstream problem, and the productive move is revising the ⏸ gates or
   splitting the slug. Continue only if the human says so after the warning.

5. AUDIT — append to `<artifactsDir>/$1/unblock.md` (create if absent):
   `## Unblock — <YYYY-MM-DD>` with the previous step, retries consumed, one line per
   finding that was open, the human's step-2 answer verbatim, and whether distill ran or
   was declined. Findings in `validation.md` / `verification.md` stay as written — they are
   evidence, and verify/validate regenerate them.

6. RESET — set `retries` to 0 and `step` to `validate` in `state.json`; remove
   `.claude/factory/.active` if present.

7. NEXT — run the branch from the step-2 table. Once verify and validate are green the
   normal tail applies: `/feat-docs $1`, closing with `/feat-distill $1`. `/feat-ship $1`
   may drive the remaining convergence. Hard guardrail: a human runs this command, outside
   any active `/goal` loop — unblocking is a judgment call, not a convergence step.

End with ✅ Verified (state changes actually written, audit entry appended) /
⚠️ Skipped-Uncertain / ❓ Needs-human-input.
