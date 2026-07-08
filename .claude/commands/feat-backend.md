---
description: Build the backend portion of an approved brief (backend track only).
argument-hint: <slug>
---
Backend build step for feature `$1`.

1. GUARD: read `.claude/factory/project.json`. If `tracks.backend.enabled` is not true, STOP and tell the user this repo has no backend track — skip to `/feat-frontend $1`. Do nothing else.
2. Write `backend $1` to `.claude/factory/.active`.
3. Use the **backend-builder** subagent to implement the backend per `brief.md`, write `backend-summary.md`, and add unit tests.
4. Run `bash .claude/hooks/quality-gate.sh backend`. If it fails, report the failures (do not mark done).
5. Update `state.json` step to `backend`. Tell the user the next step is `/feat-frontend $1` (if frontend enabled) else `/feat-verify $1`.
