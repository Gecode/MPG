from __future__ import annotations

import os
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


def resolve_gecode(gecode_root: str | None, gecode_prefix: str | None) -> GecodeConfig:
    root: Path | None = Path(gecode_root).resolve() if gecode_root else None
    prefix: Path | None = Path(gecode_prefix).resolve() if gecode_prefix else None

    if root:
        include_dirs = _existing([root, root / "gecode", root / "build", root / "build" / "gecode"])
        lib_dirs = _existing([root, root / "build", root / "lib", root / "build" / "lib"])
        env = os.environ.copy()
        var = platform_lib_path_var()
        prior = env.get(var, "")
        entries = [str(p) for p in lib_dirs]
        if prior:
            entries.append(prior)
        env[var] = os.pathsep.join(entries)
        return GecodeConfig("root", root, None, include_dirs, lib_dirs, env)

    if prefix:
        include_dirs = _existing([prefix / "include", prefix / "include" / "gecode"])
        lib_dirs = _existing([prefix / "lib", prefix / "lib64", prefix / "bin"])
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
