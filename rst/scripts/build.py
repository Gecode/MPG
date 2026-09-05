#!/usr/bin/env python3
"""Fail-closed release builder for MPG HTML and PDF artifacts."""

from __future__ import annotations

import argparse
import json
from contextlib import contextmanager
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

from build_contract import source_date_epoch, validate_release

RST_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = RST_ROOT.parent
DEFAULT_SOURCE = RST_ROOT
DEFAULT_BUILD = RST_ROOT / "_build"


def run(command: list[str], cwd: Path | None = None, env: dict[str, str] | None = None) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=cwd, env=env, check=True)


@contextmanager
def staged_outputs(build: Path, target: str):
    """Publish completed outputs only; a failed build leaves the preview intact."""
    with tempfile.TemporaryDirectory(prefix=".mpg-build-", dir=build) as temporary:
        staged = Path(temporary)
        yield staged
        names = {"html": ("html",), "pdf": ("latex",), "all": ("html", "latex")}[target]
        for name in names:
            destination = build / name
            previous = staged / (name + "-previous")
            if destination.exists():
                destination.rename(previous)
            try:
                (staged / name).rename(destination)
            except OSError:
                if previous.exists():
                    previous.rename(destination)
                raise


def clean_outputs(build: Path) -> None:
    """Remove only known MPG build outputs, never an arbitrary parent tree."""
    for name in (
        "html",
        "latex",
        "reports",
        "example-validation",
        "gecode-vis",
    ):
        path = build / name
        if path.is_dir():
            try:
                shutil.rmtree(path)
            except OSError as error:
                raise RuntimeError(f"could not clean build output: {path}") from error
        elif path.exists():
            path.unlink()


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


def pagefind(output: Path) -> None:
    executable = REPOSITORY_ROOT / "node_modules" / ".bin" / "pagefind"
    if not executable.is_file():
        raise RuntimeError(
            "Pagefind is required for the HTML build; run `npm install` from the repository root"
        )
    run([
        str(executable),
        "--site",
        str(output),
        "--include-characters",
        "+_:",
        "--exclude-selectors",
        ".headerlink",
    ], cwd=REPOSITORY_ROOT)


def tailwind(output: Path) -> None:
    """Compile the manual shell locally so release bundles stay self-contained."""
    executable = REPOSITORY_ROOT / "node_modules" / ".bin" / "tailwindcss"
    if not executable.is_file():
        raise RuntimeError(
            "Tailwind CSS is required for the HTML build; run `npm install` "
            "from the repository root"
        )
    run([
        str(executable),
        "--input",
        str(RST_ROOT / "_static" / "mpg.css"),
        "--output",
        str(output / "_static" / "mpg.css"),
        "--minify",
    ], cwd=REPOSITORY_ROOT)


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
        "https://www.gecode.dev/doc/latest/MPG.pdf",
    )
    for url in expected_urls:
        if url not in urls:
            failures.append(f"PDF annotations omit canonical URL {url}")
    obsolete_host = "gecode" + ".org"
    if obsolete_host in urls or obsolete_host in rendered:
        failures.append("PDF retains the obsolete Gecode domain")

    if failures:
        raise RuntimeError("PDF fidelity checks failed: " + "; ".join(failures))
    print(
        "verified PDF references, metadata, canonical URLs, accessible glyphs, "
        "and text extraction"
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
    default_release = "development"
    if full_book:
        inventory = Path(os.environ.get("MPG_REFERENCE_INVENTORY", RST_ROOT / "release-reference-inventory.json"))
        default_release = json.loads(inventory.read_text())["gecode_version"]
    release = validate_release(os.environ.get("GECODE_VERSION", default_release))
    os.environ.setdefault("GECODE_VERSION", release)
    os.environ.setdefault("SOURCE_DATE_EPOCH", source_date_epoch(REPOSITORY_ROOT))
    if arguments.target == "clean":
        if build == RST_ROOT or build == RST_ROOT.parent:
            parser.error("refusing to clean the source or repository root")
        clean_outputs(build)
        return 0

    build.mkdir(parents=True, exist_ok=True)

    with publication_source(source, arguments.root_doc) as (publication, root_doc), \
            staged_outputs(build, arguments.target) as output:
        if arguments.target in {"html", "all"}:
            sphinx("dirhtml", publication, output / "html", arguments.jobs, root_doc)
            tailwind(output / "html")
            pagefind(output / "html")
            reference_prefix = f"/doc/{release}/reference/"
            run([
                sys.executable,
                str(RST_ROOT / "scripts" / "verify_html.py"),
                str(output / "html"),
                "--require-pagefind",
                "--release", release,
                "--site-prefix", reference_prefix,
                # The PDF is assembled beside the HTML and reference trees by
                # the release job, not inside Sphinx's HTML output directory.
                "--site-prefix", f"/doc/{release}/MPG.pdf",
            ])

            (output / "html" / ".mpg-version").write_text(release + "\n", encoding="utf-8")

        if arguments.target in {"pdf", "all"}:
            sphinx("latex", publication, output / "latex", arguments.jobs, root_doc)
            if full_book:
                adapt_latex_book(output / "latex" / "MPG.tex")
            if shutil.which("latexmk") is None:
                raise RuntimeError("latexmk is required for the PDF target")
            run([
                "latexmk",
                "-pdfxe",
                "-halt-on-error",
                "-interaction=nonstopmode",
                "MPG.tex",
            ], cwd=output / "latex")
            verify_pdf_build(
                output / "latex",
                release,
                full_book=full_book,
            )
            (output / "latex" / ".mpg-version").write_text(release + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
