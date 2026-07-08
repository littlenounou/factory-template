# Feature Factory Cheatsheet (Fable 5 Edition)

**Language 語言:** [繁體中文](factory-cheatsheet_zh-TW.md) · English

> Full training: `docs/factory-training_en.html` · Design details: `.claude/factory/CONVENTIONS.md`
> Core belief: reliability comes from the system, not the model — sequence via commands, scope via hooks, bounded loops, independent verification.

## Install (once per repo)

```bash
./install.sh /path/to/repo   # copies .claude/; Windows: install.ps1 (run Claude Code via Git Bash/WSL)
jq --version                 # hooks need jq; missing = enforcement is OFF (fail-safe allow)
/feat-init                   # inside Claude Code: detects the stack, writes project.json, no scaffolding
```

Existing CLAUDE.md → merge the two `<<< FEATURE FACTORY >>>` blocks; greenfield repo → the snippet auto-becomes your starter CLAUDE.md.

## Run a feature

```
/feat-new <slug> "description"  → idea.md
/feat-research <slug>           → research.md (reads MEMORY.md first as Prior knowledge)
/feat-story <slug>              → story.md      ⏸ human approval before continuing
/feat-spec <slug>               → brief.md      ⏸ human approval before continuing
/feat-backend <slug>            → code + backend-summary.md (only if track enabled)
/feat-frontend <slug>           → UI (consumes the contract; reports gaps, never invents endpoints)

# Path A: manual                 # Path B: autonomous (FABLE5)
/feat-verify <slug>              /feat-ship <slug>
/feat-validate <slug>            → paste the /goal line it prints; evaluator judges each turn
  findings → /feat-fix (cap: loopMaxRetries=3) → back to verify

/feat-docs <slug>               → user docs: README + docsDir guides (EN → zh-TW, Mermaid)
/feat-distill <slug>            → closing step: bank lessons into MEMORY.md (distill failures too)
/feat-status <slug>             → check progress any time
```

The line never commits or opens PRs for you — review and commit yourself at the end.

## When you're stuck

| State | Meaning / what to do |
|---|---|
| validate clean | Run `/feat-docs` for user docs, close with `/feat-distill`, then review + commit yourself |
| `blocked` | Fix loop hit the 3-retry cap; needs a human. Distill first so open findings enter the Watchlist |
| `blocked-classifier` | Safety classifier declined — **the code is not broken**. Switch that agent to `model: opus` and re-run, or handle manually |
| Write blocked by a hook | By design — don't work around it. If truly needed: `rm .claude/factory/.active` (= leaving factory mode) |
| `jq not found` | Enforcement is actually OFF. Install jq, then continue |
| gate shows `(none configured, skipped)` | That command is blank in the manifest; add the script, then fill project.json back in |

## Non-negotiables

1. **The line = Default Mode**: prototypes/spikes run in EXPLORE and never enter `/feat-*`.
2. **Actually read the ⏸ gates**: story and spec are the only two human judgment points.
3. **MEMORY.md is code**: review its diffs — bad memory compounds as fast as good memory.
4. **Fail-Loud**: every step ends with ✅/⚠️/❓; "tests pass" never masks skipped tests; never run the factory with `disableAllHooks`.

<sub>The FABLE5 upgrades (model routing / classifier triage / memory layer / /goal convergence) are inert-but-harmless on other models — maintain one template for the whole team; pick the model with `/model`.</sub>
