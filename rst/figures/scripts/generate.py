#!/usr/bin/env python3
"""Build the MPG's shared HTML/PDF figure assets and inventory.

SVG is the canonical format for diagrams.  PDF derivatives are generated from
the SVGs for the LaTeX builder.  Historical Gist screenshots remain PNGs: they
are raster source material, so wrapping them in SVG would add no information.
"""

from __future__ import annotations

import csv
import base64
import html
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
FIGURES = HERE.parent
RST = FIGURES.parent
ROOT = RST.parent
os.environ.setdefault("SOURCE_DATE_EPOCH", "946684800")  # 2000-01-01, reproducible PDFs
LEGACY_CHAPTERS = ROOT / "docs" / "src" / "chapters"
EXTRACTED = ROOT / ".mpg" / "extract"
DIAGRAMS = FIGURES
PDF = FIGURES / "pdf"
SCREENSHOTS = FIGURES / "screenshots"
WORK = FIGURES / ".build"
MANIFESTS = RST / "manifests"

GRAPHIC_MARKERS = (
    r"\begin{pspicture}", r"\ncline", r"\ncarc", r"\rnode",
    r"\circlenode", r"\knboard", r"\knfield", r"\knmove",
)
CODE_MARKERS = (r"\insertlitcode", r"\litcode", r"\litcmd")


def run(*args: str, cwd: Path | None = None) -> None:
    completed = subprocess.run(args, cwd=cwd or ROOT, text=True, capture_output=True)
    if completed.returncode:
        details = (completed.stdout + "\n" + completed.stderr)[-5000:]
        raise RuntimeError(f"command failed ({completed.returncode}): {' '.join(args)}\n{details}")


def slug(label: str) -> str:
    # This is also the content migration convention. Keep underscores because
    # they are part of several established identifiers; change only the colon,
    # which is awkward in URLs and filenames.
    return label.replace(":", "-")


def latex_plain(value: str) -> str:
    value = re.sub(r"\\autoref\{([^}]+)\}", r"\1", value)
    value = re.sub(r"\\(?:CppInline|texttt|emph|inst)\{([^{}]*)\}", r"\1", value)
    value = re.sub(r"\\[A-Za-z@]+", "", value)
    value = value.replace("$", "").replace("{", "").replace("}", "")
    return re.sub(r"\s+", " ", value).strip()


def figure_blocks(text: str):
    start_re = re.compile(r"\\begin\{figure\}(?:\[[^]]*\])?")
    end_token = r"\end{figure}"
    for match in start_re.finditer(text):
        end = text.find(end_token, match.end())
        if end >= 0:
            yield match.start(), text[match.end():end]


def caption_of(block: str) -> str:
    # Captions in MPG do not contain balanced groups deeper than one level.
    pos = block.rfind(r"\caption{")
    if pos < 0:
        return ""
    i, depth = pos + len(r"\caption{"), 1
    result: list[str] = []
    while i < len(block) and depth:
        ch = block[i]
        if ch == "{" and (i == 0 or block[i - 1] != "\\"):
            depth += 1
        elif ch == "}" and (i == 0 or block[i - 1] != "\\"):
            depth -= 1
            if depth == 0:
                break
        result.append(ch)
        i += 1
    return "".join(result)


def inventory() -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for path in sorted(LEGACY_CHAPTERS.rglob("*.tex.in")):
        text = path.read_text()
        for offset, block in figure_blocks(text):
            labels = re.findall(r"\\label\{([^}]+)\}", block)
            caption = caption_of(block)
            includes = re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}", block)
            if labels and labels[-1] == "fig:intro:gecode_architecture":
                kind = "semantic-redraw"
            elif any(marker in block for marker in GRAPHIC_MARKERS):
                kind = "legacy-vector-conversion"
            elif includes:
                kind = "screenshot"
            elif labels and labels[-1] in {"fig:c:nonogram:ex", "fig:c:nonogram:ex-sol"}:
                kind = "data-diagram"
            elif r"\begin{tabular}" in block:
                kind = "semantic-table"
            elif any(marker in block for marker in CODE_MARKERS):
                kind = "executable-code"
            else:
                kind = "literal-output-or-code"
            label = labels[-1] if labels else ""
            asset = ""
            pdf = ""
            if kind in {"legacy-vector-conversion", "semantic-redraw", "data-diagram"} and label:
                asset = f"figures/{slug(label)}.svg"
                pdf = f"figures/pdf/{slug(label)}.pdf"
            elif kind == "screenshot":
                asset = f"figures/{slug(label)}.svg"
                pdf = f"figures/pdf/{slug(label)}.pdf"
            records.append({
                "source": str(path.relative_to(ROOT)),
                "line": text.count("\n", 0, offset) + 1,
                "label": label,
                "labels": labels,
                "caption_latex": caption,
                "caption": latex_plain(caption),
                "alt": latex_plain(caption) or (label.replace(":", " ") if label else "MPG figure"),
                "kind": kind,
                "legacy_includes": includes,
                "html_asset": asset,
                "pdf_asset": pdf,
            })
    return records


def preceding_definitions(text: str, body: str) -> str:
    """Return chapter-local command definitions needed by later figures."""
    definitions: list[str] = []
    local_names = set(re.findall(r"\\(?:re)?newcommand\s*\{(\\[^}]+)\}", body))
    command = re.compile(r"\\(?:re)?newcommand\s*\{")
    for match in command.finditer(text):
        i = match.end()
        depth = 1
        while i < len(text) and depth:
            if text[i] == "{" and text[i - 1] != "\\":
                depth += 1
            elif text[i] == "}" and text[i - 1] != "\\":
                depth -= 1
            i += 1
        while i < len(text) and text[i].isspace():
            i += 1
        if i < len(text) and text[i] == "[":
            i = text.find("]", i) + 1
        while i < len(text) and text[i].isspace():
            i += 1
        if i >= len(text) or text[i] != "{":
            continue
        depth, i = 1, i + 1
        while i < len(text) and depth:
            if text[i] == "{" and text[i - 1] != "\\":
                depth += 1
            elif text[i] == "}" and text[i - 1] != "\\":
                depth -= 1
            i += 1
        definition = text[match.start():i]
        name = re.search(r"\\(?:re)?newcommand\s*\{(\\[^}]+)\}", definition)
        if not name or name.group(1) not in local_names:
            definitions.append(definition)
    return "\n".join(definitions)


def extracted_block(record: dict[str, object]) -> str:
    source = ROOT / str(record["source"])
    expanded = EXTRACTED / source.name.removesuffix(".in")
    text = expanded.read_text()
    wanted = str(record["label"])
    for offset, block in figure_blocks(text):
        labels = re.findall(r"\\label\{([^}]+)\}", block)
        if wanted in labels and labels[-1] == wanted:
            caption = block.rfind(r"\caption{")
            body = block[:caption] if caption >= 0 else block
            return preceding_definitions(text[:offset], body) + "\n" + body
    raise RuntimeError(f"expanded figure not found: {wanted} in {expanded}")


def add_accessibility(svg_path: Path, title: str, description: str) -> None:
    text = svg_path.read_text()
    if "<title" in text:
        return
    ident = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "mpg-figure"
    insert = (
        f'<title id="{ident}-title">{html.escape(title)}</title>\n'
        f'<desc id="{ident}-desc">{html.escape(description)}</desc>\n'
    )
    text = re.sub(r"<svg\b", f'<svg role="img" aria-labelledby="{ident}-title {ident}-desc"', text, count=1)
    svg_start = text.index("<svg")
    svg_end = text.index(">", svg_start) + 1
    text = text[:svg_end] + "\n" + insert + text[svg_end:]
    svg_path.write_text(text)


def build_legacy_vector(record: dict[str, object], preamble: str) -> None:
    label = str(record["label"])
    name = slug(label)
    target = DIAGRAMS / f"{name}.svg"
    if target.is_file() and "--force" not in sys.argv:
        return
    work = WORK / name
    work.mkdir(parents=True, exist_ok=True)
    wrapper = work / "figure.tex"
    body = extracted_block(record)
    wrapper.write_text(
        preamble
        + "\n\\usepackage[active,tightpage]{preview}\n"
        + "\\begin{document}\n\\makeatletter\\def\\@captype{figure}\\makeatother\n\\begin{preview}\n"
        + body
        + "\n\\end{preview}\n\\end{document}\n"
    )
    run("latex", "-interaction=nonstopmode", "-halt-on-error", f"-output-directory={work}", str(wrapper))
    ghostscript_libraries = sorted(Path("/opt/homebrew/Cellar/ghostscript").glob("*/lib/libgs.dylib"))
    if not ghostscript_libraries:
        raise RuntimeError("dvisvgm requires Ghostscript's libgs.dylib to convert PSTricks specials")
    run(
        "dvisvgm", f"--libgs={ghostscript_libraries[-1]}", "--page=1",
        "--no-fonts", "--exact", "--bbox=min", "-o", str(target),
        str(work / "figure.dvi"),
    )
    add_accessibility(target, str(record["caption"]), str(record["alt"]))


def nonogram_svg(solution: bool) -> str:
    rows = [
        ".##...##.", "####.####", "#..###..#", "##..#..##", ".#.....#.",
        ".##...##.", "..##.##..", "...###...", "....#....",
    ]

    def hints(line: str) -> list[int]:
        result, run_length = [], 0
        for cell in line + ".":
            if cell == "#":
                run_length += 1
            elif run_length:
                result.append(run_length)
                run_length = 0
        return result

    columns = ["".join(row[x] for row in rows) for x in range(9)]
    row_hints, col_hints = list(map(hints, rows)), list(map(hints, columns))
    cell, left, top = 36, 88, 80
    width, height = left + 9 * cell + 18, top + 9 * cell + 18
    title = "Solution to the example nonogram" if solution else "Example nonogram puzzle"
    bits = [
        f'<svg xmlns="http://www.w3.org/2000/svg" role="img" viewBox="0 0 {width} {height}">',
        f"<title>{title}</title>",
        "<desc>A nine by nine nonogram with row and column hints; "
        + ("filled cells show the solution." if solution else "the grid is empty for solving.")
        + "</desc>",
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<g font-family="Charter, Georgia, serif" font-size="15" fill="#17211d">',
    ]
    for y, values in enumerate(row_hints):
        bits.append(f'<text x="{left - 12}" y="{top + (y + .66) * cell}" text-anchor="end">{" ".join(map(str, values))}</text>')
    for x, values in enumerate(col_hints):
        for j, value in enumerate(values):
            yy = top - 14 - (len(values) - 1 - j) * 18
            bits.append(f'<text x="{left + (x + .5) * cell}" y="{yy}" text-anchor="middle">{value}</text>')
    bits.append("</g>")
    bits.append('<g stroke="#66756f" stroke-width="1" shape-rendering="crispEdges">')
    for y, row in enumerate(rows):
        for x, value in enumerate(row):
            fill = "#086f42" if solution and value == "#" else "#fffdf8"
            bits.append(f'<rect x="{left + x * cell}" y="{top + y * cell}" width="{cell}" height="{cell}" fill="{fill}"/>')
    bits.append("</g></svg>\n")
    return "\n".join(bits)


def architecture_svg() -> str:
    """Authored, maintainable redraw of the MPG architecture overview."""
    modules = ("Int", "Set", "Float", "Search")
    module_markup = []
    for index, name in enumerate(modules):
        x = 304 + index * 112
        module_markup.append(
            f'<g><rect x="{x}" y="142" width="92" height="150" fill="#ffffff" '
            f'stroke="#17211d"/><text class="module" x="{x + 46}" y="208">{name}</text>'
            f'<text class="small" x="{x + 46}" y="231">module</text></g>'
        )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" role="img" viewBox="0 0 1000 390">
<title>Gecode architecture</title>
<desc>The Modeling layer spans the Int, Set, Float, and Search modules. Programming propagators and branchers extends those modules from the left. Programming variables and programming search engines are extension areas on the right. Every module rests on the Gecode kernel.</desc>
<style>
  text {{ font-family: Charter, Georgia, serif; fill: #17211d; }}
  .label {{ font-size: 21px; font-weight: 700; text-anchor: middle; }}
  .module {{ font: 700 19px "Bera Mono", "DejaVu Sans Mono", monospace; text-anchor: middle; }}
  .small {{ font-size: 15px; text-anchor: middle; }}
  .side {{ font-size: 18px; font-weight: 700; text-anchor: middle; }}
  .side-small {{ font-size: 13px; text-anchor: middle; }}
</style>
<rect width="1000" height="390" fill="#ffffff"/>
<rect x="260" y="28" width="710" height="76" fill="#d1e6dc" stroke="#0b7646" stroke-width="2"/>
<text class="label" x="615" y="74">Modeling</text>
<rect x="20" y="142" width="260" height="150" fill="#c9deee" stroke="#005ca1" stroke-width="2"/>
<text class="side" x="150" y="205">Programming propagators</text>
<text class="side" x="150" y="231">and branchers</text>
{''.join(module_markup)}
<rect x="764" y="142" width="94" height="150" fill="#f7d4a8" stroke="#eb8920" stroke-width="2"/>
<text class="side-small" x="811" y="198">Programming</text><text class="side" x="811" y="229">variables</text>
<rect x="876" y="142" width="94" height="150" fill="#f2c1bd" stroke="#da251d" stroke-width="2"/>
<text class="side-small" x="923" y="188">Programming</text><text class="side-small" x="923" y="211">search</text><text class="side" x="923" y="240">engines</text>
<rect x="260" y="316" width="710" height="52" fill="#ffffff" stroke="#17211d" stroke-width="2"/>
<text class="label" x="615" y="349">Gecode kernel</text>
</svg>\n'''


def build_data_diagrams() -> None:
    mapping = {
        "fig-intro-gecode_architecture": architecture_svg(),
        "fig-c-nonogram-ex": nonogram_svg(False),
        "fig-c-nonogram-ex-sol": nonogram_svg(True),
    }
    for name, contents in mapping.items():
        (DIAGRAMS / f"{name}.svg").write_text(contents)


def build_screenshots(records: list[dict[str, object]]) -> None:
    referenced: set[str] = set()
    for record in records:
        referenced.update(Path(str(value)).stem for value in record["legacy_includes"])
    # Preserve all historical screenshots, including currently unreferenced menu
    # captures, so the inventory is complete and later prose can use them.
    for source in sorted((ROOT / "images").glob("*.png")):
        shutil.copy2(source, SCREENSHOTS / source.name)
    asset_records = []
    for source in sorted((ROOT / "images").glob("*.png")):
        asset_records.append({
            "legacy": str(source.relative_to(ROOT)),
            "legacy_eps": str(source.with_suffix(".eps").relative_to(ROOT)) if source.with_suffix(".eps").is_file() else "",
            "asset": str((SCREENSHOTS / source.name).relative_to(RST)),
            "referenced": source.stem in referenced,
            "format": "PNG",
        })
    (MANIFESTS / "raster-assets.json").write_text(json.dumps(asset_records, indent=2) + "\n")


def png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError(f"not a PNG: {path}")
    return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")


def build_screenshot_figures(records: list[dict[str, object]]) -> None:
    """Create self-contained SVG/PDF figure wrappers around source PNGs."""
    for record in records:
        if record["kind"] != "screenshot":
            continue
        images = [ROOT / "images" / f"{Path(str(name)).stem}.png" for name in record["legacy_includes"]]
        dimensions = [png_size(path) for path in images]
        gap = 24 if len(images) > 1 else 0
        width = sum(size[0] for size in dimensions) + gap * (len(images) - 1)
        height = max(size[1] for size in dimensions)
        title = str(record["caption"])
        description = str(record["alt"])
        target = RST / str(record["html_asset"])
        bits = [
            f'<svg xmlns="http://www.w3.org/2000/svg" role="img" viewBox="0 0 {width} {height}">',
            f"<title>{html.escape(title)}</title>",
            f"<desc>{html.escape(description)}</desc>",
        ]
        x = 0
        for path, (image_width, image_height) in zip(images, dimensions):
            payload = base64.b64encode(path.read_bytes()).decode("ascii")
            y = (height - image_height) / 2
            bits.append(
                f'<image x="{x}" y="{y:g}" width="{image_width}" height="{image_height}" '
                f'href="data:image/png;base64,{payload}"/>'
            )
            x += image_width + gap
        bits.append("</svg>\n")
        target.write_text("\n".join(bits))


def build_logo() -> None:
    """Migrate the cover logo from EPS to an outlined SVG plus PDF."""
    source = ROOT / "images" / "gecode-logo.eps"
    work = WORK / "gecode-logo"
    work.mkdir(parents=True, exist_ok=True)
    intermediate = work / "gecode-logo.pdf"
    target = DIAGRAMS / "gecode-logo.svg"
    if "--force" in sys.argv or not target.is_file():
        run(
            "gs", "-q", "-dSAFER", "-dBATCH", "-dNOPAUSE",
            "-sDEVICE=pdfwrite", "-dEPSCrop", f"-sOutputFile={intermediate}",
            str(source),
        )
        run("pdftocairo", "-svg", str(intermediate), str(target))
        add_accessibility(target, "Gecode", "The four-color Gecode logo.")
    (MANIFESTS / "non-figure-assets.json").write_text(json.dumps([{
        "legacy": "images/gecode-logo.eps",
        "html_asset": "figures/gecode-logo.svg",
        "pdf_asset": "figures/pdf/gecode-logo.pdf",
        "kind": "outlined-vector-logo",
        "alt": "Gecode",
    }], indent=2) + "\n")


def svg_to_pdf() -> None:
    for source in sorted(DIAGRAMS.glob("*.svg")):
        target = PDF / (source.stem + ".pdf")
        if (
            target.is_file()
            and target.stat().st_mtime_ns >= source.stat().st_mtime_ns
            and "--force" not in sys.argv
            and "--pdf-force" not in sys.argv
        ):
            continue
        run("rsvg-convert", "-f", "pdf", "-o", str(target), str(source))


def write_manifests(records: list[dict[str, object]]) -> None:
    MANIFESTS.mkdir(parents=True, exist_ok=True)
    (MANIFESTS / "figures.json").write_text(json.dumps(records, indent=2) + "\n")
    fields = ["source", "line", "label", "kind", "caption", "alt", "html_asset", "pdf_asset"]
    with (MANIFESTS / "figures.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)


def main() -> int:
    for directory in (DIAGRAMS, PDF, SCREENSHOTS, WORK, MANIFESTS):
        directory.mkdir(parents=True, exist_ok=True)
    records = inventory()
    write_manifests(records)
    macro_text = (ROOT / "docs/src/static/macros.tex").read_text()
    macro_tail = macro_text[macro_text.index("% Redefine math tt alphabet"):]
    preamble = rf"""
\documentclass[12pt]{{report}}
\usepackage[T1]{{fontenc}}
\usepackage[charter]{{mathdesign}}
\usepackage[scaled=0.88]{{beramono}}
\usepackage{{ifthen,amsmath,amsthm,pifont,xcolor,pstricks,pstricks-add,pst-node,subfigure,calc,colortbl,fmtcount,ccicons}}
\definecolor{{GecodeGreen}}{{rgb}}{{0.04314,0.46275,0.27451}}
\definecolor{{GecodeBlue}}{{rgb}}{{0,0.36078,0.631273}}
\definecolor{{GecodeRed}}{{rgb}}{{0.8549,0.1451,0.1137255}}
\definecolor{{GecodeOrange}}{{rgb}}{{0.9216,0.537255,0.10588}}
\colorlet{{GecodeGreenOp20}}{{GecodeGreen!20}}
\colorlet{{GecodeBlueOp10}}{{GecodeBlue!10}}
\colorlet{{GecodeBlueOp20}}{{GecodeBlue!20}}
\colorlet{{GecodeBlueOp30}}{{GecodeBlue!30}}
\colorlet{{GecodeBlueOp40}}{{GecodeBlue!40}}
\colorlet{{GecodeRedOp20}}{{GecodeRed!20}}
\colorlet{{GecodeOrangeOp20}}{{GecodeOrange!20}}
\colorlet{{GecodeGreenOp50}}{{GecodeGreen!50}}
\colorlet{{GecodeBlueOp50}}{{GecodeBlue!50}}
\colorlet{{GecodeRedOp50}}{{GecodeRed!50}}
\colorlet{{GecodeOrangeOp50}}{{GecodeOrange!50}}
\providecommand{{\href}}[2]{{#2}}
\providecommand{{\autoref}}[1]{{}}
\providecommand{{\hypertarget}}[2]{{#2}}
\providecommand{{\hyperlink}}[2]{{#2}}
\providecommand{{\sectionautorefname}}{{Section}}
\providecommand{{\subsectionautorefname}}{{Section}}
\providecommand{{\chapterautorefname}}{{Chapter}}
\providecommand{{\GecodeVersion}}{{6.4.0}}
""" + macro_tail
    for record in records:
        if record["kind"] in {"legacy-vector-conversion", "semantic-redraw"}:
            print(f"vector: {record['label']}")
            build_legacy_vector(record, preamble)
    build_data_diagrams()
    build_screenshots(records)
    build_screenshot_figures(records)
    build_logo()
    svg_to_pdf()
    expected = [record for record in records if record["kind"] in {"legacy-vector-conversion", "semantic-redraw", "data-diagram", "screenshot"}]
    missing = [record["label"] for record in expected if not (RST / str(record["html_asset"])).is_file() or not (RST / str(record["pdf_asset"])).is_file()]
    if missing:
        print("missing figure derivatives: " + ", ".join(map(str, missing)), file=sys.stderr)
        return 1
    print(f"inventoried {len(records)} figure environments; generated {len(expected)} SVG/PDF pairs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
