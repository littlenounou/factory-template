# Feature Factory — Conventions (cross-repo, do not edit per project)

A reliable, manifest-driven development pipeline for Claude Code. The sequence is driven
by explicit slash commands (you run one per step), scope/quality rules are enforced by
hooks, and the fix loop is bounded. Nothing relies on a single prompt "running on its own".

## Tracks & the manifest
Each repo has `.claude/factory/project.json` (created once by `/feat-init`). It declares
which tracks exist — `backend`, `frontend`, or both — with their source `dirs`, build
`commands`, and `protectedDirs`. It also declares `artifactsDir` (pipeline hand-off files)
and `docsDir` (user-facing documentation, default `docs`). Every command, agent, and hook
reads this file, so the SAME template works for a full-stack app, a pure-frontend app
(e.g. Vite), or a pure backend (.NET / Java / C). Disabled tracks are skipped automatically.

## The pipeline
```
/feat-init      (once per repo: write project.json)
/feat-new       <slug> "<desc>"   -> idea.md + state.json
/feat-research  <slug>            -> research.md   (built-in Explore, read-only)
/feat-grill     <slug>            -> decisions.md  ⏸ interactive interview (main session)
/feat-story     <slug>            -> story.md      ⏸ human approves (GATED on decisions.md)
/feat-spec      <slug>            -> brief.md      ⏸ human approves
/feat-backend   <slug>            -> code + backend-summary.md   (if backend enabled)
/feat-frontend  <slug>            -> UI            (if frontend enabled; reads the contract)
/feat-ship      <slug>            -> FABLE 5 (optional): converge verify→validate→fix under one /goal
/feat-verify    <slug>            -> verification.md
/feat-validate  <slug>            -> validation.md (read-only review)
/feat-fix       <slug>            -> bounded loop back to the owning builder
/feat-docs      <slug>            -> README + guides/examples (EN, then zh-TW)  [after a clean validate]
/feat-distill   <slug>            -> FABLE 5: bank verified lessons into MEMORY.md  [closing step]
/feat-status    <slug>            -> where am I
```
Each step writes its output as a file under `<artifactsDir>/<slug>/`. The next step reads
those files — that is how context is handed between agents (each subagent starts with a
fresh, isolated context window and shares only the filesystem). State lives in `state.json`.

## What makes this reliable (vs a natural-language orchestrator)
- **Order** = you invoking discrete commands, not a model deciding the sequence.
- **Scope** = hooks (`scope-track.sh`) hard-block writes, not just `tools:` hints.
- **Loop** = `/feat-fix` increments `retries` and STOPS at `loopMaxRetries` (default 3).
- **Handoff** = files on disk (cheap, reviewable, resumable), not re-pasted context.

## Grill step (/feat-grill)
Runs in the MAIN session (subagents cannot hold a multi-turn interview). It interviews the
human relentlessly about the plan until shared understanding: one question per turn, each
with a recommended answer, walking the decision tree and resolving dependencies one-by-one.
Questions `research.md` or the codebase can answer are answered by reading, not asking.
Output: `<artifactsDir>/<slug>/decisions.md` (settled decisions, glossary, declined
alternatives). `/feat-story` is GATED on this file. Hard-to-reverse decisions are marked
`[durable]` — candidates for MEMORY.md, banked only by `/feat-distill` (the single-writer
contract on MEMORY.md is unchanged). "No open decisions" is a valid fast outcome.

## Prompt style (agents & commands)
Binding when editing anything under `.claude/agents/` or `.claude/commands/`:
- **Prune no-ops** — delete sentences that do not change agent behaviour (restated
  defaults, motivational filler). Every retained sentence must earn its context load.
- **Leading words over paraphrase** — prefer canonical terms deep in training data
  ("Data Clumps", "tracer bullet", "deletion test") to hundred-word explanations; the
  term IS the compressed instruction.
- **Completion criteria** — every agent ends with the Fail-Loud block; every command names
  its output file and the next command. An agent that cannot say when it is done will not
  stop predictably.

## Scope enforcement (.active)
While a build step runs, the command writes `<track> <slug>` to `.claude/factory/.active`.
`scope-track.sh` then allows writes only inside that track's dirs (plus the artifacts dir),
and always blocks build output / deps / vendored libs. With NO `.active` file, normal
editing is never blocked. `/feat-validate` (when clean), `/feat-docs` (on finish), and
`/feat-fix` (at cap) remove `.active`. You may `rm .claude/factory/.active` at any time to
disable enforcement. Requires `jq`; if `jq` is absent, hooks fail safe (allow) and print a
notice. Scope tokens: `backend` / `frontend` → track dirs; `test` → testDirs; `docs`
(research/story/spec/validate authoring) → artifacts only; `userdocs` (the `/feat-docs`
step) → `docsDir` + repo-root `README.md` / `README_zh-TW.md` only.

## User-facing documentation (the /feat-docs step)
`/feat-docs` runs AFTER a clean `/feat-validate`, via the **doc-writer** agent. It does NOT
move or archive artifacts — they stay in `<artifactsDir>/<slug>/`, already separated per
slug, and remain the source of truth for `/feat-status` and resume/fix. It only AUTHORS new
user-facing docs: English `README.md` + guides/examples under `docsDir` (with **Mermaid**
diagrams), then their Traditional Chinese (Taiwan) translations with the `_zh-TW` suffix and
a language-switch link at the top of every version. See `terminology-zh-tw.md` for the
comment rule, the document-language policy, and the TW term dictionary.

## Mode contract
**Running the factory == Default Mode** of the project's CLAUDE.md. The factory is for
features you have decided to ship. `explore` / `prototype` / `spike` / POC work is a
separate path that does NOT go through these commands (so the story/test discipline here
never conflicts with EXPLORE Mode's relaxed rules).

## Honesty
Every agent ends with the project's Fail-Loud format: ✅ Verified / ⚠️ Skipped-Uncertain /
❓ Needs-human-input. "Tests pass" is never used to mask skipped tests.

## Fable 5 addendum (marked FABLE5 in the files it touches)
Applies when the orchestrating session runs Claude Fable 5. On other models these changes
are inert-but-harmless: the `model:` fields are plain Claude Code subagent routing, and the
classifier path simply never triggers.

**Model routing.** The orchestrating (main) session carries the expensive model; workers do
not need to. Pinned via agent frontmatter:

| Agent | model | Why |
|---|---|---|
| story-writer, spec-writer, doc-writer | sonnet | authoring, no code execution |
| backend-builder, frontend-builder | sonnet | workers; switch to `opus` per-feature if the brief touches an Off-Limits / security area |
| test-verifier | sonnet | writes real tests — Haiku is a grader, not an author |
| validator | sonnet | its value is independence (a different context), not cheapness |
| memory-distiller | sonnet | judgment task, no code execution |

**Classifier refusals are not defects.** Fable 5 ships safety classifiers that can decline a
request (the API reports `stop_reason: "refusal"`; a fallback to another Claude model exists
but is opt-in, not automatic). Factory semantics:
- Agents record a refusal as `classifier-refusal: <what>` in ⚠️ — never rephrase around it.
- The validator files these under a separate ⛔ heading, owner: human.
- `/feat-fix` step 0 sets refusal-only features to `blocked-classifier` WITHOUT consuming
  retries; mixed findings proceed normally with refusals carried forward untouched.
- Rationale: a loop that cannot tell "classifier said no" from "my code is wrong" will burn
  its retry budget rephrasing a refusal.
- Security-sensitive work (anything under an Off-Limits area such as `src/security/`) is the
  most classifier-prone; prefer `model: opus` for it, or keep it outside the factory.

**Memory layer.** `<artifactsDir>/MEMORY.md` is the factory's cross-feature memory:
verified facts, general rules, dated Watchlist. `/feat-distill <slug>` (memory-distiller)
is the CLOSING step of a feature — after `/feat-docs`, or straight after a clean
`/feat-validate` if docs are skipped, or after a `blocked` outcome (where open findings go
to the Watchlist as open risks, never to General rules). `/feat-research` reads MEMORY.md
before exploring, as leads to verify rather than facts. Only evidence-backed entries are
recorded; the file is capped (~150 lines), lives in `artifactsDir` (English only, per the
document language policy), and is version-controlled — review its diffs like code.

**Convergence loop (`/feat-ship` + `/goal`).** Automates ONLY the mechanical tail
(verify → validate → fix); the two ⏸ human checkpoints (story, spec) are untouched.
- The user sets the goal (Claude cannot); `/feat-ship <slug>` prints the exact `/goal`
  line. Its condition follows three hard constraints: (1) every condition is provable from
  output actually shown in the transcript — the evaluator (a separate small model, default
  Haiku) sees only the conversation, never the filesystem; (2) the condition carries its
  own turn cap, because /goal has no built-in hard iteration limit; (3) the condition names
  the failure states (`blocked`, `blocked-classifier`, ⛔) as goal-cannot-be-met, so a
  refusal or a capped loop ends the run loudly instead of spinning.
- What stays deterministic: `loopMaxRetries` inside `/feat-fix` is the binding hard stop
  (the turn cap in the goal text is advisory — it is judged by a model). Scope enforcement
  via `.active` and all hooks apply unchanged inside the loop.
- On success the loop hands off to `/feat-docs`, then `/feat-distill`.
- `/goal` is part of the hooks system: setting `disableAllHooks` disables BOTH scope
  enforcement and /goal. Never run the factory with hooks disabled.
- Anti-reward-hacking (Rule 7): the goal is met by the code satisfying the story — never
  by weakening tests or narrating success without pasted evidence.

**References.** This addendum was motivated by 0xCodez's self-improving-agent thread and
its BlockTempo zh-TW translation. They are inspiration, not specification: every
product-behavior claim (routing, refusal signal, /goal mechanics) was re-verified against
Anthropic's official documentation before adoption.
- Original thread: https://x.com/0xCodez/status/2065089060104720776
- zh-TW translation: https://www.blocktempo.com/self-improving-agent-fable-5-2/

## Pocock addendum — provenance
The grill step, Implementation slices, the validator's smells baseline + deletion test, and
the Prompt style rules are adapted from mattpocock/skills (MIT):
https://github.com/mattpocock/skills — verified against the repo and the author's own
posts (2026-07) before adoption. Deliberately NOT adopted: CONTEXT.md (duties covered by
MEMORY.md + per-slug decisions.md, preserving the single-writer contract) and the setup
skill (covered by /feat-init + project.json).
