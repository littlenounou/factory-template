---
description: Maintenance — migrate legacy line-interleaved bilingual comments to the block-after-block form.
argument-hint: [path] (default: whole repo)
---
Migrate existing comments to the block-after-block bilingual form defined in
`.claude/factory/terminology-zh-tw.md` §1. Target: `$1` (default: the whole repo).

A MAINTENANCE command, not a pipeline step: no slug, no `state.json`. A deterministic
script does the reordering; your hands touch only the leftovers it refuses.

1. GUARD — STOP and tell the user why if either holds:
   - `.claude/factory/.active` exists (a build step is mid-flight; a repo-wide edit would
     fight the scope hook). Tell them to finish or `rm` it.
   - `git status --porcelain` is non-empty. This migration must land as ONE reviewable
     diff with no behaviour change mixed in. Tell them to commit or stash first.

2. DRY RUN — `python3 .claude/factory/comment-migrate.py $1`
   Report to the user: files scanned, files that would change, blocks regrouped, pairs
   reordered (Chinese was first), and blocks needing human review. Then STOP and ask for
   approval.

3. APPLY (after approval) — `python3 .claude/factory/comment-migrate.py $1 --apply`
   Then show `git diff --stat`. Spot-check 2-3 of the changed blocks by reading them and
   confirm the English block, separator, and Chinese block are in the right order.

4. LEFTOVERS — read `.claude/factory/comment-migration-report.md`. The "Needs human review"
   section lists blocks the script refused to reorder (usually commented-out code mixed in
   with prose, or one line holding both languages). Work through them ONE FILE AT A TIME:
   - Reorder into English block → separator → Chinese block.
   - Keep commented-out code as its own separate comment block, adjacent to nothing else.
   - Move lines only: every comment keeps its text word for word (hard guardrail). A
     comment that is wrong or missing its translation goes in your report.
   If a block is genuinely ambiguous, leave it and list it for the human.

5. Tell the user to review and commit this as a standalone comment-style commit, and that
   `python3 .claude/factory/comment-migrate.py --check` exits non-zero when interleaved
   comments remain (usable as an optional CI guard).

End with the Fail-Loud block: ✅ Verified (counts applied, leftovers you fixed by hand) /
⚠️ Skipped-Uncertain (blocks you deliberately left) / ❓ Needs-human-input.
