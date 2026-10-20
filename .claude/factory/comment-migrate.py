#!/usr/bin/env python3
"""
comment-migrate.py — convert legacy line-interleaved bilingual comments into the
block-after-block form required by .claude/factory/terminology-zh-tw.md.

Before (legacy, interleaved):        After (block-after-block):
    // Reject the request.               // Reject the request.
    // 拒絕該請求。                       // This is the last line of defence.
    // This is the last line of defence. //
    // 這是最後一道防線。                  // 拒絕該請求。
                                         // 這是最後一道防線。

The tool NEVER translates and NEVER rewords. It only reorders whole comment lines
within a single comment block and inserts one separator line. Anything it is not
certain about is left untouched and listed in the report for a human to handle.

Dry-run by default. See --help.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# Comment syntax table
# ---------------------------------------------------------------------------
# Tokens are tried longest-first, so `///` wins over `//`.
LINE_TOKENS: dict[str, tuple[str, ...]] = {
    "slash": ("///", "//!", "//"),
    "hash": ("#!", "##", "#"),
    "dash": ("---", "--"),
    "semi": (";;;", ";;", ";"),
    "percent": ("%%", "%"),
}

EXT_STYLE: dict[str, str] = {}
for _exts, _style in [
    ((".c .h .cpp .cxx .cc .hpp .hxx .cs .java .js .jsx .mjs .cjs .ts .tsx .go .rs "
      ".swift .kt .kts .scala .php .m .mm .dart .proto .gradle .groovy .zig .sol"), "slash"),
    ((".py .rb .sh .bash .zsh .ps1 .psm1 .yml .yaml .toml .tf .tfvars .r .pl .pm "
      ".mk .cmake .nix .ex .exs .jl"), "hash"),
    (".sql .lua .hs .adb .ads .elm", "dash"),
    (".lisp .clj .cljs .el .asm .s .ini .cfg", "semi"),
    (".tex .erl .m4", "percent"),
]:
    for _e in _exts.split():
        EXT_STYLE[_e] = _style

BASENAME_STYLE = {
    "Makefile": "hash", "makefile": "hash", "Dockerfile": "hash",
    "Justfile": "hash", "justfile": "hash", "Rakefile": "hash",
}

# Languages whose block comments use ` * ` continuation lines (JSDoc / Javadoc / Doxygen).
STAR_BLOCK_STYLES = {"slash"}

SKIP_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "vendor", "third_party", "Pods",
    "dist", "build", "out", "target", "bin", "obj", "coverage", "__pycache__",
    ".venv", "venv", "env", ".next", ".nuxt", ".svelte-kit", ".terraform",
    ".mypy_cache", ".pytest_cache", ".gradle", ".idea", ".vscode",
}

MAX_BYTES = 2 * 1024 * 1024  # skip anything bigger; it is not hand-written source

# ---------------------------------------------------------------------------
# Language classification
# ---------------------------------------------------------------------------
CJK_RE = re.compile(
    r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\U00020000-\U0002ebef]"
)
LATIN_RE = re.compile(r"[A-Za-z]")

# Strong signals that a "comment" line is really commented-out code, not prose.
CODE_RE = re.compile(
    r"""(
        [;{}]\s*$                                   # ends in ; { }
      | =>|->|::|\+\+|&&|\|\|                       # operator soup
      | ^\s*(?:import|from|export|const|let|var|def|class|func|function|
             public|private|protected|return|if|for|while|switch|case|
             print|echo|console\.|System\.|package|use|require)\b
      | ^\s*[\w$@]+(?:\.[\w$]+)*\s*\([^)]*\)\s*[;,)]?\s*$   # a bare call expression
      | ^\s*[\w$]+(?:\.[\w$]+|\[[^\]]*\])*\s*(?:=|\+=|-=|:=)\s*\S  # an assignment
      | ^\s*</?[a-zA-Z][\w.-]*[\s/>]                # markup tag
    )""",
    re.VERBOSE,
)


def classify(text: str) -> str:
    """Classify one comment line's content: 'zh', 'en', or 'blank'."""
    t = text.strip()
    if not t:
        return "blank"
    if CJK_RE.search(t):
        return "zh"
    if LATIN_RE.search(t):
        return "en"
    return "blank"  # separators like ----- or ===== act as paragraph breaks


def looks_like_code(text: str) -> bool:
    return bool(CODE_RE.search(text.strip()))


def is_mixed(text: str) -> bool:
    """One line holding substantial English AND Chinese (a short identifier does not count)."""
    return bool(CJK_RE.search(text)) and len(LATIN_RE.findall(text)) > 25


# A Chinese sentence ending in full-width punctuation, then an English-only tail.
ZH_THEN_EN_RE = re.compile(r"^(.*[。！？；])\s*([`A-Za-z][^㐀-鿿豈-﫿]*)$")
# An English-only head ending a sentence, then a tail that opens with Chinese
# (directly, or after one `identifier`).
EN_THEN_ZH_RE = re.compile(
    r"^([^㐀-鿿豈-﫿]*[.!?:;])\s+((?:`[^`]+`\s*)?[㐀-鿿豈-﫿].*)$"
)


def split_mixed(line: str, content: str) -> list[tuple[str, str]] | None:
    """
    Split one mixed-language comment line at its single sentence boundary into two
    lines that share the original prefix (indent, comment token, leading space).
    The tail starts its OWN new line: it is never joined onto a neighbouring line,
    and no other line is re-wrapped. Text is kept word for word; only a line break
    is inserted. Returns [(line, content), (line, content)] or None if the boundary
    is not unambiguous (the caller then sends the block to human review).
    """
    body = line.rstrip()
    core = content.rstrip()
    if not body.endswith(core):
        return None
    prefix = body[: len(body) - len(core)]
    lead = core[: len(core) - len(core.lstrip())]
    text = core.lstrip()
    m = ZH_THEN_EN_RE.match(text) or EN_THEN_ZH_RE.match(text)
    if not m:
        return None
    head, tail = m.group(1).rstrip(), m.group(2).strip()
    parts = [lead + head, lead + tail]
    if {classify(parts[0]), classify(parts[1])} != {"zh", "en"}:
        return None
    if any(is_mixed(p) for p in parts):
        return None
    return [(prefix + p, p) for p in parts]


# ---------------------------------------------------------------------------
# Findings
# ---------------------------------------------------------------------------
@dataclass
class Finding:
    path: str
    line: int          # 1-based line number of the run's first line
    kind: str          # 'migrated' | 'reordered' | 'review'
    reason: str = ""
    sample: list[str] = field(default_factory=list)


@dataclass
class Stats:
    files_scanned: int = 0
    files_changed: int = 0
    migrated: int = 0
    reordered: int = 0
    review: int = 0


# ---------------------------------------------------------------------------
# Core: regroup one run of comment content lines
# ---------------------------------------------------------------------------
def regroup(lines: list[str], contents: list[str]) -> tuple[list[str] | None, str, str]:
    """
    Given the original full lines of ONE paragraph (no blank comment lines inside)
    and their comment-content parts, decide what to do.

    Returns (new_lines_or_None, kind, reason).
    kind is 'migrated' | 'reordered' | 'review' | 'clean'.
    """
    # A mixed line that splits cleanly at one sentence boundary becomes two lines first;
    # one that does not is left as-is and trips the mixed-line review below.
    expanded: list[tuple[str, str]] = []
    for ln, c in zip(lines, contents):
        halves = split_mixed(ln, c) if is_mixed(c) else None
        expanded.extend(halves or [(ln, c)])
    was_split = len(expanded) != len(lines)
    lines = [ln for ln, _ in expanded]
    contents = [c for _, c in expanded]

    kinds = [classify(c) for c in contents]
    if "zh" not in kinds or "en" not in kinds:
        return None, "clean", ""

    switches = sum(1 for a, b in zip(kinds, kinds[1:]) if a != b)

    if switches < 1:
        return None, "clean", ""

    # A two-line EN→ZH pair is already the compliant degenerate case
    # (once split, it still needs writing back as two lines).
    if switches == 1 and kinds[0] == "en":
        return (lines, "migrated", "") if was_split else (None, "clean", "")

    if any(looks_like_code(c) for c in contents):
        return None, "review", "contains commented-out code — reordering could break it"

    # A mixed line still here had no single clean sentence boundary, so the split
    # point is ambiguous; a human should look.
    for c in contents:
        if is_mixed(c):
            return None, "review", "a line mixes substantial English and Chinese"

    en = [ln for ln, k in zip(lines, kinds) if k == "en"]
    zh = [ln for ln, k in zip(lines, kinds) if k == "zh"]
    if not en or not zh:
        return None, "clean", ""

    kind = "reordered" if switches == 1 else "migrated"
    # One English line + one Chinese line needs no separator (the rule's degenerate case).
    if len(en) == 1 and len(zh) == 1:
        return en + zh, kind, ""
    return en + ["\0SEP\0"] + zh, kind, ""


def process_run(
    out: list[str],
    run: list[tuple[int, str, str]],
    separator: str,
    path: str,
    findings: list[Finding],
) -> bool:
    """
    Process one contiguous comment run. `run` is [(lineno, full_line, content), ...].
    Appends the (possibly rewritten) lines to `out`. Returns True if changed.
    """
    changed = False
    para: list[tuple[int, str, str]] = []

    def flush() -> None:
        nonlocal changed, para
        if not para:
            return
        lines = [p[1] for p in para]
        contents = [p[2] for p in para]
        new, kind, reason = regroup(lines, contents)
        if kind == "review":
            # The whole paragraph (capped), so the human sees both languages.
            findings.append(Finding(path, para[0][0], "review", reason,
                                    lines[:20]))
            out.extend(lines)
        elif new is not None:
            findings.append(Finding(path, para[0][0], kind))
            out.extend(separator if ln == "\0SEP\0" else ln for ln in new)
            changed = True
        else:
            out.extend(lines)
        para = []

    for item in run:
        if classify(item[2]) == "blank":
            flush()
            out.append(item[1])
        else:
            para.append(item)
    flush()
    return changed


# ---------------------------------------------------------------------------
# File-level scanning
# ---------------------------------------------------------------------------
def token_of(stripped: str, style: str) -> str | None:
    for tok in LINE_TOKENS[style]:
        if stripped.startswith(tok):
            return tok
    return None


# ---------------------------------------------------------------------------
# Verification, layer 1: nothing outside the comment regions changed, and inside
# them only whole lines moved (plus separators and mixed-line splits).
# ---------------------------------------------------------------------------
@dataclass
class Region:
    old_start: int   # [old_start, old_end) in the original lines
    old_end: int
    new_start: int   # [new_start, new_end) in the rewritten lines
    new_end: int
    separator: str   # the separator line this region may gain


def reject(findings: list[Finding], first: int, path: str, reason: str) -> None:
    """Replace a file's change findings with one review finding: the file is not written."""
    line = findings[first].line if len(findings) > first else 1
    sample = [s for f in findings[first:] for s in f.sample][:20]
    del findings[first:]
    findings.append(Finding(path, line, "review", reason, sample))


def _split_prefix(line: str, token: str) -> tuple[str, str]:
    """(prefix, text): the indent, comment token and spaces, then the stripped text."""
    body = line.rstrip()
    rest = body.lstrip()
    if token and rest.startswith(token):
        rest = rest[len(token):]
    text = rest.strip()
    return body[: len(body) - len(text)] if text else body, text


def verify_lines(old: list[str], new: list[str], regions: list[Region]) -> str | None:
    """Return None when the rewrite only moved comment lines, else what went wrong."""
    old_code: list[str] = []
    new_code: list[str] = []
    o = n = 0
    for r in regions:
        old_code += old[o:r.old_start]
        new_code += new[n:r.new_start]
        o, n = r.old_end, r.new_end
    old_code += old[o:]
    new_code += new[n:]
    if old_code != new_code:
        for a, b in zip(old_code, new_code):
            if a != b:
                return f"a code line changed: {a.strip()[:60]!r}"
        return "the number of code lines changed"

    for r in regions:
        token = r.separator.strip()
        before = old[r.old_start:r.old_end]
        after = new[r.new_start:r.new_end]
        prefixes = {_split_prefix(ln, token)[0] for ln in before}
        left_old = list(before)
        left_new: list[str] = []
        for ln in after:
            if ln in left_old:
                left_old.remove(ln)
            else:
                left_new.append(ln)
        # Whatever was not moved as-is must be a mixed line split into two pieces.
        for ln in left_old:
            want = "".join(_split_prefix(ln, token)[1].split())
            pair: tuple[int, int] | None = None
            for ia, a in enumerate(left_new):
                for ib, b in enumerate(left_new):
                    if ia == ib:
                        continue
                    (pa, ta), (pb, tb) = _split_prefix(a, token), _split_prefix(b, token)
                    if "".join((ta + tb).split()) == want and pa in prefixes and pb in prefixes:
                        pair = (ia, ib)
                        break
                if pair:
                    break
            if pair is None:
                return f"a comment line was lost or altered: {ln.strip()[:60]!r}"
            for idx in sorted(pair, reverse=True):
                del left_new[idx]
        for ln in left_new:
            if ln.rstrip() != r.separator.rstrip():
                return f"an unexpected comment line appeared: {ln.strip()[:60]!r}"
    return None


DOCSTRING_OPEN = re.compile(r'^(\s*)(?:[rRbBuUfF]{0,2})("""|\'\'\')\s*$')


def scan_file(path: Path, style: str, findings: list[Finding]) -> tuple[str, bool] | None:
    try:
        raw = path.read_bytes()
    except OSError:
        return None
    if len(raw) > MAX_BYTES or b"\0" in raw:
        return None
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return None
    if not CJK_RE.search(text):
        return None  # nothing bilingual here

    # Split on the file's own line ending only. str.splitlines() would also split on
    # U+2028, \f and other characters that can sit inside a string literal, and
    # writing those lines back would break the code line in two.
    eol = "\r\n" if "\r\n" in text else "\n"
    leftover = text.replace("\r\n", "")
    mixed_eol = "\r" in leftover or (eol == "\r\n" and "\n" in leftover)
    trailing = text.endswith(eol)
    body = text[: -len(eol)] if trailing else text
    lines = body.split(eol) if body else []
    first_finding = len(findings)

    out: list[str] = []
    regions: list[Region] = []
    changed = False
    i = 0
    n = len(lines)
    is_python = path.suffix == ".py"

    while i < n:
        line = lines[i]
        stripped = line.strip()

        # --- Python docstring block -------------------------------------
        if is_python:
            m = DOCSTRING_OPEN.match(line)
            if m:
                indent, quote = m.group(1), m.group(2)
                j = i + 1
                while j < n and lines[j].strip() != quote:
                    j += 1
                if j < n:  # found the closer
                    body = [(k + 1, lines[k], lines[k]) for k in range(i + 1, j)]
                    out.append(line)
                    mark = len(out)
                    if process_run(out, body, "", str(path), findings):
                        changed = True
                    regions.append(Region(i + 1, j, mark, len(out), ""))
                    out.append(lines[j])
                    i = j + 1
                    continue

        # --- ` * ` continuation block (JSDoc / Javadoc / Doxygen) --------
        if style in STAR_BLOCK_STYLES and stripped.startswith("/*"):
            j = i
            while j < n and "*/" not in lines[j]:
                j += 1
            if j < n and j > i:
                body: list[tuple[int, str, str]] = []
                ok = True
                for k in range(i + 1, j):
                    s = lines[k].strip()
                    if not s.startswith("*"):
                        ok = False
                        break
                    body.append((k + 1, lines[k], s[1:]))
                if ok and body:
                    star_indent = lines[i + 1][: len(lines[i + 1]) - len(lines[i + 1].lstrip())]
                    out.append(lines[i])
                    mark = len(out)
                    if process_run(out, body, star_indent + "*", str(path), findings):
                        changed = True
                    regions.append(Region(i + 1, j, mark, len(out), star_indent + "*"))
                    out.append(lines[j])
                    i = j + 1
                    continue

        # --- run of line comments ---------------------------------------
        tok = token_of(stripped, style) if stripped else None
        if tok:
            indent = line[: len(line) - len(line.lstrip())]
            run: list[tuple[int, str, str]] = []
            j = i
            while j < n:
                s = lines[j].strip()
                t = token_of(s, style) if s else None
                ind = lines[j][: len(lines[j]) - len(lines[j].lstrip())]
                if t != tok or ind != indent:
                    break
                run.append((j + 1, lines[j], s[len(t):]))
                j += 1
            mark = len(out)
            if process_run(out, run, indent + tok, str(path), findings):
                changed = True
            regions.append(Region(i, j, mark, len(out), indent + tok))
            i = j
            continue

        out.append(line)
        i += 1

    if not changed:
        return None
    if mixed_eol:
        # One line ending cannot be chosen for the rewritten lines without changing
        # some line's ending, so the file is left for a human.
        reject(findings, first_finding, str(path),
               "mixed line endings — rewriting would change some of them")
        return None
    problem = verify_lines(lines, out, regions)
    if problem is not None:
        reject(findings, first_finding, str(path), f"verification failed (lines): {problem}")
        return None
    new_text = eol.join(out) + (eol if trailing else "")
    return new_text, True


# ---------------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------------
def style_for(path: Path) -> str | None:
    if path.name in BASENAME_STYLE:
        return BASENAME_STYLE[path.name]
    return EXT_STYLE.get(path.suffix)


def git_tracked(root: Path) -> list[Path] | None:
    try:
        r = subprocess.run(["git", "-C", str(root), "ls-files", "-z"],
                           capture_output=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    return [root / p for p in r.stdout.decode("utf-8", "replace").split("\0") if p]


def walk(root: Path) -> list[Path]:
    found: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in filenames:
            found.append(Path(dirpath) / f)
    return found


def discover(targets: list[Path]) -> list[Path]:
    files: list[Path] = []
    for t in targets:
        if t.is_file():
            files.append(t)
            continue
        tracked = git_tracked(t)
        cand = tracked if tracked is not None else walk(t)
        for p in cand:
            if any(part in SKIP_DIRS for part in p.parts):
                continue
            if p.is_file():
                files.append(p)
    seen, uniq = set(), []
    for p in files:
        rp = p.resolve()
        if rp not in seen:
            seen.add(rp)
            uniq.append(p)
    return uniq


def git_dirty(root: Path, ignore: Path | None = None) -> bool:
    """
    True if the working tree has changes the user should commit first.
    The tool's own report is excluded — a dry run writes it, and that must not block
    the --apply that follows.
    """
    try:
        r = subprocess.run(["git", "-C", str(root), "status", "--porcelain", "-z"],
                           capture_output=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return False
    ignore_rp = ignore.resolve() if ignore else None
    for entry in r.stdout.decode("utf-8", "replace").split("\0"):
        if len(entry) < 4:
            continue
        path = entry[3:]
        if ignore_rp is not None and (root / path).resolve() == ignore_rp:
            continue
        return True
    return False


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
def write_report(path: Path, stats: Stats, findings: list[Finding], applied: bool) -> None:
    L = ["# Bilingual comment migration report", ""]
    L.append(f"Mode: **{'APPLIED' if applied else 'DRY RUN (no files written)'}**")
    L.append("")
    L.append("| Metric | Count |")
    L.append("|---|---|")
    L.append(f"| Files scanned | {stats.files_scanned} |")
    L.append(f"| Files changed | {stats.files_changed} |")
    L.append(f"| Blocks regrouped (interleaved → block) | {stats.migrated} |")
    L.append(f"| Pairs reordered (Chinese was first) | {stats.reordered} |")
    L.append(f"| Blocks needing human review | {stats.review} |")
    L.append("")

    changed = [f for f in findings if f.kind in ("migrated", "reordered")]
    if changed:
        L += ["## Changed blocks", ""]
        by_file: dict[str, list[Finding]] = {}
        for f in changed:
            by_file.setdefault(f.path, []).append(f)
        for fp, items in sorted(by_file.items()):
            locs = ", ".join(f"L{i.line}" for i in items)
            L.append(f"- `{fp}` — {len(items)} block(s): {locs}")
        L.append("")

    review = [f for f in findings if f.kind == "review"]
    if review:
        L += ["## Needs human review (NOT changed)", "",
              "These blocks are interleaved but the tool refused to reorder them.",
              "Fix them by hand, or hand this list to Claude one file at a time.", ""]
        for f in review:
            L.append(f"### `{f.path}` L{f.line}")
            L.append(f"Reason: {f.reason}")
            L.append("```")
            L.extend(f.sample)
            L.append("```")
            L.append("")
    L.append("")
    path.write_text("\n".join(L), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(
        description="Convert line-interleaved bilingual comments to block-after-block form.")
    ap.add_argument("paths", nargs="*", default=["."],
                    help="files or directories to scan (default: current directory)")
    ap.add_argument("--apply", action="store_true",
                    help="write the changes (default is a dry run)")
    ap.add_argument("--force", action="store_true",
                    help="allow --apply even when the git working tree is dirty")
    ap.add_argument("--check", action="store_true",
                    help="CI mode: exit 1 if any interleaved comment block is found")
    ap.add_argument("--report", default=".claude/factory/comment-migration-report.md",
                    help="where to write the markdown report")
    ap.add_argument("--ext", default="",
                    help="comma-separated extension allow-list, e.g. .ts,.tsx,.py")
    args = ap.parse_args()

    targets = [Path(p) for p in (args.paths or ["."])]
    for t in targets:
        if not t.exists():
            print(f"ERROR: {t} does not exist", file=sys.stderr)
            return 1

    root = Path(".").resolve()
    report = Path(args.report)
    if args.apply and not args.force and git_dirty(root, report):
        print("ERROR: git working tree is dirty.", file=sys.stderr)
        print("Commit or stash first so this migration lands as one reviewable diff,",
              file=sys.stderr)
        print("or re-run with --force if you know what you are doing.", file=sys.stderr)
        return 1

    allow = {e.strip() for e in args.ext.split(",") if e.strip()}
    stats, findings = Stats(), []

    for p in discover(targets):
        style = style_for(p)
        if style is None:
            continue
        if allow and p.suffix not in allow:
            continue
        stats.files_scanned += 1
        before = len(findings)
        result = scan_file(p, style, findings)
        new_findings = findings[before:]
        stats.migrated += sum(1 for f in new_findings if f.kind == "migrated")
        stats.reordered += sum(1 for f in new_findings if f.kind == "reordered")
        stats.review += sum(1 for f in new_findings if f.kind == "review")
        if result is not None:
            stats.files_changed += 1
            new_text, _ = result
            if args.apply:
                # Bytes, not text mode: text mode on Windows turns every "\n" into
                # "\r\n", so CRLF files would gain "\r\r\n" and LF files become CRLF.
                p.write_bytes(new_text.encode("utf-8"))

    report.parent.mkdir(parents=True, exist_ok=True)
    write_report(report, stats, findings, args.apply)

    verb = "Rewrote" if args.apply else "Would rewrite"
    print(f"Scanned {stats.files_scanned} file(s).")
    print(f"{verb} {stats.files_changed} file(s): "
          f"{stats.migrated} block(s) regrouped, {stats.reordered} pair(s) reordered.")
    print(f"{stats.review} block(s) need human review.")
    print(f"Report: {report}")
    if not args.apply and stats.files_changed:
        print("Dry run — nothing was written. Re-run with --apply to commit the change.")

    if args.check and (stats.migrated or stats.reordered or stats.review):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
