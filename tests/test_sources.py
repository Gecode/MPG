import tempfile
import unittest
import warnings
from pathlib import Path

import tools.mpg.sources as sources


class SourcesTests(unittest.TestCase):
    def setUp(self) -> None:
        self._legacy_root = sources.LEGACY_ROOT
        self._docs_src_root = sources.DOCS_SRC_ROOT
        self._docs_chapters_root = sources.DOCS_CHAPTERS_ROOT
        self._docs_template_root = sources.DOCS_TEMPLATE_ROOT
        self._docs_static_root = sources.DOCS_STATIC_ROOT
        self._docs_bib_root = sources.DOCS_BIB_ROOT
        sources.reset_caches_for_tests()

    def tearDown(self) -> None:
        sources.LEGACY_ROOT = self._legacy_root
        sources.DOCS_SRC_ROOT = self._docs_src_root
        sources.DOCS_CHAPTERS_ROOT = self._docs_chapters_root
        sources.DOCS_TEMPLATE_ROOT = self._docs_template_root
        sources.DOCS_STATIC_ROOT = self._docs_static_root
        sources.DOCS_BIB_ROOT = self._docs_bib_root
        sources.reset_caches_for_tests()

    def _set_roots(self, root: Path) -> None:
        docs_src = root / "docs" / "src"
        sources.LEGACY_ROOT = root
        sources.DOCS_SRC_ROOT = docs_src
        sources.DOCS_CHAPTERS_ROOT = docs_src / "chapters"
        sources.DOCS_TEMPLATE_ROOT = docs_src / "template"
        sources.DOCS_STATIC_ROOT = docs_src / "static"
        sources.DOCS_BIB_ROOT = docs_src / "bib"
        sources.reset_caches_for_tests()

    def test_resolver_prefers_docs_src(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._set_roots(root)

            ch = sources.DOCS_CHAPTERS_ROOT / "modeling" / "m-started.tex.in"
            ch.parent.mkdir(parents=True, exist_ok=True)
            ch.write_text("chapter", encoding="utf-8")

            tpl = sources.DOCS_TEMPLATE_ROOT / "MPG.tex.in.in"
            tpl.parent.mkdir(parents=True, exist_ok=True)
            tpl.write_text("template", encoding="utf-8")

            bib = sources.DOCS_BIB_ROOT / "MPG.bib.in"
            bib.parent.mkdir(parents=True, exist_ok=True)
            bib.write_text("bib", encoding="utf-8")

            refs = sources.DOCS_BIB_ROOT / "references.bib"
            refs.write_text("refs", encoding="utf-8")

            macros = sources.DOCS_STATIC_ROOT / "macros.tex"
            macros.parent.mkdir(parents=True, exist_ok=True)
            macros.write_text("macros", encoding="utf-8")

            self.assertEqual(sources.chapter_source("m-started"), ch)
            self.assertEqual(sources.main_template(), tpl)
            self.assertEqual(sources.bib_template(), bib)
            self.assertEqual(sources.references_bib(), refs)
            self.assertEqual(sources.static_tex_files(), [macros])

    def test_resolver_falls_back_to_legacy(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._set_roots(root)

            ch = root / "m-started.tex.in"
            ch.write_text("chapter", encoding="utf-8")
            tpl = root / "MPG.tex.in.in"
            tpl.write_text("template", encoding="utf-8")
            bib = root / "MPG.bib.in"
            bib.write_text("bib", encoding="utf-8")
            refs = root / "references.bib"
            refs.write_text("refs", encoding="utf-8")
            macros = root / "macros.tex"
            macros.write_text("macros", encoding="utf-8")

            with warnings.catch_warnings(record=True) as seen:
                warnings.simplefilter("always")
                self.assertEqual(sources.chapter_source("m-started"), ch)
                self.assertEqual(sources.main_template(), tpl)
                self.assertEqual(sources.bib_template(), bib)
                self.assertEqual(sources.references_bib(), refs)
                self.assertEqual(sources.static_tex_files(), [macros])

            self.assertGreaterEqual(len(seen), 4)
            self.assertTrue(any("legacy source path" in str(w.message) for w in seen))

    def test_duplicate_chapter_basenames_raise(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._set_roots(root)

            a = sources.DOCS_CHAPTERS_ROOT / "modeling" / "m-started.tex.in"
            b = sources.DOCS_CHAPTERS_ROOT / "search" / "m-started.tex.in"
            a.parent.mkdir(parents=True, exist_ok=True)
            b.parent.mkdir(parents=True, exist_ok=True)
            a.write_text("a", encoding="utf-8")
            b.write_text("b", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "Duplicate chapter basenames"):
                sources.chapter_source("m-started")


if __name__ == "__main__":
    unittest.main()
