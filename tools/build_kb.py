#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_kb.py — build knowledge.json from the 9 chapter modules."""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = DATA / "knowledge.json"

MODULES_META = [
    {"slug": "00-binet", "milestone": "M0", "title": "比奈方程（现有样板）",
     "src": "中心力、比奈方程、圆锥曲线、进动",
     "tags": ["中心力", "比奈方程", "圆锥曲线", "进动"],
     "pdf": "modules/00-binet/binet.pdf", "tex": "modules/00-binet/binet.tex", "readme": None},
    {"slug": "01-effective-potential", "milestone": "M1", "title": "有效势与轨道稳定性",
     "src": "作业-2 Q1–Q7 · 作业-3 Q1 · 作业-5 Q4",
     "tags": ["有效势", "RK4", "Bertrand", "进动"],
     "pdf": "modules/01-effective-potential/note.pdf", "tex": "modules/01-effective-potential/note.tex",
     "readme": "modules/01-effective-potential/README.md"},
    {"slug": "02-scattering", "milestone": "M2", "title": "散射与俘获",
     "src": "作业-3 Q2–Q3",
     "tags": ["散射", "截面", "俘获", "RK4"],
     "pdf": "modules/02-scattering/note.pdf", "tex": "modules/02-scattering/note.tex",
     "readme": "modules/02-scattering/README.md"},
    {"slug": "03-two-body", "milestone": "M3", "title": "两体问题与系外行星",
     "src": "两体专题",
     "tags": ["两体", "RV", "多普勒", "系外行星"],
     "pdf": "modules/03-two-body/note.pdf", "tex": "modules/03-two-body/note.tex",
     "readme": "modules/03-two-body/README.md"},
    {"slug": "04-variational", "milestone": "M4", "title": "变分原理与等时摆",
     "src": "作业-6",
     "tags": ["变分", "费马", "等时摆", "Snell"],
     "pdf": "modules/04-variational/note.pdf", "tex": "modules/04-variational/note.tex",
     "readme": "modules/04-variational/README.md"},
    {"slug": "05-virtual-work", "milestone": "M5", "title": "虚功原理与静力学",
     "src": "作业-7",
     "tags": ["虚功", "静力学", "梯子", "平衡"],
     "pdf": "modules/05-virtual-work/note.pdf", "tex": "modules/05-virtual-work/note.tex",
     "readme": "modules/05-virtual-work/README.md"},
    {"slug": "06-collisions", "milestone": "M6", "title": "碰撞与变质量",
     "src": "作业-5 Q1–Q3",
     "tags": ["碰撞", "变质量", "恢复系数", "雨滴"],
     "pdf": "modules/06-collisions/note.pdf", "tex": "modules/06-collisions/note.tex",
     "readme": "modules/06-collisions/README.md"},
    {"slug": "07-rigid-body", "milestone": "M7", "title": "刚体几何与角动量",
     "src": "作业-4",
     "tags": ["刚体", "角动量", "球壳", "质心"],
     "pdf": "modules/07-rigid-body/note.pdf", "tex": "modules/07-rigid-body/note.tex",
     "readme": "modules/07-rigid-body/README.md"},
    {"slug": "08-kinematics", "milestone": "M8", "title": "运动学与非线性振动",
     "src": "作业-1",
     "tags": ["运动学", "振动", "Lorentz", "脱离"],
     "pdf": "modules/08-kinematics/note.pdf", "tex": "modules/08-kinematics/note.tex",
     "readme": "modules/08-kinematics/README.md"},
]


def strip_comment(line: str) -> str:
    # remove from first unescaped %
    idx = line.find("%")
    if idx >= 0:
        line = line[:idx]
    return line


def clean_inline(s: str) -> str:
    s = re.sub(r"\\(label|cite|ref|eqref)\{([^}]*)\}", r"\2", s)
    s = re.sub(r"\\frac\{([^{}]*)\}\{([^{}]*)\}", r"(\1)/(\2)", s)
    for cmd in ("vec", "mathbf", "boldsymbol", "mathrm", "textbf", "text",
                "mathit", "mathcal", "operatorname"):
        s = re.sub(r"\\" + cmd + r"\{([^}]*)\}", r"\1", s)
    s = s.replace("\\,", " ").replace("\\;", " ").replace("\\!", " ")
    s = s.replace("\\quad", " ").replace("\\qquad", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def clean_text_block(lines: list[str]) -> str:
    out = []
    for line in lines:
        line = strip_comment(line)
        if re.match(r"\s*\\(begin|end)\{", line):
            continue
        line = re.sub(r"\\(label|cite|ref|eqref)\{([^}]*)\}", r"\2", line)
        line = re.sub(r"\\frac\{([^{}]*)\}\{([^{}]*)\}", r"(\1)/(\2)", line)
        for cmd in ("vec", "mathbf", "boldsymbol", "mathrm", "textbf", "text",
                    "mathit", "mathcal", "operatorname"):
            line = re.sub(r"\\" + cmd + r"\{([^}]*)\}", r"\1", line)
        line = line.replace("\\,", " ").replace("\\;", " ").replace("\\!", " ")
        line = line.replace("\\quad", " ").replace("\\qquad", " ")
        line = re.sub(r"\s+", " ", line).strip()
        out.append(line)
    return "\n".join(out)


def parse_sections(tex_text: str) -> list[dict]:
    sections = []
    current = None
    for raw in tex_text.splitlines():
        line = strip_comment(raw)
        m = re.search(r"\\(section|subsection|subsubsection)\*?\{([^}]*)\}", line)
        if m:
            if current is not None:
                sections.append(current)
            current = {"level": m.group(1), "title": clean_inline(m.group(2)), "lines": []}
            continue
        if current is not None:
            if re.match(r"\s*\\(begin|end)\{", line):
                continue
            current["lines"].append(raw)
    if current is not None:
        sections.append(current)
    return sections


def chunk_paragraphs(text: str) -> list[str]:
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks = []
    cur = ""
    for p in paras:
        if cur and len(cur) + len(p) + 2 > 1400:
            if len(cur) >= 600 or not chunks:
                chunks.append(cur)
                cur = p
            else:
                cur = cur + "\n\n" + p
        else:
            cur = (cur + "\n\n" + p).strip() if cur else p
    if cur.strip():
        chunks.append(cur.strip())
    if not chunks and text.strip():
        chunks = [text.strip()]
    return chunks


def first_sentences(text: str, n: int = 2) -> str:
    # split on Chinese/Western sentence terminators
    parts = re.split(r"(?<=[。！？.!?])\s*", text.strip())
    parts = [p for p in parts if p.strip()]
    out = "".join(parts[:n])
    if out and not out.endswith(("。", "！", "？", ".", "!", "?")):
        out += "。"
    return out


def first_blockquote(readme_text: str) -> str:
    lines = []
    in_bq = False
    for line in readme_text.splitlines():
        s = line.strip()
        if s.startswith(">"):
            in_bq = True
            lines.append(s.lstrip(">").strip())
        else:
            if in_bq and s == "":
                break
            if in_bq and not s.startswith(">"):
                break
    return " ".join(lines)


def extract_section(readme_text: str, heading: str) -> str:
    lines = readme_text.splitlines()
    out = []
    in_sec = False
    for line in lines:
        s = line.strip()
        if s.startswith("## "):
            if in_sec:
                break
            if heading in s:
                in_sec = True
                continue
            continue
        if in_sec:
            out.append(s)
    return " ".join(out)


def clean_markdown(s: str) -> str:
    s = re.sub(r"\|", " ", s)
    s = re.sub(r"`+", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def readme_overview(readme_text: str) -> str:
    bq = first_blockquote(readme_text)
    model = extract_section(readme_text, "物理模型")
    model = clean_markdown(model)
    combined = (bq + "\n\n" + model).strip()
    combined = re.sub(r"\s+", " ", combined).strip()
    if len(combined) > 1400:
        combined = combined[:1400].rstrip() + "…"
    return combined


def abstract_text(tex_text: str) -> str:
    m = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", tex_text, re.S)
    if not m:
        return ""
    t = clean_text_block(m.group(1).splitlines())
    t = re.sub(r"\s+", " ", t).strip()
    return t


def build_module(meta: dict) -> dict:
    slug = meta["slug"]
    milestone = meta["milestone"]
    tex_path = ROOT / meta["tex"]
    tex_text = tex_path.read_text(encoding="utf-8")

    # summary
    if meta["readme"]:
        readme_text = (ROOT / meta["readme"]).read_text(encoding="utf-8")
        bq = first_blockquote(readme_text)
        summary = first_sentences(clean_markdown(bq), 2)
        overview_text = readme_overview(readme_text)
    else:
        ab = abstract_text(tex_text)
        summary = first_sentences(ab, 2)
        overview_text = ab[:1400]

    # chunks from tex
    sections = parse_sections(tex_text)
    chunks = []
    idx = 0
    # overview chunk first
    if overview_text.strip():
        chunks.append({
            "id": f"{milestone}-{idx:03d}",
            "module": milestone,
            "section": "模块概览",
            "text": overview_text.strip(),
            "chars": len(overview_text.strip()),
        })
        idx += 1
    for sec in sections:
        body = clean_text_block(sec["lines"])
        body = body.strip()
        if not body:
            continue
        for piece in chunk_paragraphs(body):
            piece = piece.strip()
            if not piece:
                continue
            chunks.append({
                "id": f"{milestone}-{idx:03d}",
                "module": milestone,
                "section": sec["title"],
                "text": piece,
                "chars": len(piece),
            })
            idx += 1

    return {
        "id": milestone,
        "slug": slug,
        "milestone": milestone,
        "title": meta["title"],
        "tags": meta["tags"],
        "src": meta["src"],
        "summary": summary,
        "href": f"modules/{slug}/index.html",
        "pdf": meta["pdf"],
        "chunks": chunks,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--stats", action="store_true")
    args = ap.parse_args()

    if args.check:
        if not OUT.exists():
            print("KB missing:", OUT)
            return 1
        data = json.loads(OUT.read_text(encoding="utf-8"))
        mods = data.get("modules", [])
        cc = data.get("chunk_count", 0)
        ok = len(mods) == 9 and cc > 0
        print(f"modules={len(mods)} chunks={cc} chars={data.get('char_count')}")
        return 0 if ok else 1

    if args.stats:
        if not OUT.exists():
            print("KB missing")
            return 1
        data = json.loads(OUT.read_text(encoding="utf-8"))
        print(f"modules={len(data['modules'])} chunks={data['chunk_count']} chars={data['char_count']}")
        for m in data["modules"]:
            print(f"  {m['milestone']} {m['title']}: {len(m['chunks'])} chunks")
        return 0

    modules = [build_module(m) for m in MODULES_META]
    chunk_count = sum(len(m["chunks"]) for m in modules)
    char_count = sum(c["chars"] for m in modules for c in m["chunks"])
    data = {
        "version": 1,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "modules": modules,
        "chunk_count": chunk_count,
        "char_count": char_count,
    }
    DATA.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    print(f"modules={len(modules)} chunks={chunk_count} chars={char_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
