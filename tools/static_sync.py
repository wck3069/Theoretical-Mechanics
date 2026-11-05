#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""static_sync.py — rebuild dist when site source files change."""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WATCH_DIRS = ("assets", "chapters", "modules")
WATCH_FILES = ("index.html", "catalog.html", "binet.html", "sitemap.xml", "robots.txt", "HOMEPAGE.md")
SKIP_DIRS = {".git", "dist", "qa", "data", "deploy", "tools", "__pycache__", "node_modules"}
SKIP_SUFFIX = (".log", ".aux", ".toc", ".out", ".fls", ".fdb_latexmk", ".xdv", ".synctex.gz")


def snapshot() -> dict[str, tuple[int, int]]:
    result: dict[str, tuple[int, int]] = {}
    for name in WATCH_FILES:
        path = ROOT / name
        if path.is_file():
            st = path.stat()
            result[str(path)] = (st.st_mtime_ns, st.st_size)
    for name in WATCH_DIRS:
        base = ROOT / name
        if not base.is_dir():
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
            for filename in filenames:
                if filename.endswith(SKIP_SUFFIX):
                    continue
                path = Path(dirpath) / filename
                st = path.stat()
                result[str(path)] = (st.st_mtime_ns, st.st_size)
    return result


def build() -> None:
    print(time.strftime("%Y-%m-%d %H:%M:%S"), "rebuild dist", flush=True)
    proc = subprocess.run(
        ["bash", str(ROOT / "tools" / "export_static.sh")],
        cwd=ROOT, capture_output=True, text=True,
    )
    tail = (proc.stdout + proc.stderr)[-1200:]
    print(tail, flush=True)
    if proc.returncode:
        print("build failed:", proc.returncode, flush=True)


def main() -> int:
    if not (ROOT / "tools" / "export_static.sh").is_file():
        print("export_static.sh not found", file=sys.stderr)
        return 2
    previous = snapshot()
    build()
    while True:
        time.sleep(1.0)
        current = snapshot()
        if current == previous:
            continue
        time.sleep(0.7)
        previous = snapshot()
        build()


if __name__ == "__main__":
    raise SystemExit(main())
