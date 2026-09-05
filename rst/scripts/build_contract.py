"""Small shared checks for safe and repeatable publication builds."""

from __future__ import annotations

import os
from pathlib import Path
import re
import subprocess


SAFE_RELEASE = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+(?:-[A-Za-z0-9.-]+)?")


def validate_release(value: str, *, allow_development: bool = True) -> str:
    """Validate the identifier used in URLs and output paths."""
    if value == "development":
        if not allow_development:
            raise ValueError("a published release cannot use the development identifier")
        return value
    if not SAFE_RELEASE.fullmatch(value):
        raise ValueError(f"invalid release identifier: {value!r}; expected X.Y.Z or X.Y.Z-prerelease")
    return value


def source_date_epoch(repository: Path) -> str:
    """Return a stable timestamp for tools that embed creation metadata."""
    configured = os.environ.get("SOURCE_DATE_EPOCH")
    if configured is not None:
        if not configured.isdigit():
            raise ValueError("SOURCE_DATE_EPOCH must be a non-negative integer")
        return configured
    try:
        result = subprocess.run(
            ["git", "show", "-s", "--format=%ct", "HEAD"],
            cwd=repository,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return "0"
    value = result.stdout.strip()
    return value if value.isdigit() else "0"
