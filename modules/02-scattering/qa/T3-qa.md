# M2-T3 QA 证据 — modules/02-scattering

日期：2026-10-27

## 截图

```bash
google-chrome --headless=new --no-sandbox --disable-gpu --window-size=1440,900 --virtual-time-budget=4000 --screenshot=modules/02-scattering/qa/desktop.png 'file:///home/wck/Theoretical-Mechanics/modules/02-scattering/index.html' 2>/dev/null
google-chrome --headless=new --no-sandbox --disable-gpu --window-size=768,1024 --virtual-time-budget=4000 --screenshot=modules/02-scattering/qa/tablet.png 'file:///home/wck/Theoretical-Mechanics/modules/02-scattering/index.html' 2>/dev/null
google-chrome --headless=new --no-sandbox --disable-gpu --window-size=360,640 --virtual-time-budget=4000 --screenshot=modules/02-scattering/qa/mobile.png 'file:///home/wck/Theoretical-Mechanics/modules/02-scattering/index.html' 2>/dev/null
```

PNG 尺寸（Python struct）：

```text
desktop.png 1440 900
tablet.png 768 1024
mobile.png 360 640
```

## 静态检查

```bash
~/.venv-tm/bin/python tools/check_html.py modules/02-scattering/index.html
```

结果：6/6 项通过，0 项失败，EXIT_CODE=0

```bash
~/.venv-tm/bin/python tools/check_html.py catalog.html
```

结果：6/6 项通过，0 项失败，EXIT_CODE=0

## 运行时自测

命令：`google-chrome --headless=new --no-sandbox --disable-gpu --window-size=1440,900 --virtual-time-budget=5000 --dump-dom 'file:///home/wck/Theoretical-Mechanics/modules/02-scattering/index.html?selftest=1'`

结果：SELFTEST 5/5 PASS
- ST1 scatter angle formula : theta=0.920151 ref=0.920151
- ST2 dSigma/dOmega at pi/2 : ds=0.282942 ref=0.282942
- ST3 b_c formula : bc=1.414214 ref=1.414214
- ST4 sigma capture : sigma=6.283185 ref=6.283185
- ST5 trajectory theta vs formula : PASS

## 控制台

命令：`google-chrome --headless=new --no-sandbox --disable-gpu --window-size=1440,900 --virtual-time-budget=4000 --enable-logging=stderr --dump-dom 'file:///home/wck/Theoretical-Mechanics/modules/02-scattering/index.html' 2>&1 1>/dev/null | grep -iE 'CONSOLE|Uncaught|ERROR' | grep -viE 'dbus|GPU|gpu|DevTools'`

结果：（空，无控制台错误）

## 链接检查

Python 片段检查 index.html、catalog.html、modules/02-scattering/index.html 中所有 href/src 及 JS 中的 sim/note 字符串，解析相对路径并验证文件存在。

结果：LINKS: ALL OK

## 已知问题

- Chrome 无头模式视口最小约 500 px，移动端截图使用 360 但 DOM 度量在 500。
- 排斥势 k/r² 为长程势，总散射截面发散（非 bug，物理结论）。
- 吸引势 -α/r⁴ 在 r→0 时 V→-∞，数值积分在 r<0.05 停止。
