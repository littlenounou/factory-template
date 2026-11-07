#!/usr/bin/env bash
# Smoke test for install.sh (template repo only; not installed).
# Installs into a scratch repo twice and checks what landed. cd510f7 once dropped
# install.sh's executable bit without any check failing; this catches that too.
# Usage: bash tests/install-smoke.sh
set -uo pipefail
SRC="$(cd "$(dirname "$0")/.." && pwd)"
fails=0
fail() { echo "FAIL $*"; fails=$((fails + 1)); }
ok()   { echo "ok   $*"; }

cd "$SRC" || exit 1

# Executable bits as committed (the working tree can differ on Windows checkouts).
for rel in install.sh .claude/hooks/*.sh; do
  mode="$(git ls-files -s -- "$rel" 2>/dev/null | awk '{print $1}')"
  if [ -z "$mode" ]; then [ -x "$rel" ] && mode=100755 || mode=100644; fi
  [ "$mode" = 100755 ] && ok "$rel is executable" || fail "$rel is not executable (mode $mode)"
done

# The installers' "(expect N)" counts must match the template.
for kind in agents:md commands:md hooks:sh; do
  dir="${kind%%:*}"; ext="${kind##*:}"
  have="$(ls -1 "$SRC/.claude/$dir"/*."$ext" | wc -l | tr -d ' ')"
  for inst in install.sh install.ps1; do
    want="$(grep -oE "$dir: .*\(expect [0-9]+\)" "$SRC/$inst" | grep -oE '[0-9]+\)$' | tr -d ')')"
    [ "$want" = "$have" ] && ok "$inst expects $have $dir" || fail "$inst expects '${want:-?}' $dir, template has $have"
  done
done

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
T="$TMP/repo"; mkdir "$T"

# Fresh install: .claude/ arrives byte for byte, CLAUDE.md is the snippet.
out="$(bash "$SRC/install.sh" "$T" 2>&1)" || fail "install.sh exited non-zero: $out"
diff -r "$SRC/.claude" "$T/.claude" >/dev/null && ok "fresh install: .claude/ identical to the template" \
  || fail "fresh install: .claude/ differs from the template: $(diff -rq "$SRC/.claude" "$T/.claude" | head -5)"
cmp -s "$SRC/CLAUDE.factory-snippet.md" "$T/CLAUDE.md" && ok "fresh install: CLAUDE.md is the snippet" || fail "fresh install: CLAUDE.md is not the snippet"
grep -q MISSING <<<"$out" && fail "installer reports a MISSING contract file" || ok "installer reports every contract file"
for f in "$T"/.claude/hooks/*.sh; do [ -x "$f" ] || fail "installed hook not executable: ${f#"$T/"}"; done
for x in tests .github CHANGES.md; do [ -e "$T/$x" ] && fail "$x was installed into the target repo"; done
ok "template-only files (tests/, .github/, CHANGES.md) not installed"

# Reinstall: the repo keeps MEMORY.md and its own settings keys; hooks become the template's.
echo "- [2026-01-01 smoke] keep me" >> "$T/.claude/factory/MEMORY.md"
cat > "$T/.claude/settings.json" <<'EOF'
{ "permissions": { "allow": ["Bash(ls)"] }, "env": { "SMOKE": "1" }, "hooks": { "Stop": [] } }
EOF
out="$(bash "$SRC/install.sh" "$T" 2>&1)" || fail "reinstall exited non-zero: $out"
grep -q "keep me" "$T/.claude/factory/MEMORY.md" && ok "reinstall: MEMORY.md kept" || fail "reinstall: MEMORY.md overwritten"
if command -v jq >/dev/null 2>&1; then
  jq -e '.permissions.allow == ["Bash(ls)"] and .env.SMOKE == "1"' "$T/.claude/settings.json" >/dev/null \
    && ok "reinstall: settings.json keeps the repo's keys" || fail "reinstall: settings.json lost the repo's keys"
  jq -e --slurpfile t "$SRC/.claude/settings.json" '.hooks == $t[0].hooks' "$T/.claude/settings.json" >/dev/null \
    && ok "reinstall: hooks replaced with the template's" || fail "reinstall: hooks are not the template's"
  [ -f "$T/.claude/settings.json.bak" ] && ok "reinstall: old settings saved to settings.json.bak" || fail "reinstall: no settings.json.bak"
else
  fail "jq not found: the settings.json merge cannot be checked (the template requires jq)"
fi

[ "$fails" -eq 0 ] && echo "install smoke test passed" || echo "$fails install check(s) failed"
[ "$fails" -eq 0 ]
