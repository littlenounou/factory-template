---
description: Author the user story for a feature, then pause for human approval.
argument-hint: <slug>
---
Story step for feature `$1`.

1. Write `docs $1` to `.claude/factory/.active`.
2. Use the **story-writer** subagent to produce `<artifactsDir>/$1/story.md` from `idea.md` + `research.md`.
3. Update `state.json` step to `story`.
4. ⏸ STOP. Show the user the path to story.md and say: "Review the story and acceptance criteria. When you approve, run `/feat-spec $1`. If you want changes, tell me and I'll revise." Do not proceed automatically.
