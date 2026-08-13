#!/usr/bin/env python3
"""Regression tests for the release-frozen Gecode link inventory."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "generate_reference_inventory.py"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="mpg-reference-inventory-") as temporary:
        root = Path(temporary)
        source = root / "content"
        html = root / "html"
        source.mkdir()
        html.mkdir()
        (source / "index.rst").write_text(
            "See :api:`Space` and :api:`crossword`.\n", encoding="utf-8"
        )
        (root / "gecode.tag").write_text(
            """<?xml version="1.0"?>
<tagfile>
  <compound kind="class"><name>Gecode::Space</name><filename>space.html</filename></compound>
  <compound kind="class"><name>Crossword</name><filename>crossword.html</filename></compound>
</tagfile>
""",
            encoding="utf-8",
        )
        (html / "space.html").write_text("", encoding="utf-8")
        (html / "crossword.html").write_text("", encoding="utf-8")
        output = root / "inventory.json"
        command = [
            sys.executable,
            str(SCRIPT),
            "--source", str(source),
            "--tag", str(root / "gecode.tag"),
            "--html-root", str(html),
            "--version", "9.9.9",
            "--output", str(output),
        ]
        subprocess.run(command, check=True, stdout=subprocess.PIPE, text=True)
        data = json.loads(output.read_text(encoding="utf-8"))
        assert data["base_url"] == "/doc/9.9.9/reference/"
        assert data["objects"] == {
            "Space": {"title": "Gecode::Space", "url": "space.html"},
            "crossword": {"title": "Crossword", "url": "crossword.html"},
        }

        (source / "index.rst").write_text("See :api:`Missing`.\n", encoding="utf-8")
        failed = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        assert failed.returncode != 0 and "absent from the release Doxygen tag" in failed.stdout
    print("release reference inventory generation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
