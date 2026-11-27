#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""apply_neural_entry.py — 把首页“点击行星/目录行/回车”的去向，从章节页改为知识网络页。

幂等：重复运行不会重复插入。
- 新增 chapterHref(m) helper
- selectModule / finishFlight / updateFly 兜底 / 飞行 preload iframe / pushState → neural 页
- 详情面板“进入模拟”按钮保留：改名为“进入知识网络”，章节页入口仍可从网络页面包屑/面板拿到
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "index.html"
s = P.read_text(encoding="utf-8")

if "function chapterHref(" in s:
    print("already patched")
    sys.exit(0)

helper = """function chapterHref(m){ return (m && m.sim) ? m.sim : 'chapters/01-newton/index.html'; }
function selectModule(i, animate){"""
assert "function selectModule(i, animate){" in s
s = s.replace("function selectModule(i, animate){", helper, 1)

repl = [
    ("  window.location.href = m.sim;", "  window.location.href = chapterHref(m);"),
    ("  window.location.href=f.m.sim;", "  window.location.href=chapterHref(f.m);"),
    ("  ifr.src=m.sim;", "  ifr.src=chapterHref(f.m);"),
    ("if(!o){ state.flying=null; window.location.href=f.m.sim; return; }",
     "if(!o){ state.flying=null; window.location.href=chapterHref(f.m); return; }"),
    ("try{ history.pushState({tmPortal:true},'',f.m.sim); }catch(err){}",
     "try{ history.pushState({tmPortal:true},'',chapterHref(f.m)); }catch(err){}"),
    ("sim.textContent='进入模拟'", "sim.textContent='进入模块板块 →'"),
]
for old, new in repl:
    if old not in s:
        sys.exit("pattern missing: " + old)
    s = s.replace(old, new, 1)

# 详情面板的“进入模拟”链接也要指向知识网络
old_panel = "var sim=document.createElement('a');sim.className='primary';sim.href=m.sim;"
new_panel = "var sim=document.createElement('a');sim.className='primary';sim.href=chapterHref(m);"
assert old_panel in s
s = s.replace(old_panel, new_panel, 1)

P.write_text(s, encoding="utf-8")
print("patched", P.relative_to(ROOT))
