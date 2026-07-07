import json
import tempfile
import unittest
from pathlib import Path

import tools.mpg.examples as examples
from tools.mpg.gecode import GecodeConfig


class ExampleManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self._root = examples.ROOT
        self._manifests = examples.MANIFESTS
        self._results = examples.RESULTS
        self._bin = examples.BIN

    def tearDown(self) -> None:
        examples.ROOT = self._root
        examples.MANIFESTS = self._manifests
        examples.RESULTS = self._results
        examples.BIN = self._bin

    def test_run_prefers_kind_manifest_over_legacy_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            examples.ROOT = root
            examples.MANIFESTS = root / ".mpg" / "manifests"
            examples.RESULTS = root / ".mpg" / "results"
            examples.BIN = root / ".mpg" / "bin"

            legacy = {
                "kind": "all",
                "version": "6.4.0",
                "year": "2026",
                "examples": [
                    {
                        "id": "send-more-money-with-gist",
                        "kind": "model",
                        "source": "ignored.cpp",
                        "wrapper": None,
                        "requires_gist": False,
                        "run_args": [],
                        "timeout_sec": 20,
                        "enabled": True,
                    }
                ],
            }
            current = json.loads(json.dumps(legacy))
            current["examples"][0]["requires_gist"] = True

            (root / ".mpg").mkdir(parents=True)
            examples.MANIFESTS.mkdir(parents=True)
            (root / ".mpg" / "manifest.json").write_text(json.dumps(legacy), encoding="utf-8")
            examples.manifest_path("all").write_text(json.dumps(current), encoding="utf-8")

            gc = GecodeConfig("test", None, None, [], [], {})
            summary = examples.run_examples("all", gc)

            self.assertEqual(summary["total"], 1)
            self.assertEqual(summary["skipped"], 1)
            self.assertEqual(summary["failed"], 0)

    def test_needs_gist_detects_gist_header(self) -> None:
        self.assertTrue(examples._needs_gist("#include <gecode/gist.hh>\n"))


if __name__ == "__main__":
    unittest.main()
