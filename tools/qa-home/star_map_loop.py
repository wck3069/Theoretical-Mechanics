#!/usr/bin/env python3
"""Red-capable loop v2: 星图点击多次后失效.
Forces finishFlight fallback (iframe preload delayed 5s > 2.5s timeout) via Sec-Fetch-Dest.
A1: homepage state dirty at fallback-nav moment (is-flying/iframe left behind).
A2: after history.back(), if bfcache-persisted, UI hidden / clicks dead.
Exit 1 = RED.
"""
import http.server, json, socketserver, subprocess, sys, threading, time, urllib.request
sys.path.insert(0, '/home/wck/Theoretical-Mechanics/tools/qa-neural')
from cdp import CDP

ROOT = '/home/wck/Theoretical-Mechanics'
PORT = 8097
MODE = sys.argv[2] if len(sys.argv) > 2 else 'fallback'
DELAY = 0.0 if MODE == 'portal' else 5.0

class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)
    def do_GET(self):
        try:
            path = self.path.split('?')[0].split('#')[0]
            dest = self.headers.get('Sec-Fetch-Dest', '')
            if path.endswith('/index.html') and '/chapters/' in path and dest == 'iframe':
                time.sleep(DELAY)
            if '/textures/hi/' in path and dest == 'image':
                time.sleep(1.2)
            super().do_GET()
        except (BrokenPipeError, ConnectionResetError):
            pass
    def log_message(self, *a):
        pass

class S(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

srv = S(('127.0.0.1', PORT), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()

p = subprocess.Popen(['google-chrome', '--headless=new', '--disable-gpu', '--no-sandbox',
                      '--enable-features=BackForwardCache',
                      '--remote-debugging-port=9472', '--remote-allow-origins=*',
                      '--window-size=1440,900', 'about:blank'],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def ev(c, s, tries=8):
    for i in range(tries):
        try:
            return c.cmd('Runtime.evaluate', {'expression': s, 'returnByValue': True}).get('result', {}).get('value')
        except RuntimeError as e:
            if 'navigated or closed' in str(e) or 'Cannot find context' in str(e):
                time.sleep(.4); continue
            raise
    return None

SCAN = '''(function(){
  var cv=document.getElementById('orbitCanvas');
  if(!cv) return {err:'no canvas'};
  var w=innerWidth,h=innerHeight;
  for(var y=Math.round(h*0.18); y<h*0.85; y+=36){
    for(var x=Math.round(w*0.12); x<w*0.88; x+=36){
      cv.dispatchEvent(new MouseEvent('click',{clientX:x,clientY:y,bubbles:true}));
      if(document.body.classList.contains('is-flying')) return {flying:true,x:x,y:y};
    }
  }
  return {flying:false};
})()'''
STATE = '''({isFlying:document.body.classList.contains('is-flying'),
  portalOpen:document.body.classList.contains('portal-open'),
  iframes:document.querySelectorAll('.tm-portal').length,
  uiHidden:(function(){var t=document.querySelector('.topbar');return t?getComputedStyle(t).display==='none':null})(),
  url:location.pathname+location.hash,
  navType:(performance.getEntriesByType('navigation')[0]||{}).type})'''

red = []
try:
    for _ in range(60):
        try:
            pages = json.load(urllib.request.urlopen('http://127.0.0.1:9472/json'))
            ws = next(x['webSocketDebuggerUrl'] for x in pages if x['type'] == 'page'); break
        except Exception:
            time.sleep(.15)
    c = CDP(ws)
    c.cmd('Page.enable')
    c.cmd('Emulation.setDeviceMetricsOverride', {'width': 1440, 'height': 900, 'deviceScaleFactor': 1, 'mobile': False})

    cycles = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    for cyc in range(cycles):
        c.cmd('Page.navigate', {'url': 'http://127.0.0.1:%d/index.html' % PORT})
        time.sleep(2.5)
        r = ev(c, SCAN)
        if not r or not r.get('flying'):
            print('cycle %d: SCAN FAILED: %s' % (cyc, r)); red.append('scan-dead-%d' % cyc); break
        ev(c, 'window.__bfcMarker=42')
        dirty = None
        last_home = None
        max_iframes = 0
        t0 = time.time()
        while time.time() - t0 < 8:
            st = ev(c, STATE)
            if st and 'neural' in (st.get('url') or ''):
                break
            if st:
                last_home = st
                max_iframes = max(max_iframes, st.get('iframes') or 0)
                if st.get('isFlying') and time.time() - t0 > 2.45:
                    dirty = st
            time.sleep(.03)
        time.sleep(1.2)
        after_nav = ev(c, STATE)
        print('cycle %d: after nav: %s' % (cyc, json.dumps(after_nav, ensure_ascii=False)))
        if max_iframes > 1:
            print('cycle %d: A3 IFRAME-RACE max=%d' % (cyc, max_iframes))
            red.append('A3-iframes-%d' % cyc)
        if last_home:
            print('cycle %d: last home state before nav: %s' % (cyc, json.dumps(last_home, ensure_ascii=False)))
        ev(c, 'history.back()')
        time.sleep(2.8)
        back = ev(c, STATE)
        marker = ev(c, 'window.__bfcMarker')
        print('cycle %d: after back: %s | bfcacheMarker=%s' % (cyc, json.dumps(back, ensure_ascii=False), marker))
        if marker == 42 and back and (back.get('isFlying') or back.get('iframes') or back.get('uiHidden')):
            print('cycle %d: A2 BFCACHE-FROZEN (marker survived + dirty state)' % cyc)
            red.append('A2-frozen-%d' % cyc)
        if back and (back.get('iframes') or back.get('isFlying') or back.get('portalOpen')):
            print('cycle %d: A4 BACK-LEFTOVER iframes=%s isFlying=%s' % (cyc, back.get('iframes'), back.get('isFlying')))
            red.append('A4-leftover-%d' % cyc)
        r2 = ev(c, SCAN)
        ok = bool(r2 and r2.get('flying'))
        print('cycle %d: re-scan flying=%s' % (cyc, ok))
        if not ok:
            red.append('rescan-dead-%d' % cyc)
        # leave the post-back flight/portal cleanly for next cycle: navigate fresh next loop
    print('RED: ' + str(red) if red else 'GREEN: no failure detected')
    sys.exit(1 if red else 0)
finally:
    p.terminate(); srv.shutdown()
