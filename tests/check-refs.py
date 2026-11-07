#!/usr/bin/env python3
"""
Cross-reference check for the template's own docs (template repo only; not installed).

Fails when a doc points at something that no longer exists: a section named in a
reference, a linked file or anchor, an @import, a backticked repo path, or when an
English doc and its zh-TW translation drift apart in structure.

Why: cd510f7 silently removed content twice (#53, #55) and nothing failed; the #55
symptom was a cheatsheet still pointing at CONVENTIONS "Known issues" after the section
was gone.

Reference forms (FILE is a file name, a bare stem such as CONVENTIONS, or a repo path):
  (FILE, Section)          "Section" in `FILE`        FILE "Section"
  FILE「Section」           `FILE` 的「Section」         FILE §1
A reference resolves when FILE has a heading or **bold label** that starts with
Section (case-insensitive; a leading "1." is optional). FILE §N needs a heading that
starts with "N.".

Usage:
  python3 tests/check-refs.py               check the repo
  python3 tests/check-refs.py --root DIR    check another tree (e.g. an old commit)
  python3 tests/check-refs.py --self-test   every case in tests/check-refs/cases/ must
                                            produce its expect.txt line
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
CASES = HERE / "check-refs" / "cases"

# English doc -> zh-TW translation. A pair is skipped only when both files are absent.
PAIRS = [
    ("README.md", "docs/README_zh-TW.md"),
    ("docs/factory-cheatsheet_en.md", "docs/factory-cheatsheet_zh-TW.md"),
    ("docs/factory-training_en.html", "docs/factory-training_zh-TW.html"),
]
# Names a doc uses for a template file that has another name in this repo.
ALIASES = {"CLAUDE.md": "CLAUDE.factory-snippet.md"}
# Files that exist only in a target repo at run time.
RUNTIME = {
    ".claude/factory/project.json",
    ".claude/factory/.active",
    ".claude/settings.local.json",
    ".claude/factory/comment-migration-report.md",
    ".claude/factory/sweep-report.md",
    ".claude/factory/retro-report.md",
    ".claude/factory/comment-migration.diff",
    ".claude/settings.json.bak",
}
# History may name removed sections; fixtures are deliberately broken or foreign.
SKIP_FILES = {"CHANGES.md"}
SKIP_DIRS = {".git", "cases"}

FENCE_RE = re.compile(r"^[ \t]*(```|~~~).*?^[ \t]*\1[^\n]*$", re.S | re.M)
CODE_SPAN_RE = re.compile(r"`[^`\n]+`")
FTOK = r"`?(?P<f>[\w./-]*\w)`?"
REF_PATTERNS = [
    re.compile(r"\(" + FTOK + r",\s+(?P<s>[^()\n,]{2,60}?)\s*\)"),
    re.compile(r'"(?P<s>[^"\n]{2,80})"\s+in\s+' + FTOK),
    re.compile(FTOK + r'\s+"(?P<s>[^"\n]{2,80})"'),
    re.compile(FTOK + r"\s*(?:的\s*)?「(?P<s>[^」\n]{1,80})」"),
]
SECTION_NO_RE = re.compile(FTOK + r"\s*§\s*(?P<n>\d+)")
MD_LINK_RE = re.compile(r"\[[^\]\n]*\]\((?P<t>[^)\s]+)\)")
HTML_ATTR_RE = re.compile(r'\b(?:href|src)="(?P<t>[^"]+)"')
HTML_ID_RE = re.compile(r'\bid="([^"]+)"')
IMPORT_RE = re.compile(r"^@(?P<t>\S+)\s*$", re.M)
PATH_SPAN_RE = re.compile(r"`(?P<p>(?:\.claude|docs|tests|\.github)/[^`\s]*)`")


class Repo:
    def __init__(self, root: Path):
        self.root = root
        self.files = sorted(
            p for p in root.rglob("*")
            if p.is_file() and not (set(p.relative_to(root).parts[:-1]) & SKIP_DIRS))
        self.by_name: dict[str, list[Path]] = {}
        for p in self.files:
            self.by_name.setdefault(p.name, []).append(p)
            self.by_name.setdefault(p.stem, []).append(p)
        self._sections: dict[Path, list[str]] = {}

    def rel(self, p: Path) -> str:
        return p.relative_to(self.root).as_posix()

    def docs(self) -> list[Path]:
        return [p for p in self.files if p.suffix in (".md", ".html") and p.name not in SKIP_FILES]

    def resolve(self, token: str, doc: Path) -> list[Path] | None:
        """Files a FILE token names, or None when the token is not a file name."""
        token = ALIASES.get(token, token)
        if "/" in token:
            for base in (self.root, doc.parent):
                p = (base / token.removeprefix("./")).resolve()
                if p.is_file():
                    return [p]
            return [] if token.endswith((".md", ".html")) else None
        hits = self.by_name.get(token, [])
        if hits:
            return hits
        return [] if token.endswith((".md", ".html")) else None

    def sections(self, p: Path) -> list[str]:
        if p not in self._sections:
            text = p.read_text(encoding="utf-8", errors="replace")
            names = re.findall(r"^#{1,6}[ \t]+(.+?)[ \t]*#*$", strip_fences(text), re.M)
            names += re.findall(r"\*\*([^*\n]+)\*\*", text)
            names += [re.sub(r"<[^>]+>", "", h) for h in
                      re.findall(r"<h[1-6][^>]*>(.*?)</h[1-6]>", text, re.S)]
            names += re.findall(r"<(?:b|strong)>(.*?)</(?:b|strong)>", text, re.S)
            self._sections[p] = [norm(html.unescape(n)) for n in names]
        return self._sections[p]


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("`", "").replace("*", "")).strip().strip(":").lower()


def name_matches(section: str, ref: str) -> bool:
    """A reference names a section by its leading words; a heading's number is optional."""
    ref = norm(ref)
    return section.startswith(ref) or re.sub(r"^\d+(\.\d+)*\.?\s+", "", section).startswith(ref)


def strip_fences(text: str) -> str:
    """Blank fenced code blocks, keeping line numbers."""
    return FENCE_RE.sub(lambda m: "\n" * m.group(0).count("\n"), text)


def line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def slug(heading: str) -> str:
    s = re.sub(r"[^\w\- ]", "", heading.strip().lower())
    return s.replace(" ", "-")


def anchors(p: Path) -> set[str]:
    text = p.read_text(encoding="utf-8", errors="replace")
    if p.suffix == ".html":
        return set(HTML_ID_RE.findall(text))
    return {slug(h) for h in re.findall(r"^#{1,6}[ \t]+(.+?)[ \t]*#*$", strip_fences(text), re.M)}


def section_refs(repo: Repo, doc: Path, text: str):
    """Yield (line, file token, targets, section) for every section reference."""
    for pat in REF_PATTERNS:
        for m in pat.finditer(text):
            targets = repo.resolve(m.group("f"), doc)
            if targets is not None:
                yield line_of(text, m.start()), m.group("f"), targets, m.group("s")


def check_doc(repo: Repo, doc: Path, errors: list[str]) -> None:
    raw = doc.read_text(encoding="utf-8", errors="replace")
    text = strip_fences(raw)
    where = repo.rel(doc)
    under_claude = where.startswith(".claude/")

    for line, tok, targets, sec in section_refs(repo, doc, text):
        if not targets:
            errors.append(f"{where}:{line}: {tok} does not exist (referenced for \"{sec}\")")
        elif not any(name_matches(s, sec) for t in targets for s in repo.sections(t)):
            errors.append(f"{where}:{line}: no section \"{sec}\" in {tok}")

    for m in SECTION_NO_RE.finditer(text):
        targets = repo.resolve(m.group("f"), doc)
        if targets is None:
            continue
        n = m.group("n")
        ok = any(s.startswith(n + ".") or s.startswith(n + " ") for t in targets for s in repo.sections(t))
        if not ok:
            errors.append(f"{where}:{line_of(text, m.start())}: no section {n} in {m.group('f')}")

    # Links outside code spans: spans in instruction files hold target-repo examples.
    prose = CODE_SPAN_RE.sub(lambda m: " " * len(m.group(0)), text)
    link_re = HTML_ATTR_RE if doc.suffix == ".html" else MD_LINK_RE
    for m in link_re.finditer(prose):
        check_link(repo, doc, m.group("t"), line_of(prose, m.start()), errors)

    if doc.name == "CLAUDE.factory-snippet.md":
        for m in IMPORT_RE.finditer(text):
            if not (repo.root / m.group("t")).is_file():
                errors.append(f"{where}:{line_of(text, m.start())}: @import {m.group('t')} does not exist")

    for m in PATH_SPAN_RE.finditer(text):
        p = m.group("p").rstrip(".,;:)")
        if any(c in p for c in "<>$*{}") or p in RUNTIME:
            continue
        if under_claude and not p.startswith(".claude/"):
            continue  # docs/ and tests/ in instruction files mean the target repo's
        if not (repo.root / p).exists():
            errors.append(f"{where}:{line_of(text, m.start())}: path {p} does not exist")


def check_link(repo: Repo, doc: Path, target: str, line: int, errors: list[str]) -> None:
    if re.match(r"^[a-z][a-z0-9+.-]*:", target) or "<" in target or "{" in target:
        return
    path, _, frag = target.partition("#")
    dest = (doc.parent / path).resolve() if path else doc
    where = repo.rel(doc)
    if not dest.exists():
        errors.append(f"{where}:{line}: link target {target} does not exist")
    elif frag and dest.is_file() and dest.suffix in (".md", ".html") and frag not in anchors(dest):
        errors.append(f"{where}:{line}: no anchor #{frag} in {repo.rel(dest)}")


def shape(repo: Repo, p: Path) -> dict[str, object]:
    raw = p.read_text(encoding="utf-8", errors="replace")
    text = strip_fences(raw)
    counterparts = {}
    for en, zh in PAIRS:
        counterparts[(repo.root / zh).resolve()] = (repo.root / en).resolve()
    pair_files = {(repo.root / f).resolve() for pair in PAIRS for f in pair}
    links = set()
    prose = CODE_SPAN_RE.sub(lambda m: " " * len(m.group(0)), text)
    for m in (HTML_ATTR_RE if p.suffix == ".html" else MD_LINK_RE).finditer(prose):
        t = m.group("t")
        if re.match(r"^[a-z][a-z0-9+.-]*:", t):
            continue  # absolute URLs may be localized (fonts, a page per language)
        if t.startswith("#"):
            links.add(t)
            continue
        dest = (p.parent / t.partition("#")[0]).resolve()
        if dest in pair_files:
            continue  # the language-switch link points at the other half of the pair
        links.add(repo.rel(counterparts.get(dest, dest)) if dest.is_relative_to(repo.root) else t)
    refs = {(tuple(sorted(repo.rel(x) for x in t)), norm(s)) for _, _, t, s in section_refs(repo, p, text)}
    return {
        "headings": len(re.findall(r"^#{1,6}[ \t]", text, re.M)),
        "table rows": len(re.findall(r"^[ \t]*\|", text, re.M)),
        "code fences": len(re.findall(r"^[ \t]*(?:```|~~~)", raw, re.M)),
        "<tr> rows": raw.count("<tr>"),
        "html ids": sorted(HTML_ID_RE.findall(raw)),
        "relative links": sorted(links),
        "section references": sorted(refs),
    }


def check_pairs(repo: Repo, errors: list[str]) -> None:
    for en, zh in PAIRS:
        a, b = repo.root / en, repo.root / zh
        if not a.exists() and not b.exists():
            continue
        if not (a.exists() and b.exists()):
            errors.append(f"{en if not a.exists() else zh}: missing half of the pair {en} / {zh}")
            continue
        sa, sb = shape(repo, a), shape(repo, b)
        for key in sa:
            if sa[key] != sb[key]:
                if isinstance(sa[key], list):
                    only_en = sorted(set(map(str, sa[key])) - set(map(str, sb[key])))
                    only_zh = sorted(set(map(str, sb[key])) - set(map(str, sa[key])))
                    detail = f"only in EN {only_en}, only in zh-TW {only_zh}"
                else:
                    detail = f"EN {sa[key]}, zh-TW {sb[key]}"
                errors.append(f"{zh}: {key} differ from {en}: {detail}")


def check(root: Path) -> list[str]:
    repo = Repo(root.resolve())
    errors: list[str] = []
    for doc in repo.docs():
        check_doc(repo, doc, errors)
    check_pairs(repo, errors)
    return errors


def self_test() -> int:
    """Each case is a tiny synthetic tree; expect.txt holds 'PASS' or a phrase the errors must contain."""
    failed = 0
    cases = sorted(d for d in CASES.iterdir() if d.is_dir())
    for case in cases:
        want = (case / "expect.txt").read_text(encoding="utf-8").strip()
        errors = check(case)
        got = "\n".join(errors)
        ok = (not errors) if want == "PASS" else (want in got)
        failed += not ok
        print(f"{'ok  ' if ok else 'FAIL'} {case.name}" + ("" if ok else f"\n     expected {want!r}, got {got or 'no errors'!r}"))
    print(f"\n{len(cases) - failed}/{len(cases)} self-test cases passed")
    return 1 if failed or not cases else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", type=Path, default=REPO)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    errors = check(args.root)
    for e in errors:
        print("FAIL " + e)
    print(f"{len(errors)} broken reference(s)" if errors else "All cross-references resolve.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
