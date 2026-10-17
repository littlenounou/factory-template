---
description: Show where a feature is in the pipeline, or where an epic's map stands.
argument-hint: <slug>
---
Status for feature `$1`.

If `<artifactsDir>/epics/$1/map.md` exists, `$1` is an epic — show this instead: Status,
Destination, the number of decisions so far, the frontier tickets and the blocked ones (by
title), the number of Not-yet-specified patches, and — once `cleared` — each Feature
breakdown slug with its `state.json` step (`not started` if it has no folder yet). Next:
`/feat-epic $1` while `charting`; once `cleared`, the first `/feat-new` line not yet run.

For a feature:
- Print `<artifactsDir>/$1/state.json`, plus `Epic: <e>` if `idea.md` carries `[epic: <e>]`.
- List which artifacts exist (research/decisions/story/brief/backend-summary/verification/validation).
- Print the contents of `.claude/factory/.active` if it exists (the currently enforced track), else note that no factory step is active.
- Suggest the next command based on `step`. Special case: if `step` is `blocked` or
  `blocked-classifier` (or `distilled` with open findings in `validation.md`), also show
  the current `retries` count and the blocked-handling flow: `/feat-distill $1` first
  (bank open findings into the Watchlist), then human intervention, then
  `/feat-unblock $1` to reset the retry budget and re-enter at verify.
