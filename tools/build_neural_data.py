#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_neural_data.py — 由 data/ 下的 JSON 契约文件生成 neural/data.js

数据源（唯一真源，勿手改生成的 data.js）：
  data/chapters.json   —— 7 章元信息（n/slug/title/summary/color/texture/modules）
  data/modules.json    —— 全部模块的色值 / 链接 / 标签（milestone/slug/sim/note...）
  data/knowledge.json  —— 各模块全文 chunk（含 section 归属）
  data/links.json      —— 跨模块/跨章边（同题异法/极限对照/共用工具/前置路径），可选

modules.json 中列出但 knowledge.json 尚无 chunk 的模块（M8B / M12 后补）：
打印 WARNING、跳过，并从各章 modules 列表中一并剔除；其余照常生成。

输出：neural/data.js  window.TM_NEURAL = {chapters, modules, links, linkTypes}
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "neural" / "data.js"


def load_contract(name: str) -> dict[str, Any]:
    """读取一个 JSON 契约文件；缺失 / 非法 JSON / 非对象 → 响亮退出。"""
    path = DATA / name
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        sys.exit(f"build_neural_data: missing contract {path}")
    try:
        doc: Any = json.loads(text)
    except json.JSONDecodeError as exc:
        sys.exit(f"build_neural_data: malformed JSON in {path}: {exc}")
    if not isinstance(doc, dict):
        sys.exit(f"build_neural_data: {path}: expected a JSON object, got {type(doc).__name__}")
    return doc


def contract_list(doc: dict[str, Any], key: str, name: str) -> list[dict[str, Any]]:
    rows = doc.get(key)
    if not isinstance(rows, list) or not all(isinstance(r, dict) for r in rows):
        sys.exit(f"build_neural_data: {name}: '{key}' must be a list of objects")
    return rows


def need(row: dict[str, Any], keys: tuple[str, ...], ctx: str) -> None:
    missing = [k for k in keys if k not in row]
    if missing:
        sys.exit(f"build_neural_data: {ctx}: missing keys {missing}")


def group_sections(chunks: list[dict[str, Any]], mid: str) -> list[dict[str, Any]]:
    """chunk 按 section 分组，section 保持首次出现顺序；chunk 输出 {id,text}。"""
    order: list[str] = []
    by_sec: dict[str, list[dict[str, str]]] = {}
    for ch in chunks:
        need(ch, ("id", "section", "text"), f"knowledge.json module {mid} chunk")
        sec = ch["section"]
        if sec not in by_sec:
            by_sec[sec] = []
            order.append(sec)
        by_sec[sec].append({"id": ch["id"], "text": ch["text"]})
    return [{"name": s, "chunks": by_sec[s]} for s in order]


def index_kb(kb_rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    kb_by_id: dict[str, dict[str, Any]] = {}
    for km in kb_rows:
        need(km, ("id", "chunks"), "knowledge.json module")
        if not isinstance(km["chunks"], list) or not all(isinstance(c, dict) for c in km["chunks"]):
            sys.exit(f"build_neural_data: knowledge.json module {km['id']}: 'chunks' must be a list of objects")
        if km["id"] in kb_by_id:
            sys.exit(f"build_neural_data: knowledge.json duplicate module id {km['id']}")
        kb_by_id[str(km["id"])] = km
    return kb_by_id


def build_modules(
    module_rows: list[dict[str, Any]], kb_by_id: dict[str, dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    """modules.json（元信息）× knowledge.json（chunk）→ {Mxx: {...}}；缺 chunk 的模块 WARNING 跳过。"""
    modules: dict[str, dict[str, Any]] = {}
    for m in module_rows:
        mid = str(m.get("milestone", "?"))
        need(m, ("milestone", "slug", "title", "summary", "color", "sim", "note"), f"modules.json module {mid}")
        if mid in modules:
            sys.exit(f"build_neural_data: modules.json duplicate milestone {mid}")
        km = kb_by_id.get(mid)
        if km is None or not km["chunks"]:
            print(f"WARNING: no chunks for {mid}")
            continue
        modules[mid] = {
            "id": mid,
            "slug": m["slug"],
            "title": m["title"],
            "summary": m["summary"],
            "color": m["color"],
            "tags": m.get("tags", []),
            "href": m["sim"],
            "pdf": m["note"],
            "sections": group_sections(km["chunks"], mid),
        }
    return modules


def build_chapters(
    chapter_rows: list[dict[str, Any]], known_milestones: set[str], modules: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    chapters: list[dict[str, Any]] = []
    for c in chapter_rows:
        need(c, ("n", "slug", "title", "summary", "color", "texture", "modules"), f"chapters.json {c.get('slug', '?')}")
        mods = c["modules"]
        if not isinstance(mods, list) or not all(isinstance(x, str) for x in mods):
            sys.exit(f"build_neural_data: chapters.json {c['slug']}: 'modules' must be a list of strings")
        unknown = sorted(set(mods) - known_milestones)
        if unknown:
            sys.exit(f"build_neural_data: chapters.json {c['slug']}: modules not in modules.json: {unknown}")
        chapters.append(
            {
                "slug": c["slug"],
                "n": c["n"],
                "title": c["title"],
                "summary": c["summary"],
                "color": c["color"],
                "texture": c["texture"],
                "modules": [m for m in mods if m in modules],
            }
        )
    return chapters


def build_links(known: set[str]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """data/links.json（可选）：校验端点/类型/id 唯一后原样并入输出。"""
    path = DATA / "links.json"
    if not path.exists():
        return [], {}
    doc = load_contract("links.json")
    types = doc.get("linkTypes", {})
    links = contract_list(doc, "links", "links.json")
    seen: set[str] = set()
    for l in links:
        need(l, ("id", "from", "to", "type", "title"), f"links.json {l.get('id', '?')}")
        if l["from"] not in known or l["to"] not in known:
            sys.exit(f"build_neural_data: links.json {l['id']}: endpoint not in modules.json")
        if l["type"] not in types:
            sys.exit(f"build_neural_data: links.json {l['id']}: unknown type {l['type']}")
        if l["id"] in seen:
            sys.exit(f"build_neural_data: links.json duplicate id {l['id']}")
        seen.add(l["id"])
    return links, types


def main() -> None:
    chapter_rows = contract_list(load_contract("chapters.json"), "chapters", "chapters.json")
    module_rows = contract_list(load_contract("modules.json"), "modules", "modules.json")
    kb_rows = contract_list(load_contract("knowledge.json"), "modules", "knowledge.json")

    kb_by_id = index_kb(kb_rows)
    known_milestones = {str(m.get("milestone", "")) for m in module_rows}
    orphan = sorted(set(kb_by_id) - known_milestones)
    if orphan:
        sys.exit(f"build_neural_data: knowledge.json modules absent from modules.json: {orphan}")

    modules = build_modules(module_rows, kb_by_id)
    chapters = build_chapters(chapter_rows, known_milestones, modules)
    links, link_types = build_links(known_milestones)

    out = {"chapters": chapters, "modules": modules, "links": links, "linkTypes": link_types}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(out, ensure_ascii=False, separators=(",", ":"))
    OUT.write_text(
        "/* generated by tools/build_neural_data.py — do not edit by hand */\n"
        "window.TM_NEURAL=" + payload + ";\n",
        encoding="utf-8",
    )
    total_secs = sum(len(m["sections"]) for m in modules.values())
    cross = 0
    chap_of = {m: c["slug"] for c in chapters for m in c["modules"]}
    for l in links:
        if chap_of.get(l["from"]) != chap_of.get(l["to"]):
            cross += 1
    print(f"wrote {OUT.relative_to(ROOT)}  chapters={len(chapters)} modules={len(modules)} sections={total_secs} links={len(links)} (cross-chapter={cross}) bytes={OUT.stat().st_size}")


if __name__ == "__main__":
    main()
