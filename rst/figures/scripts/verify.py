#!/usr/bin/env python3
"""Verify figure inventory, derivatives, accessibility, and RST references."""

from __future__ import annotations

import json
import os
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RST = ROOT / "rst"
FIGURES = RST / "figures"
records = json.loads((RST / "manifests" / "figures.json").read_text())

assert len(records) == 213, f"expected 213 legacy figure environments, found {len(records)}"
labels = [label for record in records for label in record["labels"]]
assert len(labels) == 217 and len(set(labels)) == 217, "legacy label inventory is incomplete or duplicated"

graphical = [record for record in records if record["kind"] in {"legacy-vector-conversion", "semantic-redraw", "data-diagram", "screenshot"}]
assert len(graphical) == 38

for record in graphical:
    svg = RST / record["html_asset"]
    pdf = RST / record["pdf_asset"]
    assert svg.is_file() and svg.stat().st_size > 300, f"missing/empty SVG: {svg}"
    assert pdf.is_file() and pdf.stat().st_size > 1000, f"missing/empty PDF: {pdf}"
    tree = ET.parse(svg)
    root = tree.getroot()
    names = {child.tag.rsplit("}", 1)[-1] for child in root}
    assert "title" in names and "desc" in names, f"missing SVG accessibility text: {svg}"
    info = subprocess.run(["pdfinfo", str(pdf)], check=True, text=True, capture_output=True).stdout
    assert re.search(r"^Pages:\s+1$", info, re.MULTILINE), f"PDF is not one page: {pdf}"
    assert "CreationDate:    Sat Jan  1" in info, f"PDF lacks reproducible creation date: {pdf}"

raster_assets = json.loads((RST / "manifests" / "raster-assets.json").read_text())
assert len(raster_assets) == 18
for record in raster_assets:
    assert (RST / record["asset"]).is_file(), f"missing screenshot source: {record['asset']}"
    assert (ROOT / record["legacy_eps"]).is_file(), f"missing legacy EPS pair: {record['legacy_eps']}"

for name in ("gecode-logo.svg",):
    assert (FIGURES / name).is_file()
    assert (FIGURES / "pdf" / Path(name).with_suffix(".pdf")).is_file()

# The architecture overview is relational, not a row of independent boxes.
# Preserve the original PSTricks topology: core modules and the two extension
# areas bridge the kernel and Modeling layers, while propagators/branchers
# overlap the modules from the left.
architecture = ET.parse(FIGURES / "fig-intro-gecode_architecture.svg").getroot()
by_id = {node.get("id"): node for node in architecture.iter() if node.get("id")}


def box(name: str) -> tuple[float, float, float, float]:
    node = by_id[name]
    if node.tag.rsplit("}", 1)[-1] == "g":
        node = next(child for child in node if child.tag.rsplit("}", 1)[-1] == "rect")
    x, y = float(node.get("x", "0")), float(node.get("y", "0"))
    return x, y, x + float(node.get("width", "0")), y + float(node.get("height", "0"))


modeling = box("modeling-layer")
kernel = box("gecode-kernel")
bridges = [
    *(box(f"module-{name}") for name in ("int", "set", "float", "search")),
    box("programming-variables"),
    box("programming-search-engines"),
]
for name, (_, top, _, bottom) in zip(
    ("Int", "Set", "Float", "Search", "variables", "search engines"), bridges
):
    assert top < modeling[3] and bottom > kernel[1], f"{name} no longer bridges Modeling and the kernel"
programming = box("programming-propagators-branchers")
assert programming[2] > bridges[2][0], "propagators/branchers no longer overlap the core modules"
assert programming[2] < bridges[3][0], "propagators/branchers incorrectly subsume the Search module"

supplemental = json.loads((RST / "manifests" / "supplemental-figures.json").read_text())
assert supplemental["schema"] == "mpg-supplemental-figures-v1"
assert len(supplemental["figures"]) == 2
for record in supplemental["figures"]:
    svg = ROOT / record["html_asset"]
    pdf = ROOT / record["pdf_asset"]
    assert svg.is_file() and pdf.is_file(), f"missing supplemental figure: {record}"
    tree = ET.parse(svg)
    names = {child.tag.rsplit("}", 1)[-1] for child in tree.getroot()}
    assert "title" in names and "desc" in names, f"missing SVG accessibility text: {svg}"
    info = subprocess.run(["pdfinfo", str(pdf)], check=True, text=True, capture_output=True).stdout
    assert re.search(r"^Pages:\s+1$", info, re.MULTILINE), f"PDF is not one page: {pdf}"
    assert "CreationDate:    Sat Jan  1" in info, f"PDF lacks reproducible creation date: {pdf}"

references = []
for source in (RST / "content").rglob("*.rst"):
    text = source.read_text()
    references.extend((source, value) for value in re.findall(r"(?:figure|image)::\s+/figures/([^\s]+)", text))
for source, value in references:
    assert (FIGURES / value).is_file(), f"broken figure reference in {source}: /figures/{value}"

# Regenerate one mixed text/vector page and require byte-for-byte identity.
probe_svg = FIGURES / "fig-intro-gecode_architecture.svg"
probe_pdf = FIGURES / ".build" / "determinism-probe.pdf"
environment = dict(os.environ, SOURCE_DATE_EPOCH="946684800")
subprocess.run(["rsvg-convert", "-f", "pdf", "-o", str(probe_pdf), str(probe_svg)], check=True, env=environment)
assert probe_pdf.read_bytes() == (FIGURES / "pdf" / "fig-intro-gecode_architecture.pdf").read_bytes(), "PDF conversion is not deterministic"

print(
    f"verified {len(records)} legacy figure environments, {len(labels)} stable labels, "
    f"{len(graphical)} inventoried and {len(supplemental['figures'])} supplemental "
    f"SVG/PDF pairs, and {len(references)} RST image references"
)
