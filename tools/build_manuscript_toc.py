#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_manuscript_toc.py — rebuild the semantic sidebar TOC of the manuscript pages.

Usage:
  python3 tools/build_manuscript_toc.py            # rebuild all four manuscripts
  python3 tools/build_manuscript_toc.py <file...>  # rebuild specific files

What it does, per manuscript (idempotent via the MS-TOC markers):
  1. Removes the legacy page-number TOC (<div class="ms-toc">第 N 页...</div>).
  2. Builds a static TOC from the h3/h4 headings of every
     <section class="ms-page" id="pN"> and writes it as
     <!-- MS-TOC:START --> <nav class="ms-toc"> ... <!-- MS-TOC:END -->
     wrapped together with <article class="ms-body"> inside <div class="ms-shell">
     (left sticky sidebar + right reading column).
  3. Demotes the loud <h2>第 N 页</h2> page headings to a de-emphasized
     marker <h2><span class="ms-pn">p.N</span></h2>. Content and anchors stay.

Heading-inclusion policy (per section, in document order):
  * every h3 whose cleaned label is not generic;
  * an h4 whose cleaned label is not generic AND either
      (a) the label starts with a section number like 2.2 / 1.9 / 3.1
          (regex ^\\d+(\\.\\d+)+), or
      (b) the section has no included h3 and this is the section's first
          non-generic heading;
  * cleaning: first remove <a class="ms-demo">…</a> chips, then strip tags,
    strip "交互演示", convert inline $...$ math to plain text, collapse
    spaces, cap length at 40 chars;
  * generic labels are skipped: 例/例题/解/证明/答/注意 (+optional number or
    letter tail), (a)…(h), 1. 2. … 10. / (1) / 1) / 3、, 0, 4, 21, 1.5, pure
    punctuation, bare 二…, 无扰动时, 存在势能修正时;
  * display depth is numbering-based: a label starting with a dotted number
    (^\d+(\.\d+)+) is l4, or l5 when the number holds >=2 dots (1.9.6);
    otherwise h3 -> l3, h4 -> l4;
  * a label starting with an OVERRIDES prefix is replaced in the TOC only
    (the article heading is never changed);
  * every link gets title="full cleaned label (untruncated)";
  * duplicate labels (punctuation-normalized, e.g. "4 编程题:" == "4 编程题：")
    within the last 5 emitted entries are skipped;
  * included headings get a stable id (pN-h3-K / pN-h4-K, K per level in the
    section) if they have none; existing ids are kept.
  * TOC hrefs target the heading id; h4 entries (l4) indent under h3 (l3).
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FILES = [
    "chapters/01-particle/manuscripts/intro.html",
    "chapters/01-particle/manuscripts/hw1.html",
    "chapters/02-system/manuscripts/chapter2.html",
    "chapters/03-variational/manuscripts/variational.html",
]

START = "<!-- MS-TOC:START -->"
END = "<!-- MS-TOC:END -->"

SECTION_RE = re.compile(r'<section class="ms-page" id="(p\d+)">(.*?)</section>', re.S)
HEAD_RE = re.compile(r"<(h[34])([^>]*)>(.*?)</\1>", re.S)
HEAD_OPEN_RE = re.compile(r"<(h[34])([^>]*)>")
ID_RE = re.compile(r'id="([^"]+)"')
TAG_RE = re.compile(r"<[^>]+>")
OLD_TOC_RE = re.compile(r'[ \t]*<div class="ms-toc">.*?</div>\s*\n?', re.S)
MARKED_RE = re.compile(re.escape(START) + r".*?" + re.escape(END) + r"\s*\n?", re.S)
PAGE_H2_RE = re.compile(r"<h2>第 (\d+) 页</h2>")
MATH_RE = re.compile(r"\$([^$]*)\$")
NUMBERED_RE = re.compile(r"\d+(\.\d+)+")
DEMO_A_RE = re.compile(r'<a class="ms-demo"[^>]*>.*?</a>', re.S)
DOTTED_RE = re.compile(r"\d+(?:\.\d+)+")
OVERRIDES = [("2. 如下图所示", "2. 球沿水平面滑动（例题）")]

GREEK = {
    "alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "epsilon": "ε",
    "zeta": "ζ", "eta": "η", "theta": "θ", "kappa": "κ", "lambda": "λ",
    "mu": "μ", "nu": "ν", "xi": "ξ", "pi": "π", "rho": "ρ", "sigma": "σ",
    "tau": "τ", "upsilon": "υ", "phi": "φ", "chi": "χ", "psi": "ψ",
    "omega": "ω", "Gamma": "Γ", "Delta": "Δ", "Theta": "Θ", "Lambda": "Λ",
    "Pi": "Π", "Sigma": "Σ", "Phi": "Φ", "Psi": "Ψ", "Omega": "Ω",
    "infty": "∞", "partial": "∂", "nabla": "∇", "times": "×", "cdot": "·",
    "approx": "≈", "leq": "≤", "geq": "≥", "neq": "≠", "to": "→",
}
SUP = {"0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵",
       "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹", "n": "ⁿ"}

EXACT_GENERIC = {"无扰动时", "存在势能修正时"}


def math_to_text(match: re.Match) -> str:
    s = match.group(1)
    s = re.sub(r"\\[dt]?frac\{([^{}]*)\}\{([^{}]*)\}", r"(\1)/(\2)", s)
    s = re.sub(r"\\sqrt\{([^{}]*)\}", r"√(\1)", s)
    s = re.sub(r"\\(?:left|right|quad|,|;|!|:)", " ", s)
    s = re.sub(r"\\([A-Za-z]+)", lambda m: GREEK.get(m.group(1), " " + m.group(1) + " "), s)
    s = re.sub(r"\^\{?([0-9n])\}?", lambda m: SUP.get(m.group(1), "^" + m.group(1)), s)
    s = re.sub(r"_\{?[A-Za-z0-9]+\}?", "", s)
    s = re.sub(r"[{}\\]", "", s)
    return s


def is_generic(label: str) -> bool:
    t = label.strip()
    if not t:
        return True
    if re.fullmatch(r"[\s.。,、;；:：!！?？()（）\[\]【】<>《》\-–—~/\\+*#@%&'\"`^=|]+", t):
        return True
    if re.fullmatch(r"\d+(?:\.\d+)*[.。]?", t):  # 0, 4, 21, 1.5, 10.
        return True
    if re.fullmatch(r"[一二三四五六七八九十百千]+", t):
        return True
    if re.fullmatch(r"(?:例|例题|解|证明|证|答|注意)(?:\s*\d*)?(?:\s*[.。:：]|\s*\(?[a-hA-H]\)?)?", t):
        return True  # 例, 例1, 解, 解:, 解2., 解 (a)
    if re.fullmatch(r"\(?\s*[a-hA-H]\s*[\)）.。]?", t):  # (a)…(h), a), b.
        return True
    if re.fullmatch(r"\(?\s*\d{1,2}\s*[.。、\)）]", t):  # 1., (1), 1), 3、
        return True
    return t in EXACT_GENERIC


def clean_label(raw: str, cap: int = 40) -> str:
    s = DEMO_A_RE.sub(" ", raw)
    s = html.unescape(s)
    s = TAG_RE.sub(" ", s)
    s = MATH_RE.sub(math_to_text, s)
    s = s.replace("交互演示", " ")
    s = re.sub(r"\s+", " ", s).strip()
    s = s.replace("--", "–")
    s = s.rstrip(" .,、;:;")
    if cap and len(s) > cap:
        s = s[:cap].rstrip(" ,、（(【[") + "…"
    return s


def toc_level(tag_level: int, label: str) -> int:
    m = DOTTED_RE.match(label)
    if m:
        return 5 if m.group(0).count(".") >= 2 else 4
    return tag_level


def dedup_key(label: str) -> str:
    return re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+", "", label).lower()


def plan_section(sid: str, body: str) -> list[tuple]:
    """Per h3/h4: (index, level, existing_id, label, included, anchor, toc_level)."""
    heads = HEAD_RE.findall(body)
    plans = []
    first_nongeneric_idx = None
    for i, (tag, attrs, inner) in enumerate(heads):
        full = clean_label(inner, cap=0)
        label = full
        for pref, rep in OVERRIDES:
            if full.startswith(pref):
                label = rep
                break
        if len(label) > 40:
            label = label[:40].rstrip(" ,、（(【[") + "…"
        idm = ID_RE.search(attrs)
        if not is_generic(label) and first_nongeneric_idx is None:
            first_nongeneric_idx = i
        plans.append((i, int(tag[1]), idm.group(1) if idm else None, label, full))
    has_h3 = any(lvl == 3 and not is_generic(label) for _i, lvl, _e, label, _full in plans)
    counters = {3: 0, 4: 0}
    out = []
    for i, lvl, eid, label, full in plans:
        include = False
        if not is_generic(label):
            if lvl == 3 or NUMBERED_RE.match(label):
                include = True
            elif not has_h3 and i == first_nongeneric_idx:
                include = True
        if include:
            counters[lvl] += 1
            anchor = eid if eid else f"{sid}-h{lvl}-{counters[lvl]}"
        else:
            anchor = eid or ""
        out.append((i, lvl, eid or "", label, include, anchor, toc_level(lvl, label), full))
    return out


def build_toc(src: str) -> tuple[list[tuple[int, str, str, str]], dict]:
    """TOC entries (toc_level, anchor, label, full_label) + {section id: plan}."""
    entries: list[tuple[int, str, str, str]] = []
    plans_by_section: dict[str, list] = {}
    seen: list[str] = []
    for sid, body in SECTION_RE.findall(src):
        plan = plan_section(sid, body)
        plans_by_section[sid] = plan
        for _i, lvl, _eid, label, include, anchor, depth, full in plan:
            if not include:
                continue
            key = dedup_key(label)
            if key in seen[-5:]:
                continue
            seen.append(key)
            entries.append((depth, anchor, label, full))
    return entries, plans_by_section


def inject_heading_ids(src: str, plans_by_section: dict) -> str:
    def fix_section(m: re.Match) -> str:
        sid, body = m.group(1), m.group(2)
        by_index = {p[0]: p for p in plans_by_section.get(sid, [])}
        counter = [-1]
        def fix_open(om: re.Match) -> str:
            counter[0] += 1
            p = by_index.get(counter[0])
            if not p or not p[4] or p[2] or not p[5]:
                return om.group(0)
            return f'<h{p[1]}{om.group(2)} id="{p[5]}">'
        return f'<section class="ms-page" id="{sid}">' + HEAD_OPEN_RE.sub(fix_open, body) + "</section>"
    return SECTION_RE.sub(fix_section, src)


def toc_html(entries: list[tuple[int, str, str, str]]) -> str:
    items = "\n".join(
        f'<li class="l{lvl}"><a href="#{anchor}" title="{html.escape(full)}">'
        f'{html.escape(label)}</a></li>'
        for lvl, anchor, label, full in entries
    )
    return (
        f"{START}\n"
        '<nav class="ms-toc" id="ms-toc" aria-label="目录">\n'
        "<details open><summary>目录</summary>\n<ul>\n"
        f"{items}\n"
        "</ul>\n</details>\n</nav>\n"
        f"{END}"
    )


def process(path: Path) -> int:
    src = path.read_text(encoding="utf-8")
    entries, plans = build_toc(src)
    src = inject_heading_ids(src, plans)

    src, n_old = OLD_TOC_RE.subn("", src)
    src, n_marked = MARKED_RE.subn("", src)

    nav = toc_html(entries)
    if '<div class="ms-shell">' in src:
        src = src.replace('<div class="ms-shell">',
                          '<div class="ms-shell">\n' + nav + "\n", 1)
    else:
        src = src.replace('<article class="ms-body">',
                          '<div class="ms-shell">\n' + nav + '\n<article class="ms-body">', 1)
        i = src.rindex("</article>")
        src = src[:i] + "</article>\n</div>" + src[i + len("</article>"):]

    src, n_h2 = PAGE_H2_RE.subn(r'<h2><span class="ms-pn">p.\1</span></h2>', src)

    path.write_text(src, encoding="utf-8")
    print(f"{path.relative_to(ROOT)}: toc entries={len(entries)}, "
          f"legacy toc removed={n_old}, marked toc replaced={n_marked}, "
          f"page markers={n_h2}, sections={len(SECTION_RE.findall(src))}")
    for lvl, anchor, label, _full in entries:
        print(f"    h{lvl} {anchor}: {label}")
    return len(entries)


def main() -> int:
    files = [Path(a) for a in sys.argv[1:]] or [ROOT / f for f in DEFAULT_FILES]
    for f in files:
        if not f.is_absolute():
            f = ROOT / f
        process(f)
    return 0


if __name__ == "__main__":
    sys.exit(main())
