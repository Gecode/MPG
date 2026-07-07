from __future__ import annotations

import shutil
from pathlib import Path

from .common import GEN_TEX, ROOT, run_cmd
from .preprocess import fixout
from .sources import references_bib


def _link_or_copy_tree(work: Path, name: str) -> None:
    target = work / name
    if target.exists():
        return
    src = ROOT / name
    if not src.is_dir():
        return
    try:
        target.symlink_to(src, target_is_directory=True)
    except OSError:
        shutil.copytree(src, target, dirs_exist_ok=True)


def build_docs() -> Path:
    mpg_tex = GEN_TEX / "MPG.tex"
    if not mpg_tex.exists():
        raise RuntimeError("MPG.tex not found in .mpg/generated/tex. Run `mpg extract` first.")

    work = GEN_TEX
    _link_or_copy_tree(work, "images")
    _link_or_copy_tree(work, "misc")
    refs = references_bib()
    if refs is not None:
        shutil.copy2(refs, work / "references.bib")

    def _run_latex(cwd: Path) -> None:
        run_cmd(["latex", "-halt-on-error", "-interaction=nonstopmode", "-file-line-error", "MPG"], cwd=cwd)

    def _needs_latex_rerun(cwd: Path) -> bool:
        log = cwd / "MPG.log"
        if not log.exists():
            return False
        text = log.read_text(encoding="utf-8", errors="replace")
        return "Rerun to get outlines right" in text or "Label(s) may have changed" in text

    def _run_pipeline(cwd: Path) -> Path:
        _run_latex(cwd)
        run_cmd(["bibtex", "MPG"], cwd=cwd)

        out = cwd / "MPG.out"
        if out.exists():
            out_in = cwd / "MPG.out.in"
            out.replace(out_in)
            out.write_text(fixout(out_in.read_text(encoding="utf-8")), encoding="utf-8")

        _run_latex(cwd)
        for _ in range(2):
            if not _needs_latex_rerun(cwd):
                break
            _run_latex(cwd)
        run_cmd(["dvips", "-K", "-Ppdf", "MPG.dvi"], cwd=cwd)
        run_cmd(["ps2pdf", "-dALLOWPSTRANSPARENCY", "MPG.ps"], cwd=cwd)
        return cwd / "MPG.pdf"

    pdf = _run_pipeline(work)
    target = ROOT / "MPG.pdf"
    if pdf.resolve() != target.resolve():
        shutil.copy2(pdf, target)
    return pdf
