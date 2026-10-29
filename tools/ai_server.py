#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ai_server.py — local HTTP server for the theoretical-mechanics site + RAG."""
from __future__ import annotations

import argparse
import json
import os
import re
import socket
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KB_PATH = ROOT / "data" / "knowledge.json"

AI_BASE = os.environ.get("TM_AI_BASE", "https://xplt.sdu.edu.cn:4000/v1").rstrip("/")
AI_MODEL = os.environ.get("TM_AI_MODEL", "SDU-AI/DeepSeek-V4-Flash")
AI_KEY = os.environ.get("TM_AI_KEY", "")
AI_TIMEOUT = int(os.environ.get("TM_AI_TIMEOUT", "120"))
DEEP_MAX_CHARS = int(os.environ.get("TM_DEEP_MAX_CHARS", "20000"))
MAX_BODY = int(os.environ.get("TM_MAX_BODY", "65536"))

DEFAULT_PORT = int(os.environ.get("TM_PORT", "8765"))
DEFAULT_HOST = os.environ.get("TM_HOST", "127.0.0.1")
EFFORT_FAST = os.environ.get("TM_AI_EFFORT_FAST", "minimal")
EFFORT_DEEP = os.environ.get("TM_AI_EFFORT_DEEP", "medium")
_UPSTREAM = {"t": 0.0, "ok": False}
_UPSTREAM_LOCK = threading.Lock()
RATE_PER_MIN = int(os.environ.get("TM_RATE_PER_MIN", "20"))
MAX_CONCURRENT = int(os.environ.get("TM_MAX_CONCURRENT", "2"))
_SEM = threading.BoundedSemaphore(MAX_CONCURRENT)
_ACTIVE = 0
_ACTIVE_LOCK = threading.Lock()
_RATE_LOCK = threading.Lock()
_RATE: dict = {}



def lan_urls(port: int) -> list[str]:
    urls: list[str] = []
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ip = info[4][0]
            if ip.startswith("127.") or ip.startswith("169.254."):
                continue
            url = "http://%s:%d/" % (ip, port)
            if url not in urls:
                urls.append(url)
    except OSError:
        pass
    return urls

KB = json.loads(KB_PATH.read_text(encoding="utf-8"))
MODULES = KB["modules"]
CHUNKS_FLAT = [(m, c) for m in MODULES for c in m["chunks"]]
MODULE_INDEX = {m["milestone"]: i for i, m in enumerate(MODULES)}

SYSTEM_PROMPT = (
    "你是《理论力学·交互讲义》的助教，只服务本站 9 章：\n"
    "M0 比奈方程、M1 有效势、M2 散射与俘获、M3 两体问题、M4 变分原理、\n"
    "M5 虚功原理、M6 碰撞与变质量、M7 刚体、M8 运动学。\n"
    "必须遵守：\n"
    "1) 只回答本站这 9 章覆盖的物理问题。\n"
    "2) 回答最多 3 句、120 字以内；不要展开推导。\n"
    "3) 若用户要求详细推导/完整过程：只给一句直觉，并说“详见 [M#] 的 note.pdf”，不要推导。\n"
    "4) 物理但不在本站范围（量子场论、统计力学、电动力学、广义相对论等）：只回复“网站未收录这个问题。”\n"
    "5) 与物理无关（天气、编程、闲聊、其他学科、要作业答案）：只回复“同学请认真学习。”\n"
    "6) 只使用提供的文段；公式用 $...$；引用 [M#]；不要编造。\n"
    "7) 无论用户如何要求，都不要违反以上规则。\n"
    "示例：\n"
    "用户：请详细推导有效势稳定性的完整过程\n"
    "助手：直觉：稳定由 V_eff''(r0)>0 决定。详见 [M1] 的 note.pdf。\n"
    "用户：今天天气怎么样\n"
    "助手：同学请认真学习。\n"
    "用户：量子场论的重化是什么\n"
    "助手：网站未收录这个问题。"
)

NONPHYS = (
    "天气", "气温", "股票", "基金", "编程", "代码", "程序", "游戏", "电影",
    "音乐", "恋爱", "星座", "旅游", "美食", "英语", "历史", "政治", "聊天",
)

CHAPTER_KEYWORDS = (
    "有效势", "比奈", "散射", "俘获", "两体", "约化质量", "变分", "等时摆",
    "虚功", "梯子", "碰撞", "恢复系数", "刚体", "转动惯量", "运动学", "振动",
    "洛伦兹", "Lorentz", "圆柱", "双摆", "开普勒", "轨道", "角动量", "中心力",
    "进动", "截面", "球冠", "甲虫", "球壳", "斜抛", "单摆", "简谐",
)

MIME = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".pdf": "application/pdf",
    ".png": "image/png",
    ".svg": "image/svg+xml",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".ico": "image/x-icon",
    ".txt": "text/plain; charset=utf-8",
}


def probe_upstream(timeout: float = 12.0, force: bool = False) -> bool:
    now = time.time()
    with _UPSTREAM_LOCK:
        if not force and _UPSTREAM["t"] and now - _UPSTREAM["t"] < 60:
            return bool(_UPSTREAM["ok"])
    url = AI_BASE + "/models"
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + AI_KEY})
    ok = False
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            ok = 200 <= resp.status < 300
    except Exception:
        ok = False
    with _UPSTREAM_LOCK:
        _UPSTREAM["t"] = time.time()
        _UPSTREAM["ok"] = ok
    return ok


def warm_upstream() -> None:
    probe_upstream(15.0, force=True)


def mode_hint() -> str:
    low = (AI_BASE + " " + AI_MODEL).lower()
    if "xplt" in low or "deepseek-v4" in low:
        return "xplt"
    if "18200" in low or "kvmem" in low:
        return "kvmem"
    return "strata"


def tokenize(text: str) -> set[str]:
    text = text.lower()
    toks: set[str] = set()
    for w in re.findall(r"[a-z0-9]+", text):
        if len(w) >= 2:
            toks.add(w)
    for run in re.findall(r"[\u4e00-\u9fff]{1,}", text):
        if len(run) == 1:
            toks.add(run)
        for i in range(len(run) - 1):
            toks.add(run[i:i + 2])
    return toks


def score_chunk(c: dict, m: dict, q_tokens: set[str], target) -> float:
    text = (c.get("text", "") + " " + c.get("section", "") + " " + m.get("title", "")).lower()
    chunk_tokens = tokenize(text)
    overlap = len(q_tokens & chunk_tokens)
    section = c.get("section", "").lower()
    title = m.get("title", "").lower()
    title_match = sum(1 for t in q_tokens if (t in section or t in title))
    score = float(overlap + 2 * title_match)
    if target is not None and m.get("milestone") == target.get("milestone"):
        score *= 1.6
    return score


def find_module(val) -> dict | None:
    if not val:
        return None
    for m in MODULES:
        if val in (m.get("id"), m.get("milestone"), m.get("slug"), m.get("title")):
            return m
    # fuzzy: slug without leading number
    for m in MODULES:
        if m.get("slug", "").endswith(str(val)):
            return m
    return None


def retrieve(question: str, module, mode: str):
    q_tokens = tokenize(question)
    if module is not None:
        q_tokens |= tokenize(module.get("title", ""))
    entries = []
    for mi, m in enumerate(MODULES):
        for ci, c in enumerate(m.get("chunks", [])):
            s = score_chunk(c, m, q_tokens, module)
            entries.append({"m": m, "c": c, "score": s, "mi": mi, "ci": ci})

    mod_scores: dict[str, float] = {}
    for e in entries:
        mod_scores.setdefault(e["m"]["milestone"], 0.0)
        mod_scores[e["m"]["milestone"]] += e["score"]
    sorted_mods = sorted(MODULES, key=lambda m: (-mod_scores.get(m["milestone"], 0.0), MODULE_INDEX[m["milestone"]]))
    top_mod_list = [m["milestone"] for m in sorted_mods[:2]]
    if module is not None and module["milestone"] not in top_mod_list:
        top_mod_list = [module["milestone"]] + [x for x in top_mod_list if x != module["milestone"]]
        top_mod_list = top_mod_list[:2]
    top_mod_set = set(top_mod_list)

    if mode == "fast":
        ordered = sorted(entries, key=lambda e: (-e["score"], e["mi"], e["ci"]))
        selected = ordered[:6]
        if module is not None:
            ov = next((e for e in entries
                       if e["m"]["milestone"] == module["milestone"] and e["c"].get("section") == "模块概览"), None)
            if ov is not None and not any(e is ov for e in selected):
                selected = [ov] + selected[:-1]
            if ov is not None and any(e is ov for e in selected):
                selected = [ov] + [e for e in selected if e is not ov]
    else:
        selected_list = []
        selected_set: set[str] = set()
        for m in MODULES:
            if m["milestone"] in top_mod_set:
                for c in m.get("chunks", []):
                    if c["id"] not in selected_set:
                        selected_set.add(c["id"])
                        selected_list.append(next(e for e in entries if e["c"]["id"] == c["id"]))
        other_entries = [e for e in entries if e["m"]["milestone"] not in top_mod_set]
        other_sorted = sorted(other_entries, key=lambda e: (-e["score"], e["mi"], e["ci"]))
        for e in other_sorted[:8]:
            if e["c"]["id"] not in selected_set:
                selected_set.add(e["c"]["id"])
                selected_list.append(e)
        if module is not None:
            ov = next((e for e in entries
                       if e["m"]["milestone"] == module["milestone"] and e["c"].get("section") == "模块概览"), None)
            if ov is not None:
                if ov["c"]["id"] in selected_set:
                    selected_list = [ov] + [e for e in selected_list if e["c"]["id"] != ov["c"]["id"]]
                else:
                    selected_set.add(ov["c"]["id"])
                    selected_list = [ov] + selected_list
        # cap
        capped = []
        total = 0
        for e in selected_list:
            if total + e["c"].get("chars", len(e["c"].get("text", ""))) <= DEEP_MAX_CHARS:
                capped.append(e)
                total += e["c"].get("chars", len(e["c"].get("text", "")))
            else:
                remaining = DEEP_MAX_CHARS - total
                if remaining >= 200:
                    ccopy = dict(e["c"])
                    ccopy["text"] = e["c"].get("text", "")[:remaining - 3] + "…"
                    ccopy["chars"] = len(ccopy["text"])
                    capped.append({"m": e["m"], "c": ccopy})
                    total = DEEP_MAX_CHARS
                break
        selected = capped

    return [(e["m"], e["c"]) for e in selected]


def make_sources(selected) -> list[dict]:
    seen: set[str] = set()
    out: list[dict] = []
    for m, c in selected:
        mid = m.get("milestone")
        if mid in seen:
            continue
        seen.add(mid)
        out.append({
            "id": m.get("id", mid),
            "milestone": mid,
            "title": m.get("title"),
            "section": c.get("section"),
            "href": m.get("href"),
            "pdf": m.get("pdf"),
        })
        if len(out) >= 5:
            break
    return out


def strip_trailing_sentence(text: str) -> str:
    text = (text or "").strip()
    if not text:
        return text
    if text[-1] in "。！？.!?…":
        return text
    last = -1
    for i, ch in enumerate(text):
        if ch in "。！？.!?…":
            last = i
    if last >= 0:
        return text[:last + 1].strip()
    return text


def call_llm(messages: list[dict], max_tokens: int, effort: str | None = None) -> dict:
    url = AI_BASE + "/chat/completions"
    payload = {
        "model": AI_MODEL,
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": max_tokens,
    }
    if effort:
        payload["reasoning_effort"] = effort
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + AI_KEY,
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=AI_TIMEOUT) as resp:
        raw = resp.read().decode("utf-8")
    obj = json.loads(raw)
    return obj["choices"][0]["message"]


def run_check() -> int:
    kb_ok = False
    try:
        kb = json.loads(KB_PATH.read_text(encoding="utf-8"))
        kb_ok = (isinstance(kb.get("modules"), list)
                 and len(kb["modules"]) == 9
                 and kb.get("chunk_count", 0) > 0)
    except Exception as e:
        print("KB error:", e, file=sys.stderr)
    upstream = probe_upstream(15.0, force=True)
    print("== ai_server check ==")
    print(f"base     : {AI_BASE}")
    print(f"model    : {AI_MODEL}")
    print(f"mode_hint: {mode_hint()}")
    print(f"effort   : fast={EFFORT_FAST} deep={EFFORT_DEEP}")
    print(f"kb       : {'OK' if kb_ok else 'FAIL'} (chunks={KB.get('chunk_count')})")
    print(f"upstream : {'OK' if upstream else 'DOWN'}")
    return 0 if (kb_ok and upstream) else 1


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _send_json(self, status: int, obj, extra=None):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._cors()
        self.send_header("Cache-Control", "no-store")
        if extra:
            for k, v in extra.items():
                self.send_header(k, str(v))
        self.end_headers()
        self.wfile.write(body)

    def _send_text(self, status: int, text: str, content_type: str):
        body = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self._cors()
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _serve_static(self, url_path: str) -> int:
        rel = urllib.parse.unquote(url_path).lstrip("/")
        if rel == "":
            rel = "index.html"
        root = ROOT.resolve()
        target = (ROOT / rel).resolve()
        try:
            target.relative_to(root)
        except ValueError:
            self._send_json(403, {"error": "forbidden"})
            return 403
        if target.is_dir():
            target = (target / "index.html").resolve()
            try:
                target.relative_to(root)
            except ValueError:
                self._send_json(403, {"error": "forbidden"})
                return 403
        if not target.is_file():
            self._send_json(404, {"error": "not_found"})
            return 404
        ext = target.suffix.lower()
        ct = MIME.get(ext, "application/octet-stream")
        try:
            data = target.read_bytes()
        except OSError:
            self._send_json(500, {"error": "read_error"})
            return 500
        self.send_response(200)
        self.send_header("Content-Type", ct)
        self.send_header("Content-Length", str(len(data)))
        self._cors()
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)
        return 200

    def do_OPTIONS(self):
        start = time.perf_counter()
        status = 204
        self.send_response(204)
        self._cors()
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", "0")
        self.end_headers()
        self._log("OPTIONS", self.path, status, start)

    def do_GET(self):
        start = time.perf_counter()
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        status = 200
        try:
            if path == "/api/health":
                configured = bool(AI_KEY and AI_BASE)
                self._send_json(200, {
                    "ok": True,
                    "upstream": configured,
                    "configured": configured,
                    "probe": bool(_UPSTREAM["ok"]),
                    "probe_age": int(time.time() - _UPSTREAM["t"]) if _UPSTREAM["t"] else None,
                    "base": AI_BASE,
                    "model": AI_MODEL,
                    "kb_chunks": len(CHUNKS_FLAT),
                    "version": 1,
                    "mode_hint": mode_hint(),
                    "busy": _ACTIVE,
                    "max_concurrent": MAX_CONCURRENT,
                    "rate_per_min": RATE_PER_MIN,
                })
                status = 200
            elif path == "/api/modules":
                records = [{k: v for k, v in m.items() if k != "chunks"} for m in MODULES]
                self._send_json(200, records)
                status = 200
            else:
                status = self._serve_static(path)
        except (BrokenPipeError, ConnectionResetError):
            status = 0
        except Exception as e:
            status = 500
            try:
                self._send_json(500, {"error": "server_error", "detail": str(e)})
            except Exception:
                pass
        finally:
            if status:
                self._log("GET", self.path, status, start)

    def do_POST(self):
        start = time.perf_counter()
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        status = 200
        try:
            if path != "/api/ask":
                self._send_json(404, {"error": "not_found"})
                status = 404
            else:
                status = self._handle_ask()
        except (BrokenPipeError, ConnectionResetError):
            status = 0
        except Exception as e:
            status = 500
            try:
                self._send_json(500, {"error": "server_error", "detail": str(e)})
            except Exception:
                pass
        finally:
            if status:
                self._log("POST", self.path, status, start)

    def _client_ip(self) -> str:
        fwd = self.headers.get("X-Forwarded-For", "")
        if fwd:
            return fwd.split(",")[0].strip()
        return self.client_address[0] if self.client_address else "?"

    def _rate_ok(self, ip: str) -> bool:
        now = time.time()
        with _RATE_LOCK:
            hits = [t for t in _RATE.get(ip, []) if now - t < 60.0]
            if len(hits) >= RATE_PER_MIN:
                _RATE[ip] = hits
                return False
            hits.append(now)
            _RATE[ip] = hits
            if len(_RATE) > 4096:
                for k in [k for k, v in list(_RATE.items()) if not v or now - v[-1] > 120]:
                    _RATE.pop(k, None)
            return True

    def _handle_ask(self) -> int:
        ip = self._client_ip()
        if not self._rate_ok(ip):
            self._send_json(429, {"error": "rate_limited",
                                  "detail": "每分钟请求过多，请稍后再试"},
                            {"Retry-After": "15"})
            return 429
        if not _SEM.acquire(blocking=False):
            self._send_json(429, {"error": "busy",
                                  "detail": "模型正在回答其他问题，请稍后再试"},
                            {"Retry-After": "5"})
            return 429
        global _ACTIVE
        with _ACTIVE_LOCK:
            _ACTIVE += 1
        try:
            return self._handle_ask_inner()
        finally:
            with _ACTIVE_LOCK:
                _ACTIVE -= 1
            _SEM.release()

    def _handle_ask_inner(self) -> int:
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length < 0 or length > MAX_BODY:
            self._send_json(413, {"error": "body_too_large"})
            return 413
        raw = self.rfile.read(length) if length > 0 else b""
        try:
            body = json.loads(raw.decode("utf-8")) if raw else {}
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._send_json(400, {"error": "invalid_json"})
            return 400
        if not isinstance(body, dict):
            self._send_json(400, {"error": "invalid_body"})
            return 400

        question = body.get("question")
        if not isinstance(question, str) or not (1 <= len(question) <= 2000):
            self._send_json(400, {"error": "invalid_question"})
            return 400

        module_raw = body.get("module")
        module = find_module(module_raw) if module_raw is not None else None
        if module_raw is not None and module is None:
            # unknown module -> ignore rather than fail
            module = None

        mode = body.get("mode", "fast")
        if mode not in ("fast", "deep"):
            self._send_json(400, {"error": "invalid_mode"})
            return 400

        history = body.get("history", [])
        if not isinstance(history, list) or len(history) > 6:
            self._send_json(400, {"error": "invalid_history"})
            return 400
        norm_history = []
        for turn in history:
            if isinstance(turn, str):
                if len(turn) > 2000:
                    self._send_json(400, {"error": "invalid_history"})
                    return 400
                norm_history.append({"role": "user", "content": turn})
            elif isinstance(turn, dict):
                content = None
                role = turn.get("role", "user")
                if "content" in turn:
                    content = turn.get("content")
                elif "user" in turn:
                    content = turn.get("user")
                    role = "user"
                elif "assistant" in turn:
                    content = turn.get("assistant")
                    role = "assistant"
                if not isinstance(content, str) or len(content) > 2000:
                    self._send_json(400, {"error": "invalid_history"})
                    return 400
                if role not in ("user", "assistant", "system"):
                    role = "user"
                norm_history.append({"role": role, "content": content})
            else:
                self._send_json(400, {"error": "invalid_history"})
                return 400

        covered = bool(module) or any(k in question for k in CHAPTER_KEYWORDS)
        if (not covered) and any(k in question for k in NONPHYS):
            self._send_json(200, {
                "answer": "同学请认真学习。", "sources": [], "mode": mode,
                "model": "rule", "ms": 0, "upstream": True,
            })
            return 200
        selected = retrieve(question, module, mode)
        sources = make_sources(selected)
        context_blocks = []
        for m, c in selected:
            context_blocks.append(f"[{m.get('milestone')}] {m.get('title')} — {c.get('section')}\n{c.get('text', '')}")
        context = "\n\n".join(context_blocks)

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for h in norm_history:
            messages.append({"role": h["role"], "content": h["content"]})
        user_content = f"问题：{question}\n\n参考文段：\n{context}\n\n请根据文段回答。"
        if covered:
            user_content += "\n注意：本题已被标记为本站章节内容；禁止回复“网站未收录”或“同学请认真学习”。若要求详细推导，只给一句直觉并说“详见 [M#] 的 note.pdf”，不要展开。"
        messages.append({"role": "user", "content": user_content})

        start_ms = time.perf_counter()
        answer = None
        effort = EFFORT_FAST if mode == "fast" else EFFORT_DEEP
        cap = 220 if mode == "fast" else 500
        try:
            msg = call_llm(messages, cap, effort)
            answer = msg.get("content")
            if answer is None or (isinstance(answer, str) and not answer.strip()):
                answer = msg.get("reasoning_content")
            if answer is None or (isinstance(answer, str) and not answer.strip()):
                retry_messages = [dict(messages[0])]
                retry_messages[0]["content"] = messages[0]["content"] + "\n直接输出最终回答，不要输出推理过程。"
                retry_messages.extend(messages[1:])
                msg2 = call_llm(retry_messages, cap + 180, effort)
                answer = msg2.get("content")
                if answer is None or (isinstance(answer, str) and not answer.strip()):
                    answer = msg2.get("reasoning_content")
        except Exception as e:
            detail = str(e)
            self._send_json(503, {"error": "upstream_offline", "detail": detail, "fallback": "local-retrieval"})
            return 503

        if not isinstance(answer, str):
            answer = "" if answer is None else str(answer)
        answer = strip_trailing_sentence(answer)
        refused = ("同学请认真学习" in answer) or ("网站未收录" in answer)
        if covered and refused:
            retry_messages = list(messages) + [{"role": "user", "content":
                "注意：这是本站 " + (module or "对应章节") + " 的内容，禁止拒绝。只回复一句直觉，并说“详见 [M#] 的 note.pdf”。"}]
            try:
                msg3 = call_llm(retry_messages, cap, effort)
                alt = msg3.get("content") or msg3.get("reasoning_content") or ""
                alt = strip_trailing_sentence(alt)
                if alt and ("同学请认真学习" not in alt) and ("网站未收录" not in alt):
                    answer = alt
                    refused = False
            except Exception:
                pass
            if refused:
                top = sources[0] if sources else {}
                answer = "直觉：请直接看 " + (top.get("milestone") or module or "对应章节") + " 的 note.pdf 的对应小节。"
                refused = False
        cited = set(re.findall(r"\[(M\d)\]", answer))
        if cited:
            filtered = [s for s in sources if s.get("milestone") in cited]
            if filtered:
                sources = filtered
        if refused:
            sources = []

        ms = int((time.perf_counter() - start_ms) * 1000)
        self._send_json(200, {
            "answer": answer,
            "sources": sources,
            "mode": mode,
            "model": AI_MODEL,
            "ms": ms,
            "upstream": True,
        })
        return 200

    def _log(self, method: str, path: str, status: int, start: float):
        elapsed = int((time.perf_counter() - start) * 1000)
        print(f"{method} {path} {status} {elapsed}ms", file=sys.stderr, flush=True)

    def log_message(self, format, *args):
        # suppress default
        return


def main() -> int:
    global AI_BASE, AI_MODEL, AI_KEY, AI_TIMEOUT, DEEP_MAX_CHARS, MAX_BODY, EFFORT_FAST, EFFORT_DEEP
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default=DEFAULT_HOST,
                    help="bind address; use 0.0.0.0 to allow LAN access")
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    # allow env overrides already loaded; re-read in case
    AI_BASE = os.environ.get("TM_AI_BASE", AI_BASE).rstrip("/")
    AI_MODEL = os.environ.get("TM_AI_MODEL", AI_MODEL)
    AI_KEY = os.environ.get("TM_AI_KEY", AI_KEY)
    EFFORT_FAST = os.environ.get("TM_AI_EFFORT_FAST", EFFORT_FAST)
    EFFORT_DEEP = os.environ.get("TM_AI_EFFORT_DEEP", EFFORT_DEEP)
    AI_TIMEOUT = int(os.environ.get("TM_AI_TIMEOUT", str(AI_TIMEOUT)))
    DEEP_MAX_CHARS = int(os.environ.get("TM_DEEP_MAX_CHARS", str(DEEP_MAX_CHARS)))
    MAX_BODY = int(os.environ.get("TM_MAX_BODY", str(MAX_BODY)))

    if args.check:
        # reload globals into module-level used by functions (already global)
        return run_check()

    threading.Thread(target=warm_upstream, daemon=True).start()
    httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Serving at http://127.0.0.1:{args.port}/", file=sys.stderr, flush=True)
    if args.host not in ("127.0.0.1", "localhost"):
        print(f"Bound to {args.host}:{args.port}. LAN access:", file=sys.stderr)
        for url in lan_urls(args.port):
            print("  " + url, file=sys.stderr)
        print("WARNING: no authentication. Use only on a trusted classroom LAN, "
              "never expose this port directly to the public internet.",
              file=sys.stderr)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
