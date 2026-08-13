from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tex import commands, strip_comments


class TexScannerTests(unittest.TestCase):
    def test_balanced_arguments_and_locations(self):
        calls = commands("before\n\\tip{A {nested} title}{body \\label{tip:x}}\n")
        tip = next(x for x in calls if x.name == "tip")
        self.assertEqual(tip.line, 2)
        self.assertEqual(tip.required, ("A {nested} title", "body \\label{tip:x}"))
        self.assertIn("tip:x", next(x for x in calls if x.name == "label").required)

    def test_comments_are_masked_but_newlines_preserved(self):
        text = "x % \\label{ignored}\n\\label{kept} % tail\n"
        self.assertEqual([x.required[0] for x in commands(text) if x.name == "label"], ["kept"])
        self.assertEqual(strip_comments(text).count("\n"), 2)


if __name__ == "__main__":
    unittest.main()
