"""Small, deliberately conservative TeX scanner used by the migration tools.

This is not a TeX interpreter.  It recognizes command invocations and balanced
arguments while retaining source locations.  Callers must explicitly decide
which commands are safe to convert.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Argument:
    kind: str
    value: str
    start: int
    end: int


@dataclass(frozen=True)
class Command:
    name: str
    arguments: tuple[Argument, ...]
    start: int
    end: int
    line: int

    @property
    def required(self) -> tuple[str, ...]:
        return tuple(a.value for a in self.arguments if a.kind == "required")

    @property
    def optional(self) -> tuple[str, ...]:
        return tuple(a.value for a in self.arguments if a.kind == "optional")


class TexScanError(ValueError):
    pass


def strip_comments(text: str) -> str:
    """Remove TeX comments without changing line numbers or character offsets."""
    chars = list(text)
    i = 0
    while i < len(chars):
        if chars[i] == "%":
            slashes = 0
            j = i - 1
            while j >= 0 and chars[j] == "\\":
                slashes += 1
                j -= 1
            if slashes % 2 == 0:
                while i < len(chars) and chars[i] != "\n":
                    chars[i] = " "
                    i += 1
                continue
        i += 1
    return "".join(chars)


def _balanced(text: str, start: int, opening: str, closing: str) -> tuple[str, int]:
    depth = 1
    i = start + 1
    content_start = i
    while i < len(text):
        c = text[i]
        if c == "\\":
            i += 2
            continue
        if c == opening:
            depth += 1
        elif c == closing:
            depth -= 1
            if depth == 0:
                return text[content_start:i], i + 1
        i += 1
    line = text.count("\n", 0, start) + 1
    raise TexScanError(f"unclosed {opening!r} argument at line {line}")


def commands(text: str, *, max_arguments: int = 4) -> list[Command]:
    """Return command calls, including calls nested inside command arguments."""
    clean = strip_comments(text)
    found: list[Command] = []
    i = 0
    while i < len(clean):
        if clean[i] != "\\":
            i += 1
            continue
        start = i
        i += 1
        if i >= len(clean):
            break
        if clean[i].isalpha() or clean[i] == "@":
            j = i + 1
            while j < len(clean) and (clean[j].isalpha() or clean[j] == "@"):
                j += 1
            name = clean[i:j]
            if j < len(clean) and clean[j] == "*":
                name += "*"
                j += 1
        else:
            name = clean[i]
            j = i + 1
        args: list[Argument] = []
        cursor = j
        for _ in range(max_arguments):
            while cursor < len(clean) and clean[cursor].isspace():
                cursor += 1
            if cursor >= len(clean) or clean[cursor] not in "[{":
                break
            opening = clean[cursor]
            closing = "]" if opening == "[" else "}"
            value, end = _balanced(clean, cursor, opening, closing)
            args.append(Argument("optional" if opening == "[" else "required", value, cursor, end))
            cursor = end
        found.append(Command(name, tuple(args), start, cursor, clean.count("\n", 0, start) + 1))
        # Advance only over the command name so nested commands in arguments are seen.
        i = j
    return found


def scan_file(path: Path) -> list[Command]:
    return commands(path.read_text(encoding="utf-8"))
