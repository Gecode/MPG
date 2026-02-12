from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import warnings

from .common import ROOT


LEGACY_ROOT = ROOT
DOCS_SRC_ROOT = ROOT / "docs" / "src"
DOCS_CHAPTERS_ROOT = DOCS_SRC_ROOT / "chapters"
DOCS_TEMPLATE_ROOT = DOCS_SRC_ROOT / "template"
DOCS_STATIC_ROOT = DOCS_SRC_ROOT / "static"
DOCS_BIB_ROOT = DOCS_SRC_ROOT / "bib"

_WARNED: set[str] = set()


def _warn_legacy(logical: str, path: Path) -> None:
    key = f"{logical}:{path}"
    if key in _WARNED:
        return
    _WARNED.add(key)
    warnings.warn(
        f"Using legacy source path for {logical}: {path}. "
        "Move the file under docs/src to remove this fallback.",
        RuntimeWarning,
        stacklevel=2,
    )


def _strip_chapter_suffix(name: str) -> str | None:
    if name.endswith(".tex.in"):
        return name[: -len(".tex.in")]
    if name.endswith(".tex"):
        return name[: -len(".tex")]
    return None


@lru_cache(maxsize=1)
def _chapter_index() -> dict[str, Path]:
    index: dict[str, Path] = {}
    if not DOCS_CHAPTERS_ROOT.exists():
        return index

    grouped: dict[str, list[Path]] = {}
    for p in sorted(DOCS_CHAPTERS_ROOT.rglob("*")):
        if not p.is_file():
            continue
        base = _strip_chapter_suffix(p.name)
        if base is None:
            continue
        grouped.setdefault(base, []).append(p)

    dupes = {name: paths for name, paths in grouped.items() if len(paths) > 1}
    if dupes:
        details: list[str] = []
        for name in sorted(dupes):
            rels = [str(p.relative_to(DOCS_SRC_ROOT)) for p in sorted(dupes[name])]
            details.append(f"{name}: {', '.join(rels)}")
        raise RuntimeError(
            f"Duplicate chapter basenames under {DOCS_CHAPTERS_ROOT}: {'; '.join(details)}"
        )

    for name, paths in grouped.items():
        index[name] = paths[0]
    return index


def reset_caches_for_tests() -> None:
    _chapter_index.cache_clear()
    _WARNED.clear()


def main_template() -> Path:
    p = DOCS_TEMPLATE_ROOT / "MPG.tex.in.in"
    if p.exists():
        return p
    legacy = LEGACY_ROOT / "MPG.tex.in.in"
    if legacy.exists():
        _warn_legacy("template", legacy)
        return legacy
    raise FileNotFoundError("Missing MPG.tex.in.in in docs/src/template and repository root")


def bib_template() -> Path:
    p = DOCS_BIB_ROOT / "MPG.bib.in"
    if p.exists():
        return p
    legacy = LEGACY_ROOT / "MPG.bib.in"
    if legacy.exists():
        _warn_legacy("bibliography template", legacy)
        return legacy
    raise FileNotFoundError("Missing MPG.bib.in in docs/src/bib and repository root")


def references_bib() -> Path | None:
    p = DOCS_BIB_ROOT / "references.bib"
    if p.exists():
        return p
    legacy = LEGACY_ROOT / "references.bib"
    if legacy.exists():
        _warn_legacy("references bibliography", legacy)
        return legacy
    return None


def static_tex_files() -> list[Path]:
    if DOCS_STATIC_ROOT.exists():
        files = sorted(p for p in DOCS_STATIC_ROOT.glob("*.tex") if p.is_file())
        if files:
            return files

    files: list[Path] = []
    for name in ("macros.tex", "license.tex"):
        p = LEGACY_ROOT / name
        if p.exists():
            _warn_legacy("static tex", p)
            files.append(p)
    return files


def chapter_source(name: str) -> Path:
    p = _chapter_index().get(name)
    if p is not None and p.exists():
        return p

    legacy_in = LEGACY_ROOT / f"{name}.tex.in"
    if legacy_in.exists():
        _warn_legacy(f"chapter {name}", legacy_in)
        return legacy_in

    legacy_tex = LEGACY_ROOT / f"{name}.tex"
    if legacy_tex.exists():
        _warn_legacy(f"chapter {name}", legacy_tex)
        return legacy_tex

    raise FileNotFoundError(f"Missing chapter source for {name}")


def resolve_include_tex(name: str, include_base: Path) -> Path:
    direct = include_base / name
    if direct.exists():
        return direct

    base = _strip_chapter_suffix(name) or name
    p = _chapter_index().get(base)
    if p is not None and p.exists():
        return p

    static = DOCS_STATIC_ROOT / f"{base}.tex"
    if static.exists():
        return static

    legacy = LEGACY_ROOT / name
    if legacy.exists():
        _warn_legacy(f"include {name}", legacy)
        return legacy

    legacy_in = LEGACY_ROOT / f"{base}.tex.in"
    if legacy_in.exists():
        _warn_legacy(f"include {name}", legacy_in)
        return legacy_in

    raise FileNotFoundError(f"Missing include/input source {name}")
