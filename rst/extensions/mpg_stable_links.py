"""Treat MPG page routes, explicit labels, and redirects as public APIs."""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
import re

from docutils import nodes
from sphinx.errors import ConfigError, ExtensionError

# Legacy MPG labels are public URLs and frequently use a colon hierarchy such
# as ``chap:m:started`` and ``fig:c:nonogram:ex``.  HTML permits colons in ids;
# preserving them exactly is safer than inventing a second naming scheme.
LABEL_RE = re.compile(r"^[a-z][a-z0-9_]*(?:[-.:][a-z0-9_]+)*$")


class MpgLegacyAlias(nodes.General, nodes.Element):
    """An exact historical fragment id alongside Sphinx's normalized id."""


def _visit_alias_html(translator, node: MpgLegacyAlias) -> None:
    translator.body.append(
        f'<span id="{translator.encode(node["alias"])}" class="mpg-anchor-alias"></span>'
    )
    raise nodes.SkipNode


def _skip_alias(translator, node: MpgLegacyAlias) -> None:
    raise nodes.SkipNode


def _load_redirects(app, config) -> None:
    path = Path(config.mpg_redirects_file)
    if not path.exists():
        config.mpg_redirects = {}
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != 1 or not isinstance(data.get("redirects"), dict):
        raise ConfigError(f"{path} must contain schema 1 and a redirects object")
    redirects = data["redirects"]
    for source, target in redirects.items():
        if not isinstance(source, str) or not isinstance(target, str):
            raise ConfigError(f"redirect keys and targets must be strings in {path}")
        if source.startswith(("/", "http:")) or ".." in PurePosixPath(source).parts:
            raise ConfigError(f"redirect source must be a release-relative URL: {source}")
        if target.startswith(("http:", "https:", "//")):
            raise ConfigError(f"redirect target must remain inside the release: {target}")
    config.mpg_redirects = redirects


def _validate_explicit_labels(app, doctree: nodes.document) -> None:
    if not app.config.mpg_require_explicit_section_labels:
        return
    docname = app.env.current_document.docname
    labels = app.env.domains.standard_domain.labels
    explicit = {
        label: label_id
        for label, (label_doc, label_id, _title) in labels.items()
        if label_doc == docname
    }
    explicit_ids = set(explicit.values())
    for section in doctree.findall(nodes.section):
        section_ids = set(section.get("ids", []))
        if not (section_ids & explicit_ids):
            title = next(iter(section.findall(nodes.title)), None)
            display = title.astext() if title is not None else "<untitled>"
            raise ExtensionError(
                f'{docname}: section "{display}" needs an explicit stable label '
                "(`.. _legacy:label:` immediately before its heading)"
            )
        for stable_label, stable_id in explicit.items():
            if stable_id not in section_ids:
                continue
            if not LABEL_RE.fullmatch(stable_label):
                raise ExtensionError(
                    f"{docname}: stable label {stable_label!r} must match {LABEL_RE.pattern}"
                )


def _prepare_legacy_aliases(app, env) -> None:
    labels = env.domains.standard_domain.labels
    aliases: dict[str, list[tuple[str, str]]] = {}
    reverse: dict[str, str] = {}
    for label, (docname, label_id, _title) in list(labels.items()):
        if ":" not in label or label == label_id:
            continue
        previous = reverse.setdefault(label_id, label)
        if previous != label:
            raise ExtensionError(
                f"legacy labels {previous!r} and {label!r} normalize to the same "
                f"Sphinx target {label_id!r}"
            )
        aliases.setdefault(docname, []).append((label, label_id))
        # Do not mutate the standard-domain target.  ``:numref:`` must resolve
        # the normalized id to the enumerable doctree node before public HTML
        # links are rewritten below.  Changing the label table here makes
        # Sphinx's number-reference resolver crash because no node has the
        # colon id.
    env.mpg_legacy_aliases = aliases


def _validate_redirect_targets(app, env) -> None:
    _prepare_legacy_aliases(app, env)
    labels = env.domains.standard_domain.labels
    docs = set(env.found_docs)
    for source, target in app.config.mpg_redirects.items():
        page, marker, anchor = target.partition("#")
        normalized_page = page.strip("/") or app.config.root_doc
        if normalized_page.endswith(".html"):
            normalized_page = normalized_page[:-5]
        if normalized_page.endswith("/index"):
            normalized_page = normalized_page[:-6]
        if normalized_page not in docs:
            raise ExtensionError(f"redirect {source!r} targets unknown page {target!r}")
        if marker and anchor not in labels:
            raise ExtensionError(f"redirect {source!r} targets unknown label {anchor!r}")


def _insert_legacy_aliases(app, doctree: nodes.document, docname: str) -> None:
    if app.builder.format != "html":
        return
    aliases = getattr(app.env, "mpg_legacy_aliases", {}).get(docname, [])
    elements = list(doctree.findall(nodes.Element))
    for alias, normalized_id in aliases:
        target = next((node for node in elements if normalized_id in node.get("ids", [])), None)
        if target is None or target.parent is None:
            raise ExtensionError(
                f"{docname}: cannot attach legacy alias {alias!r} to {normalized_id!r}"
            )
        index = target.parent.index(target)
        target.parent.insert(index, MpgLegacyAlias(alias=alias))

    # Reference resolution is complete at this event.  Keep Sphinx's internal
    # normalized ids for numbering and LaTeX, but make every emitted HTML link
    # advertise the exact historical fragment.  Local references use
    # ``refid``; cross-document references use a ``refuri`` fragment.
    normalized_to_alias = {
        normalized_id: alias
        for page_aliases in getattr(app.env, "mpg_legacy_aliases", {}).values()
        for alias, normalized_id in page_aliases
    }
    for reference in doctree.findall(nodes.reference):
        refid = reference.get("refid")
        if refid in normalized_to_alias:
            reference["refid"] = normalized_to_alias[refid]
        refuri = reference.get("refuri")
        if not refuri or "#" not in refuri:
            continue
        page, marker, fragment = refuri.rpartition("#")
        if fragment in normalized_to_alias:
            reference["refuri"] = page + marker + normalized_to_alias[fragment]


def _write_redirect_manifest(app, exception) -> None:
    if exception is not None or app.builder.format != "html":
        return
    output = {
        "schema": 1,
        "release": app.config.release,
        "redirects": app.config.mpg_redirects,
    }
    destination = Path(app.outdir) / "redirects.json"
    destination.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def setup(app):
    app.add_config_value("mpg_require_explicit_section_labels", True, "env", types={bool})
    app.add_config_value("mpg_redirects_file", "", "env", types={str})
    app.add_config_value("mpg_redirects", {}, "env", types={dict})
    app.connect("config-inited", _load_redirects)
    app.connect("doctree-read", _validate_explicit_labels)
    app.connect("env-updated", _validate_redirect_targets)
    app.connect("doctree-resolved", _insert_legacy_aliases)
    app.connect("build-finished", _write_redirect_manifest)
    app.add_node(
        MpgLegacyAlias,
        html=(_visit_alias_html, None),
        latex=(_skip_alias, None),
    )
    return {
        "version": "1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
