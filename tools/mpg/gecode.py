from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

from .common import ROOT, platform_lib_path_var


@dataclass
class GecodeConfig:
    mode: str
    root: Path | None
    prefix: Path | None
    include_dirs: list[Path]
    lib_dirs: list[Path]
    env: dict[str, str]


def _existing(ps: list[Path]) -> list[Path]:
    return [p for p in ps if p.exists()]


def _prefix_dirs(prefix: Path) -> tuple[list[Path], list[Path]]:
    include_dirs = _existing([prefix / "include", prefix / "include" / "gecode"])
    lib_dirs = _existing([prefix / "lib", prefix / "lib64", prefix / "bin"])
    return include_dirs, lib_dirs


_CORE_LIBS = [
    "gecodedriver",
    "gecodesearch",
    "gecodefloat",
    "gecodeminimodel",
    "gecodeset",
    "gecodeint",
    "gecodekernel",
    "gecodesupport",
]


def _has_core_libraries(path: Path) -> bool:
    return all(
        any((path / f"lib{name}{suffix}").exists() for suffix in (".dylib", ".so", ".a"))
        for name in _CORE_LIBS
    )


def _has_library(path: Path, name: str) -> bool:
    return any((path / f"lib{name}{suffix}").exists() for suffix in (".dylib", ".so", ".a"))


def _source_version(root: Path) -> str | None:
    cfg = root / "gecode" / "support" / "config.hpp"
    if not cfg.exists():
        return None
    m = re.search(r'#define\s+GECODE_VERSION\s+"([^"]+)"', cfg.read_text(encoding="utf-8", errors="ignore"))
    return m.group(1) if m else None


def _config_version(path: Path) -> str | None:
    for cfg in (path / "GecodeConfig.cmake", path / "gecode-config.cmake"):
        if not cfg.exists():
            continue
        m = re.search(r'set\s*\(\s*Gecode_VERSION\s+"([^"]+)"', cfg.read_text(encoding="utf-8", errors="ignore"))
        if m:
            return m.group(1)
    return None


def _root_build_dir(root: Path) -> Path | None:
    source_version = _source_version(root)
    candidates: list[tuple[Path, bool]] = [
        (root / "build" / "mpg-gist-validation", True),
        (root / "build" / "mpg-validation", False),
        (root / "cmake-build-release", False),
        (root / "cmake-build-debug", False),
    ]
    build = root / "build"
    if build.exists():
        candidates.extend((p, False) for p in sorted(build.iterdir()) if p.is_dir())
    candidates.extend([(root / "build", False), (root / "lib", False), (root, False)])

    seen: set[Path] = set()
    for candidate, needs_gist in candidates:
        candidate = candidate.resolve()
        if candidate in seen:
            continue
        seen.add(candidate)
        if not candidate.exists() or not _has_core_libraries(candidate):
            continue
        if needs_gist and not _has_library(candidate, "gecodegist"):
            continue
        candidate_version = _config_version(candidate)
        if source_version and candidate_version and candidate_version != source_version:
            continue
        return candidate
    return None


def resolve_gecode(gecode_root: str | None, gecode_prefix: str | None) -> GecodeConfig:
    root: Path | None = Path(gecode_root).resolve() if gecode_root else None
    prefix: Path | None = Path(gecode_prefix).resolve() if gecode_prefix else None

    if root:
        build_dir = _root_build_dir(root)
        if build_dir is not None and build_dir != root:
            include_dirs = _existing([build_dir, build_dir / "gecode", root, root / "gecode"])
            lib_dirs = _existing([build_dir, build_dir / "lib"])
        else:
            include_dirs = _existing([root / "build", root / "build" / "gecode", root, root / "gecode"])
            lib_dirs = _existing([root / "build", root / "build" / "lib", root / "lib", root])
        if prefix:
            p_inc, p_lib = _prefix_dirs(prefix)
            include_dirs.extend(p_inc)
            lib_dirs.extend(p_lib)
        env = os.environ.copy()
        var = platform_lib_path_var()
        prior = env.get(var, "")
        entries = [str(p) for p in dict.fromkeys(lib_dirs)]
        if prior:
            entries.append(prior)
        env[var] = os.pathsep.join(entries)
        mode = "root+prefix" if prefix else ("root-build" if build_dir is not None and build_dir != root else "root")
        return GecodeConfig(mode, root, prefix, include_dirs, lib_dirs, env)

    if prefix:
        include_dirs, lib_dirs = _prefix_dirs(prefix)
        env = os.environ.copy()
        var = platform_lib_path_var()
        prior = env.get(var, "")
        entries = [str(p) for p in lib_dirs]
        if prior:
            entries.append(prior)
        env[var] = os.pathsep.join(entries)
        return GecodeConfig("prefix", None, prefix, include_dirs, lib_dirs, env)

    # Default: prefer common system installation prefixes first.
    for sys_prefix in (Path("/usr/local"), Path("/opt/homebrew"), Path("/usr")):
        include_dirs = _existing([sys_prefix / "include", sys_prefix / "include" / "gecode"])
        lib_dirs = _existing([sys_prefix / "lib", sys_prefix / "lib64", sys_prefix / "bin"])
        if include_dirs and lib_dirs:
            env = os.environ.copy()
            var = platform_lib_path_var()
            prior = env.get(var, "")
            entries = [str(p) for p in lib_dirs]
            if prior:
                entries.append(prior)
            env[var] = os.pathsep.join(entries)
            return GecodeConfig("auto-prefix", None, sys_prefix, include_dirs, lib_dirs, env)

    # Fallback: sibling checkout.
    sibling = (ROOT / ".." / "gecode").resolve()
    if sibling.exists():
        include_dirs = _existing([sibling, sibling / "gecode"])
        lib_dirs = _existing([sibling])
        env = os.environ.copy()
        var = platform_lib_path_var()
        prior = env.get(var, "")
        entries = [str(p) for p in lib_dirs]
        if prior:
            entries.append(prior)
        env[var] = os.pathsep.join(entries)
        return GecodeConfig("auto-sibling", sibling, None, include_dirs, lib_dirs, env)

    return GecodeConfig("system", None, None, [], [], os.environ.copy())


def has_test_framework(gc: GecodeConfig) -> bool:
    if not gc.root:
        return False
    test_dir = gc.root / "test"
    needed = [test_dir / "test.cpp", test_dir / "int.cpp", test_dir / "float.cpp", test_dir / "set.cpp"]
    return all(p.exists() for p in needed)
