#!/usr/bin/env python3
"""Minimal CDP client (stdlib only): open page, run expression, screenshot."""
import base64, json, os, re, socket, struct, subprocess, sys, time, urllib.request

def ws_connect(url):
    m = re.match(r'ws://([^:/]+):(\d+)/(.*)', url)
    host, port, path = m.group(1), int(m.group(2)), m.group(3)
    s = socket.create_connection((host, port))
    key = base64.b64encode(os.urandom(16)).decode()
    req = (f"GET /{path} HTTP/1.1\r\nHost: {host}:{port}\r\nUpgrade: websocket\r\n"
           f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n")
    s.sendall(req.encode())
    resp = b''
    while b'\r\n\r\n' not in resp:
        resp += s.recv(4096)
    return s

def ws_send(s, data):
    payload = data.encode()
    hdr = bytes([0x81])
    n = len(payload)
    mask = os.urandom(4)
    if n < 126: hdr += bytes([0x80 | n])
    elif n < 65536: hdr += bytes([0x80 | 126]) + struct.pack('>H', n)
    else: hdr += bytes([0x80 | 127]) + struct.pack('>Q', n)
    s.sendall(hdr + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(payload)))

def _recv_exact(s, n):
    buf = b''
    while len(buf) < n:
        c = s.recv(n - len(buf))
        if not c: raise IOError('ws closed')
        buf += c
    return buf

def ws_recv(s):
    b0, b1 = _recv_exact(s, 2)
    ln = b1 & 0x7f
    if ln == 126: ln = struct.unpack('>H', _recv_exact(s, 2))[0]
    elif ln == 127: ln = struct.unpack('>Q', _recv_exact(s, 8))[0]
    return _recv_exact(s, ln)

class CDP:
    def __init__(self, wsurl):
        self.s = ws_connect(wsurl); self.id = 0
    def cmd(self, method, params=None):
        self.id += 1; mid = self.id
        ws_send(self.s, json.dumps({'id': mid, 'method': method, 'params': params or {}}))
        while True:
            msg = json.loads(ws_recv(self.s))
            if msg.get('id') == mid:
                if 'error' in msg: raise RuntimeError(msg['error'])
                return msg.get('result', {})

def main():
    url = sys.argv[1]
    expr = sys.argv[2] if len(sys.argv) > 2 else ''
    shot = sys.argv[3] if len(sys.argv) > 3 else ''
    w, h = (1440, 900)
    proc = subprocess.Popen(
        ['/usr/bin/google-chrome', '--headless=new', '--disable-gpu', '--no-sandbox',
         '--remote-debugging-port=9333', '--window-size=%d,%d' % (w, h),
         '--remote-allow-origins=*', 'about:blank'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(40):
            try:
                targets = json.load(urllib.request.urlopen('http://127.0.0.1:9333/json'))
                page = next(t for t in targets if t['type'] == 'page')
                break
            except Exception:
                time.sleep(0.25)
        cdp = CDP(page['webSocketDebuggerUrl'])
        cdp.cmd('Page.enable')
        cdp.cmd('Page.navigate', {'url': url})
        time.sleep(4.0)   # real wall-clock so media actually plays
        if expr:
            r = cdp.cmd('Runtime.evaluate', {'expression': expr, 'returnByValue': True, 'awaitPromise': True})
            print(json.dumps(r.get('result', {}).get('value'), ensure_ascii=False, indent=1))
        if shot:
            r = cdp.cmd('Page.captureScreenshot', {'format': 'png'})
            open(shot, 'wb').write(base64.b64decode(r['data']))
            print('shot:', shot)
    finally:
        proc.terminate()

if __name__ == '__main__':
    main()
