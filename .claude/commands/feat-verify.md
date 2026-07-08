---
description: Write acceptance tests from the story, run them, and report pass/fail.
argument-hint: <slug>
---
Verify step for feature `$1`.

1. Write `test $1` to `.claude/factory/.active`.
2. Use the **test-verifier** subagent to write acceptance tests from `story.md`'s criteria (tests directories only), run them, and write `<artifactsDir>/$1/verification.md` (criterion → pass/fail; per failure: expected/actual/owning track).
3. Update `state.json` step to `verify`. Next step: `/feat-validate $1`.
