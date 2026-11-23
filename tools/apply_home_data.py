#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""apply_home_data.py — 用 data/ 契约文件幂等重写首页内联数组

把 index.html（或 --file 指定文件）里的两个数组整体重写为契约文件的渲染结果：
  window.TM_SUBMODULES = [...]  ← data/modules.json
  window.TM_MODULES    = [...]  ← data/chapters.json

渲染保持与现有行完全一致的风格与字段顺序：单引号 JS 字面量、键不加引号、
每对象一行（行首一个空格）、收尾 `];` 顶格。重复运行产出字节相同的文件。
任一替换区无法在全文中精确定位一次 → 退出码非零且不写盘。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

SUBMARK = "window.TM_SUBMODULES = ["
CHAPMARK = "window.TM_MODULES = ["
SUB_FIELDS: tuple[str, ...] = ("slug", "milestone", "title", "src", "tags", "summary", "sim", "note", "color")
CHAP_FIELDS: tuple[str, ...] = ("n", "slug", "milestone", "title", "src", "tags", "summary", "sim", "color", "texture", "modules")


def load_rows(rel: str, key: str) -> list[dict[str, Any]]:
    """读取契约文件里 key 对应的对象数组；缺失 / 非法 → 响亮退出。"""
    path = DATA / rel
    try:
        doc: Any = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        sys.exit(f"apply_home_data: missing contract {path}")
    except json.JSONDecodeError as exc:
        sys.exit(f"apply_home_data: malformed JSON in {path}: {exc}")
    rows = doc.get(key) if isinstance(doc, dict) else None
    if not isinstance(rows, list) or not all(isinstance(r, dict) for r in rows):
        sys.exit(f"apply_home_data: {path}: '{key}' must be a list of objects")
    return rows


def js_str(s: str) -> str:
    if "</" in s:
        sys.exit(f"apply_home_data: refusing to inline string containing '</' into a <script> block: {s!r}")
    esc = s.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "\\r")
    return f"'{esc}'"


def js_lit(v: Any) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, str):
        return js_str(v)
    if isinstance(v, list):
        return "[" + ",".join(js_lit(x) for x in v) + "]"
    sys.exit(f"apply_home_data: cannot serialize {type(v).__name__} as a JS literal")


def render_obj(fields: tuple[str, ...], row: dict[str, Any]) -> str:
    missing = [k for k in fields if k not in row]
    if missing:
        sys.exit(f"apply_home_data: contract row {row.get('slug', row.get('milestone', '?'))!r}: missing keys {missing}")
    return "{" + ",".join(f"{k}:{js_lit(row[k])}" for k in fields) + "}"


def find_region(text: str, marker: str) -> tuple[int, int]:
    """定位 `marker ... ]` 替换区，返回 [marker 起点, 收尾 ']'+1)。出现次数≠1 / 括号不闭合 / 缺 ';' → 退出。"""
    hits = text.count(marker)
    if hits != 1:
        sys.exit(f"apply_home_data: marker {marker!r} found {hits} times, expected exactly 1")
    start = text.index(marker)
    depth = 0
    i = start + len(marker) - 1  # 定位在 '['
    quote: str | None = None
    while i < len(text):
        c = text[i]
        if quote is not None:
            if c == "\\":
                i += 2
                continue
            if c == quote:
                quote = None
        elif c in "'\"":
            quote = c
        elif c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                if text[i + 1 : i + 2] != ";":
                    sys.exit(f"apply_home_data: expected ';' immediately after array for {marker!r}")
                return start, i + 1
        i += 1
    sys.exit(f"apply_home_data: unbalanced array for {marker!r}")


def cross_check(chapter_rows: list[dict[str, Any]], module_rows: list[dict[str, Any]]) -> None:
    known = {str(m.get("milestone", "")) for m in module_rows}
    for c in chapter_rows:
        mods = c.get("modules", [])
        if not isinstance(mods, list) or not all(isinstance(x, str) for x in mods):
            sys.exit(f"apply_home_data: chapters.json {c.get('slug', '?')}: 'modules' must be a list of strings")
        unknown = sorted(set(mods) - known)
        if unknown:
            sys.exit(f"apply_home_data: chapters.json {c['slug']}: modules not in modules.json: {unknown}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Rewrite TM_SUBMODULES / TM_MODULES arrays from data/ contracts.")
    ap.add_argument("--file", default=str(ROOT / "index.html"), help="HTML 文件（默认 index.html；测试时用 --file 指定副本）")
    args = ap.parse_args()
    path = Path(args.file)

    text = path.read_text(encoding="utf-8")
    subs = load_rows("modules.json", "modules")
    chaps = load_rows("chapters.json", "chapters")
    cross_check(chaps, subs)

    new_text = text
    for marker, fields, rows in ((SUBMARK, SUB_FIELDS, subs), (CHAPMARK, CHAP_FIELDS, chaps)):
        start, end = find_region(new_text, marker)
        body = "\n" + ",\n".join(" " + render_obj(fields, row) for row in rows) + "\n]"
        new_text = new_text[:start] + marker + body + new_text[end:]

    path.write_text(new_text, encoding="utf-8")
    print(f"wrote {path} submodules={len(subs)} chapters={len(chaps)} bytes={path.stat().st_size}")


if __name__ == "__main__":
    main()
