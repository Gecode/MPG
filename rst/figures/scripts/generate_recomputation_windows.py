#!/usr/bin/env python3
"""Generate the two unnumbered recomputation window diagrams.

The node-state tables below are the maintainable authoring source.  They are a
direct transcription of the two legacy PSTricks trees in s-recomputation:
ordinary choice nodes, stored clones, clones made obsolete by LAO, and the
last-alternative path along which clones move.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import html
import os
import subprocess


ROOT = Path(__file__).resolve().parents[3]
FIGURES = ROOT / "rst/figures"
PDF = FIGURES / "pdf"

BLUE = "#005ca1"
ORANGE = "#eb891b"
GREY = "#d7d7d7"
INK = "#1f2529"
PAPER = "#ffffff"


@dataclass(frozen=True)
class Diagram:
    stem: str
    title: str
    description: str
    states: tuple[str, ...]
    highlighted_edges: frozenset[tuple[int, int]] = frozenset()


DIAGRAMS = (
    Diagram(
        "fig-s-re-hybrid-tree",
        "Hybrid recomputation with commit distance two",
        "A complete binary search tree of depth three. The root and every "
        "node two commits below it store orange clones; intermediate choice "
        "nodes are blue.",
        ("clone", "choice", "choice", "clone", "clone", "clone", "clone",
         "choice", "choice", "choice", "choice", "choice", "choice", "choice", "choice"),
    ),
    Diagram(
        "fig-s-re-hybrid-lao-tree",
        "Last alternative optimization with hybrid recomputation",
        "A complete binary search tree of depth three after last alternative "
        "optimization. Grey nodes mark obsolete stored clones, orange nodes "
        "mark their new locations, and orange edges mark the last-alternative path.",
        ("obsolete", "choice", "obsolete", "obsolete", "obsolete", "choice", "obsolete",
         "clone", "choice", "clone", "choice", "clone", "clone", "clone", "choice"),
        frozenset({(0, 2), (2, 6), (6, 14), (4, 10), (3, 8)}),
    ),
)


def position(index: int) -> tuple[float, float]:
    depth = (index + 1).bit_length() - 1
    first = (1 << depth) - 1
    offset = index - first
    slots = 1 << depth
    return (28 + (offset + 0.5) * 384 / slots, 25 + depth * 52)


def circle(x: float, y: float, state: str) -> str:
    fill = {"choice": BLUE, "clone": ORANGE, "obsolete": GREY}[state]
    classes = f"node {state}"
    return (
        f'<circle class="{classes}" cx="{x:.1f}" cy="{y:.1f}" r="9" '
        f'fill="{fill}" stroke="{INK}" stroke-width="1.2"/>'
    )


def render(diagram: Diagram) -> str:
    title_id = diagram.stem + "-title"
    desc_id = diagram.stem + "-desc"
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<svg xmlns="http://www.w3.org/2000/svg" role="img" '
        f'aria-labelledby="{title_id} {desc_id}" viewBox="0 0 520 230">',
        f'  <title id="{title_id}">{html.escape(diagram.title)}</title>',
        f'  <desc id="{desc_id}">{html.escape(diagram.description)}</desc>',
        '  <g fill="none" stroke-linecap="round">',
    ]
    for child in range(1, len(diagram.states)):
        parent = (child - 1) // 2
        x1, y1 = position(parent)
        x2, y2 = position(child)
        highlighted = (parent, child) in diagram.highlighted_edges
        color = ORANGE if highlighted else INK
        width = 3 if highlighted else 1.4
        lines.append(
            f'    <path d="M{x1:.1f},{y1 + 9:.1f} L{x2:.1f},{y2 - 9:.1f}" '
            f'stroke="{color}" stroke-width="{width}"/>'
        )
    lines.append("  </g>")
    lines.append('  <g aria-label="search tree nodes">')
    for index, state in enumerate(diagram.states):
        lines.append("    " + circle(*position(index), state))
    lines.extend((
        "  </g>",
        f'  <rect x="434" y="38" width="12" height="12" rx="6" fill="{BLUE}" stroke="{INK}"/>',
        f'  <text x="454" y="48" font-family="Arial, sans-serif" font-size="12" fill="{INK}">choice</text>',
        f'  <rect x="434" y="66" width="12" height="12" rx="6" fill="{ORANGE}" stroke="{INK}"/>',
        f'  <text x="454" y="76" font-family="Arial, sans-serif" font-size="12" fill="{INK}">stored clone</text>',
    ))
    if "obsolete" in diagram.states:
        lines.extend((
            f'  <rect x="434" y="94" width="12" height="12" rx="6" fill="{GREY}" stroke="{INK}"/>',
            f'  <text x="454" y="104" font-family="Arial, sans-serif" font-size="12" fill="{INK}">old clone</text>',
        ))
    if diagram.highlighted_edges:
        lines.extend((
            f'  <line x1="434" y1="132" x2="448" y2="132" stroke="{ORANGE}" stroke-width="3"/>',
            f'  <text x="454" y="136" font-family="Arial, sans-serif" font-size="12" fill="{INK}">LAO path</text>',
        ))
    lines.extend(("</svg>", ""))
    return "\n".join(line for line in lines if line)


def main() -> None:
    PDF.mkdir(parents=True, exist_ok=True)
    for diagram in DIAGRAMS:
        svg = FIGURES / f"{diagram.stem}.svg"
        pdf = PDF / f"{diagram.stem}.pdf"
        svg.write_text(render(diagram), encoding="utf-8")
        subprocess.run(
            ["rsvg-convert", "--format=pdf", "--output", str(pdf), str(svg)],
            env={**os.environ, "SOURCE_DATE_EPOCH": "946684800"},
            check=True,
        )


if __name__ == "__main__":
    main()
