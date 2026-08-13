"""Fail-closed helpers for converting the safe MPG TeX subset to reST.

The converter intentionally refuses unknown commands and environments.  It is
for deterministic mechanical work, not for guessing at complex diagrams,
tables, or macro semantics.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, asdict
import json
from pathlib import Path
import re

try:
    from .tex import commands, strip_comments
except ImportError:
    from tex import commands, strip_comments


@dataclass(frozen=True)
class ConversionIssue:
    source: str
    line: int
    construct: str
    reason: str


class UnsafeConversion(RuntimeError):
    def __init__(self, issues: list[ConversionIssue]):
        super().__init__(f"conversion refused: {len(issues)} unsupported construct(s)")
        self.issues = issues


SAFE_COMMANDS = {
    "chapter", "chapter*", "section", "section*", "subsection", "subsection*", "subsubsection",
    "label", "autoref", "ref", "pageref", "cite", "emph", "textbf", "texttt", "CppInline", "litstr",
    "item", "begin", "end", "paragraph", "CPP", "ldots", "dots", "%", "?",
}
SAFE_ENVIRONMENTS = {"itemize", "enumerate"}


def audit(text: str, source: str = "<fragment>") -> list[ConversionIssue]:
    issues: list[ConversionIssue] = []
    for c in commands(text):
        if c.name not in SAFE_COMMANDS:
            issues.append(ConversionIssue(source, c.line, f"\\{c.name}", "no semantics-preserving reST mapping"))
        elif c.name in {"begin", "end"} and c.required and c.required[0].strip() not in SAFE_ENVIRONMENTS:
            issues.append(ConversionIssue(source, c.line, f"{c.name}{{{c.required[0].strip()}}}", "environment requires manual migration or a dedicated directive"))
    # Display math is supported; other escaped TeX is caught above.
    return sorted(set(issues), key=lambda x: (x.source, x.line, x.construct))


def _replace_balanced(text: str, name: str, render) -> str:
    marker = "\\" + name
    while marker in text:
        start = text.find(marker)
        cursor = start + len(marker)
        while cursor < len(text) and text[cursor].isspace():
            cursor += 1
        if cursor >= len(text) or text[cursor] != "{":
            break
        depth = 1
        end = cursor + 1
        while end < len(text) and depth:
            if text[end] == "\\":
                end += 2
                continue
            if text[end] == "{": depth += 1
            elif text[end] == "}": depth -= 1
            end += 1
        if depth:
            break
        value = text[cursor + 1:end - 1]
        text = text[:start] + render(value) + text[end:]
    return text


def convert_fragment(text: str, source: str = "<fragment>") -> str:
    issues = audit(text, source)
    if issues:
        raise UnsafeConversion(issues)
    out = strip_comments(text)
    # Protect display and inline math before other substitutions.
    protected: list[str] = []
    def protect(match):
        token = f"@@MPGPROTECTED{len(protected)}@@"
        display = match.group(1) is not None
        body = (match.group(1) if display else match.group(2)).strip("\n")
        if display:
            protected.append(".. math::\n\n" + "\n".join("   " + line for line in body.splitlines()))
        else:
            protected.append(f":math:`{body}`")
        return token
    out = re.sub(r"\$\$(.*?)\$\$|\$([^$\n]+)\$", protect, out, flags=re.S)

    heading_marks = {"chapter": "=", "chapter*": "=", "section": "-", "section*": "-", "subsection": "~", "subsection*": "~", "subsubsection": "^"}
    for name, mark in heading_marks.items():
        out = _replace_balanced(out, name, lambda v, m=mark: f"\n{v}\n{m * len(v)}\n")
    out = _replace_balanced(out, "label", lambda v: f"\n.. _{v}:\n")
    for name in ("autoref", "ref", "pageref"):
        out = _replace_balanced(out, name, lambda v: f":ref:`{v}`")
    out = _replace_balanced(out, "cite", lambda v: f":cite:p:`{v}`")
    for name, delimiters in (("emph", ("*", "*")), ("textbf", ("**", "**")), ("texttt", ("``", "``")), ("CppInline", ("``", "``")), ("litstr", ("``", "``"))):
        out = _replace_balanced(out, name, lambda v, d=delimiters: d[0] + v + d[1])
    out = _replace_balanced(out, "paragraph", lambda v: f"\n**{v.rstrip('.')}**\n\n")
    out = re.sub(r"\\\?(.+?)\?", lambda m: f"``{m.group(1)}``", out)
    out = out.replace(r"\CPP{}", "C++").replace(r"\CPP", "C++")
    out = out.replace(r"\ldots", "…").replace(r"\dots", "…")
    out = re.sub(r"\\begin\{(?:itemize|enumerate)\}\s*", "\n", out)
    out = re.sub(r"\\end\{(?:itemize|enumerate)\}\s*", "\n", out)
    out = re.sub(r"(?m)^\s*\\item\s*", "* ", out)
    out = re.sub(r"[ \t]+\n", "\n", out)
    out = re.sub(r"\n{3,}", "\n\n", out).strip() + "\n"
    for i, value in enumerate(protected):
        out = out.replace(f"@@MPGPROTECTED{i}@@", value)
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path, nargs="?")
    parser.add_argument("--report", type=Path)
    parser.add_argument("--audit-only", action="store_true")
    args = parser.parse_args(argv)
    text = args.source.read_text(encoding="utf-8")
    issues = audit(text, args.source.as_posix())
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps({"source": args.source.as_posix(), "safe": not issues, "issues": [asdict(x) for x in issues]}, indent=2) + "\n", encoding="utf-8")
    if issues:
        for issue in issues:
            print(f"{issue.source}:{issue.line}: {issue.construct}: {issue.reason}")
        return 2
    if not args.audit_only:
        rendered = convert_fragment(text, args.source.as_posix())
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
