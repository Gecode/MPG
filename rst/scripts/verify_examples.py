#!/usr/bin/env python3
"""Build and honestly validate every canonical MPG program artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
MANIFEST = ROOT / "rst" / "manifests" / "code-projections.json"
REPORT = ROOT / "rst" / "_build" / "reports" / "examples.json"

from tools.mpg.config import get_config
from tools.mpg.examples import build
from tools.mpg.gecode import resolve_gecode


MODEL_EXPECTED = {
    "send-more-money-de-mystified": r"\{9, 5, 6, 7",
    "send-more-money": r"\{9, 5, 6, 7",
    "send-most-money-with-cost": r"\{9, 3, 4, 2",
    "send-most-money-with-driver": r"SEND \+ MOST = MONEY",
    "send-most-money": r"\{9, 3, 4, 2",
    "knights": r"Knights",
    "nonogram": r"Nonogram",
    "magic-sequence": r"MagicSequence",
    "magic-sequence-gcc": r"MagicSequence",
    "warehouses": r"Warehouses",
    "golf": r"Golf\s+Tournament plan",
    "golomb": r"GolombRuler",
    "kakuro": r"Kakuro\s+\.",
    "kakuro-naive": r"Kakuro\s+\.",
    "crossword": r"Crossword",
    "crossword-optimized": r"Crossword",
    "photo": r"Photo",
    "photo-without-modeling-support": r"Photo",
    "bin-packing-naive": r"BinPacking",
    "bin-packing-propagation": r"BinPacking",
    "bin-packing-branching": r"BinPacking",
    "latin-square-ldsb": r"Latin Square",
}

GIST = {
    "send-more-money-with-gist",
    "send-more-money-with-gist-inspection",
    "send-more-money-with-gist-comparison",
}

NOTEST_EXPECTED = {
    "shared-object-and-handle": r"4\s+5",
    "local-object-and-handle": r"4\s+5",
    "local-object-with-external-resources": r"0\s+5",
    "bab": r"m\[10\]",
    "bab-using-full-recomputation": r"m\[10\]",
    "dfs-engine": r"queens",
    "integer-variable-tracer": r"trace::init",
    "general-tracer": r"SEND\+MORE=MONEY",
    "example-search-tracer": r"trace<Search>::init",
}


def run(exe: Path, args: list[str], timeout: int, env: dict[str, str]) -> tuple[subprocess.CompletedProcess[str], float]:
    started = time.monotonic()
    try:
        result = subprocess.run(
            [str(exe), *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            env=env,
        )
    except subprocess.TimeoutExpired as error:
        stdout = error.stdout.decode() if isinstance(error.stdout, bytes) else (error.stdout or "")
        stderr = error.stderr.decode() if isinstance(error.stderr, bytes) else (error.stderr or "")
        result = subprocess.CompletedProcess([str(exe), *args], 124, stdout, stderr + f"\ntimeout after {timeout}s")
    return result, time.monotonic() - started


def artifact_integrity() -> list[dict]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows = []
    for artifact in manifest["artifacts"]:
        path = ROOT / artifact["path"]
        payload = path.read_bytes()
        actual = hashlib.sha256(payload).hexdigest()
        ok = actual == artifact["sha256"] and len(payload) == artifact["bytes"]
        rows.append({"id": artifact["id"], "path": artifact["path"], "status": "pass" if ok else "fail"})
    return rows


def compile_standalone(gc) -> list[dict]:
    output = ROOT / "rst" / "_build" / "example-validation"
    output.mkdir(parents=True, exist_ok=True)
    compiler = os.environ.get("CXX", "c++")
    includes = [argument for path in gc.include_dirs for argument in ("-I", str(path))]
    rows = []

    boolean = ROOT / "rst" / "examples" / "src" / "Boolean-domain-expression.cpp"
    boolean_tu = output / "Boolean-domain-expression-context.cpp"
    boolean_tu.write_text(
        '#include <gecode/minimodel.hh>\nusing namespace Gecode;\n'
        f'#include "{boolean.as_posix()}"\n',
        encoding="utf-8",
    )
    command = [compiler, "-std=c++17", *includes, "-c", str(boolean_tu), "-o", str(output / "Boolean-domain-expression.o")]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    rows.append({"id": boolean.stem, "profile": "compile-only-fragment", "status": "pass" if result.returncode == 0 else "fail", "stderr": result.stderr[-3000:]})

    if gc.root is None:
        rows.extend([
            {"id": "int", "profile": "vis-header-compile", "status": "fail", "reason": "requires --gecode-root to build Gecode with int.vis"},
            {"id": "putting-everything-together", "profile": "vis-model-run", "status": "fail", "reason": "requires --gecode-root to build Gecode with int.vis"},
            {"id": "int-test", "profile": "vis-test-run", "status": "fail", "reason": "requires --gecode-root to build Gecode with int.vis"},
        ])
        return rows

    vis_build = ROOT / "rst" / "_build" / "gecode-vis"
    configure = [
        "cmake", "-S", str(gc.root), "-B", str(vis_build), "-G", "Ninja",
        f"-DGECODE_WITH_VIS={ROOT / 'rst/examples/int.vis'}",
        "-DBUILD_TESTING=ON",
        "-DGECODE_ENABLE_EXAMPLES=OFF", "-DGECODE_ENABLE_GIST=OFF",
        "-DGECODE_ENABLE_FLATZINC=OFF", "-DGECODE_ENABLE_MPFR=OFF", "-DGECODE_INSTALL=OFF",
    ]
    subprocess.run(configure, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    subprocess.run(["cmake", "--build", str(vis_build), "--parallel"], check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    vis_includes = ["-I", str(vis_build), "-I", str(gc.root)]

    header_tu = output / "int-header.cpp"
    header_tu.write_text(f'#include "{(ROOT / "rst/examples/src/int.hh").as_posix()}"\n', encoding="utf-8")
    command = [compiler, "-std=c++17", *vis_includes, "-c", str(header_tu), "-o", str(output / "int-header.o")]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    rows.append({"id": "int", "profile": "header-compile", "status": "pass" if result.returncode == 0 else "fail", "stderr": result.stderr[-3000:]})

    putting = ROOT / "rst" / "examples" / "src" / "putting-everything-together.cpp"
    executable = output / "putting-everything-together"
    libraries = ["-L", str(vis_build)]
    vis_libs = ["gecodesearch", "gecodeminimodel", "gecodeint", "gecodekernel", "gecodesupport"]
    command = [compiler, "-std=c++17", *vis_includes, str(putting), *libraries, *(f"-l{name}" for name in vis_libs), "-o", str(executable)]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    row = {"id": putting.stem, "profile": "model-run", "status": "fail", "stderr": result.stderr[-3000:]}
    if result.returncode == 0:
        env = dict(gc.env)
        library_variable = "DYLD_LIBRARY_PATH" if os.uname().sysname == "Darwin" else "LD_LIBRARY_PATH"
        env[library_variable] = str(vis_build) + (os.pathsep + env[library_variable] if env.get(library_variable) else "")
        started = time.monotonic()
        try:
            executed = subprocess.run([str(executable)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=20, env=env)
        except subprocess.TimeoutExpired as error:
            stdout = error.stdout.decode() if isinstance(error.stdout, bytes) else (error.stdout or "")
            stderr = error.stderr.decode() if isinstance(error.stderr, bytes) else (error.stderr or "")
            executed = subprocess.CompletedProcess([str(executable)], 124, stdout, stderr + "\ntimeout after 20s")
        duration = time.monotonic() - started
        output_text = executed.stdout + executed.stderr
        row.update({"status": "pass" if executed.returncode == 0 and "m[8]" in output_text else "fail", "duration_sec": round(duration, 3), "stdout": executed.stdout[-3000:], "stderr": executed.stderr[-3000:]})
    rows.append(row)

    source = ROOT / "rst/examples/src/int-test.cpp"
    executable = output / "int-test"
    command = [compiler, "-std=c++17", *vis_includes, str(source), *libraries,
               "-lgecodetest", *(f"-l{name}" for name in vis_libs), "-o", str(executable)]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    row = {"id": "int-test", "profile": "vis-test-run", "status": "fail", "stderr": result.stderr[-3000:]}
    if result.returncode == 0:
        env = dict(gc.env)
        library_variable = "DYLD_LIBRARY_PATH" if os.uname().sysname == "Darwin" else "LD_LIBRARY_PATH"
        env[library_variable] = str(vis_build)
        executed, duration = run(executable, ["-iter", "1", "-threads", "1", "-log"], 20, env)
        ok = executed.returncode == 0 and "MPG::Int::Bounds" in executed.stdout and "+" in executed.stdout
        row.update({"status": "pass" if ok else "fail", "duration_sec": round(duration, 3),
                    "stdout": executed.stdout[-3000:], "stderr": executed.stderr[-3000:]})
    rows.append(row)
    return rows


def validate_public_test_consumer(gc, timeout: int) -> list[dict]:
    """Build the published test example through Gecode's public CMake API."""
    config_candidates = [directory / "GecodeConfig.cmake" for directory in gc.lib_dirs]
    if gc.prefix:
        config_candidates.extend(gc.prefix.glob("lib*/cmake/Gecode/GecodeConfig.cmake"))
    config = next((path for path in config_candidates if path.exists()), None)
    if config is None:
        return [{
            "id": "less-test",
            "profile": "installed-test-component",
            "status": "fail",
            "reason": "Gecode test component package metadata was not found",
        }]

    source_dir = ROOT / "rst" / "_build" / "less-test-consumer"
    build_dir = source_dir / "build"
    source_dir.mkdir(parents=True, exist_ok=True)
    for source, destination in (
        (ROOT / "rst/examples/src/less.cpp", source_dir / "less.cpp"),
        (ROOT / "rst/examples/src/less-test.cpp", source_dir / "less-test.cpp"),
        (ROOT / "rst/examples/fragments/less-test/CMakeLists.txt", source_dir / "CMakeLists.txt"),
    ):
        shutil.copy2(source, destination)

    configured = subprocess.run(
        ["cmake", "-S", str(source_dir), "-B", str(build_dir), "-G", "Ninja", f"-DGecode_DIR={config.parent}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    row = {
        "id": "less-test",
        "profile": "installed-test-component",
        "status": "fail",
        "configure_output": configured.stdout[-3000:],
    }
    if configured.returncode != 0:
        return [row]

    compiled = subprocess.run(
        ["cmake", "--build", str(build_dir), "--parallel"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    row["build_output"] = compiled.stdout[-3000:]
    if compiled.returncode != 0:
        return [row]

    executable = build_dir / "less-test"
    listed, _ = run(executable, ["-list-with-tags"], timeout, gc.env)
    executed, duration = run(
        executable,
        ["-tag", "check", "-test", "Int::Less", "-iter", "1", "-threads", "1"],
        timeout,
        gc.env,
    )
    listing = listed.stdout + listed.stderr
    ok = (
        listed.returncode == 0
        and "Int::Less" in listing
        and "check" in listing
        and "normal" in listing
        and executed.returncode == 0
        and "+" in executed.stdout
    )
    row.update({
        "status": "pass" if ok else "fail",
        "args": ["-tag", "check", "-test", "Int::Less", "-iter", "1", "-threads", "1"],
        "duration_sec": round(duration, 3),
        "list_stdout": listed.stdout[-3000:],
        "stdout": executed.stdout[-3000:],
        "stderr": executed.stderr[-3000:],
    })
    return [row]


def validate_binaries(timeout: int, env: dict[str, str]) -> list[dict]:
    config = get_config()
    binary_root = ROOT / ".mpg" / "bin" / "all"
    rows = []
    for name in config["models"]:
        if name in GIST:
            rows.append({"id": name, "kind": "model", "profile": "gist-interactive", "status": "skipped", "reason": "requires interactive Gist UI"})
            continue
        args = ["-solutions", "1", "-time", "1000"] if name.startswith("bin-packing-") else []
        result, duration = run(binary_root / name, args, timeout, env)
        text = result.stdout + result.stderr
        pattern = MODEL_EXPECTED[name]
        ok = result.returncode == 0 and re.search(pattern, text, re.MULTILINE) is not None
        rows.append({"id": name, "kind": "model", "profile": "bounded-model-run", "args": args, "expected_regex": pattern, "status": "pass" if ok else "fail", "exit_code": result.returncode, "duration_sec": round(duration, 3), "stdout": result.stdout[-3000:], "stderr": result.stderr[-3000:]})

    for name in config["tests"]:
        executable = binary_root / name
        listed, _ = run(executable, ["-list"], timeout, env)
        registered = len([line for line in listed.stdout.splitlines() if line.strip()])
        executed, duration = run(executable, ["-iter", "1"], timeout, env)
        ok = listed.returncode == 0 and registered >= 1 and executed.returncode == 0 and "+" in executed.stdout
        rows.append({"id": name, "kind": "test", "profile": "registered-gecode-test", "args": ["-iter", "1"], "registered_tests": registered, "registered_tests_min": 1, "status": "pass" if ok else "fail", "exit_code": executed.returncode, "duration_sec": round(duration, 3), "stdout": executed.stdout[-3000:], "stderr": executed.stderr[-3000:]})

    for name in config["notest"]:
        source = (ROOT / "rst" / "examples" / "src" / f"{name}.cpp").read_text(encoding="utf-8")
        args = ["-solutions", "1"] if "Options opt(" in source else []
        result, duration = run(binary_root / name, args, timeout, env)
        text = result.stdout + result.stderr
        if name in NOTEST_EXPECTED:
            pattern = NOTEST_EXPECTED[name]
        elif name.startswith(("none-", "size-", "assign-")):
            pattern = r"Alpha"
        elif name.startswith("dfs"):
            pattern = r"a="
        else:
            pattern = r"\S"
        ok = result.returncode == 0 and re.search(pattern, text, re.MULTILINE) is not None
        rows.append({"id": name, "kind": "standalone", "profile": "bounded-example-run", "args": args, "expected_regex": pattern, "status": "pass" if ok else "fail", "exit_code": result.returncode, "duration_sec": round(duration, 3), "stdout": result.stdout[-3000:], "stderr": result.stderr[-3000:]})
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gecode-root")
    parser.add_argument("--gecode-prefix")
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--no-build", action="store_true")
    args = parser.parse_args()
    config = get_config()
    manifest = json.loads(MANIFEST.read_text())
    compiled = {row["id"] for row in manifest["artifacts"] if row["validation"] == "compiled"}
    runners = set(config["models"] + config["tests"] + config["notest"])
    expected = runners | {"Boolean-domain-expression", "int", "int-test", "putting-everything-together"}
    if compiled != expected:
        raise SystemExit(f"compiled examples and runners differ: missing runners={sorted(compiled - expected)}, missing artifacts={sorted(expected - compiled)}")
    gc = resolve_gecode(args.gecode_root, args.gecode_prefix)
    if not args.no_build:
        build("all", gc)
    integrity = artifact_integrity()
    compile_rows = compile_standalone(gc) + validate_public_test_consumer(gc, args.timeout)
    validation = validate_binaries(args.timeout, gc.env)
    all_rows = integrity + compile_rows + validation
    failures = [row for row in all_rows if row["status"] == "fail"]
    report = {
        "schema": "mpg-example-validation-v1",
        "gecode_mode": gc.mode,
        "canonical_artifacts": len(integrity),
        "compiled_programs": len(compiled - {"int"}),
        "compiled_headers": len(compiled & {"int"}),
        "validation_profiles": len(compile_rows) + len(validation),
        "passed": sum(row["status"] == "pass" for row in all_rows),
        "skipped": sum(row["status"] == "skipped" for row in all_rows),
        "failed": len(failures),
        "integrity": integrity,
        "compile_only": compile_rows,
        "executions": validation,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"example validation: artifacts={len(integrity)} passed={report['passed']} skipped={report['skipped']} failed={report['failed']}")
    print(f"report: {REPORT}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
