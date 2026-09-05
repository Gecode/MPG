#!/usr/bin/env python3
"""Check, refresh, and register canonical MPG code excerpts.

Examples (from the repository root):
  python rst/scripts/code.py check
  python rst/scripts/code.py refresh
  python rst/scripts/code.py refresh --no-relocate
  python rst/scripts/code.py add 'new example' rst/examples/src/new.cpp --validation compiled

Refresh relocates existing excerpts from the committed source and manifest
(--base HEAD by default), so repeated refreshes before committing are safe.
Insertions at excerpt boundaries stay outside the excerpt; whole-file excerpts
grow with the file. Edits crossing a boundary or deleting an excerpt require
review: adjust its line ranges explicitly, then use --no-relocate. New excerpts
use their authored ranges. Commit the code and manifest together.
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = "rst/manifests/code-projections.json"


def fingerprint(payload: bytes) -> dict:
    return {"bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}


def source_path(root: Path, relative: str) -> Path:
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts or not relative.startswith("rst/examples/"):
        raise ValueError(f"code artifact must be under rst/examples/: {relative}")
    resolved = (root / path).resolve()
    if not resolved.is_relative_to((root / "rst/examples").resolve()):
        raise ValueError(f"code artifact escapes rst/examples/: {relative}")
    return resolved


def slice_bytes(lines: list[bytes], record: dict) -> bytes:
    start, end = record["start_line"] - 1, record["end_line"]
    if not 0 <= start <= end <= len(lines):
        raise ValueError(f"invalid code range {start + 1}:{end} in {len(lines)} lines")
    return b"".join(lines[start:end])


def source_records(projection: dict) -> list[dict]:
    return [projection, *(segment["source"] for segment in projection.get("segments", []) if "source" in segment)]


def validate(data: dict, root: Path, *, hashes: bool = True) -> None:
    if data.get("schema") != "mpg-code-v1":
        raise ValueError("expected mpg-code-v1 manifest")
    artifacts = {}
    ids = set()
    for artifact in data["artifacts"]:
        relative = artifact["path"]
        if relative in artifacts or artifact["id"] in ids:
            raise ValueError(f"duplicate code artifact path or id: {relative}")
        if artifact["validation"] not in {"compiled", "display-only"}:
            raise ValueError(f"unknown validation kind: {relative}")
        payload = source_path(root, relative).read_bytes()
        if hashes and any(artifact.get(k) != v for k, v in fingerprint(payload).items()):
            raise ValueError(f"stale artifact {relative}; run code.py refresh")
        artifacts[relative] = payload.splitlines(keepends=True)
        ids.add(artifact["id"])
    for key, projection in data["projections"].items():
        relative = projection["artifact"]
        if relative not in artifacts:
            raise ValueError(f"{key}: unknown artifact {relative}")
        lines = artifacts[relative]
        for record in source_records(projection):
            payload = slice_bytes(lines, record)
            if hashes and any(record.get(k) != v for k, v in fingerprint(payload).items()):
                raise ValueError(f"stale projection {key}; run code.py refresh")
        previous = projection["start_line"] - 1
        for segment in projection.get("segments", []):
            if ("source" in segment) == ("text" in segment):
                raise ValueError(f"{key}: segment needs exactly one of source or text")
            if "child" in segment and segment["child"] not in data["projections"]:
                raise ValueError(f"{key}: unknown child {segment['child']}")
            if "source" in segment:
                record = segment["source"]
                if record["start_line"] - 1 < previous or record["end_line"] > projection["end_line"]:
                    raise ValueError(f"{key}: source segments overlap or leave the projection range")
                previous = record["end_line"]
    for chapter in sorted((root / "rst/content").rglob("*.rst")):
        for number, line in enumerate(chapter.read_text(encoding="utf-8").splitlines(), 1):
            match = re.match(r"\s*\.\. mpg-code::\s*(.*?)\s*$", line)
            if match and match[1] not in data["projections"]:
                raise ValueError(f"{chapter.relative_to(root)}:{number}: unknown code projection {match[1]!r}")


def git_bytes(root: Path, base: str, path: str) -> bytes:
    result = subprocess.run(["git", "show", f"{base}:{path}"], cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        raise ValueError(f"cannot read {path} at {base}; use --no-relocate for authored ranges")
    return result.stdout


def relocate(record: dict, before: list[bytes], after: list[bytes], opcodes: list) -> tuple[int, int]:
    """Map a half-open excerpt through edits without guessing crossed boundaries."""
    start, end = record["start_line"] - 1, record["end_line"]
    slice_bytes(before, record)
    if start == 0 and end == len(before):
        if before and not after:
            raise ValueError("the entire excerpt was deleted")
        return 1, len(after)
    for tag, a, b, c, d in opcodes:
        if tag != "equal" and a < b and (a < start < b or a < end < b):
            raise ValueError("an edit crosses an excerpt boundary")

    def boundary(position: int, is_start: bool) -> int:
        for tag, a, b, c, d in opcodes:
            if tag == "insert" and a == position:
                return d if is_start else c
        for tag, a, b, c, d in opcodes:
            if a <= position <= b:
                if tag == "equal":
                    return c + position - a
                if position == a:
                    return c
                if position == b:
                    return d
        return len(after)

    moved_start = boundary(start, True)
    moved_end = boundary(end, False) if end > start else moved_start
    if end > start and moved_end <= moved_start:
        raise ValueError("the entire excerpt was deleted")
    return moved_start + 1, moved_end


def refresh(data: dict, root: Path, base: str = "HEAD", no_relocate: bool = False) -> None:
    baseline = None if no_relocate else json.loads(git_bytes(root, base, MANIFEST))
    old_artifacts = {} if baseline is None else {row["path"]: row for row in baseline["artifacts"]}
    sources = {}
    for artifact in data["artifacts"]:
        relative = artifact["path"]
        payload = source_path(root, relative).read_bytes()
        after = payload.splitlines(keepends=True)
        before = git_bytes(root, base, relative).splitlines(keepends=True) if relative in old_artifacts else after
        opcodes = difflib.SequenceMatcher(None, before, after, autojunk=False).get_opcodes() if before != after else []
        sources[relative] = before, after, opcodes
        artifact.update(fingerprint(payload))
    for key, projection in data["projections"].items():
        before, after, opcodes = sources[projection["artifact"]]
        old = baseline["projections"].get(key) if baseline else None
        records = source_records(projection)
        if old and old["artifact"] == projection["artifact"]:
            old_records = source_records(old)
            if len(records) != len(old_records):
                raise ValueError(f"{key}: projection structure changed; use --no-relocate")
            for record, old_record in zip(records, old_records):
                try:
                    start, end = relocate(old_record, before, after, opcodes) if opcodes else (old_record["start_line"], old_record["end_line"])
                except ValueError as error:
                    raise ValueError(f"{key}: {error}; review ranges and use --no-relocate") from error
                record.update(start_line=start, end_line=end)
        for record in records:
            record.update(fingerprint(slice_bytes(after, record)))
    validate(data, root)


def add(data: dict, root: Path, key: str, relative: str, lines: str | None, language: str, validation: str, title: str | None) -> None:
    if not key.strip() or key in data["projections"]:
        raise ValueError(f"projection key is blank or already exists: {key!r}")
    payload = source_path(root, relative).read_bytes()
    source_lines = payload.splitlines(keepends=True)
    start, end = (1, len(source_lines)) if lines is None else map(int, lines.split(":"))
    record = {"start_line": start, "end_line": end}
    record.update(fingerprint(slice_bytes(source_lines, record)))
    artifact = next((row for row in data["artifacts"] if row["path"] == relative), None)
    if artifact is None:
        ident = Path(relative).stem
        if any(row["id"] == ident for row in data["artifacts"]):
            raise ValueError(f"artifact id {ident!r} already exists; use a unique filename")
        data["artifacts"].append({"id": ident, "path": relative, "language": language, "validation": validation, **fingerprint(payload)})
    elif artifact["language"] != language or artifact["validation"] != validation:
        raise ValueError(f"{relative}: language/validation disagree with existing artifact")
    projection = {"artifact": relative, "kind": "snippet", "language": language, **record}
    if title is not None:
        projection["title"] = title
    data["projections"][key] = projection
    validate(data, root)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("check", help="check source bytes, excerpts, segments, and RST references")
    update = commands.add_parser("refresh", help="refresh hashes and relocate committed excerpts after code edits")
    update.add_argument("--base", default="HEAD", help="committed source and manifest baseline (default: HEAD)")
    update.add_argument("--no-relocate", action="store_true", help="keep explicitly authored line ranges; no Git baseline needed")
    register = commands.add_parser("add", help="register one source excerpt (whole file by default)")
    register.add_argument("key")
    register.add_argument("path", help="repository-relative path under rst/examples/")
    register.add_argument("--lines", metavar="START:END", help="inclusive line range")
    register.add_argument("--language", default="cpp")
    register.add_argument("--validation", choices=("compiled", "display-only"), default="display-only")
    register.add_argument("--title", help="optional unnumbered listing title")
    args = parser.parse_args()
    try:
        path = ROOT / MANIFEST
        data = json.loads(path.read_text(encoding="utf-8"))
        if args.command == "refresh":
            refresh(data, ROOT, args.base, args.no_relocate)
        elif args.command == "add":
            add(data, ROOT, args.key, args.path, args.lines, args.language, args.validation, args.title)
        else:
            validate(data, ROOT)
        if args.command != "check":
            path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f"code {args.command}: {error}\n")
    print(f"code {args.command}: {len(data['artifacts'])} artifacts, {len(data['projections'])} projections")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
