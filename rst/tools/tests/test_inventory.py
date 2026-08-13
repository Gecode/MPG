import json
from pathlib import Path
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[1]
ROOT = TOOLS.parents[1]
sys.path.insert(0, str(TOOLS))
from inventory import build_inventory


class InventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory = build_inventory(ROOT)

    def test_all_chapter_sources_are_in_book_graph(self):
        book = self.inventory["book"]
        graph = book["front_matter"] + book["back_matter"]
        graph += [chapter for part in book["parts"] for chapter in part["chapters"]]
        chapter_sources = [x["path"] for x in self.inventory["sources"] if "/chapters/" in x["path"]]
        self.assertEqual(sorted(graph), sorted(chapter_sources))

    def test_integrity_issues_are_explicit_lists(self):
        self.assertEqual(set(self.inventory["integrity"]), {"duplicate_labels", "unresolved_explicit_references", "template_reference_placeholders", "missing_citation_keys", "missing_graphics", "unresolved_literate_insertions"})
        self.assertEqual(self.inventory["integrity"]["duplicate_labels"], [])
        self.assertEqual(self.inventory["integrity"]["unresolved_explicit_references"], [])
        self.assertEqual(self.inventory["integrity"]["unresolved_literate_insertions"], [])

    def test_literate_blocks_are_qualified_and_nested(self):
        blocks = self.inventory["literate"]["blocks"]
        self.assertTrue(all(":" in x["id"] for x in blocks if x["file"]))
        self.assertTrue(any(x["depth"] > 0 for x in blocks))

    def test_generated_title_references_are_resolved_to_stable_ids(self):
        generated = [x for x in self.inventory["references"] if x["kind"] == "generated-title-macro"]
        self.assertGreater(len(generated), 0)
        self.assertTrue(all(x["id"].startswith(("chap:", "sec:")) for x in generated))

    def test_all_raw_tabular_constructs_are_inventory_items(self):
        self.assertEqual(self.inventory["totals"]["tabulars"], self.inventory["construct_counts"]["environments"]["tabular"])

    def test_checked_in_manifest_is_current(self):
        expected = json.loads((ROOT / "rst/manifests/legacy-parity.json").read_text(encoding="utf-8"))
        self.assertEqual(self.inventory, expected)


if __name__ == "__main__":
    unittest.main()
