"""Release reference links are checked before external URLs are skipped."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "verify_html.py"
PAGE = '<header></header><nav></nav><main>{}</main><footer></footer>'


class HtmlReleaseTests(unittest.TestCase):
    def test_references_match_the_requested_release(self):
        with tempfile.TemporaryDirectory(prefix="mpg-html-release-") as temporary:
            root = Path(temporary)
            (root / "search").mkdir()
            (root / "search/index.html").write_text(PAGE.format("Search"))
            (root / "searchindex.js").write_text("")
            (root / "redirects.json").write_text('{"schema":1,"redirects":{}}')
            for uri, succeeds in (
                ("https://www.gecode.dev/doc/6.5.0/reference/space.html", True),
                ("/doc/6.5.0/reference/space.html", True),
                ("https://example.org/doc/6.4.0/reference/space.html", True),
                ("https://www.gecode.dev/doc/6.4.0/reference/space.html", False),
                ("/doc/6.4.0/reference/space.html", False),
                ("//www.gecode.dev/doc/latest/reference/space.html", False),
            ):
                with self.subTest(uri=uri):
                    (root / "index.html").write_text(PAGE.format(f'<a href="{uri}">Space</a>'))
                    result = subprocess.run(
                        [sys.executable, str(SCRIPT), str(root), "--release", "6.5.0",
                         "--site-prefix", "/doc/6.5.0/reference/"],
                        capture_output=True, text=True,
                    )
                    if succeeds:
                        self.assertEqual(result.returncode, 0, result.stderr)
                    else:
                        self.assertNotEqual(result.returncode, 0)
                        self.assertIn("reference link targets release", result.stderr)
