from pathlib import Path
import sys
from docutils import nodes

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "extensions"))
from mpg_semantic import SemanticBuilder

builder = object.__new__(SemanticBuilder)
try:
    builder._serialize(nodes.raw("", "<unsafe>"), "fixture")
except RuntimeError as error:
    assert "unsupported resolved doctree node" in str(error)
    print("PASS semantic builder rejects unknown doctree nodes")
else:
    raise AssertionError("semantic builder accepted an unknown doctree node")
