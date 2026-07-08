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

FILE="$(printf '%s' "$INPUT" | jq -r '.tool_input.file_path // .tool_input.path // ""')"
[ -z "$FILE" ] && exit 0

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
PROJ="$ROOT/.claude/factory/project.json"
ACTIVE="$ROOT/.claude/factory/.active"
[ -f "$PROJ" ] || exit 0   # not initialised yet -> do not interfere

# repo-relative path
case "$FILE" in
  "$ROOT"/*) REL="${FILE#"$ROOT"/}" ;;
  /*)        REL="$FILE" ;;
  *)         REL="$FILE" ;;
esac

ARTDIR="$(jq -r '.artifactsDir // ".claude/factory"' "$PROJ" 2>/dev/null || echo ".claude/factory")"
# Artifacts are always writable (story/spec/research/verify/validate output)
case "$REL" in "$ARTDIR"/*|"$ARTDIR") exit 0 ;; esac

# Build output / deps / vendored libs are never writable
for p in $(jq -r '(.tracks.frontend.protectedDirs[]?, .tracks.backend.protectedDirs[]?) // empty' "$PROJ" 2>/dev/null); do
  case "$REL" in "$p"/*|"$p") echo "scope-track: '$REL' is protected ($p); blocked." >&2; exit 2 ;; esac
done

# No active factory step -> normal dev, allow
[ -f "$ACTIVE" ] || exit 0
TRACK="$(awk 'NR==1{print $1}' "$ACTIVE" 2>/dev/null || echo "")"
[ -z "$TRACK" ] && exit 0

case "$TRACK" in
  backend)  DIRS="$(jq -r '.tracks.backend.dirs[]? // empty' "$PROJ" 2>/dev/null)";;
  frontend) DIRS="$(jq -r '.tracks.frontend.dirs[]? // empty' "$PROJ" 2>/dev/null)";;
  test)     DIRS="$(jq -r '.testDirs[]? // empty' "$PROJ" 2>/dev/null)";;
  *)        DIRS="";;   # docs/readonly phases: only artifacts (handled above) allowed
esac

OK=0
for d in $DIRS; do
  case "$REL" in "$d"/*|"$d") OK=1; break ;; esac
done

if [ "$OK" -ne 1 ]; then
  echo "scope-track: active step '$TRACK' may not write '$REL' (outside its allowed dirs). Blocked." >&2
  exit 2
fi
exit 0
