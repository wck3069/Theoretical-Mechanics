# M7-T3 QA 证据 — modules/07-rigid-body

日期：2026-10-27

## 截图

```bash
google-chrome --headless=new --no-sandbox --disable-gpu --window-size=1440,900 --virtual-time-budget=4000 --screenshot=modules/07-rigid-body/qa/desktop.png 'file:///home/wck/Theoretical-Mechanics/modules/07-rigid-body/index.html' 2>/dev/null
google-chrome --headless=new --no-sandbox --disable-gpu --window-size=768,1024 --virtual-time-budget=4000 --screenshot=modules/07-rigid-body/qa/tablet.png 'file:///home/wck/Theoretical-Mechanics/modules/07-rigid-body/index.html' 2>/dev/null
google-chrome --headless=new --no-sandbox --disable-gpu --window-size=360,640 --virtual-time-budget=4000 --screenshot=modules/07-rigid-body/qa/mobile.png 'file:///home/wck/Theoretical-Mechanics/modules/07-rigid-body/index.html' 2>/dev/null
```

PNG 尺寸（Python struct）：

```text
desktop.png 1440 900
tablet.png 768 1024
mobile.png 360 640
```

## 静态检查

```bash
~/.venv-tm/bin/python tools/check_html.py modules/07-rigid-body/index.html
```

结果：6/6 项通过，0 项失败，EXIT_CODE=0

```bash
~/.venv-tm/bin/python tools/check_html.py catalog.html
```

结果：6/6 项通过，0 项失败，EXIT_CODE=0

## 运行时自测

命令：`google-chrome --headless=new --no-sandbox --disable-gpu --window-size=1440,900 --virtual-time-budget=5000 --dump-dom 'file:///home/wck/Theoretical-Mechanics/modules/07-rigid-body/index.html?selftest=1'`

结果：SELFTEST 5/5 PASS
- ST1 cap centroid hemisphere : d=0.375 ref=0.375
- ST2 cap centroid b=0.5 : d=0.175 ref=0.175
- ST3 disk L : L=0.5 ref=0.5
- ST4 shell inside V=-1/a : V=-1.0
- ST5 shell outside V=-1/(2a) : V=-0.5

## 控制台

命令：`google-chrome --headless=new --no-sandbox --disable-gpu --window-size=1440,900 --virtual-time-budget=4000 --enable-logging=stderr --dump-dom 'file:///home/wck/Theoretical-Mechanics/modules/07-rigid-body/index.html' 2>&1 1>/dev/null | grep -iE 'CONSOLE|Uncaught|ERROR' | grep -viE 'dbus|GPU|gpu|DevTools'`

结果：（空，无控制台错误）

## 链接检查

结果：LINKS: ALL OK

## 已知问题

- Chrome 无头模式视口最小约 500 px，移动端截图使用 360 但 DOM 度量在 500。
- 不含相对论效应。
