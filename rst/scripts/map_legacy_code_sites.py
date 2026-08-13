#!/usr/bin/env python3
"""Map transitional extracted reST snippets to canonical ``mpg-code`` keys."""

from __future__ import annotations

import difflib
import hashlib
import json
from pathlib import Path
import re
import argparse

ROOT = Path(__file__).resolve().parents[2]
CANONICAL = ROOT / "rst" / "manifests" / "code-projections.json"
ORACLE = ROOT / "rst" / "content" / "modeling" / "programs" / "manifest.json"
OUTPUT = ROOT / "rst" / "manifests" / "code-modeling-sites.json"


def normalize(value: str) -> str:
    value = value.replace("\\(\n)", "").replace("…", "...")
    value = re.sub(r"\[download:[^]]+\]", "", value)
    return "\n".join(line.strip() for line in value.splitlines() if line.strip())


def render(root: Path, projection: dict) -> str:
    path = root / projection["artifact"]
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    pieces: list[str] = []
    for segment in projection.get("segments", []):
        if "text" in segment:
            pieces.append(segment["text"])
        else:
            item = segment["source"]
            pieces.append("".join(lines[item["start_line"] - 1:item["end_line"]]))
    if not projection.get("segments"):
        pieces.append("".join(lines[projection["start_line"] - 1:projection["end_line"]]))
    return "".join(pieces)


def rewrite_modeling(rows: list[dict]) -> int:
    by_artifact = {row["transitional_artifact"]: row for row in rows if row["canonical_projection"]}
    changed = 0
    for rst in sorted((ROOT / "rst/content/modeling").glob("*.rst")):
        lines = rst.read_text(encoding="utf-8").splitlines()
        output: list[str] = []
        i = 0
        while i < len(lines):
            match = re.match(r"^(\s*)\.\. literalinclude::\s+(programs/\S+)\s*$", lines[i])
            if not match:
                output.append(lines[i]); i += 1; continue
            artifact = (rst.parent / match.group(2)).relative_to(ROOT).as_posix()
            mapped = by_artifact.get(artifact)
            if mapped is None:
                raise RuntimeError(f"no canonical mapping for {rst}:{i + 1} ({artifact})")
            output.append(f"{match.group(1)}.. mpg-code:: {mapped['canonical_projection']}")
            i += 1
            while i < len(lines) and lines[i].startswith(match.group(1) + "   :"):
                if ":language:" not in lines[i]:
                    output.append(lines[i])
                i += 1
            changed += 1
        rst.write_text("\n".join(output) + "\n", encoding="utf-8")
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rewrite-modeling", action="store_true", help="replace transitional modeling literalincludes with mapped mpg-code directives")
    args = parser.parse_args()
    if not ORACLE.exists():
        print("transitional modeling projection oracle is absent; nothing to map")
        return 0
    canonical = json.loads(CANONICAL.read_text(encoding="utf-8"))
    oracle = json.loads(ORACLE.read_text(encoding="utf-8"))["projections"]
    candidates: dict[str, list[tuple[str, str]]] = {}
    for key, projection in canonical["projections"].items():
        chapter = Path(projection["source"]).name.removesuffix(".tex.in")
        candidates.setdefault(chapter, []).append((key, normalize(render(ROOT, projection))))

    rows = []
    counts = {"exact": 0, "fuzzy": 0}
    for old in oracle:
        chapter = Path(old["legacy_generated_source"]).stem
        content = (ROOT / old["artifact"]).read_text(encoding="utf-8")
        needle = normalize(content)
        choices = candidates.get(chapter, [])
        exact = [item for item in choices if item[1] == needle]
        if exact:
            key, _ = exact[0]
            confidence = 1.0
            method = "exact-normalized"
            counts["exact"] += 1
        elif choices:
            scored = sorted(
                ((difflib.SequenceMatcher(None, needle, text, autojunk=False).ratio(), key) for key, text in choices),
                reverse=True,
            )
            confidence, key = scored[0]
            method = "fuzzy-review-required"
            counts["fuzzy"] += 1
        else:
            key, confidence, method = "", 0.0, "unmapped"
        rows.append({
            "transitional_artifact": old["artifact"],
            "transitional_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
            "canonical_projection": key,
            "confidence": round(confidence, 6),
            "method": method,
            "directive": old["directive"],
            "directive_line_before_extraction": old["directive_line_before_extraction"],
        })
    payload = {
        "schema": "mpg-code-site-map-v1",
        "site_count": len(rows),
        "exact_normalized": counts["exact"],
        "fuzzy_review_required": counts["fuzzy"],
        "sites": rows,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"mapped {len(rows)} transitional sites: {counts['exact']} exact, {counts['fuzzy']} requiring review")
    if args.rewrite_modeling:
        changed = rewrite_modeling(rows)
        print(f"rewrote {changed} transitional literalinclude directives")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
