# Feature Factory template (Plan A: per-repo, version-controlled)

**Language 語言:** English · [繁體中文](docs/README_zh-tw.md)

A reusable, language-agnostic Claude Code pipeline. One template, copied into each repo;
behaviour is driven by a per-repo manifest (`.claude/factory/project.json`). Works for
full-stack, frontend-only, or backend-only projects.

## Learn more
- **[Training guide](docs/factory-training_en.html)** — one-page walkthrough of the design
  philosophy, the assembly line, the mechanisms, and the Fable 5 upgrade (for onboarding).
- **[Cheatsheet](docs/factory-cheatsheet_en.md)** — one-screen quick reference: install,
  command flow, stuck-state table, non-negotiables (for daily use).

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
snippet is copied as a starter.

## First-time setup in the repo (3 steps)
1. Merge `CLAUDE.factory-snippet.md` into your `CLAUDE.md` (add the `@import` line near the
   top; paste the block into "Project-Specific Rules"). Skip if you let it be the starter.
2. Open Claude Code in the repo and run `/feat-init` (detects stack or asks; writes
   `project.json`; does NOT scaffold code).
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
/feat-distill <slug>    # FABLE 5: bank this feature's verified lessons into MEMORY.md
/feat-ship <slug>       # FABLE 5 (optional): converge verify→validate→fix under one /goal
/feat-status <slug>     # any time
```
FABLE 5 additions (model routing, classifier-refusal handling, memory layer, convergence
loop) are documented in the "Fable 5 addendum" of `.claude/factory/CONVENTIONS.md`. They
are inert-but-harmless when the session runs another model.
See `.claude/factory/CONVENTIONS.md` for the full design.


This template does not auto-commit or open PRs by design.
