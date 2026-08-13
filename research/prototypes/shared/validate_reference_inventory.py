#!/usr/bin/env python3
"""Validate the release-import boundary for a Gecode symbol inventory."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit


VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
KEY_RE = re.compile(r"^[a-z][a-z0-9_-]*:\S+$")
BASE_RE = re.compile(r"^/doc/([0-9]+\.[0-9]+\.[0-9]+)/reference/$")


def validate(data: object, site_root: Path | None = None) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["top level must be an object"]

    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")

    version = data.get("gecode_version")
    if not isinstance(version, str) or not VERSION_RE.fullmatch(version):
        errors.append("gecode_version must be a semantic release triplet")

    base_url = data.get("base_url")
    base_match = BASE_RE.fullmatch(base_url) if isinstance(base_url, str) else None
    if base_match is None:
        errors.append("base_url must be /doc/<version>/reference/")
    elif isinstance(version, str) and base_match.group(1) != version:
        errors.append("base_url version must equal gecode_version")

    if not isinstance(data.get("generated_by"), str) or not data["generated_by"].strip():
        errors.append("generated_by must be a non-empty string")

    objects = data.get("objects")
    if not isinstance(objects, dict) or not objects:
        errors.append("objects must be a non-empty object")
        return errors

    for key, value in sorted(objects.items()):
        if not isinstance(key, str) or not KEY_RE.fullmatch(key):
            errors.append(f"invalid object key: {key!r}")
        if not isinstance(value, dict):
            errors.append(f"{key}: entry must be an object")
            continue
        title = value.get("title")
        relative_url = value.get("url")
        if not isinstance(title, str) or not title.strip():
            errors.append(f"{key}: title must be non-empty")
        if not isinstance(relative_url, str):
            errors.append(f"{key}: url must be a string")
            continue
        parsed = urlsplit(relative_url)
        if parsed.scheme or parsed.netloc or relative_url.startswith("/") or ".." in parsed.path.split("/"):
            errors.append(f"{key}: url must be relative and contained by the imported reference tree")
            continue
        if not parsed.path.endswith(".html"):
            errors.append(f"{key}: url path must name an HTML file")
        if site_root is not None and isinstance(base_url, str):
            target = site_root / base_url.lstrip("/") / parsed.path
            if not target.is_file():
                errors.append(f"{key}: imported target does not exist: {target}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inventory", type=Path)
    parser.add_argument("--site-root", type=Path)
    args = parser.parse_args(argv)
    try:
        data = json.loads(args.inventory.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    errors = validate(data, args.site_root)
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1
    print(f"OK: {len(data['objects'])} symbols for Gecode {data['gecode_version']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
