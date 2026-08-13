"""Generate and verify the per-source MPG migration coverage contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any


PART_DESTINATIONS = {
    "part:m": "rst/content/parts/modeling.rst",
    "part:c": "rst/content/parts/case-studies.rst",
    "part:p": "rst/content/parts/propagators.rst",
    "part:b": "rst/content/parts/branchers.rst",
    "part:v": "rst/content/parts/variables.rst",
    "part:s": "rst/content/parts/search-engines.rst",
}


def destination_for(source: str) -> str | None:
    name = Path(source).name.removesuffix(".tex.in").removesuffix(".tex")
    if "/chapters/core/" in source:
        return "rst/content/core/intro.rst" if name == "intro" else f"rst/content/core/{name}.rst"
    if "/chapters/modeling/" in source:
        return f"rst/content/modeling/{name.removeprefix('m-')}.rst"
    if "/chapters/case-studies/" in source:
        return f"rst/content/case-studies/{name.removeprefix('c-')}.rst"
    if "/chapters/programming/" in source:
        return f"rst/content/propagators/{name.removeprefix('p-')}.rst"
    if "/chapters/search/" in source and name.startswith("b-"):
        return f"rst/content/branchers/{name.removeprefix('b-')}.rst"
    if "/chapters/search/" in source and name.startswith("s-"):
        return f"rst/content/search-engines/{name.removeprefix('s-')}.rst"
    if "/chapters/appendix/" in source:
        return "rst/content/variables/index.rst"
    if "/chapters/meta/" in source:
        return f"rst/content/backmatter/{name}.rst"
    if source.endswith("static/license.tex"):
        return "rst/content/backmatter/license.rst"
    return None


def _item(kind: str, occurrence: dict[str, Any], destination: str | None, verification: str) -> dict[str, Any]:
    return {
        "key": f"{kind}:{occurrence['source']}:{occurrence['line']}:{occurrence['id']}",
        "kind": kind,
        "source": occurrence["source"],
        "line": occurrence["line"],
        "id": occurrence["id"],
        "destination": destination,
        "disposition": "required",
        "verification": verification,
    }


def build_contract(legacy: dict[str, Any]) -> dict[str, Any]:
    source_mappings = []
    template_destinations = [
        "rst/content/index.rst", "rst/content/parts/modeling.rst",
        "rst/content/parts/case-studies.rst", "rst/content/parts/propagators.rst",
        "rst/content/parts/branchers.rst", "rst/content/parts/variables.rst",
        "rst/content/parts/search-engines.rst", "rst/content/backmatter/changelog.rst",
        "rst/content/backmatter/license.rst",
    ]
    for record in legacy["sources"]:
        source = record["path"]
        if "/chapters/" in source or source.endswith("static/license.tex"):
            source_mappings.append({"source": source, "destination": destination_for(source), "disposition": "convert"})
        elif source.endswith("template/MPG.tex.in.in"):
            source_mappings.append({"source": source, "destinations": template_destinations, "disposition": "decompose"})
        elif source.endswith("static/macros.tex"):
            source_mappings.append({"source": source, "destination": "rst/_static/latex/mpg-classic.sty", "disposition": "reimplement"})
        elif "/bib/" in source:
            source_mappings.append({"source": source, "destination": "rst/content/references.bib", "disposition": "merge-bibliography"})
        else:
            source_mappings.append({"source": source, "destination": None, "disposition": "unassigned"})

    items: list[dict[str, Any]] = []
    for occurrence in legacy["labels"]:
        destination = PART_DESTINATIONS.get(occurrence["id"]) if occurrence["source"].endswith("MPG.tex.in.in") else destination_for(occurrence["source"])
        # Labels in macro definitions are parameter placeholders, not content.
        if occurrence["id"].startswith("#"):
            continue
        items.append(_item("label", occurrence, destination, "exact-rst-anchor"))
    for occurrence in legacy["citations"]:
        items.append(_item("citation", occurrence, destination_for(occurrence["source"]), "exact-citation-role"))
    for occurrence in legacy["tips"]:
        verification = "exact-rst-anchor" if not occurrence["id"].startswith("unlabeled-") else "coverage-marker"
        items.append(_item("tip", occurrence, destination_for(occurrence["source"]), verification))
    for occurrence in legacy["figures"]:
        verification = "exact-rst-anchor" if not occurrence["id"].startswith("unlabeled-") else "coverage-marker"
        items.append(_item("figure", occurrence, destination_for(occurrence["source"]), verification))
        if occurrence.get("caption") is not None:
            items.append(_item("caption", occurrence, destination_for(occurrence["source"]), "coverage-marker"))
    for occurrence in legacy.get("tables", []) + legacy.get("tabulars", []):
        items.append(_item("table", occurrence, destination_for(occurrence["source"]), "coverage-marker"))
    for occurrence in legacy["literate"]["insertions"]:
        items.append(_item("literal-projection", occurrence, destination_for(occurrence["source"]), "coverage-marker"))

    return {
        "schema": "mpg-source-coverage-contract-v1",
        "marker_syntax": ".. mpg-covered: <contract item key>",
        "source_mappings": sorted(source_mappings, key=lambda x: x["source"]),
        "items": sorted(items, key=lambda x: (x["source"], x["line"], x["kind"], x["id"])),
        "totals": {
            "sources": len(source_mappings),
            "items": len(items),
            "by_kind": {kind: sum(x["kind"] == kind for x in items) for kind in sorted({x["kind"] for x in items})},
        },
    }


def _scan_destination(path: Path) -> dict[str, set[str]]:
    if not path.is_file():
        return {"labels": set(), "citations": set(), "markers": set()}
    text = path.read_text(encoding="utf-8")
    labels = set(re.findall(r"(?m)^\.\. _(.+):\s*$", text))
    # Named directives are the native way to attach a stable label to the
    # enumerable node itself.  This is required for numbered figure/program
    # references; a separate target immediately before the directive would
    # preserve the fragment but lose the number.
    labels.update(re.findall(r"(?m)^\s+:name:\s*(\S+)\s*$", text))
    citations: set[str] = set()
    for keys in re.findall(r":cite(?::[a-z]+)?:`([^`]+)`", text):
        citations.update(x.strip() for x in keys.split(",") if x.strip())
    markers = set(re.findall(r"(?m)^\.\. mpg-covered:\s*(.+?)\s*$", text))
    return {"labels": labels, "citations": citations, "markers": markers}


def verify_contract(contract: dict[str, Any], root: Path) -> dict[str, Any]:
    cache: dict[str, dict[str, set[str]]] = {}
    missing_sources = []
    missing_destinations = []
    for mapping in contract["source_mappings"]:
        if not (root / mapping["source"]).is_file():
            missing_sources.append(mapping["source"])
        destinations = mapping.get("destinations") or [mapping.get("destination")]
        for destination in destinations:
            if not destination or not (root / destination).is_file():
                missing_destinations.append({"source": mapping["source"], "destination": destination, "disposition": mapping["disposition"]})
    missing_items = []
    for item in contract["items"]:
        destination = item.get("destination")
        if not destination:
            missing_items.append({**item, "failure": "no destination assigned"})
            continue
        if destination not in cache:
            cache[destination] = _scan_destination(root / destination)
        scanned = cache[destination]
        verification = item["verification"]
        if verification == "exact-rst-anchor":
            present = item["id"] in scanned["labels"]
        elif verification == "exact-citation-role":
            present = item["id"] in scanned["citations"]
        elif verification == "coverage-marker":
            present = item["key"] in scanned["markers"]
        else:
            present = False
        if not present:
            missing_items.append({**item, "failure": f"missing {verification}"})
    complete = not missing_sources and not missing_destinations and not missing_items
    return {
        "schema": "mpg-source-coverage-report-v1",
        "complete": complete,
        "missing_sources": missing_sources,
        "missing_destinations": missing_destinations,
        "missing_items": missing_items,
        "totals": {"required_items": len(contract["items"]), "missing_items": len(missing_items)},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--generate", action="store_true")
    parser.add_argument("--output", type=Path, help="verification report output")
    args = parser.parse_args(argv)
    legacy = json.loads(args.manifest.read_text(encoding="utf-8"))
    generated = build_contract(legacy)
    rendered_contract = json.dumps(generated, indent=2) + "\n"
    if args.generate:
        args.contract.parent.mkdir(parents=True, exist_ok=True)
        args.contract.write_text(rendered_contract, encoding="utf-8")
        return 0
    if args.contract.read_text(encoding="utf-8") != rendered_contract:
        print(f"stale coverage contract: {args.contract}")
        return 2
    report = verify_contract(generated, args.root.resolve())
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if report["complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
