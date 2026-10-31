"""Hash-checked literate code projections backed by canonical MPG sources."""

from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path

from docutils import nodes
from docutils.parsers.rst import directives
from docutils.statemachine import StringList
from pygments.formatters.latex import escape_tex
from sphinx import addnodes
from sphinx.directives.code import CodeBlock
from sphinx.errors import ExtensionError
from sphinx.util import logging

logger = logging.getLogger(__name__)


class MpgCodeTitle(nodes.General, nodes.Element):
    """An unnumbered literate-block title, distinct from a Program caption."""


def visit_mpg_code_title_html(translator, node: MpgCodeTitle) -> None:
    translator.body.append(translator.starttag(node, "div", CLASS="mpg-code-title"))
    title = translator.encode(node["title"])
    permalink_id = node.get("mpg_permalink_id")
    if permalink_id is None:
        translator.body.append(title)
    else:
        translator.body.append(
            f'<a class="mpg-code-fragment-link" '
            f'href="#{translator.encode(permalink_id)}">{title} '
            '<span class="mpg-code-equivalence" aria-hidden="true">&equiv;</span></a>'
        )


def depart_mpg_code_title_html(translator, node: MpgCodeTitle) -> None:
    translator.body.append("</div>")


def visit_mpg_code_title_latex(translator, node: MpgCodeTitle) -> None:
    # Use Sphinx's verbatim-title hook so the literate label and its code are
    # measured, kept, framed, and split as one object.  A separate preceding
    # block looks detached and can be stranded at a page boundary.
    translator.body.append(
        '\\global\\MPGUnnumberedVerbatimTitletrue\n'
        f'\\gdef\\MPGCurrentCodeTitle{{{translator.encode(node["title"])}}}\n'
        '\\gdef\\sphinxVerbatimTitle{\\relax}\n'
    )


def depart_mpg_code_title_latex(translator, node: MpgCodeTitle) -> None:
    pass


def _visit_literal_block(translator, node: nodes.literal_block, rewrite) -> None:
    """Render a literal block with Sphinx, then rewrite its highlighted output."""
    first = len(translator.body)
    try:
        type(translator).visit_literal_block(translator, node)
    finally:
        translator.body[first:] = [rewrite("".join(translator.body[first:]))]


def _link_placeholders(node: nodes.literal_block, output: str, link) -> str:
    """Make each resolved `// [child]` placeholder comment link to its fragment."""
    for comment, anchor in node.get("mpg_child_links", []):
        old, new = link(comment, anchor)
        if old not in output:
            logger.warning("cannot link MPG code placeholder %r", comment, location=node)
        output = output.replace(old, new, 1)
    return output


def visit_literal_block_html(translator, node: nodes.literal_block) -> None:
    def link(comment: str, anchor: str) -> tuple[str, str]:
        text = html.escape(comment, quote=False)
        return (
            f">{text}</span>",
            f'><a class="mpg-code-child-link" href="#{html.escape(anchor)}">{text}</a></span>',
        )

    _visit_literal_block(translator, node, lambda output: _link_placeholders(node, output, link))


def visit_literal_block_latex(translator, node: nodes.literal_block) -> None:
    def link(comment: str, anchor: str) -> tuple[str, str]:
        text = escape_tex(comment, "PYG")
        return f"{{{text}}}", f"{{\\hyperlink{{mpg-{anchor}}}{{{text}}}}}"

    def rewrite(output: str) -> str:
        output = _link_placeholders(node, output, link)
        anchor = node.get("mpg_latex_target")
        if anchor:
            # Inside the first code line the target is in horizontal mode and
            # cannot disturb the frame or the page breaking around it.
            line = output.index("\n", output.index("\\begin{sphinxVerbatim")) + 1
            output = f"{output[:line]}\\hypertarget{{mpg-{anchor}}}{{}}{output[line:]}"
        return output

    _visit_literal_block(translator, node, rewrite)


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _bytes_for_range(path: Path, record: dict) -> bytes:
    lines = path.read_bytes().splitlines(keepends=True)
    start = int(record["start_line"]) - 1
    end = int(record["end_line"])
    if start < 0 or end < start or end > len(lines):
        raise ExtensionError(f"invalid code projection range {path}:{start + 1}-{end}")
    return b"".join(lines[start:end])


def _checked_range(path: Path, record: dict, context: str) -> str:
    data = _bytes_for_range(path, record)
    actual = _digest(data)
    if actual != record["sha256"] or len(data) != int(record["bytes"]):
        raise ExtensionError(
            f"stale MPG code projection {context}: {path} no longer matches its source map; "
            "run `uv run --locked -- python rst/scripts/author_code.py refresh`, then verify the preview"
        )
    return data.decode("utf-8")


def _load_manifest(app, config) -> None:
    path = Path(config.mpg_code_manifest)
    if not path.is_absolute():
        path = Path(app.confdir) / path
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ExtensionError(f"cannot load MPG code manifest {path}: {error}") from error
    if data.get("schema") != "mpg-code-v1":
        raise ExtensionError(f"unsupported MPG code manifest schema in {path}")
    root = Path(config.mpg_code_root)
    if not root.is_absolute():
        root = Path(app.confdir) / root
    artifacts = {row["path"]: row for row in data.get("artifacts", [])}
    for relative, artifact in artifacts.items():
        source = root / relative
        try:
            payload = source.read_bytes()
        except OSError as error:
            raise ExtensionError(f"missing canonical MPG code artifact {source}: {error}") from error
        if _digest(payload) != artifact["sha256"] or len(payload) != int(artifact["bytes"]):
            raise ExtensionError(
                f"canonical MPG code artifact is stale: {source}; "
                "run `uv run --locked -- python rst/scripts/author_code.py refresh`, then verify the preview"
            )
    for key, projection in data.get("projections", {}).items():
        if projection["artifact"] not in artifacts:
            raise ExtensionError(f"projection {key!r} names unknown artifact {projection['artifact']}")
        source = root / projection["artifact"]
        _checked_range(source, projection, key)
        for ordinal, segment in enumerate(projection.get("segments", []), 1):
            if "source" in segment:
                _checked_range(source, segment["source"], f"{key} segment {ordinal}")
    config.mpg_code_manifest_data = data
    config.mpg_code_manifest_path = str(path)


def _link_pdf_downloads(app, doctree: nodes.document, docname: str) -> None:
    """Link to the same collected download filename published by HTML."""
    if app.builder.format != "latex":
        return
    for download in list(doctree.findall(addnodes.download_reference)):
        filename = download.get("filename")
        if filename:
            url = (
                f"https://www.gecode.dev/doc/{app.config.release}/modeling/"
                f"_downloads/{filename}"
            )
        else:
            url = download.get("refuri")
        if url:
            download.replace_self(nodes.reference("", "", *download.children, refuri=url))


def _prepare_program_anchors(app, doctree: nodes.document, docname: str) -> None:
    """Give Programs and fragments readable targets, and link child placeholders.

    The LaTeX builder resolves the assembled book as one doctree, so placeholders
    link across chapters there; an HTML placeholder links within its page.
    """
    if app.builder.format not in ("html", "latex"):
        return
    html_output = app.builder.format == "html"

    claimed = {
        target_id
        for element in doctree.findall(nodes.Element)
        for target_id in element.get("ids", [])
    }

    def claim(base: str) -> str:
        anchor = base
        suffix = 2
        while anchor in claimed:
            anchor = f"{base}-{suffix}"
            suffix += 1
        claimed.add(anchor)
        return anchor

    for container in doctree.findall(nodes.container) if html_output else ():
        if not container.get("literal_block"):
            continue
        caption = next(
            (child for child in container.children if isinstance(child, nodes.caption)),
            None,
        )
        if caption is None:
            continue

        ids = container.setdefault("ids", [])
        anchor = next(
            (target_id for target_id in ids
             if not (target_id.startswith("id") and target_id[2:].isdigit())),
            None,
        )
        if anchor is None:
            anchor = claim(nodes.make_id(f"program-{caption.astext()}") or "program")
            ids.append(anchor)

        container["mpg_permalink_id"] = anchor

    # A placeholder targets its child's title, else its Program, else its code.
    fragments: dict[str, str] = {}
    for title in doctree.findall(MpgCodeTitle) if html_output else ():
        anchor = claim(nodes.make_id(f"fragment-{title['projection_key']}") or "fragment")
        title["ids"].append(anchor)
        title["mpg_permalink_id"] = anchor
        fragments.setdefault(title["projection_key"], anchor)

    blocks = list(doctree.findall(nodes.literal_block))
    children = {child for block in blocks for _, child in block.get("mpg_child_placeholders", [])}
    for block in blocks:
        key = block.get("mpg_projection_key")
        if key not in children or key in fragments:
            continue
        anchor = block.parent.get("mpg_permalink_id") if html_output else None
        if anchor is None:
            anchor = claim(nodes.make_id(f"fragment-{key}") or "fragment")
            if html_output:
                block["ids"].append(anchor)
            else:
                block["mpg_latex_target"] = anchor
        fragments[key] = anchor

    for block in blocks:
        block["mpg_child_links"] = [
            [comment, fragments[child]]
            for comment, child in block.get("mpg_child_placeholders", [])
            if child in fragments
        ]


class MpgCodeDirective(CodeBlock):
    """Render a named literate projection from a canonical compiled source."""

    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = dict(CodeBlock.option_spec)
    option_spec.update(
        {
            "download": directives.unchanged,
            "small": directives.flag,
            "direct": directives.flag,
        }
    )

    def run(self) -> list[nodes.Node]:
        key = self.arguments[0].strip()
        data = self.env.app.config.mpg_code_manifest_data
        projection = data.get("projections", {}).get(key)
        if projection is None:
            raise self.error(f"unknown MPG code projection {key!r}")
        root = Path(self.env.app.config.mpg_code_root)
        source = root / projection["artifact"]
        self.env.note_dependency(str(source))
        self.env.note_dependency(self.env.app.config.mpg_code_manifest_path)

        segments = projection.get("segments")
        placeholders: list[list[str]] = []
        if segments is None:
            rendered = _checked_range(source, projection, key)
        else:
            pieces: list[str] = []
            for ordinal, segment in enumerate(segments, 1):
                if "source" in segment:
                    pieces.append(_checked_range(source, segment["source"], f"{key} segment {ordinal}"))
                else:
                    text = segment.get("text", "")
                    pieces.append(text)
                    if "child" in segment and text.strip().startswith("//"):
                        placeholders.append([text.strip(), segment["child"]])
            rendered = "".join(pieces)

        download = "download" in self.options
        download_label = self.options.get("download") or source.name
        small = "small" in self.options
        direct = "direct" in self.options
        options = dict(self.options)
        for custom in ("download", "small", "direct"):
            options.pop(custom, None)
        # Only the 99 legacy figure-wrapped programs have authored captions.
        # Literate insertion fragments are deliberately unnumbered; inventing
        # a caption here turned 190 snippets into spurious Programs and
        # polluted the classical Figures inventory.
        artifact_rows = {row["path"]: row for row in data["artifacts"]}
        language = artifact_rows[projection["artifact"]].get("language", "cpp")
        self.arguments = ["console" if language == "console" else language]
        self.options = options
        self.content = StringList(rendered.splitlines(), source=str(source))
        result = super().run()
        for block in result[0].findall(nodes.literal_block):
            block["mpg_projection_key"] = key
            block["mpg_child_placeholders"] = placeholders
        if projection.get("title") and not direct and "caption" not in options:
            title_node = MpgCodeTitle()
            title_node["title"] = projection["title"]
            title_node["projection_key"] = key
            result.insert(0, title_node)
        if small:
            for node in result:
                node["classes"].append("mpg-code-small")
        if download:
            label = download_label
            target = "/" + projection["artifact"].removeprefix("rst/")
            reference = addnodes.download_reference("", label, reftarget=target)
            paragraph = nodes.paragraph(classes=["mpg-code-download"])
            paragraph += nodes.Text("Download: ")
            paragraph += reference
            result.append(paragraph)
        return result


def setup(app):
    app.add_config_value("mpg_code_manifest", "manifests/code-projections.json", "env", types={str})
    app.add_config_value("mpg_code_root", "..", "env", types={str})
    app.add_config_value("mpg_code_manifest_data", {}, "env")
    app.add_config_value("mpg_code_manifest_path", "", "env", types={str})
    app.connect("config-inited", _load_manifest)
    app.connect("doctree-resolved", _link_pdf_downloads)
    app.connect("doctree-resolved", _prepare_program_anchors, priority=450)
    app.add_directive("mpg-code", MpgCodeDirective)
    app.add_node(
        nodes.literal_block,
        override=True,
        html=(visit_literal_block_html, None),
        latex=(visit_literal_block_latex, None),
    )
    app.add_node(
        MpgCodeTitle,
        html=(visit_mpg_code_title_html, depart_mpg_code_title_html),
        latex=(visit_mpg_code_title_latex, depart_mpg_code_title_latex),
    )
    return {"version": "1.0", "parallel_read_safe": True, "parallel_write_safe": True}
