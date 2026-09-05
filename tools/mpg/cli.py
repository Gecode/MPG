from __future__ import annotations

import argparse
import os
import subprocess
import shutil
import sys

from .common import ROOT, WORK, which, write_json
from .config import get_config
from .examples import build, run_examples
from .gecode import has_test_framework, resolve_gecode


def cmd_doctor(args: argparse.Namespace) -> int:
    gc = resolve_gecode(args.gecode_root, args.gecode_prefix)
    checks = {
        "python": True,
        "cmake": which("cmake"),
        "ninja": which("ninja"),
        "node": which("node"),
        "latexmk": which("latexmk"),
        "xelatex": which("xelatex"),
        "pdftotext": which("pdftotext"),
        "rsvg-convert": which("rsvg-convert"),
        "gecode_mode": gc.mode,
        "gecode_include_dirs": [str(p) for p in gc.include_dirs],
        "gecode_lib_dirs": [str(p) for p in gc.lib_dirs],
        "gecode_has_test_framework": has_test_framework(gc),
    }
    write_json(ROOT / ".mpg" / "doctor.json", checks)
    for k, v in checks.items():
        print(f"{k}: {v}")
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    gc = resolve_gecode(args.gecode_root, args.gecode_prefix)
    examples = build(args.kind, gc)
    print(f"Built {len(examples)} examples for kind={args.kind}")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    gc = resolve_gecode(args.gecode_root, args.gecode_prefix)
    summary = run_examples(args.kind, gc, timeout=args.timeout)
    print(f"Run summary: passed={summary['passed']} failed={summary['failed']} total={summary['total']}")
    return 0 if summary["failed"] == 0 else 1


def cmd_test(args: argparse.Namespace) -> int:
    cmd_build(args)
    return cmd_run(args)


def cmd_docs(args: argparse.Namespace) -> int:
    subprocess.run([sys.executable, str(ROOT / "rst/scripts/check_sources.py")], cwd=ROOT, check=True)
    environment = os.environ.copy()
    environment.setdefault("GECODE_VERSION", get_config()["version"])
    subprocess.run(
        [sys.executable, str(ROOT / "rst/scripts/build.py"), "all"],
        cwd=ROOT, env=environment, check=True,
    )
    return 0


def cmd_dist(args: argparse.Namespace) -> int:
    subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"], cwd=ROOT, check=True)
    for script in ("verify_platform.py", "verify_examples.py"):
        command = [sys.executable, str(ROOT / "rst/scripts" / script)]
        if script == "verify_examples.py":
            if args.gecode_root:
                command.extend(["--gecode-root", args.gecode_root])
            if args.gecode_prefix:
                command.extend(["--gecode-prefix", args.gecode_prefix])
        subprocess.run(command, cwd=ROOT, check=True)
    cmd_docs(args)
    version = os.environ.get("GECODE_VERSION", get_config()["version"])
    subprocess.run(
        [sys.executable, str(ROOT / "rst/scripts/package_release.py"),
         "--build", str(ROOT / "rst/_build"), "--output", str(ROOT / "output"),
         "--version", version],
        cwd=ROOT, check=True,
    )
    return 0


def cmd_clean(args: argparse.Namespace) -> int:
    if WORK.exists():
        shutil.rmtree(WORK)
    print("Removed .mpg workspace")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="mpg", description="Build and test MPG canonical examples and RST publications")
    p.add_argument("--gecode-root", default=None)
    p.add_argument("--gecode-prefix", default=None)

    sub = p.add_subparsers(dest="cmd", required=True)

    def add_gecode_args(sp: argparse.ArgumentParser) -> None:
        sp.add_argument("--gecode-root", default=None)
        sp.add_argument("--gecode-prefix", default=None)

    s = sub.add_parser("doctor")
    add_gecode_args(s)

    build_p = sub.add_parser("build")
    add_gecode_args(build_p)
    build_p.add_argument("--kind", choices=["models", "tests", "notest", "all"], default="all")

    run_p = sub.add_parser("run")
    add_gecode_args(run_p)
    run_p.add_argument("--kind", choices=["models", "tests", "notest", "all"], default="all")
    run_p.add_argument("--timeout", type=int, default=None)

    test_p = sub.add_parser("test")
    add_gecode_args(test_p)
    test_p.add_argument("--kind", choices=["models", "tests", "notest", "all"], default="all")
    test_p.add_argument("--timeout", type=int, default=None)

    s = sub.add_parser("docs")
    add_gecode_args(s)
    s = sub.add_parser("dist")
    add_gecode_args(s)
    s = sub.add_parser("clean")
    add_gecode_args(s)
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    handlers = {
        "doctor": cmd_doctor,
        "build": cmd_build,
        "run": cmd_run,
        "test": cmd_test,
        "docs": cmd_docs,
        "dist": cmd_dist,
        "clean": cmd_clean,
    }
    return handlers[args.cmd](args)
