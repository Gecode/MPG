from __future__ import annotations

from pathlib import Path
import sys
import unittest

from docutils import nodes


RST_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RST_ROOT / "extensions"))

from mpg_semantics import MpgTip, visit_mpg_tip_latex


class _Translator:
    def __init__(self) -> None:
        self.body: list[str] = []

    def encode(self, value: str) -> str:
        return value

    def hypertarget(self, target: str) -> str:
        return f"target:{target}"


class PdfRhythmTests(unittest.TestCase):
    def test_tip_heading_runs_into_first_body_paragraph(self) -> None:
        translator = _Translator()
        node = MpgTip()
        node["number"] = "2.1"
        node["title"] = "Space& versus Home"
        visit_mpg_tip_latex(translator, node)
        self.assertEqual(
            translator.body[-1], r"\begin{MPGTip}{2.1}{Space& versus Home}"
        )

    def test_classical_code_blocks_keep_display_rhythm(self) -> None:
        adapter = (RST_ROOT / "_static/latex/mpg-sphinx.sty").read_text(
            encoding="utf-8"
        )
        classical = (RST_ROOT / "_static/latex/mpg-classic.sty").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            r"\renewcommand{\sphinxverbatimsmallskipamount}{\medskipamount}",
            adapter,
        )
        self.assertIn(r"\needspace{5\baselineskip}", classical)


if __name__ == "__main__":
    unittest.main()
