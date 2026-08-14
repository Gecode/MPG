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
        for expected in ("katex.min.js", "auto-render.min.js",
                         "katex_autorenderer.js"):
            if expected not in chapter:
                raise RuntimeError(f"HTML omitted the KaTeX asset {expected}")
        if "MathJax" in chapter:
            raise RuntimeError("HTML retained MathJax after the KaTeX switch")
        katex_config = (output / "_static" / "katex_autorenderer.js").read_text(
            encoding="utf-8"
        )
        for expected in (
            r'"\\Gecode": "\\mathsf{Gecode}"',
            r'"\\NN": "\\mathbb{N}"',
            r'"\\ZZ": "\\mathbb{Z}"',
            r'"\\RR": "\\mathbb{R}"',
            r'"\\arcsinh": "\\operatorname{arcsinh}"',
            r'"\\arccosh": "\\operatorname{arccosh}"',
            r'"\\arctanh": "\\operatorname{arctanh}"',
            r'"\\mbox": "\\text{#1}"',
            r'"\\reifyeqv": "#1=\\mathtt{1}\\Leftrightarrow #2"',
            r'"\\reifyimp": "#1=\\mathtt{1}\\Rightarrow #2"',
            r'"\\reifypmi": "#1=\\mathtt{1}\\Leftarrow #2"',
            "throwOnError: true",
            'strict: "error"',
        ):
            if expected not in katex_config:
                raise RuntimeError(f"HTML KaTeX configuration omitted {expected}")
        if r"\[0 &lt; 1\]" not in chapter:
            raise RuntimeError("display TeX was not safely HTML-escaped")
        for expected in (
            'href="#getting-started"',
            'id="fixture-first-model"',
            'id="fixture-tip"',
            'class="mpg-tip',
            'alt="Gecode"',
            'gecode-logo.svg',
            'class="mpg-page-logo ',
            '<main id="mpg-main" class="mpg-body min-w-0 max-w-[64rem]" role="main" tabindex="-1" data-pagefind-body>',
            '>Modeling &amp; Programming with Gecode</a>',
            'class="mpg-current-title ',
            'class="mpg-navigation-scroll ',
            '<pagefind-modal-trigger placeholder="Find a topic or API" shortcut="mod+k">',
            '<pagefind-modal>',
            '<pagefind-results max-sub-results="1">',
            'href="{{ sub.url | safeUrl }}"',
            'ranking: { termFrequency: 0 }',
            'new URL(document.documentElement.dataset.content_root, location.href).pathname',
            'data-mpg-dialog-open="mpg-mobile-navigation"',
            'aria-controls="mpg-mobile-navigation"',
            '<dialog class="mpg-mobile-navigation ',
            'method="dialog"',
            'Tip 1.1',
            'Program 1.1',
            'Program 1.2',
            'Program 1.3',
            '>Name constraints after their intent</span></a>',
            'class="mpg-part-opening',
            'class="literal-block-wrapper',
            'id="fixture-program"',
            '<a class="mpg-object-number" href="#fixture-program"><span class="caption-number">Program 1.1 </span></a>',
            'href="#fixture-program" title="Link to this code"',
            'id="fig-m-fixture-external-program"',
            'href="#fig-m-fixture-external-program" title="Link to this code"',
            'id="program-an-unnamed-program"',
            'href="#program-an-unnamed-program" title="Link to this code"',
            'hover:[&amp;_.headerlink]:opacity-100',
            'focus-within:[&amp;_.headerlink]:opacity-100',
            'id="fig-m-fixture"',
            '<figure class="mpg-content-figure mpg-figure-compact',
            '<figcaption>',
            '<a class="mpg-object-number" href="#fig-m-fixture"><span class="caption-number">Figure 1.1 </span></a>',
            '<span class="caption-text">Available values</span>',
            'href="#fig-m-fixture" title="Link to this image"',
            'id="fixture-tip"',
            '<a class="mpg-object-number" href="#fixture-tip"><span>Tip 1.1</span></a>',
            'href="#fixture-tip" title="Link to this tip"',
            'id="fixture-table"',
            '<a class="mpg-object-number" href="#fixture-table"><span class="caption-number">Table 1.1 </span></a>',
            'href="#fixture-table" title="Link to this table"',
            'id="equation-fixture-equation"',
            'href="#equation-fixture-equation" title="Permalink to this equation"',
            '<strong class="mpg-paragraph-heading">Classical heading.</strong> This paragraph',
            'Figure 1.1',
            'id="constraint-overview"',
            'font-mpg-sans',
            'max-compact:pe-20',
            'class="mb-4 ps-6 max-compact:ps-5',
            'mt-5 mb-6',
            'class="mt-3 first:mt-0 font-bold',
            'class="ms-5 mt-1 max-compact:ms-4',
            '<section class="mpg-search-definition" data-pagefind-weight="10">',
            '<h3 class="mpg-search-definition mt-8',
            'id="fixture-constraints" data-pagefind-weight="10"',
        ):
            if expected not in chapter:
                raise RuntimeError(f"HTML omitted {expected}")
        for unexpected in ('>Manual contents</a>', '>Current chapter<'):
            if unexpected in chapter:
                raise RuntimeError(f"HTML retained obsolete sidebar text {unexpected}")
        if chapter.count('<pagefind-modal-trigger placeholder="Find a topic or API" shortcut="mod+k">') != 2:
            raise RuntimeError("desktop and mobile navigation need Pagefind search triggers")
        if chapter.count('<pagefind-modal>') != 1:
            raise RuntimeError("each page needs exactly one shared Pagefind search modal")

        search_script = (output / "_static" / "mpg-search.js").read_text(
            encoding="utf-8"
        )
        for expected in ("sessionStorage", "dialog.close()", "input.select()"):
            if expected not in search_script:
                raise RuntimeError(f"search lifecycle omitted {expected}")

        navigation_script = (output / "_static" / "mpg-navigation.js").read_text(
            encoding="utf-8"
        )
        if "scrollIntoView" in navigation_script:
            raise RuntimeError("section tracking must not scroll the chapter navigation")

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
        for expected in ('.mpg-body .math {', 'font-weight: 400;',
                         'body.mpg-manual { background-image: none;',
                         '--mpg-compact-gutter: clamp(1rem, 4vw, 3rem);',
                         '.mpg-figure-compact',
                         '.mpg-window-diagram',
                         '.mpg-object-number,\n.mpg-code-fragment-link { text-decoration: none; }',
                         ':is(.mpg-object-number, .mpg-code-fragment-link):is(:hover, :focus-visible)',
                         '.mpg-body .katex { font-size: var(--mpg-math-size); }',
                         '.mpg-body .katex .mathtt {'):
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
                         r"\newcommand{\MPGLiterateBorderWidth}{.4pt}",
                         r"\MPGCodeTitleText{\MPGCurrentCodeTitle}",
                         r"pre_border-radius=0pt",
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
