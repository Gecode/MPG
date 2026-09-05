"""Published examples must run with the selected Gecode library environment."""

import os
from pathlib import Path
import sys
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from verify_examples import run


class ExampleEnvironmentTests(unittest.TestCase):
    def test_child_receives_the_selected_library_environment(self):
        environment = dict(os.environ, MPG_TEST_LIBRARY_PATH="selected-gecode")
        result, _ = run(
            Path(sys.executable),
            ["-c", "import os; print(os.environ['MPG_TEST_LIBRARY_PATH'])"],
            5,
            environment,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "selected-gecode")
