# Unblock command — recovered and applied (2026-08-14, designed 2026-07-31)

**This work was designed on 2026-07-31 and never landed in the repo.** It was delivered as
an overlay zip that was evidently not extracted: `feat-unblock.md` is absent, no
2026-07-31 entry existed in this file, and the command count stayed at 16. As a knock-on,
the 2026-08-12 entry below records "Command count 15 → 16" for `/feat-recomment` against a
base that should already have been 16. **Correct count is now 17** (8 agents, 17 commands,
3 hooks). The design below is the one agreed in that session, re-applied to the files as
they stand today and rephrased where it collided with the writing-for-agents negation rule.

## The gap it closes
`retries` is persisted in `state.json` and nothing reset it. After a `blocked` stop and a
manual fix, the next `/feat-fix` would compute `retries = 4 > 3` and re-block immediately —
the line had no supported way back on.

## New file
- **feat-unblock.md** — `/feat-unblock <slug>`: main-session, human-only resume after
  `blocked` / `blocked-classifier` (and `distilled`-after-block, because `/feat-distill`
  overwrites `step` and a guard accepting only `blocked` would lock the recommended
  distill-first order out of its own path). Shows the open findings and the retry count,
  asks how the block was handled (fixed manually / story-spec revised / accepted as risk /
  classifier route) and branches the next step on the answer, recommends distill first,
  warns on a second block for the same feature (upstream problem — revise the ⏸ gates or
  split the slug), appends an audit entry to `<slug>/unblock.md`, resets `retries` to 0 and
  sets `step` to `validate`. Findings are never edited away; the command never runs inside
  an active `/goal` loop.

## Modified
- **feat-fix.md** — both endings (retry cap, and the classifier-only `blocked-classifier`
  path) now name `/feat-unblock` as the way back, with `state.json` changed by that command
  rather than by hand.
- **feat-ship.md** — 2d names the resume path (`/goal clear` → human → unblock → fresh
  ship); a non-negotiable added: a blocked state ends the goal, and both unblocking and the
  retry budget stay with the human, outside the loop.
- **feat-status.md** — blocked states also print `retries` and the distill → human →
  unblock flow.
- **CONVENTIONS.md** — pipeline diagram gains `/feat-unblock`; the reliability bullet notes
  that re-entry is a command rather than a silent state edit; `.active` removal list
  updated; new section **Blocked handling (/feat-unblock)** covering cap semantics
  (increment-then-check: three real fixes, the fourth call stops), what happens at the cap,
  the four-step handling flow, and the hard guardrails.
- **README.md / README_zh-TW.md / install.sh / install.ps1** — pipeline lists and expected
  counts, 16 → 17.
- **factory-cheatsheet_{en,zh-TW}.md / factory-training_{en,zh-TW}.html** — command flow,
  loopnote, fix stage and stuck tables carry the resume path, including a "blocks a second
  time" row. One stale stage number missed by this session's earlier renumber
  (`回到 06 重驗` in the zh-TW file) was caught and fixed here.

## Conflict review before re-adding (this pass)
Checked against the current architecture and the `/writing-for-agents` standard before the
command went back in. Four fixes, two confirmations:

- **Confirmed — hook scope.** `scope-track.sh` exits 0 for anything under `artifactsDir`
  regardless of `.active`, so `unblock.md` and `state.json` writes are never blocked.
- **Confirmed — `step: validate` still fits.** `/feat-ship`'s precondition accepts
  `validate`, so the 2026-07-31 decision to reuse it rather than invent an `unblocked`
  state holds against today's `feat-ship.md`. Inventing a state would have required editing
  that precondition list.
- **Fixed — stale grill analogy.** The draft cited `/feat-grill` as precedent for asking
  one question at a time. Grill became round-by-round in the v1.2 sync, so the citation now
  covers only what still holds: the interview runs in the main session because a subagent
  cannot hold one. (Unblock asking a single question stays correct — one question *is* the
  whole frontier.)
- **Fixed — negation in the pointer.** The description ended "never invoked by an
  autonomous loop"; rephrased to state where it does run. Body negations: zero.
- **Fixed — duplication between steps 2 and 7.** The four handling answers and their four
  next-steps were stated twice, forcing the agent to hold a cross-reference. Merged into one
  branch table in step 2; step 7 runs the branch. With the rationale preamble pruned (it
  lives in CONVENTIONS' Blocked handling), the command went 549 → 464 words — from the
  longest command file in the repo to mid-pack.
- **Fixed — memory-distiller integration.** `unblock.md` now appears in the distiller's
  "especially" input list. It contains the human's verbatim diagnosis of why the loop
  stalled, which is the highest-value lesson in the folder, and the generic "everything
  under `<slug>/`" was leaving it to chance.

Considered and rejected: adding a phase-boundary pointer to the command. `/feat-unblock` is
a boundary, but `CLAUDE.md`'s Context Health already covers every `/feat-*` seam — repeating
it here would be a cache of that rule.

## Also: /feat-recomment discoverability
`/feat-recomment` was already documented in eight files, but was absent from the two places
people actually look for a command: the pipeline block in `CONVENTIONS.md` and the
"Run a feature" list in both READMEs — it had been kept out deliberately, since it is not a
pipeline step. It now appears in both as an explicitly labelled **Maintenance** entry
(no slug, no artifacts), and `CONVENTIONS.md` gained a short "Maintenance commands" section
pointing at the existing detail section.

---

# writing-for-agents pass — change summary (2026-08-14)

Audited every agent-read document against upstream's `/writing-for-agents` (v1.2, renamed
from `writing-great-skills`; its scope now explicitly covers `CLAUDE.md`). Six findings,
all applied. Measured effect on the always-loaded budget: `CLAUDE.md` 2639 → ~1740 words
(-34%); negations across the template 28 → single digits.

## New files (disclosed reference — pointer-reached, never `@import`ed)
- **`.claude/factory/CLAUDE-rationale.md`** — every rule's *Why* note, extracted from
  `CLAUDE.md`. Human reading only: no pointer reaches it, so it costs no context load.
  Includes the three-generation history of the Context Health section.
- **`.claude/factory/EXPLORE-MODE.md`** — the EXPLORE Mode table and exit procedure. Only
  some runs branch into exploration, so it moved behind a pointer; Rules 0/1/2/9 stay
  inline because every branch needs them.
- **`.claude/factory/PHASE-BOUNDARIES.md`** — the five-option ladder (continue → `/clear`
  → hand off → subagent → `/compact`). Reached at a boundary; the mid-phase signals stay
  inline in `CLAUDE.md` because the agent acts on them continuously.

## Modified
- **CLAUDE.factory-snippet.md** — (1) every soft prohibition rephrased as its positive
  target, per upstream's **negation** failure mode: banning a behaviour drags it into
  context and makes it more available. Rule 1 retitled "Pick a Side, Flag the Other",
  Rule 8 "Match Conventions, Surface Anti-Patterns"; Rule 9's "Do NOT use AI for" list
  became "Write plain deterministic code for" with the same items. Hard guardrails that
  cannot be phrased positively were kept and paired with a positive target. (2) All
  *Why* notes, EXPLORE Mode and the phase-boundary ladder moved to the files above.
  (3) The changelog table moved into this file. (4) Duplication with the imported
  `terminology-zh-tw.md` (comment rule, document-language policy, TW terms — three
  bullets) collapsed to one bullet naming that file as the single source of truth.
- **CONVENTIONS.md** — §Prompt style gains **Prompt the positive** (the negation lever);
  new §Disclosed reference table mapping each companion file to the branch that reaches
  it; one negation rephrased in §Scope enforcement.
- **backend-builder.md / frontend-builder.md** — the `typecheck → lint → test` prose was a
  **cache** of `quality-gate.sh` (which loops exactly those three phases) and was restated
  again by the calling command; reduced to the one command. The `Don't: touch frontend /
  backend files` bullet duplicated the positive hook-enforced scope line directly above it
  and was cut. backend-builder's closing "never report tests pass while hiding skipped
  ones" was Rule 0 stated a third time; cut.
- **story-writer.md / spec-writer.md** — "Do not write or modify any source code" is a
  no-op: neither agent has Edit or Bash in its `tools:`. Cut from both.
- **validator.md** — "(You have no Edit/Bash tools…)" was a cache of its own frontmatter;
  cut. Two negations rephrased; the smells guardrail now states what 🔴 is reserved for.
- **test-verifier.md / memory-distiller.md** — negations rephrased positively; the
  guardrail on never paraphrasing refused content kept and labelled as a hard guardrail.
- **doc-writer.md** — description trimmed (the trailing "Does not touch source, tests…"
  was negation plus identity the body already carries). Step 2's fuzzy bound "as needed"
  — an invitation to premature completion — replaced with a demand: docs continue until
  every acceptance criterion in `story.md` is reachable from one.
- **feat-grill.md** — the two remaining negations rephrased.
- **All five agents carrying it** — the `classifier-refusal` definition was duplicated
  near-verbatim (~180 words). The definition now lives once in CONVENTIONS.md's Fable 5
  addendum; agents repeat the token and the action only. (Repeating a token is what a
  leading word is for; repeating the meaning is duplication.)

## Downstream docs (same pass)
- **README.md** — `/feat-grill` line now reads "round-by-round interview"; setup step 1
  notes that the three companion files are pointer-reached, never `@import`ed; new
  section "What the agent loads, and what it reaches for" carrying the same branch table
  as CONVENTIONS.md, aimed at the human installing the template.
- **docs/README_zh-TW.md** — retranslated in full against the updated English source, per
  the document language policy. This is a wholesale replacement, not a diff.
- **install.sh / install.ps1** — the completeness check now also verifies the five
  contract files under `.claude/factory/` (the two imported plus the three pointer-reached
  ones), and the post-install summary lists them ok/MISSING. A pointer whose target did
  not ship is a silent failure: the agent simply never reaches the material, and nothing
  errors. Agent/command/hook counts are unchanged at 8 / 16 / 3.

- **docs/factory-cheatsheet_{en,zh-TW}.md** — grill line now "round-by-round interview";
  new **Contract files** paragraph under Install (which three load every turn, which three
  are pointer-reached); new stuck-table row for a bloated context pointing at the ladder;
  new non-negotiable #5 "Decide context at boundaries" (Fail-Loud → #6).
- **docs/factory-training_{en,zh-TW}.html** — **`/feat-grill` was missing from both files
  entirely**, a gap left over from the 2026-07-23 Pocock pass that the 2026-08-12 pass
  explicitly did not close. Added as station 03 (interview badge, round-by-round frontier
  description), inserted into the scrolling belt, and added to the run-a-feature terminal;
  stations 03–10 renumbered to 04–11 and the two `06→08` loop references retargeted to
  `07→09`. New Under-the-Hood row "Contract file layout" covering the two `@import`s and
  the three pointer-reached companions, with progressive disclosure as the stated reason.
  New stuck-table row and new House Rule, both mirroring the cheatsheet. Verified: 14
  stations, 6 rules, 22 table rows, balanced tags, HTMLParser-clean, EN/zh-TW at parity.

## Follow-ups (not in this pass)
- The no-op test is model-relative and settled by running the document, not by reading it.
  This pass was static analysis: watch the next few features for a rule that stopped
  binding because its prohibition was removed, and restore it as a paired guardrail.
- Cheatsheet / training HTML regeneration (already pending from the v1.2 sync) should pick
  up the new file layout.

---

# Pocock v1.2 sync — change summary (2026-08-14)

Adapted from mattpocock/skills v1.2.0 (MIT; released 2026-08-05). Four adoptions:
round-by-round grilling + phase-boundary context rules + the "cache" prompt-pruning term
+ validator smells 8 → 12. NOT adopted: plugin/Codex/docs-site packaging (distribution
channel only), `/wizard` / `/to-questionnaire` / `/wait-what` (standalone skills,
Watchlist candidates), `/prototype` branch retention (EXPLORE Mode is outside the
factory), `/wayfinder` decision tickets (stays a Watchlist item — upstream now offers a
mature model to copy when `/feat-epic` is built).

## Modified
- **feat-grill.md** — step 3 rewritten: map decisions as a design tree and ask the whole
  FRONTIER (every question whose prerequisites are settled) as one numbered round, then
  recompute; fixed `❓ Q<n> / ➡️ recommendation` shape so the user answers by number;
  codebase-answerable fact-finding dispatched to background read-only Explore subagents
  so it never blocks a round. In-session opt-out back to one-at-a-time honoured; no
  config surface added. decisions.md format, the story gate, and the MEMORY.md
  single-writer contract unchanged.
- **CLAUDE.factory-snippet.md** — Context Health replaced by "Phase Boundaries": the
  context decision moves to the seams between `/feat-*` steps and walks five options in
  order (continue → `/clear` → hand off → subagent/slices → `/compact` last). Maps the
  options onto machinery the factory already has: the artifacts dir is the standing
  handoff, the builders are the subagents, Implementation slices are the splitter. The
  four observable distress signals are kept but demoted to symptoms-to-surface — signals
  ① and ② no longer prescribe `/compact` (mid-diagnosis compaction destroys evidence).
  One human-facing note records upstream's ~150k-token smart zone as a judgement aid for
  option 1, explicitly never an AI self-check. Changelog row added.
- **CONVENTIONS.md** — §Grill step re-described (frontier rounds, background
  fact-finding); §Prompt style gains the **Cache test** (the environment is a source of
  truth; a sentence restating a cheap lookup is a stale-prone cache — keep only what the
  agent cannot find by looking); Pocock provenance note bumped to v1.2.0 / 2026-08.
- **validator.md** — smells baseline extended with Speculative Generality, Message
  Chains, Middle Man, Refused Bequest (guardrails unchanged: repo CLAUDE.md overrides;
  never 🔴 on a smell alone).

## Follow-ups (not in this pass)
- Regenerate `factory-cheatsheet_{en,zh-TW}.md` and `factory-training_{en,zh-TW}.html`:
  the grill flow description and the stuck-state table still describe one-per-turn, and
  the house rules need a phase-boundary entry.
- `README.md` / `README_zh-TW.md`: the `/feat-grill` comment line still reads
  "interactive interview" (still true); no change strictly required, but the training
  guide link text may warrant a refresh alongside the docs above.
- Watchlist (`/feat-epic`): when built, copy upstream's decision-ticket + parallel
  research burn-down model from `/wayfinder` v1.2.

---

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
- ~~Regenerate `factory-cheatsheet_{en,zh-TW}.md` and `factory-training_{en,zh-TW}.html`~~
  — done in the 2026-08-14 passes (grill station added, counts corrected to 17).
- ~~Optional maintenance pass: prune all 8 agents per the new Prompt style rules~~ — done
  in the 2026-08-14 writing-for-agents pass; the commands were pruned selectively, not all.
- Watchlist: /wayfinder-style epic planning layer (`/feat-epic`); periodic deep-module
  sweep as an explore-mode tool.


---

# CLAUDE.md changelog (moved here 2026-08-14 from the contract itself)

| Date | Author | Change |
|------|--------|--------|
| 2026-05-20 | Robert | Initial version: 12-rule framework with EXPLORE Mode layering |
| 2026-06-05 | Robert | Merged Feature Factory pipeline (@import CONVENTIONS + project-specific block) |
| 2026-06-08 | Robert | Added bilingual-comment / doc-language policy, TW terminology import, and the `/feat-docs` user-documentation step |
| 2026-07-08 | (fill in) | Fable 5 upgrade: agent model routing, classifier-refusal handling (`blocked-classifier`), memory layer (`/feat-distill` + MEMORY.md), convergence loop (`/feat-ship` + `/goal`). Marked FABLE5 throughout; inert on other models. Closing order: validate → docs → distill. |
| 2026-08-12 | (fill in) | Bilingual comments switched from line-interleaved to block-after-block; `/feat-recomment` + `comment-migrate.py` added |
| 2026-08-14 | (fill in) | Pocock v1.2 sync: grill round-by-round (frontier), Context Health rewritten as phase-boundary decision list, prompt-style "cache" term, validator smells 8 → 12 |
| 2026-08-14 | (fill in) | writing-for-agents pass: prohibitions rephrased positively, rationale/EXPLORE Mode/phase-boundary ladder disclosed to companion files, changelog moved here |
