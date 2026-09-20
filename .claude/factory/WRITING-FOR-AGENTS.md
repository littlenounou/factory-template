<!-- Adapted from mattpocock/skills `writing-for-agents` (MIT), as read on upstream main
     on 2026-09-20. Reached by the pointer in CONVENTIONS.md; never @imported. -->
# Writing for agents

Binding reference whenever you edit anything the agent reads: `CLAUDE.md`, a file under
`.claude/factory/`, `.claude/agents/`, or `.claude/commands/`. The aim is a *predictable*
document — the agent takes the same process every run. Every rule below applies; a
change is done when each touched line passes all of them.

## The two loads
- **Context load** — always-loaded material: `CLAUDE.md` and its `@import`s, every agent
  and command description. Here it multiplies: each factory agent reloads `CLAUDE.md` and
  its imports on every run (only built-in Explore and Plan skip them).
- **Cognitive load** — the human's burden of knowing which document exists and when to
  reach for it. Spend it where human judgement matters.

## Context pointers
A pointer names out-of-context material and the condition for reaching it: an agent or
command `description`, a "read X when Y" line. Its wording decides when the material is
reached. Front-load the leading word; one trigger per branch (synonyms of one branch
collapse — user-utterance triggers, which must match what people say, excepted); cut the
identity the body already carries. A must-have target behind a weak pointer is a variance
bug: sharpen the wording first, inline the material only if sharpening fails.

## Information hierarchy
Steps (ordered actions) and reference (rules, facts consulted on demand), placed on a
ladder by how immediately the agent needs them: in-file step → in-file reference →
**disclosed** reference behind a pointer. The branching test decides: inline what every
branch needs; disclose what only some branches reach. Keep a concept's definition, rules
and caveats under one heading (**co-location**). **Sprawl** — a file too long even when
every line is live — thins attention; the cure is the ladder, and a split by branch or by
sequence.

## Completion criteria
Every step ends on a checkable, demanding criterion: "every acceptance criterion reachable
from a doc", never "as needed". A vague bound invites **premature completion**, pulled by
the steps still ahead: sharpen the bound first; hide later steps behind a real context
boundary (a hand-off or a subagent) only when the rush is observed. Here, every agent
ends with the Fail-Loud block, and every command names its output file and the next
command.

## Leading words
A pretrained concept repeated as a token anchors behaviour in the fewest tokens ("deletion
test", "tracer bullet", "frontier", "fog of war"). Collapse a restated triad or a
sentence-long gesture into one such word. **Prompt the positive**: state the target
behaviour, because a prohibition drags the banned behaviour into context. A ban stays only
as a hard guardrail with no positive form, labelled as one and paired with its target.

## Pruning
- **Single source of truth, per context.** Within one context, each meaning lives once.
  An agent file is its own context, so a rule its task needs may repeat across agent
  files; a rule `CLAUDE.md` or its imports already carry reaches every factory agent and
  stays out of the agent file.
- **Cache test.** The environment is a source of truth — `project.json`, `scope-track.sh`,
  agent frontmatter, `--help`. A line restating a cheap lookup is a cache that goes stale;
  keep what looking cannot find — the unwritten convention, the reason, the gotcha.
- **Relevance.** A line that bears on no run — history, provenance, motivation — goes to
  `CLAUDE-rationale.md` or into an HTML comment (stripped before loading). Change history
  goes where the change lives: an edit to the factory template itself into the template
  repo's `CHANGES.md` (never installed into a target repo); a project-specific adjustment
  in a target repo into that repo's own changelog or commit message.
  Unpruned, stale layers settle as **sediment**.
- **No-ops.** A sentence that restates what the model already does pays load to say
  nothing: delete the whole sentence. The test is model-relative, so settle a dispute by
  running the document, not by debate.
