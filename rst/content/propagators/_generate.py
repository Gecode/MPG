"""One-shot, semantics-preserving converter for the legacy MPG p-* chapters.

This is kept beside its generated tranche while the migration is reviewed.  It
uses Pandoc only for ordinary LaTeX prose and tables; MPG labels, references,
tips, figures, and literate projections are handled explicitly.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "docs/src/chapters/programming"
OUT = ROOT / "rst/content/propagators"
CONTRACT = json.loads((ROOT / "rst/manifests/source-coverage.json").read_text())
CODE_MANIFEST = json.loads((ROOT / "rst/manifests/code-projections.json").read_text())
MAPPINGS = {
    Path(item["source"]).name: Path(item["destination"]).name
    for item in CONTRACT["source_mappings"]
    if "/programming/" in item["source"]
}
ITEMS = CONTRACT["items"]


def balanced(text: str, start: int, opening: str = "{", closing: str = "}") -> tuple[str, int]:
    assert text[start] == opening
    depth = 1
    i = start + 1
    while i < len(text) and depth:
        if text[i] == "\\":
            i += 2
            continue
        if text[i] == opening:
            depth += 1
        elif text[i] == closing:
            depth -= 1
        i += 1
    if depth:
        raise ValueError(f"unbalanced input at byte {start}")
    return text[start + 1 : i - 1], i


def command_args(text: str, start: int, name: str, required: int) -> tuple[list[str], int] | None:
    i = start + len(name) + 1
    while i < len(text) and text[i].isspace():
        i += 1
    if i < len(text) and text[i] == "[":
        _, i = balanced(text, i, "[", "]")
        while i < len(text) and text[i].isspace():
            i += 1
    args: list[str] = []
    for _ in range(required):
        if i >= len(text) or text[i] != "{":
            return None
        arg, i = balanced(text, i)
        args.append(arg)
        while i < len(text) and text[i].isspace():
            i += 1
    return args, i


def replace_command(text: str, name: str, required: int, render) -> str:
    marker = "\\" + name
    pos = 0
    while True:
        start = text.find(marker, pos)
        if start < 0:
            return text
        # Do not match a prefix of a longer control word.
        after_name = start + len(marker)
        if after_name < len(text) and text[after_name].isalpha():
            pos = after_name
            continue
        parsed = command_args(text, start, name, required)
        if parsed is None:
            pos = after_name
            continue
        args, end = parsed
        replacement = render(*args)
        text = text[:start] + replacement + text[end:]
        pos = start + len(replacement)


def strip_literate_definitions(text: str) -> str:
    lines: list[str] = []
    depth = 0
    for line in text.splitlines(keepends=True):
        if re.match(r"\s*\\begin\{litcode\}", line):
            depth += 1
            continue
        if depth and re.match(r"\s*\\end\{litcode\}", line):
            depth -= 1
            continue
        if not depth:
            lines.append(line)
    if depth:
        raise ValueError("unterminated litcode environment")
    return "".join(lines)


def parse_literate(src: Path) -> tuple[dict[str, str], dict[str, str]]:
    """Return exact block text and generated filename keyed by block id."""
    blocks: dict[str, str] = {}
    downloads: dict[str, str] = {}
    in_litcode = False
    in_texonly = False
    current_file = ""
    current = ""
    stack: list[str] = []
    for raw in src.read_text().splitlines(keepends=True):
        line = raw.rstrip("\n")
        match = re.match(r"\\begin\{litcode\}(?:\[texonly\])?\{(.*?)\}(?:\{.*?\})?", line)
        if match:
            in_litcode = True
            current_file = match.group(1)
            normalized = current_file.replace(" ", "-")
            if "." not in normalized:
                normalized += ".cpp"
            if "[texonly]" not in line:
                downloads[current_file] = normalized
            current = ""
            stack = []
            continue
        if not in_litcode:
            continue
        if line == r"\end{litcode}":
            blocks[current_file] = current
            in_litcode = False
            continue
        match = re.match(r"\s*\\begin\{litblock\}\{(.*)\}", line)
        if match:
            name = match.group(1)
            if name == "texonly":
                in_texonly = True
                stack.append(name)
                continue
            stack.extend((current, name))
            current = ""
            continue
        match = re.match(r"(\s*)\\end\{litblock\}", line)
        if match:
            name = stack.pop()
            if name == "texonly":
                in_texonly = False
                continue
            blocks[f"{current_file}:{name}"] = current
            previous = stack.pop()
            current = previous
            if name == "anonymous":
                current += match.group(1) + "...\n"
            elif name != "ignore":
                current += match.group(1) + f"// {name.split(':')[-1]}\n"
            continue
        current += raw
    return blocks, downloads


def resolve_block(key: str, blocks: dict[str, str]) -> str:
    if key in blocks:
        return key
    for candidate in blocks:
        if candidate.endswith(":" + key) or key.endswith(":" + candidate):
            return candidate
    raise KeyError(key)


def line_range(path: Path, excerpt: str) -> tuple[int, int] | None:
    source = path.read_text().splitlines()
    wanted = excerpt.rstrip("\n").splitlines()
    if not wanted or "..." in wanted:
        return None
    for start in range(len(source) - len(wanted) + 1):
        if source[start : start + len(wanted)] == wanted:
            return start + 1, start + len(wanted)
    return None


def marker(source: str, kind: str, item_id: str) -> str:
    matches = [
        item["key"]
        for item in ITEMS
        if item["source"] == source and item["kind"] == kind and item["id"] == item_id
    ]
    return "".join(f".. mpg-covered: {key}\n\n" for key in matches)


def pandoc(text: str) -> str:
    result = subprocess.run(
        ["pandoc", "-f", "latex", "-t", "rst", "--wrap=none"],
        input=text,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout


def indent(text: str, spaces: int = 3) -> str:
    pad = " " * spaces
    return "\n".join(pad + line if line else "" for line in text.rstrip().splitlines()) + "\n"


def normalize_semantic_directives(text: str) -> str:
    """Normalize protected directive headers after Pandoc's block round-trip."""
    lines = text.splitlines()
    output: list[str] = []
    index = 0
    semantic = re.compile(
        r"^(?P<indent>[ ]*)\.\. (?:mpg-(?:code|figure|tip|part)|image|rubric)::"
    )
    while index < len(lines):
        match = semantic.match(lines[index])
        if not match:
            output.append(lines[index])
            index += 1
            continue
        base = len(match.group("indent"))
        output.append(lines[index])
        index += 1
        options: list[str] = []
        while index < len(lines):
            if not lines[index].strip():
                lookahead = index + 1
                while lookahead < len(lines) and not lines[lookahead].strip():
                    lookahead += 1
                if (
                    lookahead < len(lines)
                    and len(lines[lookahead]) - len(lines[lookahead].lstrip(" ")) >= base + 3
                    and lines[lookahead].lstrip().startswith(":")
                ):
                    index = lookahead
                    continue
                break
            indentation = len(lines[index]) - len(lines[index].lstrip(" "))
            if indentation >= base + 3 and lines[index].lstrip().startswith(":"):
                options.append(lines[index])
                index += 1
                continue
            break
        output.extend(options)
        while index < len(lines) and not lines[index].strip():
            index += 1
        output.append("")
    return "\n".join(output) + "\n"


class Converter:
    def __init__(self, src: Path):
        self.src = src
        self.source = src.relative_to(ROOT).as_posix()
        self.blocks, self.downloads = parse_literate(src)
        self.tokens: dict[str, str] = {}
        self.serial = 0
        self.tip_items = [item for item in ITEMS if item["source"] == self.source and item["kind"] == "tip"]
        self.table_items = [item for item in ITEMS if item["source"] == self.source and item["kind"] == "table"]
        self.display_sites = [item for item in CODE_MANIFEST["display_sites"] if item["source"] == self.source]
        self.site_by_key = {item["key"]: item for item in self.display_sites}
        self.direct_sites = [item for item in self.display_sites if item["site_kind"] == "direct-display"]

    def token(self, rendered: str) -> str:
        value = f"MPGBLOCKTOKEN{self.serial}END"
        self.serial += 1
        self.tokens[value] = rendered
        return "\n\n" + value + "\n\n"

    def mpg_code(self, key: str, caption: str | None, label: str | None, line: int) -> str:
        if key not in CODE_MANIFEST["projections"]:
            raise KeyError(f"unknown canonical code projection {key!r}")
        site = self.site_by_key[key]
        out = f".. mpg-code:: {key}\n"
        if caption:
            out += f"   :caption: {self.inline_text(caption)}\n"
        if label:
            out += f"   :name: {label}\n"
        if site.get("small"):
            out += "   :small:\n"
        if site.get("direct") or site["site_kind"] == "direct-display":
            out += "   :direct:\n"
        # Only complete literate units are downloadable.  A named projection
        # such as ``less:posting`` is intentionally a view into ``less`` and
        # must not acquire a second, misleading download link.
        if key in self.downloads and site["site_kind"] == "literate-insertion":
            out += "   :download:\n"
        out += "\n"
        out = marker(self.source, "literal-projection", key) + out
        if label:
            out = (
                marker(self.source, "caption", label)
                + marker(self.source, "figure", label)
                + out
            )
        return out

    def inline_text(self, text: str) -> str:
        rendered = self.convert_fragment(text).strip()
        return " ".join(line.strip() for line in rendered.splitlines() if line.strip())

    def extract_environment(self, text: str, env: str, render) -> str:
        pattern = re.compile(rf"\\begin\{{{re.escape(env)}\}}(.*?)\\end\{{{re.escape(env)}\}}", re.S)
        while True:
            match = pattern.search(text)
            if not match:
                return text
            replacement = self.token(render(match.group(1), text.count("\n", 0, match.start()) + 1))
            text = text[: match.start()] + replacement + text[match.end() :]

    def protect_structures(self, text: str) -> str:
        # Extract every direct display before figures and tips. This preserves
        # nested displays and lets the canonical display-site manifest assign
        # their exact source-order keys.
        def code(body: str, line: int) -> str:
            if not self.direct_sites:
                raise RuntimeError(f"unmapped direct display in {self.source}:{line}")
            site = self.direct_sites.pop(0)
            return self.mpg_code(site["key"], None, None, line)

        text = self.extract_environment(text, "code", code)

        # Figures and tables contain code projections, SVG replacements, or
        # real tabular material.  Handle them before ordinary Pandoc parsing.
        def figure(body: str, line: int) -> str:
            labels = re.findall(r"\\label\{([^}]*)\}", body)
            label = labels[-1] if labels else None
            cap_match = re.search(r"\\caption(?:\[[^]]*\])?\{", body)
            caption = None
            if cap_match:
                caption, cap_end = balanced(body, cap_match.end() - 1)
                body = body[: cap_match.start()] + body[cap_end:]
            body = re.sub(r"\\label\{[^}]*\}", "", body)
            insert = re.search(r"\\insert(?:small)?litcode(?:\[direct\])?\{([^}]*)\}", body)
            if insert:
                return self.mpg_code(insert.group(1), caption, label, line)
            if label in {
                "fig:p:started:scheduling_propagators",
                "fig:p:started:propagators_views_varimp",
                "fig:p:domain:transitions",
            }:
                stem = label.replace(":", "-")
                out = marker(self.source, "caption", label) + marker(self.source, "figure", label)
                if "\\begin{tabular}" in body and self.table_items:
                    out += f".. mpg-covered: {self.table_items.pop(0)['key']}\n\n"
                out += f".. mpg-figure:: {self.inline_text(caption or label)}\n   :name: {label}\n\n"
                alt = self.inline_text(caption or label)
                out += "   .. only:: html\n\n"
                out += f"      .. image:: /figures/{stem}.svg\n         :alt: {alt}\n\n"
                out += "   .. only:: latex\n\n"
                out += f"      .. image:: /figures/pdf/{stem}.pdf\n         :alt: {alt}\n"
                return out
            converted = self.convert_fragment(body).strip()
            out = ""
            if label:
                out += marker(self.source, "caption", label) + marker(self.source, "figure", label)
            if "\\begin{tabular}" in body and self.table_items:
                out += f".. mpg-covered: {self.table_items.pop(0)['key']}\n\n"
            if label:
                out += f".. mpg-figure:: {self.inline_text(caption or label)}\n   :name: {label}\n\n"
                out += indent(converted, 3)
            else:
                out += converted + "\n"
            return out

        def table(body: str, line: int) -> str:
            labels = re.findall(r"\\label\{([^}]*)\}", body)
            label = labels[-1] if labels else None
            cap_match = re.search(r"\\caption(?:\[[^]]*\])?\{", body)
            caption = None
            if cap_match:
                caption, cap_end = balanced(body, cap_match.end() - 1)
                body = body[: cap_match.start()] + body[cap_end:]
            body = re.sub(r"\\label\{[^}]*\}", "", body)
            out = ""
            if label:
                out += marker(self.source, "caption", label) + marker(self.source, "table", label)
                out += f".. _{label}:\n\n"
            if caption:
                out += f".. rubric:: {self.inline_text(caption)}\n\n"
            out += self.convert_fragment(body).strip() + "\n"
            return out

        text = self.extract_environment(text, "figure", figure)
        text = self.extract_environment(text, "table", table)

        def important(body: str, line: int) -> str:
            return ".. important::\n\n" + indent(self.convert_fragment(body).strip(), 3)

        text = self.extract_environment(text, "important", important)

        # Tips are balanced commands rather than environments.
        marker_name = "\\tip"
        while marker_name in text:
            start = text.find(marker_name)
            parsed = command_args(text, start, "tip", 2)
            if parsed is None:
                break
            (title, body), end = parsed
            line = text.count("\n", 0, start) + 1
            labels = re.findall(r"\\label\{([^}]*)\}", body)
            item = self.tip_items.pop(0)
            rendered = f".. mpg-covered: {item['key']}\n\n" if item["verification"] == "coverage-marker" else ""
            rendered += f".. mpg-tip:: {self.inline_text(title)}\n"
            if labels:
                rendered += f"   :name: {labels[0]}\n"
                body = re.sub(r"\\label\{[^}]*\}", "", body)
            rendered += "\n" + indent(self.convert_fragment(body).strip(), 3)
            replacement = self.token(rendered)
            text = text[:start] + replacement + text[end:]

        # Non-figure literate inserts.
        for command in ("insertlitcode", "insertsmalllitcode"):
            needle = "\\" + command
            while needle in text:
                start = text.find(needle)
                parsed = command_args(text, start, command, 1)
                if parsed is None:
                    break
                (key,), end = parsed
                rendered = self.mpg_code(key, None, None, text.count("\n", 0, start) + 1)
                replacement = self.token(rendered)
                text = text[:start] + replacement + text[end:]
        return text

    def protect_inline(self, text: str) -> str:
        # Preserve public cross-reference targets and citations literally.
        text = replace_command(text, "otherref", 2, lambda target, title: f"MPGXREFB{target}MPGXMID{title}MPGXE")
        for name in ("autoref", "ref", "pageref"):
            text = replace_command(text, name, 1, lambda target: f"MPGREFB{target}MPGREFE")
        # Both optional and non-optional cite forms are accepted by command_args.
        text = replace_command(text, "cite", 1, lambda keys: f"MPGCITEB{keys}MPGCITEE")
        text = replace_command(text, "gecoderef", 1, lambda title: rf"\texttt{{{title}}}")
        text = replace_command(text, "CppInline", 1, lambda value: rf"\texttt{{{value}}}")
        text = replace_command(text, "litstr", 1, lambda value: rf"\texttt{{{value}}}")
        text = replace_command(text, "reifyeqv", 2, lambda a, b: rf"{a}=\mathtt{{1}}\Leftrightarrow {b}")
        text = replace_command(text, "reifyimp", 2, lambda a, b: rf"{a}=\mathtt{{1}}\Rightarrow {b}")
        text = replace_command(text, "reifypmi", 2, lambda a, b: rf"{a}=\mathtt{{1}}\Leftarrow {b}")
        text = replace_command(text, "range", 2, lambda a, b: rf"\left[{a}\;..\;{b}\right]")
        text = replace_command(text, "setc", 2, lambda a, b: rf"\{{{a}\mid {b}\}}")
        text = replace_command(text, "seqc", 3, lambda a, b, c: rf"\left\langle {a}\right\rangle_{{{b}}}^{{{c}}}")
        text = replace_command(text, "rseqc", 3, lambda a, b, c: rf"\left\langle [{a}_i..{b}_i]\right\rangle_{{i=0}}^{{{c}}}")
        text = re.sub(r"\\\?(.+?)\?", lambda m: r"\texttt{" + m.group(1) + "}", text)
        text = text.replace(r"\CPP{}", "C++").replace(r"\CPP", "C++")
        text = text.replace(r"\YES", "yes")
        text = text.replace(r"\boundsz", r"\operatorname{bounds}(\mathbb{Z})")
        text = text.replace(r"\arcsinh", r"\operatorname{arcsinh}")
        text = text.replace(r"\arccosh", r"\operatorname{arccosh}")
        text = text.replace(r"\arctanh", r"\operatorname{arctanh}")
        text = text.replace("~", " ")
        return text

    def add_section_labels(self, text: str) -> str:
        lines = text.splitlines()
        output: list[str] = []
        used: set[str] = set()
        current_section = ""
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
                    semantic_slug = slug
                    if semantic_slug in used and current_section:
                        semantic_slug = f"{current_section}-{slug}"
                    serial = 2
                    base = semantic_slug
                    while semantic_slug in used:
                        semantic_slug = f"{base}-{serial}"
                        serial += 1
                    used.add(semantic_slug)
                    chapter = self.src.name.removeprefix("p-").removesuffix(".tex.in")
                    if output and output[-1].strip():
                        output.append("")
                    output.extend((f".. _propagators:{chapter}:{semantic_slug}:", ""))
                if lines[index + 1].strip().startswith("-"):
                    current_section = re.sub(r"[^a-z0-9]+", "-", line.lower()).strip("-")
            output.append(line)
        return "\n".join(output) + "\n"

    def postprocess(self, text: str, section_labels: bool = False) -> str:
        text = re.sub(r"\.\. _`([^`]+)`: ?", r".. _\1:", text)
        text = re.sub(
            r"MPGREFB([^\s]+?)MPGREFE",
            lambda match: (
                f":numref:`{match.group(1)}`"
                if match.group(1).startswith("fig:")
                else f":numref:`{match.group(1)}`"
                if match.group(1).startswith("tip:")
                else f":ref:`{match.group(1)}`"
            ),
            text,
        )
        text = re.sub(
            r"MPGXREFB([^\s]+?)MPGXMID(.+?)MPGXE",
            lambda m: f":ref:`{m.group(2)} <{m.group(1)}>`",
            text,
        )
        text = re.sub(
            r"MPGCITEB(.+?)MPGCITEE",
            lambda m: ":cite:p:`" + ",".join(k.strip() for k in m.group(1).split(",")) + "`",
            text,
        )
        # Pandoc may escape token capitals neither in prose nor standalone lines.
        for token, rendered in self.tokens.items():
            text = re.sub(
                rf"(?m)^(?P<indent>\s*){token}\s*$",
                lambda match: "\n".join(
                    match.group("indent") + line if line else ""
                    for line in rendered.rstrip().splitlines()
                ),
                text,
            )
            text = text.replace(token, rendered.rstrip())
        text = re.sub(r"(?m)^\s+(\.\. mpg-covered:)", r"\1", text)
        # Literate insertions carry a root-level coverage marker.  Pandoc can
        # retain list indentation on the directive that follows it; remove
        # that indentation from the complete directive header/options block.
        # Direct displays have no marker and deliberately retain their source
        # nesting (notably inside tips and figures).
        text = re.sub(
            r"(?m)^(\.\. mpg-covered: literal-projection:[^\n]+\n\n)"
            r"(?P<indent>[ ]+)(\.\. mpg-code::[^\n]+\n)"
            r"(?P<options>(?:(?P=indent)[ ]{3}:[^\n]+\n)*)",
            lambda match: (
                match.group(1)
                + match.group(3)
                + "".join(
                    line[len(match.group("indent")) :] + "\n"
                    for line in match.group("options").splitlines()
                )
            ),
            text,
        )
        text = re.sub(r"(:ref:`[^`]+`)(?=[A-Za-z])", r"\1 ", text)
        text = re.sub(r"(:cite:p:`[^`]+`)(?=[A-Za-z])", r"\1 ", text)
        text = re.sub(r"(:ref:`[^`]+`)(?=[A-Za-z0-9(\[])", r"\1 ", text)
        # Explicit markup and directives are block constructs.  Pandoc can
        # place protected tokens directly against surrounding prose; restore
        # the required blank boundaries deterministically.
        text = re.sub(r"(?m)(?<!\n\n)^(\.\. (?:_|mpg-covered:|mpg-code::|mpg-figure::|figure::|image::|rubric::|mpg-tip::|important::|code-block::))", r"\n\1", text)
        text = re.sub(
            r"(?m)((?:^\.\. literalinclude::.*\n)(?:^   :.*\n)*)(?=\S)",
            lambda match: match.group(1) + "\n",
            text,
        )
        text = re.sub(
            r":math:`([^`]+)`",
            lambda match: ":math:`" + re.sub(r"\s+", " ", match.group(1)) + "`",
            text,
            flags=re.S,
        )
        # Terminate directive bodies, captions, grid tables, and literal
        # blocks before returning to document-level prose.
        text = re.sub(r"(?m)^(\s{3,}\S.*)\n(?=\S)", r"\1\n\n", text)
        text = text.replace(r"O(n \log | | | n)", r"O(n \log n)")
        text = re.sub(
            r"(?m)^   \| ``linear``\s+\| propagator with :math:`\\approx` linear complexity \(or :math:`O\(n \\log n\)`\)\s+\|$",
            "   | ``linear``                 | propagator with :math:`\\\\approx` linear complexity (or :math:`O(n \\\\log n)`)   |",
            text,
        )
        text = re.sub(r"[ \t]+\n", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = "\n".join(
            line for line in text.splitlines()
            if not (line.startswith(".. _") and not re.fullmatch(r"\.\. _[a-z][a-z0-9_]*(?:[-.:][a-z0-9_]+)*:", line))
        ) + "\n"
        # Recursive fragment conversion can re-introduce indentation after the
        # first normalization pass.  Make covered literate insertions proper
        # document-level directives at the final boundary, while leaving
        # uncovered direct displays nested in their owning tip or figure.
        text = re.sub(
            r"(?m)^(\.\. mpg-covered: literal-projection:[^\n]+\n\n)"
            r"(?P<indent>[ ]+)(\.\. mpg-code::[^\n]+\n)"
            r"(?P<options>(?:(?P=indent)(?:[ ]{3}:[^\n]+|[ ]*)\n)*)",
            lambda match: (
                match.group(1)
                + match.group(3)
                + "".join(
                    line[len(match.group("indent")) :] + "\n"
                    for line in match.group("options").splitlines()
                )
            ),
            text,
        )
        # Options are part of a directive header and may not be separated from
        # it (or one another) by blank lines.  Pandoc's token round-trip can
        # insert those blanks around protected block tokens.
        text = re.sub(
            r"(?m)^([ ]*\.\. mpg-code::[^\n]+)\n\n(?=[ ]+:[a-z])",
            r"\1\n",
            text,
        )
        text = re.sub(
            r"(?m)^([ ]+:[a-z][^\n]*)\n\n(?=[ ]+:[a-z])",
            r"\1\n",
            text,
        )
        text = re.sub(
            r"(:(?:num)?ref:`[^`]+`|:cite:p:`[^`]+`)(?=[A-Za-z0-9])",
            r"\1 ",
            text,
        )
        # A blank line terminates a reST grid table.  Pandoc inserts such
        # lines between LaTeX tabular rows; remove them only when both
        # neighbouring lines are unambiguously grid-table syntax.
        while re.search(r"(?m)^([ ]*[+|].*)\n\n(?=[ ]*[+|])", text):
            text = re.sub(
                r"(?m)^([ ]*[+|].*)\n\n(?=[ ]*[+|])",
                r"\1\n",
                text,
            )
        text = re.sub(r"(?m)^\.\s*$\n?", "", text)
        text = normalize_semantic_directives(text)
        text = text.strip() + "\n"
        if section_labels:
            text = self.add_section_labels(text)
            # LaTeX ``\paragraph`` headings are visual run-in headings, not a
            # new document hierarchy level.  Rubrics retain that appearance
            # without corrupting Sphinx's section tree; legacy and generated
            # stable targets immediately preceding them remain intact.
            text = re.sub(
                r"(?m)^([^\n]+)\n'{3,}\s*$",
                lambda match: f".. rubric:: {match.group(1)}",
                text,
            )
            text = normalize_semantic_directives(text)
        return text

    def convert_fragment(self, text: str) -> str:
        text = self.protect_inline(text)
        return self.postprocess(pandoc(text))

    def convert(self) -> str:
        text = strip_literate_definitions(self.src.read_text())
        text = self.protect_structures(text)
        text = self.protect_inline(text)
        return self.postprocess(pandoc(text), section_labels=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for src in sorted(SRC.glob("p-*.tex.in")):
        destination = OUT / MAPPINGS[src.name]
        destination.write_text(Converter(src).convert())


if __name__ == "__main__":
    main()
