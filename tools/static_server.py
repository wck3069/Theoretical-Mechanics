#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""static_server.py — tiny static server for the preview.

Features:
- no-store cache headers (preview must never serve stale pages);
- GET /__live returns a build stamp (max mtime under dist) so browsers can poll it;
- HTML responses get an inline live-reload poller injected before </body>,
  so an open tab refreshes itself whenever the watcher rebuilds dist/.
"""
from __future__ import annotations

import argparse
import os
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# ES5, inline, dependency-free: first poll stores the stamp; a later poll that
# sees a different stamp saves scrollY and reloads; the reloaded page restores
# the scroll and re-seeds the stamp.
LIVE_SNIPPET = (
    "<script>(function(){var k=\"tm-live-stamp\";"
    "var s=sessionStorage.getItem(k);"
    "if(s&&s.indexOf(\"scroll:\")===0){var y=+s.slice(7);"
    "sessionStorage.removeItem(k);"
    "requestAnimationFrame(function(){window.scrollTo(0,y);});}"
    "function poll(){fetch(\"/__live\").then(function(r){return r.text();})"
    ".then(function(t){var p=sessionStorage.getItem(k);"
    "if(p&&p!==t){sessionStorage.setItem(k,\"scroll:\"+window.scrollY);location.reload();return;}"
    "sessionStorage.setItem(k,t);setTimeout(poll,2000);})"
    ".catch(function(){setTimeout(poll,4000);});}"
    "poll();})();</script>"
).encode()

_stamp_cache = {"at": 0.0, "value": ""}


def build_stamp(root: str) -> str:
    """Max st_mtime_ns over every file under root, memoized for 1s."""
    now = time.monotonic()
    if now - _stamp_cache["at"] < 1.0 and _stamp_cache["value"]:
        return _stamp_cache["value"]
    try:
        best = 0
        for dirpath, _dirs, files in os.walk(root):
            for name in files:
                try:
                    mtime = os.stat(os.path.join(dirpath, name)).st_mtime_ns
                except OSError:
                    continue
                if mtime > best:
                    best = mtime
        value = str(best)
    except Exception:
        value = "ERR-%d" % int(time.time())
    _stamp_cache["at"] = now
    _stamp_cache["value"] = value
    return value


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self) -> None:
        path = (self.path or "").split("?")[0].lower()
        if path.endswith((".html", ".htm", "/")) or path.startswith("/__live"):
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
            self.send_header("Pragma", "no-cache")
        else:
            self.send_header("Cache-Control", "public, max-age=60")
        super().end_headers()

    def _serve_live_stamp(self) -> None:
        body = build_stamp(self.directory).encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _resolve_html(self, path: str) -> Path | None:
        """Return the .html file this URL maps to inside root, else None."""
        fs = Path(self.translate_path(path))
        if fs.is_dir():
            fs = fs / "index.html"
        if fs.suffix.lower() != ".html" or not fs.is_file():
            return None
        root = Path(self.directory).resolve()
        try:
            fs.resolve().relative_to(root)
        except ValueError:
            return None
        return fs

    def do_GET(self) -> None:  # noqa: N802 (http.server naming)
        path, _, query = self.path.partition("?")
        if path == "/__live":
            self._serve_live_stamp()
            return
        html = None if "selftest=1" in query else self._resolve_html(path)
        if html is None:
            super().do_GET()
            return
        data = html.read_bytes()
        cut = data.lower().rfind(b"</body>")
        if cut == -1:
            super().do_GET()
            return
        out = data[:cut] + LIVE_SNIPPET + data[cut:]
        self.send_response(200)
        self.send_header("Content-Type", self.guess_type(str(html)))
        self.send_header("Content-Length", str(len(out)))
        self.end_headers()
        self.wfile.write(out)


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
