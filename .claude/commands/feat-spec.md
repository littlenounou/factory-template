---
description: Turn the approved story into a technical brief, then pause for human approval.
argument-hint: <slug>
---
Spec step for feature `$1` (the story is assumed human-approved).

1. Write `docs $1` to `.claude/factory/.active`.
2. Use the **spec-writer** subagent to produce `<artifactsDir>/$1/brief.md` from `story.md` + `research.md` + root `CLAUDE.md` + `project.json`. The brief MUST state which tracks (backend/frontend) are affected — only tracks enabled in project.json.
3. Update `state.json` step to `spec`.
4. ⏸ STOP. Tell the user to review brief.md. On approval: if the brief affects the backend track run `/feat-backend $1`; otherwise run `/feat-frontend $1`.
