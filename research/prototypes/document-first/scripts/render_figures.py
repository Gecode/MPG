#!/usr/bin/env python3
"""Render every Graphviz source to web and print vector formats."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
FIGURES = ROOT / "figures"


def main() -> None:
    dot = shutil.which("dot")
    if dot is None:
        raise SystemExit("Graphviz 'dot' is required to render figures")

    for source in sorted(FIGURES.glob("*.dot")):
        for format_name in ("svg", "pdf"):
            target = source.with_suffix(f".{format_name}")
            subprocess.run(
                [dot, f"-T{format_name}", str(source), "-o", str(target)],
                check=True,
            )
            print(f"rendered {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
