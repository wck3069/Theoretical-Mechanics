# M6-T2 验证证据 — modules/06-collisions/index.html

日期：2026-10-27

## 静态检查

命令：`~/.venv-tm/bin/python tools/check_html.py modules/06-collisions/index.html`
结果：6/6 项通过，0 项失败，EXIT_CODE=0

## 运行时自测

命令：`google-chrome --headless=new --no-sandbox --disable-gpu --window-size=1440,900 --virtual-time-budget=5000 --dump-dom 'file:///home/wck/Theoretical-Mechanics/modules/06-collisions/index.html?selftest=1'`

结果：SELFTEST 5/5 PASS
- ST1 beta deflection : beta>0
- ST2 alpha_max formula : alpha_max=26.565
- ST3 raindrop v(0)=0 : v0=0
- ST4 collision chain H=4h : H/h=4.0
- ST5 beta_max e=0.5 : beta_max in (30,40)

## 数值验证

命令：`~/.venv-tm/bin/python modules/06-collisions/qa/numeric_check.py`
结果：3/3 PASS
