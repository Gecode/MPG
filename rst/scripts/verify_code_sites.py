#!/usr/bin/env python3
"""Prove that every legacy code display maps once to canonical ``mpg-code``."""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
CODE = ROOT / "rst/manifests/code-projections.json"
COVERAGE = ROOT / "rst/manifests/source-coverage.json"
REPORT = ROOT / "rst/_build/reports/code-sites.json"
MPG_CODE = re.compile(r"^\s*\.\. mpg-code::\s+(.+?)\s*$")
LITERAL = re.compile(r"^\s*\.\. literalinclude::\s+(.+?)\s*$")


def main() -> int:
    code = json.loads(CODE.read_text(encoding="utf-8"))
    coverage = json.loads(COVERAGE.read_text(encoding="utf-8"))
    destinations = {
        row["source"]: row["destination"]
        for row in coverage["source_mappings"] if row.get("destination")
    }
    expected: dict[str, list[str]] = {}
    for site in code["display_sites"]:
        expected.setdefault(site["source"], []).append(site["key"])

    errors: list[dict] = []
    actual_all: list[str] = []
    expected_all: list[str] = []
    for source, keys in sorted(expected.items()):
        destination = destinations.get(source)
        expected_all.extend(keys)
        if destination is None or not (ROOT / destination).exists():
            errors.append({"source": source, "kind": "missing-destination", "destination": destination, "expected": len(keys)})
            continue
        actual: list[str] = []
        for line_no, line in enumerate((ROOT / destination).read_text(encoding="utf-8").splitlines(), 1):
            match = MPG_CODE.match(line)
            if match:
                key = match.group(1)
                actual.append(key)
                actual_all.append(key)
                if key not in code["projections"]:
                    errors.append({"source": source, "destination": destination, "line": line_no, "kind": "unknown-projection", "key": key})
            match = LITERAL.match(line)
            if match and (".mpg/generated" in match.group(1) or "/programs/" in match.group(1) or match.group(1).startswith("programs/")):
                errors.append({"source": source, "destination": destination, "line": line_no, "kind": "legacy-or-divergent-literalinclude", "target": match.group(1)})
        if actual != keys:
            missing = list((Counter(keys) - Counter(actual)).elements())
            extra = list((Counter(actual) - Counter(keys)).elements())
            errors.append({"source": source, "destination": destination, "kind": "site-sequence-mismatch", "expected_count": len(keys), "actual_count": len(actual), "missing": missing, "extra": extra})

    expected_counts = Counter(expected_all)
    actual_counts = Counter(actual_all)
    ambiguous = {key: {"expected": count, "actual": actual_counts[key]} for key, count in expected_counts.items() if actual_counts[key] != count}
    if ambiguous:
        errors.append({"kind": "global-site-cardinality", "keys": ambiguous})
    report = {
        "schema": "mpg-code-site-verification-v1",
        "expected_sites": len(expected_all),
        "mapped_sites": len(actual_all),
        "chapters": len(expected),
        "errors": errors,
        "status": "pass" if not errors else "fail",
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"code-site verification: expected={len(expected_all)} mapped={len(actual_all)} errors={len(errors)}")
    print(f"report: {REPORT}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
