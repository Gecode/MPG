"""Expose Sphinx sections as useful, ranked Pagefind sub-results."""

from __future__ import annotations

from docutils import nodes
from sphinx.writers.html5 import HTML5Translator

DEFINITION_PARENT_TITLES = {"Constraint overview"}
DEFINITION_WEIGHT = "10"
DEFINITION_CLASS = "mpg-search-definition"


def _direct_title(section: nodes.section) -> nodes.title | None:
    return next(
        (child for child in section.children if isinstance(child, nodes.title)),
        None,
    )


def _prepare_pagefind_sections(app, doctree: nodes.document, docname: str) -> None:
    """Move public fragments onto headings, where Pagefind can split results."""
    if app.builder.format != "html":
        return

    for section in doctree.findall(nodes.section):
        title = _direct_title(section)
        if title is None or not section.get("ids"):
            continue

        # Sphinx normally puts the readable fragment on ``section``. Pagefind
        # only creates sub-results from ids on h1-h6, so preserve the exact
        # public fragment while moving it to the section's heading.
        public_id = section["ids"][0]
        title["ids"].insert(0, public_id)
        section["mpg_search_heading_anchor"] = True

        parent = section.parent
        if isinstance(parent, nodes.section):
            parent_title = _direct_title(parent)
            if (parent_title is not None
                    and parent_title.astext() in DEFINITION_PARENT_TITLES):
                title["classes"].append(DEFINITION_CLASS)
                section["classes"].append(DEFINITION_CLASS)


class MpgSearchHTMLTranslator(HTML5Translator):
    """Add Pagefind weights to semantically authoritative headings."""

    def visit_section(self, node: nodes.Element) -> None:
        if not node.get("mpg_search_heading_anchor"):
            super().visit_section(node)
            return
        # Keep section ids in the doctree for Sphinx's numbering lookup, but
        # emit the public id only on the heading to avoid duplicate HTML ids.
        ids = node["ids"]
        node["ids"] = []
        try:
            super().visit_section(node)
        finally:
            node["ids"] = ids
        if len(ids) > 1:
            self.body[-1] += "".join(
                f'<span id="{self.encode(section_id)}"></span>'
                for section_id in ids[1:]
            )
        if DEFINITION_CLASS in node.get("classes", []):
            self.body[-1] = self.body[-1].replace(
                ">", f' data-pagefind-weight="{DEFINITION_WEIGHT}">', 1
            )

    def visit_title(self, node: nodes.Element) -> None:
        super().visit_title(node)
        if DEFINITION_CLASS not in node.get("classes", []):
            return
        for index in range(len(self.body) - 1, -1, -1):
            if self.body[index].startswith("<h"):
                self.body[index] = self.body[index].replace(
                    ">", f' data-pagefind-weight="{DEFINITION_WEIGHT}">', 1
                )
                break


def setup(app):
    app.connect("doctree-resolved", _prepare_pagefind_sections, priority=900)
    app.set_translator("html", MpgSearchHTMLTranslator, override=True)
    app.set_translator("dirhtml", MpgSearchHTMLTranslator, override=True)
    return {
        "version": "1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
