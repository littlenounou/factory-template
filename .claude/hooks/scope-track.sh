#!/usr/bin/env bash
# PreToolUse hook (Edit|Write). Enforces per-track write scope ONLY while a factory
# build step is active. The active step+slug is written to .claude/factory/.active
# by the /feat-* commands. With no .active file, normal editing is never blocked.
set -uo pipefail
INPUT="$(cat)"

# jq is required for enforcement; degrade safely (allow) if unavailable.
if ! command -v jq >/dev/null 2>&1; then
  echo "scope-track: jq not found; enforcement skipped (install jq to enable)." >&2
  exit 0
fi

# jq.exe on Windows ends each -r line with CRLF; drop the CR (a no-op elsewhere).
jqr() { jq -r "$@" | tr -d '\r'; }

# Paths are compared as keys. On Windows (Git Bash, MSYS2, Cygwin) Claude passes
# C:\x\repo\a.ts while git reports C:/x/repo, and NTFS ignores case, so the key uses /
# separators, writes /c/ and /cygdrive/c/ as c:/, and is lower case. Elsewhere the key is
# the path itself: exact and case-sensitive.
case "$(uname -s 2>/dev/null)" in MINGW*|MSYS*|CYGWIN*) WIN=1 ;; *) WIN=0 ;; esac
key() {
  if [ "$WIN" -eq 1 ]; then
    printf '%s' "$1" | tr '\\' '/' | tr '[:upper:]' '[:lower:]' |
      sed -E 's#^/cygdrive/([a-z])/#\1:/#; s#^/([a-z])/#\1:/#'
  else
    printf '%s' "$1"
  fi
}

FILE="$(printf '%s' "$INPUT" | jqr '.tool_input.file_path // .tool_input.path // ""')"
[ -z "$FILE" ] && exit 0

# Repo root: the cwd's git top level, which follows Claude into a worktree. If the cwd
# has left the repo (a `cd` elsewhere), fall back to the session's project dir so the
# manifest is still found; never to the bare cwd, which would silently allow everything.
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [ -z "$ROOT" ] || [ ! -f "$ROOT/.claude/factory/project.json" ]; then
  [ -n "${CLAUDE_PROJECT_DIR:-}" ] && ROOT="$CLAUDE_PROJECT_DIR"
fi
[ -n "$ROOT" ] || ROOT="$(pwd)"
PROJ="$ROOT/.claude/factory/project.json"
ACTIVE="$ROOT/.claude/factory/.active"
[ -f "$PROJ" ] || exit 0   # not initialised yet -> do not interfere

# repo-relative path (as a key; see key() above)
KFILE="$(key "$FILE")"
KROOT="$(key "$ROOT")"
case "$KFILE" in
  "$KROOT"/*) REL="${KFILE#"$KROOT"/}" ;;
  *)          REL="$KFILE" ;;
esac

ARTDIR="$(key "$(jqr '.artifactsDir // ".claude/factory"' "$PROJ" 2>/dev/null || echo ".claude/factory")")"
# Artifacts are always writable (story/spec/research/verify/validate output)
case "$REL" in "$ARTDIR"/*|"$ARTDIR") exit 0 ;; esac

# Build output / deps / vendored libs are never writable
for p in $(jqr '(.tracks.frontend.protectedDirs[]?, .tracks.backend.protectedDirs[]?) // empty' "$PROJ" 2>/dev/null); do
  p="$(key "$p")"
  case "$REL" in "$p"/*|"$p") echo "scope-track: '$REL' is protected ($p); blocked." >&2; exit 2 ;; esac
done

# No active factory step -> normal dev, allow
[ -f "$ACTIVE" ] || exit 0
TRACK="$(tr -d '\r' < "$ACTIVE" 2>/dev/null | awk 'NR==1{print $1}')"
[ -z "$TRACK" ] && exit 0

case "$TRACK" in
  backend)  DIRS="$(jqr '.tracks.backend.dirs[]? // empty' "$PROJ" 2>/dev/null)";;
  frontend) DIRS="$(jqr '.tracks.frontend.dirs[]? // empty' "$PROJ" 2>/dev/null)";;
  test)     DIRS="$(jqr '.testDirs[]? // empty' "$PROJ" 2>/dev/null)";;
  userdocs) # /feat-docs: user-facing docs only — docsDir + repo-root README files.
            DOCSDIR="$(jqr '.docsDir // "docs"' "$PROJ" 2>/dev/null)"
            DIRS="$DOCSDIR README.md README_zh-TW.md";;
  *)        DIRS="";;   # docs/readonly phases: only artifacts (handled above) allowed
esac

OK=0
for d in $DIRS; do
  d="$(key "$d")"
  case "$REL" in "$d"/*|"$d") OK=1; break ;; esac
done

if [ "$OK" -ne 1 ]; then
  echo "scope-track: active step '$TRACK' may not write '$REL' (outside its allowed dirs). Blocked." >&2
  exit 2
fi
exit 0
