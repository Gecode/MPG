import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "rst" / "scripts"))

from build_contract import source_date_epoch, validate_release
from build import clean_outputs


class BuildContractTests(unittest.TestCase):
    def test_release_identifiers_are_safe_for_paths_and_urls(self) -> None:
        self.assertEqual(validate_release("6.4.0"), "6.4.0")
        self.assertEqual(validate_release("6.4.0-rc.1"), "6.4.0-rc.1")
        self.assertEqual(validate_release("development"), "development")
        for invalid in ("../outside", ".", "..", "latest", "6.4", "6.4.0+build.1"):
            with self.subTest(version=invalid), self.assertRaises(ValueError):
                validate_release(invalid)
        with self.assertRaises(ValueError):
            validate_release("development", allow_development=False)

    def test_source_date_epoch_is_stable_for_the_checkout(self) -> None:
        first = source_date_epoch(ROOT)
        second = source_date_epoch(ROOT)
        self.assertTrue(first.isdigit())
        self.assertEqual(first, second)

    def test_clean_outputs_removes_only_owned_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            build = Path(temporary)
            (build / "html" / "stale").mkdir(parents=True)
            (build / "latex").mkdir()
            (build / "reports").mkdir()
            unrelated = build / "keep-me.txt"
            unrelated.write_text("keep", encoding="utf-8")

            clean_outputs(build)

            self.assertFalse((build / "html").exists())
            self.assertFalse((build / "latex").exists())
            self.assertFalse((build / "reports").exists())
            self.assertEqual(unrelated.read_text(encoding="utf-8"), "keep")


if __name__ == "__main__":
    unittest.main()
