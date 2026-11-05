#!/usr/bin/env python3
"""
Regression tests for .claude/factory/comment-migrate.py.

Each case in cases/manifest.json is a small anonymized file that reproduces a bug seen
on a real repo (see the "why" field). For every case the runner checks:

- rewrite:     --apply turns the input into the expected file (or leaves it unchanged)
- idempotence: running --apply again on the result changes nothing
- --check:     the exit code on the untouched input
- review:      the number of blocks sent to human review (when the case sets it)
- report:      a phrase the report must contain (when the case sets it)

These fixtures are permanent: the bugs they cover were fixed once (55f2256) and lost
again two days later (cd510f7) because nothing re-ran them.

Usage: python3 tests/comment-migrate/run.py [--script PATH]
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
DEFAULT_SCRIPT = REPO / ".claude" / "factory" / "comment-migrate.py"
REVIEW_RE = re.compile(r"(\d+) block\(s\) need human review")


def run(script: Path, cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-I", str(script), *args],
                          cwd=cwd, capture_output=True, text=True, encoding="utf-8")


def review_count(stdout: str) -> int | None:
    m = REVIEW_RE.search(stdout)
    return int(m.group(1)) if m else None


def check_case(script: Path, name: str, spec: dict) -> list[str]:
    problems: list[str] = []
    src = HERE / "cases" / name
    expected = (HERE / "cases" / spec["expected"]).read_bytes() if "expected" in spec else src.read_bytes()

    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        # Each case runs as `case.py` in its own folder so file names cannot matter.
        target = work / "case.py"
        shutil.copyfile(src, target)

        chk = run(script, work, "case.py", "--check", "--report", "report-check.md")
        if "check" in spec and chk.returncode != spec["check"]:
            problems.append(f"--check exit {chk.returncode}, expected {spec['check']}")

        app = run(script, work, "case.py", "--apply", "--force", "--report", "report.md")
        if app.returncode not in (0, 1):
            problems.append(f"--apply crashed (exit {app.returncode}): {app.stderr.strip()[-300:]}")
            return problems
        got = target.read_bytes()
        if got != expected:
            problems.append("rewrite differs from the expected file:\n" + unified(expected, got))

        if "review" in spec:
            n = review_count(app.stdout)
            if n != spec["review"]:
                problems.append(f"{n} block(s) sent to review, expected {spec['review']}")

        if "report_contains" in spec:
            report = (work / "report.md").read_text(encoding="utf-8") if (work / "report.md").exists() else ""
            if spec["report_contains"] not in report:
                problems.append(f"report does not mention {spec['report_contains']!r}")

        again = run(script, work, "case.py", "--apply", "--force", "--report", "report2.md")
        if target.read_bytes() != got:
            problems.append("not idempotent: a second --apply changed the file again:\n"
                            + unified(got, target.read_bytes()))
        elif "Would rewrite 0" not in again.stdout and "Rewrote 0" not in again.stdout:
            problems.append("second --apply reported changes: " + again.stdout.splitlines()[1])
    return problems


def unified(a: bytes, b: bytes) -> str:
    import difflib
    return "".join(difflib.unified_diff(
        a.decode("utf-8").splitlines(True), b.decode("utf-8").splitlines(True),
        "expected", "got", n=2))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--script", type=Path, default=DEFAULT_SCRIPT)
    ap.add_argument("-k", default="", help="only run cases whose name contains this text")
    args = ap.parse_args()

    manifest = json.loads((HERE / "cases" / "manifest.json").read_text(encoding="utf-8"))
    failed = 0
    for name, spec in manifest.items():
        if args.k not in name:
            continue
        problems = check_case(args.script.resolve(), name, spec)
        if problems:
            failed += 1
            print(f"FAIL {name} — {spec['why']}")
            for p in problems:
                print("     " + p.replace("\n", "\n     "))
        else:
            print(f"ok   {name}")
    total = sum(1 for n in manifest if args.k in n)
    print(f"\n{total - failed}/{total} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
