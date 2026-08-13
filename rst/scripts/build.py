#!/usr/bin/env python3
"""Fail-closed release builder for MPG HTML and PDF artifacts."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

RST_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = RST_ROOT
DEFAULT_BUILD = RST_ROOT / "_build"


def run(command: list[str], cwd: Path | None = None, env: dict[str, str] | None = None) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=cwd, env=env, check=True)


def sphinx(builder: str, source: Path, output: Path, jobs: str, root_doc: str | None) -> None:
    environment = os.environ.copy()
    if root_doc:
        environment["MPG_ROOT_DOC"] = root_doc
    run([
        sys.executable,
        "-m",
        "sphinx",
        "-W",
        "--keep-going",
        "-n",
        "-T",
        "-j",
        jobs,
        "-c",
        str(RST_ROOT),
        "-b",
        builder,
        str(source),
        str(output),
    ], env=environment)


def adapt_latex_book(path: Path) -> None:
    """Put deferred Sphinx material back in the classical MPG book order.

    sphinxcontrib-bibtex writes the bibliography at the end of the merged
    LaTeX document even when its directive occurs before the changelog.  That
    produces an empty Bibliography chapter in the requested location and a
    second, populated bibliography after the license.  Keep this narrow and
    fail closed so a Sphinx output-shape change cannot silently reorder the
    published book.
    """
    text = path.read_text(encoding="utf-8")
    bibliography = re.compile(
        r"\n\\begin\{sphinxthebibliography\}\{\d+\}.*?"
        r"\\end\{sphinxthebibliography\}\n",
        re.DOTALL,
    )
    blocks = bibliography.findall(text)
    if len(blocks) != 1:
        raise RuntimeError(
            f"expected one deferred Sphinx bibliography in {path}, found {len(blocks)}"
        )
    placeholder = re.compile(
        r"\\chapter\{Bibliography\}\n"
        r"((?:\\label\{[^\n]+\})+)\n"
        r"\\sphinxstepscope\n\n+(?=\\chapter\{Changelog\})"
    )
    matches = list(placeholder.finditer(text))
    if len(matches) != 1:
        raise RuntimeError(
            f"expected one empty Bibliography chapter in {path}, found {len(matches)}"
        )
    block = blocks[0]
    text = bibliography.sub("\n", text, count=1)
    text, replacements = placeholder.subn(
        lambda match: match.group(1) + block + "\n", text, count=1
    )
    if replacements != 1:
        raise RuntimeError(f"failed to place bibliography in {path}")
    path.write_text(text, encoding="utf-8")


def verify_pdf_build(directory: Path, release: str, *, full_book: bool) -> None:
    """Reject the migration failures that previously reached the PDF."""
    log = (directory / "MPG.log").read_text(encoding="utf-8", errors="replace")
    forbidden_log = (
        "Missing character:",
        "There were undefined references",
        "Reference `",
        "Hyper reference `",
    )
    failures = [needle for needle in forbidden_log if needle in log]

    if full_book:
        expected_streams = {"MPG.lof": 213, "MPG.lotip": 78}
        for filename, expected in expected_streams.items():
            entries = sum(
                line.startswith(r"\contentsline")
                for line in (directory / filename).read_text(
                    encoding="utf-8", errors="replace"
                ).splitlines()
            )
            if entries != expected:
                failures.append(f"{filename} has {entries} entries, expected {expected}")

    if shutil.which("pdftotext") is None:
        raise RuntimeError("pdftotext is required for the PDF fidelity checks")
    text_path = directory / "MPG.txt"
    run(["pdftotext", "-layout", "MPG.pdf", text_path.name], cwd=directory)
    rendered = text_path.read_text(encoding="utf-8", errors="replace")
    leaked = re.search(r"``|:(?:math|ref|numref|cite(?:\:[a-z])?):|\bpart:[mcpbvs]\b", rendered)
    if leaked:
        failures.append(f"rendered authoring markup {leaked.group(0)!r}")
    if full_book:
        if len(re.findall(r"^\s*Bibliography\s*$", rendered, re.MULTILINE)) != 1:
            failures.append("the PDF does not contain exactly one Bibliography chapter")
        if re.search(r"missing (?:booktitle|year) in", rendered):
            failures.append("the rendered bibliography contains unresolved crossrefs")

    extraction_garbage = {
        "BoolDomExprand": "joined Program 7.1 caption",
        "dom()function": "joined Program 7.1 caption",
        "ǩ Important": "Font Awesome admonition icon",
        "cb n d": "Creative Commons icon font",
        "\ufffd": "Unicode replacement character",
    }
    for needle, description in extraction_garbage.items():
        if needle in rendered:
            failures.append(f"rendered text contains {description}: {needle!r}")

    if shutil.which("pdffonts") is None:
        raise RuntimeError("pdffonts is required for the PDF font checks")
    fonts = subprocess.run(
        ["pdffonts", "MPG.pdf"], cwd=directory, check=True,
        text=True, stdout=subprocess.PIPE,
    ).stdout
    for inaccessible_font in ("FontAwesome", "Dingbats", "CCIcons"):
        if inaccessible_font in fonts:
            failures.append(f"PDF embeds non-semantic icon font {inaccessible_font}")
    if shutil.which("pdfinfo") is None:
        raise RuntimeError("pdfinfo is required for the PDF metadata and URL checks")
    info = subprocess.run(
        ["pdfinfo", "MPG.pdf"], cwd=directory, check=True,
        text=True, stdout=subprocess.PIPE,
    ).stdout
    for field in ("Title:", "Subject:", "Keywords:", "Author:"):
        if not re.search(rf"^{field}\s+\S", info, re.MULTILINE):
            failures.append(f"PDF metadata field {field[:-1]} is empty")

    urls = subprocess.run(
        ["pdfinfo", "-url", "MPG.pdf"], cwd=directory, check=True,
        text=True, stdout=subprocess.PIPE,
    ).stdout
    expected_urls = (
        f"https://www.gecode.dev/doc/{release}/MPG.pdf",
        "https://www.gecode.dev/doc-latest/MPG.pdf",
    )
    for url in expected_urls:
        if url not in urls:
            failures.append(f"PDF annotations omit canonical URL {url}")
    obsolete_host = "gecode" + ".org"
    if obsolete_host in urls or obsolete_host in rendered:
        failures.append("PDF retains the obsolete Gecode domain")

    if failures:
        raise RuntimeError("PDF fidelity checks failed: " + "; ".join(failures))
    detail = ", 213 Figures entries, and 78 Tips entries" if full_book else ""
    print(
        "verified PDF references, metadata, canonical URLs, accessible glyphs, "
        f"and text extraction{detail}"
    )


@contextmanager
def publication_source(source: Path, root_doc: str | None):
    """Expose clean release routes without moving canonical figure sources."""
    if source != RST_ROOT:
        yield source, root_doc
        return
    with tempfile.TemporaryDirectory(prefix="mpg-sphinx-source-") as temporary:
        staged = Path(temporary)
        for child in sorted((RST_ROOT / "content").iterdir()):
            (staged / child.name).symlink_to(child, target_is_directory=child.is_dir())
        (staged / "figures").symlink_to(RST_ROOT / "figures", target_is_directory=True)
        (staged / "examples").symlink_to(RST_ROOT / "examples", target_is_directory=True)
        yield staged, root_doc or "index"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", choices=("html", "pdf", "all", "clean"))
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--build", type=Path, default=DEFAULT_BUILD)
    parser.add_argument("--jobs", default="auto")
    parser.add_argument("--root-doc", help="test-only root document override")
    arguments = parser.parse_args()

    source = arguments.source.resolve()
    build = arguments.build.resolve()
    full_book = source == RST_ROOT and arguments.root_doc is None
    if arguments.target == "clean":
        if build == RST_ROOT or build == RST_ROOT.parent:
            parser.error("refusing to remove the source or repository root")
        shutil.rmtree(build, ignore_errors=True)
        return 0

    with publication_source(source, arguments.root_doc) as (publication, root_doc):
        if arguments.target in {"html", "all"}:
            sphinx("dirhtml", publication, build / "html", arguments.jobs, root_doc)
            reference_prefix = f"/doc/{os.environ.get('GECODE_VERSION', 'development')}/reference/"
            run([
                sys.executable,
                str(RST_ROOT / "scripts" / "verify_html.py"),
                str(build / "html"),
                "--site-prefix", reference_prefix,
                # The PDF is assembled beside the HTML and reference trees by
                # the release job, not inside Sphinx's HTML output directory.
                "--site-prefix", f"/doc/{os.environ.get('GECODE_VERSION', 'development')}/MPG.pdf",
            ])

        if arguments.target in {"pdf", "all"}:
            sphinx("latex", publication, build / "latex", arguments.jobs, root_doc)
            if full_book:
                adapt_latex_book(build / "latex" / "MPG.tex")
            if shutil.which("latexmk") is None:
                raise RuntimeError("latexmk is required for the PDF target")
            run([
                "latexmk",
                "-pdfxe",
                "-halt-on-error",
                "-interaction=nonstopmode",
                "MPG.tex",
            ], cwd=build / "latex")
            verify_pdf_build(
                build / "latex",
                os.environ.get("GECODE_VERSION", "development"),
                full_book=full_book,
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
