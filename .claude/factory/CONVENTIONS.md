# Feature Factory — Conventions (cross-repo, do not edit per project)

A reliable, manifest-driven development pipeline for Claude Code. The sequence is driven
by explicit slash commands (you run one per step), scope/quality rules are enforced by
hooks, and the fix loop is bounded. Nothing relies on a single prompt "running on its own".

## Tracks & the manifest
Each repo has `.claude/factory/project.json` (created once by `/feat-init`). It declares
which tracks exist — `backend`, `frontend`, or both — with their source `dirs`, build
`commands`, and `protectedDirs`. It also declares `artifactsDir` (pipeline hand-off files)
and `docsDir` (user-facing documentation, default `docs`). Every command, agent, and hook
reads this file, so the SAME template works for a full-stack app, a pure-frontend app
(e.g. Vite), or a pure backend (.NET / Java / C). Disabled tracks are skipped automatically.

## The pipeline
```
/feat-init      (once per repo: write project.json)
/feat-new       <slug> "<desc>"   -> idea.md + state.json
/feat-research  <slug>            -> research.md   (built-in Explore, read-only)
/feat-story     <slug>            -> story.md      ⏸ human approves
/feat-spec      <slug>            -> brief.md      ⏸ human approves
/feat-backend   <slug>            -> code + backend-summary.md   (if backend enabled)
/feat-frontend  <slug>            -> UI            (if frontend enabled; reads the contract)
/feat-verify    <slug>            -> verification.md
/feat-validate  <slug>            -> validation.md (read-only review)
/feat-fix       <slug>            -> bounded loop back to the owning builder
/feat-docs      <slug>            -> README + guides/examples (EN, then zh-TW)  [after a clean validate]
/feat-status    <slug>            -> where am I
```
Each step writes its output as a file under `<artifactsDir>/<slug>/`. The next step reads
those files — that is how context is handed between agents (each subagent starts with a
fresh, isolated context window and shares only the filesystem). State lives in `state.json`.

## What makes this reliable (vs a natural-language orchestrator)
- **Order** = you invoking discrete commands, not a model deciding the sequence.
- **Scope** = hooks (`scope-track.sh`) hard-block writes, not just `tools:` hints.
- **Loop** = `/feat-fix` increments `retries` and STOPS at `loopMaxRetries` (default 3).
- **Handoff** = files on disk (cheap, reviewable, resumable), not re-pasted context.

## Scope enforcement (.active)
While a build step runs, the command writes `<track> <slug>` to `.claude/factory/.active`.
`scope-track.sh` then allows writes only inside that track's dirs (plus the artifacts dir),
and always blocks build output / deps / vendored libs. With NO `.active` file, normal
editing is never blocked. `/feat-validate` (when clean), `/feat-docs` (on finish), and
`/feat-fix` (at cap) remove `.active`. You may `rm .claude/factory/.active` at any time to
disable enforcement. Requires `jq`; if `jq` is absent, hooks fail safe (allow) and print a
notice. Scope tokens: `backend` / `frontend` → track dirs; `test` → testDirs; `docs`
(research/story/spec/validate authoring) → artifacts only; `userdocs` (the `/feat-docs`
step) → `docsDir` + repo-root `README.md` / `README_zh-TW.md` only.

## User-facing documentation (the /feat-docs step)
`/feat-docs` runs AFTER a clean `/feat-validate`, via the **doc-writer** agent. It does NOT
move or archive artifacts — they stay in `<artifactsDir>/<slug>/`, already separated per
slug, and remain the source of truth for `/feat-status` and resume/fix. It only AUTHORS new
user-facing docs: English `README.md` + guides/examples under `docsDir` (with **Mermaid**
diagrams), then their Traditional Chinese (Taiwan) translations with the `_zh-TW` suffix and
a language-switch link at the top of every version. See `terminology-zh-tw.md` for the
comment rule, the document-language policy, and the TW term dictionary.

## Mode contract
**Running the factory == Default Mode** of the project's CLAUDE.md. The factory is for
features you have decided to ship. `explore` / `prototype` / `spike` / POC work is a
separate path that does NOT go through these commands (so the story/test discipline here
never conflicts with EXPLORE Mode's relaxed rules).

## Honesty
Every agent ends with the project's Fail-Loud format: ✅ Verified / ⚠️ Skipped-Uncertain /
❓ Needs-human-input. "Tests pass" is never used to mask skipped tests.
