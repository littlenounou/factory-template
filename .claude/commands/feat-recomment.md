---
description: One-off maintenance — convert legacy line-interleaved bilingual comments in existing code to the block-after-block form. Not part of the per-feature pipeline.
argument-hint: [path] (default: whole repo)
---
Migrate existing comments to the block-after-block bilingual form defined in
`.claude/factory/terminology-zh-tw.md` §1. Target: `$1` (default: the whole repo).

This is a MAINTENANCE command, not a pipeline step. It has no slug and writes no artifacts.
The mechanical reordering is done by a deterministic script — you do NOT rewrite comments
by hand except for the leftovers the script explicitly refuses to touch.

1. GUARD — refuse to proceed and tell the user why if either holds:
   - `.claude/factory/.active` exists (a build step is mid-flight; a repo-wide edit would
     fight the scope hook). Tell them to finish or `rm` it.
   - `git status --porcelain` is non-empty. This migration must land as ONE reviewable
     diff with no behaviour change mixed in. Tell them to commit or stash first.

2. DRY RUN — `python3 .claude/factory/comment-migrate.py $1`
   Report to the user: files scanned, files that would change, blocks regrouped, pairs
   reordered (Chinese was first), and blocks needing human review. Then STOP and ask for
   approval. Do not apply on your own initiative.

3. APPLY (after approval) — `python3 .claude/factory/comment-migrate.py $1 --apply`
   Then show `git diff --stat`. Spot-check 2-3 of the changed blocks by reading them and
   confirm the English block, separator, and Chinese block are in the right order.

4. LEFTOVERS — read `.claude/factory/comment-migration-report.md`. The "Needs human review"
   section lists blocks the script refused to reorder (usually commented-out code mixed in
   with prose, or one line holding both languages). Work through them ONE FILE AT A TIME:
   - Reorder into English block → separator → Chinese block.
   - Keep commented-out code as its own separate comment block, adjacent to nothing else.
   - Do NOT translate, reword, add, or delete any comment text. If a comment is wrong or
     missing a translation, say so in your report — do not silently author new prose.
   If a block is genuinely ambiguous, leave it and list it for the human.

5. Tell the user to review and commit this as a standalone comment-style commit, and that
   `python3 .claude/factory/comment-migrate.py --check` exits non-zero when interleaved
   comments remain (usable as an optional CI guard).

End with the Fail-Loud block: ✅ Verified (counts applied, leftovers you fixed by hand) /
⚠️ Skipped-Uncertain (blocks you deliberately left) / ❓ Needs-human-input.
