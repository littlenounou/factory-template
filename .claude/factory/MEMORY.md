# Factory Memory (FABLE 5 memory layer — cross-feature, version-controlled)

> Written ONLY by the memory-distiller agent via `/feat-distill`, after a feature passes
> validation. Read at the start of `/feat-research`. Humans may edit freely — this file is
> part of the repo and reviewable in PRs like any other change.
>
> Entry contract (enforced by the distiller):
> - Every entry is VERIFIED: it traces to something that actually happened in a shipped
>   feature (a failed-then-fixed test, a validator finding, a quality-gate failure, a
>   surfaced anti-pattern). Speculation and restated CLAUDE.md rules do not belong here.
> - One line per entry, general form, dated and attributed: `- [YYYY-MM-DD slug] statement`
> - Hard cap ~150 lines total. The distiller merges duplicates and drops the least
>   valuable entries to stay under it — memory that nobody can afford to read is not memory.

## Verified facts
<!-- Stable truths about THIS codebase discovered while shipping features.
     e.g. - [2026-07-06 user-auth] Session middleware runs before tenant resolution; anything reading tenant in middleware sees null. -->
(none yet)

## General rules
<!-- Reusable do/don't patterns distilled from fixes and findings, written so the NEXT
     feature can apply them without context.
     e.g. - [2026-07-06 csv-export] Streaming responses bypass the global error handler; wrap them explicitly. -->
- [2026-07-17 template] Worker tier bumped to claude-sonnet-5 (env pin). Expect ~1.0–1.35× token counts vs 4.6 (new tokenizer) and possible safety refusals from workers (cyber safeguards default-on) — refusal triage in /feat-fix covers this. Lessons above this line were produced under Sonnet 4.6-or-earlier behavior.
- [2026-07-09 template] Subagent model routing is enforced by the project settings env pin (`CLAUDE_CODE_SUBAGENT_MODEL`), not by frontmatter (claude-code#44385; any-scope env overrides it). Before a factory run, `echo $CLAUDE_CODE_SUBAGENT_MODEL` — a shell export beats settings. Broken-routing signature: /usage shows orchestrator + Haiku only, Sonnet at zero.

## Watchlist
<!-- Known-flaky things, deferred cleanups surfaced under Rule 5, and open risks that are
     not defects of any single feature. Remove entries when resolved.
     e.g. - [2026-07-06 report-gen] tests/e2e/pdf.spec is timing-sensitive on CI; reruns usually pass. -->
(none yet)
