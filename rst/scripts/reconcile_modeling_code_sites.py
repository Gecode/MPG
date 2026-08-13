#!/usr/bin/env python3
"""Reconcile migrated modeling code directives with the canonical display order.

This is a deliberately narrow migration helper.  It only corrects projection
keys at already existing display positions; missing displays are placed by the
content migration after inspecting their semantic scope.
"""

from __future__ import annotations

import difflib
from collections import Counter
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "rst/manifests/code-projections.json"
DIRECTIVE = re.compile(r"^(\s*\.\. mpg-code::\s+)(.+?)(\s*)$")


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    sources = sorted({
        row["source"] for row in manifest["display_sites"]
        if "/modeling/" in row["source"]
    })
    changed = 0
    replaced_literals = 0
    for source in sources:
        name = Path(source).name.removeprefix("m-").replace(".tex.in", ".rst")
        target = ROOT / "rst/content/modeling" / name
        if not target.exists():
            continue
        expected = [row["key"] for row in manifest["display_sites"] if row["source"] == source]
        lines = target.read_text(encoding="utf-8").splitlines()
        positions: list[int] = []
        actual: list[str] = []
        for index, line in enumerate(lines):
            match = DIRECTIVE.match(line)
            if match:
                positions.append(index)
                actual.append(match.group(2))
        matcher = difflib.SequenceMatcher(a=actual, b=expected, autojunk=False)
        for tag, a1, a2, b1, b2 in matcher.get_opcodes():
            if tag != "replace" or (a2 - a1) > (b2 - b1):
                continue
            for offset in range(a2 - a1):
                pos = positions[a1 + offset]
                match = DIRECTIVE.match(lines[pos])
                assert match is not None
                replacement = expected[b1 + offset]
                if match.group(2) != replacement:
                    lines[pos] = match.group(1) + replacement + match.group(3)
                    changed += 1
        # Pandoc represented the displays it could not understand as anonymous
        # reST literal blocks.  After correcting the keys above, their order is
        # exactly the order of the still-missing canonical display sites.
        actual = []
        for line in lines:
            match = DIRECTIVE.match(line)
            if match:
                actual.append(match.group(2))
        remaining = Counter(actual)
        missing: list[str] = []
        for key in expected:
            if remaining[key]:
                remaining[key] -= 1
            else:
                missing.append(key)
        sites = {
            row["key"]: row
            for row in manifest["display_sites"]
            if row["source"] == source
        }
        output: list[str] = []
        literal_index = 0
        index = 0
        while index < len(lines):
            marker = re.match(r"^(\s*)::\s*$", lines[index])
            if marker is None:
                output.append(lines[index])
                index += 1
                continue
            if literal_index >= len(missing):
                raise RuntimeError(f"more anonymous literal blocks than missing sites in {target}")
            key = missing[literal_index]
            site = sites[key]
            indent = marker.group(1)
            output.append(f"{indent}.. mpg-code:: {key}")
            if site.get("site_kind") == "direct-display" or site.get("direct"):
                output.append(f"{indent}   :direct:")
            if site.get("small"):
                output.append(f"{indent}   :small:")
            output.append("")
            index += 1
            while index < len(lines) and not lines[index].strip():
                index += 1
            while index < len(lines):
                line = lines[index]
                indentation = len(line) - len(line.lstrip())
                if line.strip() and indentation <= len(indent):
                    break
                index += 1
            literal_index += 1
            replaced_literals += 1
        if literal_index != len(missing):
            raise RuntimeError(
                f"{target}: replaced {literal_index} anonymous literal blocks "
                f"but {len(missing)} canonical displays remain"
            )
        # Normalize semantic display options occurrence-by-occurrence.  Direct
        # code/cmd environments encode directness in ``site_kind`` whereas
        # literate insertions carry an explicit ``direct`` boolean.
        normalized: list[str] = []
        occurrence = 0
        index = 0
        while index < len(output):
            match = DIRECTIVE.match(output[index])
            if match is None:
                normalized.append(output[index])
                index += 1
                continue
            if occurrence >= len(expected) or match.group(2) != expected[occurrence]:
                raise RuntimeError(f"{target}: code sequence diverged at occurrence {occurrence + 1}")
            site = manifest["display_sites"][0]
            # Keys may repeat, so select the occurrence from this source rather
            # than using the key-indexed convenience map above.
            source_sites = [row for row in manifest["display_sites"] if row["source"] == source]
            site = source_sites[occurrence]
            desired_direct = site.get("site_kind") == "direct-display" or bool(site.get("direct"))
            desired_small = bool(site.get("small"))
            normalized.append(output[index])
            index += 1
            options: list[str] = []
            while index < len(output) and re.match(r"^\s+:[^:]+:.*$", output[index]):
                if not re.match(r"^\s+:(?:direct|small):\s*$", output[index]):
                    options.append(output[index])
                index += 1
            indent = match.group(1).split("..")[0]
            if desired_direct:
                options.append(f"{indent}   :direct:")
            if desired_small:
                options.append(f"{indent}   :small:")
            normalized.extend(options)
            occurrence += 1
        if occurrence != len(expected):
            raise RuntimeError(f"{target}: found {occurrence} of {len(expected)} expected code sites")
        target.write_text("\n".join(normalized) + "\n", encoding="utf-8")
    print(f"corrected {changed} existing modeling projection keys")
    print(f"replaced {replaced_literals} anonymous literal blocks with canonical mpg-code sites")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
