#!/usr/bin/env python3
"""Materialize and fingerprint code dependencies declared by QMD files."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
INCLUDE = re.compile(r'\binclude="([^"]+\.(?:cc|cpp|hh|hpp))"')


def declared_sources() -> list[Path]:
    sources: set[Path] = set()
    for document in sorted(ROOT.glob("*.qmd")):
        for relative in INCLUDE.findall(document.read_text(encoding="utf-8")):
            source = (ROOT / relative).resolve()
            try:
                source.relative_to(ROOT)
            except ValueError as error:
                raise SystemExit(f"code include escapes project: {relative}") from error
            if not source.is_file():
                raise SystemExit(f"missing code include in {document.name}: {relative}")
            sources.add(source)
    if not sources:
        raise SystemExit("no code includes found")
    return sorted(sources)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "_build" / "extracted")
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)

    manifest: list[dict[str, str]] = []
    for source in declared_sources():
        relative = source.relative_to(ROOT)
        target = output / relative.name
        shutil.copyfile(source, target)
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        manifest.append(
            {
                "document_source": relative.as_posix(),
                "extracted_source": target.relative_to(output).as_posix(),
                "sha256": digest,
            }
        )
        print(f"extracted {relative} -> {target.relative_to(ROOT)}")

    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
