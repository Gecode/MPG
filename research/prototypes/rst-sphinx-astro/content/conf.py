from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "extensions"))

project = "Modeling and Programming with Gecode"
author = "The Gecode Team"
release = "6.4.0"
extensions = ["sphinxcontrib.bibtex", "sphinx.ext.imgconverter", "mpg_semantic"]
root_doc = "index"
exclude_patterns = ["_build"]
nitpicky = True
numfig = True
numfig_secnum_depth = 1
numfig_format = {
    "figure": "Figure %s",
    "table": "Table %s",
    "code-block": "Program %s",
    "section": "Section %s",
}
bibtex_bibfiles = ["references.bib"]
bibtex_default_style = "plain"
math_numfig = True
math_eqref_format = "Equation {number}"
mathjax3_config = {"tex": {"macros": {"Gecode": "\\\\mathsf{Gecode}"}}}
latex_engine = "xelatex"
latex_documents = [("index", "mpg-rst-spike.tex", project, author, "manual")]
latex_additional_files = [
    str(ROOT.parent / "shared" / "classical-pdf" / "mpg-classic.sty"),
    str(ROOT.parent / "shared" / "classical-pdf" / "mpg-sphinx.sty"),
    str(ROOT.parent / "shared" / "classical-pdf" / "gecode-logo.pdf"),
]
latex_elements = {
    "papersize": "a4paper",
    "pointsize": "12pt",
    "classoptions": ",openright",
    "preamble": r"""
\newcommand{\Gecode}{\mathsf{Gecode}}
\usepackage{mpg-sphinx}
""",
}
mpg_reference_inventory = str(ROOT.parent / "shared" / "reference-inventory.json")
mpg_download_root = str(ROOT / "examples")
