from __future__ import annotations

import argparse
import subprocess
import shutil
import tarfile
import zipfile
from pathlib import Path

from .common import GEN_SRC, GEN_TEX, ROOT, WORK, ensure_dirs, which, write_json
from .config import get_config, write_default_config
from .examples import build, run_examples, write_manifest
from .gecode import has_test_framework, resolve_gecode
from .latex import build_docs


def cmd_doctor(args: argparse.Namespace) -> int:
    gc = resolve_gecode(args.gecode_root, args.gecode_prefix)
    checks = {
        "python": True,
        "cmake": which("cmake"),
        "ninja": which("ninja"),
        "latex": which("latex"),
        "bibtex": which("bibtex"),
        "dvips": which("dvips"),
        "ps2pdf": which("ps2pdf"),
        "gecode_mode": gc.mode,
        "gecode_include_dirs": [str(p) for p in gc.include_dirs],
        "gecode_lib_dirs": [str(p) for p in gc.lib_dirs],
        "gecode_has_test_framework": has_test_framework(gc),
    }
    write_json(ROOT / ".mpg" / "doctor.json", checks)
    for k, v in checks.items():
        print(f"{k}: {v}")
    return 0


def cmd_extract(args: argparse.Namespace) -> int:
    ensure_dirs()
    cfg = get_config()
    legacy = WORK / "legacy"
    if legacy.exists():
        shutil.rmtree(legacy)
    legacy.mkdir(parents=True, exist_ok=True)
    try:
        (legacy / "bin").symlink_to(ROOT / "bin", target_is_directory=True)
    except OSError:
        shutil.copytree(ROOT / "bin", legacy / "bin", dirs_exist_ok=True)

    # Copy static .tex files for include.perl expansion context.
    for p in ROOT.glob("*.tex"):
        shutil.copy2(p, legacy / p.name)

    def run_gl(src: Path, dst: Path) -> None:
        with src.open("r", encoding="utf-8") as fin, dst.open("w", encoding="utf-8") as fout:
            subprocess.run(["perl", "bin/gl.perl", cfg["year"]], cwd=legacy, stdin=fin, stdout=fout, check=True, text=True)

    # Chapter generation.
    for ch in cfg["chapters"]:
        p_in = ROOT / f"{ch}.tex.in"
        p_tex = ROOT / f"{ch}.tex"
        out = legacy / f"{ch}.tex"
        if p_in.exists():
            run_gl(p_in, out)
        elif p_tex.exists():
            shutil.copy2(p_tex, out)
        else:
            raise FileNotFoundError(f"Missing chapter source for {ch}")

    # changelog + acknowledgements.
    if (ROOT / "changelog.tex.in").exists():
        run_gl(ROOT / "changelog.tex.in", legacy / "changelog.tex")
        with (ROOT / "changelog.tex.in").open("r", encoding="utf-8") as fin, (legacy / "acks.tex").open("w", encoding="utf-8") as fout:
            subprocess.run(["perl", "bin/gen-ack.perl"], cwd=legacy, stdin=fin, stdout=fout, check=True, text=True)

    # titles.
    title_inputs = [str(ROOT / f"{c}.tex.in") for c in cfg["chapters"] if (ROOT / f"{c}.tex.in").exists()]
    with (legacy / "titles.tex.in").open("w", encoding="utf-8") as fout:
        subprocess.run(["perl", "bin/gen-titles.perl", *title_inputs], cwd=legacy, stdout=fout, check=True, text=True)
    run_gl(legacy / "titles.tex.in", legacy / "titles.tex")

    # Main document include+shorten+gl.
    base = (ROOT / "MPG.tex.in.in").read_text(encoding="utf-8").replace("@VERSION@", cfg["version"]).replace("@YEAR@", cfg["year"])
    p1 = subprocess.run(["perl", "bin/include.perl"], cwd=legacy, input=base, text=True, stdout=subprocess.PIPE, check=True)
    p2 = subprocess.run(["perl", "bin/shorten.perl"], cwd=legacy, input=p1.stdout, text=True, stdout=subprocess.PIPE, check=True)
    (legacy / "MPG.tex.in").write_text(p2.stdout, encoding="utf-8")
    run_gl(legacy / "MPG.tex.in", legacy / "MPG.tex")

    # Bibliography template.
    (legacy / "MPG.bib").write_text(
        (ROOT / "MPG.bib.in").read_text(encoding="utf-8").replace("@VERSION@", cfg["version"]).replace("@YEAR@", cfg["year"]),
        encoding="utf-8",
    )

    # Mirror legacy outputs into .mpg workspace.
    GEN_TEX.mkdir(parents=True, exist_ok=True)
    for p in legacy.glob("*.tex"):
        shutil.copy2(p, GEN_TEX / p.name)
    for p in ("MPG.tex.in", "MPG.bib"):
        if (legacy / p).exists():
            shutil.copy2(legacy / p, GEN_TEX / p)
    generated_cpp = []
    GEN_SRC.mkdir(parents=True, exist_ok=True)
    for ext in ("*.cpp", "*.hh", "*.vis"):
        for p in legacy.glob(ext):
            shutil.copy2(p, GEN_SRC / p.name)
            if p.suffix == ".cpp":
                generated_cpp.append(p.name)

    manifest_examples = write_manifest("all")
    write_json(
        ROOT / ".mpg" / "extract.json",
        {
            "generated_cpp": sorted(set(generated_cpp)),
            "chapter_count": len(cfg["chapters"]),
            "example_count": len(manifest_examples),
        },
    )
    print(f"Extracted chapters: {len(cfg['chapters'])}")
    print(f"Generated C++ files: {len(generated_cpp)}")
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
    cmd_extract(args)
    cmd_build(args)
    return cmd_run(args)


def cmd_docs(args: argparse.Namespace) -> int:
    if not (GEN_TEX / "MPG.tex").exists():
        cmd_extract(args)
    pdf = build_docs()
    print(f"Built PDF: {pdf}")
    return 0


def cmd_dist(args: argparse.Namespace) -> int:
    ensure_dirs()
    dist = ROOT / "dist"
    if dist.exists():
        shutil.rmtree(dist)
    dist.mkdir(parents=True, exist_ok=True)

    pdf = ROOT / "MPG.pdf"
    if not pdf.exists():
        cmd_docs(args)

    tar_path = dist / "MPG.tar.gz"
    with tarfile.open(tar_path, "w:gz") as tf:
        tf.add(ROOT / ".mpg" / "generated" / "src", arcname="MPG")

    zip_path = ROOT / "MPG.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(pdf, arcname="MPG.pdf")
        zf.write(tar_path, arcname="MPG.tar.gz")
    print(f"Created {zip_path}")
    return 0


def cmd_clean(args: argparse.Namespace) -> int:
    if WORK.exists():
        shutil.rmtree(WORK)
    print("Removed .mpg workspace")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="mpg", description="MPG modern tooling")
    p.add_argument("--gecode-root", default=None)
    p.add_argument("--gecode-prefix", default=None)

    sub = p.add_subparsers(dest="cmd", required=True)

    def add_gecode_args(sp: argparse.ArgumentParser) -> None:
        sp.add_argument("--gecode-root", default=None)
        sp.add_argument("--gecode-prefix", default=None)

    s = sub.add_parser("doctor")
    add_gecode_args(s)
    s = sub.add_parser("extract")
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
    write_default_config()
    parser = build_parser()
    args = parser.parse_args(argv)

    handlers = {
        "doctor": cmd_doctor,
        "extract": cmd_extract,
        "build": cmd_build,
        "run": cmd_run,
        "test": cmd_test,
        "docs": cmd_docs,
        "dist": cmd_dist,
        "clean": cmd_clean,
    }
    return handlers[args.cmd](args)
