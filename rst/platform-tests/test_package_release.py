#!/usr/bin/env python3
"""Check the versioned release-bundle contract in isolation."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "package_release.py"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="mpg-package-") as temporary:
        root = Path(temporary)
        build = root / "build"
        html = build / "html"
        (html / "search").mkdir(parents=True)
        (html / ".doctrees").mkdir()
        (build / "latex").mkdir()
        for path, text in (
            (html / "index.html", "<title>MPG manual</title><main>MPG</main>"),
            (html / "search" / "index.html", "<title>Search</title><main>Search</main>"),
            (html / "searchindex.js", "Search.setIndex({});"),
            (html / "redirects.json", '{"schema":1,"redirects":{}}'),
            (html / ".buildinfo.bak", "stale build metadata"),
            (html / ".doctrees" / "environment.pickle", "private Sphinx cache"),
            (build / "latex" / "MPG.pdf", "%PDF-fixture"),
        ):
            path.write_text(text, encoding="utf-8")
        output = root / "output"
        command = [
            sys.executable, str(SCRIPT), "--build", str(build),
            "--output", str(output), "--version", "9.9.9",
        ]
        subprocess.run(command, check=True, stdout=subprocess.PIPE, text=True)
        release = output / "releases" / "9.9.9" / "modeling"
        manifest = json.loads((release / "release-manifest.json").read_text())
        assert manifest["mount"] == "/doc/9.9.9/modeling/"
        assert manifest["entrypoint"] == "index.html"
        assert manifest["pages"] == [{"route": "", "title": "MPG manual"}]
        assert {item["path"] for item in manifest["files"]} == {
            "MPG.pdf", "index.html", "redirects.json", "search/index.html", "searchindex.js"
        }
        assert not (release / ".buildinfo.bak").exists()
        assert not (release / ".doctrees").exists()
        assert (output / "pdf" / "MPG-9.9.9.pdf").read_bytes() == b"%PDF-fixture"
        duplicate = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        assert duplicate.returncode != 0 and "already exists" in duplicate.stdout
    print("release bundle packaging passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
