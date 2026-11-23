import sys,json,time,subprocess,urllib.request
sys.path.insert(0,str(__import__('pathlib').Path(__file__).resolve().parent))
from cdp import CDP
import os
BASE=os.environ.get('BASE','http://127.0.0.1:8099')
p=subprocess.Popen(['google-chrome','--headless=new','--disable-gpu','--no-sandbox','--remote-debugging-port=9468','--remote-allow-origins=*','about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
    for _ in range(60):
        try:
            pages=json.load(urllib.request.urlopen('http://127.0.0.1:9468/json')); ws=next(x['webSocketDebuggerUrl'] for x in pages if x['type']=='page');break
        except Exception: time.sleep(.15)
    c=CDP(ws);c.cmd('Page.enable');c.cmd('Emulation.setDeviceMetricsOverride',{'width':1440,'height':900,'deviceScaleFactor':1,'mobile':False})
    def ev(s):return c.cmd('Runtime.evaluate',{'expression':s,'returnByValue':True}).get('result',{}).get('value')
    def nav(path):c.cmd('Page.navigate',{'url':BASE+path});time.sleep(1.7)
    def state():return ev('({url:location.href,hash:location.hash,crumb:document.getElementById("crumbs").textContent,title:document.getElementById("pTitle").textContent,panel:document.getElementById("panel").classList.contains("open"),nodes:document.querySelectorAll("#gNodes .node").length})')
    def click(sel):
        pt=ev('(function(){var e=document.querySelector('+json.dumps(sel)+');var b=e.getBoundingClientRect();var x=b.x+b.width/2,y=b.y+b.height/2,t=document.elementFromPoint(x,y);return {x:x,y:y,hit:t.tagName,hitClass:t.getAttribute("class")};})()')
        for typ in ['mousePressed','mouseReleased']:c.cmd('Input.dispatchMouseEvent',{'type':typ,'x':pt['x'],'y':pt['y'],'button':'left','clickCount':1})
        time.sleep(.3);return pt
    def esc():
        c.cmd('Input.dispatchKeyEvent',{'type':'keyDown','key':'Escape','code':'Escape','windowsVirtualKeyCode':27});c.cmd('Input.dispatchKeyEvent',{'type':'keyUp','key':'Escape','code':'Escape','windowsVirtualKeyCode':27});time.sleep(.3)
    out={}
    nav('/neural/#/chapter-01-newton');out['moduleCard']={'before':state(),'hit':click('#gBells .jcard'),'after':state()}
    nav('/neural/#/chapter-01-newton');out['jellyLayerRetired']={'children':ev('document.querySelectorAll("#jellyLayer *").length'),'videos':ev('document.querySelectorAll("video").length')}
    nav('/neural/#/chapter-03-lagrangian/m11');out['moduleClose']={'before':state(),'hit':click('#pClose'),'after':state()}
    nav('/neural/#/chapter-03-lagrangian/m11/M11-004');out['nodeEsc']={'before':state()};esc();out['nodeEsc']['first']=state();esc();out['nodeEsc']['second']=state()
    nav('/neural/#/chapter-01-newton');out['overviewEsc']={'before':state()};esc();out['overviewEsc']['after']=state()
    nav('/neural/#/chapter-03-lagrangian/m11/bogus');out['invalidNode']={'state':state(),'notice':ev('document.getElementById("notice").className')}
    nav('/neural/#/chapter-01-newton');out['orb']={'hit':click('#orb .core')};time.sleep(1);out['orb']['destination']=ev('location.pathname')
    print(json.dumps(out,ensure_ascii=False,indent=2))
finally:p.terminate()
