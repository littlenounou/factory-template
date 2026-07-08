---
description: Start a new feature. Creates its artifact folder, idea.md, and state.json.
argument-hint: <slug> <one-line feature description>
---
Start a new feature.

- First token of "$ARGUMENTS" is the slug (kebab-case). The rest is the description.
- Read `artifactsDir` from `.claude/factory/project.json` (default `.claude/factory`).
- Create `<artifactsDir>/<slug>/` containing:
  - `idea.md` — the description text.
  - `state.json` — `{ "slug": "<slug>", "step": "new", "retries": 0 }`.
- Confirm creation and tell the user the next step is `/feat-research <slug>`.
