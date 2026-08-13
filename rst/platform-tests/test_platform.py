#!/usr/bin/env python3
"""Integration checks for strict publication mechanics."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
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
        run([
            sys.executable,
            str(RST_ROOT / "scripts" / "verify_html.py"),
            str(output),
            "--site-prefix", "/doc/development/reference/",
            "--site-prefix", "/doc/development/MPG.pdf",
        ])

        chapter = (output / "chapter" / "index.html").read_text(encoding="utf-8")
        for expected in (
            'href="#getting-started"',
            'id="fixture-first-model"',
            'id="fixture-tip"',
            'class="mpg-tip',
            'alt="Gecode"',
            'gecode-logo.svg',
            'class="mpg-page-logo"',
            '>Modeling &amp; Programming with Gecode</a>',
            'class="mpg-current-title"',
            'class="mpg-navigation-scroll"',
            'data-mpg-dialog-open="mpg-mobile-navigation"',
            'aria-controls="mpg-mobile-navigation"',
            '<dialog class="mpg-mobile-navigation"',
            'method="dialog"',
            'Tip 1.1',
            '>Name constraints after their intent</span></a>',
            'class="mpg-part-opening',
            'class="literal-block-wrapper',
            'id="fig-m-fixture"',
            '<figure class="mpg-content-figure',
            '<figcaption>',
            '<span class="caption-text">Available values</span>',
            '<strong class="mpg-paragraph-heading">Classical heading.</strong> This paragraph',
            'Figure 1.1',
        ):
            if expected not in chapter:
                raise RuntimeError(f"HTML omitted {expected}")
        for unexpected in ('>Manual contents</a>', '>Current chapter<'):
            if unexpected in chapter:
                raise RuntimeError(f"HTML retained obsolete sidebar text {unexpected}")
        if chapter.count('id="mpg-search-field-desktop"') != 1 or chapter.count('id="mpg-search-field-mobile"') != 1:
            raise RuntimeError("desktop and mobile navigation need unique search labels")

        index = (output / "index.html").read_text(encoding="utf-8")
        for expected in ('href="chapter/#fixture-tip"',
                         'href="chapter/#fig-m-fixture"',
                         '>Name constraints after their intent</span></a>'):
            if expected not in index:
                raise RuntimeError(f"cross-page tip reference omitted {expected}")
        html = "\n".join(path.read_text(encoding="utf-8") for path in output.rglob("*.html"))
        if (re.search(r'id="[^"]*:[^"]*"', html)
                or re.search(r'href="[^"]*#[^"]*:[^"]*"', html)):
            raise RuntimeError("HTML exposed LaTeX-oriented authoring labels")

        part = (output / "part" / "index.html").read_text(encoding="utf-8")
        if part.count("<h1") != 1:
            raise RuntimeError("HTML part page must have exactly one h1")
        for expected in ('class="mpg-part-opening', '<h1>Modeling</h1>',
                         '<strong class="mpg-paragraph-heading">Start here.</strong>'):
            if expected not in part:
                raise RuntimeError(f"HTML part page omitted {expected}")

        css = (output / "_static" / "mpg.css").read_text(encoding="utf-8")
        for expected in ('.mpg-body :is(ul, ol) > li + li',
                         '.mpg-body dt {', '.mpg-body dd {'):
            if expected not in css:
                raise RuntimeError(f"web reading rhythm omitted {expected}")

        latex_output = root / "latex"
        sphinx_latex(FIXTURE, latex_output)
        latex = (latex_output / "MPG.tex").read_text(encoding="utf-8")
        for expected in (r"\begin{figure}[tbp]", r"\caption[Values]{Available values}",
                         r"\paragraph{Classical heading.}",
                         r"chapter:fig-m-fixture"):
            if expected not in latex:
                raise RuntimeError(f"LaTeX omitted {expected}")
        adapter = (latex_output / "mpg-sphinx.sty").read_text(encoding="utf-8")
        for expected in (r"pdflang={en-GB}", r"pdfdisplaydoctitle=true",
                         r"https://www.gecode.dev/doc/\MPGGecodeVersion/MPG.pdf",
                         r"HeaderFamily={\rmfamily\bfseries}",
                         r"\titleformat{\paragraph}[runin]",
                         r"\renewenvironment{description}",
                         r"\topsep 10\p@ \@plus4\p@ \@minus6\p@",
                         r"\def\MPGClassicalListI",
                         r"\let\@listi\MPGClassicalListI",
                         r"\itemsep5\p@  \@plus2.5\p@ \@minus\p@",
                         r"includegraphics[width=.18\textwidth]{cc-by-nc-nd.pdf}"):
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
