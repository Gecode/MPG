from __future__ import annotations

import re
from pathlib import Path

from .common import GEN_TEX, ROOT


def gen_acks(changelog_in: Path, out: Path) -> None:
    names: dict[str, str] = {}
    for line in changelog_in.read_text(encoding="utf-8").splitlines():
        m = re.search(r"\[\\AckName\{(.*)\}\{(.*)\}\]", line)
        if m:
            names[m.group(2)] = m.group(1)
    text = ",\n".join(f"{names[k]} {k}" for k in sorted(names)) + ".\n"
    out.write_text(text, encoding="utf-8")


def gen_titles(chapters: list[Path], out: Path) -> None:
    c_title = ""
    s_title = ""
    c: dict[str, str] = {}
    s: dict[str, str] = {}
    for p in chapters:
        for line in p.read_text(encoding="utf-8").splitlines():
            m = re.match(r"\\chapter\{(.*)\}", line)
            if m:
                c_title = m.group(1)
                continue
            m = re.match(r"\\chapter\[(.*)\]\{(.*)\}", line)
            if m:
                c_title = m.group(1)
                continue
            m = re.match(r"\\section\{(.*)\}", line)
            if m:
                s_title = m.group(1)
                continue
            m = re.match(r"\\label\{chap:(.:.*)\}", line)
            if m:
                c[m.group(1)] = c_title
                continue
            m = re.match(r"\\label\{sec:(m:.*)\}", line)
            if m:
                s[m.group(1)] = s_title
                continue

    out_lines: list[str] = []
    for k in sorted(c):
        cmd = k.replace(":", "").replace("_", "").replace("-", "")
        out_lines.append(
            f"\\newcommand{{\\tc{cmd}}}{{\\hyperref[chap:{k}]{{\\autoref*{{chap:{k}}} ({c[k]})}}}}\n"
        )
    for k in sorted(s):
        cmd = k.replace(":", "").replace("_", "").replace("-", "")
        out_lines.append(f"\\newcommand{{\\ts{cmd}}}{{\\autoref{{sec:{k}}}}}\n")
        out_lines.append(f"\\newcommand{{\\pts{cmd}}}{{(\\autoref{{sec:{k}}})}}\n")
    out.write_text("\n".join(out_lines) + "\n", encoding="utf-8")


def expand_includes(text: str, include_base: Path) -> str:
    out: list[str] = []
    for line in text.splitlines(keepends=True):
        m = re.match(r"^\\include\{(.*)\}", line)
        if m:
            name = m.group(1) + ".tex"
            p = include_base / name
            if not p.exists():
                p = ROOT / name
            out.append(p.read_text(encoding="utf-8"))
            continue
        m = re.match(r"^\\input (.*)", line)
        if m:
            name = m.group(1) + ".tex"
            p = include_base / name
            if not p.exists():
                p = ROOT / name
            out.append(p.read_text(encoding="utf-8"))
            continue
        out.append(line)
    return "".join(out)


def shorten_labels(text: str) -> str:
    label: dict[str, str] = {}
    n = 0

    def relabel(s: str) -> str:
        nonlocal n
        if s not in label:
            n += 1
            label[s] = f"l:{n}"
        return label[s]

    out_lines: list[str] = []
    for line in text.splitlines():
        for cmd in ("litfile", "litlabel", "litref"):
            line = re.sub(
                rf"\\{cmd}\{{([^}}]+)\}}",
                lambda m: f"\\{cmd}{{{relabel(m.group(1))}}}",
                line,
            )
        line = re.sub(r"\\autoref\{([^}]+)\}", lambda m: f"\\autoref{{{relabel(m.group(1))}}}", line)
        line = re.sub(r"\\label\{([^}]+)\}", lambda m: f"\\label{{{relabel(m.group(1))}}}", line)
        line = re.sub(
            r"\\hyperref\[([^\]]+)\]\{\\autoref\*\{([^}]+)\}",
            lambda m: f"\\hyperref[{relabel(m.group(1))}]{{\\autoref*{{{relabel(m.group(2))}}}",
            line,
        )
        out_lines.append(line)
    return "\n".join(out_lines) + "\n"


def fixout(text: str) -> str:
    out: list[str] = []
    for line in text.splitlines():
        m = re.match(r"\\BOOKMARK \[(.*)\]\[(.*)\]\{(.*)\}\{(.*)\}\{(.*)\}", line)
        if not m:
            out.append(line)
            continue
        a, b, c, d, e = m.groups()
        if any(x in d for x in ("Bibliography", "License", "Changelog")):
            e = ""
        out.append(f"\\BOOKMARK [{a}][{b}]{{{c}}}{{{d}}}{{{e}}}")
    return "\n".join(out) + "\n"


def render_mpg_tex(version: str, year: str) -> tuple[Path, Path]:
    mpg_in_in = ROOT / "MPG.tex.in.in"
    text = mpg_in_in.read_text(encoding="utf-8")
    text = text.replace("@VERSION@", version).replace("@YEAR@", year)
    text = expand_includes(text, GEN_TEX)
    text = replace_doc_refs(text)
    text = shorten_labels(text)
    mpg_in = GEN_TEX / "MPG.tex.in"
    mpg = GEN_TEX / "MPG.tex"
    mpg_in.write_text(text, encoding="utf-8")
    mpg.write_text(text, encoding="utf-8")
    return mpg_in, mpg


def replace_doc_refs(text: str) -> str:
    url: dict[tuple[str, str], str] = {}
    title: dict[tuple[str, str], str] = {}
    db = ROOT / "bin" / "gl.db"
    if db.exists():
        for line in db.read_text(encoding="utf-8").splitlines():
            m = re.match(r"URL (.*) (.*) (.*)", line)
            if m:
                url[(m.group(1), m.group(2))] = m.group(3)
                continue
            m = re.match(r'TITLE (.*) (.*) \"(.*)\"', line)
            if m:
                title[(m.group(1), m.group(2))] = m.group(3)

    def repl(m: re.Match[str]) -> str:
        kind = m.group(1)
        ref = m.group(2)
        u = url.get((kind, ref)) or url.get((kind, f"Gecode::{ref}")) or "NONE"
        u = u.replace("_", r"\_")
        if kind in {"example", "group", "page"}:
            txt = title.get((kind, ref), ref)
        else:
            safe = re.sub(r"([#$%&_{}])", r"\\\1", ref)
            txt = f"\\\\CppInline{{{safe}}}"
        return f"\\\\litdocref{{{u}}}{{{txt}}}"

    return re.sub(r"\\gecoderef\[([^\]]*)\]\{([^}]*)\}", repl, text)
