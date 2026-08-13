import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from coverage import build_contract, verify_contract


class CoverageTests(unittest.TestCase):
    def test_contract_is_per_source_and_per_construct(self):
        legacy = {
            "sources": [{"path": "docs/src/chapters/modeling/m-a.tex.in"}],
            "labels": [{"id": "chap:m:a", "source": "docs/src/chapters/modeling/m-a.tex.in", "line": 2}],
            "citations": [{"id": "Paper", "source": "docs/src/chapters/modeling/m-a.tex.in", "line": 3}],
            "tips": [], "figures": [], "tables": [], "tabulars": [],
            "literate": {"insertions": []},
        }
        contract = build_contract(legacy)
        mapping = next(x for x in contract["source_mappings"] if x["source"].endswith("m-a.tex.in"))
        self.assertEqual(mapping["destination"], "rst/content/modeling/a.rst")
        self.assertEqual({x["kind"] for x in contract["items"]}, {"label", "citation"})

    def test_verifier_fails_on_silent_drop(self):
        contract = {
            "source_mappings": [{"source": "docs/src/chapters/modeling/m-a.tex.in", "destination": "rst/content/modeling/a.rst", "disposition": "convert"}],
            "items": [{"key": "label:k", "kind": "label", "id": "chap:m:a", "source": "docs/src/chapters/modeling/m-a.tex.in", "line": 1, "destination": "rst/content/modeling/a.rst", "disposition": "required", "verification": "exact-rst-anchor"}],
        }
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "docs/src/chapters/modeling").mkdir(parents=True)
            (root / "docs/src/chapters/modeling/m-a.tex.in").write_text("legacy", encoding="utf-8")
            (root / "rst/content/modeling").mkdir(parents=True)
            (root / "rst/content/modeling/a.rst").write_text("A\n=\n", encoding="utf-8")
            report = verify_contract(contract, root)
        self.assertFalse(report["complete"])
        self.assertEqual(report["totals"]["missing_items"], 1)

    def test_named_enumerable_is_an_exact_anchor(self):
        contract = {
            "source_mappings": [{"source": "docs/src/chapters/search/s-a.tex.in", "destination": "rst/content/search-engines/a.rst", "disposition": "convert"}],
            "items": [{"key": "figure:k", "kind": "figure", "id": "fig:s:a:program", "source": "docs/src/chapters/search/s-a.tex.in", "line": 1, "destination": "rst/content/search-engines/a.rst", "disposition": "required", "verification": "exact-rst-anchor"}],
        }
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "docs/src/chapters/search").mkdir(parents=True)
            (root / "docs/src/chapters/search/s-a.tex.in").write_text("legacy", encoding="utf-8")
            (root / "rst/content/search-engines").mkdir(parents=True)
            (root / "rst/content/search-engines/a.rst").write_text(
                ".. mpg-code:: example\n   :name: fig:s:a:program\n",
                encoding="utf-8",
            )
            report = verify_contract(contract, root)
        self.assertTrue(report["complete"])


if __name__ == "__main__":
    unittest.main()
