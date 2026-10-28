#!/home/wck/.venv-tm/bin/python
# -*- coding: utf-8 -*-
"""check_html.py —— 单文件 HTML 检查（PLAN.md §4.2/§5.5/§7.2，P0-T2）

用法：
  /home/wck/.venv-tm/bin/python tools/check_html.py <file.html> [<file.html> ...]

检查项（每项独立 PASS/FAIL；任一 FAIL → 退出码 1）：
  1.  内联 JS 语法：每个无 src 的 <script> 块用 esprima 解析
      （提取脚本块前先剔除 HTML 注释；node/npm 缺失，esprima 为
      记录的替代方案，见 qa/global/toolchain.md）
  2a. 全文无 http://、https://（含属性、CSS、JS 字符串、注释）
  2b. 无协议相对地址 //（资源属性、CSS url()、字符串字面量）
  2c. 资源标签（script src / link href / img·iframe·embed·audio·video·
      source·track src / object data）只允许本地相对路径
  2d. 无 fetch( 调用、无 import 语句/动态 import()、无 XMLHttpRequest
      **唯一例外**：站内本地 AI 助教（P10 起）允许对同源端点
      fetch('/api/ask') 与 fetch('/api/health')——必须是这两个
      字面量、同源相对路径；任何其它 fetch 一律 FAIL。
  2e. 无已知 CDN 域名（unpkg、jsdelivr、cdnjs、Google Fonts、esm.sh 等）

退出码：0 全部通过；1 存在 FAIL；2 用法/环境错误。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import esprima
except ImportError:
    print("FATAL: esprima 不可用 —— 请用 ~/.venv-tm/bin/python 运行"
          "（决策记录见 qa/global/toolchain.md）", file=sys.stderr)
    sys.exit(2)

SCHEME_RE = re.compile(r"https?://", re.IGNORECASE)
PROTO_REL_ATTR_RE = re.compile(r"""(?:src|href|data)\s*=\s*["']//""")
PROTO_REL_CSS_RE = re.compile(r"""url\(\s*["']?//""")
PROTO_REL_STR_RE = re.compile(r"""["']//""")
RESOURCE_TAG_RE = re.compile(
    r"<\s*(script|link|img|iframe|embed|audio|video|source|track|object)\b[^>]*>",
    re.IGNORECASE)
ATTR_IN_TAG_RE = re.compile(
    r"""\b(src|href|data)\s*=(?:"([^"]*)"|'([^']*)')""", re.IGNORECASE)
LOCAL_PATH_RE = re.compile(r"^[A-Za-z0-9_.][A-Za-z0-9_./-]*$")
HAS_SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
FETCH_RE = re.compile(r"\bfetch\s*\(")
# 唯一豁免：站内本地 AI 助教的同源端点（相对路径、双引号或单引号均可）。
# 任何绝对地址都不可能通过 2a/2b，因此这里只需限定路径字面量。
ALLOWED_FETCH_RE = re.compile(
    r"""\bfetch\s*\(\s*(?:API_BASE\s*\+\s*)?(['"])/api/(?:ask|health)\1""")
# 唯一允许的绝对地址：本机环回 AI 服务（file:// 打开页面时使用）。
LOOPBACK_RE = re.compile(r"""http://(?:127\.0\.0\.1|localhost):8765(?=['"\s/]|$)""")
IMPORT_STMT_RE = re.compile(r"""\bimport\s*[\('"{]""")
IMPORT_NAME_RE = re.compile(r"\bimport\s+[A-Za-z_$]")
XHR_RE = re.compile(r"\bXMLHttpRequest\b")
CDN_HOSTS = ("unpkg.com", "jsdelivr.net", "cdnjs.cloudflare.com",
             "fonts.googleapis.com", "fonts.gstatic.com", "ajax.googleapis.com",
             "code.jquery.com", "maxcdn.bootstrapcdn.com", "bootcdn.net",
             "esm.sh", "skypack.dev")
SCRIPT_BLOCK_RE = re.compile(r"<script\b([^>]*)>(.*?)</script\s*>",
                             re.IGNORECASE | re.DOTALL)
TYPE_ATTR_RE = re.compile(r"""type\s*=\s*["']?([^"'\s>]+)""", re.IGNORECASE)
SRC_ATTR_RE = re.compile(r"""src\s*=\s*["'][^"']*["']""", re.IGNORECASE)
JS_TYPES = ("", "text/javascript", "application/javascript", "module",
            "text/ecmascript", "application/ecmascript")

CHECK_COUNT = 6  # 1 + 2a..2e


COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


def strip_html_comments(text: str) -> str:
    """把 HTML 注释整体替换为等长空白（行号与偏移不变）。

    仅用于脚本块提取：避免把注释文字中提到的 <script> 字样误认为
    脚本标签；其余检查仍在原文上执行（注释里的外链同样算违规）。
    """
    return COMMENT_RE.sub(lambda m: " " * len(m.group(0)), text)


def line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def check_inline_js(text: str) -> tuple[int, list[str]]:
    """返回 (解析的块数, 失败信息列表)。"""
    blocks, failures = 0, []
    for m in SCRIPT_BLOCK_RE.finditer(text):
        attrs, body = m.group(1), m.group(2)
        if SRC_ATTR_RE.search(attrs):
            continue  # 带 src 的块由 2c 检查
        tmatch = TYPE_ATTR_RE.search(attrs)
        ttype = tmatch.group(1).lower() if tmatch else ""
        if ttype not in JS_TYPES:
            continue  # application/json、text/template 等非 JS 块
        blocks += 1
        base_line = line_of(text, m.start())
        try:
            if ttype == "module":
                esprima.parseModule(body)
            else:
                esprima.parseScript(body)
        except esprima.Error as exc:
            rel = getattr(exc, "lineNumber", 1) or 1
            desc = getattr(exc, "description", str(exc))
            failures.append(
                f"内联 <script> 块（起于第 {base_line} 行）语法错误："
                f"第 {base_line + rel - 1} 行：{desc}")
    return blocks, failures


def check_resource_tags(text: str) -> list[str]:
    """2c：资源标签的 src/href/data 只允许本地相对路径。"""
    failures = []
    for tag in RESOURCE_TAG_RE.finditer(text):
        for am in ATTR_IN_TAG_RE.finditer(tag.group(0)):
            value = am.group(2) if am.group(2) is not None else am.group(3)
            name = am.group(1).lower()
            where = f"第 {line_of(text, tag.start())} 行 <{tag.group(1).lower()}> {name}=\"{value}\""
            if value == "":
                failures.append(f"{where}：空引用")
            elif HAS_SCHEME_RE.match(value):
                failures.append(f"{where}：带 scheme 的外部引用")
            elif value.startswith("//"):
                failures.append(f"{where}：协议相对地址")
            elif value.startswith("/"):
                failures.append(f"{where}：根相对路径（指向模块目录之外）")
            elif not LOCAL_PATH_RE.match(value):
                failures.append(f"{where}：非本地相对路径")
    return failures


def check_file(path: Path) -> bool:
    """对单个文件执行全部检查；返回 True 表示全部通过。"""
    print(f"== check_html.py: {path} ==")
    try:
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError) as exc:
        print(f"[FAIL] 0. 无法读取文件：{exc}")
        print(f"-- 摘要：0/{CHECK_COUNT} 项通过，{CHECK_COUNT} 项失败")
        return False

    failed = 0

    def report(idx: str, name: str, fails: list[str], ok_msg: str) -> None:
        nonlocal failed
        if fails:
            failed += 1
            for msg in fails:
                print(f"[FAIL] {idx}. {name}：{msg}")
        else:
            print(f"[PASS] {idx}. {name}（{ok_msg}）")

    # 1. 内联 JS 语法（在剔除 HTML 注释后的文本上提取脚本块，
    #    避免把注释中提到的 <script> 字样误认为脚本标签）
    blocks, js_fails = check_inline_js(strip_html_comments(text))
    report("1", "内联 JS 语法", js_fails,
           f"{blocks} 个 <script> 块，esprima {esprima.__version__}")

    # 2a. http/https 外链
    masked = LOOPBACK_RE.sub(lambda m: " " * len(m.group(0)), text)
    fails = [f"第 {line_of(text, m.start())} 行发现 {m.group(0)}"
             for m in SCHEME_RE.finditer(masked)]
    report("2a", "无 http 或 https 外链", fails, "全文未出现")

    # 2b. 协议相对地址
    fails = []
    for pat in (PROTO_REL_ATTR_RE, PROTO_REL_CSS_RE, PROTO_REL_STR_RE):
        for m in pat.finditer(text):
            fails.append(f"第 {line_of(text, m.start())} 行发现协议相对地址 //")
            break
    report("2b", "无协议相对地址", fails, "属性、CSS、字符串均未出现")

    # 2c. 资源标签本地路径
    report("2c", "资源引用均为本地相对路径", check_resource_tags(text),
           "无外部资源标签")

    # 2d. fetch / import / XMLHttpRequest
    fails = []
    for m in FETCH_RE.finditer(text):
        if ALLOWED_FETCH_RE.match(text[m.start():m.start() + 160]):
            continue
        fails.append(f"第 {line_of(text, m.start())} 行发现 fetch( 调用"
                     "（仅允许同源 /api/ask 与 /api/health）")
    for pat, label in ((IMPORT_STMT_RE, "import 语句"),
                       (IMPORT_NAME_RE, "import 语句"), (XHR_RE, "XMLHttpRequest")):
        for m in pat.finditer(text):
            fails.append(f"第 {line_of(text, m.start())} 行发现 {label}")
    report("2d", "无网络请求或外部模块加载", sorted(set(fails)), "未出现")

    # 2e. CDN 域名
    lowered = text.lower()
    fails = [f"发现 CDN 域名 {host}" for host in CDN_HOSTS if host in lowered]
    report("2e", "无 CDN 域名引用", fails, "未出现")

    passed = CHECK_COUNT - failed
    print(f"-- 摘要：{passed}/{CHECK_COUNT} 项通过，{failed} 项失败")
    return failed == 0


def main(argv: list[str]) -> int:
    if len(argv) < 1:
        print(__doc__)
        return 2
    all_ok = True
    for arg in argv:
        path = Path(arg)
        if not path.is_file():
            print(f"ERROR: 文件不存在：{path}", file=sys.stderr)
            return 2
        if not check_file(path):
            all_ok = False
    code = 0 if all_ok else 1
    print(f"EXIT_CODE={code}")
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
