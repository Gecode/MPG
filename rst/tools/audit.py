"""Audit all legacy MPG TeX files for generic-converter safety."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path

try:
    from .convert import audit
except ImportError:
    from convert import audit


def audit_tree(root: Path) -> dict:
    files = sorted((root / "docs/src/chapters").rglob("*.tex.in"))
    files += [root / "docs/src/template/MPG.tex.in.in"]
    files += sorted((root / "docs/src/static").glob("*.tex"))
    results = []
    for path in files:
        issues = audit(path.read_text(encoding="utf-8"), path.relative_to(root).as_posix())
        results.extend(asdict(x) for x in issues)
    constructs: dict[str, int] = {}
    for issue in results:
        constructs[issue["construct"]] = constructs.get(issue["construct"], 0) + 1
    return {
        "schema": "mpg-generic-conversion-audit-v1",
        "safe": not results,
        "files": len(files),
        "issues": results,
        "unsupported_constructs": dict(sorted(constructs.items())),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    report = audit_tree(args.root.resolve())
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if report["safe"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
