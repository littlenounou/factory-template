#!/usr/bin/env bash
set -euo pipefail
TARGET="${1:-}"
[ -n "$TARGET" ] || { echo "Usage: ./install.sh /path/to/your/repo"; exit 1; }
[ -d "$TARGET" ] || { echo "Error: '$TARGET' is not a directory."; exit 1; }
SRC="$(cd "$(dirname "$0")" && pwd)"

# Fail loud if the template itself is incomplete (e.g. a partial download).
missing=""
for d in .claude/agents .claude/commands .claude/hooks .claude/factory; do
  [ -d "$SRC/$d" ] || missing="$missing $d"
done
[ -f "$SRC/.claude/settings.json" ] || missing="$missing .claude/settings.json"
if [ -n "$missing" ]; then
  echo "ERROR: this template copy is incomplete — missing:$missing"
  echo "Your download likely skipped the hidden .claude/ folder. Re-download the ZIP and"
  echo "extract it with hidden files included, then run install.sh again."
  exit 1
fi

mkdir -p "$TARGET/.claude"
cp -R "$SRC/.claude/." "$TARGET/.claude/"
chmod +x "$TARGET/.claude/hooks/"*.sh 2>/dev/null || true
echo "• Copied .claude/ into $TARGET"

if [ -f "$TARGET/CLAUDE.md" ]; then
  cp "$SRC/CLAUDE.factory-snippet.md" "$TARGET/CLAUDE.factory-snippet.md"
  echo "• Existing CLAUDE.md left untouched — merge the two <<< FEATURE FACTORY >>> blocks"
  echo "  from CLAUDE.factory-snippet.md (copied to the repo root) into it."
else
  cp "$SRC/CLAUDE.factory-snippet.md" "$TARGET/CLAUDE.md"
  echo "• No CLAUDE.md found — installed the snippet as a starter CLAUDE.md."
fi

echo
echo "Installed (counts):"
echo "  agents:   $(ls -1 "$TARGET/.claude/agents"/*.md 2>/dev/null | wc -l | tr -d ' ')  (expect 8)"
echo "  commands: $(ls -1 "$TARGET/.claude/commands"/*.md 2>/dev/null | wc -l | tr -d ' ')  (expect 14)"
echo "  hooks:    $(ls -1 "$TARGET/.claude/hooks"/*.sh 2>/dev/null | wc -l | tr -d ' ')  (expect 3)"
echo "Done. Next: cd \"$TARGET\", open Claude Code, run /feat-init"
