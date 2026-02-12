from __future__ import annotations

import json
import os
import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from .common import BIN, BUILD, GEN_SRC, RESULTS, ROOT, ensure_dirs, run_cmd, write_json
from .config import get_config
from .gecode import GecodeConfig, has_test_framework


MODEL_LIBS = [
    "gecodedriver",
    "gecodesearch",
    "gecodefloat",
    "gecodeminimodel",
    "gecodeset",
    "gecodeint",
    "gecodekernel",
    "gecodesupport",
]
TEST_LIBS = [
    "gecodesearch",
    "gecodefloat",
    "gecodeminimodel",
    "gecodeset",
    "gecodeint",
    "gecodekernel",
    "gecodesupport",
]


@dataclass
class Example:
    name: str
    kind: str
    source: Path
    wrapper: Path | None
    requires_gist: bool
    run_args: list[str]
    timeout_sec: int
    enabled: bool


def _kind_names(kind: str, cfg: dict) -> list[tuple[str, str]]:
    if kind == "models":
        return [(x, "model") for x in cfg["models"]]
    if kind == "tests":
        return [(x, "test") for x in cfg["tests"]]
    if kind == "notest":
        return [(x, "notest") for x in cfg["notest"]]
    if kind == "all":
        return [(x, "model") for x in cfg["models"]] + [(x, "test") for x in cfg["tests"]] + [(x, "notest") for x in cfg["notest"]]
    raise ValueError(f"Unsupported kind: {kind}")


def _build_examples(kind: str, cfg: dict) -> list[Example]:
    out: list[Example] = []
    for name, ex_kind in _kind_names(kind, cfg):
        source = ROOT / f"{name}.cpp"
        if not source.exists():
            source = GEN_SRC / f"{name}.cpp"
        wrapper = None
        if ex_kind == "test":
            wrapper = ROOT / "test" / f"{name}.cpp"
        elif ex_kind == "notest":
            wrapper = ROOT / "notest" / f"{name}.cpp"

        md = cfg["examples"].get(name, {})
        if "source" in md:
            source = GEN_SRC / md["source"]
        if "wrapper" in md:
            wrapper = ROOT / md["wrapper"]
        run_args = list(md.get("run_args", []))
        if not run_args:
            src_text = source.read_text(encoding="utf-8", errors="ignore") if source.exists() else ""
            if ex_kind == "test":
                run_args = ["-help"]
            elif ("Options opt(" in src_text) or ("SizeOptions opt(" in src_text) or ("Driver::Options opt(" in src_text):
                run_args = ["-help"]

        out.append(
            Example(
                name=name,
                kind=ex_kind,
                source=source,
                wrapper=wrapper,
                requires_gist=False,
                run_args=run_args,
                timeout_sec=int(md.get("timeout_sec", cfg["run_timeout_sec"])),
                enabled=bool(md.get("enabled", True)),
            )
        )
    return [e for e in out if e.enabled]


def write_manifest(kind: str) -> list[Example]:
    cfg = get_config()
    examples = _build_examples(kind, cfg)
    manifest = {
        "kind": kind,
        "version": cfg["version"],
        "year": cfg["year"],
        "examples": _manifest_rows(examples),
    }
    write_json(ROOT / ".mpg" / "manifest.json", manifest)
    return examples


def _has_library(name: str, lib_dirs: list[Path]) -> bool:
    if not lib_dirs:
        return True
    prefixes = [f"lib{name}.", f"{name}."]
    for d in lib_dirs:
        if not d.exists():
            continue
        for p in d.iterdir():
            if any(p.name.startswith(pref) for pref in prefixes):
                return True
    return False


def _needs_gist(text: str) -> bool:
    return bool(re.search(r"(gecode/gist\.hh|\bGist::)", text))


def _prepare_sources(examples: list[Example], src_dir: Path) -> list[tuple[Example, Path]]:
    src_dir.mkdir(parents=True, exist_ok=True)
    mapped: list[tuple[Example, Path]] = []
    for ex in examples:
        if not ex.source.exists():
            raise RuntimeError(f"Missing generated source: {ex.source}. Run `mpg extract` first.")
        out = src_dir / f"{ex.name}.cpp"
        if ex.wrapper is None:
            out.write_text(ex.source.read_text(encoding="utf-8"), encoding="utf-8")
        else:
            if not ex.wrapper.exists():
                raise RuntimeError(f"Missing wrapper source: {ex.wrapper}")
            out.write_text(
                ex.source.read_text(encoding="utf-8") + ex.wrapper.read_text(encoding="utf-8"),
                encoding="utf-8",
            )
        txt = out.read_text(encoding="utf-8", errors="ignore")
        ex.requires_gist = _needs_gist(txt)
        if ex.requires_gist and not ex.run_args:
            # Prevent interactive Gist UI from blocking automated runs.
            ex.run_args = ["-help"]
        mapped.append((ex, out))
    return mapped


def _manifest_rows(examples: list[Example]) -> list[dict]:
    return [
        {
            "id": e.name,
            "kind": e.kind,
            "source": str(e.source),
            "wrapper": str(e.wrapper) if e.wrapper else None,
            "requires_gist": e.requires_gist,
            "run_args": e.run_args,
            "timeout_sec": e.timeout_sec,
            "enabled": e.enabled,
        }
        for e in examples
    ]


def _emit_cmake(build_dir: Path, mapped: list[tuple[Example, Path]], gc: GecodeConfig, cfg: dict, kind: str) -> Path:
    cmake_dir = build_dir / "cmake"
    src_dir = build_dir / "src"
    cmake_dir.mkdir(parents=True, exist_ok=True)
    runtime_dir = BIN / kind
    runtime_dir.mkdir(parents=True, exist_ok=True)

    lines: list[str] = [
        "cmake_minimum_required(VERSION 3.16)",
        "project(mpg_examples LANGUAGES CXX)",
        "set(CMAKE_CXX_STANDARD 17)",
        "set(CMAKE_CXX_STANDARD_REQUIRED ON)",
        f"set(CMAKE_RUNTIME_OUTPUT_DIRECTORY \"{runtime_dir.as_posix()}\")",
    ]
    if cfg["compile_flags"]:
        flags = " ".join(cfg["compile_flags"])
        lines.append(f"add_compile_options({flags})")
    if gc.include_dirs:
        lines.append("include_directories(" + " ".join(f'\"{p.as_posix()}\"' for p in gc.include_dirs) + ")")
    if gc.lib_dirs:
        lines.append("set(_MPG_LIB_DIRS " + " ".join(f'\"{p.as_posix()}\"' for p in gc.lib_dirs) + ")")
    else:
        lines.append("set(_MPG_LIB_DIRS)")

    for lib in sorted(set(MODEL_LIBS + TEST_LIBS + ["gecodegist"])):
        lines.append(
            f"find_library(MPG_LIB_{lib.upper()} NAMES {lib} PATHS ${{_MPG_LIB_DIRS}}"
            + (" NO_DEFAULT_PATH" if gc.lib_dirs else "")
            + ")"
        )
        lines.append(
            f"if(NOT MPG_LIB_{lib.upper()})\n  find_library(MPG_LIB_{lib.upper()} NAMES {lib})\nendif()"
        )

    if any(e.kind == "test" for e, _ in mapped):
        if not has_test_framework(gc):
            raise RuntimeError(
                "Test examples need Gecode test framework sources. "
                "Provide --gecode-root pointing to a Gecode source/build tree."
            )
        t = gc.root / "test"
        lines.append(
            "add_library(mpg_gecode_test_objs OBJECT "
            f'\"{(t / "test.cpp").as_posix()}\" '
            f'\"{(t / "int.cpp").as_posix()}\" '
            f'\"{(t / "float.cpp").as_posix()}\" '
            f'\"{(t / "set.cpp").as_posix()}\")'
        )

    for ex, src in mapped:
        lines.append(f'add_executable({ex.name} "{src.as_posix()}")')
        libs = list(TEST_LIBS if ex.kind == "test" else MODEL_LIBS)
        if ex.requires_gist:
            libs.insert(1, "gecodegist")
        if ex.kind == "test":
            lines.append(f"target_sources({ex.name} PRIVATE $<TARGET_OBJECTS:mpg_gecode_test_objs>)")
        resolved = " ".join(f"${{MPG_LIB_{l.upper()}}}" for l in libs)
        lines.append(f"target_link_libraries({ex.name} PRIVATE {resolved})")

    cmakelists = cmake_dir / "CMakeLists.txt"
    cmakelists.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return cmake_dir


def build(kind: str, gc: GecodeConfig) -> list[Example]:
    ensure_dirs()
    cfg = get_config()
    examples = write_manifest(kind)
    skipped: list[dict[str, str]] = []
    if not _has_library("gecodegist", gc.lib_dirs):
        kept: list[Example] = []
        for ex in examples:
            txt = ex.source.read_text(encoding="utf-8", errors="ignore") if ex.source.exists() else ""
            if _needs_gist(txt):
                skipped.append({"id": ex.name, "reason": "gecodegist library not available in selected Gecode installation"})
            else:
                kept.append(ex)
        examples = kept
    build_dir = BUILD / kind
    src_dir = build_dir / "src"
    mapped = _prepare_sources(examples, src_dir)
    write_json(
        ROOT / ".mpg" / "manifest.json",
        {
            "kind": kind,
            "version": cfg["version"],
            "year": cfg["year"],
            "examples": _manifest_rows(examples),
        },
    )
    cmake_dir = _emit_cmake(build_dir, mapped, gc, cfg, kind)

    gen = "Ninja"
    run_cmd(["cmake", "-S", str(cmake_dir), "-B", str(build_dir / "out"), "-G", gen])
    run_cmd(["cmake", "--build", str(build_dir / "out"), "--parallel"])
    if skipped:
        write_json(RESULTS / f"build-{kind}.json", {"kind": kind, "skipped": skipped})
    return examples


def run_examples(kind: str, gc: GecodeConfig, timeout: int | None = None) -> dict:
    manifest = json.loads((ROOT / ".mpg" / "manifest.json").read_text(encoding="utf-8"))
    rows = list(manifest["examples"])
    out_rows = []

    for row in rows:
        name = row["id"]
        ex_kind = row["kind"]
        if kind != "all":
            want = {"models": "model", "tests": "test", "notest": "notest"}[kind]
            if ex_kind != want:
                continue
        if bool(row.get("requires_gist")):
            out_rows.append(
                {
                    "id": name,
                    "kind": ex_kind,
                    "status": "skipped",
                    "message": "Gist examples are compile-only in automated runs",
                }
            )
            continue
        exe = BIN / kind / name
        if not exe.exists() and os.name == "nt":
            exe = exe.with_suffix(".exe")
        if not exe.exists():
            out_rows.append({"id": name, "status": "missing", "message": "binary not found"})
            continue
        args = [str(exe)] + list(row.get("run_args", []))
        t = int(timeout if timeout is not None else row.get("timeout_sec", 20))
        started = time.time()
        try:
            cp = subprocess.run(args, timeout=t, env=gc.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            status = "pass" if cp.returncode == 0 else "fail"
            stderr_text = cp.stderr[-5000:]
            if (
                status == "fail"
                and bool(row.get("requires_gist"))
                and ("Incompatible processor." in stderr_text and "Qt build requires" in stderr_text)
            ):
                status = "skipped"
            out_rows.append(
                {
                    "id": name,
                    "kind": ex_kind,
                    "status": status,
                    "exit_code": cp.returncode,
                    "duration_sec": round(time.time() - started, 3),
                    "stdout": cp.stdout[-5000:],
                    "stderr": stderr_text,
                }
            )
        except subprocess.TimeoutExpired:
            out_rows.append(
                {
                    "id": name,
                    "kind": ex_kind,
                    "status": "timeout",
                    "duration_sec": round(time.time() - started, 3),
                    "timeout_sec": t,
                }
            )

    summary = {
        "kind": kind,
        "total": len(out_rows),
        "passed": sum(1 for r in out_rows if r["status"] == "pass"),
        "skipped": sum(1 for r in out_rows if r["status"] == "skipped"),
        "failed": sum(1 for r in out_rows if r["status"] in {"fail", "timeout", "missing"}),
        "results": out_rows,
    }
    write_json(RESULTS / f"run-{kind}.json", summary)
    return summary
