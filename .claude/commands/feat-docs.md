---
description: After a clean validation, generate user-facing documentation — English README + guides/examples with Mermaid diagrams, then Traditional Chinese (zh-TW) translations. Final pipeline step.
argument-hint: <slug>
---
User-facing documentation step for feature `$1`. Run this AFTER `/feat-validate $1` is clean.

This step does NOT move or archive the development artifacts. They stay in
`<artifactsDir>/$1/` (already separated per slug) and remain the source of truth for
`/feat-status` and any resume/fix. This step only AUTHORS new user-facing docs.

1. Read `docsDir` from `.claude/factory/project.json` (default `docs`).
2. Write `userdocs $1` to `.claude/factory/.active`. (This is a distinct scope token from the
   `docs` phase used by research/story/spec/validate. The `scope-track.sh` hook allows the
   `userdocs` step to write only inside `<docsDir>/`, the repo-root `README.md`, and
   `README_zh-TW.md`. It still cannot touch source, build output, deps, or vendored libs.)
3. Use the **doc-writer** subagent to:
   - Read `story.md`, `brief.md`, `backend-summary.md` (if present), the actual implemented
     source, and `.claude/factory/terminology-zh-tw.md`.
   - Author the ENGLISH docs first: update/create the repo-root `README.md`, plus
     operation/usage and example documents under `<docsDir>/`. Use **Mermaid** for any
     flowchart / sequence / Gantt / mindmap / class / state diagram where a diagram is
     clearer than prose.
   - Then produce the Traditional Chinese (Taiwan) translation of each English doc with the
     `_zh-TW` filename suffix (e.g. `README.md` → `README_zh-TW.md`,
     `<docsDir>/usage.md` → `<docsDir>/usage_zh-TW.md`).
   - Put a language-switch line at the TOP of BOTH versions of every doc (relative links),
     e.g. English: `> 🌐 **English** | [繁體中文](./README_zh-TW.md)` and
     zh-TW: `> 🌐 [English](./README.md) | **繁體中文**`.
   - Follow the TW terminology in `terminology-zh-tw.md` for the Chinese versions.
4. Update `state.json` step to `docs`, then set it to `done`.
5. Remove `.claude/factory/.active` (re-enable normal editing). Tell the user the docs are
   written (list the files created), ready for their own review/commit. FABLE 5: suggest
   `/feat-distill $1` as the closing step — bank this feature's verified lessons into
   MEMORY.md while the artifacts are fresh.
