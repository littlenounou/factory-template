<!-- Feature Factory — Conventions (cross-repo, do not edit per project). Loaded every
     turn by the main session and by every factory agent: it carries only what crosses
     commands. Each command and agent file owns its own procedure. Why each mechanism
     exists: CLAUDE-rationale.md; history: the factory template repo's CHANGES.md
     (not installed into this repo). -->
# Feature Factory — Conventions

## Pipeline
`.claude/factory/project.json` (written once by `/feat-init`) is the single source of
truth for tracks (`backend` / `frontend`: `dirs`, `commands`, `protectedDirs`, `enabled`),
`artifactsDir`, and `docsDir`. Every command, agent and hook reads it; a disabled track's
steps are skipped.
```
/feat-epic      <epic> "<desc>"   -> epics/<epic>/map.md    (optional, above the line)
/feat-new       <slug> "<desc>"   -> idea.md + state.json
/feat-research  <slug>            -> research.md
/feat-grill     <slug>            -> decisions.md   ⏸ interview
/feat-story     <slug>            -> story.md       ⏸ human approves
/feat-spec      <slug>            -> brief.md       ⏸ human approves
/feat-backend   <slug>            -> code + backend-summary.md
/feat-frontend  <slug>            -> UI
/feat-verify    <slug>            -> verification.md
/feat-validate  <slug>            -> validation.md
/feat-fix       <slug>            -> bounded fix loop (loopMaxRetries)
/feat-ship      <slug>            -> verify→validate→fix under one /goal (optional)
/feat-unblock   <slug>            -> human-authorized resume after `blocked`
/feat-docs      <slug>            -> README + guides (EN, then zh-TW)
/feat-distill   <slug>            -> MEMORY.md      [closing step]
/feat-status    <slug>            -> where a feature, or an epic, stands
/feat-recomment [path]  /feat-sweep [path]          (maintenance: no slug, no state.json)
```
The human drives the order, one `/feat-*` per step; order, branching and the fix loop live
in commands and hooks (Rule 9). Each step writes under `<artifactsDir>/<slug>/` and the
next step reads it: files on disk are the only hand-off between contexts.

## Invariants
- Running a `/feat-*` command is Default Mode. Exploratory work takes the EXPLORE Mode
  path instead of the line.
- `state.json` changes only through commands; `retries` resets only through `/feat-unblock`.
- Scope is hook-enforced: the running step writes `<track> <slug>` to
  `.claude/factory/.active`, and `scope-track.sh` confines writes to that track (the
  artifacts dir stays writable). A blocked write is the hook doing its job — report it and
  stay in the track (Rule 5). With no `.active`, editing is unrestricted;
  `rm .claude/factory/.active` means leaving factory mode.
- Hooks stay on: `disableAllHooks` turns off scope enforcement and `/goal` alike. Hooks
  need `jq`; without it they fail safe (allow) and say so.
- `<artifactsDir>/MEMORY.md` has one writer, `/feat-distill`. Every other step reads it as
  leads to verify.
- Epics and features share one slug namespace; `epics` is reserved.

## Evidence & redaction
A step proves itself with real output pasted into its artifact — Rule 7 is met by
evidence, not narration. Artifacts are version-controlled, so redaction comes first:
- Credential values enter as `<REDACTED>` — tokens, keys, connection strings, cookies,
  signed URLs — in `verification.md`, `validation.md`, `decisions.md`, and `MEMORY.md`.
- Reproduction commands reference a credential through its environment variable
  (`curl -H "Authorization: Bearer $API_TOKEN" …`).
- A captured run is quoted at its signal-carrying lines — the failing assertion, the
  error, the differing field — in place of the whole dump.
`protect-secrets.sh` guards secret FILES by name; artifact CONTENT is this rule's job.

## Classifier refusals
On Fable 5 a safety classifier can decline a request (`stop_reason: "refusal"`). A refusal
is not a defect:
- Record it as `classifier-refusal: <what>` in ⚠️ and continue with the rest of the work.
  Hard guardrail: the refused content is never rephrased, retried by rewording, or
  paraphrased into an artifact.
- The validator lists refusals under a separate ⛔ heading, owner: human.
- `/feat-fix` sets a refusal-only feature to `blocked-classifier` without consuming
  `retries`.

## Disclosed reference
Before editing `CLAUDE.md` or anything under `.claude/`, read
`.claude/factory/WRITING-FOR-AGENTS.md`.
