#!/usr/bin/env bash
# Every template-repo check, in one entry for CI and local runs (template repo only;
# not installed). Runs all checks, then exits 1 if any failed.
# Usage: bash tests/run-all.sh
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
failed=()

run() {
  local name="$1"; shift
  echo; echo "=== $name"
  if "$@"; then echo "--- PASS $name"; else echo "--- FAIL $name"; failed+=("$name"); fi
}

shell_syntax() {
  local rc=0 f
  while IFS= read -r f; do bash -n "$f" || { echo "FAIL $f"; rc=1; }; done \
    < <(find . -name '*.sh' -not -path './.git/*' -not -path '*/cases/*' | sort)
  [ "$rc" -eq 0 ] && echo "every .sh parses"
  return "$rc"
}

# compile() without writing __pycache__ (install.sh would copy one out of .claude/factory).
python_syntax() {
  find . -name '*.py' -not -path './.git/*' -not -path '*/cases/*' -print0 | sort -z |
    xargs -0 python3 -I -c '
import sys
bad = 0
for f in sys.argv[1:]:
    try:
        compile(open(f, "rb").read(), f, "exec")
    except SyntaxError as e:
        print(f"FAIL {f}: {e}"); bad = 1
print("every .py compiles" if not bad else "")
sys.exit(bad)'
}

run "cross-references"            python3 -I tests/check-refs.py
run "cross-reference self-test"   python3 -I tests/check-refs.py --self-test
run "comment-migrate fixtures"    python3 -I tests/comment-migrate/run.py
run "shell syntax"                shell_syntax
run "python syntax"               python_syntax
run "install.sh smoke test"       bash tests/install-smoke.sh

echo
if [ "${#failed[@]}" -eq 0 ]; then
  echo "All template checks passed."
else
  echo "Failed: ${failed[*]}"
  exit 1
fi
