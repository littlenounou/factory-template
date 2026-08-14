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

**Contract files.** `CLAUDE.md` `@import`s `CONVENTIONS.md` + `terminology-zh-tw.md` — those three load every turn. Three more under `.claude/factory/` are reached by pointer, never imported: `EXPLORE-MODE.md`, `PHASE-BOUNDARIES.md`, and `CLAUDE-rationale.md` (why each rule exists — human reading only; edit it in the same PR when you change a rule). The installer lists all five ok/MISSING.

## Run a feature

```
/feat-new <slug> "description"  → idea.md
/feat-research <slug>           → research.md (reads MEMORY.md first as Prior knowledge)
/feat-grill <slug>              → decisions.md  ⏸ round-by-round interview (gates /feat-story)
/feat-story <slug>              → story.md      ⏸ human approval before continuing
/feat-spec <slug>               → brief.md      ⏸ human approval before continuing
/feat-backend <slug>            → code + backend-summary.md (only if track enabled)
/feat-frontend <slug>           → UI (consumes the contract; reports gaps, never invents endpoints)

# Path A: manual                 # Path B: autonomous (FABLE5)
/feat-verify <slug>              /feat-ship <slug>
/feat-validate <slug>            → paste the /goal line it prints; evaluator judges each turn
  findings → /feat-fix (cap: loopMaxRetries=3) → back to verify
  at the cap → blocked → distill → human handles → /feat-unblock (resets retries)

/feat-unblock <slug>            → after `blocked`: human-authorized resume (resets retries)
/feat-docs <slug>               → user docs: README + docsDir guides (EN → zh-TW, Mermaid)
/feat-distill <slug>            → closing step: bank lessons into MEMORY.md (distill failures too)
/feat-status <slug>             → check progress any time
```

The line never commits or opens PRs for you — review and commit yourself at the end.

## Maintenance (outside the line)

```
/feat-recomment [path]          → migrate legacy interleaved bilingual comments to block form
```

No slug, no artifacts. Guards on a clean git tree, dry-runs first, then drives
`.claude/factory/comment-migrate.py`, which only REORDERS comment lines — never translates or
rewords. Blocks it refuses (commented-out code, lines mixing both languages) land in
`comment-migration-report.md` for a human. `--check` exits non-zero while interleaving remains.

## When you're stuck

| State | Meaning / what to do |
|---|---|
| validate clean | Run `/feat-docs` for user docs, close with `/feat-distill`, then review + commit yourself |
| `blocked` | Fix loop hit the 3-retry cap; needs a human. Flow: `/feat-distill` (findings → Watchlist) → fix manually / revise story-spec / accept risk → `/feat-unblock` (resets retries, re-enters at verify). `state.json` is changed by that command, not by hand |
| `blocked-classifier` | Safety classifier declined — **the code is not broken**. Switch that agent to `model: opus` and re-run, or handle manually; then `/feat-unblock` to re-enter the line |
| blocks a 2nd time | The problem is upstream — revise story/spec at the ⏸ gates or split the slug (`/feat-unblock` warns you) |
| Write blocked by a hook | By design — don't work around it. If truly needed: `rm .claude/factory/.active` (= leaving factory mode) |
| context feels bloated / you're repeating yourself | You're mid-phase — finish it. At the next boundary walk the ladder in `PHASE-BOUNDARIES.md`: continue → `/clear` → hand off → subagent → `/compact` last. `/clear` is the default: artifacts on disk rebuild the context |
| `jq not found` | Enforcement is actually OFF. Install jq, then continue |
| gate shows `(none configured, skipped)` | That command is blank in the manifest; add the script, then fill project.json back in |

## Non-negotiables

1. **The line = Default Mode**: prototypes/spikes run in EXPLORE and never enter `/feat-*`.
2. **Actually read the ⏸ gates**: story and spec are the only two human judgment points.
3. **MEMORY.md is code**: review its diffs — bad memory compounds as fast as good memory.
4. **Comments are block-after-block**: full English block → one empty comment line → full zh-TW block. Never alternate line by line; migrate legacy code with `/feat-recomment`, not by hand.
5. **Decide context at boundaries**: the seam between `/feat-*` steps is where you choose — `/compact` is the last option there, not the first. Mid-phase: continue, or split into subagents.
6. **Fail-Loud**: every step ends with ✅/⚠️/❓; "tests pass" never masks skipped tests; never run the factory with `disableAllHooks`.

<sub>The FABLE5 upgrades (model routing / classifier triage / memory layer / /goal convergence) are inert-but-harmless on other models — maintain one template for the whole team; pick the model with `/model`.</sub>
