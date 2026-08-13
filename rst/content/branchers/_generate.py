"""One-shot migration of the legacy brancher and search-engine chapters.

The shared programming-chapter converter owns the TeX prose conversion.  This
adapter supplies the production ``mpg-code`` projection directive and the two
search-tree drawings which have canonical SVG/PDF replacements.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[3]
BASE_PATH = ROOT / "rst/content/propagators/_generate.py"
SPEC = importlib.util.spec_from_file_location("mpg_programming_generator", BASE_PATH)
assert SPEC is not None and SPEC.loader is not None
base = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(base)

CONTRACT = json.loads((ROOT / "rst/manifests/source-coverage.json").read_text())
CODE_MANIFEST = json.loads((ROOT / "rst/manifests/code-projections.json").read_text())
MAPPINGS = {
    ROOT / item["source"]: ROOT / item["destination"]
    for item in CONTRACT["source_mappings"]
    if "/search/" in item["source"]
    and Path(item["source"]).name.startswith(("b-", "s-"))
}


class Converter(base.Converter):
    def __init__(self, src: Path):
        super().__init__(src)
        self.direct_displays = sorted(
            (
                site for site in CODE_MANIFEST["display_sites"]
                if site["source"] == self.source and site["site_kind"] == "direct-display"
            ),
            key=lambda site: site["source_line"],
        )
        self.direct_display_index = 0

    def protect_inline(self, text: str) -> str:
        text = base.replace_command(
            text,
            "gecoderef",
            1,
            lambda title: f"MPGAPIB{title}MPGAPIE",
        )
        return super().protect_inline(text)

    def postprocess(self, text: str, section_labels: bool = False) -> str:
        rendered = super().postprocess(text, section_labels)
        rendered = re.sub(r"MPGAPIB(.+?)MPGAPIE", r":api:`\1`", rendered)
        rendered = re.sub(r"(:api:`[^`]+`)(?=[A-Za-z])", r"\1 ", rendered)
        rendered = re.sub(r":ref:`Figure <([^`>]+)>`", r":numref:`\1`", rendered)
        # TeX's ``\?d?istance`` idiom deliberately joins a code-formatted
        # letter to the rest of a word.  A backslash-space is not the reST
        # equivalent (it starts an invalid interpreted-text construct).
        rendered = re.sub(r"``\\ ([A-Za-z])", r"``\1", rendered)
        # Role substitutions must not eat the following word.  Pandoc's
        # protected-token restoration loses this boundary for adjacent TeX
        # commands such as ``\autoref{...}shows``.
        rendered = re.sub(
            r"(:(?:api|ref|numref|cite(?::[a-z])?):`[^`]+`)(?=[A-Za-z(])",
            r"\1 ",
            rendered,
        )
        prefix = "branchers" if self.src.name.startswith("b-") else "search-engines"
        chapter = self.src.name[2:].removesuffix(".tex.in")
        rendered = re.sub(
            r"(?m)^\.\. _([a-z0-9-]+)\.-([0-9]+):$",
            lambda match: f".. _{prefix}:{chapter}:{match.group(1)}-{int(match.group(2)) + 1}:",
            rendered,
        )
        if self.src.name == "s-started.tex.in":
            marker = (
                ".. mpg-covered: table:docs/src/chapters/search/"
                "s-started.tex.in:243:tabular@docs/src/chapters/search/"
                "s-started.tex.in:243\n\n"
            )
            rendered = rendered.replace(".. container:: center\n", marker + ".. container:: center\n", 1)
        # Legacy \paragraph headings are run-in navigational signposts, not
        # section levels.  Rubrics preserve that visual and semantic role and
        # avoid corrupting the chapter/section/subsection hierarchy.
        rendered = re.sub(r"(?m)^([^\n]+)\n'{3,}$", r".. rubric:: \1", rendered)
        return self.normalize_directive_spacing(rendered)

    @staticmethod
    def normalize_directive_spacing(text: str) -> str:
        """Repair boundaries lost when protected directives are restored.

        The shared converter stores directives as opaque tokens while prose is
        passed through Pandoc.  Token restoration may remove the mandatory
        blank line after an ``mpg-code`` block or add blank lines between an
        image/figure directive and its options.  Normalize just those authored
        constructs, retaining all prose whitespace unchanged.
        """
        lines = text.splitlines()

        # Options belong immediately to their directive, even when the
        # directive is nested under ``only`` or ``container``.
        changed = True
        while changed:
            changed = False
            out: list[str] = []
            for index, line in enumerate(lines):
                if (
                    not line
                    and out
                    and index + 1 < len(lines)
                    and lines[index + 1].lstrip().startswith(":")
                    and (
                        ".. mpg-figure::" in out[-1]
                        or ".. mpg-tip::" in out[-1]
                        or ".. image::" in out[-1]
                        or out[-1].lstrip().startswith(":")
                    )
                ):
                    changed = True
                    continue
                out.append(line)
            lines = out

        # ``mpg-code`` has no directive body: after its contiguous options,
        # the next prose/marker must be separated by a blank line.
        out = []
        index = 0
        while index < len(lines):
            line = lines[index]
            out.append(line)
            match = re.match(r"^( *)\.\. mpg-code::", line)
            if not match:
                index += 1
                continue
            indent = len(match.group(1))
            index += 1
            while index < len(lines):
                candidate = lines[index]
                if candidate.startswith(" " * (indent + 3) + ":"):
                    out.append(candidate)
                    index += 1
                    continue
                break
            if index < len(lines) and lines[index] != "":
                out.append("")
        return "\n".join(out) + "\n"

    def literalinclude(self, key: str, caption: str | None, label: str | None, line: int) -> str:
        resolved = base.resolve_block(key, self.blocks)
        out = base.marker(self.source, "literal-projection", key)
        out += f".. mpg-code:: {resolved}\n"
        if caption:
            out += f"   :caption: {self.inline_text(caption)}\n"
        if label:
            out += f"   :name: {label}\n"
        if self.downloads.get(resolved.split(":", 1)[0]) is not None:
            out += "   :download:\n"
        out += "\n"
        if label:
            out = (
                base.marker(self.source, "caption", label)
                + base.marker(self.source, "figure", label)
                + out
            )
        return out

    def protect_structures(self, text: str) -> str:
        def direct_code(match: re.Match[str]) -> str:
            line = text.count("\n", 0, match.start()) + 1
            if self.direct_display_index >= len(self.direct_displays):
                raise ValueError(f"unmapped direct code display in {self.source}:{line}")
            site = self.direct_displays[self.direct_display_index]
            self.direct_display_index += 1
            if site["source_line"] != line:
                raise ValueError(
                    f"direct code display map drift in {self.source}: "
                    f"expected line {site['source_line']}, found {line}"
                )
            out = f".. mpg-code:: {site['key']}\n   :direct:\n"
            if site.get("small"):
                out += "   :small:\n"
            return self.token(out + "\n")

        direct_pattern = re.compile(
            r"\\begin\{(?:smallcode|code)\}.*?\\end\{(?:smallcode|code)\}",
            re.S,
        )
        text = direct_pattern.sub(direct_code, text)
        window_pattern = re.compile(r"\\begin\{window\}\[0,r,\{(.*?)\\end\{window\}", re.S)

        def replace_window(match: re.Match[str]) -> str:
            body = match.group(1)
            split = body.rfind("},{}]")
            if split < 0:
                return match.group(0)
            prose = body[split + len("},{}]"):].strip()
            if "commit distance" in prose:
                label = "fig:s:re:hybrid-tree"
                stem = "fig-s-re-hybrid-tree"
                alt = "Hybrid recomputation with commit distance two"
            elif "LAO as described" in prose:
                label = "fig:s:re:hybrid-lao-tree"
                stem = "fig-s-re-hybrid-lao-tree"
                alt = "Last alternative optimization with hybrid recomputation"
            else:
                return match.group(0)
            rendered = self.convert_fragment(prose).strip() + "\n\n"
            rendered = rendered.replace("sketched to the right", "shown below")
            rendered += f".. _{label}:\n\n"
            rendered += ".. only:: html\n\n"
            rendered += f"   .. image:: /figures/{stem}.svg\n"
            rendered += f"      :alt: {alt}\n"
            rendered += "      :class: mpg-window-diagram\n\n"
            rendered += ".. only:: latex\n\n"
            rendered += f"   .. image:: /figures/pdf/{stem}.pdf\n"
            rendered += f"      :alt: {alt}\n"
            rendered += "      :class: mpg-window-diagram\n"
            return self.token(rendered)

        text = window_pattern.sub(replace_window, text)
        assets = {
            "fig:s:re:ex": "fig-s-re-ex",
            "fig:s:re:lao:ex": "fig-s-re-lao-ex",
        }
        pattern = re.compile(r"\\begin\{figure\}(.*?)\\end\{figure\}", re.S)

        def replace(match: re.Match[str]) -> str:
            body = match.group(1)
            labels = re.findall(r"\\label\{([^}]*)\}", body)
            label = labels[-1] if labels else ""
            if label not in assets:
                return match.group(0)
            cap_match = re.search(r"\\caption\{", body)
            caption = label
            if cap_match:
                caption, _ = base.balanced(body, cap_match.end() - 1)
            rendered = base.marker(self.source, "caption", label)
            rendered += base.marker(self.source, "figure", label)
            rendered += f".. mpg-figure:: {self.inline_text(caption)}\n"
            rendered += f"   :name: {label}\n\n"
            rendered += "   .. only:: html\n\n"
            rendered += f"      .. image:: /figures/{assets[label]}.svg\n"
            rendered += f"         :alt: {self.inline_text(caption)}\n\n"
            rendered += "   .. only:: latex\n\n"
            rendered += f"      .. image:: /figures/pdf/{assets[label]}.pdf\n"
            rendered += f"         :alt: {self.inline_text(caption)}\n"
            return self.token(rendered)

        text = pattern.sub(replace, text)
        rendered = super().protect_structures(text)
        if self.direct_display_index != len(self.direct_displays):
            raise ValueError(
                f"unrendered direct code displays in {self.source}: "
                f"{len(self.direct_displays) - self.direct_display_index}"
            )
        return rendered

    def add_section_labels(self, text: str) -> str:
        lines = text.splitlines()
        output: list[str] = []
        used: dict[str, int] = {}
        prefix = "branchers" if self.src.name.startswith("b-") else "search-engines"
        chapter = self.src.name[2:].removesuffix(".tex.in")
        for index, line in enumerate(lines):
            is_title = (
                index + 1 < len(lines)
                and line.strip()
                and re.fullmatch(r"([=\-~^'])\1{2,}", lines[index + 1].strip()) is not None
            )
            if is_title:
                previous = len(output) - 1
                while previous >= 0 and not output[previous].strip():
                    previous -= 1
                has_label = previous >= 0 and output[previous].startswith(".. _") and output[previous].endswith(":")
                if not has_label:
                    slug = re.sub(r"[^a-z0-9]+", "-", line.lower()).strip("-") or "section"
                    used[slug] = used.get(slug, 0) + 1
                    suffix = f"-{used[slug]}" if used[slug] > 1 else ""
                    if output and output[-1].strip():
                        output.append("")
                    output.extend((f".. _{prefix}:{chapter}:{slug}{suffix}:", ""))
            output.append(line)
        return "\n".join(output) + "\n"


def main() -> None:
    for source, destination in sorted(MAPPINGS.items()):
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(Converter(source).convert())


if __name__ == "__main__":
    main()
