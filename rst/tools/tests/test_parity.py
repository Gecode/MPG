from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from parity import compare, scan_rst


class ParityTests(unittest.TestCase):
    def test_reports_missing_public_ids_and_citations(self):
        legacy = {"labels": [{"id": "chap:a"}, {"id": "sec:b"}], "citations": [{"id": "Paper"}], "totals": {}}
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "index.rst").write_text(".. _chap:a:\n\nSee :cite:p:`Other`.\n", encoding="utf-8")
            report = compare(legacy, scan_rst(root))
        self.assertFalse(report["complete"])
        self.assertEqual(report["missing_labels"], ["sec:b"])
        self.assertEqual(report["missing_citation_keys"], ["Paper"])


if __name__ == "__main__":
    unittest.main()
