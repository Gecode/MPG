#!/usr/bin/env -S uv run -- python
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.mpg.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
