#!/usr/bin/env python3
"""
comment-migrate.py — convert legacy interleaved bilingual comments into the
block-after-block form required by .claude/factory/terminology-zh-tw.md.

Before (legacy, interleaved):        After (block-after-block):
    // Reject the request.               // Reject the request.
    // 拒絕該請求。                       // This is the last line of defence.
    // This is the last line of defence. //
    // 這是最後一道防線。                  // 拒絕該請求。
                                         // 這是最後一道防線。

The tool NEVER translates and NEVER rewords. It only reorders whole comment lines
within a single comment block, inserts separator lines, and splits a line that holds
one English and one Chinese sentence at the sentence boundary. Anything it is not
certain about is left untouched and listed in the report for a human to handle.

Safety guarantees:
- A comment run ends at the first line that is not a pure comment line.
- Python files are read with `tokenize` + `ast`: only real `#` comment lines and real
  docstrings are candidates. Triple-quoted strings that are not docstrings (SQL, test
  data) and string literals containing Chinese are never touched.
- Language is decided with context: a wrapped Chinese line made only of identifiers
  and full-width punctuation stays in the Chinese block.
- Line order inside a single-language run never changes.
- Multi-line English followed directly by Chinese (no separator) is flagged, not fixed.
- A blank line that splits one sentence is flagged, never removed.
- Before writing, every rewritten file is re-checked: code tokens unchanged, the same
  comment and docstring lines present, and every comment still above the same code.
  C#, Java, JS and TS files are also re-lexed so string literals cannot change. If
  any check fails, the file is NOT written and is flagged.

Dry-run by default. --diff writes the exact patch for review. See --help.
Regression tests: tests/comment-migrate/run.py in the template repo.
"""

from __future__ import annotations

import argparse
import ast
import difflib
import io
import os
import re
import subprocess
import sys
import tokenize
from collections import Counter
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
    "　-〿"                       # CJK punctuation: 、。「」『』
    "㄀-ㄯ"                       # Bopomofo
    "㐀-䶿一-鿿豈-﫿"
    "＀-￯"                       # full-width forms: （）：，！？
    "\U00020000-\U0002ebef"
    "]"
)
IDEOGRAPH = "㐀-䶿一-鿿豈-﫿"
LATIN_RE = re.compile(r"[A-Za-z]")

# A Chinese line ending in one of these has finished its sentence.
ZH_TERMINAL = ("。", "！", "？", "；", "：")
# An English line ending in one of these has finished its sentence (or clause list).
EN_TERMINAL = (".", "!", "?", ":", ";")

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
_QUOTED_RE = re.compile(r'"[^"\n]*"|“[^”\n]*”')
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
                zh_open = k == "zh" and not t.endswith(EN_TERMINAL)
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


def classify(text: str) -> str:
    """One line on its own, with no context."""
    return classify_lines([text])[0]


def _parses_as_python(text: str) -> bool:
    for src in (text, text + "\n    pass", "def _():\n    " + text,
                "def _():\n    " + text + "\n        pass"):
        try:
            ast.parse(src)
            return True
        except (SyntaxError, ValueError):
            continue
    return False


def looks_like_code(text: str, is_python: bool = False) -> bool:
    """
    True for commented-out code. In Python a line counts only if it also parses as
    Python and does not read as prose ("return value is cached" parses, but it is a
    sentence).
    """
    t = text.strip()
    if not CODE_RE.search(t):
        return False
    if not is_python:
        return True
    if not _parses_as_python(t):
        return False
    return prose_words(t) < 3 or bool(re.search(r"[=()\[\]{}'\"]", t))


def is_mixed(text: str) -> bool:
    """
    One line holding real English prose AND Chinese. Identifiers, `code spans` and
    "quoted messages" inside a Chinese sentence do not count as English prose.
    """
    if not re.search(f"[{IDEOGRAPH}]", text):
        return False
    return prose_words(_QUOTED_RE.sub(" ", text)) >= 4


# A Chinese sentence ending in full-width punctuation, then an English-only tail.
ZH_THEN_EN_RE = re.compile(rf"^(.*[。！？；])\s*([`A-Za-z][^{IDEOGRAPH}]*)$")
# An English-only head ending a sentence, then a tail that opens with Chinese
# (directly, or after one `identifier`).
EN_THEN_ZH_RE = re.compile(
    rf"^([^{IDEOGRAPH}]*[.!?:;])\s+((?:`[^`]+`\s*)?[{IDEOGRAPH}].*)$"
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
    line: int          # 1-based line number of the block's first line
    kind: str          # 'migrated' | 'reordered' | 'review'
    reason: str = ""
    sample: list[str] = field(default_factory=list)
    whole_file: bool = False   # the whole file was left unwritten


@dataclass
class Stats:
    files_scanned: int = 0
    files_changed: int = 0
    migrated: int = 0
    reordered: int = 0
    review: int = 0
    files_skipped: int = 0     # would have changed, but failed verification
    layer1_only: list[str] = field(default_factory=list)  # changed, no lexer for the language


@dataclass
class Split:
    """One mixed line written back as two lines. Used to undo the split in verification."""
    original: str
    parts: tuple[str, str]


# ---------------------------------------------------------------------------
# Core: regroup one paragraph of comment content lines
# ---------------------------------------------------------------------------
SEP = "\0SEP\0"

MID_SENTENCE = ("mid-sentence blank line: a blank line splits one sentence in two "
                "(the text before it is unfinished) — remove it by hand")


def regroup(
    lines: list[str],
    contents: list[str],
    kinds: list[str],
    is_python: bool,
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

    if any(looks_like_code(c, is_python) for c in contents):
        return None, "review", "contains commented-out code — reordering could break it"

    for c in contents:
        if is_mixed(c):
            return None, "review", "a line mixes substantial English and Chinese"

    en = [ln for ln, k in zip(lines, kinds) if k == "en"]
    zh = [ln for ln, k in zip(lines, kinds) if k == "zh"]
    new = en + zh if (len(en) == 1 and len(zh) == 1) else en + [SEP] + zh

    if (pin_first and new[0] != lines[0]) or (pin_last and new[-1] != lines[-1]):
        return None, "review", ("text shares a line with the docstring quotes and "
                                "regrouping would move it — fix by hand")

    kind = "reordered" if switches == 1 else "migrated"
    return new, kind, ""


def _unfinished(text: str, lang: str) -> bool:
    t = text.strip()
    if lang == "en":
        return bool(t) and not t.endswith(EN_TERMINAL) and not SEPARATOR_RE.fullmatch(t)
    return t.endswith(("，", "、"))


def _continues(text: str, lang: str) -> bool:
    t = text.strip()
    if lang == "en":
        return bool(t) and (t[0].islower() or t[0] in "`(")
    return bool(t) and bool(CJK_RE.match(t))


def process_run(
    out: list[str],
    run: list[tuple[int, str, str]],
    separator: str,
    path: str,
    findings: list[Finding],
    splits: list[Split],
    is_python: bool = False,
    pin_first: bool = False,
    pin_last: bool = False,
) -> bool:
    """
    Process one contiguous comment run. `run` is [(lineno, full_line, content), ...]
    and must hold ONLY comment / docstring lines. Appends the (possibly rewritten)
    lines to `out`. Returns True if changed.

    Two levels, in this order:
    1. Paragraph level (paragraphs are split by blank lines): a paragraph that
       interleaves languages line by line is regrouped, as before.
    2. Run level: when every paragraph is single-language and the languages
       alternate in pairs (EN, ZH, EN, ZH), whole paragraphs are reordered to
       EN…EN, separator, ZH…ZH. Paragraphs keep their own lines and order.
    """
    # Split mixed lines first, so the halves are classified with their neighbours.
    # split_of[i] = (original line, 0 or 1) for the two halves of a split line.
    items: list[tuple[int, str, str]] = []
    split_of: dict[int, tuple[str, int]] = {}
    for lineno, line, content in run:
        halves = split_mixed(line, content) if is_mixed(content) else None
        if halves and not (pin_first and lineno == run[0][0]) \
                and not (pin_last and lineno == run[-1][0]):
            for h, (h_line, h_content) in enumerate(halves):
                split_of[len(items)] = (line, h)
                items.append((lineno, h_line, h_content))
        else:
            items.append((lineno, line, content))

    def as_written(idxs: list[int]) -> list[str]:
        """The original lines, with any split line put back together."""
        res: list[str] = []
        for i in idxs:
            if i in split_of:
                if split_of[i][1] == 0:
                    res.append(split_of[i][0])
            else:
                res.append(items[i][1])
        return res

    def splits_in(idxs: list[int]) -> list[Split]:
        return [Split(split_of[i][0].strip(), (items[i][1].strip(), items[i + 1][1].strip()))
                for i in idxs if i in split_of and split_of[i][1] == 0]

    kinds_all = classify_lines([c for _, _, c in items])
    paras: list[list[int]] = []
    cur: list[int] = []
    for i, k in enumerate(kinds_all):
        if k == "blank":
            if cur:
                paras.append(cur)
            cur = []
        else:
            cur.append(i)
    if cur:
        paras.append(cur)

    # --- level 1: each paragraph on its own ----------------------------------
    para_new: dict[int, list[str]] = {}
    para_state: list[str] = []          # 'clean' | 'changed' | 'review'
    para_lang: list[str | None] = []
    local: list[Finding] = []
    for p in paras:
        lines = [items[i][1] for i in p]
        contents = [items[i][2] for i in p]
        kinds = [kinds_all[i] for i in p]
        new, kind, reason = regroup(
            lines, contents, kinds, is_python,
            pin_first=pin_first and p[0] == 0,
            pin_last=pin_last and p[-1] == len(items) - 1,
        )
        langs = set(kinds)
        para_lang.append(langs.pop() if len(langs) == 1 and kinds[0] in ("en", "zh") else None)
        if kind == "review":
            local.append(Finding(path, items[p[0]][0], "review", reason, as_written(p)[:20]))
            para_state.append("review")
        elif new is not None:
            local.append(Finding(path, items[p[0]][0], kind))
            para_new[p[0]] = new
            para_state.append("changed")
        else:
            para_state.append("clean")

    # --- mid-sentence blank lines (reported, never removed) ------------------
    for a, b in zip(paras, paras[1:]):
        la, lb = kinds_all[a[-1]], kinds_all[b[0]]
        if la == lb and la in ("en", "zh") and b[0] - a[-1] >= 2 \
                and _unfinished(items[a[-1]][2], la) and _continues(items[b[0]][2], lb):
            sample = [items[a[-1]][1], items[a[-1] + 1][1], items[b[0]][1]]
            local.append(Finding(path, items[a[-1]][0], "review", MID_SENTENCE, sample))

    # --- level 2: whole paragraphs ------------------------------------------
    reordered: list[str] | None = None
    if len(paras) >= 2 and all(s == "clean" for s in para_state) and None not in para_lang:
        # Language groups: consecutive paragraphs in the same language.
        groups: list[tuple[str, int, int]] = []   # (lang, first_para, last_para)
        for idx, lang in enumerate(para_lang):
            if groups and groups[-1][0] == lang:
                groups[-1] = (lang, groups[-1][1], idx)
            else:
                groups.append((lang, idx, idx))
        n_en = sum(1 for g in groups if g[0] == "en")
        n_zh = sum(1 for g in groups if g[0] == "zh")
        compliant = [g[0] for g in groups] in (["en"], ["zh"], ["en", "zh"])
        # Code-like paragraphs (doctests, examples) have no translation and must stay
        # where they are, so a block holding one is left alone.
        code_like = any(looks_like_code(items[i][2], is_python)
                        for i, k in enumerate(kinds_all) if k != "blank")
        if not compliant and not code_like:
            first_line = items[paras[groups[0][1]][0]][0]
            whole = as_written(list(range(len(items))))
            if n_en != n_zh:
                local.append(Finding(path, first_line, "review",
                                     "English and Chinese paragraphs alternate but do not pair "
                                     "up (a paragraph is missing its translation)", whole[:20]))
            else:
                def span(g: tuple[str, int, int]) -> list[str]:
                    lo = paras[g[1]][0]
                    hi = paras[g[2]][-1]
                    return [items[i][1] for i in range(lo, hi + 1)]
                sep_line = next((items[i][1] for i, k in enumerate(kinds_all)
                                 if k == "blank" and not items[i][2].strip()), SEP)
                ordered = [g for g in groups if g[0] == "en"] + [g for g in groups if g[0] == "zh"]
                new_body: list[str] = []
                for gi, g in enumerate(ordered):
                    if gi:
                        new_body.append(sep_line)
                    new_body += span(g)
                lo, hi = paras[0][0], paras[-1][-1]
                old_body = [items[i][1] for i in range(lo, hi + 1)]
                if (pin_first and lo == 0 and new_body[0] != old_body[0]) or \
                        (pin_last and hi == len(items) - 1 and new_body[-1] != old_body[-1]):
                    local.append(Finding(path, first_line, "review",
                                         "text shares a line with the docstring quotes and "
                                         "reordering paragraphs would move it — fix by hand",
                                         whole[:20]))
                else:
                    reordered = [items[i][1] for i in range(lo)] + new_body \
                        + [items[i][1] for i in range(hi + 1, len(items))]
                    local.append(Finding(path, first_line,
                                         "reordered" if len(groups) == 2 else "migrated"))

    # --- write ---------------------------------------------------------------
    findings.extend(local)
    if reordered is not None:
        out.extend(separator if ln == SEP else ln for ln in reordered)
        splits.extend(splits_in(list(range(len(items)))))
        return True

    # Paragraph by paragraph. A paragraph under review is written exactly as it was,
    # so a line split inside it is put back together.
    changed = bool(para_new)
    kept_split = False
    para_at = {p[0]: (p, s) for p, s in zip(paras, para_state)}
    i = 0
    while i < len(items):
        if i in para_at:
            p, state = para_at[i]
            if state == "changed":
                out.extend(separator if ln == SEP else ln for ln in para_new[i])
                splits.extend(splits_in(p))
            elif state == "review":
                out.extend(as_written(p))
            else:
                out.extend(items[j][1] for j in p)
                if splits_in(p):
                    splits.extend(splits_in(p))
                    kept_split = True
            i = p[-1] + 1
        else:
            out.append(items[i][1])
            i += 1
    if kept_split:
        # A split whose two halves were already in order: the split is the change.
        findings.append(Finding(path, run[0][0], "migrated"))
        changed = True
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


@dataclass
class Layout:
    """How the file breaks into lines, so the rewrite can be joined back the same way."""
    eol: str
    trailing: bool
    mixed: bool


def split_source(text: str) -> tuple[list[str], Layout]:
    # Split on the file's own line ending only. str.splitlines() would also split on
    # U+2028, \f and other characters that can sit inside a string literal, and
    # writing those lines back would break the code line in two.
    eol = "\r\n" if "\r\n" in text else "\n"
    leftover = text.replace("\r\n", "")
    mixed = "\r" in leftover or (eol == "\r\n" and "\n" in leftover)
    trailing = text.endswith(eol)
    body = text[: -len(eol)] if trailing else text
    return (body.split(eol) if body else []), Layout(eol, trailing, mixed)


def join_source(out: list[str], layout: Layout) -> str:
    return layout.eol.join(out) + (layout.eol if layout.trailing else "")


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


def scan_python(path: Path, text: str, findings: list[Finding],
                splits: list[Split]) -> list[str] | None:
    info = python_structure(text)
    if info is None:
        findings.append(Finding(str(path), 1, "review",
                                "file does not parse as Python — skipped entirely"))
        return None
    comment_lines, docs = info
    lines, _ = split_source(text)
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
                if process_run(out, run, "", str(path), findings, splits, True,
                               pin_first, pin_last):
                    changed = True
                out.extend(lines[last_idx + 1:end + 1])
            i = end + 1
            continue

        if i in comment_lines:
            run, indent, tok = run_of_line_comments(
                lines, i, "hash", lambda j: j in comment_lines)
            if run:
                if process_run(out, run, indent + tok, str(path), findings, splits, True):
                    changed = True
                i += len(run)
                continue

        out.append(lines[i])
        i += 1

    return out if changed else None


def _undo_splits(entries: Counter, splits: list[Split]) -> Counter:
    """Merge each split pair back into its original line, so both sides compare equal."""
    entries = Counter(entries)
    for s in splits:
        for anchor in sorted({a for (t, a) in entries if t == s.parts[0]}):
            a_key, b_key = (s.parts[0], anchor), (s.parts[1], anchor)
            if entries[a_key] and entries[b_key]:
                entries[a_key] -= 1
                entries[b_key] -= 1
                entries[(s.original, anchor)] += 1
                break
    return +entries


def python_signature(text: str, splits: list[Split] | None = None):
    """
    What must NOT change: every code token in order; every comment line together with
    the number of code tokens before it (so a comment cannot move past code); and the
    multiset of docstring lines.
    """
    info = python_structure(text)
    if info is None:
        return None
    _, docs = info
    doc_starts = set(docs)
    code: list[tuple] = []
    comments: Counter = Counter()
    doc_lines: Counter = Counter()
    for tk in tokenize.generate_tokens(io.StringIO(text).readline):
        if tk.type in (tokenize.NL, tokenize.INDENT, tokenize.DEDENT):
            continue
        if tk.type == tokenize.COMMENT:
            if tk.string.lstrip("#").strip():
                comments[(tk.string.strip(), len(code))] += 1
            continue
        if tk.type == tokenize.STRING and (tk.start[0] - 1) in doc_starts:
            code.append((tk.type, "<docstring>", tk.start[0] == tk.end[0]))
            for ln in tk.string.split("\n"):
                if ln.strip():
                    doc_lines[(ln.strip(), len(code))] += 1
            continue
        code.append((tk.type, tk.string))
    if splits:
        comments = _undo_splits(comments, splits)
        doc_lines = _undo_splits(doc_lines, splits)
    return code, comments, doc_lines


# ---- other languages -----------------------------------------------------------
def scan_generic(path: Path, text: str, style: str, findings: list[Finding],
                 splits: list[Split]) -> list[str] | None:
    lines, _ = split_source(text)
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
                    if process_run(out, body, star_indent + "*", str(path), findings, splits):
                        changed = True
                    out.append(lines[j])
                    i = j + 1
                    continue

        # --- run of line comments ---------------------------------------
        if stripped and is_comment(i):
            run, indent, tok = run_of_line_comments(lines, i, style, is_comment)
            if process_run(out, run, indent + tok, str(path), findings, splits):
                changed = True
            i += len(run)
            continue

        out.append(line)
        i += 1

    return out if changed else None


def generic_signature(lines: list[str], style: str, splits: list[Split] | None = None):
    """
    Non-comment lines in order, plus every non-empty comment line together with the
    number of non-comment lines before it (so a comment cannot move past code).
    """
    code: list[str] = []
    comments: Counter = Counter()
    for ln in lines:
        s = ln.strip()
        if not s:
            continue
        tok = token_of(s, style)
        star = style in STAR_BLOCK_STYLES and s.startswith("*") and not s.startswith("*/")
        if tok is not None or star:
            body = s[len(tok):] if tok else s[1:]
            if body.strip():
                comments[(s, len(code))] += 1
        else:
            code.append(ln)
    if splits:
        comments = _undo_splits(comments, splits)
    return code, comments


# ---------------------------------------------------------------------------
# Lexer check for C#, Java, JS and TS (from PR #51): comments may move; code and
# string literals must not change. This catches text the scanner mistook for
# comments, such as `//` lines inside a template literal or verbatim string.
# ---------------------------------------------------------------------------
class LexError(Exception):
    pass



_CS_STRING = re.compile(r'(\$*)(@?)(\$*)("{3,}|")')
_JS_REGEX_KEYWORDS = {
    "return", "typeof", "instanceof", "in", "of", "new", "delete", "void", "throw",
    "case", "do", "else", "yield", "await",
}


class _CLikeLexer:
    """
    Splits C#, Java and JS/TS source into code and literals, dropping comments.
    Not a parser: it only needs to know where comments, strings, template
    literals and regex literals start and end. Anything it cannot follow to the
    end raises LexError, and the file goes to human review.
    """

    def __init__(self, text: str, lang: str) -> None:
        self.t = text
        self.n = len(text)
        self.lang = lang
        self.tokens: list[str] = []

    def run(self) -> list[str]:
        self.code(0, 0)
        return self.tokens

    def code(self, i: int, hole_braces: int) -> int:
        """Top level when hole_braces == 0; else an interpolation hole closed by that many '}'."""
        t, n = self.t, self.n
        top = hole_braces == 0
        buf: list[str] = []
        depth = 0
        after_literal = False

        def flush() -> None:
            text = " ".join("".join(buf).split())
            if top and text:
                self.tokens.append("code: " + text)
            buf.clear()

        while i < n:
            if t.startswith("//", i):
                j = t.find("\n", i)
                i = n if j < 0 else j
                buf.append(" ")
                continue
            if t.startswith("/*", i):
                j = t.find("*/", i + 2)
                if j < 0:
                    raise LexError("unterminated /* comment")
                i = j + 2
                buf.append(" ")
                continue
            end = self.literal(i)
            if end is None and t[i] == "/" and self.lang == "js" and self.regex_allowed(buf, after_literal):
                end = self.regex(i)
            if end is not None:
                flush()
                if top:
                    self.tokens.append("literal: " + t[i:end])
                after_literal = True
                i = end
                continue
            c = t[i]
            if not top:
                if c == "{":
                    depth += 1
                elif c == "}":
                    if depth == 0:
                        if not t.startswith("}" * hole_braces, i):
                            raise LexError("unbalanced braces in an interpolation hole")
                        return i + hole_braces
                    depth -= 1
            buf.append(c)
            if not c.isspace():
                after_literal = False
            i += 1
        if not top:
            raise LexError("unterminated interpolation hole")
        flush()
        return n

    def regex_allowed(self, buf: list[str], after_literal: bool) -> bool:
        before = "".join(buf).rstrip()
        if not before:
            return not after_literal
        last = before[-1]
        if last.isalnum() or last in "_$":
            word = re.search(r"[\w$]+$", before)
            return word is not None and word.group() in _JS_REGEX_KEYWORDS
        if last in ")]":
            return False
        if last == "!" and len(before) > 1 and (before[-2].isalnum() or before[-2] in "_$)]"):
            return False  # TS non-null `x! / y`
        if last == "}":
            raise LexError("a '/' after '}' could be a regex or a division")
        return True

    def literal(self, i: int) -> int | None:
        t, c = self.t, self.t[i]
        if self.lang == "cs":
            if c in '$@"':
                m = _CS_STRING.match(t, i)
                if m is None:
                    return None
                dollars = len(m.group(1)) + len(m.group(3))
                quotes = m.group(4)
                if m.group(2):
                    # Verbatim opens with ONE quote; `@"""a"` starts with an escaped quote.
                    return self.cs_verbatim(m.start(4) + 1, dollars > 0)
                if len(quotes) >= 3:
                    return self.cs_raw(m.end(), len(quotes), dollars)
                return self.quoted(m.end(), '"', dollars > 0)
            if c == "'":
                return self.quoted(i + 1, "'", False)
            return None
        if self.lang == "java":
            if t.startswith('"""', i):
                return self.text_block(i + 3)
            if c in "\"'":
                return self.quoted(i + 1, c, False)
            return None
        if c in "\"'":
            return self.quoted(i + 1, c, False)
        if c == "`":
            return self.template(i + 1)
        return None

    def quoted(self, j: int, quote: str, holes: bool) -> int:
        t, n = self.t, self.n
        while j < n:
            ch = t[j]
            if ch == "\\":
                j += 2
            elif ch == quote:
                return j + 1
            elif ch == "\n":
                break
            elif holes and t.startswith("{{", j) or holes and t.startswith("}}", j):
                j += 2
            elif holes and ch == "{":
                j = self.code(j + 1, 1)
            else:
                j += 1
        raise LexError("unterminated string literal")

    def cs_verbatim(self, j: int, holes: bool) -> int:
        t, n = self.t, self.n
        while j < n:
            if t.startswith('""', j):
                j += 2
            elif t[j] == '"':
                return j + 1
            elif holes and (t.startswith("{{", j) or t.startswith("}}", j)):
                j += 2
            elif holes and t[j] == "{":
                j = self.code(j + 1, 1)
            else:
                j += 1
        raise LexError("unterminated verbatim string")

    def cs_raw(self, j: int, quotes: int, dollars: int) -> int:
        t, n = self.t, self.n
        close = '"' * quotes
        while j < n:
            if t.startswith(close, j):
                return j + quotes
            if dollars and t[j] == "{":
                k = 0
                while j + k < n and t[j + k] == "{":
                    k += 1
                j += k
                if k >= dollars:
                    j = self.code(j, dollars)
                continue
            j += 1
        raise LexError("unterminated raw string literal")

    def text_block(self, j: int) -> int:
        t, n = self.t, self.n
        while j < n:
            if t[j] == "\\":
                j += 2
            elif t.startswith('"""', j):
                return j + 3
            else:
                j += 1
        raise LexError("unterminated text block")

    def template(self, j: int) -> int:
        t, n = self.t, self.n
        while j < n:
            if t[j] == "\\":
                j += 2
            elif t[j] == "`":
                return j + 1
            elif t.startswith("${", j):
                j = self.code(j + 2, 1)
            else:
                j += 1
        raise LexError("unterminated template literal")

    def regex(self, i: int) -> int:
        t, n = self.t, self.n
        j = i + 1
        in_class = False
        while j < n:
            ch = t[j]
            if ch == "\\":
                j += 2
                continue
            if ch == "\n":
                break
            if ch == "[":
                in_class = True
            elif ch == "]":
                in_class = False
            elif ch == "/" and not in_class:
                j += 1
                while j < n and (t[j].isalnum() or t[j] in "_$"):
                    j += 1
                return j
            j += 1
        raise LexError("unterminated regex literal")


# JSX/TSX are left out: JSX text and closing tags (`</div>`, `Don't`) are not
# lexable without a JSX-aware lexer, so they get layer 1 only.
LEXER_LANG = {".cs": "cs", ".java": "java", ".js": "js", ".mjs": "js", ".cjs": "js", ".ts": "js"}


def verify_lexed(suffix: str, old: str, new: str) -> str | None:
    """C#, Java, JS, TS: code and string literals must be identical after the rewrite."""
    lang = LEXER_LANG.get(suffix)
    if lang is None:
        return None
    try:
        before = _CLikeLexer(old, lang).run()
    except LexError as exc:
        return f"the original file does not lex: {exc}"
    try:
        after = _CLikeLexer(new, lang).run()
    except LexError as exc:
        return f"the rewritten file does not lex: {exc}"
    if before == after:
        return None
    for a, b in zip(before, after):
        if a != b:
            return f"code or a string literal changed near {a[:60]!r}"
    return "the number of code tokens changed"


def scan_file(path: Path, style: str, findings: list[Finding]) -> tuple[str, bool] | None:
    """
    Return (rewritten text, lexer_checked), or None if the file is unchanged or unsafe
    to change. lexer_checked is False when only the line-level check could run.
    """
    text = read_source(path)
    if text is None:
        return None
    local: list[Finding] = []
    splits: list[Split] = []
    lines, layout = split_source(text)
    if path.suffix == ".py":
        out = scan_python(path, text, local, splits)
    else:
        out = scan_generic(path, text, style, local, splits)

    def reject(reason: str) -> None:
        # Nothing is written for this file, so its "changed" findings are dropped.
        findings.extend(f for f in local if f.kind == "review")
        sample = [s for f in local for s in f.sample][:20]
        findings.append(Finding(str(path), 1, "review", reason, sample, whole_file=True))

    if out is None:
        findings.extend(local)
        return None
    if layout.mixed:
        reject("mixed line endings — rewriting would change some of them; file left untouched")
        return None

    new = join_source(out, layout)
    if path.suffix == ".py":
        safe = python_signature(text) == python_signature(new, splits)
        lexer_checked = True
    else:
        safe = generic_signature(lines, style) == generic_signature(out, style, splits)
        lexer_checked = path.suffix in LEXER_LANG
    if not safe:
        reject("safety check failed: the rewrite would alter more than comment line order, "
               "or move a comment past code — file left untouched")
        return None
    problem = verify_lexed(path.suffix, text, new)
    if problem is not None:
        reject(f"safety check failed (lexer): {problem} — file left untouched")
        return None
    findings.extend(local)
    return new, lexer_checked


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
    # This script is installed into every repo; its docstring shows interleaved comments
    # on purpose, so it never scans itself.
    seen, uniq = {Path(__file__).resolve()}, []
    for p in files:
        rp = p.resolve()
        if rp not in seen:
            seen.add(rp)
            uniq.append(p)
    return uniq


def git_dirty(root: Path, ignore: list[Path]) -> bool:
    """
    True if the working tree has changes the user should commit first.
    The tool's own outputs (report, diff) are excluded — a dry run writes them, and
    that must not block the --apply that follows.
    """
    try:
        r = subprocess.run(["git", "-C", str(root), "status", "--porcelain", "-z"],
                           capture_output=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return False
    ignore_rp = {p.resolve() for p in ignore}
    for entry in r.stdout.decode("utf-8", "replace").split("\0"):
        if len(entry) < 4:
            continue
        path = entry[3:]
        if (root / path).resolve() in ignore_rp:
            continue
        return True
    return False


# ---------------------------------------------------------------------------
# Report and diff
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
    L.append(f"| Files left unwritten (failed safety check) | {stats.files_skipped} |")
    L.append(f"| Changed files without a lexer check | {len(stats.layer1_only)} |")
    L.append("")
    L += ["Every changed file passed the line-level safety check: code unchanged, the same",
          "comment lines present, every comment still above the same code. Python, C#,",
          "Java, JS and TS files were also checked by a tokenizer or lexer.", ""]

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

    if stats.layer1_only:
        L += ["## Changed without a lexer check", "",
              "No lexer exists for these languages. Review their diff with care:",
              "a comment-like line inside a string or heredoc would not be caught.", ""]
        L += [f"- `{fp}`" for fp in stats.layer1_only]
        L.append("")

    review = [f for f in findings if f.kind == "review"]
    if review:
        L += ["## Needs human review (NOT changed)", "",
              "These blocks are not compliant, but the tool refused to change them",
              "(ambiguous language split, commented-out code, missing separator,",
              "mid-sentence blank line, ...). Fix them by hand, or hand this list to",
              "Claude one file at a time.", ""]
        for f in review:
            L.append(f"### `{f.path}` L{f.line}")
            L.append(f"Reason: {f.reason}")
            if f.sample:
                L.append("```")
                L.extend(f.sample)
                L.append("```")
            L.append("")
    L.append("")
    path.write_text("\n".join(L), encoding="utf-8")


def unified_diff(path: Path, old: str, new: str) -> str:
    """A git-style patch for one file, keeping its line endings (so `git apply` works)."""
    name = path.as_posix()
    a, b = old.splitlines(True), new.splitlines(True)
    lines: list[str] = []
    for ln in difflib.unified_diff(a, b, f"a/{name}", f"b/{name}"):
        lines.append(ln)
        if not ln.endswith(("\n", "\r")):
            lines.append("\n\\ No newline at end of file\n")
    return "".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(
        description="Convert interleaved bilingual comments to block-after-block form.")
    ap.add_argument("paths", nargs="*", default=["."],
                    help="files or directories to scan (default: current directory)")
    ap.add_argument("--apply", action="store_true",
                    help="write the changes (default is a dry run)")
    ap.add_argument("--force", action="store_true",
                    help="allow --apply even when the git working tree is dirty")
    ap.add_argument("--check", action="store_true",
                    help="CI mode: exit 1 if any non-compliant comment block is found")
    ap.add_argument("--report", default=".claude/factory/comment-migration-report.md",
                    help="where to write the markdown report")
    ap.add_argument("--diff", default="",
                    help="also write the full patch of the changes to this file, for review")
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
    diff_path = Path(args.diff) if args.diff else None
    outputs = [report] + ([diff_path] if diff_path else [])
    if args.apply and not args.force and git_dirty(root, outputs):
        print("ERROR: git working tree is dirty.", file=sys.stderr)
        print("Commit or stash first so this migration lands as one reviewable diff,",
              file=sys.stderr)
        print("or re-run with --force if you know what you are doing.", file=sys.stderr)
        return 1

    allow = {e.strip() for e in args.ext.split(",") if e.strip()}
    stats, findings = Stats(), []
    patches: list[str] = []

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
        stats.files_skipped += sum(1 for f in new_findings if f.whole_file)
        if result is not None:
            new_text, lexer_checked = result
            stats.files_changed += 1
            if not lexer_checked:
                stats.layer1_only.append(str(p))
            if diff_path is not None:
                patches.append(unified_diff(p, p.read_bytes().decode("utf-8"), new_text))
            if args.apply:
                # Bytes, not text mode: text mode on Windows turns every "\n" into
                # "\r\n", so CRLF files would gain "\r\r\n" and LF files become CRLF.
                p.write_bytes(new_text.encode("utf-8"))

    report.parent.mkdir(parents=True, exist_ok=True)
    write_report(report, stats, findings, args.apply)
    if diff_path is not None:
        diff_path.parent.mkdir(parents=True, exist_ok=True)
        diff_path.write_bytes("".join(patches).encode("utf-8"))

    verb = "Rewrote" if args.apply else "Would rewrite"
    print(f"Scanned {stats.files_scanned} file(s).")
    print(f"{verb} {stats.files_changed} file(s): "
          f"{stats.migrated} block(s) regrouped, {stats.reordered} pair(s) reordered.")
    print(f"{stats.review} block(s) need human review"
          f" ({stats.files_skipped} whole file(s) left unwritten after a failed safety check).")
    if stats.layer1_only:
        print(f"{len(stats.layer1_only)} changed file(s) had no lexer check; see the report.")
    print(f"Report: {report}")
    if diff_path is not None:
        print(f"Diff: {diff_path}")
    if not args.apply and stats.files_changed:
        print("Dry run — nothing was written. Review the diff, then re-run with --apply.")

    if args.check and (stats.migrated or stats.reordered or stats.review):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
