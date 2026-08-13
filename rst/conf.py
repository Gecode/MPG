"""Production Sphinx configuration for Modeling and Programming with Gecode.

Build from the repository root with ``rst/scripts/build.py``.  Keeping the
configuration outside ``content`` lets a release bundle contain authored
sources separately from the publication machinery.
"""

from __future__ import annotations

import os
from pathlib import Path
import re
import sys

RST_ROOT = Path(__file__).resolve().parent
REPOSITORY_ROOT = RST_ROOT.parent
sys.path.insert(0, str(RST_ROOT / "extensions"))

project = "Modeling and Programming with Gecode"
author = "Christian Schulte, Guido Tack, Mikael Z. Lagerkvist"
copyright = "2005-2026, The Gecode Team"
release = os.environ.get("GECODE_VERSION", "development")
version = release
if not re.fullmatch(r"[0-9A-Za-z.+-]+", release):
    raise ValueError(f"GECODE_VERSION is not a safe release identifier: {release!r}")

extensions = [
    "sphinx.ext.imgconverter",
    "sphinx.ext.intersphinx",
    "sphinxcontrib.bibtex",
    "mpg_code",
    "mpg_semantics",
    "mpg_stable_links",
]

root_doc = os.environ.get("MPG_ROOT_DOC", "content/index")
source_suffix = {".rst": "restructuredtext"}
exclude_patterns = [
    "_build/**",
    "platform-tests/**",
    # Migration-only collection pages.  The production book owns ordering in
    # ``content/index`` and the semantic part pages; including these a second
    # time changes chapter numbering and creates duplicate toctree parents.
    "content/core/index.rst",
    "content/modeling/index.rst",
    "content/propagators/index.rst",
    "core/index.rst",
    "modeling/index.rst",
    "propagators/index.rst",
    "Thumbs.db",
    ".DS_Store",
]
templates_path = [str(RST_ROOT / "_templates")]
nitpicky = True
keep_warnings = False
show_warning_types = True
# The maintained bibliography deliberately uses BibTeX ``crossref`` entries.
# sphinxcontrib-bibtex validates the child entry before inheriting the
# proceedings title and reports a false missing-booktitle warning for those
# records; the rendered bibliography still contains the inherited venue.
suppress_warnings: list[str] = ["bibtex.missing_field"]

primary_domain = "cpp"
highlight_language = "cpp"
pygments_style = "default"

numfig = True
numfig_secnum_depth = 1
numfig_format = {
    "figure": "Figure %s",
    "table": "Table %s",
    "code-block": "Program %s",
    "tip": "Tip %s",
    "section": "Section %s",
}
math_numfig = True
math_eqref_format = "Equation {number}"
mathjax3_config = {
    "tex": {
        "macros": {
            "Gecode": r"\\mathsf{Gecode}",
            "NN": r"\\mathbb{N}",
            "ZZ": r"\\mathbb{Z}",
            "RR": r"\\mathbb{R}",
        }
    }
}

# Sphinx search is generated at release time and works without a server.  The
# website may index the same pages, but this output remains independently
# searchable when hosted as a release artifact.
html_theme = "basic"
html_title = project
html_short_title = "MPG"
html_static_path = [str(RST_ROOT / "_static")]
html_css_files = ["mpg.css"]
html_logo = str(RST_ROOT / "figures" / "gecode-logo.svg")
html_sidebars = {"**": ["mpg-localtoc.html", "mpg-search.html"]}
html_use_index = True
html_domain_indices = True
html_copy_source = True
html_show_sourcelink = False
html_show_sphinx = False
html_show_copyright = True
html_search_language = "en"
html_baseurl = os.environ.get("MPG_HTML_BASEURL", "")
html_context = {
    # Deliberately short, web-navigation labels.  The authored page titles
    # remain canonical; this hierarchy is the stable documentation shell.
    "mpg_navigation": [
        {
            "letter": "M", "title": "Modeling", "overview": "parts/modeling",
            "pages": [
                ("modeling/started", "Getting started"),
                ("modeling/comfy", "Getting comfortable"),
                ("modeling/integer", "Integer and Boolean constraints"),
                ("modeling/set", "Set constraints"),
                ("modeling/float", "Floating-point constraints"),
                ("modeling/minimodel", "MiniModel"),
                ("modeling/branch", "Branching"),
                ("modeling/search", "Search"),
                ("modeling/gist", "Gist"),
                ("modeling/driver", "Command-line driver"),
                ("modeling/group", "Groups"),
            ],
        },
        {
            "letter": "C", "title": "Case studies", "overview": "parts/case-studies",
            "pages": [
                ("case-studies/golomb", "Golomb rulers"),
                ("case-studies/magic-sequence", "Magic sequence"),
                ("case-studies/photo", "Photo arrangement"),
                ("case-studies/warehouses", "Warehouses"),
                ("case-studies/nonogram", "Nonograms"),
                ("case-studies/golf", "Golf tournament"),
                ("case-studies/knights", "Knights"),
                ("case-studies/bin-packing", "Bin packing"),
                ("case-studies/kakuro", "Kakuro"),
                ("case-studies/crossword", "Crossword"),
            ],
        },
        {
            "letter": "P", "title": "Propagators", "overview": "parts/propagators",
            "pages": [
                ("propagators/started", "Getting started"),
                ("propagators/avoid", "What to avoid"),
                ("propagators/reified", "Reification and rewriting"),
                ("propagators/domain", "Domain constraints"),
                ("propagators/advisors", "Advisors"),
                ("propagators/views", "Views"),
                ("propagators/sets", "Set propagators"),
                ("propagators/floats", "Float propagators"),
                ("propagators/memory", "Memory management"),
            ],
        },
        {
            "letter": "B", "title": "Branchers", "overview": "parts/branchers",
            "pages": [
                ("branchers/started", "Getting started"),
                ("branchers/advanced", "Advanced branchers"),
            ],
        },
        {
            "letter": "V", "title": "Variables", "overview": "parts/variables",
            "pages": [("variables/index", "Programming variables")],
        },
        {
            "letter": "S", "title": "Search engines", "overview": "parts/search-engines",
            "pages": [
                ("search-engines/started", "Getting started"),
                ("search-engines/recomputation", "Recomputation"),
                ("search-engines/engine", "Engine implementation"),
            ],
        },
    ],
}

# Every section label is a public interface.  Title-derived ids may still be
# emitted by docutils, but references and redirects must use explicit labels.
mpg_require_explicit_section_labels = True
mpg_redirects_file = str(RST_ROOT / "redirects.json")

_new_bibliography = RST_ROOT / "content" / "references.bib"
_legacy_bibliography = REPOSITORY_ROOT / "docs" / "src" / "bib" / "references.bib"
bibtex_bibfiles = [
    os.environ.get(
        "MPG_BIBLIOGRAPHY",
        str(_new_bibliography if _new_bibliography.exists() else _legacy_bibliography),
    )
]
bibtex_default_style = "plain"

# Imported Gecode API symbols remain release-versioned.  A release job can
# replace this mapping or point it at a local objects.inv before building.
intersphinx_mapping = {}

latex_engine = "xelatex"
latex_documents = [
    (root_doc, "MPG.tex", project, author, "manual"),
]
latex_additional_files = [
    str(RST_ROOT / "_static" / "latex" / "mpg-classic.sty"),
    str(RST_ROOT / "_static" / "latex" / "mpg-sphinx.sty"),
    # Binary artwork remains the one extracted and checked against the legacy
    # title page.  The figures workstream will move all publication assets,
    # including this logo, into the final release asset tree.
    str(REPOSITORY_ROOT / "research" / "prototypes" / "shared" / "classical-pdf" / "gecode-logo.pdf"),
    str(RST_ROOT / "figures" / "pdf" / "cc-by-nc-nd.pdf"),
]
latex_elements = {
    "papersize": "a4paper",
    "pointsize": "12pt",
    "classoptions": ",openright",
    # Keep figures out of the prose flow in the PDF.  Prefer the top of a
    # page, allow the bottom or a dedicated float page when necessary, and
    # deliberately omit LaTeX's `h` (place approximately "here") option.
    "figure_align": "tbp",
    # Match the long-standing a4wide measure used by MPG.  Sphinx's default
    # manual geometry is narrower and changes both the book's density and the
    # pagination of almost every chapter.
    "geometry": r"""\usepackage{geometry}
\setlength{\textwidth}{6.375in}
\setlength{\oddsidemargin}{0in}
\setlength{\evensidemargin}{0in}
\setlength{\topmargin}{0pt}
\setlength{\textheight}{42\baselineskip}
\addtolength{\textheight}{\topskip}""",
    "preamble": r"""
\newcommand{\Gecode}{\mathsf{Gecode}}
\newcommand{\MPGGecodeVersion}{""" + release + r"""}
\usepackage{mpg-sphinx}
""",
}

# The semantic extension can resolve these against a release inventory.  The
# empty value leaves normal C++ cross-references available during migration.
_frozen_reference_inventory = RST_ROOT / "release-reference-inventory.json"
mpg_reference_inventory = os.environ.get(
    "MPG_REFERENCE_INVENTORY",
    str(_frozen_reference_inventory) if _frozen_reference_inventory.exists() else "",
)
mpg_download_root = str(REPOSITORY_ROOT)
mpg_code_manifest = str(RST_ROOT / "manifests" / "code-projections.json")
mpg_code_root = str(REPOSITORY_ROOT)
