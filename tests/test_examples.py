import json
import shutil
import subprocess
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

    def test_missing_canonical_source_does_not_use_legacy_copy(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            examples.ROOT = root
            (root / "demo.cpp").write_text("int main() {}\n", encoding="utf-8")
            config = {"models": ["demo"], "examples": {}, "run_timeout_sec": 20}
            selected = examples._build_examples("models", config)
            with self.assertRaisesRegex(RuntimeError, "Missing canonical example source"):
                examples._prepare_sources(selected, root / "build")

    @unittest.skipUnless(shutil.which("cmake"), "requires CMake")
    def test_reconfigure_selects_libraries_from_current_gecode(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            examples.BIN = root / "bin"
            for name in ("first", "second"):
                libraries = root / name
                libraries.mkdir()
                for library in examples.MODEL_LIBS:
                    (libraries / f"lib{library}.a").touch()
                gc = GecodeConfig("test", None, None, [], [libraries], {})
                cmake = examples._emit_cmake(root / "build", [], gc, {"compile_flags": []}, "models")
                subprocess.run(
                    ["cmake", "-S", str(cmake), "-B", str(root / "out")],
                    check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                )
                cache = (root / "out/CMakeCache.txt").read_text(encoding="utf-8")
                self.assertIn(f"MPG_LIB_GECODEINT:FILEPATH={libraries}/libgecodeint.a", cache)


if __name__ == "__main__":
    unittest.main()
