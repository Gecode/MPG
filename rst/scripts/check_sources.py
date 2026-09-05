#!/usr/bin/env python3
"""Validate maintained MPG code projections and figure companions."""
from pathlib import Path
import subprocess
import sys

RST = Path(__file__).resolve().parents[1]


def main() -> int:
    for command in (
        [sys.executable, str(RST / "scripts/author_code.py"), "check"],
        [sys.executable, str(RST / "figures/scripts/verify.py")],
    ):
        subprocess.run(command, check=True)
    print("maintained MPG source checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
