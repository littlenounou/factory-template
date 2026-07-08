---
description: Read-only review against story+brief; classify findings; decide whether a fix loop is needed.
argument-hint: <slug>
---
Validate step for feature `$1`.

1. Write `docs $1` to `.claude/factory/.active`.
2. Use the **validator** subagent to review the implementation against `story.md` + `brief.md` + `verification.md` and write `<artifactsDir>/$1/validation.md` with 🔴Critical / 🟠Important / ⚪Minor findings, each citing `path:line` + owning track.
3. Update `state.json` step to `validate`.
4. Decide:
   - If there are any 🔴 or 🟠 findings, or any failing acceptance test → tell the user to run `/feat-fix $1`.
   - If clean → remove `.claude/factory/.active` (re-enable normal editing) and tell the user the feature is ready for their own review/commit. (This template does not auto-commit or open PRs.) FABLE 5: also suggest running `/feat-distill $1` to bank this feature's verified lessons into MEMORY.md before moving on.
