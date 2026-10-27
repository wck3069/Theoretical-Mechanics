# M5-T2 验证证据 — modules/05-virtual-work/index.html

日期：2026-10-27

## 静态检查

命令：`~/.venv-tm/bin/python tools/check_html.py modules/05-virtual-work/index.html`
结果：6/6 项通过，0 项失败，EXIT_CODE=0

## 运行时自测

命令：`google-chrome --headless=new --no-sandbox --disable-gpu --window-size=1440,900 --virtual-time-budget=5000 --dump-dom 'file:///home/wck/Theoretical-Mechanics/modules/05-virtual-work/index.html?selftest=1'`

结果：SELFTEST 5/5 PASS
- ST1 theta_min formula : theta_min=45.0 ref=45.0
- ST2 theta_min mu=0.25 : theta_min=63.4349 ref=63.4349
- ST3 force balance critical : Nw=0.5 fc=0.5
- ST4 critical angle <1% : err<0.01
- ST5 monotonic mu-theta : t(0.25)>t(1.0)

## 数值验证

命令：`~/.venv-tm/bin/python modules/05-virtual-work/qa/numeric_check.py`
结果：4/4 PASS
