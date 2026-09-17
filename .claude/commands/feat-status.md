---
description: Show where a feature is in the pipeline.
argument-hint: <slug>
---
Status for feature `$1`.

- Print `<artifactsDir>/$1/state.json`.
- List which artifacts exist (research/decisions/story/brief/backend-summary/verification/validation).
- Print the contents of `.claude/factory/.active` if it exists (the currently enforced track), else note that no factory step is active.
- Suggest the next command based on `step`. Special case: if `step` is `blocked` or
  `blocked-classifier` (or `distilled` with open findings in `validation.md`), also show
  the current `retries` count and the blocked-handling flow: `/feat-distill $1` first
  (bank open findings into the Watchlist), then human intervention, then
  `/feat-unblock $1` to reset the retry budget and re-enter at verify.
