#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""build_web_reader.py — render the LaTeX sources as site-styled HTML readers.

Sources:
  manuscript/chapters/ch01..ch07.tex  -> chapters/<slug>/manuscripts/book.html
  modules/*/note.tex                  -> modules/<dir>/note.html
  modules/00-binet/binet.tex          -> modules/00-binet/binet.html

Math stays TeX and is rendered by the local MathJax. TikZ pictures are
compiled to SVG. Numbered equations get a tag (chapter.section style for the
book, plain 1,2,3 for module notes) and \eqref / \ref{eq:...} become text.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PANDOC = shutil.which("pandoc") or str(Path.home() / "bin" / "pandoc")

CHAPTERS = [
    ("ch01", "01-newton"),
    ("ch02", "02-variational"),
    ("ch03", "03-lagrangian"),
    ("ch04", "04-oscillations"),
    ("ch05", "05-rigid-body"),
    ("ch06", "06-hamiltonian"),
    ("ch07", "07-relativity"),
]
MODULE_TITLES = {
    "00-binet": ("比奈方程", "binet"),
    "01-effective-potential": ("有效势与轨道稳定性", "note"),
    "02-scattering": ("散射与俘获", "note"),
    "03-two-body": ("两体问题与系外行星", "note"),
    "04-variational": ("变分原理与等时摆", "note"),
    "05-virtual-work": ("虚功原理与静力学", "note"),
    "06-collisions": ("碰撞与变质量", "note"),
    "07-rigid-body": ("刚体几何与角动量", "note"),
    "08-kinematics": ("运动学与质点动力学", "note"),
    "09-atwood-pulley": ("有转动惯量的 Atwood 机", "note"),
    "10-coupled-systems": ("耦合系统与小振动", "note"),
    "11-rotation-and-field": ("旋转参考系与磁场", "note"),
}

ENV_RE = re.compile(
    r"\\begin\{(equation|align|align\*|gather|gather\*|multline|multline\*|eqnarray|eqnarray\*)\}(.*?)\\end\{\1\}",
    re.S,
)
LABEL_RE = re.compile(r"\\label\{([^}]+)\}")
TITLE_RE = re.compile(r"\\title\{((?:[^{}]|\{[^{}]*\})*)\}")
ABSTRACT_RE = re.compile(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", re.S)
CHAPTER_RE = re.compile(r"\\chapter\*?\{((?:[^{}]|\{[^{}]*\})*)\}")
HEADING_RE = re.compile(r"<h([1-4])([^>]*)>(.*?)</h\1>", re.S)
TAG_RE = re.compile(r"<[^>]+>")
TCOLBOX_TITLE_RE = re.compile(r"\\begin\{tcolorbox\}\[([^\]]*?)\]", re.S)
TITLE_OPT_RE = re.compile(r"title=\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}")


def strip_tex(text: str) -> str:
    text = re.sub(r"\\(textbf|textit|emph|mathrm|text|mathbf|operatorname)\{([^{}]*)\}", r"\2", text)
    text = re.sub(r"\$[^$]*\$", "", text)
    text = re.sub(r"\\[a-zA-Z]+\*?", "", text)
    text = text.replace("{", "").replace("}", "").replace("~", " ")
    return re.sub(r"\s+", " ", text).strip()


def number_equations(tex: str, prefix: str | None) -> tuple[str, dict[str, str]]:
    labels: dict[str, str] = {}
    counter = [0]

    def repl(m: re.Match) -> str:
        env, content = m.group(1), m.group(2)
        if env.endswith("*"):
            return "\\begin{%s}%s\\end{%s}" % (env, LABEL_RE.sub("", content), env)
        counter[0] += 1
        num = f"{prefix}.{counter[0]}" if prefix else str(counter[0])
        for lab in LABEL_RE.findall(content):
            labels[lab] = num
        content = LABEL_RE.sub("", content)
        content = re.sub(r"\\(nonumber|notag)\b", "", content)
        if env == "equation":
            return "\\begin{equation}" + content + "\\tag{" + num + "}\\end{equation}"
        inner = "aligned" if env.startswith("align") or env.startswith("eqnarray") else "gathered"
        return "\\begin{equation}\\begin{%s}%s\\end{%s}\\tag{%s}\\end{equation}" % (inner, content, inner, num)

    tex = ENV_RE.sub(repl, tex)

    def ref_repl(m: re.Match) -> str:
        lab = m.group(2)
        if lab not in labels:
            return "\\ref{%s}" % lab if m.group(1) == "eqref" else m.group(0)
        return f"({labels[lab]})" if m.group(1) == "eqref" else labels[lab]

    tex = re.sub(r"\\(eqref|ref)\{([^}]+)\}", ref_repl, tex)
    return tex, labels


def compile_tikz(preamble: str, tikz: str, out_svg: Path) -> bool:
    out_svg.parent.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha1((preamble + tikz).encode("utf-8")).hexdigest()[:16]
    cache = out_svg.parent / (".cache-" + key + ".svg")
    if cache.exists():
        shutil.copyfile(cache, out_svg)
        return True
    pre = preamble
    pre = re.sub(r"\\documentclass(?:\[[^\]]*\])?\{[^}]*\}", "\\\\documentclass[border=3pt]{standalone}\\n\\\\usepackage[UTF8]{ctex}\\n\\\\newcounter{chapter}", pre, count=1)
    pre = re.sub(r"\\setCJK[^\n]*\n", "", pre)
    pre = re.sub(r"\\ctexset\{.*?\n\}\n", "", pre, flags=re.S)
    doc = pre + "\n\\begin{document}\n" + tikz + "\n\\end{document}\n"
    with tempfile_dir(out_svg.parent) as td:
        tex = Path(td) / "fig.tex"
        tex.write_text(doc, encoding="utf-8")
        data_dir = ROOT / "manuscript" / "figures"
        if data_dir.is_dir():
            shutil.copytree(data_dir, Path(td) / "figures", dirs_exist_ok=True)
        r = subprocess.run(
            ["xelatex", "-interaction=nonstopmode", "-halt-on-error", "fig.tex"],
            cwd=td, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        )
        pdf = Path(td) / "fig.pdf"
        if not pdf.exists():
            print("  ! tikz compile failed:", tikz[:60].replace("\n", " "), file=sys.stderr)
            return False
        subprocess.run(["pdftocairo", "-svg", str(pdf), str(cache)], check=True)
    shutil.copyfile(cache, out_svg)
    return True


class tempfile_dir:
    def __init__(self, base: Path):
        self.base = base

    def __enter__(self) -> str:
        self.path = self.base / ".tikz-tmp"
        if self.path.exists():
            shutil.rmtree(self.path)
        self.path.mkdir(parents=True)
        return str(self.path)

    def __exit__(self, *exc) -> None:
        shutil.rmtree(self.path, ignore_errors=True)


def convert_tikz(tex: str, preamble: str, fig_dir: Path, slug: str) -> str:
    count = [0]

    def repl(m: re.Match) -> str:
        tikz = m.group(0)
        count[0] += 1
        svg = fig_dir / f"{slug}-fig{count[0]}.svg"
        if not compile_tikz(preamble, tikz, svg):
            return ""
        return "\\includegraphics[width=0.86\\linewidth]{" + f"figs/{svg.name}" + "}"

    return re.sub(r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}", repl, tex, flags=re.S)


def pandoc_fragment(tex_path: Path, workdir: Path) -> str:
    out = workdir / ".body.html"
    r = subprocess.run(
        [PANDOC, str(tex_path), "-f", "latex", "-t", "html5", "--mathjax", "--wrap=none", "-o", str(out)],
        cwd=workdir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )
    if r.returncode != 0 or not out.exists():
        raise RuntimeError(f"pandoc failed for {tex_path}:\n{r.stdout[-2000:]}")
    body = out.read_text(encoding="utf-8")
    out.unlink()
    return body


def shift_headings(body: str) -> str:
    def repl(m: re.Match) -> str:
        level = min(5, int(m.group(1)) + 1)
        return f"<h{level}{m.group(2)}>{m.group(3)}</h{level}>"
    return HEADING_RE.sub(repl, body)



def starred_titles(tex: str) -> set[str]:
    out = set()
    for m in re.finditer(r"\\(?:section|subsection|subsubsection)\*\{((?:[^{}]|\{[^{}]*\})*)\}", tex):
        out.add(re.sub(r"\s+", "", strip_tex(m.group(1))))
    return out


def number_sections(body: str, starred: set[str], chapter: str | None) -> str:
    h2 = h3 = 0
    unnumbered = False

    def repl(m: re.Match) -> str:
        nonlocal h2, h3, unnumbered
        level, attrs, inner = int(m.group(1)), m.group(2), m.group(3)
        text = re.sub(r"\s+", "", strip_tex(TAG_RE.sub("", inner)))
        if level == 2:
            if text in starred:
                unnumbered = True
                return m.group(0)
            unnumbered = False
            h2 += 1
            h3 = 0
            num = f"{chapter}.{h2}" if chapter else str(h2)
        elif level == 3:
            if unnumbered:
                return m.group(0)
            h3 += 1
            num = f"{chapter}.{h2}.{h3}" if chapter else f"{h2}.{h3}"
        else:
            return m.group(0)
        return f'<h{level}{attrs}><span class="ms-secno">{num}</span>{inner}</h{level}>'

    return HEADING_RE.sub(repl, body)


def make_toc(body: str) -> str:
    items = []
    for m in HEADING_RE.finditer(body):
        level, attrs, inner = int(m.group(1)), m.group(2), m.group(3)
        if level > 3:
            continue
        idm = re.search(r'id="([^"]+)"', attrs)
        if not idm:
            continue
        text = html.unescape(TAG_RE.sub("", inner))
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            continue
        if len(text) > 54:
            text = text[:53] + "…"
        items.append(f'<li class="l{level}"><a href="#{idm.group(1)}">{html.escape(text)}</a></li>')
    return "\n".join(items)



ENV_TITLES = {
    "physicsbox": "物理图像与理解 · PHYSICAL INSIGHT",
    "keybox": "核心结论 · KEY RESULT",
    "mathbox": "数学注记 · MATH NOTE",
    "modernbox": "进一步探索 · FURTHER",
}


def add_env_titles(body: str) -> str:
    for cls, title in ENV_TITLES.items():
        body = body.replace(
            f'<div class="{cls}">',
            f'<div class="{cls}"><div class="ms-callout-title">{html.escape(title)}</div>',
        )
    return body


def add_box_titles(body: str, titles: list[str]) -> str:
    it = iter(titles)

    def repl(m: re.Match) -> str:
        try:
            t = next(it)
        except StopIteration:
            return m.group(0)
        return m.group(0) + f'<div class="ms-callout-title">{html.escape(t)}</div>'

    return re.sub(r'<div class="tcolorbox">', repl, body)


def page_shell(*, title: str, lead: str, eyebrow: str, body: str, toc: str,
               assets: str, nav: list[tuple[str, str]], links: list[tuple[str, str]],
               footer_left: str, footer_right: str) -> str:
    nav_html = "".join(f'<a href="{html.escape(h)}">{html.escape(t)}</a>' for h, t in nav)
    links_html = ""
    if links:
        links_html = '<div class="ms-links"><b>相关</b>' + "".join(
            f'<a href="{html.escape(h)}">{html.escape(t)}</a>' for h, t in links
        ) + "</div>"
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)} · 理论力学</title>
<link rel="stylesheet" href="{assets}/manuscript.css">
<link rel="stylesheet" href="{assets}/ui-liquid.css">
<script>
window.MathJax={{tex:{{inlineMath:[['$','$'],['\\\\(','\\\\)']],displayMath:[['$$','$$'],['\\\\[','\\\\]']],tags:'ams'}},svg:{{fontCache:'local'}}}};
</script>
</head>
<body class="ms-reader ms-generated">
<header class="ms-header"><div class="in">
<a class="ms-brand" href="{assets}/../index.html">✦ 理论力学</a>
<nav class="ms-nav">{nav_html}</nav>
</div></header>
<main class="ms-wrap">
<div class="ms-hero">
<div class="ms-eyebrow">{html.escape(eyebrow)}</div>
<h1>{html.escape(title)}</h1>
<p class="ms-lead">{html.escape(lead)}</p>
{links_html}
</div>
<div class="ms-shell">
<nav class="ms-toc" id="ms-toc" aria-label="目录">
<details open><summary>目录</summary>
<ul>
{toc}
</ul>
</details>
</nav>
<article class="ms-body">
{body}
</article>
</div>
</main>
<footer class="ms-footer"><span>{html.escape(footer_left)}</span><span>{footer_right}</span></footer>
<script src="{assets}/manuscript-nav.js"></script>
<script src="{assets}/tm-i18n-data.js"></script>
<script src="{assets}/tm-i18n.js"></script>
<script src="{assets}/mathjax/tex-svg.js"></script>
<script src="{assets}/ui-motion.js" defer></script>
</body>
</html>
"""


def build_note(dirname: str, assets: str) -> None:
    mod = ROOT / "modules" / dirname
    label, stem = MODULE_TITLES[dirname]
    src = mod / f"{stem}.tex"
    tex = src.read_text(encoding="utf-8")
    title_m = TITLE_RE.search(tex)
    title = strip_tex(title_m.group(1)) if title_m else label
    abs_m = ABSTRACT_RE.search(tex)
    lead = strip_tex(abs_m.group(1)) if abs_m else f"{label} · 网页阅读版，可直接阅读与复制公式。"
    if len(lead) > 220:
        lead = lead[:219] + "…"
    tex = tex.replace("\\boldsymbol", "\\mathbf").replace("\\bm", "\\mathbf")
    tex, _ = number_equations(tex, None)
    tmp = mod / ".webreader.tex"
    tmp.write_text(tex, encoding="utf-8")
    try:
        body = pandoc_fragment(tmp, mod)
    finally:
        tmp.unlink(missing_ok=True)
    body = shift_headings(body)
    body = number_sections(body, set(), None)
    toc = make_toc(body)
    out = mod / f"{stem}.html"
    nav = [("index.html", "← 模拟页"), ("../../manuscript/index.html", "书稿"), ("../../index.html", "星图")]
    out.write_text(page_shell(
        title=title, lead=lead, eyebrow="推导 · 网页阅读版",
        body=body, toc=toc, assets=assets,
        nav=nav, links=[("index.html", f"{label} 模拟")],
        footer_left=f"{title} · 网页阅读版",
        footer_right='<a href="index.html">返回模拟</a>',
    ), encoding="utf-8")
    print("wrote", out.relative_to(ROOT), f"({out.stat().st_size/1024:.0f} KB)")


def build_chapter(ch: str, slug: str) -> None:
    main_tex = (ROOT / "manuscript" / "main.tex").read_text(encoding="utf-8")
    pre = main_tex[: main_tex.index("\\begin{document}")]
    src = ROOT / "manuscript" / "chapters" / f"{ch}.tex"
    raw = src.read_text(encoding="utf-8")
    title_m = CHAPTER_RE.search(raw)
    title = strip_tex(title_m.group(1)) if title_m else slug
    chapter_no = str(int(ch[2:]))
    fig_dir = ROOT / "chapters" / slug / "manuscripts" / "figs"
    body_tex = convert_tikz(raw, pre, fig_dir, ch)
    body_tex = body_tex.replace("\\boldsymbol", "\\mathbf").replace("\\bm", "\\mathbf")
    body_tex, _ = number_equations(body_tex, chapter_no)
    body_tex = re.sub(r"\\begin\{tcolorbox\}\[[^\]]*\]", "\\\\begin{tcolorbox}", body_tex)
    box_titles = []
    for m in TCOLBOX_TITLE_RE.finditer(raw):
        tm = TITLE_OPT_RE.search(m.group(1))
        if tm:
            box_titles.append(strip_tex(tm.group(1)))
    tmp_dir = ROOT / "chapters" / slug / "manuscripts"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp = tmp_dir / ".webreader.tex"
    combined = (pre + "\\begin{document}\n" + body_tex + "\n\\end{document}\n").replace("\\boldsymbol", "\\mathbf").replace("\\bm", "\\mathbf")
    tmp.write_text(combined, encoding="utf-8")
    try:
        body = pandoc_fragment(tmp, tmp_dir)
    finally:
        tmp.unlink(missing_ok=True)
    body = re.sub(r'^<h1[^>]*>.*?</h1>\s*', "", body, count=1, flags=re.S)
    body = number_sections(body, starred_titles(raw), chapter_no)
    body = add_env_titles(body)
    body = add_box_titles(body, box_titles)
    toc = make_toc(body)
    out = tmp_dir / "book.html"
    assets = "../../../assets"
    out.write_text(page_shell(
        title=title, lead="本章书稿全文，可检索、可复制。",
        eyebrow="书稿 · 网页阅读版",
        body=body, toc=toc, assets=assets,
        nav=[("../index.html", "← 章节门户"), ("../../../manuscript/index.html", "书稿"), ("../../../index.html", "星图")],
        links=[("../index.html", f"{title} 章节")],
        footer_left=f"{title} · 书稿网页版",
        footer_right='<a href="../index.html">返回章节</a>',
    ), encoding="utf-8")
    print("wrote", out.relative_to(ROOT), f"({out.stat().st_size/1024:.0f} KB)")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="", help="only one module dir / chapter slug")
    args = ap.parse_args()
    if not Path(PANDOC).exists():
        sys.exit(f"pandoc not found at {PANDOC}")
    only = args.only
    for dirname, (_, stem) in MODULE_TITLES.items():
        if only and only not in (dirname, stem):
            continue
        if (ROOT / "modules" / dirname / f"{stem}.tex").exists():
            build_note(dirname, "../../assets")
    for ch, slug in CHAPTERS:
        if only and only not in (ch, slug):
            continue
        build_chapter(ch, slug)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
