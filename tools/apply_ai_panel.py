#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""apply_ai_panel.py —— 幂等注入器：把 tm-ai-panel.html 片段注入 index.html。

用法：
  python tools/apply_ai_panel.py --apply [--target PATH]
  python tools/apply_ai_panel.py --check [--target PATH]
  python tools/apply_ai_panel.py --revert [--target PATH]

默认 target: 仓库根 index.html。
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FRAGMENT_PATH = ROOT / "assets" / "tm-ai-panel.html"
KB_PATH = ROOT / "assets" / "tm-offline-kb.js"
KB_PLACEHOLDER = "<!-- TM-OFFLINE-KB -->"
PLACEHOLDER = "<!-- TM-AI-MOUNT -->"
START = "<!-- TM-AI:START -->"
END = "<!-- TM-AI:END -->"


def read_fragment():
    frag = FRAGMENT_PATH.read_text(encoding="utf-8")
    if KB_PLACEHOLDER in frag:
        if KB_PATH.exists():
            kb = KB_PATH.read_text(encoding="utf-8")
            frag = frag.replace(KB_PLACEHOLDER,
                                '<script id="tm-offline-kb">\n' + kb + '\n</script>', 1)
        else:
            frag = frag.replace(KB_PLACEHOLDER, '<!-- offline KB missing -->', 1)
    return frag


def find_block(text):
    s = text.find(START)
    if s == -1:
        return None
    e = text.find(END, s)
    if e == -1:
        return None
    return s, e + len(END)


def cmd_apply(target):
    text = target.read_text(encoding="utf-8")
    frag = read_fragment()
    block = START + "\n" + frag + "\n" + END
    loc = find_block(text)
    if loc is not None:
        s, e = loc
        new = text[:s] + block + text[e:]
        action = "updated"
    else:
        if PLACEHOLDER not in text:
            print("FAIL: placeholder not found and no existing block", file=sys.stderr)
            return 1
        new = text.replace(PLACEHOLDER, block, 1)
        action = "injected"
    target.write_text(new, encoding="utf-8")
    print("OK: {} ({})".format(target, action))
    return 0


def cmd_check(target):
    text = target.read_text(encoding="utf-8")
    loc = find_block(text)
    if loc is None:
        if PLACEHOLDER in text:
            print("STALE: placeholder present, block missing")
            return 1
        print("MISSING: no block and no placeholder")
        return 1
    s, e = loc
    frag = read_fragment()
    expected = START + "\n" + frag + "\n" + END
    if text[s:e] != expected:
        print("STALE: block differs from fragment")
        return 1
    print("OK: block present and up to date")
    return 0


def cmd_revert(target):
    text = target.read_text(encoding="utf-8")
    loc = find_block(text)
    if loc is None:
        print("OK: no block to revert")
        return 0
    s, e = loc
    new = text[:s] + PLACEHOLDER + text[e:]
    target.write_text(new, encoding="utf-8")
    print("OK: reverted ({})".format(target))
    return 0


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--apply", action="store_true")
    g.add_argument("--check", action="store_true")
    g.add_argument("--revert", action="store_true")
    ap.add_argument("--target", default=None)
    args = ap.parse_args()
    target = Path(args.target) if args.target else (ROOT / "index.html")
    if not target.is_file():
        # allow creating? no
        pass
    if args.apply:
        return cmd_apply(target)
    if args.check:
        return cmd_check(target)
    if args.revert:
        return cmd_revert(target)
    return 2


if __name__ == "__main__":
    sys.exit(main())
