#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""merge_kb_drafts.py — 把 modules/*/knowledge.draft.json 合并进 data/knowledge.json。

兼容两种草稿格式：
  扁平：{"id"/"milestone": "M27", "slug", "title", "tags", "src", "summary", "href", "chunks": [...]}
  嵌套：{"M28": {"title", "slug", "summary", "chunks": [...]}}

元信息（title/tags/src/summary/sim→href/note→pdf）以 data/modules.json 注册表为准；
草稿只提供 chunks。注册表中不存在或 KB 已含的里程碑默认跳过（--replace 允许覆盖 chunks）。
合并后重算 chunk_count/char_count。

用法：
  python3 tools/merge_kb_drafts.py            # 合并所有缺失模块
  python3 tools/merge_kb_drafts.py --replace  # 已存在的也用草稿 chunks 覆盖
  python3 tools/merge_kb_drafts.py --check    # 只报告哪些草稿未入库
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KB_PATH = ROOT / "data" / "knowledge.json"
REG_PATH = ROOT / "data" / "modules.json"


def parse_draft(path: Path) -> tuple[str, dict]:
    d = json.loads(path.read_text(encoding="utf-8"))
    if "chunks" in d:
        mid = d.get("milestone") or d.get("id")
        return str(mid), d
    # nested {M##: {...}}
    if len(d) == 1:
        mid, body = next(iter(d.items()))
        if isinstance(body, dict) and "chunks" in body:
            return str(mid), body
    raise SystemExit(f"merge_kb_drafts: 无法识别草稿格式 {path}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--replace", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    kb = json.loads(KB_PATH.read_text(encoding="utf-8"))
    reg = {m["milestone"]: m for m in json.loads(REG_PATH.read_text(encoding="utf-8"))["modules"]}
    have = {m["milestone"]: m for m in kb["modules"]}

    drafts = sorted((ROOT / "modules").glob("*/knowledge.draft.json"))
    added, replaced, skipped = [], [], []
    for path in drafts:
        mid, body = parse_draft(path)
        if mid not in reg:
            skipped.append(f"{mid}(不在注册表)")
            continue
        if mid in have and not args.replace:
            skipped.append(f"{mid}(已入库)")
            continue
        r = reg[mid]
        chunks = []
        for c in body["chunks"]:
            text = c.get("text", "")
            chunks.append({
                "id": c["id"], "module": mid,
                "section": c.get("section", ""),
                "text": text, "chars": len(text),
            })
        entry = {
            "id": mid, "slug": r["slug"], "milestone": mid,
            "title": r["title"], "tags": r.get("tags", []),
            "src": r.get("src", ""), "summary": r.get("summary", ""),
            "href": r.get("sim", ""), "pdf": r.get("note", ""),
            "chunks": chunks,
        }
        if mid in have:
            have[mid].update(entry)
            replaced.append(mid)
        else:
            kb["modules"].append(entry)
            have[mid] = entry
            added.append(mid)

    if args.check:
        missing = [parse_draft(p)[0] for p in drafts if parse_draft(p)[0] not in have]
        print(f"drafts={len(drafts)} 未入库={missing or '无'}")
        return 0 if not missing else 1

    # 按注册表顺序排序，保持 M0..M26,S7 之后追加新里程碑的稳定顺序
    order = {m: i for i, m in enumerate(reg)}
    kb["modules"].sort(key=lambda m: order.get(m["milestone"], 999))
    kb["chunk_count"] = sum(len(m["chunks"]) for m in kb["modules"])
    kb["char_count"] = sum(c["chars"] for m in kb["modules"] for c in m["chunks"])
    kb["built_at"] = datetime.now(timezone.utc).isoformat()
    KB_PATH.write_text(json.dumps(kb, ensure_ascii=False), encoding="utf-8")
    print(f"added={added or '无'} replaced={replaced or '无'} skipped={skipped or '无'}")
    print(f"KB: modules={len(kb['modules'])} chunks={kb['chunk_count']} chars={kb['char_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
