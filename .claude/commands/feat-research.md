---
description: Map the codebase for a feature (uses the built-in read-only Explore) and write research.md.
argument-hint: <slug>
---
Research step for feature `$1`.

1. Set the active phase: write `docs $1` to `.claude/factory/.active`.
2. Use the built-in **Explore** subagent (read-only) to investigate, then write `<artifactsDir>/$1/research.md` with: relevant files mapped, existing patterns to follow, similar features already in the codebase, and risks (e.g. auth/tenant, timezones, concurrency, existing infra to reuse). Do not modify any code.
3. Update `state.json` step to `research`.
4. Tell the user to skim research.md, then run `/feat-story $1`.
