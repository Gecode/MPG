#!/usr/bin/env python3
"""Check release HTML invariants without network access or extra packages."""

from __future__ import annotations

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


FIGURE_SIZE_CLASSES = frozenset({
    "mpg-figure-narrow",
    "mpg-figure-compact",
    "mpg-figure-medium",
    "mpg-figure-wide",
    "mpg-figure-full",
})


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.links: list[str] = []
        self.permalinks: list[tuple[str, str]] = []
        self.landmarks: set[str] = set()
        self.figure_stack: list[tuple[str, set[str]]] = []
        self.unsized_figures: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        attributes = dict(attrs)
        if "id" in attributes:
            if attributes["id"] in self.ids:
                raise ValueError(f"duplicate id {attributes['id']!r}")
            self.ids.add(attributes["id"])
        if tag == "a" and "href" in attributes:
            self.links.append(attributes["href"])
            if "headerlink" in attributes.get("class", "").split():
                self.permalinks.append(
                    (attributes.get("title", ""), attributes["href"])
                )
        if tag in {"main", "nav", "header", "footer"}:
            self.landmarks.add(tag)
        if tag == "figure":
            self.figure_stack.append(
                (attributes.get("id", "<unnamed>"), set(attributes.get("class", "").split()))
            )
        elif tag == "img" and self.figure_stack:
            figure_id, classes = self.figure_stack[-1]
            if classes.isdisjoint(FIGURE_SIZE_CLASSES):
                self.unsized_figures.append(figure_id)

    def handle_endtag(self, tag: str) -> None:
        if tag == "figure" and self.figure_stack:
            self.figure_stack.pop()


def target_file(root: Path, page: Path, uri: str) -> tuple[Path, str]:
    split = urlsplit(uri)
    path = unquote(split.path)
    if path.startswith("/"):
        destination = root / path.lstrip("/")
    else:
        destination = page.parent / path
    if not path or path.endswith("/"):
        destination = destination / "index.html"
    elif destination.suffix == "":
        destination = destination / "index.html"
    return destination.resolve(), unquote(split.fragment)


def main() -> int:
    argument_parser = argparse.ArgumentParser(description=__doc__)
    argument_parser.add_argument("root", type=Path)
    argument_parser.add_argument("--site-prefix", action="append", default=[])
    argument_parser.add_argument("--release", help="required Gecode version for reference links")
    argument_parser.add_argument("--require-pagefind", action="store_true")
    arguments = argument_parser.parse_args()
    root = arguments.root.resolve()
    pages = sorted(root.rglob("*.html"))
    if not pages:
        raise SystemExit("no HTML pages found")
    parsed: dict[Path, PageParser] = {}
    for page in pages:
        parser = PageParser()
        parser.feed(page.read_text(encoding="utf-8"))
        parsed[page.resolve()] = parser
        if page.name != "genindex.html" and not {"main", "nav", "header", "footer"} <= parser.landmarks:
            raise SystemExit(f"missing document landmarks: {page}")
        if parser.unsized_figures:
            figures = ", ".join(parser.unsized_figures)
            raise SystemExit(f"figures lack an intentional width in {page}: {figures}")

    for page, parser in parsed.items():
        for title, uri in parser.permalinks:
            if title == "Link to this table" and re.fullmatch(r"#id[0-9]+", uri):
                raise SystemExit(
                    f"numbered table uses an unstable generated fragment in {page}: {uri}"
                )
        for uri in parser.links:
            split = urlsplit(uri)
            if arguments.release and (
                not split.scheme and not split.netloc
                or split.hostname in {"www.gecode.dev", "gecode.dev"}
            ):
                reference = re.match(r"/doc/([^/]+)/reference(?:/|$)", unquote(split.path))
                if reference and reference[1] != arguments.release:
                    raise SystemExit(
                        f"reference link targets release {reference[1]} instead of "
                        f"{arguments.release} in {page}: {uri}"
                    )
            if split.scheme or split.netloc or uri.startswith(("mailto:", "javascript:")):
                continue
            if split.path.startswith(tuple(arguments.site_prefix)):
                continue
            destination, fragment = target_file(root, page, uri)
            if destination.suffix != ".html":
                if not destination.exists():
                    raise SystemExit(f"broken local asset from {page}: {uri}")
                continue
            target = parsed.get(destination)
            if target is None:
                raise SystemExit(f"broken local page from {page}: {uri} -> {destination}")
            if fragment and fragment not in target.ids:
                raise SystemExit(f"broken fragment from {page}: {uri}")

    required = [root / "search" / "index.html", root / "searchindex.js", root / "redirects.json"]
    if arguments.require_pagefind:
        required.extend([
            root / "pagefind" / "pagefind-entry.json",
            root / "pagefind" / "pagefind-component-ui.css",
            root / "pagefind" / "pagefind-component-ui.js",
        ])
        css = (root / "_static" / "mpg.css").read_text(encoding="utf-8")
        if '@import "tailwindcss"' in css:
            raise SystemExit("release CSS was not compiled by Tailwind")
        for utility in (
            ".fixed{position:fixed!important}",
            ".flex{display:flex!important}",
            ".text-pretty{text-wrap:pretty!important}",
            r".focus-within\:\[\&_\.headerlink\]\:opacity-100",
        ):
            if utility not in css:
                raise SystemExit(f"release CSS omitted Tailwind utility {utility}")
    for path in required:
        if not path.exists():
            raise SystemExit(f"missing search/link artifact: {path}")
    redirects = json.loads((root / "redirects.json").read_text(encoding="utf-8"))
    if redirects.get("schema") != 1 or not isinstance(redirects.get("redirects"), dict):
        raise SystemExit("invalid redirect artifact")
    print(f"verified {len(pages)} HTML pages, local links, search, and redirects")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
