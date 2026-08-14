from __future__ import annotations

from pathlib import Path
import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]


@unittest.skipUnless(importlib.util.find_spec("sphinx"), "Sphinx is not installed")
class MpgCodeDirectiveTests(unittest.TestCase):
    def _build(self, builder: str, body: str) -> Path:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        base = Path(temp.name)
        (base / "conf.py").write_text(
            "import sys\n"
            f"sys.path.insert(0, {str(ROOT / 'rst' / 'extensions')!r})\n"
            "extensions=['mpg_code']\n"
            "master_doc='index'\n"
            f"mpg_code_manifest={str(ROOT / 'rst' / 'manifests' / 'code-projections.json')!r}\n"
            f"mpg_code_root={str(ROOT)!r}\n",
            encoding="utf-8",
        )
        (base / "index.rst").write_text("Code\n====\n\n" + body, encoding="utf-8")
        (base / "examples").symlink_to(ROOT / "rst" / "examples", target_is_directory=True)
        out = base / "out"
        subprocess.run(
            [sys.executable, "-m", "sphinx", "-W", "--keep-going", "-b", builder, str(base), str(out)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        return out

    def test_spaced_key_and_blank_download_copy_canonical_bytes(self) -> None:
        out = self._build("dirhtml", ".. mpg-code:: assign min\n   :download:\n")
        downloads = list((out / "_downloads").rglob("assign-min.cpp"))
        self.assertEqual(len(downloads), 1)
        self.assertEqual(downloads[0].read_bytes(), (ROOT / "rst/examples/src/assign-min.cpp").read_bytes())

    def test_custom_download_label(self) -> None:
        out = self._build("html", ".. mpg-code:: assign min\n   :download: complete example\n")
        html = (out / "index.html").read_text(encoding="utf-8")
        self.assertIn("complete example", html)

    def test_literate_insertion_keeps_its_unnumbered_block_title(self) -> None:
        body = ".. mpg-code:: send more money:no leading zeros\n"
        html = (self._build("html", body) / "index.html").read_text(encoding="utf-8")
        fragment_id = "fragment-send-more-money-no-leading-zeros"
        self.assertIn(f'class="mpg-code-title" id="{fragment_id}"', html)
        self.assertIn(
            f'<a class="mpg-code-fragment-link" href="#{fragment_id}">'
            'no leading zeros <span class="mpg-code-equivalence" '
            'aria-hidden="true">&equiv;</span></a>',
            html,
        )
        self.assertNotIn("Program ", html)

        latex = (self._build("latex", body) / "projectnamenotset.tex").read_text(
            encoding="utf-8"
        )
        self.assertIn(r"\gdef\MPGCurrentCodeTitle{no leading zeros}", latex)
        self.assertIn(r"\gdef\sphinxVerbatimTitle{\relax}", latex)
        self.assertIn(r"\global\MPGUnnumberedVerbatimTitletrue", latex)
        self.assertNotIn(r"\caption", latex)


if __name__ == "__main__":
    unittest.main()
