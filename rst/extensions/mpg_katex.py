"""Compatibility fixes for the KaTeX Sphinx renderer.

``sphinxcontrib-katex`` escapes inline TeX before placing it in HTML, but does
not do the same for display TeX.  A literal ``<`` in a display equation is
therefore parsed as the start of an HTML tag before KaTeX's auto-renderer can
see it.  Patch the visitor before the upstream extension registers it.
"""

from __future__ import annotations

from docutils import nodes
from sphinx.locale import _
import sphinxcontrib.katex as katex


def _html_visit_displaymath(self, node):
    self.body.append(self.starttag(node, "div", CLASS="math"))

    if node["number"]:
        number = katex.get_node_equation_number(self, node)
        self.body.append(f'<span class="eqno">({number})')
        self.add_permalink_ref(node, _("Permalink to this equation"))
        self.body.append("</span>")

    latex = katex.get_latex(node)
    if self.builder.config.katex_prerender:
        self.body.append(katex.render_latex(latex, {"displayMode": True}))
        self.body.append("</div>")
    elif node["nowrap"]:
        self.body.append(self.encode(latex))
        self.body.append("</div>")
    else:
        self.body.append(self.builder.config.katex_display[0])
        self.body.append(self.encode(latex))
        self.body.append(self.builder.config.katex_display[1])
        self.body.append("</div>\n")

    raise nodes.SkipNode


def setup(app):
    katex.html_visit_displaymath = _html_visit_displaymath
    return {
        "version": "1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
