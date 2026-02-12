from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / ".mpg"
GEN = WORK / "generated"
GEN_TEX = GEN / "tex"
GEN_SRC = GEN / "src"
BUILD = WORK / "build"
BIN = WORK / "bin"
RESULTS = WORK / "results"


def ensure_dirs() -> None:
    for p in (WORK, GEN, GEN_TEX, GEN_SRC, BUILD, BIN, RESULTS):
        p.mkdir(parents=True, exist_ok=True)


def run_cmd(cmd: list[str], cwd: Path | None = None, env: dict[str, str] | None = None) -> None:
    subprocess.run(cmd, cwd=cwd or ROOT, env=env, check=True)


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def which(name: str) -> bool:
    return shutil.which(name) is not None


def normalize_name(name: str) -> str:
    return "-".join(name.strip().split())


def platform_lib_path_var() -> str:
    if os.name == "nt":
        return "PATH"
    if os.uname().sysname.lower() == "darwin":
        return "DYLD_LIBRARY_PATH"
    return "LD_LIBRARY_PATH"
