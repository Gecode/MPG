from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


class FailedPreviewTests(unittest.TestCase):
    def test_invalid_authoring_keeps_previous_page_and_search(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source = base / "source"
            source.mkdir()
            (source / "index.rst").write_text(".. _test-page:\n\nTest page\n=========\n\n.. unknown-mpg-directive::\n")
            html = base / "build/html"
            (html / "pagefind").mkdir(parents=True)
            (html / "index.html").write_text("previous successful page")
            (html / "pagefind/pagefind.js").write_text("previous search")
            result = subprocess.run(
                [sys.executable, str(ROOT / "rst/scripts/build.py"), "html",
                 "--source", str(source), "--root-doc", "index", "--build", str(base / "build")],
                text=True, capture_output=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unknown-mpg-directive", result.stdout + result.stderr)
            self.assertEqual((html / "index.html").read_text(), "previous successful page")
            self.assertEqual((html / "pagefind/pagefind.js").read_text(), "previous search")


if __name__ == "__main__":
    unittest.main()
