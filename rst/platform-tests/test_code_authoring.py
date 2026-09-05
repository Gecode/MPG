"""Exercise code authoring against real temporary Git baselines."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("mpg_code_authoring", Path(__file__).resolve().parents[1] / "scripts/author_code.py")
code = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(code)


class StandardLibraryImportTests(unittest.TestCase):
    def test_sphinx_script_path_preserves_debugger_imports(self):
        scripts = Path(__file__).resolve().parents[1] / "scripts"
        subprocess.run(
            [sys.executable, "-c",
             "import sys; sys.path.insert(0, sys.argv[1]); "
             "import code, doctest, pdb; assert hasattr(code, 'InteractiveConsole')",
             str(scripts)],
            check=True,
        )


class CodeAuthoringTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="mpg-code-authoring-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.relative = "rst/examples/src/sample.cpp"
        self.source = self.root / self.relative
        self.source.parent.mkdir(parents=True)
        self.original = "// header\nint a = 1;\nint b = 2;\n// footer\n"
        self.source.write_text(self.original)
        self.data = {"schema": "mpg-code-v1", "artifacts": [], "projections": {}}
        code.add(self.data, self.root, "chunk", self.relative, "2:3", "cpp", "display-only", "Example")
        code.add(self.data, self.root, "whole", self.relative, None, "cpp", "display-only", None)
        manifest = self.root / code.MANIFEST
        manifest.parent.mkdir(parents=True)
        manifest.write_text(json.dumps(self.data))
        for arguments in (["init", "-q"], ["add", "."], ["-c", "user.name=MPG test", "-c", "user.email=mpg@example.invalid", "commit", "-qm", "baseline"]):
            subprocess.run(["git", *arguments], cwd=self.root, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def test_refresh_relocates_from_baseline_even_after_repeated_edits(self):
        self.source.write_text("// added\n" + self.original.replace("int b = 2;", "int b = 3;"))
        code.refresh(self.data, self.root)
        self.assertEqual((self.data["projections"]["chunk"]["start_line"], self.data["projections"]["chunk"]["end_line"]), (3, 4))
        once = copy.deepcopy(self.data)
        code.refresh(self.data, self.root)
        self.assertEqual(self.data, once)
        self.source.write_text("// added\n// another\n" + self.original)
        code.refresh(self.data, self.root)
        self.assertEqual((self.data["projections"]["chunk"]["start_line"], self.data["projections"]["chunk"]["end_line"]), (4, 5))
        self.assertEqual(self.data["projections"]["whole"]["end_line"], 6)
        code.validate(self.data, self.root)

    def test_deleted_excerpt_and_crossed_boundaries_require_review(self):
        for changed in ("// header\n// footer\n", "// replacement\nint b = 2;\n// footer\n"):
            with self.subTest(changed=changed):
                self.source.write_text(changed)
                with self.assertRaisesRegex(ValueError, "review ranges"):
                    code.refresh(copy.deepcopy(self.data), self.root)
        self.data["projections"]["chunk"].update(start_line=2, end_line=2)
        self.data["projections"]["whole"].update(start_line=1, end_line=3)
        code.refresh(self.data, self.root, no_relocate=True)
        code.validate(self.data, self.root)

    def test_check_rejects_stale_code_unknown_rst_keys_and_unsafe_paths(self):
        self.source.write_text(self.original.replace("int a = 1", "int a = 3"))
        with self.assertRaisesRegex(ValueError, "stale artifact"):
            code.validate(self.data, self.root)
        code.refresh(self.data, self.root)
        content = self.root / "rst/content"
        content.mkdir()
        (content / "chapter.rst").write_text(".. mpg-code:: unknown\n")
        with self.assertRaisesRegex(ValueError, "chapter.rst:1: unknown code projection"):
            code.validate(self.data, self.root)
        with self.assertRaisesRegex(ValueError, "under rst/examples"):
            code.add(self.data, self.root, "escape", "rst/examples/../../../outside.cpp", None, "cpp", "display-only", None)


if __name__ == "__main__":
    unittest.main()
