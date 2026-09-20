---
description: User-facing docs after a clean validation — English README + guides with Mermaid, then zh-TW translations.
argument-hint: <slug>
---
User-facing documentation step for feature `$1`. Run this AFTER `/feat-validate $1` is clean.
The per-slug artifacts stay where they are, as the pipeline's record.

1. Read `docsDir` from `.claude/factory/project.json` (default `docs`).
2. Write `userdocs $1` to `.claude/factory/.active`.
3. Use the **doc-writer** subagent for slug `$1`. It is done when its report lists every doc
   it wrote in both languages.
4. Update `state.json` step to `docs`, then set it to `done`.
5. Remove `.claude/factory/.active` (re-enable normal editing). Tell the user the docs are
   written (list the files created), ready for their own review/commit. FABLE 5: suggest
   `/feat-distill $1` as the closing step — bank this feature's verified lessons into
   MEMORY.md while the artifacts are fresh.
