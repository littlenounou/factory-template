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
# The contract points at these by relative path; a missing one is a silent dead pointer.
for f in CONVENTIONS.md terminology-zh-tw.md CLAUDE-rationale.md EXPLORE-MODE.md PHASE-BOUNDARIES.md WRITING-FOR-AGENTS.md; do
  [ -f "$SRC/.claude/factory/$f" ] || missing="$missing .claude/factory/$f"
done
if [ -n "$missing" ]; then
  echo "ERROR: this template copy is incomplete — missing:$missing"
  echo "Your download likely skipped the hidden .claude/ folder. Re-download the ZIP and"
  echo "extract it with hidden files included, then run install.sh again."
  exit 1
fi

# Template-owned files are overwritten on every install. Two files are the repo's own and
# are handled below instead: .claude/factory/MEMORY.md and .claude/settings.json.
mkdir -p "$TARGET/.claude/factory"
shopt -s dotglob
for item in "$SRC/.claude/"*; do
  case "$(basename "$item")" in settings.json|factory) continue ;; esac
  cp -R "$item" "$TARGET/.claude/"
done
for item in "$SRC/.claude/factory/"*; do
  [ "$(basename "$item")" = "MEMORY.md" ] && continue
  cp -R "$item" "$TARGET/.claude/factory/"
done
shopt -u dotglob
chmod +x "$TARGET/.claude/hooks/"*.sh 2>/dev/null || true
echo "• Copied .claude/ into $TARGET"

# MEMORY.md is written by /feat-distill, so the repo's copy is never overwritten. It lives in
# <artifactsDir>; read that from project.json the same way the hooks do.
ARTDIR=".claude/factory"
PROJ="$TARGET/.claude/factory/project.json"
if [ -f "$PROJ" ] && command -v jq >/dev/null 2>&1; then
  ARTDIR="$(jq -r '.artifactsDir // ".claude/factory"' "$PROJ" 2>/dev/null || true)"
  ARTDIR="${ARTDIR#./}"; ARTDIR="${ARTDIR%/}"
  [ -n "$ARTDIR" ] || ARTDIR=".claude/factory"
fi
MEM="$TARGET/.claude/factory/MEMORY.md"
if [ "$ARTDIR" != ".claude/factory" ]; then
  echo "• MEMORY.md not installed: artifactsDir is '$ARTDIR', so the memory layer is"
  echo "  $ARTDIR/MEMORY.md. To start one, copy the template's .claude/factory/MEMORY.md there."
elif [ -f "$MEM" ]; then
  echo "• Kept the repo's .claude/factory/MEMORY.md (never overwritten)."
else
  cp "$SRC/.claude/factory/MEMORY.md" "$MEM"
  echo "• Installed a starter .claude/factory/MEMORY.md."
fi

# settings.json: the template owns .hooks; every other key (permissions, env, ...) is the repo's.
# Merge: keep the repo's keys, add keys only the template has, replace .hooks with the template's.
SET="$TARGET/.claude/settings.json"
TPL="$SRC/.claude/settings.json"
if [ ! -f "$SET" ]; then
  cp "$TPL" "$SET"
  echo "• Installed .claude/settings.json."
elif ! command -v jq >/dev/null 2>&1 || ! jq -e 'type == "object"' "$SET" >/dev/null 2>&1; then
  cp "$SET" "$SET.bak"
  cp "$TPL" "$SET"
  echo "WARNING: could not merge .claude/settings.json (jq not found, or the file is not a JSON object)."
  echo "  Replaced it with the template's; your old file is .claude/settings.json.bak."
  echo "  Copy back any permissions or other settings you need."
else
  if jq -e '.hooks == null' "$SET" >/dev/null; then
    note="• Merged .claude/settings.json: added the factory hooks, kept your other settings."
  elif jq -e --slurpfile t "$TPL" '.hooks == $t[0].hooks' "$SET" >/dev/null; then
    note="• Merged .claude/settings.json: hooks already current, kept your other settings."
  else
    cp "$SET" "$SET.bak"
    note="• Merged .claude/settings.json: replaced \"hooks\" with the template's, kept your other
  settings. The old file is .claude/settings.json.bak; re-add any hooks of your own from it."
  fi
  MERGE='($t[0] + .) | .hooks = $t[0].hooks'
  # Rewrite only when something changes, so an up-to-date file keeps its formatting.
  if ! jq -e --slurpfile t "$TPL" "($MERGE) == ." "$SET" >/dev/null; then
    tmp="$(mktemp)"
    jq --slurpfile t "$TPL" "$MERGE" "$SET" > "$tmp"
    cat "$tmp" > "$SET"
    rm -f "$tmp"
  fi
  echo "$note"
fi

if [ -f "$TARGET/CLAUDE.md" ]; then
  cp "$SRC/CLAUDE.factory-snippet.md" "$TARGET/CLAUDE.factory-snippet.md"
  echo "• Existing CLAUDE.md left untouched — add the two @import lines from the"
  echo "  <<< FEATURE FACTORY >>> block of CLAUDE.factory-snippet.md (copied to the repo root)."
  echo "  Upgrading? Delete the old \"### Feature Factory\" block — it now lives in CONVENTIONS.md."
else
  cp "$SRC/CLAUDE.factory-snippet.md" "$TARGET/CLAUDE.md"
  echo "• No CLAUDE.md found — installed the snippet as a starter CLAUDE.md."
fi

echo
echo "Installed (counts):"
echo "  agents:   $(ls -1 "$TARGET/.claude/agents"/*.md 2>/dev/null | wc -l | tr -d ' ')  (expect 8)"
echo "  commands: $(ls -1 "$TARGET/.claude/commands"/*.md 2>/dev/null | wc -l | tr -d ' ')  (expect 20)"
echo "  hooks:    $(ls -1 "$TARGET/.claude/hooks"/*.sh 2>/dev/null | wc -l | tr -d ' ')  (expect 3)"
echo
echo "Contract files in .claude/factory/ (imported by CLAUDE.md, or reached by pointer):"
for f in CONVENTIONS.md terminology-zh-tw.md CLAUDE-rationale.md EXPLORE-MODE.md PHASE-BOUNDARIES.md WRITING-FOR-AGENTS.md; do
  [ -f "$TARGET/.claude/factory/$f" ] && echo "  ok  $f" || echo "  MISSING  $f"
done

# The hooks in settings.json use onFailure: "block", which needs Claude Code 2.1.295+.
# Warn only: the installer may run in a shell where `claude` is not on PATH.
NEED="2.1.295"
echo
if command -v claude >/dev/null 2>&1; then
  HAVE="$(claude --version 2>/dev/null | awk '{print $1}')"
  older=0
  IFS=. read -r h1 h2 h3 _ <<< "${HAVE}.0.0"
  IFS=. read -r n1 n2 n3 _ <<< "$NEED"
  for pair in "$h1:$n1" "$h2:$n2" "$h3:$n3"; do
    a="${pair%%:*}"; b="${pair##*:}"; a="${a//[!0-9]/}"; a="${a:-0}"
    if [ "$a" -lt "$b" ]; then older=1; break; fi
    if [ "$a" -gt "$b" ]; then break; fi
  done
  if [ "$older" -eq 1 ]; then
    echo "WARNING: Claude Code $HAVE is older than $NEED. The hooks rely on onFailure: \"block\""
    echo "  (a hook that cannot run blocks the tool call). Upgrade Claude Code before using this repo."
  else
    echo "Claude Code $HAVE — ok (needs $NEED+)."
  fi
else
  echo "NOTE: 'claude' not found on PATH here; check that Claude Code is $NEED or later."
fi
echo "Done. Next: cd \"$TARGET\", open Claude Code, run /feat-init"
