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

Safety guarantees:
- A comment run ends at the first line that is not a pure comment line.
- Python files are read with `tokenize` + `ast`: only real `#` comment lines and real
  docstrings are candidates. Triple-quoted strings that are not docstrings (SQL, test
  data) and string literals containing Chinese are never touched.
- Wrapped lines stay with the sentence they continue: a Chinese sentence that wraps
  onto a code-only line keeps that line in the Chinese block.
- Multi-line English followed directly by Chinese (no separator) is flagged, not fixed.
- Before writing, every rewritten file is re-checked. If anything other than the order
  of comment / docstring lines changed, the file is NOT written and is flagged.

Dry-run by default. See --help.
"""

from __future__ import annotations

import argparse
import ast
import io
import os
import re
import subprocess
import sys
import tokenize
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
# CJK ideographs PLUS CJK / full-width punctuation, so a line like
# "（COLUMN_NAME | …）。" counts as Chinese.
CJK_RE = re.compile(
    "["
    "\u3000-\u303f"                       # CJK punctuation: 、。「」『』
    "\u3100-\u312f"                       # Bopomofo
    "\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff"
    "\uff00-\uffef"                       # full-width forms: （）：，！？
    "\U00020000-\U0002ebef"
    "]"
)
LATIN_RE = re.compile(r"[A-Za-z]")

# A Chinese line ending in one of these has finished its sentence.
ZH_TERMINAL = ("。", "！", "？", "；", "：")

# A line made only of rule characters acts as a paragraph break.
SEPARATOR_RE = re.compile(r"[-=*~_#/+.\s]{3,}")

# Strong signals that a "comment" line is really commented-out code, not prose.
CODE_RE = re.compile(
    r"""(
        [;{}]\s*$                                   # ends in ; { }
      | =>|->|::|\+\+|&&|\|\|                       # operator soup
      | ^\s*(?:>>>|\.\.\.\s)                        # doctest prompt
      | ^\s*(?:import|from|export|const|let|var|def|class|func|function|
             public|private|protected|return|if|for|while|switch|case|
             print|echo|console\.|System\.|package|use|require|assert)\b
      | ^\s*[\w$@]+(?:\.[\w$]+)*\s*\([^)]*\)\s*[;,)]?\s*$   # a bare call expression
      | ^\s*[\w$]+(?:\.[\w$]+|\[[^\]]*\])*\s*(?:=|\+=|-=|:=)\s*\S  # an assignment
      | ^\s*</?[a-zA-Z][\w.-]*[\s/>]                # markup tag
    )""",
    re.VERBOSE,
)

_BACKTICK_RE = re.compile(r"`[^`]*`")
_PROSE_WORD_RE = re.compile(r"(?<![\w.])[A-Za-z][a-z]+(?![\w(])")


def prose_words(text: str) -> int:
    """Count ordinary English words, ignoring `code spans` and identifiers."""
    return len(_PROSE_WORD_RE.findall(_BACKTICK_RE.sub(" ", text)))


def classify_lines(contents: list[str]) -> list[str]:
    """
    Classify each comment line as 'zh', 'en', 'blank' or 'ambiguous', using the
    previous line as context so a wrapped sentence stays in one language:

    - any CJK character (including full-width punctuation) -> 'zh'
    - a line with no CJK that follows an unfinished Chinese sentence continues it
      -> 'zh', but only if it holds no English prose words at all (pure code,
      identifiers, symbols); any English word there -> 'ambiguous'
    - a line with no letters at all continues whatever came before it
    """
    kinds: list[str] = []
    prev_kind: str | None = None
    zh_open = False  # True while a Chinese sentence has not reached its terminal mark
    for c in contents:
        t = c.strip()
        if not t or SEPARATOR_RE.fullmatch(t):
            kinds.append("blank")
            prev_kind, zh_open = None, False
            continue
        if CJK_RE.search(t):
            k = "zh"
            zh_open = not t.endswith(ZH_TERMINAL)
        elif LATIN_RE.search(t):
            if prev_kind == "zh" and zh_open:
                k = "zh" if prose_words(t) == 0 else "ambiguous"
                # A code-only continuation may close the sentence with ASCII punctuation.
                zh_open = k == "zh" and not t.endswith((".", "!", "?", ";", ":"))
            else:
                k = "en"
                zh_open = False
        else:
            k = prev_kind or "blank"
        kinds.append(k)
        if k == "blank":
            prev_kind, zh_open = None, False
        else:
            prev_kind = k
    return kinds


def looks_like_code(text: str) -> bool:
    return bool(CODE_RE.search(text.strip()))


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
# Core: regroup one paragraph of comment content lines
# ---------------------------------------------------------------------------
SEP = "\0SEP\0"


def regroup(
    lines: list[str],
    contents: list[str],
    kinds: list[str],
    pin_first: bool = False,
    pin_last: bool = False,
) -> tuple[list[str] | None, str, str]:
    """
    Given the original full lines of ONE paragraph (no blank comment lines inside),
    their comment-content parts and their language kinds, decide what to do.

    pin_first / pin_last: that line physically carries a docstring's opening /
    closing quotes, so it must stay where it is.

    Returns (new_lines_or_None, kind, reason).
    kind is 'migrated' | 'reordered' | 'review' | 'clean'.
    """
    if "zh" not in kinds or ("en" not in kinds and "ambiguous" not in kinds):
        return None, "clean", ""

    if "ambiguous" in kinds:
        return None, "review", ("an English-looking line follows an unfinished Chinese "
                                "line — cannot tell a wrapped sentence from a new one")

    switches = sum(1 for a, b in zip(kinds, kinds[1:]) if a != b)
    n_en, n_zh = kinds.count("en"), kinds.count("zh")

    if switches == 1 and kinds[0] == "en":
        # English block, then Chinese block. One line each is the compliant
        # degenerate case; anything longer needs a separator the author must place.
        if n_en == 1 and n_zh == 1:
            return None, "clean", ""
        return None, "review", ("English block followed by Chinese block with no "
                                "separator — insert a bare comment line / blank "
                                "docstring line between them")

    if any(looks_like_code(c) for c in contents):
        return None, "review", "contains commented-out code — reordering could break it"

    # Mixed-language lines (one line holding both languages) mean the split point
    # is ambiguous; a human should look.
    for c in contents:
        if CJK_RE.search(c) and len(LATIN_RE.findall(c)) > 25:
            return None, "review", "a line mixes substantial English and Chinese"

    en = [ln for ln, k in zip(lines, kinds) if k == "en"]
    zh = [ln for ln, k in zip(lines, kinds) if k == "zh"]
    new = en + zh if (len(en) == 1 and len(zh) == 1) else en + [SEP] + zh

    if (pin_first and new[0] != lines[0]) or (pin_last and new[-1] != lines[-1]):
        return None, "review", ("text shares a line with the docstring quotes and "
                                "regrouping would move it — fix by hand")

    kind = "reordered" if switches == 1 else "migrated"
    return new, kind, ""


def process_run(
    out: list[str],
    run: list[tuple[int, str, str]],
    separator: str,
    path: str,
    findings: list[Finding],
    pin_first: bool = False,
    pin_last: bool = False,
) -> bool:
    """
    Process one contiguous comment run. `run` is [(lineno, full_line, content), ...]
    and must hold ONLY comment / docstring lines. Appends the (possibly rewritten)
    lines to `out`. Returns True if changed.
    """
    changed = False
    kinds_all = classify_lines([r[2] for r in run])
    para: list[int] = []  # indexes into run

    def flush() -> None:
        nonlocal changed, para
        if not para:
            return
        lines = [run[i][1] for i in para]
        contents = [run[i][2] for i in para]
        kinds = [kinds_all[i] for i in para]
        new, kind, reason = regroup(
            lines, contents, kinds,
            pin_first=pin_first and para[0] == 0,
            pin_last=pin_last and para[-1] == len(run) - 1,
        )
        if kind == "review":
            findings.append(Finding(path, run[para[0]][0], "review", reason, lines[:8]))
            out.extend(lines)
        elif new is not None:
            findings.append(Finding(path, run[para[0]][0], kind))
            out.extend(separator if ln == SEP else ln for ln in new)
            changed = True
        else:
            out.extend(lines)
        para = []

    for i, item in enumerate(run):
        if kinds_all[i] == "blank":
            flush()
            out.append(item[1])
        else:
            para.append(i)
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


STRING_OPEN_RE = re.compile(r'^[rRbBuUfF]{0,2}("""|\'\'\')')


def read_source(path: Path) -> str | None:
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
    return text


def join_lines(out: list[str], text: str) -> str:
    eol = "\r\n" if "\r\n" in text else "\n"
    trailing = text.endswith(("\n", "\r"))
    return eol.join(out) + (eol if trailing else "")


def run_of_line_comments(lines: list[str], i: int, style: str, is_comment_line):
    """
    Collect consecutive pure comment lines starting at i that share one token and
    one indent. The run ends at the FIRST line that is not a pure comment line.
    Returns (run, indent, token).
    """
    first = lines[i]
    indent = first[: len(first) - len(first.lstrip())]
    tok = token_of(first.strip(), style)
    run: list[tuple[int, str, str]] = []
    j = i
    while j < len(lines):
        ln = lines[j]
        s = ln.strip()
        if not s or not is_comment_line(j):
            break
        t = token_of(s, style)
        ind = ln[: len(ln) - len(ln.lstrip())]
        if t != tok or ind != indent:
            break
        run.append((j + 1, ln, s[len(t):]))
        j += 1
    return run, indent, tok


# ---- Python --------------------------------------------------------------------
def python_structure(text: str):
    """
    Return (comment_lines, docstrings) for Python source, or None if it does not parse.
    comment_lines: 0-based indexes of lines whose ONLY token is a COMMENT.
    docstrings: {start: (start, end)} 0-based inclusive, multi-line docstrings only.
    """
    try:
        tree = ast.parse(text)
        toks = list(tokenize.generate_tokens(io.StringIO(text).readline))
    except (SyntaxError, ValueError, tokenize.TokenError):
        return None

    skip = {tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE, tokenize.INDENT,
            tokenize.DEDENT, tokenize.ENDMARKER, tokenize.ENCODING}
    code_lines: set[int] = set()
    comment_lines: set[int] = set()
    for tk in toks:
        if tk.type == tokenize.COMMENT:
            comment_lines.add(tk.start[0] - 1)
        elif tk.type not in skip:
            code_lines.update(range(tk.start[0] - 1, tk.end[0]))
    # A comment that shares a line with code (or sits inside a multi-line string's
    # span) is never a candidate.
    comment_lines -= code_lines

    docs: dict[int, tuple[int, int]] = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = node.body
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                e = body[0].value
                if e.end_lineno is not None and e.end_lineno > e.lineno:
                    docs[e.lineno - 1] = (e.lineno - 1, e.end_lineno - 1)
    return comment_lines, docs


def docstring_run(lines: list[str], start: int, end: int):
    """
    Build the run for the multi-line docstring spanning lines[start..end].
    Returns (run, pin_first, pin_last, first_idx, last_idx), or None when the layout
    is unusual enough (implicit concatenation, code after the closer, ...) that the
    docstring is left alone.
    """
    s_open = lines[start].strip()
    m = STRING_OPEN_RE.match(s_open)
    if not m:
        return None
    quote = m.group(1)
    s_close = lines[end].rstrip()
    if s_open.count(quote) != 1 or s_close.count(quote) != 1 or not s_close.endswith(quote):
        return None
    open_text = s_open[m.end():]
    close_text = s_close.strip()[: -len(quote)]

    first_idx = start if open_text.strip() else start + 1
    last_idx = end if close_text.strip() else end - 1
    if last_idx < first_idx:
        return None

    run: list[tuple[int, str, str]] = []
    for k in range(first_idx, last_idx + 1):
        if k == start:
            content = open_text
        elif k == end:
            content = close_text
        else:
            content = lines[k]
        run.append((k + 1, lines[k], content))
    return run, first_idx == start, last_idx == end, first_idx, last_idx


def scan_python(path: Path, text: str, findings: list[Finding]) -> str | None:
    info = python_structure(text)
    if info is None:
        findings.append(Finding(str(path), 1, "review",
                                "file does not parse as Python — skipped entirely"))
        return None
    comment_lines, docs = info
    lines = text.splitlines()
    out: list[str] = []
    changed = False
    i, n = 0, len(lines)
    while i < n:
        if i in docs:
            start, end = docs[i]
            built = docstring_run(lines, start, end)
            if built is None:
                out.extend(lines[start:end + 1])
            else:
                run, pin_first, pin_last, first_idx, last_idx = built
                out.extend(lines[start:first_idx])
                if process_run(out, run, "", str(path), findings, pin_first, pin_last):
                    changed = True
                out.extend(lines[last_idx + 1:end + 1])
            i = end + 1
            continue

        if i in comment_lines:
            run, indent, tok = run_of_line_comments(
                lines, i, "hash", lambda j: j in comment_lines)
            if run:
                if process_run(out, run, indent + tok, str(path), findings):
                    changed = True
                i += len(run)
                continue

        out.append(lines[i])
        i += 1

    return join_lines(out, text) if changed else None


def python_signature(text: str):
    """What must NOT change: every code token, plus the sets of comment/docstring lines."""
    info = python_structure(text)
    if info is None:
        return None
    _, docs = info
    doc_starts = set(docs)
    code, doc_lines, comments = [], [], []
    for tk in tokenize.generate_tokens(io.StringIO(text).readline):
        if tk.type in (tokenize.NL, tokenize.INDENT, tokenize.DEDENT):
            continue
        if tk.type == tokenize.COMMENT:
            if tk.string.lstrip("#").strip():
                comments.append(tk.string.strip())
            continue
        if tk.type == tokenize.STRING and (tk.start[0] - 1) in doc_starts:
            code.append((tk.type, "<docstring>", tk.start[0] == tk.end[0]))
            doc_lines.extend(ln.strip() for ln in tk.string.splitlines() if ln.strip())
            continue
        code.append((tk.type, tk.string))
    return code, sorted(doc_lines), sorted(comments)


# ---- other languages -----------------------------------------------------------
def scan_generic(path: Path, text: str, style: str, findings: list[Finding]) -> str | None:
    lines = text.splitlines()
    out: list[str] = []
    changed = False
    i, n = 0, len(lines)

    def is_comment(j: int) -> bool:
        return token_of(lines[j].strip(), style) is not None

    while i < n:
        line = lines[i]
        stripped = line.strip()

        # --- ` * ` continuation block (JSDoc / Javadoc / Doxygen) --------
        if style in STAR_BLOCK_STYLES and stripped.startswith("/*") and "*/" not in stripped:
            j = i + 1
            while j < n and "*/" not in lines[j]:
                j += 1
            # Only a closer that sits alone on its line; otherwise leave the block.
            if j < n and lines[j].strip() in ("*/", "**/"):
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
                    if process_run(out, body, star_indent + "*", str(path), findings):
                        changed = True
                    out.append(lines[j])
                    i = j + 1
                    continue

        # --- run of line comments ---------------------------------------
        if stripped and is_comment(i):
            run, indent, tok = run_of_line_comments(lines, i, style, is_comment)
            if process_run(out, run, indent + tok, str(path), findings):
                changed = True
            i += len(run)
            continue

        out.append(line)
        i += 1

    return join_lines(out, text) if changed else None


def generic_signature(text: str, style: str):
    """Non-comment lines in order, plus the multiset of non-empty comment lines."""
    code, comments = [], []
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        tok = token_of(s, style)
        star = style in STAR_BLOCK_STYLES and s.startswith("*") and not s.startswith("*/")
        if tok is not None or star:
            body = s[len(tok):] if tok else s[1:]
            if body.strip():
                comments.append(ln.rstrip())
        else:
            code.append(ln)
    return code, sorted(comments)


def scan_file(path: Path, style: str, findings: list[Finding]) -> str | None:
    """Return the rewritten text, or None if the file is unchanged or unsafe to change."""
    text = read_source(path)
    if text is None:
        return None
    local: list[Finding] = []
    if path.suffix == ".py":
        new = scan_python(path, text, local)
        safe = new is None or python_signature(text) == python_signature(new)
    else:
        new = scan_generic(path, text, style, local)
        safe = new is None or generic_signature(text, style) == generic_signature(new, style)

    if not safe:
        # Nothing is written for this file, so its "changed" findings are dropped.
        findings.extend(f for f in local if f.kind == "review")
        findings.append(Finding(str(path), 1, "review",
                                "safety check failed: the rewrite would alter more than "
                                "comment line order — file left untouched"))
        return None
    findings.extend(local)
    return new


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
              "These blocks are not compliant, but the tool refused to change them",
              "(ambiguous language split, commented-out code, missing separator, ...).",
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
            if args.apply:
                # newline="" keeps the line endings the rewrite already joined with.
                with open(p, "w", encoding="utf-8", newline="") as fh:
                    fh.write(result)

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
