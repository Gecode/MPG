"""Build the canonical, deterministic content inventory for legacy MPG."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
from typing import Any

try:
    from .tex import Command, commands
except ImportError:  # Direct execution: python rst/tools/inventory.py
    from tex import Command, commands


SCHEMA = "mpg-legacy-content-v1"
HEADING_COMMANDS = ("chapter", "chapter*", "section", "section*", "subsection", "subsection*", "subsubsection")
REF_COMMANDS = ("autoref", "ref", "pageref")
LITERATE_INSERTS = ("insertlitcode", "insertsmalllitcode")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _arg(command: Command, index: int = 0) -> str | None:
    values = command.required
    return values[index].strip() if len(values) > index else None


def _occurrence(command: Command, source: str, value: str, **extra: Any) -> dict[str, Any]:
    item: dict[str, Any] = {"id": value, "source": source, "line": command.line}
    item.update(extra)
    return item


def _source_files(root: Path) -> list[Path]:
    src = root / "docs" / "src"
    paths = [src / "template" / "MPG.tex.in.in"]
    paths += sorted((src / "chapters").rglob("*.tex.in"))
    paths += sorted((src / "static").glob("*.tex"))
    return paths


def _parse_book(template_commands: list[Command], chapters: dict[str, Path], root: Path) -> dict[str, Any]:
    parts: list[dict[str, Any]] = []
    front: list[str] = []
    back: list[str] = []
    current: dict[str, Any] | None = None
    bibliography_seen = False
    for command in template_commands:
        if command.name == "bibliography":
            bibliography_seen = True
        if command.name == "mypart" and len(command.required) >= 2:
            current = {
                "title": command.required[1].strip(),
                "legacy_number_width": command.required[0].strip(),
                "chapters": [],
                "source_line": command.line,
            }
            parts.append(current)
        elif command.name == "include" and command.required:
            name = command.required[0].strip()
            if name not in chapters:
                continue
            rel = _rel(chapters[name], root)
            if bibliography_seen:
                back.append(rel)
            elif current is None:
                front.append(rel)
            else:
                current["chapters"].append(rel)
    return {
        "front_matter": front,
        "parts": parts,
        "back_matter": back,
        "generated_front_matter": ["title-page", "publication-and-license-summary", "acknowledgments", "contents", "figures", "tips"],
        "generated_back_matter": ["bibliography"],
    }


def build_inventory(root: Path) -> dict[str, Any]:
    root = root.resolve()
    docs = root / "docs" / "src"
    if not docs.is_dir():
        raise FileNotFoundError(f"legacy source root not found: {docs}")
    paths = _source_files(root)
    missing = [str(p) for p in paths if not p.is_file()]
    if missing:
        raise FileNotFoundError("missing source files: " + ", ".join(missing))

    chapter_paths = sorted((docs / "chapters").rglob("*.tex.in"))
    chapters = {p.name.removesuffix(".tex.in"): p for p in chapter_paths}
    parsed: dict[Path, list[Command]] = {p: commands(p.read_text(encoding="utf-8")) for p in paths}
    template = docs / "template" / "MPG.tex.in.in"

    labels: list[dict[str, Any]] = []
    references: list[dict[str, Any]] = []
    citations: list[dict[str, Any]] = []
    tips: list[dict[str, Any]] = []
    figures: list[dict[str, Any]] = []
    tables: list[dict[str, Any]] = []
    tabulars: list[dict[str, Any]] = []
    headings: list[dict[str, Any]] = []
    literate_definitions: list[dict[str, Any]] = []
    literate_blocks: list[dict[str, Any]] = []
    literate_insertions: list[dict[str, Any]] = []
    graphics: list[dict[str, Any]] = []
    environments: Counter[str] = Counter()
    macros: Counter[str] = Counter()

    # gen-titles.perl turns chapter and modeling-section labels into shortcut
    # commands.  Recover the mapping from the maintained labels rather than
    # depending on a generated titles.tex file.
    label_values = []
    for path, calls in parsed.items():
        label_values.extend(_arg(c) for c in calls if c.name == "label" and _arg(c))
    title_macros: dict[str, str] = {}
    for label in label_values:
        if label.startswith("chap:"):
            suffix = label[len("chap:"):].replace(":", "").replace("_", "").replace("-", "")
            title_macros["tc" + suffix] = label
        elif label.startswith("sec:m:"):
            suffix = label[len("sec:"):].replace(":", "").replace("_", "").replace("-", "")
            title_macros["ts" + suffix] = label
            title_macros["pts" + suffix] = label

    for path in paths:
        source = _rel(path, root)
        calls = parsed[path]
        current_literate_file: str | None = None
        literate_stack: list[str] = []
        for c in calls:
            macros[c.name] += 1
            value = _arg(c)
            if c.name == "begin" and value:
                environments[value] += 1
                if value == "tabular":
                    tabulars.append(_occurrence(c, source, f"tabular@{source}:{c.line}", columns=c.required[1].strip() if len(c.required) >= 2 else None))
            if c.name in HEADING_COMMANDS and value is not None:
                headings.append(_occurrence(c, source, value, level=c.name))
            elif c.name == "label" and value:
                labels.append(_occurrence(c, source, value))
            elif c.name in REF_COMMANDS and value:
                references.append(_occurrence(c, source, value, kind=c.name))
            elif c.name == "otherref" and value:
                references.append(_occurrence(c, source, value, kind=c.name))
            elif c.name == "cite" and value:
                for key in (k.strip() for k in value.split(",")):
                    if key:
                        citations.append(_occurrence(c, source, key))
            elif c.name == "tip" and len(c.required) >= 2:
                body_labels = [nested.required[0].strip() for nested in commands(c.required[1]) if nested.name == "label" and nested.required]
                tips.append(_occurrence(c, source, body_labels[0] if body_labels else f"unlabeled-tip@{source}:{c.line}", title=c.required[0].strip(), labels=body_labels))
            elif c.name in LITERATE_INSERTS and value:
                literate_insertions.append(_occurrence(c, source, value, kind=c.name, direct="direct" in c.optional))
            elif c.name == "begin" and value == "litcode":
                required = c.required
                name = required[1].strip() if required and required[0] == "litcode" and len(required) > 1 else None
                # begin's first required argument is the environment name. Optional
                # arguments follow it, then litcode's required arguments.
                if len(required) >= 2:
                    name = required[1].strip()
                    current_literate_file = name
                    literate_stack = []
                    output = name.replace(" ", "-") if "." in name else name.replace(" ", "-") + ".cpp"
                    literate_definitions.append(_occurrence(c, source, name, texonly="texonly" in c.optional, author=required[2].strip() if len(required) >= 3 else None, output=output))
            elif c.name == "begin" and value == "litblock" and len(c.required) >= 2:
                name = c.required[1].strip()
                qualified = f"{current_literate_file}:{name}" if current_literate_file else name
                literate_blocks.append(_occurrence(c, source, qualified, name=name, file=current_literate_file, parent=literate_stack[-1] if literate_stack else None, depth=len(literate_stack), special=name in {"anonymous", "ignore", "texonly"}))
                literate_stack.append(name)
            elif c.name == "end" and value == "litblock":
                if literate_stack:
                    literate_stack.pop()
            elif c.name == "end" and value == "litcode":
                current_literate_file = None
                literate_stack = []
            elif c.name == "includegraphics" and value:
                graphics.append(_occurrence(c, source, value, options=list(c.optional)))
            if c.name in title_macros:
                references.append(_occurrence(c, source, title_macros[c.name], kind="generated-title-macro", macro=c.name))

        text = path.read_text(encoding="utf-8")
        for match in re.finditer(r"\\begin\{(figure|table)\}(.*?)\\end\{\1\}", text, flags=re.S):
            kind, body = match.group(1), match.group(2)
            line = text.count("\n", 0, match.start()) + 1
            body_calls = commands(body)
            item = {
                "id": next((_arg(x) for x in body_calls if x.name == "label" and _arg(x)), f"unlabeled-{kind}@{source}:{line}"),
                "source": source,
                "line": line,
                "caption": next((_arg(x) for x in body_calls if x.name == "caption" and _arg(x) is not None), None),
            }
            (figures if kind == "figure" else tables).append(item)

    label_counts = Counter(x["id"] for x in labels)
    duplicate_labels = sorted(k for k, count in label_counts.items() if count > 1)
    label_ids = set(label_counts)
    placeholders = sorted({x["id"] for x in references if x["id"].startswith("#")})
    unresolved = sorted({x["id"] for x in references if not x["id"].startswith("#") and x["id"] not in label_ids})

    bib_paths = sorted((docs / "bib").glob("*.bib*"))
    bib_entries: list[dict[str, str]] = []
    for path in bib_paths:
        for match in re.finditer(r"@([A-Za-z]+)\s*\{\s*([^,\s]+)", path.read_text(encoding="utf-8")):
            bib_entries.append({"id": match.group(2), "type": match.group(1).lower(), "source": _rel(path, root)})
    cited = {x["id"] for x in citations}
    known_bib = {x["id"] for x in bib_entries}

    asset_paths = sorted(p for p in (root / "images").glob("*") if p.is_file()) + sorted(p for p in (docs / "assets").glob("*") if p.is_file())
    assets = [{"path": _rel(p, root), "bytes": p.stat().st_size, "sha256": _sha256(p)} for p in asset_paths]
    stems = {p.with_suffix("").relative_to(root).as_posix() for p in asset_paths}
    missing_graphics = sorted({g["id"] for g in graphics if Path(g["id"]).with_suffix("").as_posix() not in stems})
    literate_targets = {x["id"] for x in literate_definitions} | {x["id"] for x in literate_blocks}
    unresolved_literate = []
    for insertion in literate_insertions:
        key = insertion["id"]
        if key in literate_targets:
            continue
        if any(target.endswith(":" + key) or key.endswith(":" + target) for target in literate_targets):
            continue
        unresolved_literate.append(key)

    source_records = []
    for path in paths + bib_paths:
        source_records.append({
            "path": _rel(path, root),
            "lines": len(path.read_text(encoding="utf-8").splitlines()),
            "bytes": path.stat().st_size,
            "sha256": _sha256(path),
        })

    def ordered(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return sorted(items, key=lambda x: (x["source"], x["line"], x["id"]))

    return {
        "schema": SCHEMA,
        "source_root": "docs/src",
        "book": _parse_book(parsed[template], chapters, root),
        "sources": sorted(source_records, key=lambda x: x["path"]),
        "headings": ordered(headings),
        "labels": ordered(labels),
        "references": ordered(references),
        "citations": ordered(citations),
        "bibliography": sorted(bib_entries, key=lambda x: (x["id"], x["source"])),
        "tips": ordered(tips),
        "figures": ordered(figures),
        "tables": ordered(tables),
        "tabulars": ordered(tabulars),
        "literate": {
            "definitions": ordered(literate_definitions),
            "blocks": ordered(literate_blocks),
            "insertions": ordered(literate_insertions),
        },
        "graphics_references": ordered(graphics),
        "assets": assets,
        "construct_counts": {
            "environments": dict(sorted(environments.items())),
            "macros": dict(sorted(macros.items())),
        },
        "integrity": {
            "duplicate_labels": duplicate_labels,
            "unresolved_explicit_references": unresolved,
            "template_reference_placeholders": placeholders,
            "missing_citation_keys": sorted(cited - known_bib),
            "missing_graphics": missing_graphics,
            "unresolved_literate_insertions": sorted(set(unresolved_literate)),
        },
        "totals": {
            "chapter_sources": len(chapter_paths),
            "source_files": len(source_records),
            "labels": len(labels),
            "references": len(references),
            "unique_citations": len(cited),
            "tips": len(tips),
            "figures": len(figures),
            "tables": len(tables),
            "tabulars": len(tabulars),
            "literate_files": len(literate_definitions),
            "literate_blocks": len(literate_blocks),
            "literate_insertions": len(literate_insertions),
            "graphics_references": len(graphics),
            "assets": len(assets),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path, help="fail if this checked-in manifest differs")
    args = parser.parse_args(argv)
    inventory = build_inventory(args.root)
    rendered = json.dumps(inventory, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    if args.check:
        expected = args.check.read_text(encoding="utf-8")
        if expected != rendered:
            print(f"stale parity manifest: {args.check}")
            return 1
    if not args.output and not args.check:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
