---
description: After a clean validation, generate user-facing documentation — English README + guides/examples with Mermaid diagrams, then Traditional Chinese (zh-TW) translations. Final pipeline step.
argument-hint: <slug>
---
User-facing documentation step for feature `$1`. Run this AFTER `/feat-validate $1` is clean.

This step does NOT move or archive the development artifacts. They stay in
`<artifactsDir>/$1/` (already separated per slug) and remain the source of truth for
`/feat-status` and any resume/fix. This step only AUTHORS new user-facing docs.

1. Read `docsDir` from `.claude/factory/project.json` (default `docs`).
2. Write `userdocs $1` to `.claude/factory/.active` — a distinct scope token: the hook
   allows writes only inside `<docsDir>/`, root `README.md`, and `README_zh-TW.md`.
3. Use the **doc-writer** subagent for feature `$1`. Its agent file is the full authoring
   contract: English docs first (README + guides under `<docsDir>/`, Mermaid diagrams), then
   `_zh-TW` translations, language-switch links atop every doc, TW terminology.
4. Update `state.json` step to `docs`, then set it to `done`.
5. Remove `.claude/factory/.active` (re-enable normal editing). Tell the user the docs are
   written (list the files created), ready for their own review/commit. FABLE 5: suggest
   `/feat-distill $1` as the closing step — bank this feature's verified lessons into
   MEMORY.md while the artifacts are fresh.
