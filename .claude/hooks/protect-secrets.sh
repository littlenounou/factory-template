#!/usr/bin/env bash
# PreToolUse hook. Blocks writing secret files (Edit|Write) and staging/committing
# them (Bash git add/commit). Always on, independent of factory state.
set -uo pipefail
INPUT="$(cat)"
command -v jq >/dev/null 2>&1 || { echo "protect-secrets: jq not found; skipped." >&2; exit 0; }

TOOL="$(printf '%s' "$INPUT" | jq -r '.tool_name // ""')"
SECRET_RE='(^|/)(\.env($|\.)|.*\.(key|pem|p12|pfx)$|secrets?\.(json|ya?ml|yml|txt|env))'

if [ "$TOOL" = "Bash" ]; then
  CMD="$(printf '%s' "$INPUT" | jq -r '.tool_input.command // ""')"
  if printf '%s' "$CMD" | grep -Eiq 'git[[:space:]]+(add|commit)'; then
    if printf '%s' "$CMD" | grep -Eiq '\.env|\.key|\.pem|\.p12|\.pfx|secret'; then
      echo "protect-secrets: this command looks like it stages/commits a secret. Blocked." >&2
      exit 2
    fi
  fi
  exit 0
fi

FILE="$(printf '%s' "$INPUT" | jq -r '.tool_input.file_path // .tool_input.path // ""')"
[ -z "$FILE" ] && exit 0
if printf '%s' "$FILE" | grep -Eiq "$SECRET_RE"; then
  echo "protect-secrets: '$FILE' looks like a secret file; edits blocked." >&2
  exit 2
fi
exit 0
