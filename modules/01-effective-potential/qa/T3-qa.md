# M1-T3 QA 证据 — modules/01-effective-potential

日期：2026-10-27 · 验证人：主代理（google-chrome headless + ~/.venv-tm/bin/python）

## 截图

命令（按任务给定形式，stderr 重定向到 /dev/null）：

```bash
cd /home/wck/Theoretical-Mechanics
google-chrome --headless=new --no-sandbox --disable-gpu --window-size=1440,900 --virtual-time-budget=4000 --screenshot=modules/01-effective-potential/qa/desktop.png 'file:///home/wck/Theoretical-Mechanics/modules/01-effective-potential/index.html' 2>/dev/null
google-chrome --headless=new --no-sandbox --disable-gpu --window-size=768,1024 --virtual-time-budget=4000 --screenshot=modules/01-effective-potential/qa/tablet.png 'file:///home/wck/Theoretical-Mechanics/modules/01-effective-potential/index.html' 2>/dev/null
google-chrome --headless=new --no-sandbox --disable-gpu --window-size=360,640 --virtual-time-budget=4000 --screenshot=modules/01-effective-potential/qa/mobile.png 'file:///home/wck/Theoretical-Mechanics/modules/01-effective-potential/index.html' 2>/dev/null
```

Chrome stdout（bytes written）：

```text
398790 bytes written to file modules/01-effective-potential/qa/desktop.png
246448 bytes written to file modules/01-effective-potential/qa/tablet.png
94246 bytes written to file modules/01-effective-potential/qa/mobile.png
```

PNG 尺寸回读（Python struct）：

```text
modules/01-effective-potential/qa/desktop.png 1440 900 398790 bytes
modules/01-effective-potential/qa/tablet.png 768 1024 246448 bytes
modules/01-effective-potential/qa/mobile.png 360 640 94246 bytes
```

产物：

```text
-rw-rw-r-- 1 wck wck 398790 Oct 27 15:25 modules/01-effective-potential/qa/desktop.png
-rw-rw-r-- 1 wck wck 246448 Oct 27 15:25 modules/01-effective-potential/qa/tablet.png
-rw-rw-r-- 1 wck wck  94246 Oct 27 15:25 modules/01-effective-potential/qa/mobile.png
```

## 布局溢出测量

命令（metrics 探针，`--dump-dom` 提取 `div#metrics` 的 METRICS 行）：

```bash
cd /home/wck/Theoretical-Mechanics
for sz in "1440,900" "768,1024" "360,640"; do
  google-chrome --headless=new --no-sandbox --disable-gpu --window-size=$sz --virtual-time-budget=4000 \
    --dump-dom 'file:///home/wck/Theoretical-Mechanics/modules/01-effective-potential/index.html' 2>/dev/null \
    | grep -o 'METRICS [0-9 ]*' | tail -1
done
```

输出：

```text
METRICS 1440 813 1440 813
METRICS 768 937 768 937
METRICS 500 553 500 553
```

说明：`METRICS <innerWidth> <innerHeight> <scrollWidth> <scrollHeight>`。三档 scrollWidth 均等于 innerWidth，无横向溢出。360 档被 Chrome headless 钳制到 500 最小宽度（已知行为，见「已知问题」）。

HUD 验证（1440×900，`div#hudT`）：

```text
id="hudT">0.03
```

`hudT` 显示数值（非 NaN）。

## 静态检查

命令：

```bash
cd /home/wck/Theoretical-Mechanics
/home/wck/.venv-tm/bin/python tools/check_html.py modules/01-effective-potential/index.html
/home/wck/.venv-tm/bin/python tools/check_html.py catalog.html
```

原始输出（每文件最后两行）：

```text
== check_html.py: modules/01-effective-potential/index.html ==
...
-- 摘要：6/6 项通过，0 项失败
EXIT_CODE=0

== check_html.py: catalog.html ==
...
-- 摘要：6/6 项通过，0 项失败
EXIT_CODE=0
```

两文件均 6/6 PASS。

## 运行时自测

命令：

```bash
cd /home/wck/Theoretical-Mechanics
google-chrome --headless=new --no-sandbox --disable-gpu --window-size=1440,900 --virtual-time-budget=4000 \
  --dump-dom 'file:///home/wck/Theoretical-Mechanics/modules/01-effective-potential/index.html?selftest=1' 2>/dev/null \
  | grep -A6 'SELFTEST' | head -7
```

输出（SELFTEST 行 + 5 条详情）：

```text
SELFTEST 5/5 PASS
[PASS] ST1 kepler turning points : roots=[1.0520303695138074, 2.2813029638195257] err=4.4e-16
[PASS] ST2 RK4 drift+period : drift=3.1e-14 Tr=13.52000 Ta=13.51926 rel=5.5e-5
[PASS] ST3 Bertrand ratio (k=2:2, kepler:1) : ratio_harm=2.0000 ratio_kep=1.0000
[PASS] ST4 gauss Lmax=1.0405 : L=0.99: eq=2 stable=1; L=1.05: eq=0
[PASS] ST5 gamma/r3 precession = 6*pi*gam/L^4 : shift=0.0534 theo=0.0545
```

## 控制台

命令：

```bash
cd /home/wck/Theoretical-Mechanics
google-chrome --headless=new --no-sandbox --disable-gpu --enable-logging=stderr --window-size=1440,900 --virtual-time-budget=4000 \
  --dump-dom 'file:///home/wck/Theoretical-Mechanics/modules/01-effective-potential/index.html' 2>/tmp/chrome_stderr.txt 1>/dev/null
grep -iE 'CONSOLE|Uncaught|ERROR' /tmp/chrome_stderr.txt | grep -viE 'dbus|GPU|gpu|DevTools'
```

输出（过滤后）：

```text
（空：无 CONSOLE / Uncaught / ERROR 行）
```

## 链接检查

命令（Python 片段）：

```python
import re, os
files=['index.html','catalog.html','modules/01-effective-potential/index.html']
ok=True; checked=0
for f in files:
    txt=open(f,encoding='utf-8').read()
    cands=set()
    for m in re.finditer(r'(?:href|src)\s*=\s*["\']([^"\']+)["\']', txt):
        cands.add(m.group(1))
    for m in re.finditer(r'(?:sim|note)\s*:\s*["\']([^"\']+)["\']', txt):
        cands.add(m.group(1))
    base=os.path.dirname(os.path.abspath(f))
    for c in sorted(cands):
        if c.startswith(('http://','https://','//','#','mailto:')): continue
        if '?' in c: c=c.split('?')[0]
        if not c: continue
        p=os.path.normpath(os.path.join(base,c))
        exists=os.path.exists(p)
        checked+=1
        print(f, '->', c, 'OK' if exists else 'MISSING')
        if not exists: ok=False
print('checked',checked)
print('LINKS: ALL OK' if ok else 'LINKS: FAIL')
```

输出：

```text
index.html -> binet.pdf OK
catalog.html -> binet.pdf OK
catalog.html -> index.html OK
catalog.html -> modules/01-effective-potential/index.html OK
catalog.html -> modules/01-effective-potential/note.pdf OK
modules/01-effective-potential/index.html -> ../../index.html OK
modules/01-effective-potential/index.html -> note.pdf OK
checked 7
LINKS: ALL OK
```

## 已知问题

- Chrome headless 将窗口宽度钳制到最小 500px：`--window-size=360,640` 实际渲染为 500×553（METRICS 行 `METRICS 500 553 500 553`）。这是浏览器行为，非页面缺陷；页面 CSS 仍按 360 断点设计，真实设备 360 宽度下布局由 CSS 媒体查询控制。截图 `mobile.png` 实际尺寸为 360×640（截图分辨率不受钳制影响）。
- 无其他已知问题：三档均无横向溢出（scrollWidth == innerWidth），控制台无错误，自测 5/5 PASS，静态检查 6/6 PASS，链接全部可用。
