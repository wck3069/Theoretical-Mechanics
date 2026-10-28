#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""layout_qa.py —— 无头 Chrome 确定性布局检查。

用法：
  python3 tools/layout_qa.py [--viewport 1440x900] [--viewport 390x844] [页面 ...]

检查项：横向溢出、关键浮层越界、关键浮层互相遮挡、可见文本字号 < 11px、
canvas 尺寸为 0。页面在临时目录中复制后注入检查脚本，不改动仓库文件。
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHROME = shutil.which("google-chrome") or "/usr/bin/google-chrome"

QA_JS = """
<script>
(function(){
  function rect(e){var b=e.getBoundingClientRect();return {l:Math.round(b.left),t:Math.round(b.top),r:Math.round(b.right),b:Math.round(b.bottom),w:Math.round(b.width),h:Math.round(b.height)};}
  function visible(e){var s=getComputedStyle(e);return s.display!=='none'&&s.visibility!=='hidden'&&s.opacity!=='0';}
  function area(a,b){var w=Math.min(a.r,b.r)-Math.max(a.l,b.l);var h=Math.min(a.b,b.b)-Math.max(a.t,b.t);return w>4&&h>4?w*h:0;}
  var HOMEPAGE=['.hero','#catalog','.cmdbar','.hud','#detailView','#drawer','#tmai-panel','#tmai-launcher','.footnote'];
  var MODULE=['.brand','.hud','.panel','.tm-orbit-nav'];
  var isHome=!!document.querySelector('.hero');
  var sels=isHome?HOMEPAGE:MODULE;
  var boxes={};
  var out={vw:innerWidth,vh:innerHeight,sw:document.documentElement.scrollWidth,sh:document.documentElement.scrollHeight,page:isHome?'home':'module',elements:[],overlaps:[],offscreen:[],tiny:[],canvases:[]};
  out.overflowX=out.sw>out.vw+1;
  sels.forEach(function(s){var e=document.querySelector(s);if(e&&visible(e)){var r=rect(e);boxes[s]=r;out.elements.push({s:s,r:r,fs:getComputedStyle(e).fontSize});}});
  var keys=Object.keys(boxes);
  for(var i=0;i<keys.length;i++)for(var j=i+1;j<keys.length;j++){
    var a=boxes[keys[i]],b=boxes[keys[j]];var ar=area(a,b);
    if(ar>0) out.overlaps.push({a:keys[i],b:keys[j],area:ar});
  }
  var CLOSED={'#drawer':1,'#catalog':1};
  keys.forEach(function(k){var r=boxes[k];
    if(CLOSED[k]){var el=document.querySelector(k);if(!el||!el.classList.contains('open'))return;}
    if(r.l<-2||r.t<-2||r.r>out.vw+2||r.b>out.vh+2) out.offscreen.push({s:k,r:r});
  });
  var all=document.querySelectorAll('body *');
  for(var n=0;n<all.length;n++){
    var e=all[n];if(!visible(e))continue;
    var txt=(e.textContent||'').trim();if(!txt||e.children.length>0)continue;
    var fs=parseFloat(getComputedStyle(e).fontSize);
    if(fs&&fs<11) out.tiny.push({tag:e.tagName,cls:String(e.className||'').slice(0,40),fs:fs,txt:txt.slice(0,24)});
  }
  out.tiny=out.tiny.slice(0,20);
  var cs=document.querySelectorAll('canvas');
  for(var c=0;c<cs.length;c++){var cv=cs[c];out.canvases.push({id:cv.id||String(cv.className||''),w:cv.width,h:cv.height,cw:cv.clientWidth,ch:cv.clientHeight});}
  var pre=document.createElement('pre');pre.id='tm-qa';pre.textContent='QARESULT'+JSON.stringify(out);document.body.appendChild(pre);
})();
</script>
"""


def build_page(src: Path, dst: Path) -> None:
    text = src.read_text(encoding="utf-8")
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text.replace("</body>", QA_JS + "</body>"), encoding="utf-8")


def run_chrome(url: str, size: str, profile: Path) -> str:
    proc = subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
         "--user-data-dir=" + str(profile), "--hide-scrollbars",
         "--virtual-time-budget=6000", "--window-size=" + size.replace("x", ","),
         "--dump-dom", url],
        capture_output=True, text=True, timeout=90)
    return proc.stdout


def parse(dom: str) -> dict | None:
    m = re.search(r"QARESULT(\{.*?\})</pre>", dom, re.DOTALL)
    if not m:
        return None
    return json.loads(m.group(1))


def summarize(tag: str, data: dict) -> bool:
    problems = []
    tag = tag + " [%dx%d]" % (data["vw"], data["vh"])
    if data["overflowX"]:
        problems.append("横向溢出 %d>%d" % (data["sw"], data["vw"]))
    for o in data["offscreen"]:
        r = o["r"]
        if r["r"] > 2 and r["b"] > 2:
            problems.append("越界 %s %s" % (o["s"], r))
    for o in data["overlaps"]:
        problems.append("遮挡 %s×%s %dpx²" % (o["a"], o["b"], o["area"]))
    if data["tiny"]:
        problems.append("小字号 %d 处(最小 %s)" % (
            len(data["tiny"]), min(t["fs"] for t in data["tiny"])))
    for c in data["canvases"]:
        if c["w"] == 0 or c["h"] == 0:
            problems.append("画布为零 %s" % c["id"])
    ok = not problems
    print("%s  %-46s  %s" % ("PASS" if ok else "FAIL", tag,
                             "ok" if ok else " | ".join(problems[:4])))
    if data["tiny"]:
        for t in data["tiny"][:5]:
            print("        tiny %5.1fpx <%s class=%s> %s" % (
                t["fs"], t["tag"], t["cls"], t["txt"]))
    return ok


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--viewport", action="append", default=[])
    ap.add_argument("pages", nargs="*")
    args = ap.parse_args(argv)
    sizes = args.viewport or ["1440x900", "390x844"]
    pages = args.pages or (["index.html"] + [str(p) for p in sorted(ROOT.glob("modules/*/index.html"))])
    tmp = Path(tempfile.mkdtemp(prefix="tmqa-"))
    bad = 0
    try:
        for page in pages:
            src = (ROOT / page).resolve()
            rel = src.relative_to(ROOT)
            dst = tmp / rel
            build_page(src, dst)
            for size in sizes:
                data = parse(run_chrome(dst.as_uri(), size, tmp / ("prof-" + str(abs(hash((page, size)))))))
                if data is None:
                    print("FAIL  %-46s  无 QARESULT" % (str(rel) + " @" + size))
                    bad += 1
                    continue
                if not summarize(str(rel) + " @" + size, data):
                    bad += 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("-- %d/%d 检查通过" % (len(pages) * len(sizes) - bad, len(pages) * len(sizes)))
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
