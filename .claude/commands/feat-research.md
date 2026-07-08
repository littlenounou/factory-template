---
description: Map the codebase for a feature (uses the built-in read-only Explore) and write research.md.
argument-hint: <slug>
---
Research step for feature `$1`.

1. Set the active phase: write `docs $1` to `.claude/factory/.active`.
2. FABLE 5 memory: if `<artifactsDir>/MEMORY.md` exists, read it first. Copy the entries
   relevant to this feature into a **Prior knowledge** section at the top of `research.md`
   (cite each as `[date slug]`), and use them to direct the exploration. Treat them as leads
   to verify against the current code, not as facts — the codebase may have moved on.
3. Use the built-in **Explore** subagent (read-only) to investigate, then write `<artifactsDir>/$1/research.md` with: relevant files mapped, existing patterns to follow, similar features already in the codebase, and risks (e.g. auth/tenant, timezones, concurrency, existing infra to reuse). Do not modify any code.
4. Update `state.json` step to `research`.
5. Tell the user to skim research.md, then run `/feat-story $1`.
