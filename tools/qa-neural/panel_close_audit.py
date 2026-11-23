#!/usr/bin/env python3
"""panel_close_audit.py — 桌面预览面板 ✕ 回归（用户报告：点开小标题右面框关闭键不可以使用）。

流程：卡片首击=预览面板（hash 不变）→ 物理点 ✕ 必须关闭 → 再击同卡=进入模块视图
→ ✕ 回总览。修复前 closeDetail 无 preview 分支，✕ 空转（RED）。
用法: BASE=http://127.0.0.1:8081 python3 tools/qa-neural/panel_close_audit.py
退出码 0=GREEN 1=RED。
"""
import json, os, subprocess, sys, time, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cdp import CDP

BASE = os.environ.get('BASE', 'http://127.0.0.1:8081')
URL = BASE + '/neural/index.html#/chapter-01-newton'
p = subprocess.Popen(['google-chrome', '--headless=new', '--disable-gpu', '--no-sandbox',
                      '--remote-debugging-port=9474', '--remote-allow-origins=*', 'about:blank'],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def ev(c, s, tries=6):
    for _ in range(tries):
        try:
            return c.cmd('Runtime.evaluate', {'expression': s, 'returnByValue': True}).get('result', {}).get('value')
        except RuntimeError as e:
            if 'navigated or closed' in str(e) or 'Cannot find context' in str(e):
                time.sleep(.4); continue
            raise
    return None

STATE = '''({hash:location.hash,panel:document.getElementById('panel').classList.contains('open'),
  preview:!!(window.__stateProbe&&window.__stateProbe())})'''
PLAIN = '''({hash:location.hash,panel:document.getElementById('panel').classList.contains('open'),
  title:(document.getElementById('pTitle')||{}).textContent||'',
  cards:document.querySelectorAll('#gBells .jcard').length,
  nodes:document.querySelectorAll('#gNodes .node').length})'''

def click(c, x, y):
    for typ in ['mousePressed', 'mouseReleased']:
        c.cmd('Input.dispatchMouseEvent', {'type': typ, 'x': x, 'y': y, 'button': 'left', 'clickCount': 1})

def center(c, sel):
    for _ in range(8):
        pt = ev(c, '''(function(){var e=document.querySelector(%s);if(!e)return null;
          var b=e.getBoundingClientRect();return {x:b.x+b.width/2,y:b.y+b.height/2,w:b.width};})()''' % json.dumps(sel))
        if pt:
            return pt
        time.sleep(.5)
    return None

fails = []
try:
    for _ in range(60):
        try:
            pages = json.load(urllib.request.urlopen('http://127.0.0.1:9474/json'))
            ws = next(x['webSocketDebuggerUrl'] for x in pages if x['type'] == 'page'); break
        except Exception:
            time.sleep(.15)
    c = CDP(ws)
    c.cmd('Page.enable')
    c.cmd('Emulation.setDeviceMetricsOverride', {'width': 1440, 'height': 900, 'deviceScaleFactor': 1, 'mobile': False})
    c.cmd('Page.navigate', {'url': URL}); time.sleep(3.5)

    pt = center(c, '#gBells .jcard')
    click(c, pt['x'], pt['y']); time.sleep(1.0)
    s1 = ev(c, PLAIN)
    print('1 first card click (preview):', json.dumps(s1, ensure_ascii=False))
    if not (s1 and s1['panel'] and s1['hash'] == '#/chapter-01-newton'):
        fails.append('preview-open')

    pc = center(c, '#pClose')
    click(c, pc['x'], pc['y']); time.sleep(1.0)
    s2 = ev(c, PLAIN)
    print('2 physical X on preview:', json.dumps(s2, ensure_ascii=False))
    if s2 and s2['panel']:
        fails.append('X-DEAD-ON-PREVIEW')

    pt = center(c, '#gBells .jcard')
    click(c, pt['x'], pt['y']); time.sleep(.8)
    pt = center(c, '#gBells .jcard')
    click(c, pt['x'], pt['y']); time.sleep(1.2)
    s3 = ev(c, PLAIN)
    print('3 second click (module view):', json.dumps(s3, ensure_ascii=False))
    if not (s3 and '/m0' in s3['hash'] and s3['nodes'] > 0):
        fails.append('module-enter')

    pc = center(c, '#pClose')
    click(c, pc['x'], pc['y']); time.sleep(1.0)
    s4 = ev(c, PLAIN)
    print('4 X on module view:', json.dumps(s4, ensure_ascii=False))
    if not (s4 and not s4['panel'] and s4['hash'] == '#/chapter-01-newton'):
        fails.append('X-module-view')

    print('RED: ' + str(fails) if fails else 'GREEN: panel close works in preview and module view')
    sys.exit(1 if fails else 0)
finally:
    p.terminate()
