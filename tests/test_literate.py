from pathlib import Path

from tools.mpg.literate import process_literate_file


def test_literate_basic(tmp_path: Path) -> None:
    src = Path("tests/golden/literate/sample.tex.in")
    out = tmp_path / "out.tex"
    process_literate_file(src, out, year="2020", emit_cpp=False)
    text = out.read_text(encoding="utf-8")
    assert "\\CppInline" in text
    assert "\\litcodeblock" in text
    assert "..." in text
