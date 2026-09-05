#!/usr/bin/env python3
"""Check the current figure sources, media companions, and authored references."""
from __future__ import annotations

import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

FIGURES = Path(__file__).resolve().parents[1]
RST = FIGURES.parent


def main() -> int:
    figures = sorted(FIGURES.glob("*.svg"))
    if not figures:
        raise SystemExit("no maintained SVG figures")
    for source in figures:
        root = ET.parse(source).getroot()
        for name in ("title", "desc"):
            element = root.find("{http://www.w3.org/2000/svg}" + name)
            if element is None or not "".join(element.itertext()).strip():
                raise SystemExit(f"{source}: missing useful SVG {name}")
        for node in root.iter():
            href = node.get("href", node.get("{http://www.w3.org/1999/xlink}href", ""))
            if href and not href.startswith(("#", "data:")):
                if "://" in href or not (source.parent / href).is_file():
                    raise SystemExit(f"{source}: unavailable external image {href}")
        pdf = FIGURES / "pdf" / source.with_suffix(".pdf").name
        info = subprocess.run(["pdfinfo", str(pdf)], check=True, text=True, capture_output=True).stdout
        if not re.search(r"^Pages:\s+1$", info, re.MULTILINE):
            raise SystemExit(f"{pdf}: figure must have one page")
        size = re.search(r"^Page size:\s+([\d.]+) x ([\d.]+)", info, re.MULTILINE)
        if size is None or min(map(float, size.groups())) <= 0:
            raise SystemExit(f"{pdf}: invalid page dimensions")
    references = 0
    for source in (RST / "content").rglob("*.rst"):
        for value in re.findall(r"(?:figure|image)::\s+/figures/([^\s]+)", source.read_text()):
            if not (FIGURES / value).is_file():
                raise SystemExit(f"{source}: missing figure {value}")
            references += 1
    print(f"verified {len(figures)} accessible SVG/PDF pairs and {references} authored image references")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
