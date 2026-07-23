---
description: Author the user story for a feature, then pause for human approval.
argument-hint: <slug>
---
Story step for feature `$1`.

1. GUARD: if `<artifactsDir>/$1/decisions.md` does not exist, STOP and tell the user to run
   `/feat-grill $1` first — the story consumes settled decisions, not open questions.
2. Write `docs $1` to `.claude/factory/.active`.
3. Use the **story-writer** subagent to produce `<artifactsDir>/$1/story.md` from `idea.md` + `research.md` + `decisions.md`.
4. Update `state.json` step to `story`.
5. ⏸ STOP. Show the user the path to story.md and say: "Review the story and acceptance criteria. When you approve, run `/feat-spec $1`. If you want changes, tell me and I'll revise." Do not proceed automatically.
