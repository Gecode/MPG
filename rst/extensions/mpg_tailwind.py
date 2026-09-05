"""Attach Tailwind utilities to ordinary Sphinx document structures."""

from __future__ import annotations

from docutils import nodes


HEADING_CLASSES = {
    1: (
        "mt-0", "mb-6", "pe-28", "max-compact:pe-20",
        "font-mpg-sans", "text-[clamp(1.9rem,2.7vw,2.35rem)]",
        "max-compact:text-[1.85rem]", "leading-tight", "font-bold",
        "tracking-[-0.018em]", "text-mpg-ink", "text-balance",
    ),
    2: (
        "mt-12", "mb-4", "pt-1", "font-mpg-sans", "text-[1.4rem]",
        "leading-tight", "font-bold", "tracking-[-0.008em]",
        "text-mpg-ink", "text-balance",
    ),
    3: (
        "mt-8", "mb-3", "font-mpg-sans", "text-lg", "leading-tight",
        "font-bold", "text-mpg-ink", "text-balance",
    ),
    4: (
        "mt-6", "mb-2", "font-mpg-sans", "text-base", "leading-tight",
        "font-bold", "text-mpg-ink", "text-balance",
    ),
}

FRONT_PAGE_HEADING_CLASSES = (
    "mt-0", "mb-8", "pe-40", "xl:pe-48", "2xl:pe-56",
    "max-compact:pe-24",
    "font-mpg-sans", "text-[clamp(2.6rem,5vw,4rem)]",
    "max-compact:text-[2.25rem]", "leading-[1.08]", "font-bold",
    "tracking-[-0.025em]", "text-mpg-ink", "text-balance",
)

PERMALINK_CLASSES = (
    "[&_.headerlink]:opacity-0",
    "[&_.headerlink]:transition-opacity",
    "hover:[&_.headerlink]:opacity-100",
    "focus-within:[&_.headerlink]:opacity-100",
    "motion-reduce:[&_.headerlink]:transition-none",
)


def _add_classes(node: nodes.Element, classes: tuple[str, ...]) -> None:
    existing = node.setdefault("classes", [])
    for class_name in classes:
        if class_name not in existing:
            existing.append(class_name)


def _section_depth(section: nodes.section) -> int:
    depth = 1
    parent = section.parent
    while parent is not None:
        if isinstance(parent, nodes.section):
            depth += 1
        parent = parent.parent
    return depth


def _inside_special_structure(node: nodes.Node) -> bool:
    """Leave bespoke directives and dense structures to their component CSS."""
    parent = node.parent
    while parent is not None:
        if isinstance(parent, (nodes.Admonition, nodes.figure, nodes.table)):
            return True
        # Part openings contain ordinary prose and lists. Only their title
        # banner has bespoke styling; the blurb needs the usual reading rhythm.
        if type(parent).__name__ in {"MpgTip", "MpgFigure"}:
            return True
        parent = parent.parent
    return False


def _style_html_doctree(app, doctree: nodes.document, docname: str) -> None:
    """Add static utilities late enough to include prior semantic transforms."""
    if app.builder.format != "html":
        return

    for section in doctree.findall(nodes.section):
        title = next(
            (child for child in section.children if isinstance(child, nodes.title)),
            None,
        )
        if title is not None:
            depth = min(_section_depth(section), max(HEADING_CLASSES))
            classes = (
                FRONT_PAGE_HEADING_CLASSES
                if docname == app.config.root_doc and depth == 1
                else HEADING_CLASSES[depth]
            )
            _add_classes(title, classes)

    for paragraph in doctree.findall(nodes.paragraph):
        if _inside_special_structure(paragraph):
            continue
        if isinstance(paragraph.parent, (nodes.definition, nodes.list_item)):
            _add_classes(paragraph, ("mb-4", "last:mb-0", "text-pretty"))
        else:
            _add_classes(paragraph, ("mb-4", "text-pretty"))

    for item_list in (*doctree.findall(nodes.bullet_list),
                      *doctree.findall(nodes.enumerated_list)):
        if _inside_special_structure(item_list):
            continue
        if isinstance(item_list.parent, nodes.list_item):
            _add_classes(item_list, ("my-2", "ps-6", "max-compact:ps-5"))
        else:
            _add_classes(item_list, ("mb-4", "ps-6", "max-compact:ps-5"))
        if isinstance(item_list, nodes.bullet_list):
            _add_classes(item_list, ("list-disc",))

    for item in doctree.findall(nodes.list_item):
        if not _inside_special_structure(item):
            _add_classes(item, ("ps-0.5", "[&+li]:mt-1.5"))

    for definition_list in doctree.findall(nodes.definition_list):
        if not _inside_special_structure(definition_list):
            _add_classes(definition_list, ("mt-5", "mb-6"))
    for term in doctree.findall(nodes.term):
        if not _inside_special_structure(term):
            _add_classes(term, ("mt-3", "first:mt-0", "font-bold"))
    for definition in doctree.findall(nodes.definition):
        if not _inside_special_structure(definition):
            _add_classes(definition, ("ms-5", "mt-1", "max-compact:ms-4"))

    for quote in doctree.findall(nodes.block_quote):
        if not _inside_special_structure(quote):
            _add_classes(quote, ("mb-4",))

    for figure in doctree.findall(nodes.figure):
        if any(isinstance(child, nodes.caption) for child in figure.children):
            _add_classes(figure, PERMALINK_CLASSES)

    for table in doctree.findall(nodes.table):
        if any(isinstance(child, nodes.title) for child in table.children):
            _add_classes(table, PERMALINK_CLASSES)

    for equation in doctree.findall(nodes.math_block):
        if equation.get("number") or equation.get("label"):
            _add_classes(equation, PERMALINK_CLASSES)

    # MpgTip is a custom admonition node, so avoid importing the semantic
    # extension solely for a styling check.
    for admonition in doctree.findall(nodes.Admonition):
        if type(admonition).__name__ == "MpgTip":
            _add_classes(admonition, PERMALINK_CLASSES)

    for container in doctree.findall(nodes.container):
        if (container.get("literal_block")
                and any(isinstance(child, nodes.caption) for child in container.children)):
            _add_classes(container, PERMALINK_CLASSES)


def setup(app):
    app.connect("doctree-resolved", _style_html_doctree, priority=950)
    return {
        "version": "1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
