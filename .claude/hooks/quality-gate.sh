#!/usr/bin/env bash
# Usage: bash .claude/hooks/quality-gate.sh [backend|frontend|all]   (from the repo root)
# Runs typecheck -> lint -> test for the requested enabled track(s), reading
# commands from .claude/factory/project.json. Exits non-zero on the first failure.
set -uo pipefail
command -v jq >/dev/null 2>&1 || { echo "quality-gate: jq required." >&2; exit 1; }
# Repo root: the cwd's git top level; if the cwd has left the repo, the session's
# project dir (same resolution as scope-track.sh).
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [ -z "$ROOT" ] || [ ! -f "$ROOT/.claude/factory/project.json" ]; then
  [ -n "${CLAUDE_PROJECT_DIR:-}" ] && ROOT="$CLAUDE_PROJECT_DIR"
fi
[ -n "$ROOT" ] || ROOT="$(pwd)"
PROJ="$ROOT/.claude/factory/project.json"
[ -f "$PROJ" ] || { echo "quality-gate: project.json not found; run /feat-init first." >&2; exit 1; }
WANT="${1:-all}"
# Manifest commands are written relative to the repo root; run them from there even
# when the caller's shell sits in a subdirectory.
cd "$ROOT" || { echo "quality-gate: cannot cd to $ROOT" >&2; exit 1; }

run_track() {
  t="$1"
  [ "$(jq -r ".tracks.$t.enabled // false" "$PROJ")" = "true" ] || return 0
  for phase in typecheck lint test; do
    cmd="$(jq -r ".tracks.$t.commands.$phase // \"\"" "$PROJ")"
    [ -z "$cmd" ] && { echo "── [$t] $phase: (none configured, skipped)"; continue; }
    echo "── [$t] $phase: $cmd"
    if ! ( cd "$ROOT" && eval "$cmd" ); then echo "quality-gate: [$t] $phase FAILED" >&2; return 1; fi
  done
  return 0
}

rc=0
if [ "$WANT" = "all" ]; then
  for t in backend frontend; do run_track "$t" || rc=1; done
else
  run_track "$WANT" || rc=1
fi
[ "$rc" -eq 0 ] && echo "quality-gate: PASS" || echo "quality-gate: FAIL"
exit "$rc"
