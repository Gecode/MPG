from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Iterable


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


def run_capture(cmd: list[str], cwd: Path | None = None) -> str:
    out = subprocess.run(cmd, cwd=cwd or ROOT, check=True, text=True, stdout=subprocess.PIPE)
    return out.stdout


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_make_list(var: str) -> list[str]:
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    pattern = re.compile(rf"^{re.escape(var)}\s*=\s*\\\n(?P<body>(?:\s+.*\\\n)+\s+.*)$", re.MULTILINE)
    m = pattern.search(makefile)
    if not m:
        return []
    tokens: list[str] = []
    for line in m.group("body").splitlines():
        line = line.strip()
        if line.endswith("\\"):
            line = line[:-1].strip()
        if not line:
            continue
        tokens.extend(line.split())
    return tokens


def which(name: str) -> bool:
    return shutil.which(name) is not None


def normalize_name(name: str) -> str:
    return re.sub(r"\s+", "-", name.strip())


def chunked(it: Iterable[str], size: int) -> list[list[str]]:
    out: list[list[str]] = []
    cur: list[str] = []
    for x in it:
        cur.append(x)
        if len(cur) >= size:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def platform_lib_path_var() -> str:
    if os.name == "nt":
        return "PATH"
    if os.uname().sysname.lower() == "darwin":
        return "DYLD_LIBRARY_PATH"
    return "LD_LIBRARY_PATH"
