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
        # Each case runs as `case<ext>` in its own folder so file names cannot matter.
        fname = "case" + src.suffix
        target = work / fname
        shutil.copyfile(src, target)

        chk = run(script, work, fname, "--check", "--report", "report-check.md")
        if "check" in spec and chk.returncode != spec["check"]:
            problems.append(f"--check exit {chk.returncode}, expected {spec['check']}")

        app = run(script, work, fname, "--apply", "--force", "--report", "report.md")
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

        again = run(script, work, fname, "--apply", "--force", "--report", "report2.md")
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


def unit_checks(script: Path) -> list[tuple[str, str | None]]:
    """
    Direct checks of the safety net. The scanner itself no longer produces these bad
    rewrites, so the cases above cannot prove the net would catch one; these feed
    known-bad rewrites straight to the signature functions.
    Returns [(name, problem_or_None)].
    """
    import importlib.util
    sys.dont_write_bytecode = True  # never leave __pycache__ in .claude/factory (install.sh copies it)
    spec = importlib.util.spec_from_file_location("comment_migrate", script)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod  # dataclasses look their module up here while loading
    try:
        spec.loader.exec_module(mod)
    except Exception as exc:  # noqa: BLE001 — report any import failure as a test failure
        return [("import the script", f"{type(exc).__name__}: {exc}")]
    if not hasattr(mod, "python_signature") or not hasattr(mod, "generic_signature"):
        return [("signature functions exist", "python_signature / generic_signature missing")]

    results: list[tuple[str, str | None]] = []

    def expect(name: str, cond: bool, why: str) -> None:
        results.append((name, None if cond else why))

    py_old = ("def f(x):\n    # The first check.\n    # 第一個檢查。\n"
              "    assert x\n    assert not x\n")
    py_moved = ("def f(x):\n    # The first check.\n    assert x\n"
                "    # 第一個檢查。\n    assert not x\n")
    py_same = ("def f(x):\n    # 第一個檢查。\n    # The first check.\n"
               "    assert x\n    assert not x\n")
    try:
        expect("B8 python: a comment moved past code is caught",
               mod.python_signature(py_old) != mod.python_signature(py_moved),
               "python_signature did not notice the comment moving below an assert")
        expect("B8 python: reordering inside one block is allowed",
               mod.python_signature(py_old) == mod.python_signature(py_same),
               "python_signature rejected a reorder that stays above the same code")
    except Exception as exc:  # noqa: BLE001 — an old signature shape is a failure, not a crash
        results.append(("B8 python", f"signature call failed: {exc}"))

    cs_old = ["void F() {", "    // The first check.", "    // 第一個檢查。",
              "    Check(a);", "    Check(b);", "}"]
    cs_moved = ["void F() {", "    // The first check.", "    Check(a);",
                "    // 第一個檢查。", "    Check(b);", "}"]
    try:
        expect("B8 generic: a comment moved past code is caught",
               mod.generic_signature(cs_old, "slash") != mod.generic_signature(cs_moved, "slash"),
               "generic_signature did not notice the comment moving below a code line")
    except Exception as exc:  # noqa: BLE001 — an old signature shape is a failure, not a crash
        results.append(("B8 generic", f"signature call failed: {exc}"))

    if hasattr(mod, "Split"):
        try:
            orig = "# The cache never expires. 此快取永不過期。"
            halves = ("# The cache never expires.", "# 此快取永不過期。")
            old = f"def f():\n    {orig}\n    return 1\n"
            new = f"def f():\n    {halves[0]}\n    {halves[1]}\n    return 1\n"
            split = mod.Split(orig, halves)
            expect("split: a recorded mixed-line split passes the check",
                   mod.python_signature(old) == mod.python_signature(new, [split]),
                   "python_signature rejected a recorded split")
            expect("split: an unrecorded split is caught",
                   mod.python_signature(old) != mod.python_signature(new),
                   "python_signature accepted a split nobody recorded")
        except Exception as exc:  # noqa: BLE001
            results.append(("split", f"signature call failed: {exc}"))
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--script", type=Path, default=DEFAULT_SCRIPT)
    ap.add_argument("-k", default="", help="only run cases whose name contains this text")
    args = ap.parse_args()

    failed = 0
    units = unit_checks(args.script.resolve()) if not args.k else []
    for name, problem in units:
        if problem:
            failed += 1
            print(f"FAIL [unit] {name} — {problem}")
        else:
            print(f"ok   [unit] {name}")

    manifest = json.loads((HERE / "cases" / "manifest.json").read_text(encoding="utf-8"))
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
    total = sum(1 for n in manifest if args.k in n) + len(units)
    print(f"\n{total - failed}/{total} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
