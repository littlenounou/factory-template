---
description: Maintenance — migrate legacy line-interleaved bilingual comments to the block-after-block form.
argument-hint: "[path] (default: whole repo)"
---
Migrate existing comments to the block-after-block bilingual form defined in
`.claude/factory/terminology-zh-tw.md` §1. Target: `$1` (default: the whole repo).

A MAINTENANCE command, not a pipeline step: no slug, no `state.json`. A deterministic
script does the reordering; your hands touch only the leftovers it refuses.
`OUT` below is `--report .claude/factory/comment-migration-report.md --diff
.claude/factory/comment-migration.diff`; pass the same `OUT` on every run.

1. GUARD: STOP and tell the user why if either holds:
   - `.claude/factory/.active` exists (a build step is mid-flight; a repo-wide edit would
     fight the scope hook). Tell them to finish or `rm` it.
   - `git status --porcelain` is non-empty. This migration must land as ONE reviewable
     diff with no behaviour change mixed in. Tell them to commit or stash first.

2. DRY RUN: `python3 .claude/factory/comment-migrate.py $1 OUT`
   Report to the user: files scanned, files that would change, blocks regrouped, pairs
   reordered, blocks needing human review, files left unwritten after a failed safety
   check, and changed files without a lexer check (named in the report).

3. REVIEW: read the whole `.claude/factory/comment-migration.diff` yourself, then show it
   to the user in full (every hunk, not a stat or a sample). Check each hunk:
   - every changed line is a comment or docstring line;
   - each block still sits directly above the same line of code;
   - English block, separator, Chinese block, in that order;
   - lines inside one language keep their order.
   A hunk that fails any check is a script bug: do not apply. Report the hunk and stop.
   Otherwise STOP and ask for approval. Approval means the user has read the whole diff.

4. APPLY (after approval): `python3 .claude/factory/comment-migrate.py $1 --apply OUT`
   Done when `git apply -R --check .claude/factory/comment-migration.diff` passes and
   `git diff --stat` lists exactly the files in that diff: what landed is what was
   reviewed. If either fails, run `git checkout -- .` and report it as a script bug.

5. LEFTOVERS: read `.claude/factory/comment-migration-report.md`. "Needs human review"
   lists blocks the script refused to change, each with its reason:
   - commented-out code mixed in with prose;
   - one line holding both languages with no single clean sentence boundary;
   - an English-looking line right after an unfinished Chinese sentence (a wrapped
     sentence or a new English one: the script cannot tell);
   - English block followed by Chinese block with no separator: insert the separator;
   - paragraphs that alternate languages but do not pair up: a translation is missing;
   - mid-sentence blank line: delete that one blank line;
   - text sharing a line with docstring quotes that regrouping would move;
   - "safety check failed": the file was not written, because the rewrite would have
     changed code or a string literal (usually a comment-like line inside a string,
     heredoc or template literal). Fix only its real comments by hand.
   Work through them ONE FILE AT A TIME:
   - Reorder into English block → separator → Chinese block.
   - A wrapped sentence keeps all its lines together, including a continuation line that
     holds only code or punctuation.
   - Keep commented-out code as its own separate comment block, adjacent to nothing else.
   - Move lines only: every comment keeps its text word for word (hard guardrail). A
     comment that is wrong or missing its translation goes in your report.
   - A line holding both languages is the one exception: split it at the language
     boundary into separate lines, each with the line's own prefix (indent, comment
     token, leading space). The moved part starts its OWN new line. Never join it onto
     the end of a neighbouring line, and never re-wrap the lines around it.
   If a block is genuinely ambiguous, leave it and list it for the human.

6. Tell the user to review and commit this as a standalone comment-style commit, and that
   `python3 .claude/factory/comment-migrate.py --check` exits non-zero while any block
   still needs migration or review (usable as an optional CI guard).

End with the Fail-Loud block: ✅ Verified (counts applied, leftovers you fixed by hand) /
⚠️ Skipped-Uncertain (blocks you deliberately left) / ❓ Needs-human-input.
