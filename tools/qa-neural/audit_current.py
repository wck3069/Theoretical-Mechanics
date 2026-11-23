import sys, json, time, subprocess, urllib.request, base64
from pathlib import Path
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))
from cdp import CDP

out=Path('/tmp/nqa/current-audit'); out.mkdir(exist_ok=True)
p=subprocess.Popen(['google-chrome','--headless=new','--disable-gpu','--no-sandbox','--remote-debugging-port=9467','--remote-allow-origins=*','about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
    for _ in range(60):
        try:
            pages=json.load(urllib.request.urlopen('http://127.0.0.1:9467/json'))
            ws=next(x['webSocketDebuggerUrl'] for x in pages if x['type']=='page'); break
        except Exception:
            time.sleep(.15)
    c=CDP(ws); c.cmd('Page.enable'); c.cmd('Runtime.enable')
    def ev(expr):
        return c.cmd('Runtime.evaluate',{'expression':expr,'returnByValue':True}).get('result',{}).get('value')
    results=[]
    cases=[('home','/',1440,900),('overview','/neural/#/chapter-01-newton',1440,900),('overview4','/neural/#/chapter-03-lagrangian',1440,900),('module','/neural/#/chapter-03-lagrangian/m11',1440,900),('detail','/neural/#/chapter-03-lagrangian/m11/M11-003',1440,900),('mobile-overview','/neural/#/chapter-01-newton',390,844),('mobile-detail','/neural/#/chapter-03-lagrangian/m11/M11-003',390,844)]
    for name,path,w,h in cases:
        c.cmd('Emulation.setDeviceMetricsOverride',{'width':w,'height':h,'deviceScaleFactor':1,'mobile':w<900})
        c.cmd('Page.navigate',{'url':'http://127.0.0.1:8081'+path}); time.sleep(2.5)
        c.cmd('Runtime.evaluate',{'expression':'window.__auditErrors=[];window.addEventListener("error",function(e){window.__auditErrors.push(e.message);});'})
        shot=c.cmd('Page.captureScreenshot',{'format':'png'})
        (out/(name+'.png')).write_bytes(base64.b64decode(shot['data']))
        record=ev('''(function(){var panel=document.getElementById('panel');return {width:innerWidth,height:innerHeight,hash:location.hash,title:document.title,panelOpen:!!panel&&panel.classList.contains('open'),panelTitle:document.getElementById('pTitle')?document.getElementById('pTitle').textContent:'',body:document.getElementById('pBody')?document.getElementById('pBody').textContent.slice(0,300):'',videos:document.querySelectorAll('video').length,fx:!!document.getElementById('fx'),nodeCount:document.querySelectorAll('#gNodes .node').length};})()''')
        record['case']=name
        if name=='module':
            c.cmd('Runtime.evaluate',{'expression':'''(function(){var el=document.querySelectorAll('#gNodes .node text')[4];var r=el.getBoundingClientRect();window.__pt={x:r.x+r.width/2,y:r.y+r.height/2};})()'''})
            point=ev('window.__pt')
            for typ in ['mousePressed','mouseReleased']:
                c.cmd('Input.dispatchMouseEvent',{'type':typ,'x':point['x'],'y':point['y'],'button':'left','clickCount':1})
            time.sleep(.5)
            record['afterRealClick']=ev('({hash:location.hash,title:document.getElementById("pTitle").textContent,crumbs:document.getElementById("crumbs").textContent})')
            c.cmd('Page.reload'); time.sleep(2)
            record['afterReload']=ev('({hash:location.hash,title:document.getElementById("pTitle").textContent,crumbs:document.getElementById("crumbs").textContent})')
        results.append(record)
    (out/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
    print(json.dumps(results,ensure_ascii=False,indent=2))
finally:
    p.terminate()
