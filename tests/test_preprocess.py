import unittest
from pathlib import Path

from tools.mpg.preprocess import shorten_labels


class PreprocessTests(unittest.TestCase):
    def test_shorten_labels(self) -> None:
        inp = Path("tests/golden/preprocess/shorten-input.tex").read_text(encoding="utf-8")
        out = shorten_labels(inp)
        exp = Path("tests/golden/preprocess/shorten-expected.tex").read_text(encoding="utf-8")
        self.assertEqual(out, exp)


if __name__ == "__main__":
    unittest.main()
