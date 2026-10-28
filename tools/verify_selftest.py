#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_selftest.py —— 用无头 Chrome 跑所有模块的 ?selftest=1 数值断言。

用法：
  python3 tools/verify_selftest.py [模块目录 ...]

每个模块都在 file:// 下加载，等待虚拟时间 4s，读取 #selftestPanel 的
文本，统计 PASS / FAIL。任一模块出现 FAIL、或面板为空，退出码 1。
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHROME = shutil.which("google-chrome") or "/usr/bin/google-chrome"
PANEL_RE = re.compile(
    r'<div[^>]*id="selftestPanel"[^>]*>(.*?)</div>', re.IGNORECASE | re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")


def panel_text(dom: str) -> str:
    match = PANEL_RE.search(dom)
    if not match:
        return ""
    return TAG_RE.sub("\n", match.group(1)).strip()


def run_one(path: Path) -> tuple[int, int, str]:
    url = path.as_uri() + "?selftest=1"
    with tempfile.TemporaryDirectory(prefix="tm-profile-") as profile:
        proc = subprocess.run(
            [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
             "--user-data-dir=" + profile, "--hide-scrollbars",
             "--virtual-time-budget=6000", "--dump-dom", url],
            capture_output=True, text=True, timeout=120)
    text = panel_text(proc.stdout)
    passed = len(re.findall(r"\bPASS\b", text))
    failed = len(re.findall(r"\bFAIL\b", text))
    if "selftestPanel" not in path.read_text(encoding="utf-8"):
        return -1, 0, "无 selftest 契约（遗留模块）"
    if proc.returncode != 0 and not text:
        return 0, 1, "chrome 退出码 " + str(proc.returncode)
    return passed, failed, " ".join(text.split())[:160]


def main(argv: list[str]) -> int:
    targets = [Path(a).resolve() for a in argv] or sorted(
        ROOT.glob("modules/*/index.html"))
    if not targets:
        print("没有找到模块")
        return 2
    bad = 0
    for path in targets:
        try:
            passed, failed, note = run_one(path)
        except subprocess.TimeoutExpired:
            print("[TIMEOUT] " + str(path))
            bad += 1
            continue
        if passed == -1:
            print("SKIP  %-42s  %s" % (path.parent.name, note))
            continue
        status = "PASS" if failed == 0 and passed > 0 else "FAIL"
        if status == "FAIL":
            bad += 1
        print("%s  %-42s  pass=%d fail=%d  %s" % (
            status, path.parent.name, passed, failed, note))
    print("-- %d/%d 模块通过" % (len(targets) - bad, len(targets)))
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
