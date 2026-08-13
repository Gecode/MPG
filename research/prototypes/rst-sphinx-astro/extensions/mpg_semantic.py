"""Strict resolved-doctree exporter and release-inventory API role for MPG."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from docutils import nodes
from sphinx import addnodes
from sphinx.builders import Builder
from sphinx.roles import SphinxRole
from sphinx.util import logging
from sphinx.util.nodes import split_explicit_title
from docutils.parsers.rst import Directive, directives

LOGGER = logging.getLogger(__name__)


class MpgPart(nodes.General, nodes.Element):
    pass


class MpgTip(nodes.Admonition, nodes.Element):
    pass


class MpgPartDirective(Directive):
    required_arguments = 1
    final_argument_whitespace = True
    has_content = True
    option_spec = {
        "authors": directives.unchanged_required,
        "letter": directives.unchanged_required,
    }

    def run(self):
        node = MpgPart()
        node["title"] = self.arguments[0]
        node["authors"] = self.options.get("authors", "")
        letter = self.options.get("letter", "")
        if len(letter) != 1 or not letter.isascii() or not letter.isalpha():
            raise self.error(":letter: must be one ASCII letter")
        node["part_number"] = ord(letter.upper()) - ord("A") + 1
        self.state.nested_parse(self.content, self.content_offset, node)
        return [node]


class MpgTipDirective(Directive):
    required_arguments = 1
    final_argument_whitespace = True
    has_content = True

    def run(self):
        node = MpgTip()
        node["title"] = self.arguments[0]
        self.state.nested_parse(self.content, self.content_offset, node)
        return [node]


def visit_mpg_part_latex(translator, node):
    title = translator.encode(node["title"])
    authors = translator.encode(node["authors"])
    translator.body.append(
        f"\\MPGSetPartAuthors{{{authors}}}\n"
        "\\MPGSetPartBlurb{%\n"
    )
    node["latex_title"] = title


def depart_mpg_part_latex(translator, node):
    translator.body.append(
        f"}}\n\\MPGPartNumber{{{node['part_number']}}}{{{node['latex_title']}}}\n"
    )


def visit_mpg_tip_latex(translator, node):
    translator.body.append(f"\\begin{{MPGTip}}{{{translator.encode(node['title'])}}}\n")


def depart_mpg_tip_latex(translator, node):
    translator.body.append("\\end{MPGTip}\n")


class ApiRole(SphinxRole):
    def run(self):
        inventory = self.env.app.config.mpg_reference_inventory_data
        _explicit, title, target = split_explicit_title(self.text)
        item = inventory["objects"].get(target)
        if item is None:
            LOGGER.warning("API symbol %s is absent from imported Gecode inventory", target,
                           location=(self.env.docname, self.lineno), type="mpg", subtype="api")
            return [nodes.literal(target, target)], []
        ref = nodes.reference(title, title, refuri=inventory["base_url"] + item["url"])
        ref["classes"].append("api-symbol")
        ref["api_symbol"] = target
        ref["inventory_version"] = inventory["gecode_version"]
        return [ref], []


def _text(node: nodes.Node) -> str:
    return node.astext()


class SemanticBuilder(Builder):
    name = "mpg-semantic"
    format = "json"
    epilog = "MPG semantic release bundle written."
    allow_parallel = False

    def init(self) -> None:
        previous = Path(self.outdir) / "publication.json"
        self.pages: dict[str, Any] = json.loads(previous.read_text()).get("pages", {}) if previous.exists() else {}

    def get_outdated_docs(self):
        return iter(())

    def get_target_uri(self, docname: str, typ: str | None = None) -> str:
        return f"{docname}/" if docname != self.config.root_doc else ""

    def prepare_writing(self, docnames) -> None:
        Path(self.outdir).mkdir(parents=True, exist_ok=True)

    def _number(self, node: nodes.Element, docname: str, kind: str) -> str | None:
        ids = node.get("ids", [])
        figures = self.env.toc_fignumbers.get(docname, {}).get(kind, {})
        for node_id in ids:
            if node_id in figures:
                return ".".join(str(part) for part in figures[node_id])
        return None

    def _serialize(self, node: nodes.Node, docname: str) -> dict[str, Any] | None:
        if isinstance(node, nodes.Text):
            return {"type": "text", "value": str(node)}

        common = {"ids": list(node.get("ids", [])), "classes": list(node.get("classes", []))} if isinstance(node, nodes.Element) else {}
        child_nodes = []
        for child in getattr(node, "children", []):
            converted = self._serialize(child, docname)
            if converted is not None:
                child_nodes.append(converted)

        if isinstance(node, nodes.document):
            return {"type": "document", "docname": docname, "children": child_nodes}
        if isinstance(node, MpgPart):
            return {"type": "part", "title": node["title"], "authors": node["authors"],
                    "letter": chr(ord("A") + node["part_number"] - 1),
                    "children": child_nodes}
        if isinstance(node, MpgTip):
            return {"type": "admonition", "kind": "tip", "title": node["title"],
                    **common, "children": child_nodes}
        if isinstance(node, nodes.section):
            return {"type": "section", **common, "children": child_nodes}
        if isinstance(node, nodes.title):
            if isinstance(node.parent, nodes.table):
                return {"type": "caption", "kind": "table", "children": child_nodes}
            parent = node.parent
            level = 1
            while parent is not None:
                if isinstance(parent, nodes.section):
                    level += 1
                parent = parent.parent
            section = node.parent if isinstance(node.parent, nodes.section) else None
            section_ids = section.get("ids", []) if section is not None else []
            key = "" if level == 2 else next((f"#{x}" for x in section_ids if f"#{x}" in self.env.toc_secnumbers.get(docname, {})), None)
            number_parts = self.env.toc_secnumbers.get(docname, {}).get(key) if key is not None else None
            number = ".".join(str(part) for part in number_parts) if number_parts else None
            return {"type": "title", **common, "level": min(level - 1, 6), "number": number, "children": child_nodes}
        if isinstance(node, nodes.paragraph):
            return {"type": "paragraph", **common, "children": child_nodes}
        if isinstance(node, nodes.literal):
            return {"type": "inlineCode", "value": _text(node), **common}
        if isinstance(node, nodes.emphasis):
            return {"type": "emphasis", "children": child_nodes}
        if isinstance(node, nodes.strong):
            return {"type": "strong", "children": child_nodes}
        if isinstance(node, nodes.inline):
            return {"type": "span", **common, "children": child_nodes}
        if isinstance(node, nodes.math_block):
            number = node.get("number")
            chapter = self.env.toc_secnumbers.get(docname, {}).get("", ())
            full_number = ".".join(str(part) for part in (*chapter, number)) if number and chapter else number
            return {"type": "equation", **common, "tex": node.astext(),
                    "label": node.get("label"), "number": str(full_number) if full_number else None}
        if isinstance(node, nodes.math):
            return {"type": "inlineMath", "tex": node.astext()}
        if isinstance(node, nodes.figure):
            return {"type": "figure", **common, "number": self._number(node, docname, "figure"), "children": child_nodes}
        if isinstance(node, nodes.image):
            return {"type": "image", "uri": node.get("uri"), "alt": node.get("alt", ""), "width": node.get("width")}
        if isinstance(node, nodes.caption):
            parent = node.parent
            kind = "figure" if isinstance(parent, nodes.figure) else "table" if isinstance(parent, nodes.table) else "code-block"
            return {"type": "caption", "kind": kind, "children": child_nodes}
        if isinstance(node, nodes.literal_block):
            parent = node.parent
            wrapper = parent if isinstance(parent, nodes.container) else node
            return {"type": "code", **common, "language": node.get("language", "text"),
                    "value": node.astext(), "number": self._number(wrapper, docname, "code-block")}
        if isinstance(node, nodes.container):
            return {"type": "container", **common, "number": self._number(node, docname, "code-block"), "children": child_nodes}
        if isinstance(node, nodes.compound):
            return {"type": "group", **common, "children": child_nodes}
        if isinstance(node, nodes.table):
            return {"type": "table", **common, "number": self._number(node, docname, "table"), "children": child_nodes}
        if isinstance(node, nodes.tgroup):
            return {"type": "tableGroup", "columns": node.get("cols"), "children": child_nodes}
        if isinstance(node, nodes.colspec):
            return None
        if isinstance(node, nodes.thead):
            return {"type": "tableHead", "children": child_nodes}
        if isinstance(node, nodes.tbody):
            return {"type": "tableBody", "children": child_nodes}
        if isinstance(node, nodes.row):
            return {"type": "tableRow", "children": child_nodes}
        if isinstance(node, nodes.entry):
            return {"type": "tableCell", "children": child_nodes}
        if isinstance(node, nodes.Admonition):
            return {"type": "admonition", "kind": node.tagname, **common, "children": child_nodes}
        if isinstance(node, addnodes.download_reference):
            return {"type": "download", "source": node.get("reftarget"),
                    "filename": node.get("filename"), "children": child_nodes}
        if isinstance(node, nodes.reference):
            result = {"type": "reference", "uri": node.get("refuri"), "anchor": node.get("refid"),
                      "children": child_nodes, **common}
            for key in ("api_symbol", "inventory_version"):
                if key in node:
                    result[key] = node[key]
            return result
        if isinstance(node, nodes.target):
            return {"type": "anchor", **common}
        if isinstance(node, nodes.citation):
            return {"type": "citation", **common, "children": child_nodes}
        if isinstance(node, nodes.label):
            return {"type": "citationLabel", "children": child_nodes}
        if isinstance(node, (nodes.bullet_list, nodes.enumerated_list)):
            return {"type": "list", "ordered": isinstance(node, nodes.enumerated_list), "children": child_nodes}
        if isinstance(node, nodes.list_item):
            return {"type": "listItem", "children": child_nodes}
        if isinstance(node, (addnodes.compact_paragraph, addnodes.pending_xref)):
            return {"type": "span", "children": child_nodes}
        if isinstance(node, addnodes.toctree):
            return None
        if isinstance(node, nodes.system_message):
            raise RuntimeError(f"system message reached semantic builder: {node.astext()}")
        raise RuntimeError(f"unsupported resolved doctree node: {node.__class__.__module__}.{node.__class__.__name__}")

    def write_doc(self, docname: str, doctree: nodes.document) -> None:
        if docname != self.config.root_doc:
            self.pages[docname] = self._serialize(doctree, docname)

    def finish(self) -> None:
        inventory = self.config.mpg_reference_inventory_data
        manifest = {
            "schema": 1,
            "publication": {"title": self.config.project, "release": self.config.release},
            "reference_inventory": {"gecode_version": inventory["gecode_version"], "base_url": inventory["base_url"]},
            "pages": self.pages,
        }
        (Path(self.outdir) / "publication.json").write_text(json.dumps(manifest, indent=2) + "\n")


def _load_inventory(app, config) -> None:
    path = Path(config.mpg_reference_inventory)
    data = json.loads(path.read_text())
    if data.get("schema_version") != 1 or not isinstance(data.get("objects"), dict):
        raise ValueError(f"unsupported Gecode reference inventory: {path}")
    config.mpg_reference_inventory_data = data


def setup(app):
    app.add_config_value("mpg_reference_inventory", "", "env", types={str})
    app.add_config_value("mpg_download_root", "", "env", types={str})
    app.connect("config-inited", _load_inventory)
    app.add_role("api", ApiRole())
    app.add_directive("mpg-part", MpgPartDirective)
    app.add_directive("mpg-tip", MpgTipDirective)
    app.add_node(MpgPart, latex=(visit_mpg_part_latex, depart_mpg_part_latex))
    app.add_node(MpgTip, latex=(visit_mpg_tip_latex, depart_mpg_tip_latex))
    app.add_builder(SemanticBuilder)
    return {"version": "0.1", "parallel_read_safe": True, "parallel_write_safe": False}
