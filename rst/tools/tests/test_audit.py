from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from audit import audit_tree


class AuditTests(unittest.TestCase):
    def test_full_tree_report_is_fail_closed_and_located(self):
        root = Path(__file__).resolve().parents[3]
        report = audit_tree(root)
        self.assertFalse(report["safe"])
        self.assertGreater(len(report["issues"]), 0)
        self.assertTrue(all(x["source"].startswith("docs/src/") and x["line"] > 0 for x in report["issues"]))
        self.assertIn("begin{figure}", report["unsupported_constructs"])


if __name__ == "__main__":
    unittest.main()
