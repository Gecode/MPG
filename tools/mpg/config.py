from __future__ import annotations

import tomllib
from .common import ROOT


DEFAULT_VERSION = "6.4.0"
DEFAULT_YEAR = "2026"
DEFAULT_MODELS = [
    "send-more-money-de-mystified",
    "send-more-money-with-gist",
    "send-more-money-with-gist-inspection",
    "send-more-money-with-gist-comparison",
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
    return tomllib.loads(cfg.read_text(encoding="utf-8"))


def get_config() -> dict:
    user = load_user_config()
    models = DEFAULT_MODELS
    tests = DEFAULT_TESTS
    notest = DEFAULT_NOTEST
    return {
        "version": user.get("version", DEFAULT_VERSION),
        "year": str(user.get("year", DEFAULT_YEAR)),
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
