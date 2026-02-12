import tempfile
import unittest
from pathlib import Path

from tools.mpg.literate import process_literate_file


class LiterateTests(unittest.TestCase):
    def test_literate_matches_golden(self) -> None:
        src = Path("tests/golden/literate/sample.tex.in")
        expected = Path("tests/golden/literate/expected.tex").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out.tex"
            process_literate_file(src, out, year="2020", emit_cpp=False)
            text = out.read_text(encoding="utf-8")
        self.assertEqual(text, expected)


if __name__ == "__main__":
    unittest.main()
