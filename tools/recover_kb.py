#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""recover_kb.py — 灾难恢复：从最新 neural 快照重建 data/knowledge.json。

正常管线方向是 knowledge.json → build_neural_data.py → neural/data.js。
若 knowledge.json 丢失或被遗留工具（build_kb.py 的 12 模块旧编号管线）覆盖回退，
本工具用 data/modules.json（注册表元信息）× neural/data.js（最新完整 chunk 快照）
反向重建 knowledge.json。

恢复后必须重跑 build_neural_data.py 并 diff data.js：diff 为空即证明往返一致。

用法：
  python3 tools/recover_kb.py            # 重建
  python3 tools/recover_kb.py --check    # 只校验现有 KB 是否覆盖注册表全部里程碑
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG_PATH = ROOT / "data" / "modules.json"
NEURAL_PATH = ROOT / "neural" / "data.js"
OUT = ROOT / "data" / "knowledge.json"


def load_neural_modules() -> dict:
    s = NEURAL_PATH.read_text(encoding="utf-8")
    i = s.find("{")
    j = s.rfind("}")
    if i < 0 or j < 0:
        raise SystemExit("recover_kb: neural/data.js 中找不到 JSON 载荷")
    return json.loads(s[i:j + 1])["modules"]


def registry() -> list[dict]:
    return json.loads(REG_PATH.read_text(encoding="utf-8"))["modules"]


def check() -> int:
    if not OUT.exists():
        print("recover_kb --check: knowledge.json 缺失")
        return 1
    kb = json.loads(OUT.read_text(encoding="utf-8"))
    have = {m["milestone"] for m in kb.get("modules", [])}
    want = [r["milestone"] for r in registry()]
    missing = [m for m in want if m not in have]
    cc = kb.get("chunk_count", 0)
    print(f"modules={len(have)}/{len(want)} chunks={cc} missing={missing or '无'}")
    return 0 if not missing and cc > 0 else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    if args.check:
        return check()

    neu = load_neural_modules()
    modules, missing = [], []
    for r in registry():
        mid = r["milestone"]
        n = neu.get(mid)
        if not n or not n.get("sections"):
            missing.append(mid)
            continue
        chunks = []
        for sec in n["sections"]:
            for c in sec.get("chunks", []):
                text = c.get("text", "")
                chunks.append({
                    "id": c["id"], "module": mid,
                    "section": sec.get("name", ""),
                    "text": text, "chars": len(text),
                })
        modules.append({
            "id": mid, "slug": r["slug"], "milestone": mid,
            "title": r["title"], "tags": r.get("tags", []),
            "src": r.get("src", ""), "summary": r.get("summary", ""),
            "href": n.get("href") or r.get("sim", ""),
            "pdf": n.get("pdf") or r.get("note", ""),
            "chunks": chunks,
        })
    if missing:
        print("recover_kb: 注册表模块在 neural 快照中缺失，拒绝写出不完整 KB:", missing)
        return 1
    cc = sum(len(m["chunks"]) for m in modules)
    ch = sum(c["chars"] for m in modules for c in m["chunks"])
    data = {
        "version": 1,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "modules": modules,
        "chunk_count": cc,
        "char_count": ch,
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    print(f"recovered: modules={len(modules)} chunks={cc} chars={ch}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
