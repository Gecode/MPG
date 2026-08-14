#!/usr/bin/env python3
"""Keep literate titles and code inside one classical PDF panel."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def require(path: Path, fragment: str) -> None:
    if fragment not in path.read_text(encoding="utf-8"):
        raise RuntimeError(f"{path} omitted {fragment!r}")


def main() -> int:
    adapter = ROOT / "_static" / "latex" / "mpg-sphinx.sty"
    classic = ROOT / "_static" / "latex" / "mpg-classic.sty"
    extension = ROOT / "extensions" / "mpg_code.py"
    require(adapter, r"\newcommand{\MPGLiterateBorderWidth}{.4pt}")
    require(adapter, r"\MPGCodeTitleText{\MPGCurrentCodeTitle}")
    require(adapter, "pre_border-radius=0pt")
    require(extension, r"\\gdef\\MPGCurrentCodeTitle")
    require(extension, r"\\gdef\\sphinxVerbatimTitle{\\relax}")
    require(classic, r"\enspace$\equiv$")
    print("literate title and code share the classical PDF panel")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
