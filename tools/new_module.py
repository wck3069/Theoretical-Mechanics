#!/home/wck/.venv-tm/bin/python
# -*- coding: utf-8 -*-
"""new_module.py —— 从 templates/ 生成模块骨架（PLAN.md §4.2/§4.3，P0-T2）

用法：
  /home/wck/.venv-tm/bin/python tools/new_module.py <slug> [--out <dir>] [--title <标题>]

参数：
  slug          模块代号（ASCII，如 01-effective-potential）
  --out DIR     模块目录（默认 modules/<slug>）。DIR 即三件套落地目录：
                new_module.py <slug> --out /tmp/x 直接在 /tmp/x 下生成文件
  --title TEXT  模块标题（默认与 slug 相同）

生成物：
  DIR/note.tex     自 templates/note.tex
  DIR/index.html   自 templates/index.html
  DIR/README.md    自 templates/module-README.md
  DIR/qa/          证据目录（空）

规则：
  - 替换占位符 {{MODULE_TITLE}} → 标题、{{MODULE_SLUG}} → slug；
    note.tex 中按 LaTeX 转义（_ # $ % & { } 等），index.html 中按 HTML 转义；
  - 任一目标文件已存在 → 拒绝覆盖、退出码 1（先全量检查，后写入）；
  - slug 必须为非空 ASCII（§11：模块 slug 用 ASCII）。

退出码：0 成功；1 拒绝覆盖；2 用法/路径错误。
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = REPO_ROOT / "templates"

# 模板文件 → 目标文件
TEMPLATE_FILES = {
    "note.tex": "note.tex",
    "index.html": "index.html",
    "module-README.md": "README.md",
}

PLACEHOLDER_TITLE = "{{MODULE_TITLE}}"
PLACEHOLDER_SLUG = "{{MODULE_SLUG}}"

# LaTeX 特殊字符单遍转义（先建映射再一次性替换，避免二次替换污染）
_LATEX_MAP = {
    "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
    "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
    "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
}
_LATEX_RE = re.compile("|".join(re.escape(k) for k in _LATEX_MAP))


def latex_escape(s: str) -> str:
    return _LATEX_RE.sub(lambda m: _LATEX_MAP[m.group(0)], s)


def html_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="new_module.py",
        description="从 templates/ 生成模块骨架（note.tex / index.html / README.md / qa/）")
    parser.add_argument("slug", help="模块代号（ASCII，如 01-effective-potential）")
    parser.add_argument("--out", metavar="DIR", default=None,
                        help="模块目录（默认 modules/<slug>；三件套直接生成在 DIR 下）")
    parser.add_argument("--title", default=None, help="模块标题（默认用 slug）")
    args = parser.parse_args(argv)

    slug = args.slug.strip()
    if not slug or not slug.isascii():
        print(f"ERROR: slug 必须为非空 ASCII：{slug!r}", file=sys.stderr)
        return 2
    title = args.title if args.title else slug

    module_dir = Path(args.out) if args.out else REPO_ROOT / "modules" / slug
    if module_dir.exists() and not module_dir.is_dir():
        print(f"ERROR: 目标已存在且不是目录：{module_dir}", file=sys.stderr)
        return 2

    # 先全量检查，后写入：任何目标文件已存在 → 拒绝覆盖
    targets = {name: module_dir / dst for name, dst in TEMPLATE_FILES.items()}
    existing = [p for p in targets.values() if p.exists()]
    if existing:
        print("ERROR: 拒绝覆盖已存在的文件：", file=sys.stderr)
        for p in existing:
            print(f"  - {p}", file=sys.stderr)
        return 1

    for name, dst in targets.items():
        src = TEMPLATE_DIR / name
        if not src.is_file():
            print(f"ERROR: 模板缺失：{src}", file=sys.stderr)
            return 2
        text = src.read_text(encoding="utf-8")
        if dst.name == "note.tex":
            t, s = latex_escape(title), latex_escape(slug)
        elif dst.name == "index.html":
            t, s = html_escape(title), html_escape(slug)
        else:
            t, s = title, slug
        text = text.replace(PLACEHOLDER_TITLE, t).replace(PLACEHOLDER_SLUG, s)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(text, encoding="utf-8")
        print(f"created: {dst}")

    qa_dir = module_dir / "qa"
    qa_dir.mkdir(parents=True, exist_ok=True)
    print(f"created: {qa_dir}/")
    print(f"模块骨架完成：{module_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
