"""Compare migrated reST semantics with the canonical legacy inventory."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any


RST_LABEL = re.compile(r"(?m)^\.\. _(.+):\s*$")
RST_REF = re.compile(r":ref:`(?:[^`<>]+\s*<)?([^`<>]+)>?`")
RST_CITE = re.compile(r":cite(?::[a-z]+)?:`([^`]+)`")
RST_DIRECTIVE = re.compile(r"(?m)^\.\.\s+([\w-]+)::(?:\s*(.*))?$")


def scan_rst(root: Path) -> dict[str, Any]:
    labels: set[str] = set()
    refs: set[str] = set()
    citations: set[str] = set()
    directives: dict[str, int] = {}
    files = sorted(root.rglob("*.rst")) if root.exists() else []
    for path in files:
        text = path.read_text(encoding="utf-8")
        labels.update(RST_LABEL.findall(text))
        refs.update(RST_REF.findall(text))
        for group in RST_CITE.findall(text):
            citations.update(x.strip() for x in group.split(",") if x.strip())
        for name, _ in RST_DIRECTIVE.findall(text):
            directives[name] = directives.get(name, 0) + 1
    return {"files": len(files), "labels": sorted(labels), "references": sorted(refs), "citations": sorted(citations), "directives": dict(sorted(directives.items()))}


def compare(legacy: dict[str, Any], migrated: dict[str, Any]) -> dict[str, Any]:
    required_labels = {x["id"] for x in legacy["labels"]}
    required_citations = {x["id"] for x in legacy["citations"]}
    actual_labels = set(migrated["labels"])
    actual_citations = set(migrated["citations"])
    directives = migrated["directives"]
    semantic_counts = {
        "figures": directives.get("figure", 0),
        "tips": directives.get("tip", 0) + directives.get("mpg-tip", 0),
        "tables": directives.get("table", 0) + directives.get("list-table", 0) + directives.get("csv-table", 0),
        "program_directives": directives.get("mpg-program", 0) + directives.get("literalinclude", 0),
        "code_blocks": directives.get("code-block", 0) + directives.get("code", 0),
    }
    expected_semantic_counts = {
        "figures": len(legacy.get("figures", [])),
        "tips": len(legacy.get("tips", [])),
        "tables_or_tabulars": len(legacy.get("tables", [])) + len(legacy.get("tabulars", [])),
        "literate_files": len(legacy.get("literate", {}).get("definitions", [])),
        "literate_insertions": len(legacy.get("literate", {}).get("insertions", [])),
    }
    return {
        "schema": "mpg-rst-parity-report-v1",
        "complete": required_labels <= actual_labels and required_citations <= actual_citations,
        "legacy_totals": legacy["totals"],
        "migrated": migrated,
        "expected_semantic_counts": expected_semantic_counts,
        "migrated_semantic_counts": semantic_counts,
        "missing_labels": sorted(required_labels - actual_labels),
        "extra_labels": sorted(actual_labels - required_labels),
        "missing_citation_keys": sorted(required_citations - actual_citations),
        "extra_citation_keys": sorted(actual_citations - required_citations),
        "note": "Completion is gated by stable labels and citations. Semantic counts are review signals because one reST directive can replace several legacy TeX constructs.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--rst-root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    report = compare(json.loads(args.manifest.read_text(encoding="utf-8")), scan_rst(args.rst_root))
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if report["complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
