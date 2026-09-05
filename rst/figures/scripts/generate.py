#!/usr/bin/env python3
"""Render deterministic PDF companions from the maintained SVG figures."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import tempfile

FIGURES = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sources", nargs="*", type=Path, help="SVG paths; defaults to every maintained figure")
    parser.add_argument("--check", action="store_true", help="report stale PDF companions without modifying them")
    arguments = parser.parse_args()
    sources = arguments.sources or sorted(FIGURES.glob("*.svg"))
    failures = []
    with tempfile.TemporaryDirectory(prefix="mpg-figures-") as temporary:
        for source in sources:
            source = source.resolve()
            if source.parent != FIGURES or source.suffix != ".svg":
                parser.error(f"expected an SVG directly inside {FIGURES}: {source}")
            target = FIGURES / "pdf" / source.with_suffix(".pdf").name
            rendered = Path(temporary) / target.name
            subprocess.run(
                ["rsvg-convert", "-f", "pdf", "-o", str(rendered), str(source)],
                check=True, env=dict(os.environ, SOURCE_DATE_EPOCH="946684800"),
            )
            if target.is_file() and target.read_bytes() == rendered.read_bytes():
                continue
            if arguments.check:
                failures.append(str(target))
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(rendered.read_bytes())
                print(f"updated {target}")
    if failures:
        raise SystemExit("stale figure PDFs; run rst/figures/scripts/generate.py:\n" + "\n".join(failures))
    print(f"{'checked' if arguments.check else 'rendered'} {len(sources)} SVG/PDF pairs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
