#!/usr/bin/env python3
"""Package a tested MPG build for release-time import by the Gecode site."""

from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import shutil


class TitleParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_title = False
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag == "title":
            self.in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.parts.append(data)


def page_title(path: Path) -> str:
    parser = TitleParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return " ".join("".join(parser.parts).split())


def page_route(path: Path, root: Path) -> str:
    relative = path.relative_to(root).as_posix()
    if relative == "index.html":
        return ""
    if relative.endswith("/index.html"):
        return relative.removesuffix("index.html")
    return relative


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", type=Path, default=Path("rst/_build"))
    parser.add_argument("--output", type=Path, default=Path("output"))
    parser.add_argument("--version", required=True)
    arguments = parser.parse_args()

    html = arguments.build / "html"
    pdf = arguments.build / "latex" / "MPG.pdf"
    required = [
        html / "index.html",
        html / "search" / "index.html",
        html / "searchindex.js",
        html / "redirects.json",
        pdf,
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise SystemExit("release build is incomplete: " + ", ".join(missing))

    release = arguments.output / "releases" / arguments.version / "modeling"
    public_pdf = arguments.output / "pdf" / f"MPG-{arguments.version}.pdf"
    if release.exists() or public_pdf.exists():
        raise SystemExit(
            "release output already exists; remove the exact versioned output before repackaging"
        )
    release.parent.mkdir(parents=True, exist_ok=True)
    public_pdf.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        html,
        release,
        ignore=shutil.ignore_patterns(".doctrees", ".buildinfo.bak"),
    )
    shutil.copy2(pdf, release / "MPG.pdf")
    shutil.copy2(pdf, public_pdf)

    files = []
    for path in sorted(item for item in release.rglob("*") if item.is_file()):
        files.append({
            "path": path.relative_to(release).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": digest(path),
        })
    pages = [
        {"route": page_route(path, release), "title": page_title(path)}
        for path in sorted(release.rglob("*.html"))
        if path.relative_to(release).as_posix() not in {"genindex.html", "search/index.html"}
    ]
    manifest = {
        "schema": "gecode-mpg-release-v1",
        "version": arguments.version,
        "mount": f"/doc/{arguments.version}/modeling/",
        "entrypoint": "index.html",
        "pdf": "MPG.pdf",
        "search": "searchindex.js",
        "redirects": "redirects.json",
        "pages": pages,
        "files": files,
    }
    (release / "release-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"packaged {len(files)} files for {manifest['mount']}")
    print(f"PDF: {public_pdf}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
