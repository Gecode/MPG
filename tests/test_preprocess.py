from pathlib import Path

from tools.mpg.preprocess import shorten_labels


def test_shorten_labels() -> None:
    inp = Path("tests/golden/preprocess/shorten-input.tex").read_text(encoding="utf-8")
    out = shorten_labels(inp)
    exp = Path("tests/golden/preprocess/shorten-expected.tex").read_text(encoding="utf-8")
    assert out == exp
