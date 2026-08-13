#!/usr/bin/env python3
"""Dependency-free semantic checker for the MPG content-model prototype."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ID_RE = re.compile(r"^[a-z][a-z0-9]*(?:[._:/-][a-z0-9]+)*$")
RUN_MODES = {"run", "test-harness", "expected-failure"}
HELP_ARGS = {"-help", "--help", "-?"}


def _need(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def _objects(document: dict[str, Any], key: str, errors: list[str]) -> list[dict[str, Any]]:
    value = document.get(key)
    if not isinstance(value, list):
        errors.append(f"{key}: expected an array")
        return []
    result = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            errors.append(f"{key}[{index}]: expected an object")
        else:
            result.append(item)
    return result


def validate(document: dict[str, Any], *, source: Path | None = None, check_paths: bool = False) -> list[str]:
    """Return all structural and cross-reference errors in *document*."""
    errors: list[str] = []
    _need(document.get("model_version") == "0.1", "model_version: expected '0.1'", errors)

    publication = document.get("publication")
    if not isinstance(publication, dict):
        errors.append("publication: expected an object")
        publication = {}

    pages = _objects(document, "pages", errors)
    artifacts = _objects(document, "code_artifacts", errors)
    profiles = _objects(document, "validation_profiles", errors)
    figures = _objects(document, "figure_assets", errors)

    global_ids: dict[str, str] = {}

    def register(value: Any, location: str) -> None:
        if not isinstance(value, str) or not ID_RE.fullmatch(value):
            errors.append(f"{location}: invalid stable ID {value!r}")
            return
        if value in global_ids:
            errors.append(f"{location}: duplicate stable ID {value!r}; first declared at {global_ids[value]}")
        else:
            global_ids[value] = location

    register(publication.get("id"), "publication.id")
    for pi, part in enumerate(publication.get("navigation", [])):
        if isinstance(part, dict):
            register(part.get("id"), f"publication.navigation[{pi}].id")
    for i, page in enumerate(pages):
        register(page.get("id"), f"pages[{i}].id")
        for j, block in enumerate(page.get("blocks", [])):
            if isinstance(block, dict) and block.get("type") in {"heading", "code_projection"}:
                register(block.get("id"), f"pages[{i}].blocks[{j}].id")
    for i, artifact in enumerate(artifacts):
        register(artifact.get("id"), f"code_artifacts[{i}].id")
    for i, profile in enumerate(profiles):
        register(profile.get("id"), f"validation_profiles[{i}].id")
    for i, figure in enumerate(figures):
        register(figure.get("id"), f"figure_assets[{i}].id")

    page_by_id = {x.get("id"): x for x in pages if isinstance(x.get("id"), str)}
    artifact_by_id = {x.get("id"): x for x in artifacts if isinstance(x.get("id"), str)}
    profile_by_id = {x.get("id"): x for x in profiles if isinstance(x.get("id"), str)}
    figure_by_id = {x.get("id"): x for x in figures if isinstance(x.get("id"), str)}

    for pi, part in enumerate(publication.get("navigation", [])):
        if not isinstance(part, dict):
            errors.append(f"publication.navigation[{pi}]: expected an object")
            continue
        for page_id in part.get("page_ids", []):
            _need(page_id in page_by_id, f"publication.navigation[{pi}]: unknown page {page_id!r}", errors)

    for i, artifact in enumerate(artifacts):
        artifact_id = artifact.get("id")
        regions = artifact.get("regions")
        if not isinstance(regions, list) or not regions:
            errors.append(f"code_artifacts[{i}].regions: expected a non-empty array")
            continue
        region_by_id: dict[str, dict[str, Any]] = {}
        roots = 0
        for j, region in enumerate(regions):
            if not isinstance(region, dict):
                errors.append(f"code_artifacts[{i}].regions[{j}]: expected an object")
                continue
            rid = region.get("id")
            if not isinstance(rid, str) or not ID_RE.fullmatch(rid):
                errors.append(f"code_artifacts[{i}].regions[{j}].id: invalid stable ID {rid!r}")
            elif rid in region_by_id:
                errors.append(f"code_artifacts[{i}]: duplicate region ID {rid!r}")
            else:
                region_by_id[rid] = region
            if region.get("parent_id") is None:
                roots += 1
            span = region.get("source_span", {})
            if isinstance(span, dict):
                start, end = span.get("start_line"), span.get("end_line")
                _need(isinstance(start, int) and isinstance(end, int) and start <= end,
                      f"code_artifacts[{i}].regions[{j}]: invalid source line range", errors)
        _need(roots == 1, f"code_artifacts[{i}]: expected exactly one root region, found {roots}", errors)
        for rid, region in region_by_id.items():
            parent = region.get("parent_id")
            if parent is not None:
                _need(parent in region_by_id, f"code_artifacts[{i}].regions[{rid!r}]: unknown parent {parent!r}", errors)
            seen: set[str] = set()
            current: Any = rid
            while current is not None and current in region_by_id:
                if current in seen:
                    errors.append(f"code_artifacts[{i}].regions[{rid!r}]: parent cycle through {current!r}")
                    break
                seen.add(current)
                current = region_by_id[current].get("parent_id")

        declared_profiles = artifact.get("validation_profile_ids", [])
        for profile_id in declared_profiles:
            profile = profile_by_id.get(profile_id)
            _need(profile is not None, f"code_artifacts[{i}]: unknown validation profile {profile_id!r}", errors)
            if profile is not None:
                _need(profile.get("artifact_id") == artifact_id,
                      f"validation profile {profile_id!r} targets {profile.get('artifact_id')!r}, not {artifact_id!r}", errors)

    for i, page in enumerate(pages):
        for j, block in enumerate(page.get("blocks", [])):
            if not isinstance(block, dict):
                errors.append(f"pages[{i}].blocks[{j}]: expected an object")
                continue
            if block.get("type") == "code_projection":
                aid = block.get("artifact_id")
                artifact = artifact_by_id.get(aid)
                if artifact is None:
                    errors.append(f"pages[{i}].blocks[{j}]: unknown artifact {aid!r}")
                    continue
                region_ids = {r.get("id") for r in artifact.get("regions", []) if isinstance(r, dict)}
                rid = block.get("region_id")
                _need(rid in region_ids, f"pages[{i}].blocks[{j}]: unknown region {rid!r} in {aid!r}", errors)
                for override in block.get("fold_overrides", {}):
                    _need(override in region_ids,
                          f"pages[{i}].blocks[{j}]: fold override names unknown region {override!r}", errors)
            elif block.get("type") == "figure":
                fid = block.get("figure_id")
                _need(fid in figure_by_id, f"pages[{i}].blocks[{j}]: unknown figure {fid!r}", errors)

    for i, profile in enumerate(profiles):
        profile_id = profile.get("id")
        artifact_id = profile.get("artifact_id")
        artifact = artifact_by_id.get(artifact_id)
        _need(artifact is not None, f"validation_profiles[{i}]: unknown artifact {artifact_id!r}", errors)
        if artifact is not None:
            _need(profile_id in artifact.get("validation_profile_ids", []),
                  f"validation profile {profile_id!r} is not listed by artifact {artifact_id!r}", errors)

        mode = profile.get("mode")
        execute = profile.get("execute")
        expect = profile.get("expect")
        if mode == "compile-only":
            _need(execute is None, f"validation profile {profile_id!r}: compile-only must not declare execute", errors)
            _need(expect is None, f"validation profile {profile_id!r}: compile-only must not declare runtime expectations", errors)
        elif mode in RUN_MODES:
            _need(isinstance(execute, dict), f"validation profile {profile_id!r}: mode {mode!r} requires execute", errors)
            _need(isinstance(expect, dict), f"validation profile {profile_id!r}: mode {mode!r} requires expect", errors)
        elif mode == "interactive":
            _need(isinstance(execute, dict) and execute.get("automated") is False,
                  f"validation profile {profile_id!r}: interactive execution must set automated=false", errors)
        else:
            errors.append(f"validation profile {profile_id!r}: unknown mode {mode!r}")

        if mode == "test-harness":
            args = execute.get("arguments", []) if isinstance(execute, dict) else []
            _need(not HELP_ARGS.intersection(args),
                  f"validation profile {profile_id!r}: test-harness must run tests, not a help argument", errors)
            _need(isinstance(expect, dict) and isinstance(expect.get("registered_tests_min"), int),
                  f"validation profile {profile_id!r}: test-harness must assert registered_tests_min", errors)
        if mode == "expected-failure" and isinstance(expect, dict):
            codes = expect.get("exit_codes", [])
            _need(bool(codes) and 0 not in codes,
                  f"validation profile {profile_id!r}: expected-failure requires nonzero exit_codes", errors)

    if check_paths:
        if source is None:
            errors.append("path checking requires the manifest source path")
        else:
            root_value = document.get("repository_root")
            root = (source.parent / root_value).resolve() if isinstance(root_value, str) else source.parent
            paths: set[str] = set()
            for path in publication.get("bibliography_paths", []):
                paths.add(path)
            for artifact in artifacts:
                generation = artifact.get("generation", {})
                if isinstance(generation, dict):
                    paths.update(generation.get("source_paths", []))
                for region in artifact.get("regions", []):
                    if isinstance(region, dict) and isinstance(region.get("source_span"), dict):
                        paths.add(region["source_span"].get("path"))
            for profile in profiles:
                compile_data = profile.get("compile", {})
                if isinstance(compile_data, dict):
                    for unit in compile_data.get("units", []):
                        if isinstance(unit, dict) and unit.get("kind") == "path":
                            paths.add(unit.get("path"))
            for figure in figures:
                paths.add(figure.get("source"))
            for value in sorted(x for x in paths if isinstance(x, str)):
                _need((root / value).exists(), f"path does not exist: {value!r} (root {root})", errors)

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--check-paths", action="store_true", help="verify referenced repository files")
    args = parser.parse_args(argv)
    try:
        document = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if not isinstance(document, dict):
        print("error: top-level JSON value must be an object", file=sys.stderr)
        return 2
    errors = validate(document, source=args.manifest, check_paths=args.check_paths)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"Validation failed with {len(errors)} error(s).")
        return 1
    print(
        "OK: "
        f"{len(document['pages'])} page(s), "
        f"{len(document['code_artifacts'])} artifact(s), "
        f"{len(document['validation_profiles'])} validation profile(s), "
        f"{len(document['figure_assets'])} figure asset(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
