from __future__ import annotations

from pathlib import Path
try:
    import tomllib
except ModuleNotFoundError:  # Python <3.11
    try:
        import tomli as tomllib
    except ModuleNotFoundError:
        tomllib = None

import re
from .common import ROOT
from .sources import main_template


DEFAULT_VERSION = "6.3.0"
DEFAULT_YEAR = "2020"
DEFAULT_MODELS = [
    "send-more-money-de-mystified",
    "send-more-money-with-gist",
    "send-more-money-with-gist-inspection",
    "send-more-money",
    "send-most-money-with-cost",
    "send-most-money-with-driver",
    "send-most-money",
    "knights",
    "nonogram",
    "magic-sequence",
    "magic-sequence-gcc",
    "warehouses",
    "golf",
    "golomb",
    "kakuro",
    "kakuro-naive",
    "crossword",
    "crossword-optimized",
    "photo",
    "photo-without-modeling-support",
    "bin-packing-naive",
    "bin-packing-propagation",
    "bin-packing-branching",
    "latin-square-ldsb",
]
DEFAULT_TESTS = [
    "less-even-better",
    "less-better",
    "less-concise",
    "less",
    "disequality",
    "equal-naive",
    "equal",
    "equal-idempotent",
    "equal-idempotent-using-modification-events",
    "or-true",
    "or-true-concise",
    "or-true-with-dynamic-subscriptions",
    "less-or-equal-reified-full",
    "less-or-equal-reified-half",
    "max-using-rewriting",
    "or-true-using-rewriting",
    "min-and-max",
    "less-for-integer-and-Boolean-variables",
    "domain-equal-with-and-without-offset",
    "or-and-and-from-or",
    "naive-domain-equal",
    "non-shared-domain-equal",
    "domain-equal-using-bounds-propagation",
    "domain-equal-using-staging",
    "domain-equal-with-offset",
    "samedom",
    "samedom-using-predefined-view-advisors",
    "or",
    "intersection",
    "linear",
]
DEFAULT_NOTEST = [
    "shared-object-and-handle",
    "local-object-and-handle",
    "local-object-with-external-resources",
    "none-min",
    "none-min-improved",
    "size-min",
    "assign-min",
    "none-min-and-none-max",
    "none-min-with-no-good-support",
    "dfs-binary",
    "dfs",
    "bab",
    "dfs-using-full-recomputation",
    "dfs-using-full-recomputation-and-lao",
    "dfs-using-hybrid-recomputation",
    "dfs-using-adaptive-recomputation",
    "bab-using-full-recomputation",
    "dfs-engine",
    "integer-variable-tracer",
    "general-tracer",
    "example-search-tracer",
]


def load_user_config() -> dict:
    cfg = ROOT / "mpg.toml"
    if not cfg.exists():
        return {}
    if tomllib is None:
        # Keep operation possible on Python <3.11 without extra dependencies.
        return {}
    return tomllib.loads(cfg.read_text(encoding="utf-8"))


def get_config() -> dict:
    user = load_user_config()
    chapters = _discover_chapters()
    models = DEFAULT_MODELS
    tests = DEFAULT_TESTS
    notest = DEFAULT_NOTEST
    return {
        "version": user.get("version", DEFAULT_VERSION),
        "year": str(user.get("year", DEFAULT_YEAR)),
        "chapters": user.get("chapters", chapters),
        "models": user.get("models", models),
        "tests": user.get("tests", tests),
        "notest": user.get("notest", notest),
        "compile_flags": user.get(
            "compile_flags",
            ["-DNDEBUG", "-fvisibility=hidden", "-ffast-math", "-fno-strict-aliasing", "-pthread", "-O3", "-ggdb"],
        ),
        "run_timeout_sec": int(user.get("run_timeout_sec", 20)),
        "examples": user.get("examples", {}),
    }


def _discover_chapters() -> list[str]:
    src = main_template().read_text(encoding="utf-8")
    names = re.findall(r"\\include\{([^}]+)\}", src)
    names = [n for n in names if n not in {"changelog", "acks", "titles", "license"}]
    return names




def write_default_config() -> None:
    cfg = ROOT / "mpg.toml"
    if cfg.exists():
        return
    cfg.write_text(
        """version = "6.3.0"
year = 2020
run_timeout_sec = 20

# Optional explicit overrides.
# chapters = ["intro", "m-started"]
# models = ["send-more-money"]
# tests = ["less"]
# notest = ["none-min"]
# compile_flags = ["-O2"]

[examples]
# Example override schema:
# [examples.send-more-money]
# kind = "model"
# source = "send-more-money.cpp"
# run_args = ["-help"]
# timeout_sec = 10
# enabled = true
""",
        encoding="utf-8",
    )
