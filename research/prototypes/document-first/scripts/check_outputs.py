#!/usr/bin/env python3
"""Check semantic evidence in the rendered artifacts."""

from __future__ import annotations

import hashlib
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "_build" / "site"


class LocalLinks(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.targets: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attribute = "href" if tag in {"a", "link"} else "src" if tag in {"img", "script"} else None
        if attribute is None:
            return
        for name, value in attrs:
            if name == attribute and value:
                self.targets.append(value)


def require(text: str, fragment: str, description: str) -> None:
    if fragment not in text:
        raise SystemExit(f"rendered HTML lacks {description}: {fragment!r}")


def main() -> None:
    model = (SITE / "modeling.html").read_text(encoding="utf-8")
    require(model, 'id="eq-total-count"', "numbered equation target")
    require(model, 'href="#eq-total-count"', "equation cross-reference")
    require(model, 'id="fig-propagation"', "figure target")
    require(model, 'href="#lst-magic-sequence"', "listing cross-reference")
    require(model, "Schulte and Stuckey", "processed citation")
    require(model, 'data-source-file="examples/magic-sequence.cpp"', "code provenance")
    require(model, "MagicSequence", "included canonical C++")
    require(model, "figures/propagation.svg", "web SVG figure")

    canonical = ROOT / "examples" / "magic-sequence.cpp"
    extracted = ROOT / "_build" / "extracted" / "magic-sequence.cpp"
    if hashlib.sha256(canonical.read_bytes()).digest() != hashlib.sha256(
        extracted.read_bytes()
    ).digest():
        raise SystemExit("extracted C++ differs from canonical source")

    pdf = SITE / "Modeling-and-Programming-with-Gecode.pdf"
    if not pdf.is_file() or pdf.stat().st_size < 20_000:
        raise SystemExit(f"missing or implausibly small PDF: {pdf}")

    checked_links = 0
    for page in sorted(SITE.glob("*.html")):
        links = LocalLinks()
        links.feed(page.read_text(encoding="utf-8"))
        for raw_target in links.targets:
            parsed = urlsplit(raw_target)
            if parsed.scheme or parsed.netloc or not parsed.path or parsed.path.startswith("/"):
                continue
            target = (page.parent / unquote(parsed.path)).resolve()
            if not target.exists():
                raise SystemExit(f"broken local target in {page.name}: {raw_target}")
            checked_links += 1

    print(
        f"checked HTML semantics, {checked_links} local assets/links, "
        f"and {pdf.stat().st_size}-byte PDF"
    )


if __name__ == "__main__":
    main()
