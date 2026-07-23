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
