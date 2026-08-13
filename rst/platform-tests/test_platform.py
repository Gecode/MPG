#!/usr/bin/env python3
"""Integration checks for strict publication mechanics."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from docutils import nodes

RST_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = Path(__file__).resolve().parent / "fixture"
sys.path.insert(0, str(RST_ROOT / "extensions"))
from mpg_semantics import _use_pdf_figure_derivatives


def run(command: list[str], expect_success: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if (result.returncode == 0) != expect_success:
        print(result.stdout)
        raise RuntimeError(f"unexpected exit {result.returncode}: {' '.join(command)}")
    return result


def sphinx(source: Path, output: Path, *, success: bool = True) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["MPG_ROOT_DOC"] = "index"
    result = subprocess.run([
        sys.executable, "-m", "sphinx", "-W", "-n", "-T", "-j", "auto",
        "-c", str(RST_ROOT), "-b", "dirhtml", str(source), str(output),
    ], env=environment, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if (result.returncode == 0) != success:
        print(result.stdout)
        raise RuntimeError(f"unexpected Sphinx exit {result.returncode}")
    return result


def sphinx_latex(source: Path, output: Path) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["MPG_ROOT_DOC"] = "index"
    result = subprocess.run([
        sys.executable, "-m", "sphinx", "-W", "-n", "-T", "-j", "auto",
        "-c", str(RST_ROOT), "-b", "latex", str(source), str(output),
    ], env=environment, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if result.returncode != 0:
        print(result.stdout)
        raise RuntimeError("unexpected LaTeX Sphinx exit")
    return result


def main() -> int:
    class Builder:
        format = "latex"

    class App:
        builder = Builder()
        confdir = str(RST_ROOT)

    document = nodes.container()
    image = nodes.image(uri="/figures/fig-intro-gecode_architecture.svg")
    document += image
    _use_pdf_figure_derivatives(App(), document)
    if image["uri"] != "/figures/pdf/fig-intro-gecode_architecture.pdf":
        raise RuntimeError("LaTeX did not select the canonical PDF figure derivative")

    with tempfile.TemporaryDirectory(prefix="mpg-platform-") as temporary:
        root = Path(temporary)
        output = root / "html"
        sphinx(FIXTURE, output)
        run([sys.executable, str(RST_ROOT / "scripts" / "verify_html.py"), str(output)])

        chapter = (output / "chapter" / "index.html").read_text(encoding="utf-8")
        for expected in (
            'id="chap:m:fixture"',
            'href="#chap:m:fixture"',
            'id="fig:m:fixture"',
            'id="fixture-first-model"',
            'id="fixture-tip"',
            'class="mpg-tip',
            'Tip 1.1',
            '>Name constraints after their intent</span></a>',
            'class="mpg-part-opening',
            'class="literal-block-wrapper',
            'id="fig-m-fixture"',
            '<figure class="mpg-content-figure',
            '<figcaption>',
            '<span class="caption-text">Available values</span>',
            'Figure 1.1',
        ):
            if expected not in chapter:
                raise RuntimeError(f"HTML omitted {expected}")

        index = (output / "index.html").read_text(encoding="utf-8")
        for expected in ('href="chapter/#fixture-tip"',
                         'href="chapter/#fig:m:fixture"',
                         '>Name constraints after their intent</span></a>'):
            if expected not in index:
                raise RuntimeError(f"cross-page tip reference omitted {expected}")

        latex_output = root / "latex"
        sphinx_latex(FIXTURE, latex_output)
        latex = (latex_output / "MPG.tex").read_text(encoding="utf-8")
        for expected in (r"\begin{figure}[htbp]", r"\caption{Available values}",
                         r"chapter:fig-m-fixture"):
            if expected not in latex:
                raise RuntimeError(f"LaTeX omitted {expected}")
        adapter = (latex_output / "mpg-sphinx.sty").read_text(encoding="utf-8")
        for expected in (r"pdflang={en-GB}", r"pdfdisplaydoctitle=true",
                         r"https://www.gecode.dev/doc/\MPGGecodeVersion/MPG.pdf"):
            if expected not in adapter:
                raise RuntimeError(f"PDF adapter omitted {expected}")

        manifest = json.loads((output / "redirects.json").read_text(encoding="utf-8"))
        assert manifest == {"redirects": {}, "release": "development", "schema": 1}

        broken = root / "broken"
        broken.mkdir()
        (broken / "references.bib").write_text("", encoding="utf-8")
        (broken / "index.rst").write_text("Unlabelled\n==========\n", encoding="utf-8")
        failure = sphinx(broken, root / "broken-html", success=False)
        if "needs an explicit stable label" not in failure.stdout:
            print(failure.stdout)
            raise RuntimeError("unlabelled section did not fail for the intended reason")

    print("platform fixture and fail-closed label policy passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
