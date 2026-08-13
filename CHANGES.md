# Bilingual comment style — change summary (2026-08-12)

Comment rule changed from line-interleaved (EN line / ZH line, alternating) to
block-after-block: the complete English block, one empty comment line, then the complete
Traditional Chinese (Taiwan) block. Reason: alternating lines forces the reader to skip
every other line to follow either language.

## New files
- **comment-migrate.py** (`.claude/factory/`) — stdlib-only Python 3 migration tool.
  Reorders existing comment lines only; never translates or rewords. Handles line comments,
  `*`-continuation blocks (JSDoc / Javadoc / Doxygen) and Python docstrings; preserves
  indentation, comment token and CRLF; idempotent. Refuses blocks containing commented-out
  code or lines mixing both languages, listing them in `comment-migration-report.md`.
  Dry-run by default; refuses `--apply` on a dirty git tree (its own report file is
  excluded from that check, so dry-run → apply is not self-blocking); `--check` is a CI guard.
- **feat-recomment.md** — `/feat-recomment [path]`: maintenance command (no slug, no
  artifacts) that guards, dry-runs, asks for approval, applies, then works the leftover
  review list by hand. Command count 15 → 16.

## Modified
- **terminology-zh-tw.md** — §1 rewritten: block-after-block structure, explicit "do NOT
  interleave", multi-line / docstring / one-line examples, and an anti-pattern example.
- **CLAUDE.factory-snippet.md** — comment bullet updated; changelog row added.
- **CONVENTIONS.md** — new "Legacy comment migration" section.
- **README.md / README_zh-TW.md** — comment-rule summary updated; migration paragraph added;
  counts 15 → 16 commands.
- **install.sh / install.ps1** — expected commands 15 → 16.
- **factory-cheatsheet_{en,zh-TW}.md** — new "Maintenance (outside the line)" block for
  `/feat-recomment`; new non-negotiable #4 on block-after-block comments (Fail-Loud → #5).
  Also cleared a pre-existing gap: `/feat-grill` was missing from the run-a-feature block.
- **factory-training_{en,zh-TW}.html** — new "Comment & doc contract" row in Under the Hood;
  new "Maintenance (outside the line)" terminal block in How to Run It; new House Rule on
  block-after-block comments; footer edition date 2026-07 → 2026-08. The pipeline belt and
  stage diagram are unchanged — `/feat-recomment` is maintenance, not a pipeline step.

## Follow-ups (not in this pass)
- Decide per repo whether to run `comment-migrate.py --check` in CI. It is deliberately NOT
  wired into `quality-gate.sh`: comment style should not fail a build, and a repo mid-migration
  would sit permanently red.

---

# Pocock integration — change summary (2026-07-23)

Adapted from mattpocock/skills (MIT). Four adoptions, agreed with the maintainer:
grill interview (mandatory, standalone command) + tracer-bullet slices + smells baseline
+ prompt-style rules. NOT adopted: CONTEXT.md, setup skill, /wayfinder (Watchlist item).

## New file
- **feat-grill.md** — `/feat-grill <slug>`: main-session interview (one question per turn,
  recommended answer each, codebase-answerable questions read not asked) → `decisions.md`
  with Decisions (`[durable]` markers), Glossary, Declined alternatives. Command count 14 → 15.

## Modified — pipeline placement
- **feat-research.md** — next step is now `/feat-grill`.
- **feat-story.md** — GUARD added: STOP if `decisions.md` missing; story-writer also reads it.
- **feat-status.md** — artifact list includes `decisions`.
- **CONVENTIONS.md** — pipeline diagram + new "Grill step" and "Prompt style" sections +
  provenance note. (Fixed nothing else; Fable 5 addendum untouched.)

## Modified — agents
- **story-writer.md** — reads decisions.md; settled decisions are not open questions;
  glossary terms are canonical.
- **spec-writer.md** — reads decisions.md; new brief section 7 "Implementation slices"
  (vertical tracer-bullet slices, `blocked-by` declarations); Risks renumbered to 8.
- **backend-builder.md / frontend-builder.md** — implement slice-by-slice in order;
  never start a slice whose blockers are unfinished.
- **validator.md** — Fowler smells baseline (8 smells; repo CLAUDE.md overrides; never 🔴
  on a smell alone) + shallow-module deletion test.
- **memory-distiller.md** — banks shipping-confirmed `[durable]` decisions into Verified
  facts; an overturned durable decision is recorded as the lesson.

## Modified — install & docs
- **install.sh / install.ps1** — expected commands 14 → 15.
- **README.md / README_zh-TW.md** — pipeline lists include `/feat-grill`; counts updated.

## Follow-ups (not in this pass)
- Regenerate `factory-cheatsheet_{en,zh-TW}.md` and `factory-training_{en,zh-TW}.html`
  (they still describe the 14-command flow).
- Optional maintenance pass: prune all 8 agents / 15 commands per the new Prompt style rules.
- Watchlist: /wayfinder-style epic planning layer (`/feat-epic`); periodic deep-module
  sweep as an explore-mode tool.
