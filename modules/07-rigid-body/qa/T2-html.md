# M7-T2 验证证据 — modules/07-rigid-body/index.html

日期：2026-10-27

## 静态检查

命令：`~/.venv-tm/bin/python tools/check_html.py modules/07-rigid-body/index.html`
结果：6/6 项通过，0 项失败，EXIT_CODE=0

## 运行时自测

命令：`google-chrome --headless=new --no-sandbox --disable-gpu --window-size=1440,900 --virtual-time-budget=5000 --dump-dom 'file:///home/wck/Theoretical-Mechanics/modules/07-rigid-body/index.html?selftest=1'`

结果：SELFTEST 5/5 PASS
- ST1 cap centroid hemisphere : d=0.375 ref=0.375
- ST2 cap centroid b=0.5 : d=0.175 ref=0.175
- ST3 disk L : L=0.5 ref=0.5
- ST4 shell inside V=-1/a : V=-1.0
- ST5 shell outside V=-1/(2a) : V=-0.5

## 数值验证

命令：`~/.venv-tm/bin/python modules/07-rigid-body/qa/numeric_check.py`
结果：6/6 PASS
