# /feat-epic: delegate, and human-ruled scope drops (2026-09-20)

Follow-up to `/feat-epic`. Two gaps found while walking the WORK loop: a ticket that turns
out to move only one feature had no exit except being answered in the epic or squeezed into
Out of scope, and both scope drops were decided by the agent alone, at the point in the run
where the pull to finish is strongest (upstream's premature completion). CHART is unchanged.

- **Third way to close a ticket: `delegated`.** The question moves one feature only, so
  that feature's `/feat-grill` settles it. Its Decisions-so-far line reads
  `delegated to <feature-slug> — <the open question>`, and step 6 carries it into the
  Feature breakdown as `open: <ticket titles>` beside that feature's `/feat-new` line. A
  question that shapes the split, or that several features depend on, stays with the epic.
- **The human rules on every scope drop.** Out of scope and delegated are now raised in the
  same grilling round as the ticket being resolved (`❓` + `➡️`, no extra round), and step 5
  acts on the answer. The Destination's own Out of scope, agreed while charting, is already
  the human's.
- **Closing report** names every ticket closed without being answered, with its new owner,
  so a drop cannot pass silently.
- Clearing the map is unchanged: no open ticket, no fog. Delegating closes a ticket, so no
  condition had to be relaxed.

## Modified
- **feat-epic.md** — ticket `Status` gains `delegated`; new "Three ways a ticket closes"
  paragraph; WORK steps 3, 5, 6 and the closing report. 1,007 → ~1,140 words.

## writing-for-agents check on the change
- **Step ordering fixed.** Step 4 set `closed` on the ticket in hand before step 5 could
  apply a ruling to it, so dropping the ticket you just resolved contradicted itself. Step 3
  now says the ticket in hand may itself be dropped, and step 4 covers answered tickets.
- **Co-location.** `Decisions so far` was defined as "one line per closed ticket", which
  invited out-of-scope tickets in and needed a "never in Decisions so far" ban in step 5.
  The definition now reads "answered or delegated", and the ban is gone — a boundary stated
  once where the concept is defined, not repeated as a prohibition at the point of use.
- **No-ops cut.** "No separate round" restated "in the same round"; "which step 6 carries
  into the breakdown" restated step 6's own instruction.

---

# writing-for-agents pass 2 — always-loaded layer (2026-09-20)

Second audit against upstream `writing-for-agents` (read on main, 2026-09-20). The finding
that drove it: Claude Code loads `CLAUDE.md` **and its `@import`s into every custom
subagent** (only built-in Explore and Plan skip them), so the always-loaded layer is paid
once per turn in the main session and again on every factory agent run. `CONVENTIONS.md`
had grown into a design document — mostly procedures already owned by command files,
caches of the environment, and history. Measured (HTML comments excluded, as they are
stripped before loading): always-loaded words **5,217 → 2,644 (-49%)**; `CONVENTIONS.md`
2,810 → ~530; snippet 1,619 → 1,391; agent descriptions 238 → 181; command descriptions
382 → 313 (descriptions are always-loaded pointers too).

## Decisions (grilled with the maintainer)
- **`CONVENTIONS.md` stays the imported file, shrunk to the core** — existing repos keep
  their `@import` line; reinstalling upgrades them. Design narrative moved to
  `CLAUDE-rationale.md` (human-only, never loaded).
- **Duplicated procedure is deleted, not moved** — the command/agent file is the single
  source of truth; README, cheatsheets and training carry the human overview.
- **Prompt style disclosed** to `WRITING-FOR-AGENTS.md`, reached by one pointer, and
  re-synced to upstream's current reference.
- **Snippet block 2/2 deleted**; its unique rules folded into the core.
- **Scope includes commands and agents**, at least everything added since the
  2026-08-14 pass (`/feat-recomment`, `/feat-unblock`, `/feat-sweep`, `/feat-epic`) plus
  lines the core change touched.
- **Verification by traceability** (table below) plus a live `/context` check by the
  maintainer.

## New file
- **`.claude/factory/WRITING-FOR-AGENTS.md`** — disclosed reference: the two loads (with
  the per-subagent multiplier), context pointers, information hierarchy and the branching
  test, co-location, sprawl, completion criteria (clarity + demand, premature completion),
  leading words and the positive prompt, and pruning (single source of truth per context,
  cache test, relevance/sediment, no-ops). Contract files 5 → 6.

## Modified
- **CONVENTIONS.md** — rewritten as the core: Pipeline (manifest + diagram), Invariants,
  Evidence & redaction, Classifier refusals (the definition the agents point at), and the
  pointer to `WRITING-FOR-AGENTS.md`. Human notes sit in an HTML comment. Supersedes the
  §Epic planning section added earlier today.
- **CLAUDE-rationale.md** — new "Factory mechanisms" part: why commands + hooks, blocked
  handling, the Fable 5 addendum (routing, refusals, memory layer, convergence loop,
  references), maintenance commands, Pocock provenance.
- **CLAUDE.factory-snippet.md** — block 2/2 removed; merge is now the two `@import` lines;
  header comment lists the fourth companion file and the upgrade step.
- **Agents** — backend/frontend-builder: restated Rules 5/7/9 removed (CLAUDE.md reaches
  them), slice rule and hook line phrased positively, a no-op parenthetical cut.
  test-verifier: description negation cut, redaction restatement → pointer. validator:
  description negation + rationale cut, ⛔ line phrased positively. memory-distiller:
  description trimmed, "never modify" → "you write one file". doc-writer: scope stated
  three times → once, positively; doc-language line (a cache of terminology §2) cut.
  spec-writer: restated Rule 1 cut. Classifier pointers retargeted to the new section.
- **Commands** — feat-recomment: identity trimmed, a duplicate approval ban cut, the
  word-for-word guardrail labelled and paired. feat-unblock: dead pointer to §Blocked
  handling removed. feat-sweep, feat-ship, feat-distill, feat-init: descriptions pruned.
  feat-docs: doc-writer's procedure and the scope-token cache removed (the agent owns
  both); completion criterion added. feat-fix: redaction and refusal restatements →
  pointers. feat-grill: MEMORY single-writer restatement cut. feat-epic: provenance moved
  to rationale; state paragraph tightened.
- **install.sh / install.ps1** — contract list gains `WRITING-FOR-AGENTS.md`; merge
  message now says "add the two @import lines" plus the upgrade step.
- **README.md / docs/README_zh-TW.md, cheatsheets, training HTML (EN/zh-TW)** — merge
  instructions, the loads table (four companions), the per-subagent reload, and pointers
  from "full design in CONVENTIONS.md" to `CLAUDE-rationale.md`.

- **Dangling `CHANGES.md` references fixed** — `CHANGES.md` stays at this repo's root, but
  the installer ships only `.claude/` and the snippet, so a bare "`CHANGES.md`" in an
  installed file pointed at nothing in a target repo (or at that repo's own changelog).
  The snippet's footer (always loaded, since 2026-08-14), the CONVENTIONS header comment,
  and WRITING-FOR-AGENTS' Relevance rule now name the factory template repo's `CHANGES.md`
  explicitly; the Relevance rule also routes a target repo's own adjustments to that
  repo's changelog or commit message.

## Traceability — every removed CONVENTIONS.md line and where it lives now
| Removed section | Single source of truth now |
|---|---|
| Tracks & the manifest | core §Pipeline (condensed) |
| The pipeline (per-step detail) | core diagram + each command file |
| What makes this reliable | CLAUDE-rationale.md; order/Rule 9 line kept in core |
| Grill step | feat-grill.md |
| Epic planning | feat-epic.md; slug namespace kept in core §Invariants |
| Blocked handling | feat-fix.md steps 1–2, feat-unblock.md, feat-status.md; why → rationale |
| Maintenance commands | feat-sweep.md, feat-recomment.md; core diagram line |
| Prompt style | WRITING-FOR-AGENTS.md (superset) |
| Scope enforcement | core §Invariants; token list = scope-track.sh; each command removes `.active` itself |
| User-facing documentation | feat-docs.md + doc-writer.md; terminology-zh-tw.md §2 |
| Legacy comment migration | feat-recomment.md + comment-migrate.py; `--check` rationale → rationale |
| Disclosed reference table | snippet pointers (EXPLORE, PHASE-BOUNDARIES); core pointer (WRITING-FOR-AGENTS) |
| Mode contract | core §Invariants |
| Honesty | CLAUDE.md Rule 0 + each agent's closing line |
| Fable 5: model routing | agent frontmatter `model:` + its comment; why → rationale |
| Fable 5: classifier refusals | core §Classifier refusals, feat-fix.md step 0, validator.md |
| Fable 5: memory layer | feat-distill.md, memory-distiller.md, feat-research.md, MEMORY.md header |
| Fable 5: convergence loop | feat-ship.md; design constraints → rationale |
| References, Pocock provenance | CLAUDE-rationale.md |
| Snippet block 2/2 | core §Pipeline/§Invariants; Fail-Loud = Rule 0; comment rule = terminology-zh-tw.md |
| Builders' Rules 5/7/9, spec-writer's Rule 1 | CLAUDE.md (loaded into every factory agent) |

## Upgrade note
The `/feat-epic` delivery zip placed `README_zh-TW.md` at the repo root by mistake; its home
is `docs/README_zh-TW.md` (the language links in both READMEs point there). If a root copy
exists, delete it — `docs/README_zh-TW.md` in this change carries both updates.
Reinstall. In an existing `CLAUDE.md`, delete the old "### Feature Factory" block under
Project-Specific Rules; keeping it is harmless duplication, not an error.

## Follow-ups
- Run `/context` before and after in a real repo and compare Memory files; then ship one
  small feature to confirm no rule stopped binding (the no-op test is model-relative).
- ❓ Open: mark all 19 commands `disable-model-invocation: true` (they are user-invoked by
  design). Upside: the model can never self-start a pipeline step, and descriptions may
  leave the context. Not applied — reports disagree on whether descriptions actually
  leave the context, and one open bug has the model refusing a user-typed command.

---

# /feat-epic: epic planning layer (2026-09-20)

Resolves the last Watchlist item, the `/wayfinder`-style epic planning layer (parked
2026-07-23). An optional command ABOVE `/feat-new`, for an effort bigger than one feature
whose route is still foggy. Adapted from mattpocock/skills `/wayfinder` (MIT; read on
upstream main, 2026-09-20). Kept: name the Destination first, the map as an index (a
decision lives only in its ticket), decision tickets (plan, don't do), the blocking
frontier, fog of war (Not yet specified), Out of scope, one ticket per session with
research tickets burned down in parallel. NOT taken: the issue tracker, ticket claims,
and the `task` type.

## Decisions (grilled with the maintainer)
- **One command, two modes.** `/feat-epic <epic> "<desc>"` charts; `/feat-epic <epic>
  [ticket]` works the next frontier ticket. Mode is chosen by whether the map exists.
- **Local markdown, no state machinery.** `<artifactsDir>/epics/<epic>/map.md` +
  `tickets/NN-<name>.md`, blocking by a `Blocked by:` line. No `state.json` (the map is
  the state; `state.json` stays per feature), `.active` untouched — artifacts are always
  writable, so it runs safely mid-feature. A tracker would need `gh`, auth, and writes the
  hooks cannot see.
- **Three ticket types.** research (AFK: background Explore, parallel; the main session
  does web lookups when Explore is denied them), grilling (HITL: `/feat-grill`'s round
  shape), prototype (HITL: text inline, code via EXPLORE Mode under `prototype/`, linked).
  `task` dropped — human-only steps are rare here (see the 2026-09-19 triage); they become
  a Notes ❓ item plus `Blocked by: human — …`. Claims dropped: single driver.
- **One HITL ticket per run**; the seam between tickets is a phase boundary.
- **Reference, not inherit or re-grill.** Features carry `[epic: <epic>]` in `idea.md`;
  `/feat-research` copies the epic decisions a feature relies on into `research.md` →
  Epic context, and `/feat-grill` treats them as settled (re-open only with new evidence).
- **Hand-off by paste-ready lines.** A cleared map ends in a Feature breakdown of
  `/feat-new <slug> … [epic: <epic>]` lines in build order (`after:` for dependencies,
  advisory). The command creates no feature folder; no fog at chart time means no map.
- **No MEMORY.md path.** Epic decisions are plans, and MEMORY.md takes only verified
  entries. They reach it the normal way: the child feature's `research.md` carries them,
  and `/feat-distill` banks what shipping confirmed. Single-writer contract unchanged;
  `memory-distiller.md` unchanged (it already reads `research.md`).
- **`/feat-status` shows epics** (status, Destination, decision count, frontier/blocked
  tickets, fog, and each child feature's step once cleared); a child feature shows
  `Epic: <epic>`.
- **One slug namespace.** `/feat-new` and `/feat-epic` each refuse a slug the other uses,
  and `epics` is reserved. `/feat-epic` ends every run by reminding the user of this.

## New file
- **feat-epic.md** — `/feat-epic`. Uses the built-in Explore subagent; no new agent
  (agent count stays 8). Command count 18 → 19.

## Modified
- **feat-new.md** — slug GUARD (shared namespace, `epics` reserved).
- **feat-research.md** — step 2: `[epic: <e>]` → Epic context section, settled decisions.
- **feat-grill.md** — step 3: Epic context decisions are settled.
- **feat-status.md** — epic view; child feature prints its epic.
- **CONVENTIONS.md** — pipeline diagram gains `/feat-epic`; new §Epic planning;
  provenance note records what was kept and dropped from `/wayfinder`.
- **install.sh / install.ps1** — expected commands 18 → 19.
- **README.md / docs/README_zh-TW.md** — count 18 → 19; `/feat-epic` atop the Run-a-feature
  block; `/feat-status` note.
- **factory-cheatsheet_{en,zh-TW}.md** — new "Plan an epic" section; `/feat-status` note.
- **factory-training_{en,zh-TW}.html** — spec box commands 18 → 19; "Plan an epic" terminal
  block before the standard path. Stations, house rules, and table rows unchanged.
- **CHANGES.md** — `/feat-epic` Watchlist lines struck in the 2026-08-14 and 2026-07-23
  entries; the Watchlist is empty.

## Unchanged, checked
`memory-distiller.md`, `feat-story.md`, `PHASE-BOUNDARIES.md` (its ladder already covers
any `/feat-*` seam), `CLAUDE.factory-snippet.md`, `scope-track.sh`.

---

# /feat-sweep: periodic deep-module sweep (2026-09-19)

Resolves the Watchlist item "periodic deep-module sweep" (2026-07-23). New maintenance
command, outside the per-feature pipeline. Shape adapted from mattpocock/skills
`improve-codebase-architecture` (MIT; read at v1.2.3): scope before scanning, weight
recently changed code, deletion test as the filter, three strength tiers, never edits
code. NOT taken from upstream: the HTML report, `CONTEXT.md` / ADR updates, and the
post-pick grilling (`/feat-grill` already owns that once a candidate enters the line).

## Decisions (grilled with the maintainer)
- **A maintenance command, not an EXPLORE-MODE section.** The Watchlist called it an
  "explore-mode tool", but `EXPLORE-MODE.md` is a rule-relaxation table for prototype
  work; a read-only sweep relaxes no rule. `/feat-recomment` is the precedent.
- **Named `/feat-sweep [path]`** — every command carries the `feat-` prefix.
- **One report, overwritten**: `<artifactsDir>/sweep-report.md`, version-controlled, so
  git history is the trend. Each candidate ends in a paste-ready `/feat-new` line; the
  command never creates a feature folder.
- **Shallow modules only.** The 12-smell baseline stays with the validator on per-feature
  diffs; repo-wide it would bury the candidates in ⚪ noise. Cap: 7 candidates, tiers
  Strong / Worth exploring / Speculative, plus a Top recommendation.
- **No reminder mechanism.** Cadence is the human's. A nudge from `/feat-distill` would
  couple an outside-the-line tool into the pipeline.

## New file
- **feat-sweep.md** — `/feat-sweep [path]`. Uses the built-in read-only Explore subagent
  (no new agent; agent count stays 8). Reads root `CLAUDE.md` (documented conventions
  override), MEMORY.md (`[durable]` decisions are not re-litigated), and the previous
  report (candidates marked `new` / `repeat`). Leaves `.active`, `state.json`, and
  MEMORY.md alone, so it needs no GUARD and may run mid-feature. Command count 17 → 18.

## Modified
- **CONVENTIONS.md** — §Maintenance commands describes `/feat-sweep`; the group is now
  "no slug, no `state.json`" (both maintenance commands do write a report file).
- **install.sh / install.ps1** — expected commands 17 → 18.
- **README.md / README_zh-TW.md** — count 17 → 18; `/feat-sweep` in the Maintenance list.
- **factory-cheatsheet_{en,zh-TW}.md** — `/feat-sweep` in the Maintenance block plus one
  paragraph (read-only, report shape, suggested cadence); the existing paragraph is now
  labelled as `/feat-recomment`'s, since the block lists two commands.
- **factory-training_{en,zh-TW}.html** — spec box commands 17 → 18; `/feat-sweep` added
  to the Maintenance terminal block. Stations, house rules, and table rows unchanged.
- **CHANGES.md** — the 2026-07-23 Watchlist line struck through for the sweep half
  (`/feat-epic` remains open).

---

# Upstream standalone skills triage: change summary (2026-09-19)

Closes the "Watchlist candidates" left open by the 2026-08-14 v1.2 sync. Each skill was
read at mattpocock/skills v1.2.3 (latest; released 2026-08-06). All three are declined.
A decline is a non-item, not a deferral: none of these stays on the Watchlist. No template
file changes other than this one.

## Declined
- **`/wait-what`**: re-pitches a message that did not land, in ASD-STE100 Simplified
  Technical English with the vocabulary from `CONTEXT.md`. The factory declined
  `CONTEXT.md` on 2026-07-23 (the glossary lives per feature in `decisions.md`), so half
  the skill has nothing to read. It repairs one chat message and touches no step, gate, or
  artifact. ASD-STE100 is an English register; it does nothing for zh-TW conversations.
- **`/to-questionnaire`**: turns a decision the user cannot answer alone into a Markdown
  questionnaire for the one person who can. Its only contact point is `/feat-grill`, which
  has no exit for a decision only a third party can settle. The maintainer confirmed that
  case does not come up: the person running the grill is the decision-maker. No gap, so
  nothing to adopt. If that changes, the fix is a "parked decision" outcome in
  `/feat-grill` and the `/feat-story` guard, not this skill.
- **`/wizard`**: generates an interactive bash script that walks a human through steps only
  they can perform and writes captured values to `.env` files and GitHub Actions secrets.
  Human-only setup steps are rare in the repos using this template, and the builders'
  ❓ Needs-human-input section covers them. Vendoring would also mean carrying upstream's
  fixed `template.sh` library through every sync (v1.2.3 already changed it) and adding a
  model-invoked skill to a template whose agents are name-invoked by design. A repo that
  needs it can install the upstream skill directly; it runs outside the factory line.

## Modified
- **CHANGES.md**: "Watchlist candidates" in the 2026-08-14 entry struck through with a
  pointer to this entry.

---

# Pocock v1.2.3 sync — evidence redaction (2026-09-18)

Adapted from mattpocock/skills v1.2.3 (MIT), PR #779 "Make `diagnosing-bugs` redact
secrets". One adoption: redaction as the first move on pasted evidence. Upstream applies it
to a diagnosis loop; the transferable part is the ordering, which our Rule 7 evidence
requirement makes load-bearing the same way.

**The gap it closes.** Rule 7 mandates pasted evidence, and that evidence lands in
version-controlled artifacts (`verification.md`, `validation.md`, `decisions.md`,
`MEMORY.md`). The only existing defence, `protect-secrets.sh`, matches secret FILES by name
(`.env*`, `*.key|pem|p12|pfx`, `secrets.*`) and `git add|commit` command strings — it never
inspects content. A token echoed by a failing test or an `Authorization:` header in a
reproduction line was written and committed with nothing firing.

NOT adopted from the same release: PR #781 (dropping Claude Code tool and agent-type names
from subagent dispatch, for Codex portability) — this template is Claude Code only by
design, and cross-harness support is out of scope, not a deferred item; PR #783 (`wizard`
time-estimate removal, skill never adopted); v1.2.2 (`writing-for-agents` Codex metadata —
we borrowed its prose rules, not its packaging). Upstream published no 1.2.1 changelog
section.

## Modified — contract
- **CONVENTIONS.md** — new **Evidence & redaction** section after §Honesty, the single
  source of truth: credential values enter as `<REDACTED>`; reproduction commands reference
  the credential through its environment variable; a captured run is quoted at its
  signal-carrying lines. States plainly that `protect-secrets.sh` covers secret files by
  name and artifact CONTENT is this rule's job, and names Rule 7 as what it serves (the
  house-rule number is deliberately not cross-referenced — it would go stale). Pocock
  provenance note bumped to v1.2.3 / 2026-09 with the non-adoptions recorded.
- **test-verifier.md** — completion criterion for a criterion is now its REDACTED evidence
  in `verification.md`; points at CONVENTIONS.md rather than restating the rationale.
- **feat-fix.md** — step 3 gains a per-track reporting bullet: a fix counts as done when its
  redacted gate/test evidence is shown.
- **validator.md** — Security check extended to the artifacts themselves; a live credential
  in one is a finding graded by impact. Guardrails unchanged (🔴 stays reserved for security
  and failing criteria, so an exposed credential can still reach 🔴 on its own merits).

## Modified — human-facing docs
- **factory-cheatsheet_{en,zh-TW}.md** — new non-negotiable #6 "Redact before you paste";
  Fail-Loud renumbered #6 → #7, keeping it last as in the 2026-08-12 and 2026-08-14 passes.
  Rules #1–#5 unchanged.
- **factory-training_{en,zh-TW}.html** — matching House Rule card inserted before
  "No workarounds, no varnish"; footer edition date 2026-08 → 2026-09. Pipeline belt, stage
  diagram and Under-the-Hood table untouched: this is a contract rule, not a pipeline step.
  Verified: 14 stations, 7 rules, 22 table rows, balanced tags, HTMLParser-clean, EN/zh-TW
  at parity.

## Deliberately not done
- **No CI gate.** No content scan in `quality-gate.sh`, on the same reasoning as
  `comment-migrate.py --check`: a high-false-positive check that can leave a repo
  permanently red does not belong in the build.
- **`protect-secrets.sh` untouched.** Its filename/command contract is a different defence;
  the two are complementary and neither subsumes the other.
- Agent/command/hook counts, the `.active` scope mechanism, and the MEMORY.md single-writer
  contract are unchanged, so `install.sh` / `install.ps1` need no edit.

## Follow-ups (not in this pass)
- The rule is enforced by reading, not by tooling. Watch the next few features for evidence
  that landed unredacted; if it recurs, the cheap next step is a PostToolUse hook that warns
  (never blocks) on high-entropy strings written into `artifactsDir`, not a gate.
- `README.md` / `README_zh-TW.md` were not touched: they summarise commands and counts, and
  neither changed. Revisit only if the redaction rule gets a line in the setup steps.

---

# comment-migrate.py — correctness fixes (2026-09-16)

Field report from `/feat-recomment --apply` on a Python repo: all 9 changed blocks were
wrong. Code lines moved, two asserts swapped, docstrings split mid-sentence. **If you applied
the 2026-08-12 script, revert that commit** (or `git checkout -- .` if uncommitted) and
re-run with this version.

## Root causes
1. **Closing `"""` read as an opener.** The docstring detector matched any line that was
   only `"""`. After a docstring opening with text (`"""Summary.`), its closing quotes were
   taken as a new opener, so every code line up to the next bare `"""` became "docstring
   body" and was reordered. This caused the displaced comments and the swapped asserts
   (a Chinese string literal counted as a Chinese line).
2. **Full-width punctuation not counted as Chinese.** `（COLUMN_NAME | …）。` has no CJK
   ideograph, so it was classified English and pulled away from its own sentence.
3. **Line-by-line judgement.** Classification ignored the previous line, so a wrapped
   sentence could be split across the two blocks.

## Fixed (comment-migrate.py)
- Python is scanned with `tokenize` + `ast`: only lines whose sole token is a comment, and
  only real module/class/function docstrings, are candidates. String literals, SQL or test
  data in triple-quoted strings, and trailing comments after code are never touched.
- A comment run ends at the first line that is not a pure comment line (all languages).
- CJK detection now includes CJK punctuation, Bopomofo and full-width forms.
- Continuation-aware classification: a no-CJK line after an unfinished Chinese sentence
  stays Chinese when it holds only code / identifiers / symbols; if it holds any English
  word it is flagged as ambiguous instead of guessed.
- New review flags: multi-line English followed by Chinese with no separator; text on a
  docstring's quote line that regrouping would move; ambiguous language split.
- Pre-write safety net: each rewritten file is compared with the original (Python: full
  token stream plus comment/docstring line multisets; others: non-comment lines in order
  plus comment line multiset). On any mismatch the file is not written and is flagged.
- `assert` and doctest prompts (`>>>`) count as commented-out code.
- JSDoc blocks are handled only when `*/` stands alone on its line.
- Writes preserve the file's own line endings.

Verified on reproductions of all four reported failures, edge cases (quote-line docstrings,
CRLF JSDoc, trailing comments, `--check` exit code, forced safety-net failure), and a stress
run on 574 CPython stdlib files with injected interleaved Chinese: 356 files / 3,643 blocks
rewritten, 0 AST changes, 0 non-comment line changes, second run changes nothing.

## Modified
- **feat-recomment.md** — step 3 adds a whole-diff check that only comment lines changed;
  step 4 lists every review reason and the wrapped-sentence rule.
- **CONVENTIONS.md** — "Legacy comment migration" describes the new guarantees.
- **README.md / README_zh-TW.md** — one sentence on the no-code-change guarantee.
- **factory-cheatsheet_{en,zh-TW}.md** — refusal list updated; no-code-change guarantee added.

---

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
~~Watchlist candidates~~ all declined 2026-09-19, PR #__), `/prototype` branch
retention (EXPLORE Mode is outside the
factory), ~~`/wayfinder` decision tickets (stays a Watchlist item — upstream now offers a
mature model to copy when `/feat-epic` is built)~~ — built 2026-09-20 as `/feat-epic` (PR #__).

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
- ~~Watchlist (`/feat-epic`): when built, copy upstream's decision-ticket + parallel
  research burn-down model from `/wayfinder` v1.2.~~ — shipped 2026-09-20 (PR #__).

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
- ~~Watchlist: /wayfinder-style epic planning layer (`/feat-epic`)~~ — shipped 2026-09-20
  (PR #__); ~~periodic deep-module sweep as an explore-mode tool~~ — shipped 2026-09-19 as
  `/feat-sweep` (PR #__). The Watchlist is now empty.


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
| 2026-09-16 | (fill in) | `comment-migrate.py` correctness fixes: tokenize/ast Python scanning, continuation-aware classification, pre-write safety check |
