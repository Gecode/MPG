import pickle
import sys
from pathlib import Path

environment = Path(sys.argv[1]) / ".doctrees" / "environment.pickle"
with environment.open("rb") as stream:
    env = pickle.load(stream)
expected = {
    "first-page": "../examples/send-more-money.cpp",
    "crossword": "../../shared/hard-pages/examples/crossword-grid.cpp",
    "nonogram": "../../shared/hard-pages/examples/nonogram-heart.cpp",
}
for document, source in expected.items():
    dependencies = {str(path) for path in env.dependencies[document]}
    assert source in dependencies, (document, dependencies)
print("PASS literalinclude registered all canonical C++ dependencies")
