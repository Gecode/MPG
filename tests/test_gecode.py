import tempfile
import unittest
from pathlib import Path

from tools.mpg.gecode import has_test_framework, resolve_gecode


class GecodeResolutionTests(unittest.TestCase):
    def _write_core_libs(self, path: Path, *, gist: bool = False) -> None:
        path.mkdir(parents=True, exist_ok=True)
        names = [
            "gecodedriver",
            "gecodesearch",
            "gecodefloat",
            "gecodeminimodel",
            "gecodeset",
            "gecodeint",
            "gecodekernel",
            "gecodesupport",
        ]
        if gist:
            names.append("gecodegist")
        for name in names:
            (path / f"lib{name}.dylib").write_text("", encoding="utf-8")

    def test_source_tree_build_layout_is_discovered(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = (Path(tmp) / "gecode").resolve()
            (root / "gecode").mkdir(parents=True)
            (root / "build").mkdir()
            cfg = resolve_gecode(str(root), None)

            self.assertEqual(cfg.mode, "root")
            self.assertEqual(root / "build", cfg.include_dirs[0])
            self.assertIn(root, cfg.include_dirs)
            self.assertIn(root / "gecode", cfg.include_dirs)
            self.assertEqual(root / "build", cfg.lib_dirs[0])

    def test_matching_cmake_build_is_preferred_over_top_level_libs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = (Path(tmp) / "gecode").resolve()
            support = root / "gecode" / "support"
            support.mkdir(parents=True)
            (support / "config.hpp").write_text('#define GECODE_VERSION "6.4.0"\n', encoding="utf-8")
            self._write_core_libs(root)
            build = root / "build" / "mpg-validation"
            self._write_core_libs(build)
            (build / "GecodeConfig.cmake").write_text('set(Gecode_VERSION "6.4.0")\n', encoding="utf-8")

            cfg = resolve_gecode(str(root), None)

            self.assertEqual(cfg.mode, "root-build")
            self.assertEqual(build, cfg.lib_dirs[0])
            self.assertEqual(build, cfg.include_dirs[0])
            self.assertIn(root / "gecode", cfg.include_dirs)

    def test_gist_validation_build_is_preferred_when_available(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = (Path(tmp) / "gecode").resolve()
            support = root / "gecode" / "support"
            support.mkdir(parents=True)
            (support / "config.hpp").write_text('#define GECODE_VERSION "6.4.0"\n', encoding="utf-8")
            plain = root / "build" / "mpg-validation"
            gist = root / "build" / "mpg-gist-validation"
            self._write_core_libs(plain)
            self._write_core_libs(gist, gist=True)
            (plain / "GecodeConfig.cmake").write_text('set(Gecode_VERSION "6.4.0")\n', encoding="utf-8")
            (gist / "GecodeConfig.cmake").write_text('set(Gecode_VERSION "6.4.0")\n', encoding="utf-8")

            cfg = resolve_gecode(str(root), None)

            self.assertEqual(cfg.mode, "root-build")
            self.assertEqual(gist, cfg.lib_dirs[0])

    def test_test_framework_requires_all_source_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "gecode"
            test_dir = root / "test"
            test_dir.mkdir(parents=True)
            for name in ("test.cpp", "int.cpp", "float.cpp", "set.cpp"):
                (test_dir / name).write_text("", encoding="utf-8")
            cfg = resolve_gecode(str(root), None)

            self.assertTrue(has_test_framework(cfg))


if __name__ == "__main__":
    unittest.main()
