"""Hash-checked literate code projections backed by canonical MPG sources."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from docutils import nodes
from docutils.parsers.rst import directives
from docutils.statemachine import StringList
from sphinx import addnodes
from sphinx.directives.code import CodeBlock
from sphinx.errors import ExtensionError


class MpgCodeTitle(nodes.General, nodes.Element):
    """An unnumbered literate-block title, distinct from a Program caption."""


def visit_mpg_code_title_html(translator, node: MpgCodeTitle) -> None:
    translator.body.append('<div class="mpg-code-title">')
    translator.body.append(translator.encode(node["title"]))


def depart_mpg_code_title_html(translator, node: MpgCodeTitle) -> None:
    translator.body.append("</div>")


def visit_mpg_code_title_latex(translator, node: MpgCodeTitle) -> None:
    translator.body.append(f'\\MPGCodeTitle{{{translator.encode(node["title"])}}}\n')


def depart_mpg_code_title_latex(translator, node: MpgCodeTitle) -> None:
    pass


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
            "run rst/scripts/migrate_code.py during migration or update the canonical manifest intentionally"
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
            raise ExtensionError(f"canonical MPG code artifact is stale: {source}")
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
        if segments is None:
            rendered = _checked_range(source, projection, key)
        else:
            pieces: list[str] = []
            for ordinal, segment in enumerate(segments, 1):
                if "source" in segment:
                    pieces.append(_checked_range(source, segment["source"], f"{key} segment {ordinal}"))
                else:
                    pieces.append(segment.get("text", ""))
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
        insertion_keys = {
            site["key"]
            for site in data.get("display_sites", [])
            if site.get("site_kind") == "literate-insertion"
        }
        if key in insertion_keys and not direct and "caption" not in options:
            title = key.rsplit(":", 1)[-1]
            title_node = MpgCodeTitle()
            title_node["title"] = title
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
    app.add_directive("mpg-code", MpgCodeDirective)
    app.add_node(
        MpgCodeTitle,
        html=(visit_mpg_code_title_html, depart_mpg_code_title_html),
        latex=(visit_mpg_code_title_latex, depart_mpg_code_title_latex),
    )
    return {"version": "1.0", "parallel_read_safe": True, "parallel_write_safe": True}
