#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""static_server.py — tiny static server with no-store caching for the preview."""
from __future__ import annotations

import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        super().end_headers()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(ROOT / "dist"))
    ap.add_argument("--bind", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8081)
    args = ap.parse_args()
    root = str(Path(args.root).resolve())
    handler = lambda *a, **kw: Handler(*a, directory=root, **kw)
    print("serving %s at http://%s:%d/" % (root, args.bind, args.port), flush=True)
    ThreadingHTTPServer((args.bind, args.port), handler).serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
