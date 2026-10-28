#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""apply_theme.py"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FRAGMENT = ROOT / "assets" / "tm-module-theme.html"
HEAD_START = "<!-- TM-THEME-HEAD:START -->"
HEAD_END = "<!-- TM-THEME-HEAD:END -->"
BODY_START = "<!-- TM-THEME-BODY:START -->"
BODY_END = "<!-- TM-THEME-BODY:END -->"
SPLIT_MARKER = "<!-- TM-THEME-SPLIT -->"


def read_text(path: Path) -> str:
    with path.open("r", encoding="utf-8", newline="") as f:
        return f.read()


def write_text(path: Path, text: str) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        f.write(text)


def split_fragment() -> tuple[str, str]:
    raw = read_text(FRAGMENT)
    if SPLIT_MARKER not in raw:
        raise SystemExit("fragment missing split marker")
    head_raw, _sep, body_raw = raw.partition(SPLIT_MARKER)
    head_part = head_raw.strip("\n")
    body_part = body_raw.strip("\n")
    if not head_part or not body_part:
        raise SystemExit("fragment part empty")
    return head_part, body_part


def remove_blocks(text: str) -> str:
    text = re.sub(r"<!-- TM-THEME-HEAD:START -->.*?<!-- TM-THEME-HEAD:END -->\n?", "", text, flags=re.S)
    text = re.sub(r"<!-- TM-THEME-BODY:START -->.*?<!-- TM-THEME-BODY:END -->\n?", "", text, flags=re.S)
    return text


def apply_text(text: str, head_part: str, body_part: str) -> str:
    text = remove_blocks(text)
    head_block = HEAD_START + "\n" + head_part + "\n" + HEAD_END
    body_block = BODY_START + "\n" + body_part + "\n" + BODY_END
    head_matches = list(re.finditer(r"</head\s*>", text, flags=re.I))
    if not head_matches:
        raise ValueError("no </head>")
    hi = head_matches[-1].start()
    text = text[:hi] + head_block + "\n" + text[hi:]
    body_matches = list(re.finditer(r"</body\s*>", text, flags=re.I))
    if not body_matches:
        raise ValueError("no </body>")
    bi = body_matches[-1].start()
    text = text[:bi] + body_block + "\n" + text[bi:]
    return text


def revert_text(text: str) -> str:
    return remove_blocks(text)


def has_markers(text: str) -> bool:
    return HEAD_START in text or BODY_START in text


def default_targets() -> list[Path]:
    return sorted((ROOT / "modules").glob("*/index.html"))


def resolve_targets(args_paths) -> list[Path]:
    if args_paths:
        out = []
        for p in args_paths:
            pp = Path(p)
            if not pp.is_absolute():
                pp = (Path.cwd() / pp).resolve()
            out.append(pp)
        return out
    return [p.resolve() for p in default_targets()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--revert", action="store_true")
    parser.add_argument("paths", nargs="*")
    args = parser.parse_args()

    mode = "check" if args.check else ("revert" if args.revert else "apply")
    targets = resolve_targets(args.paths)
    head_part, body_part = split_fragment()

    if mode == "apply":
        n = 0
        for p in targets:
            if not p.is_file():
                print("MISSING FILE: " + str(p))
                continue
            text = read_text(p)
            new_text = apply_text(text, head_part, body_part)
            if new_text != text:
                write_text(p, new_text)
                n += 1
        print("applied: %d/%d files" % (n, len(targets)))
        return 0

    if mode == "revert":
        n = 0
        for p in targets:
            if not p.is_file():
                print("MISSING FILE: " + str(p))
                continue
            text = read_text(p)
            new_text = revert_text(text)
            if new_text != text:
                write_text(p, new_text)
                n += 1
        print("reverted: %d/%d files" % (n, len(targets)))
        return 0

    bad = 0
    for p in targets:
        if not p.is_file():
            print("%s: MISSING FILE" % p)
            bad += 1
            continue
        text = read_text(p)
        base = revert_text(text)
        expected = apply_text(base, head_part, body_part)
        if text == expected:
            print("%s: OK" % p)
        else:
            if has_markers(text):
                print("%s: STALE" % p)
            else:
                print("%s: MISSING" % p)
            bad += 1
    print("checked: %d/%d ok" % (len(targets) - bad, len(targets)))
    if bad:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
