#!/usr/bin/env python3
"""One-time migration of MPG's TeX literate programs to canonical sources.

The checked output of this script is release input.  Sphinx and the example
test runner consume only ``rst/examples`` and the generated manifest; they do
not invoke TeX or the historical Perl extractor.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
CHAPTERS = ROOT / "docs" / "src" / "chapters"
LEGACY_ARTIFACTS = ROOT / ".mpg" / "generated" / "src"
EXAMPLES = ROOT / "rst" / "examples"
SOURCES = EXAMPLES / "src"
FRAGMENTS = EXAMPLES / "fragments"
MANIFEST = ROOT / "rst" / "manifests" / "code-projections.json"

BEGIN_CODE = re.compile(r"^(?P<indent>\s*)\\begin\{litcode\}(?:\[(?P<option>[^]]+)\])?\{(?P<name>[^}]*)\}(?:\{(?P<authors>[^}]*)\})?\s*$")
END_CODE = re.compile(r"^\s*\\end\{litcode\}\s*$")
BEGIN_BLOCK = re.compile(r"^(?P<indent>\s*)\\begin\{litblock\}\{(?P<name>.*)\}\s*$")
END_BLOCK = re.compile(r"^(?P<indent>\s*)\\end\{litblock\}\s*$")
INSERT = re.compile(r"\\(?P<small>insertsmalllitcode|insertlitcode)(?:\[(?P<mode>direct)\])?\{(?P<key>[^}]+)\}")
DIRECT_BEGIN = re.compile(r"^\s*\\begin\{(?P<kind>code|smallcode|cmd|smallcmd)\}\s*$")
DIRECT_END = re.compile(r"^\s*\\end\{(?P<kind>code|smallcode|cmd|smallcmd)\}\s*$")
LABEL = re.compile(r"\\label\{(?P<label>[^}]+)\}")
MARKER = re.compile(r"^\s*// __MPG_(?P<side>BEGIN|END)_(?P<id>\d{6})__\s*$")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def filename_for(name: str) -> str:
    value = "-".join(name.strip().split())
    return value if "." in value else value + ".cpp"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def chapter_sources() -> list[Path]:
    return sorted(CHAPTERS.rglob("*.tex.in"))


def scan_direct_snippets(path: Path) -> list[dict]:
    """Inventory non-literate code/command displays in authoring order."""
    rows: list[dict] = []
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    in_litcode = False
    active: dict | None = None
    context = "document"
    context_counts: dict[tuple[str, str], int] = {}
    chapter = path.name.removesuffix(".tex.in")
    for line_no, line in enumerate(lines, 1):
        if BEGIN_CODE.match(line.rstrip("\n")):
            in_litcode = True
        if in_litcode:
            if END_CODE.match(line.rstrip("\n")):
                in_litcode = False
            continue
        label = LABEL.search(line)
        if label:
            context = label.group("label")
        if active is None:
            match = DIRECT_BEGIN.match(line.rstrip("\n"))
            if not match:
                continue
            kind = match.group("kind")
            base_kind = "cmd" if "cmd" in kind else "code"
            counter_key = (context, base_kind)
            context_counts[counter_key] = context_counts.get(counter_key, 0) + 1
            ordinal = context_counts[counter_key]
            safe_context = re.sub(r"[^a-zA-Z0-9_.:-]+", "-", context).strip("-").lower()
            key = f"snippet:{chapter}:{safe_context}:{base_kind}:{ordinal}"
            active = {
                "key": key,
                "kind": base_kind,
                "small": kind.startswith("small"),
                "source": rel(path),
                "source_line": line_no,
                "content": [],
            }
            continue
        end = DIRECT_END.match(line.rstrip("\n"))
        if end:
            rows.append(active)
            active = None
        else:
            active["content"].append(line)
    if active is not None:
        raise RuntimeError(f"unclosed direct code environment in {path}:{active['source_line']}")
    return rows


def instrument(path: Path, counter: list[int]) -> tuple[str, list[dict], list[dict]]:
    """Add inert C++ markers and return unit/block metadata and insertions."""
    output: list[str] = []
    stack: list[dict] = []
    units: list[dict] = []
    insertions: list[dict] = []
    current: dict | None = None
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        for match in INSERT.finditer(line):
            insertions.append({
                "key": match.group("key"),
                "source": rel(path),
                "line": line_no,
                "small": match.group("small") == "insertsmalllitcode",
                "direct": match.group("mode") == "direct",
            })
        match = BEGIN_CODE.match(line)
        if match:
            counter[0] += 1
            current = {
                "id": counter[0],
                "key": match.group("name"),
                "source": rel(path),
                "source_line": line_no,
                "texonly": match.group("option") == "texonly",
                "authors": match.group("authors") or "",
                "blocks": [],
            }
            units.append(current)
            output.append(line)
            if not current["texonly"]:
                output.append(f"// __MPG_BEGIN_{current['id']:06d}__")
            continue
        if current is not None and END_CODE.match(line):
            if stack:
                raise RuntimeError(f"unclosed litblock in {path}:{line_no}")
            if not current["texonly"]:
                output.append(f"// __MPG_END_{current['id']:06d}__")
            current["source_end_line"] = line_no
            output.append(line)
            current = None
            continue
        if current is not None:
            match = BEGIN_BLOCK.match(line)
            if match:
                counter[0] += 1
                block = {
                    "id": counter[0],
                    "name": match.group("name"),
                    "source": rel(path),
                    "source_line": line_no,
                    "parent_id": stack[-1]["id"] if stack else current["id"],
                    "unit_id": current["id"],
                }
                current["blocks"].append(block)
                stack.append(block)
                output.append(line)
                if not current["texonly"] and block["name"] != "texonly":
                    output.append(match.group("indent") + f"// __MPG_BEGIN_{block['id']:06d}__")
                continue
            match = END_BLOCK.match(line)
            if match:
                if not stack:
                    raise RuntimeError(f"unmatched litblock end in {path}:{line_no}")
                block = stack.pop()
                block["source_end_line"] = line_no
                if not current["texonly"] and block["name"] != "texonly":
                    output.append(match.group("indent") + f"// __MPG_END_{block['id']:06d}__")
                output.append(line)
                continue
        output.append(line)
    if current is not None:
        raise RuntimeError(f"unclosed litcode in {path}")
    return "\n".join(output) + "\n", units, insertions


def texonly_artifact(unit: dict) -> tuple[bytes, dict[int, tuple[int, int]]]:
    """Turn an intentional display-only unit into a canonical fragment file."""
    path = ROOT / unit["source"]
    source = path.read_text(encoding="utf-8").splitlines(keepends=True)
    by_start = {block["source_line"]: block for block in unit["blocks"]}
    by_end = {block["source_end_line"]: block for block in unit["blocks"]}
    output: list[str] = []
    starts: dict[int, int] = {unit["id"]: 0}
    spans: dict[int, tuple[int, int]] = {}
    for line_no in range(unit["source_line"] + 1, unit["source_end_line"]):
        if line_no in by_start:
            starts[by_start[line_no]["id"]] = len(output)
            continue
        if line_no in by_end:
            block = by_end[line_no]
            spans[block["id"]] = (starts[block["id"]], len(output))
            continue
        output.append(source[line_no - 1])
    spans[unit["id"]] = (0, len(output))
    return "".join(output).encode("utf-8"), spans


def run_instrumented(source: Path, text: str, workspace: Path) -> dict[str, list[str]]:
    (workspace / "bin").symlink_to(ROOT / "bin", target_is_directory=True)
    result = subprocess.run(
        ["perl", str(ROOT / "bin" / "gl.perl"), "2026"],
        cwd=workspace,
        input=text,
        text=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    if result.returncode:
        raise RuntimeError(f"legacy instrumentation failed for {source}: {result.stderr}")
    return {p.name: p.read_text(encoding="utf-8").splitlines(keepends=True) for p in workspace.iterdir() if p.suffix in {".cpp", ".hh"}}


def strip_markers(lines: list[str]) -> tuple[list[str], dict[int, tuple[int, int]]]:
    clean: list[str] = []
    starts: dict[int, int] = {}
    spans: dict[int, tuple[int, int]] = {}
    for line in lines:
        match = MARKER.match(line.rstrip("\n"))
        if not match:
            clean.append(line)
            continue
        ident = int(match.group("id"))
        if match.group("side") == "BEGIN":
            starts[ident] = len(clean)
        else:
            if ident not in starts:
                raise RuntimeError(f"end marker without start: {ident}")
            spans[ident] = (starts.pop(ident), len(clean))
    if starts:
        raise RuntimeError(f"unclosed source markers: {sorted(starts)}")
    return clean, spans


def fragment_record(lines: list[str], start: int, end: int) -> dict:
    data = "".join(lines[start:end]).encode("utf-8")
    return {"start_line": start + 1, "end_line": end, "sha256": digest(data), "bytes": len(data)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare generated data without changing checked files")
    args = parser.parse_args()
    if not LEGACY_ARTIFACTS.exists():
        raise SystemExit("missing .mpg/generated/src; run the legacy extraction once to bootstrap")

    counter = [0]
    all_units: list[dict] = []
    all_insertions: list[dict] = []
    direct_snippets: list[dict] = []
    instrumented: list[tuple[Path, str]] = []
    for path in chapter_sources():
        text, units, insertions = instrument(path, counter)
        instrumented.append((path, text))
        all_units.extend(units)
        all_insertions.extend(insertions)
        direct_snippets.extend(scan_direct_snippets(path))

    staged_sources: dict[str, bytes] = {}
    staged_fragments: dict[str, bytes] = {}
    staged_snippets: dict[str, bytes] = {}
    spans: dict[int, tuple[str, int, int]] = {}
    with tempfile.TemporaryDirectory(prefix="mpg-code-migration-") as temp:
        temp_root = Path(temp)
        for ordinal, (path, text) in enumerate(instrumented):
            workspace = temp_root / f"chapter-{ordinal:03d}"
            workspace.mkdir()
            generated = run_instrumented(path, text, workspace)
            for name, marked_lines in generated.items():
                clean, file_spans = strip_markers(marked_lines)
                data = "".join(clean).encode("utf-8")
                legacy = LEGACY_ARTIFACTS / name
                if not legacy.exists() or legacy.read_bytes() != data:
                    raise RuntimeError(f"instrumented extraction did not reproduce {legacy}")
                previous = staged_sources.setdefault(name, data)
                if previous != data:
                    raise RuntimeError(f"two literate units generate different {name}")
                for ident, (start, end) in file_spans.items():
                    spans[ident] = (name, start, end)

    units_by_id = {unit["id"]: unit for unit in all_units}
    blocks_by_id = {block["id"]: block for unit in all_units for block in unit["blocks"]}
    projections: dict[str, dict] = {}
    occurrences: list[dict] = []
    key_by_node: dict[int, str] = {}
    span_by_node: dict[int, tuple[str, int, int]] = {}
    name_by_node: dict[int, str] = {}
    parent_by_node: dict[int, int] = {}
    for unit in all_units:
        if unit["texonly"]:
            filename = filename_for(unit["key"])
            data, local_spans = texonly_artifact(unit)
            staged_fragments[filename] = data
            lines = data.decode("utf-8").splitlines(keepends=True)
            start, end = local_spans[unit["id"]]
            artifact_path = f"rst/examples/fragments/{filename}"
        else:
            filename, start, end = spans[unit["id"]]
            lines = staged_sources[filename].decode("utf-8").splitlines(keepends=True)
            local_spans = {block["id"]: spans[block["id"]][1:] for block in unit["blocks"] if block["id"] in spans}
            artifact_path = f"rst/examples/src/{filename}"
        record = {
            "artifact": artifact_path,
            "kind": "skeleton",
            **fragment_record(lines, start, end),
            "source": unit["source"],
            "source_line": unit["source_line"],
            "language": "cpp",
        }
        if unit["key"] in projections:
            raise RuntimeError(f"duplicate projection key: {unit['key']}")
        projections[unit["key"]] = record
        key_by_node[unit["id"]] = unit["key"]
        span_by_node[unit["id"]] = (artifact_path, start, end)
        name_by_node[unit["id"]] = unit["key"]
        occurrences.append({"key": unit["key"], "node_id": unit["id"]})
        name_counts: dict[str, int] = {}
        for block in unit["blocks"]:
            name = block["name"]
            if name == "texonly":
                continue
            name_counts[name] = name_counts.get(name, 0) + 1
            if unit["texonly"]:
                bstart, bend = local_spans[block["id"]]
            else:
                filename2, bstart, bend = spans[block["id"]]
                if filename2 != filename:
                    raise RuntimeError("block and unit mapped to different artifacts")
            semantic = f"{unit['key']}:{name}"
            occurrence = name_counts[name]
            unique = semantic if occurrence == 1 else f"{semantic}#{occurrence}"
            entry = {
                "artifact": artifact_path,
                "kind": "fragment",
                **fragment_record(lines, bstart, bend),
                "source": block["source"],
                "source_line": block["source_line"],
                "parent_node_id": block["parent_id"],
                "language": "cpp",
            }
            # Anonymous blocks are occurrence-addressable inventory entries, not
            # stable authoring names.  Named duplicates retain #N disambiguation.
            projections[unique] = entry
            key_by_node[block["id"]] = unique
            span_by_node[block["id"]] = (artifact_path, bstart, bend)
            name_by_node[block["id"]] = name
            parent_by_node[block["id"]] = block["parent_id"]
            occurrences.append({"key": unique, "node_id": block["id"]})

    # A projection is a graph of hash-checked source ranges.  Direct children
    # are replaced with the same sort of concise placeholders used by MPG's
    # original literate listings.  This is what keeps the crossword's large
    # anonymous dictionary out of the whole-program listing.
    children_by_parent: dict[int, list[int]] = {}
    for node_id, parent_id in parent_by_node.items():
        children_by_parent.setdefault(parent_id, []).append(node_id)
    for node_id, key in key_by_node.items():
        artifact_path, start, end = span_by_node[node_id]
        artifact_data = staged_sources.get(Path(artifact_path).name, staged_fragments.get(Path(artifact_path).name))
        assert artifact_data is not None
        lines = artifact_data.decode("utf-8").splitlines(keepends=True)
        cursor = start
        segments: list[dict] = []
        children = sorted(children_by_parent.get(node_id, []), key=lambda child: span_by_node[child][1])
        for child in children:
            _, child_start, child_end = span_by_node[child]
            child_name = name_by_node[child]
            cover_start = child_start
            if child_name not in {"anonymous", "ignore", "texonly"} and child_start > cursor:
                # gl.perl writes ``// block name`` immediately before our start
                # marker for named blocks.  It belongs to the collapsed child.
                cover_start -= 1
            if cover_start > cursor:
                segments.append({"source": fragment_record(lines, cursor, cover_start)})
            indent = ""
            probe = lines[cover_start] if cover_start < len(lines) else ""
            indent = probe[: len(probe) - len(probe.lstrip())]
            if child_name == "anonymous":
                segments.append({"text": indent + "...\n", "child": key_by_node[child]})
            elif child_name == "ignore":
                segments.append({"text": "", "child": key_by_node[child]})
            elif child_name != "texonly":
                segments.append({"text": indent + f"// [{key_by_node[child]}]\n", "child": key_by_node[child]})
            cursor = child_end
        if cursor < end:
            segments.append({"source": fragment_record(lines, cursor, end)})
        projections[key]["segments"] = segments

    # Direct ``code`` and ``cmd`` environments are canonical projections too.
    # Their semantic key is anchored in the preceding explicit section label,
    # not in a generated TeX line number.
    direct_sites: list[dict] = []
    chapter_ordinals: dict[str, int] = {}
    for row in direct_snippets:
        chapter = Path(row["source"]).name.removesuffix(".tex.in")
        chapter_ordinals[chapter] = chapter_ordinals.get(chapter, 0) + 1
        extension = ".sh" if row["kind"] == "cmd" else ".cpp"
        filename = f"snippets/{chapter}/{row['kind']}-{chapter_ordinals[chapter]:03d}{extension}"
        data = "".join(row["content"]).encode("utf-8")
        staged_snippets[filename] = data
        source_lines = data.decode("utf-8").splitlines(keepends=True)
        projection = {
            "artifact": f"rst/examples/fragments/{filename}",
            "kind": "command" if row["kind"] == "cmd" else "snippet",
            **fragment_record(source_lines, 0, len(source_lines)),
            "source": row["source"],
            "source_line": row["source_line"],
            "small": row["small"],
            "language": "console" if row["kind"] == "cmd" else "cpp",
            "segments": [{"source": fragment_record(source_lines, 0, len(source_lines))}],
        }
        projections[row["key"]] = projection
        direct_sites.append({k: row[k] for k in ("key", "kind", "small", "source", "source_line")})

    missing_insertions = sorted({row["key"] for row in all_insertions if row["key"] not in projections})
    if missing_insertions:
        raise RuntimeError(f"insertions without canonical projections: {missing_insertions}")

    artifacts = []
    for name, data in sorted(staged_sources.items()):
        artifacts.append({
            "id": Path(name).stem,
            "path": f"rst/examples/src/{name}",
            "sha256": digest(data),
            "bytes": len(data),
            "language": "cpp",
            "validation": "compiled",
        })
    for name, data in sorted(staged_fragments.items()):
        artifacts.append({
            "id": "fragment-" + Path(name).stem,
            "path": f"rst/examples/fragments/{name}",
            "sha256": digest(data),
            "bytes": len(data),
            "language": "cpp",
            "validation": "display-only",
            "reason": "legacy texonly pseudocode or incomplete sketch",
        })
    for name, data in sorted(staged_snippets.items()):
        is_command = name.endswith(".sh")
        artifacts.append({
            "id": "snippet-" + name.replace("/", "-").rsplit(".", 1)[0],
            "path": f"rst/examples/fragments/{name}",
            "sha256": digest(data),
            "bytes": len(data),
            "language": "console" if is_command else "cpp",
            "validation": "display-only",
            "reason": "command transcript" if is_command else "illustrative source fragment",
        })

    display_sites = [
        dict(row, source_line=row["line"], site_kind="literate-insertion")
        for row in all_insertions
    ]
    display_sites.extend(dict(row, site_kind="direct-display") for row in direct_sites)
    display_sites.sort(key=lambda row: (row["source"], row["source_line"]))
    display_count: dict[str, int] = {}
    for row in display_sites:
        display_count[row["source"]] = display_count.get(row["source"], 0) + 1
        row["display_ordinal"] = display_count[row["source"]]
    manifest = {
        "schema": "mpg-code-v1",
        "artifact_count": len(artifacts),
        "block_count": sum(len(unit["blocks"]) for unit in all_units),
        "insertion_count": len(all_insertions),
        "projection_count": len(projections),
        "artifacts": artifacts,
        "projections": dict(sorted(projections.items())),
        "insertions": all_insertions,
        "direct_display_count": len(direct_sites),
        "display_site_count": len(display_sites),
        "display_sites": display_sites,
        "texonly_units": [
            {k: unit[k] for k in ("key", "source", "source_line")}
            for unit in all_units if unit["texonly"]
        ],
    }
    manifest_data = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")

    if args.check:
        failures = []
        for name, data in staged_sources.items():
            target = SOURCES / name
            if not target.exists() or target.read_bytes() != data:
                failures.append(rel(target))
        for name, data in staged_fragments.items():
            target = FRAGMENTS / name
            if not target.exists() or target.read_bytes() != data:
                failures.append(rel(target))
        for name, data in staged_snippets.items():
            target = FRAGMENTS / name
            if not target.exists() or target.read_bytes() != data:
                failures.append(rel(target))
        if not MANIFEST.exists() or MANIFEST.read_bytes() != manifest_data:
            failures.append(rel(MANIFEST))
        if failures:
            raise SystemExit("stale canonical code migration: " + ", ".join(failures))
        print(f"canonical code migration is current: {len(artifacts)} artifacts, {len(projections)} projections")
        return 0

    SOURCES.mkdir(parents=True, exist_ok=True)
    for name, data in staged_sources.items():
        (SOURCES / name).write_bytes(data)
    FRAGMENTS.mkdir(parents=True, exist_ok=True)
    for name, data in staged_fragments.items():
        (FRAGMENTS / name).write_bytes(data)
    for name, data in staged_snippets.items():
        target = FRAGMENTS / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_bytes(manifest_data)
    print(f"migrated {len(artifacts)} artifacts and {len(projections)} projections")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
