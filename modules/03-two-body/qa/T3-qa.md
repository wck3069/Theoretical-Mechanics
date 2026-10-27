# M3-T3 QA 证据 — modules/03-two-body

日期：2026-10-27

## 截图

```bash
google-chrome --headless=new --no-sandbox --disable-gpu --window-size=1440,900 --virtual-time-budget=4000 --screenshot=modules/03-two-body/qa/desktop.png 'file:///home/wck/Theoretical-Mechanics/modules/03-two-body/index.html' 2>/dev/null
google-chrome --headless=new --no-sandbox --disable-gpu --window-size=768,1024 --virtual-time-budget=4000 --screenshot=modules/03-two-body/qa/tablet.png 'file:///home/wck/Theoretical-Mechanics/modules/03-two-body/index.html' 2>/dev/null
google-chrome --headless=new --no-sandbox --disable-gpu --window-size=360,640 --virtual-time-budget=4000 --screenshot=modules/03-two-body/qa/mobile.png 'file:///home/wck/Theoretical-Mechanics/modules/03-two-body/index.html' 2>/dev/null
```

PNG 尺寸（Python struct）：

```text
desktop.png 1440 900
tablet.png 768 1024
mobile.png 360 640
```

## 静态检查

```bash
~/.venv-tm/bin/python tools/check_html.py modules/03-two-body/index.html
```

结果：6/6 项通过，0 项失败，EXIT_CODE=0

```bash
~/.venv-tm/bin/python tools/check_html.py catalog.html
```

结果：6/6 项通过，0 项失败，EXIT_CODE=0

## 运行时自测

命令：`google-chrome --headless=new --no-sandbox --disable-gpu --window-size=1440,900 --virtual-time-budget=5000 --dump-dom 'file:///home/wck/Theoretical-Mechanics/modules/03-two-body/index.html?selftest=1'`

结果：SELFTEST 5/5 PASS
- ST1 r1 Jupiter : r1=0.004956 ref=0.004956
- ST2 omega Kepler III : w=0.530129 ref=0.530129
- ST3 v1 Earth : v1=0.000019 ref=0.000019
- ST4 Doppler Jupiter : dl=0.00002075 ref~0.00002075
- ST5 period : P=11.852172 ref=11.852172

## 控制台

命令：`google-chrome --headless=new --no-sandbox --disable-gpu --window-size=1440,900 --virtual-time-budget=4000 --enable-logging=stderr --dump-dom 'file:///home/wck/Theoretical-Mechanics/modules/03-two-body/index.html' 2>&1 1>/dev/null | grep -iE 'CONSOLE|Uncaught|ERROR' | grep -viE 'dbus|GPU|gpu|DevTools'`

结果：（空，无控制台错误）

## 链接检查

结果：LINKS: ALL OK

## 已知问题

- Chrome 无头模式视口最小约 500 px，移动端截图使用 360 但 DOM 度量在 500。
- 圆轨道近似（e≈0），实际椭圆轨道修正未实现。
- 不含相对论效应。
