#!/usr/bin/env bash
# Usage: bash .claude/hooks/quality-gate.sh [backend|frontend|all]
# Runs typecheck -> lint -> test for the requested enabled track(s), reading
# commands from .claude/factory/project.json. Exits non-zero on the first failure.
set -uo pipefail
command -v jq >/dev/null 2>&1 || { echo "quality-gate: jq required." >&2; exit 1; }
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
PROJ="$ROOT/.claude/factory/project.json"
[ -f "$PROJ" ] || { echo "quality-gate: project.json not found; run /feat-init first." >&2; exit 1; }
WANT="${1:-all}"

run_track() {
  t="$1"
  [ "$(jq -r ".tracks.$t.enabled // false" "$PROJ")" = "true" ] || return 0
  for phase in typecheck lint test; do
    cmd="$(jq -r ".tracks.$t.commands.$phase // \"\"" "$PROJ")"
    [ -z "$cmd" ] && { echo "── [$t] $phase: (none configured, skipped)"; continue; }
    echo "── [$t] $phase: $cmd"
    if ! eval "$cmd"; then echo "quality-gate: [$t] $phase FAILED" >&2; return 1; fi
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
