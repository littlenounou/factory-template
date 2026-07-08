# Feature Factory template (Plan A: per-repo, version-controlled)

A reusable, language-agnostic Claude Code pipeline. One template, copied into each repo;
behaviour is driven by a per-repo manifest (`.claude/factory/project.json`). Works for
full-stack, frontend-only, or backend-only projects.

## Requirements
- Claude Code (CLI). Agents / commands / hooks only take effect there.
- `bash` and `jq` available on PATH (hooks use them). On Windows, run Claude Code from
  Git Bash or WSL so the hooks execute; install `jq`. Without `jq`, hooks fail safe
  (allow) and print a notice — i.e. enforcement is skipped, nothing breaks.

## Install into a repo
```
# macOS / Linux
./install.sh /path/to/your/repo
# Windows PowerShell
./install.ps1 C:\path\to\your\repo
```
The installer copies `.claude/` into the repo and makes hooks executable. If the repo
already has a `CLAUDE.md`, it is NOT modified — the installer drops
`CLAUDE.factory-snippet.md` next to it for you to merge. If there is no `CLAUDE.md`, the
snippet is copied as a starter. Expected counts after install: 7 agents, 12 commands, 3 hooks.

## First-time setup in the repo (3 steps)
1. Merge `CLAUDE.factory-snippet.md` into your `CLAUDE.md` (add the two `@import` lines near
   the top — `CONVENTIONS.md` and `terminology-zh-tw.md`; paste the block into
   "Project-Specific Rules"). Skip if you let it be the starter.
2. Open Claude Code in the repo and run `/feat-init` (detects stack or asks; writes
   `project.json` including `docsDir`; does NOT scaffold code).
3. Confirm the manifest.

## Run a feature
```
/feat-new <slug> "what you want"
/feat-research <slug>
/feat-story <slug>      # review story.md, then:
/feat-spec <slug>       # review brief.md, then:
/feat-backend <slug>    # if backend enabled
/feat-frontend <slug>   # if frontend enabled
/feat-verify <slug>
/feat-validate <slug>
/feat-fix <slug>        # only if findings; bounded by loopMaxRetries
/feat-docs <slug>       # after a clean validate: README + guides/examples (EN, then zh-TW)
/feat-status <slug>     # any time
```
See `.claude/factory/CONVENTIONS.md` for the full design.

## Comments, documentation & TW terminology
`.claude/factory/terminology-zh-tw.md` (imported by `CLAUDE.md`) is the single source of truth for:
- **Bilingual comments** — every comment is an English line followed by a Traditional Chinese (Taiwan) line.
- **Document language policy** — pipeline artifacts under `.claude/factory/<slug>/` are English only;
  user-facing docs (`README.md` + everything under `docsDir`) are English first, then a `_zh-TW`
  translation, each with a language-switch link at the top.
- **TW term dictionary** — Taiwan mainstream terms only (no Mainland China variants).

`/feat-docs` (the **doc-writer** agent) produces those user-facing docs with **Mermaid** diagrams
(flowchart / sequence / Gantt / mindmap / class / state). It does NOT move or archive the per-slug
artifacts — they stay in place as the pipeline's record.


This template does not auto-commit or open PRs by design.
