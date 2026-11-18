#!/usr/bin/env bash
# Hook smoke test (template repo only; not installed). Runs the same cases against
# scope-track.sh, protect-secrets.sh and quality-gate.sh twice:
#   native  - this machine as is (the Linux CI runner);
#   windows - a simulated Git Bash: uname says MINGW64, jq ends each -r line with CRLF
#             (native jq.exe), git reports the root as C:/x/repo, and Claude passes
#             backslash paths such as C:\x\repo\src\a.ts.
# Then checks that a Windows checkout (core.autocrlf=true) of an installed repo keeps the
# hook scripts LF. Usage: bash tests/hooks-smoke.sh
set -uo pipefail
TPL="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
fails=0
ok()   { echo "  ok    $*"; }
bad()  { echo "  FAIL  $*"; fails=$((fails + 1)); }

# --- a target repo with the hooks and a manifest -----------------------------------
REPO="$WORK/repo"
mkdir -p "$REPO/.claude/factory" "$REPO/src"
cp -R "$TPL/.claude/hooks" "$REPO/.claude/"
cat > "$REPO/.claude/factory/project.json" <<'EOF'
{
  "artifactsDir": ".claude/factory",
  "testDirs": ["tests"],
  "tracks": {
    "backend":  { "enabled": true, "dirs": ["src"], "protectedDirs": ["node_modules"],
                  "commands": { "test": "echo ran > gate-ran.txt" } },
    "frontend": { "enabled": false, "dirs": ["web"] }
  }
}
EOF
git -C "$REPO" init -q

# --- the simulated Windows environment ----------------------------------------------
# The hooks run with cwd $WORK/win, where the relative path C:/x/repo resolves to $REPO.
SHIM="$WORK/shim"
mkdir -p "$SHIM" "$WORK/win/C:/x" "$REPO/C:/x"
ln -s "$REPO" "$WORK/win/C:/x/repo"
# quality-gate.sh cds into the root and then reads C:/x/repo/... again; on Windows that
# path is absolute, here it is relative, so it must also resolve from inside the repo.
ln -s "$REPO" "$REPO/C:/x/repo"
REALJQ="$(command -v jq)"; REALGIT="$(command -v git)"
printf '#!/bin/sh\necho MINGW64_NT-10.0-26100\n' > "$SHIM/uname"
printf '#!/bin/bash\n"%s" "$@" | sed '\''s/$/\\r/'\''; exit "${PIPESTATUS[0]}"\n' "$REALJQ" > "$SHIM/jq"
printf '#!/bin/bash\n[ "$1 $2" = "rev-parse --show-toplevel" ] && { echo "C:/x/repo"; exit 0; }\nexec "%s" "$@"\n' "$REALGIT" > "$SHIM/git"
chmod +x "$SHIM"/*

MODE=""
path() {   # path <repo-relative path> -> what Claude would pass in this mode
  if [ "$MODE" = windows ]; then printf 'C:\\x\\repo\\%s' "${1//\//\\}"; else printf '%s/%s' "$REPO" "$1"; fi
}
run_hook() {   # run_hook <script> <json>; prints the exit code
  if [ "$MODE" = windows ]; then
    ( cd "$WORK/win" && printf '%s' "$2" | PATH="$SHIM:$PATH" CLAUDE_PROJECT_DIR='C:\x\repo' \
        bash "$REPO/.claude/hooks/$1" >/dev/null 2>&1 ); echo $?
  else
    ( cd "$REPO" && printf '%s' "$2" | CLAUDE_PROJECT_DIR="$REPO" \
        bash "$REPO/.claude/hooks/$1" >/dev/null 2>&1 ); echo $?
  fi
}
write_json() { jq -cn --arg t "$1" --arg p "$2" '{tool_name: $t, tool_input: {file_path: $p}}'; }
bash_json()  { jq -cn --arg c "$1" '{tool_name: "Bash", tool_input: {command: $c}}'; }
expect() {   # expect <want exit> <label> <script> <json>
  local got; got="$(run_hook "$3" "$4")"
  if [ "$got" = "$1" ]; then ok "[$MODE] $2 -> $got"; else bad "[$MODE] $2: exit $got, want $1"; fi
}
active() { if [ -n "$1" ]; then printf '%b' "$1" > "$REPO/.claude/factory/.active"; else rm -f "$REPO/.claude/factory/.active"; fi; }

for MODE in native windows; do
  echo "=== $MODE"
  active 'backend demo\n'
  expect 0 "scope-track: backend writes src/a.ts"                scope-track.sh "$(write_json Write "$(path src/a.ts)")"
  expect 0 "scope-track: backend writes its artifact"            scope-track.sh "$(write_json Write "$(path .claude/factory/demo/brief.md)")"
  expect 2 "scope-track: backend writes web/x.ts"                scope-track.sh "$(write_json Write "$(path web/x.ts)")"
  active 'backend demo\r\n'
  expect 0 "scope-track: CRLF .active, src/a.ts"                 scope-track.sh "$(write_json Write "$(path src/a.ts)")"
  active ''
  expect 2 "scope-track: no step, protected node_modules/x.js"   scope-track.sh "$(write_json Write "$(path node_modules/x.js)")"
  expect 0 "scope-track: no step, README.md"                     scope-track.sh "$(write_json Write "$(path README.md)")"

  expect 2 "protect-secrets: Write .env"                         protect-secrets.sh "$(write_json Write "$(path .env)")"
  expect 2 "protect-secrets: Write config/secrets.json"          protect-secrets.sh "$(write_json Write "$(path config/secrets.json)")"
  expect 2 "protect-secrets: Write certs/a.pem"                  protect-secrets.sh "$(write_json Write "$(path certs/a.pem)")"
  expect 0 "protect-secrets: Write src/a.ts"                     protect-secrets.sh "$(write_json Write "$(path src/a.ts)")"
  expect 2 "protect-secrets: Bash git add .env"                  protect-secrets.sh "$(bash_json 'git add .env')"
  expect 0 "protect-secrets: Bash git status"                    protect-secrets.sh "$(bash_json 'git status')"

  rm -f "$REPO/gate-ran.txt"
  run_hook quality-gate.sh '' >/dev/null
  if [ -f "$REPO/gate-ran.txt" ]; then ok "[$MODE] quality-gate runs the enabled track's command"
  else bad "[$MODE] quality-gate skipped the enabled backend track"; fi
done

# Case: NTFS ignores it, Linux does not. Each platform keeps its own rule.
active 'backend demo\n'
MODE=native
expect 2 "scope-track: SRC/a.ts is not src/ (case-sensitive)"   scope-track.sh "$(write_json Write "$REPO/SRC/a.ts")"
MODE=windows
expect 0 "scope-track: c:\\X\\Repo\\SRC\\a.ts is in src/"        scope-track.sh "$(write_json Write 'c:\X\Repo\SRC\a.ts')"
expect 0 "scope-track: /c/x/repo/src/a.ts (MSYS form)"           scope-track.sh "$(write_json Write '/c/x/repo/src/a.ts')"
active ''

# --- a Windows checkout of an installed repo keeps the hooks LF -----------------------
echo "=== windows checkout (core.autocrlf=true)"
TGT="$WORK/target"; mkdir -p "$TGT"; git -C "$TGT" init -q
bash "$TPL/install.sh" "$TGT" >/dev/null 2>&1 || bad "install.sh failed"
git -C "$TGT" add -A
git -C "$TGT" -c user.name=t -c user.email=t@t -c core.autocrlf=true commit -qm install
git -c core.autocrlf=true clone -q "$TGT" "$WORK/checkout"
crlf=0
for f in "$WORK/checkout/.claude/hooks/"*.sh; do
  if grep -q $'\r' "$f"; then bad "$(basename "$f") checked out with CRLF"; crlf=1; fi
done
[ "$crlf" -eq 0 ] && ok "hook scripts stay LF"

echo
if [ "$fails" -eq 0 ]; then echo "hooks smoke test passed"; else echo "hooks smoke test: $fails failure(s)"; exit 1; fi
