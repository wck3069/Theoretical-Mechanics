#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""apply_seo.py — inject idempotent SEO metadata and write sitemap/robots."""
from __future__ import annotations

import html
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://wck3069.github.io/Theoretical-Mechanics"
SITE = "理论力学：从质点到哈密顿"
IMAGE = BASE + "/assets/og-cover.png"
START = "<!-- TM-SEO:START -->"
END = "<!-- TM-SEO:END -->"
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.DOTALL | re.IGNORECASE)
BLOCK_RE = re.compile(re.escape(START) + r".*?" + re.escape(END), re.DOTALL)
KB_RE = re.compile(r'(<script id="tm-offline-kb">\n).*?(\n</script>)', re.DOTALL)


def site_stats() -> tuple[int, int, int]:
    """从数据源动态读取章数、单元数、跨章关联数。"""
    def load(name: str) -> dict:
        return json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))

    chapters = len(load("chapters.json")["chapters"])
    modules = len(load("modules.json")["modules"])
    links = len(load("links.json")["links"])
    return chapters, modules, links


CHAPTER_COUNT, MODULE_COUNT, LINK_COUNT = site_stats()


def lastmod() -> str:
    """sitemap 的 lastmod：git 最新提交日期，失败则回退当天日期。"""
    try:
        out = subprocess.run(
            ["git", "-C", str(ROOT), "log", "-1", "--date=short", "--format=%cd"],
            capture_output=True, text=True, timeout=10, check=True,
        ).stdout.strip()
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", out):
            return out
    except (OSError, subprocess.SubprocessError):
        pass
    return datetime.now().strftime("%Y-%m-%d")


def pages() -> list[Path]:
    out = [ROOT / "index.html", ROOT / "catalog.html", ROOT / "binet.html"]
    out += sorted((ROOT / "chapters").glob("*/index.html"))
    out += sorted((ROOT / "chapters").glob("*/manuscripts/*.html"))
    out += sorted((ROOT / "modules").glob("*/index.html"))
    return [p for p in out if p.is_file()]


def title_of(text: str, path: Path) -> str:
    m = TITLE_RE.search(text)
    if not m:
        return path.stem
    title = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(1))).strip()
    return html.unescape(title)


def description(path: Path, title: str) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return (f"理论力学交互讲义：从质点到哈密顿。{CHAPTER_COUNT} 章星图导航、"
                f"{MODULE_COUNT} 个交互与知识单元、{LINK_COUNT} 条跨章知识关联，"
                f"含手写书稿 HTML 版与本地 AI 助教。")
    if rel == "catalog.html":
        return (f"理论力学站点目录：{CHAPTER_COUNT} 章、{MODULE_COUNT} 个交互与知识单元、"
                f"{LINK_COUNT} 条跨章知识关联，附手写书稿与作业页。")
    if rel == "binet.html":
        return "比奈方程专题页：中心力、圆锥曲线、轨道进动与交互演示。"
    if "/manuscripts/" in rel:
        return f"{title}：手写手稿 HTML 版，MathJax 本地渲染，含 SVG 插图。"
    if rel.startswith("modules/"):
        return f"{title}：可拖拽交互演示、公式推导与数值自测。"
    return f"{title}：章节导读、交互模块与手写手稿入口。"


def block(path: Path, text: str) -> str:
    rel = path.relative_to(ROOT).as_posix()
    url = BASE + ("/" if rel == "index.html" else "/" + rel)
    title = html.unescape(title_of(text, path))
    desc = html.unescape(description(path, title))
    og_type = "article" if (rel.startswith("modules/") or "/manuscripts/" in rel) else "website"
    vals = {
        "title": html.escape(title, quote=True),
        "desc": html.escape(desc, quote=True),
        "url": html.escape(url, quote=True),
        "image": html.escape(IMAGE, quote=True),
        "site": html.escape(SITE, quote=True),
    }
    return "\n".join([
        START,
        f'<meta name="description" content="{vals["desc"]}">',
        f'<meta name="author" content="wck3069">',
        f'<meta name="theme-color" content="#05060f">',
        f'<link rel="canonical" href="{vals["url"]}">',
        f'<meta property="og:type" content="{og_type}">',
        f'<meta property="og:site_name" content="{vals["site"]}">',
        f'<meta property="og:title" content="{vals["title"]}">',
        f'<meta property="og:description" content="{vals["desc"]}">',
        f'<meta property="og:url" content="{vals["url"]}">',
        f'<meta property="og:image" content="{vals["image"]}">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        f'<meta property="og:image:alt" content="{vals["site"]}">',
        '<meta property="og:locale" content="zh_CN">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{vals["title"]}">',
        f'<meta name="twitter:description" content="{vals["desc"]}">',
        f'<meta name="twitter:image" content="{vals["image"]}">',
        END,
    ])


def sync_inline_kb() -> None:
    index = ROOT / "index.html"
    kb = ROOT / "assets" / "tm-offline-kb.js"
    if not index.is_file() or not kb.is_file():
        return
    text = index.read_text(encoding="utf-8")
    payload = kb.read_text(encoding="utf-8").rstrip("\n")
    new = KB_RE.sub(lambda m: m.group(1) + payload + m.group(2), text, count=1)
    if new != text:
        index.write_text(new, encoding="utf-8")


def main() -> int:
    sync_inline_kb()
    items = pages()
    for path in items:
        text = path.read_text(encoding="utf-8")
        new = block(path, text)
        if BLOCK_RE.search(text):
            text = BLOCK_RE.sub(new, text, count=1)
        elif "</head>" in text:
            text = text.replace("</head>", new + "\n</head>", 1)
        else:
            print("SKIP (no </head>):", path)
            continue
        path.write_text(text, encoding="utf-8")

    mod = lastmod()
    urls = []
    for path in items:
        rel = path.relative_to(ROOT).as_posix()
        loc = BASE + ("/" if rel == "index.html" else "/" + rel)
        urls.append("  <url><loc>%s</loc><lastmod>%s</lastmod></url>" % (html.escape(loc), mod))
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls) + "\n</urlset>\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n" % BASE, encoding="utf-8")
    print("pages=%d sitemap=%d" % (len(items), len(urls)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
