---
description: Build the frontend portion of an approved brief (frontend track only).
argument-hint: <slug>
---
Frontend build step for feature `$1`.

1. GUARD: if `tracks.frontend.enabled` is not true, STOP and say this repo has no frontend track — go to `/feat-verify $1`.
2. Write `frontend $1` to `.claude/factory/.active`.
3. Use the **frontend-builder** subagent to implement the UI per `brief.md`. If the backend track is enabled, it must consume `backend-summary.md` and must NOT invent endpoints — report contract gaps instead.
4. Run `bash .claude/hooks/quality-gate.sh frontend`. Report any failures honestly.
5. Update `state.json` step to `frontend`. Next step: `/feat-verify $1`.
