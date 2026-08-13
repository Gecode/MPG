"""Authoring semantics shared by MPG's HTML and classical PDF editions."""

from __future__ import annotations

import json
from pathlib import Path

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx.errors import ExtensionError
from sphinx.roles import SphinxRole
from sphinx.util import logging
from sphinx.util.nodes import split_explicit_title

LOGGER = logging.getLogger(__name__)


class MpgPart(nodes.General, nodes.Element):
    """A mnemonic MPG part opening and its introductory blurb."""


class MpgTip(nodes.Admonition, nodes.Element):
    """A numbered, referenceable modeling/programming tip."""


class MpgFigure(nodes.figure):
    """A captioned figure whose body may contain arbitrary reST content."""


class MpgCaption(nodes.caption):
    """A figure caption with an optional, deliberately short list title."""


class MpgPartDirective(Directive):
    required_arguments = 1
    final_argument_whitespace = True
    has_content = True
    option_spec = {
        "authors": directives.unchanged_required,
        "letter": directives.unchanged_required,
        "name": directives.unchanged,
        "class": directives.class_option,
    }

    def run(self) -> list[nodes.Node]:
        letter = self.options.get("letter", "")
        if len(letter) != 1 or not letter.isascii() or not letter.isalpha():
            raise self.error(":letter: must be one ASCII letter")
        node = MpgPart()
        node["title"] = self.arguments[0]
        node["authors"] = self.options.get("authors", "")
        node["letter"] = letter.upper()
        node["part_number"] = ord(letter.upper()) - ord("A") + 1
        node["classes"].extend(self.options.get("class", []))
        self.add_name(node)
        self.state.nested_parse(self.content, self.content_offset, node)
        # An include used as the directive body can retain a synthetic
        # block_quote around the entire blurb.  It is not authorial quotation
        # and narrows the classical part page by several ems.
        if len(node) == 1 and isinstance(node[0], nodes.block_quote):
            quote = node[0]
            node.children = quote.children
            for child in node.children:
                child.parent = node
        return [node]


class MpgTipDirective(Directive):
    required_arguments = 1
    final_argument_whitespace = True
    has_content = True
    option_spec = {
        "name": directives.unchanged,
        "class": directives.class_option,
    }

    def run(self) -> list[nodes.Node]:
        node = MpgTip()
        node["title"] = self.arguments[0]
        env = getattr(self.state.document.settings, "env", None)
        if env is not None:
            # LaTeX assembles a single doctree and discards per-node source
            # paths.  Preserve ownership explicitly so repeated automatic
            # ids can still be matched to Sphinx's chapter-scoped numbering.
            node["docname"] = env.docname
        node["classes"].extend(self.options.get("class", []))
        inline, messages = self.state.inline_text(node["title"], self.lineno)
        node["title"] = "".join(part.astext() for part in inline)
        self.add_name(node)
        self.state.nested_parse(self.content, self.content_offset, node)
        return [node, *messages]


class MpgFigureDirective(Directive):
    required_arguments = 1
    final_argument_whitespace = True
    has_content = True
    option_spec = {
        "name": directives.unchanged_required,
        "short-caption": directives.unchanged,
        "class": directives.class_option,
    }

    def run(self) -> list[nodes.Node]:
        if "name" not in self.options:
            raise self.error(":name: is required for stable figure linking")
        node = MpgFigure()
        node["classes"].extend(("mpg-content-figure", *self.options.get("class", [])))
        self.add_name(node)
        self.state.nested_parse(self.content, self.content_offset, node)
        caption_text = self.arguments[0]
        caption = MpgCaption(caption_text, "")
        caption["short_caption"] = self.options.get("short-caption", "")
        caption.extend(self.state.inline_text(caption_text, self.lineno)[0])
        node += caption
        return [node]


def visit_mpg_caption_html(translator, node: MpgCaption) -> None:
    translator.visit_caption(node)


def depart_mpg_caption_html(translator, node: MpgCaption) -> None:
    translator.depart_caption(node)


def visit_mpg_caption_latex(translator, node: MpgCaption) -> None:
    """Emit LaTeX's optional caption only when the author supplied one.

    The full caption remains visible and is still exposed to HTML.  The short
    form affects only the list of figures, matching the original MPG source's
    ``\\caption[short]{full}`` distinction.
    """
    translator.in_caption += 1
    short_caption = node.get("short_caption", "")
    if short_caption:
        translator.body.append(r"\caption[" + translator.encode(short_caption) + "]{")
    else:
        translator.body.append(r"\caption{")


def depart_mpg_caption_latex(translator, node: MpgCaption) -> None:
    translator.depart_caption(node)


def visit_mpg_part_html(translator, node: MpgPart) -> None:
    translator.body.append(translator.starttag(node, "section", CLASS="mpg-part-opening"))
    translator.body.append(
        '<div class="mpg-part-heading">'
        f'<span class="mpg-part-letter" aria-label="Part {node["letter"]}">'
        f'{translator.encode(node["letter"])}</span>'
        '<div class="mpg-part-titles">'
        f'<p class="mpg-part-kind">Part {translator.encode(node["letter"])}</p>'
        f'<h1>{translator.encode(node["title"])}</h1>'
        f'<p class="mpg-part-authors">{translator.encode(node["authors"])}</p>'
        "</div></div><div class=\"mpg-part-blurb\">"
    )


def depart_mpg_part_html(translator, node: MpgPart) -> None:
    translator.body.append("</div></section>")


def visit_mpg_tip_html(translator, node: MpgTip) -> None:
    number = node.get("number", "")
    label = f"Tip {number}" if number else "Tip"
    title = translator.encode(node["title"])
    translator.body.append(translator.starttag(node, "aside", CLASS="mpg-tip", role="note"))
    translator.body.append(
        f'<p class="mpg-tip-title"><span>{label}</span>'
        f' <span class="mpg-tip-subject">({title}).</span></p>'
        '<div class="mpg-tip-body"> '
    )


def depart_mpg_tip_html(translator, node: MpgTip) -> None:
    translator.body.append(
        '</div><span class="mpg-tip-end" aria-hidden="true">&#9668;</span></aside>'
    )


def visit_mpg_part_latex(translator, node: MpgPart) -> None:
    node["latex_title"] = translator.encode(node["title"])
    for target_id in node.get("ids", []):
        translator.body.append(translator.hypertarget(target_id) + "\n")
    translator.body.append(
        f'\\MPGSetPartAuthors{{{translator.encode(node["authors"])}}}\n'
        "\\MPGSetPartBlurb{%\n"
    )


def depart_mpg_part_latex(translator, node: MpgPart) -> None:
    translator.body.append(
        f'}}\n\\MPGPartNumber{{{node["part_number"]}}}{{{node["latex_title"]}}}\n'
    )


def visit_mpg_tip_latex(translator, node: MpgTip) -> None:
    # Custom LaTeX visitors must emit their own hypertargets.  The standard
    # admonition/figure visitors normally do this on our behalf, but MPGTip is
    # a bespoke environment.  Without these labels, perfectly valid ``:ref:``
    # links to tips remain undefined in the generated PDF.
    for target_id in node.get("ids", []):
        translator.body.append(translator.hypertarget(target_id) + "\n")
    translator.body.append(
        f'\\begin{{MPGTip}}{{{node.get("number", "")}}}'
        f'{{{translator.encode(node["title"])}}}\n'
    )


def depart_mpg_tip_latex(translator, node: MpgTip) -> None:
    translator.body.append("\\end{MPGTip}\n")


def _assign_tip_numbers(app, doctree: nodes.document, docname: str) -> None:
    for node in doctree.findall(MpgTip):
        source_doc = node.get("docname")
        if source_doc is None:
            source_doc = app.env.path2doc(node.source) if node.source else None
        target_ids = list(node.get("ids", []))
        if source_doc is None:
            # A merged LaTeX doctree drops ``node.source`` but retains the
            # normalized public label id.  Use Sphinx's label registry to
            # recover the owning document before consulting its figure
            # numbers.  This also disambiguates repeated automatic ids such
            # as ``id12`` across chapters.
            label_docs = {
                label_doc
                for label_doc, label_id, _title
                in app.env.domaindata.get("std", {}).get("labels", {}).values()
                if label_id in target_ids
            }
            if len(label_docs) == 1:
                source_doc = next(iter(label_docs))
        source_doc = source_doc or docname
        numbers = app.env.toc_fignumbers.get(source_doc, {}).get("tip", {})
        latex_prefix = source_doc + ":"
        target_ids += [target_id.removeprefix(latex_prefix) for target_id in target_ids]
        number = next((numbers[target_id] for target_id in target_ids
                       if target_id in numbers), None)
        if number is None:
            # The LaTeX builder merges all documents into the root doctree and
            # prefixes each enumerable id with its source docname.  Node source
            # paths point at the temporary publication staging tree, so
            # ``path2doc`` cannot always recover that docname here.
            matches = []
            for candidate_doc, figure_types in app.env.toc_fignumbers.items():
                for target_id, candidate_number in figure_types.get("tip", {}).items():
                    qualified_id = f"{candidate_doc}:{target_id}"
                    if any(
                        actual_id == target_id
                        or actual_id == qualified_id
                        or actual_id.endswith(f":{qualified_id}")
                        for actual_id in target_ids
                    ):
                        matches.append((candidate_doc, target_id, candidate_number))
            unique_matches = {
                (candidate_doc, target_id, tuple(candidate_number))
                for candidate_doc, target_id, candidate_number in matches
            }
            if len(unique_matches) == 1:
                number = next(iter(unique_matches))[2]
        if number is None:
            raise ExtensionError(
                f"{docname}: semantic tip has no Sphinx enumerable number; "
                f"source={node.source!r}, ids={node.get('ids', [])!r}, "
                f"title={node.get('title', '')!r}; give it a stable :name:"
            )
        node["number"] = ".".join(str(value) for value in number)


def _restore_typed_reference_text(app, doctree: nodes.document, docname: str) -> None:
    """Restore the visible vocabulary of MPG's legacy ``autoref`` links."""

    labels = app.env.domaindata.get("std", {}).get("labels", {})
    label_by_id = {
        target_id: (label, target_doc, title)
        for label, (target_doc, target_id, title) in labels.items()
        if label.startswith(("chap:", "sec:", "part:", "tip:"))
    }
    sections_by_id: dict[str, nodes.section] = {}
    tips_by_id: dict[str, MpgTip] = {}
    for section in doctree.findall(nodes.section):
        for target_id in section.get("ids", []):
            sections_by_id[target_id] = section
    for tip in doctree.findall(MpgTip):
        for target_id in tip.get("ids", []):
            tips_by_id[target_id] = tip

    def section_number(label: str, target_doc: str, target_id: str) -> str:
        section = sections_by_id.get(target_id)
        if label.startswith("chap:"):
            toc_id = ""
        elif section is not None and section.get("ids"):
            toc_id = "#" + section["ids"][0]
        else:
            toc_id = "#" + target_id
        number = app.env.toc_secnumbers.get(target_doc, {}).get(toc_id)
        return ".".join(str(value) for value in number) if number else ""

    for reference in doctree.findall(nodes.reference):
        target_id = reference.get("refid")
        if not target_id:
            refuri = reference.get("refuri", "")
            if "#" in refuri:
                target_id = refuri.rsplit("#", 1)[1]
        info = label_by_id.get(target_id)
        if info is None:
            continue
        label, target_doc, title = info
        if label.startswith("part:"):
            text = f"Part {label.split(':', 1)[1].upper()}"
        elif label.startswith("chap:"):
            number = section_number(label, target_doc, target_id)
            text = f"Chapter {number} ({title})" if number else title
        elif label.startswith("sec:"):
            number = section_number(label, target_doc, target_id)
            text = f"Section {number}" if number else title
        else:
            tip = tips_by_id.get(target_id)
            number = tip.get("number", "") if tip is not None else ""
            text = f"Tip {number}" if number else title
        reference.children = [nodes.Text(text)]


def _start_unnumbered_backmatter(app, doctree: nodes.document, docname: str) -> None:
    """Make Bibliography, Changelog, and License classical backmatter."""

    if app.builder.name == "latex" and docname == "backmatter/bibliography":
        doctree.insert(
            0,
            nodes.raw("", r"\setcounter{secnumdepth}{-1}", format="latex"),
        )


def _route_latex_part_labels(app, env) -> None:
    """Point part references at the part nodes included in the PDF doctree.

    The standalone ``parts/*`` pages own the public HTML labels, but are not
    members of the book toctree.  LaTeX therefore needs the same semantic
    labels routed to the local part opener rather than an orphan web page.
    """

    if app.builder.name != "latex":
        return
    destinations = {
        "m": ("modeling/started", "Modeling"),
        "c": ("case-studies/golomb", "Case studies"),
        "p": ("propagators/started", "Programming propagators"),
        "b": ("branchers/started", "Programming branchers"),
        "v": ("variables/index", "Programming variables"),
        "s": ("search-engines/started", "Programming search engines"),
    }
    standard = env.domaindata.get("std", {})
    labels = standard.get("labels", {})
    anonlabels = standard.get("anonlabels", {})
    for letter, (target_doc, title) in destinations.items():
        label = f"part:{letter}"
        target_id = f"pdf-part-{letter}"
        labels[label] = (target_doc, target_id, title)
        anonlabels[label] = (target_doc, target_id)


def _use_pdf_figure_derivatives(app, doctree: nodes.document) -> None:
    """Use maintained vector PDF derivatives in the LaTeX edition.

    HTML keeps the canonical SVG URI.  Asking Sphinx's generic image
    converter to rediscover the PDF at publication time is both slower and
    less reproducible than selecting the checked derivative maintained beside
    the SVG source.
    """
    if getattr(app.builder, "format", "") != "latex":
        return
    figure_root = Path(app.confdir) / "figures"
    for image in doctree.findall(nodes.image):
        uri = image.get("uri", "")
        if not uri.endswith(".svg"):
            continue
        name = Path(uri).name
        derivative = figure_root / "pdf" / f"{Path(name).stem}.pdf"
        if derivative.is_file():
            image["uri"] = f"/figures/pdf/{derivative.name}"


class ApiRole(SphinxRole):
    """Resolve a Gecode symbol against the release's frozen API inventory."""

    def run(self):
        inventory = getattr(self.env.app.config, "mpg_reference_inventory_data", None)
        explicit, title, target = split_explicit_title(self.text)
        if not explicit:
            title = target
        if inventory is None:
            LOGGER.warning(
                "API inventory is not configured; cannot resolve %s",
                target,
                location=(self.env.docname, self.lineno),
                type="mpg",
                subtype="api",
            )
            return [nodes.literal(target, title)], []
        item = inventory["objects"].get(target)
        if item is None:
            LOGGER.warning(
                "API symbol %s is absent from imported Gecode inventory",
                target,
                location=(self.env.docname, self.lineno),
                type="mpg",
                subtype="api",
            )
            return [nodes.literal(target, title)], []
        ref = nodes.reference(title, title, refuri=inventory["base_url"] + item["url"])
        ref["classes"].append("api-symbol")
        return [ref], []


def _load_inventory(app, config) -> None:
    if not config.mpg_reference_inventory:
        config.mpg_reference_inventory_data = None
        return
    path = Path(config.mpg_reference_inventory)
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or not isinstance(data.get("objects"), dict):
        raise ValueError(f"unsupported Gecode reference inventory: {path}")
    configured_release = app.config.release
    inventory_release = data.get("gecode_version")
    if configured_release != "development" and inventory_release != configured_release:
        raise ValueError(
            f"Gecode reference inventory is for {inventory_release}, "
            f"but this release is {configured_release}"
        )
    config.mpg_reference_inventory_data = data


def setup(app):
    app.add_config_value("mpg_reference_inventory", "", "env", types={str})
    app.add_config_value("mpg_download_root", "", "env", types={str})
    app.connect("config-inited", _load_inventory)
    # Run before Sphinx's image collector normalizes source-relative paths and
    # records the files that must be copied into the LaTeX output directory.
    app.connect("doctree-read", _use_pdf_figure_derivatives, priority=100)
    app.connect("env-updated", _route_latex_part_labels)
    app.connect("doctree-resolved", _assign_tip_numbers, priority=500)
    app.connect("doctree-resolved", _restore_typed_reference_text, priority=800)
    app.connect("doctree-resolved", _start_unnumbered_backmatter, priority=900)
    app.add_role("api", ApiRole())
    app.add_directive("mpg-part", MpgPartDirective)
    app.add_directive("mpg-tip", MpgTipDirective)
    app.add_directive("mpg-figure", MpgFigureDirective)
    app.add_node(
        MpgPart,
        html=(visit_mpg_part_html, depart_mpg_part_html),
        latex=(visit_mpg_part_latex, depart_mpg_part_latex),
    )
    app.add_enumerable_node(
        MpgTip,
        "tip",
        title_getter=lambda node: node["title"],
        html=(visit_mpg_tip_html, depart_mpg_tip_html),
        latex=(visit_mpg_tip_latex, depart_mpg_tip_latex),
    )
    app.add_enumerable_node(
        MpgFigure,
        "figure",
        html=(lambda translator, node: translator.visit_figure(node),
              lambda translator, node: translator.depart_figure(node)),
        latex=(lambda translator, node: translator.visit_figure(node),
               lambda translator, node: translator.depart_figure(node)),
    )
    app.add_node(
        MpgCaption,
        html=(visit_mpg_caption_html, depart_mpg_caption_html),
        latex=(visit_mpg_caption_latex, depart_mpg_caption_latex),
    )
    return {
        "version": "1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
