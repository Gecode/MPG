#!/usr/bin/env python3
"""One-command strict verification of the Sphinx publication platform."""

from __future__ import annotations

from pathlib import Path
import re
import subprocess
import sys
import tempfile

RST_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = RST_ROOT / "platform-tests" / "fixture"


def run(command: list[str]) -> str:
    print("+", " ".join(command), flush=True)
    result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if result.returncode:
        print(result.stdout)
        raise RuntimeError(f"command failed with exit {result.returncode}")
    return result.stdout


def main() -> int:
    run([sys.executable, str(RST_ROOT / "platform-tests" / "test_reference_inventory.py")])
    run([sys.executable, str(RST_ROOT / "platform-tests" / "test_package_release.py")])
    run([sys.executable, str(RST_ROOT / "platform-tests" / "test_platform.py")])
    run([
        sys.executable,
        "-m",
        "unittest",
        "discover",
        "-s",
        str(RST_ROOT / "platform-tests"),
        "-p",
        "test_*.py",
    ])
    with tempfile.TemporaryDirectory(prefix="mpg-release-platform-") as temporary:
        build = Path(temporary)
        run([
            sys.executable,
            str(RST_ROOT / "scripts" / "build.py"),
            "pdf",
            "--source",
            str(FIXTURE),
            "--build",
            str(build),
            "--root-doc",
            "index",
        ])
        pdf = build / "latex" / "MPG.pdf"
        if not pdf.exists():
            raise RuntimeError("PDF target did not produce MPG.pdf")
        log = (build / "latex" / "MPG.log").read_text(encoding="utf-8", errors="replace")
        forbidden = re.compile(
            r"Overfull \\[hv]box|Undefined control sequence|There were undefined references|Missing character"
        )
        match = forbidden.search(log)
        if match:
            raise RuntimeError(f"PDF log contains {match.group(0)}")
        fonts = run(["pdffonts", str(pdf)])
        for family in ("Charter", "BeraSansMono"):
            if family not in fonts:
                raise RuntimeError(f"PDF does not embed {family}")
        info = run(["pdfinfo", str(pdf)])
        if "Page size:       595.28 x 841.89 pts (A4)" not in info:
            raise RuntimeError("PDF is not A4")
    print("strict HTML, search, deep-link, redirect, and classical PDF checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
