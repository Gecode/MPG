"""Treat MPG page routes, explicit labels, and redirects as public APIs."""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
import re

from docutils import nodes
from sphinx.errors import ConfigError, ExtensionError

# MPG source labels frequently use a LaTeX-oriented colon hierarchy such as
# ``chap:m:started`` and ``fig:c:nonogram:ex``. They remain internal identifiers
# for cross-references and PDF numbering. Public HTML exposes readable slugs only.
LABEL_RE = re.compile(r"^[a-z][a-z0-9_]*(?:[-.:][a-z0-9_]+)*$")


class MpgWebAnchor(nodes.General, nodes.Element):
    """A readable public fragment for a target with an internal source label."""


def _visit_web_anchor_html(translator, node: MpgWebAnchor) -> None:
    translator.body.append(
        f'<span id="{translator.encode(node["fragment"])}" class="mpg-web-anchor"></span>'
    )
    raise nodes.SkipNode


def _skip_web_anchor(translator, node: MpgWebAnchor) -> None:
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
                "(`.. _label:` immediately before its heading)"
            )
        for stable_label, stable_id in explicit.items():
            if stable_id not in section_ids:
                continue
            if not LABEL_RE.fullmatch(stable_label):
                raise ExtensionError(
                    f"{docname}: stable label {stable_label!r} must match {LABEL_RE.pattern}"
                )


def _prepare_web_fragments(app, env) -> None:
    labels = env.domains.standard_domain.labels
    source_targets: dict[str, list[tuple[str, str]]] = {}
    reverse: dict[str, str] = {}
    for label, (docname, label_id, _title) in list(labels.items()):
        if ":" not in label or label == label_id:
            continue
        previous = reverse.setdefault(label_id, label)
        if previous != label:
            raise ExtensionError(
                f"source labels {previous!r} and {label!r} normalize to the same "
                f"Sphinx target {label_id!r}"
            )
        source_targets.setdefault(docname, []).append((label, label_id))
        # Do not mutate the standard-domain target.  ``:numref:`` must resolve
        # the normalized id to the enumerable doctree node before public HTML
        # links are rewritten below.  Changing the label table here makes
        # Sphinx's number-reference resolver crash because no node has the
        # colon id.
    env.mpg_source_targets = source_targets
    web_fragments: dict[str, str] = {}
    if app.builder.format != "html":
        env.mpg_web_fragments = web_fragments
        return
    for target_doc, page_targets in source_targets.items():
        if target_doc not in env.found_docs:
            continue
        doctree = env.get_doctree(target_doc)
        elements = list(doctree.findall(nodes.Element))
        claimed = {
            target_id
            for element in elements
            for target_id in element.get("ids", [])
        }
        generated: set[str] = set()
        for source_label, normalized_id in page_targets:
            target = next(
                (node for node in elements if normalized_id in node.get("ids", [])),
                None,
            )
            if target is None:
                raise ExtensionError(
                    f"{target_doc}: cannot find web target {normalized_id!r}"
                )
            section = target if isinstance(target, nodes.section) else target.parent
            if (source_label.startswith(("chap:", "sec:", "part:"))
                    and isinstance(section, nodes.section) and section.get("ids")):
                web_fragments[normalized_id] = section["ids"][0]
            elif isinstance(target, nodes.rubric):
                base = nodes.make_id(target.astext()) or normalized_id
                candidate = base
                suffix = 2
                while candidate in claimed or candidate in generated:
                    candidate = f"{base}-{suffix}"
                    suffix += 1
                generated.add(candidate)
                web_fragments[normalized_id] = candidate
            elif isinstance(target, nodes.target) and target.parent is not None:
                siblings = target.parent.children
                index = siblings.index(target)
                following = siblings[index + 1] if index + 1 < len(siblings) else None
                if isinstance(following, nodes.rubric):
                    base = nodes.make_id(following.astext())
                else:
                    base = nodes.make_id(source_label.rsplit(":", 1)[-1])
                candidate = base or normalized_id
                suffix = 2
                while candidate in claimed or candidate in generated:
                    candidate = f"{base}-{suffix}"
                    suffix += 1
                generated.add(candidate)
                web_fragments[normalized_id] = candidate
            else:
                web_fragments[normalized_id] = normalized_id
    env.mpg_web_fragments = web_fragments


def _validate_redirect_targets(app, env) -> None:
    _prepare_web_fragments(app, env)
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


def _publish_web_fragments(app, doctree: nodes.document, docname: str) -> None:
    if app.builder.format != "html":
        return
    source_targets = getattr(app.env, "mpg_source_targets", {}).get(docname, [])
    elements = list(doctree.findall(nodes.Element))
    normalized_to_canonical = dict(getattr(app.env, "mpg_web_fragments", {}))
    for source_label, normalized_id in source_targets:
        target = next((node for node in elements if normalized_id in node.get("ids", [])), None)
        if target is None or target.parent is None:
            raise ExtensionError(
                f"{docname}: cannot publish source target {source_label!r} as {normalized_id!r}"
            )
        canonical = normalized_to_canonical.get(normalized_id, normalized_id)
        canonical_exists = any(canonical in node.get("ids", []) for node in elements)
        index = target.parent.index(target)
        if not canonical_exists:
            target.parent.insert(index, MpgWebAnchor(fragment=canonical))

    # Reference resolution is complete at this event.  Keep Sphinx's internal
    # ids for numbering and LaTeX, and point emitted HTML at human-readable
    # public fragments.
    for reference in doctree.findall(nodes.reference):
        refid = reference.get("refid")
        if refid in normalized_to_canonical:
            reference["refid"] = normalized_to_canonical[refid]
        refuri = reference.get("refuri")
        if not refuri or "#" not in refuri:
            continue
        page, marker, fragment = refuri.rpartition("#")
        if fragment in normalized_to_canonical:
            reference["refuri"] = page + marker + normalized_to_canonical[fragment]


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
    app.connect("doctree-resolved", _publish_web_fragments)
    app.connect("build-finished", _write_redirect_manifest)
    app.add_node(
        MpgWebAnchor,
        html=(_visit_web_anchor_html, None),
        latex=(_skip_web_anchor, None),
    )
    return {
        "version": "1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
