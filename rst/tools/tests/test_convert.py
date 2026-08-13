from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from convert import UnsafeConversion, convert_fragment


class ConverterTests(unittest.TestCase):
    def test_safe_fragment_preserves_anchor_and_reference(self):
        source = r"""\section{A model}
\label{sec:model}
See \autoref{sec:model} and \?Space? with $x=1$.
"""
        result = convert_fragment(source)
        self.assertIn(".. _sec:model:", result)
        self.assertIn(":ref:`sec:model`", result)
        self.assertIn("``Space``", result)
        self.assertIn(":math:`x=1`", result)

    def test_unknown_macro_fails_closed(self):
        with self.assertRaises(UnsafeConversion) as caught:
            convert_fragment(r"Keep \mystery{this}")
        self.assertEqual(caught.exception.issues[0].construct, r"\mystery")

    def test_complex_environment_fails_closed(self):
        with self.assertRaises(UnsafeConversion):
            convert_fragment(r"\begin{tabular}{cc}a&b\end{tabular}")


if __name__ == "__main__":
    unittest.main()
