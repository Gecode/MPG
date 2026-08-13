#!/usr/bin/env python3
"""Freeze the Gecode links used by MPG from a release Doxygen tag file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET


RST_API = re.compile(r":api:`([^`]+)`")
EXAMPLE_CLASSES = {
    "bin-packing": "BinPacking",
    "crossword": "Crossword",
    "golf": "Golf",
    "golomb-ruler": "GolombRuler",
    "kakuro": "Kakuro",
    "magic-sequence": "MagicSequence",
    "nonogram": "Nonogram",
    "photo": "Photo",
    "warehouses": "Warehouses",
}


def api_targets(source: Path) -> list[str]:
    targets: set[str] = set()
    for path in sorted(source.rglob("*.rst")):
        for match in RST_API.finditer(path.read_text(encoding="utf-8")):
            value = match.group(1)
            explicit = re.fullmatch(r".*?\s*<([^<>]+)>", value)
            targets.add(explicit.group(1) if explicit else value)
    return sorted(targets)


def compounds(tag_file: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for compound in ET.parse(tag_file).getroot().findall("compound"):
        name = compound.findtext("name")
        filename = compound.findtext("filename")
        if name and filename:
            result[name] = filename
    return result


def resolve(target: str, available: dict[str, str]) -> tuple[str, str]:
    candidates = [target, f"Gecode::{target}"]
    if target in EXAMPLE_CLASSES:
        candidates.insert(0, EXAMPLE_CLASSES[target])
    elif target.startswith("knights:"):
        candidates.insert(0, target.partition(":")[2])
    hits = [(name, available[name]) for name in candidates if name in available]
    if not hits:
        raise ValueError(f"API target {target!r} is absent from the release Doxygen tag")
    name, url = hits[0]
    return name, url


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("rst/content"))
    parser.add_argument("--tag", type=Path, required=True)
    parser.add_argument("--html-root", type=Path)
    parser.add_argument("--version", required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()

    available = compounds(arguments.tag)
    objects = {}
    for target in api_targets(arguments.source):
        title, url = resolve(target, available)
        if arguments.html_root is not None and not (arguments.html_root / url).is_file():
            raise ValueError(f"Doxygen tag points at missing release page: {url}")
        objects[target] = {"title": title, "url": url}

    payload = {
        "schema_version": 1,
        "gecode_version": arguments.version,
        "base_url": f"/doc/{arguments.version}/reference/",
        "generated_by": "Gecode release Doxygen tag",
        "objects": objects,
    }
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"wrote {len(objects)} frozen references to {arguments.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
