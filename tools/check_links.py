#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_links.py — verify that local href/src targets exist.

Usage:
  python3 tools/check_links.py --root .
  python3 tools/check_links.py --root dist
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

ATTR_RE = re.compile(r'\b(?:href|src)="([^"]+)"', re.IGNORECASE)
COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
SCRIPT_RE = re.compile(r"<script\b.*?</script>", re.DOTALL | re.IGNORECASE)
STYLE_RE = re.compile(r"<style\b.*?</style>", re.DOTALL | re.IGNORECASE)
SKIP_PREFIX = ("http://", "https://", "mailto:", "tel:", "javascript:", "data:", "#", "//")
SKIP_TEMPLATE = ("{{", "{%")


def clean(text: str) -> str:
    text = COMMENT_RE.sub("", text)
    text = SCRIPT_RE.sub("", text)
    text = STYLE_RE.sub("", text)
    return text


def resolve(root: Path, page: Path, value: str) -> Path | None:
    value = value.strip()
    if not value or value.startswith(SKIP_PREFIX) or any(x in value for x in SKIP_TEMPLATE):
        return None
    path = unquote(urlparse(value).path)
    if not path:
        return None
    if path.startswith("/"):
        target = root / path.lstrip("/")
    else:
        target = page.parent / path
    target = target.resolve()
    if target.is_dir():
        target = target / "index.html"
    return target


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = ap.parse_args()
    root = Path(args.root).resolve()
    skip_dirs = {"dist", ".git", "node_modules", "__pycache__", "templates", "assets"}
    pages = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        for name in filenames:
            if name.endswith(".html") and name != "tm-ai-panel.html":
                pages.append(Path(dirpath) / name)

    missing: list[tuple[Path, str, Path]] = []
    checked = 0
    for page in pages:
        try:
            text = clean(page.read_text(encoding="utf-8", errors="ignore"))
        except OSError as exc:
            print("READ_FAIL", page, exc)
            continue
        for value in ATTR_RE.findall(text):
            target = resolve(root, page, value)
            if target is None:
                continue
            checked += 1
            if not target.exists():
                missing.append((page, value, target))

    print("pages=%d links=%d missing=%d" % (len(pages), checked, len(missing)))
    for page, value, target in missing[:50]:
        print("MISSING %s -> %s" % (page.relative_to(root), value))
    return 0 if not missing else 1


if __name__ == "__main__":
    sys.exit(main())
