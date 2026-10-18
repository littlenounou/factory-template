---
description: "Maintenance: read-only retrospective on a session's transcript; writes retro-report.md with ranked improvements to the agent's environment."
argument-hint: "[session-id | slug] (default: the most recent session in this repo)"
---
Run a retrospective on the agent's **environment**: the steering files, pointers, tooling
and checks a session worked inside, as opposed to the code it wrote. Target: `$1`.

This is a MAINTENANCE command, not a pipeline step: it has no slug of its own and no
`state.json`. It reads transcripts and repo files and writes one file:
`<artifactsDir>/retro-report.md`. `.active`, `state.json`, and `MEMORY.md` stay exactly as
they are, and every change it proposes is applied by the human. Mistakes in the code
itself belong to `/feat-distill`, which turns them into lessons and proposed checks.

1. SOURCE: resolve which transcripts to read. Claude Code keeps each session as a JSONL
   transcript under `~/.claude/projects/`, in the folder named after this repo's path;
   subagent runs are stored beside their session.
   - No `$1`: the newest transcript other than this one. If this session itself ran
     `/feat-*` steps, read this session instead.
   - A session id: that transcript.
   - A slug: the transcripts that ran a `/feat-*` step on that slug, newest first, at most 3.
   If no transcript is found, STOP and say where you looked: a retro without its primary
   source would be guesswork.

2. CONTEXT: read root `CLAUDE.md` and its `@import`s, `.claude/factory/project.json`,
   `<artifactsDir>/MEMORY.md` (if present), the previous `<artifactsDir>/retro-report.md`
   (if present), and the repo's guardrail wiring: `.github/workflows/`, any pre-commit
   config, and the `lint` / `test` scripts the manifest's commands call.

3. SCAN: use the built-in **Explore** subagent to read the transcripts and return evidence
   per category below: tool calls tallied by name, the largest tool results, repeated
   searches, and the signal-carrying lines. Transcripts hold raw tool output, so Evidence
   & redaction (CONVENTIONS.md) applies to everything it returns.
   - **Navigation**: a file or fact the agent searched for repeatedly before finding it.
     Finding: the path and the search count; the fix is a navigation pointer.
   - **Tool economy**: a call whose output was far larger than the agent used (a full test
     log, a whole-file read for one symbol, a repeated identical command). Finding: the
     call, its rough size, and the cheaper form.
   - **No-ops**: a line in an always-loaded steering file (`CLAUDE.md`, its imports, an
     agent or command file this session used) that restates default behaviour or never
     bore on any step. Finding: the line and why it changed nothing; the test is the
     No-ops rule in `WRITING-FOR-AGENTS.md`. One session is weak evidence, so a no-op seen
     once is `Low`.
   - **Information access**: a fact the agent needed and could not reach (dev server logs,
     a third-party service's state, generated files outside the repo). Finding: what was
     missing and the read-only route that would supply it.
   - **Guardrail wiring**: a `project.json` lint or test command that is configured but
     failed to run in this session's `quality-gate.sh` output (command not found, missing
     config), or that no CI job or pre-commit hook runs. A blank command is already
     `/feat-distill`'s `no guardrail` entry; leave it there.
   A mistake in the code itself is not a candidate: name the slug in one line and point to
   `/feat-distill <slug>`.

4. REPORT: overwrite `<artifactsDir>/retro-report.md` (English). Header: date, the
   transcripts read (session ids), `git rev-parse --short HEAD`. Then at most 7
   candidates, most severe first, each with:
   - **Title**, category, and severity: `High` (cost recurs every session or every
     feature) / `Medium` (recurs in some runs) / `Low` (seen once, or small).
   - `new` or `repeat` (it appeared in the previous report).
   - **Evidence**: transcript steps and the observed cost, redacted.
   - **Change**: the target file and how it loads (always-loaded, reached by pointer, or
     config), plus the proposed line or setting. For `CLAUDE.md` and its imports, prefer
     one pointer line to inlined material; any edit under `.claude/` follows
     `WRITING-FOR-AGENTS.md`. A change that needs code becomes a paste-ready
     `/feat-new <slug> <one-line description>`.
   - **Effect**: what the next session does differently.
   Close with **Top recommendation**: the one candidate to apply first, and why. When the
   transcripts show nothing worth changing, say so explicitly: a clean retro is a valid
   result, and a padded report costs the reader more than an empty one.

5. Tell the user to review the report, apply the candidates they choose themselves
   (editing `CLAUDE-rationale.md` in the same commit when a rule changes), and commit
   `retro-report.md` so its git history shows the trend. What to apply, and when to run
   the next retro, are theirs to decide.

End with the Fail-Loud block: ✅ Verified (transcripts read, categories scanned, candidates
kept) / ⚠️ Skipped-Uncertain (transcripts or categories you could not read or judge) /
❓ Needs-human-input.
