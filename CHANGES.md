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

## Pruning pass (style-only, zero behaviour change) — same day, round 2
Applied the Prompt style rules retroactively:
- All 8 agent frontmatter descriptions cut to one line (249 → 103 words, −58%).
  Factory agents are only name-invoked by commands; rich trigger descriptions were
  pure context load on the orchestrating session.
- feat-docs.md no longer restates the doc-writer agent file (which IS the subagent's
  system prompt): 304 → 194 words. The checklist survives as leading words.
- Minor no-op prunes in story-writer / validator / doc-writer bodies; backend and
  frontend builders' hook-block wording converged (deliberate cross-context duplication
  kept, phrasing unified).
- Deliberately untouched: feat-ship (goal text is precision machinery), feat-fix,
  and all remaining commands — no no-ops found worth the diff noise.

## Follow-ups (not in this pass)
- Regenerate `factory-cheatsheet_{en,zh-TW}.md` and `factory-training_{en,zh-TW}.html`
  (they still describe the 14-command flow).
- Watchlist: /wayfinder-style epic planning layer (`/feat-epic`); periodic deep-module
  sweep as an explore-mode tool (`/arch-sweep`: read-only detection outside the factory,
  execution re-enters via /feat-new).
