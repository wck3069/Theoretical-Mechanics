#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pixel_audit.py — deterministic visual-QA proxy (no vision model available).

Screenshots every surface, then judges with pixel statistics + DOM geometry:
  blank/dead regions, edge density, colour presence, horizontal overflow,
  clipped text, broken images, JS errors, missing key elements.
Screenshots + summary saved to /tmp/nqa/pixels/ for human review.
Exit 0 = all cases PASS (warnings allowed), 1 = any FAIL, 2 = harness error.
"""
import argparse, base64, io, json, statistics, subprocess, sys, time, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cdp import CDP
from PIL import Image, ImageFilter

OUT = Path('/tmp/nqa/pixels'); OUT.mkdir(parents=True, exist_ok=True)

CASES = [
    # (name, path, w, h, required CSS selector)
    ('home',            '/', 1440, 900, 'canvas,#solar,#planets,canvas#scene'),
    ('neural-desktop',  '/neural/#/chapter-01-newton', 1440, 900, '#orb'),
    ('neural-rel',      '/neural/#/chapter-07-relativity/m12', 1440, 900, '#panel'),
    ('neural-mobile',   '/neural/#/chapter-03-lagrangian', 390, 844, '#orb'),
    ('ch01',            '/chapters/01-newton/index.html', 1440, 900, '.card'),
    ('ch07',            '/chapters/07-relativity/index.html', 1440, 900, '.card'),
    ('ch07-mobile',     '/chapters/07-relativity/index.html', 390, 844, '.card'),
    ('manu-hw1',        '/chapters/01-newton/manuscripts/hw1.html', 1440, 900, 'svg,img'),
    ('manu-var',        '/chapters/02-variational/manuscripts/variational.html', 1440, 900, 'svg,img'),  # moved by manuscript surgery
    ('manu-ch2',        '/chapters/01-newton/manuscripts/chapter2.html', 1440, 900, 'svg,img'),          # moved by manuscript surgery
    ('mod00',           '/modules/00-binet/index.html', 1440, 900, 'canvas'),
    ('mod08',           '/modules/08-kinematics/index.html', 1440, 900, 'canvas'),
    ('mod10',           '/modules/10-coupled-systems/index.html', 1440, 900, 'canvas'),
    ('mod13',           '/modules/13-lightcone-worldlines/index.html', 1440, 900, 'canvas'),
    ('mod14',           '/modules/14-foucault-rose/index.html', 1440, 900, 'canvas'),
    ('mod15',           '/modules/15-lagrange-points/index.html', 1440, 900, 'canvas'),
    ('mod16',           '/modules/16-doppler-beaming/index.html', 1440, 900, 'canvas'),
    ('stub-redirect',   '/chapters/01-particle/index.html', 1440, 900, 'a'),
    ('stub-manu',       '/chapters/03-lagrangian/manuscripts/variational.html', 1440, 900, 'a'),
]

JS_PROBE = r'''(function(req){
  var out={errors: window.__auditErrors||null,
    hscroll: document.documentElement.scrollWidth > innerWidth+4,
    docScrollW: document.documentElement.scrollWidth, innerW: innerWidth,
    fonts: document.fonts ? document.fonts.status : 'n/a',
    brokenImgs: [].slice.call(document.images).filter(function(i){return i.complete&&i.naturalWidth===0;}).slice(0,5).map(function(i){return i.src;}),
    clipped: [], missing: true};
  if(req){ for (var s of req.split(',')) { try{ if(document.querySelector(s.trim())){ out.missing=false; break; } }catch(e){} } }
  [].slice.call(document.querySelectorAll('body *')).forEach(function(e){
    if(out.clipped.length>=6) return;
    var s=getComputedStyle(e);
    if(s.display==='none'||s.visibility==='hidden') return;
    if(s.overflowX==='visible'&&s.overflowY==='visible') return;
    if(e.scrollWidth>e.clientWidth+6||e.scrollHeight>e.clientHeight+6){
      var t=(e.textContent||'').trim().slice(0,28);
      if(t) out.clipped.push({tag:e.tagName,cls:String(e.className).slice(0,32),
        sw:e.scrollWidth,cw:e.clientWidth,sh:e.scrollHeight,ch:e.clientHeight,txt:t});
    }
  });
  return out;
})'''

def pixel_stats(png: bytes) -> dict:
    img = Image.open(io.BytesIO(png)).convert('RGB')
    small = img.resize((240, 135))
    gray = small.convert('L')
    gp = list(gray.tobytes())
    stdev = statistics.pstdev(gp)
    mean = statistics.mean(gp)
    cells = []
    for cy in range(3):
        for cx in range(3):
            box = gray.crop((cx * 80, cy * 45, cx * 80 + 80, cy * 45 + 45))
            cells.append(statistics.pstdev(list(box.tobytes())))
    edges = statistics.mean(list(gray.filter(ImageFilter.FIND_EDGES).tobytes()))
    rgb = small.tobytes()
    sat = statistics.mean(max(rgb[i:i + 3]) - min(rgb[i:i + 3]) for i in range(0, len(rgb), 3))
    return dict(mean=round(mean, 1), stdev=round(stdev, 1), edge=round(edges, 2),
                sat=round(sat, 1), dead_cells=sum(1 for c in cells if c < 1.2), cells=[round(c, 1) for c in cells])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default='http://127.0.0.1:8081')
    ap.add_argument('--port', type=int, default=9469)
    ap.add_argument('--only', default='', help='comma list of case names to run')
    args = ap.parse_args()
    cases = [c for c in CASES if not args.only or c[0] in args.only.split(',')]

    proc = subprocess.Popen(
        ['google-chrome', '--headless=new', '--disable-gpu', '--no-sandbox',
         f'--remote-debugging-port={args.port}', '--remote-allow-origins=*', 'about:blank'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        ws = None
        for _ in range(60):
            try:
                pages = json.load(urllib.request.urlopen(f'http://127.0.0.1:{args.port}/json'))
                ws = next(x['webSocketDebuggerUrl'] for x in pages if x['type'] == 'page')
                break
            except Exception:
                time.sleep(0.15)
        if not ws:
            print('chrome did not come up', file=sys.stderr); return 2
        c = CDP(ws)
        c.cmd('Page.enable')
        c.cmd('Page.addScriptToEvaluateOnNewDocument',
              {'source': 'window.__auditErrors=[];window.addEventListener("error",function(e){window.__auditErrors.push(String(e.message).slice(0,200));});'})
        results = []
        for name, path, w, h, req in cases:
            c.cmd('Emulation.setDeviceMetricsOverride',
                  {'width': w, 'height': h, 'deviceScaleFactor': 1, 'mobile': w < 900})
            c.cmd('Page.navigate', {'url': args.base + path})
            time.sleep(2.8)
            shot = c.cmd('Page.captureScreenshot', {'format': 'png'})
            png = base64.b64decode(shot['data'])
            (OUT / f'{name}.png').write_bytes(png)
            px = pixel_stats(png)
            dom = c.cmd('Runtime.evaluate',
                        {'expression': JS_PROBE + '(' + json.dumps(req) + ')', 'returnByValue': True}
                        ).get('result', {}).get('value') or {}
            fails, warns = [], []
            if px['stdev'] < 1.5:
                fails.append(f'blank page (stdev={px["stdev"]})')
            if px['edge'] < 0.5:
                fails.append(f'no edges (edge={px["edge"]})')
            if px['dead_cells'] >= 6:
                fails.append(f'{px["dead_cells"]}/9 dead cells')
            if dom.get('hscroll'):
                fails.append(f'h-overflow doc={dom.get("docScrollW")} > {dom.get("innerW")}')
            if dom.get('brokenImgs'):
                fails.append(f'broken imgs: {dom["brokenImgs"]}')
            if dom.get('errors'):
                fails.append(f'js errors: {dom["errors"][:3]}')
            if dom.get('missing'):
                fails.append(f'required missing: {req}')
            if dom.get('clipped'):
                warns.append(f'{len(dom["clipped"])} clipped (may be legit scrollers)')
            if px['sat'] < 3:
                warns.append(f'mono chrome (sat={px["sat"]})')
            results.append(dict(case=name, verdict='FAIL' if fails else 'PASS',
                                fails=fails, warns=warns, pixels=px,
                                clipped=dom.get('clipped', [])[:6],
                                shot=str(OUT / f'{name}.png')))
        (OUT / 'summary.json').write_text(json.dumps(results, ensure_ascii=False, indent=2))
        bad = [r for r in results if r['verdict'] == 'FAIL']
        for r in results:
            line = f'{r["case"]:16s} {r["verdict"]}  mean={r["pixels"]["mean"]:5} sd={r["pixels"]["stdev"]:5} edge={r["pixels"]["edge"]:5} sat={r["pixels"]["sat"]:4}'
            for f in r['fails']: line += f'\n    FAIL: {f}'
            for wn in r['warns']: line += f'\n    warn: {wn}'
            print(line)
        print(f'\n{len(results)-len(bad)}/{len(results)} PASS · shots+summary in {OUT}')
        return 1 if bad else 0
    finally:
        proc.terminate()


if __name__ == '__main__':
    raise SystemExit(main())
