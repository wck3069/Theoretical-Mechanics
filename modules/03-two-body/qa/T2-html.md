# M3-T2 验证证据 — modules/03-two-body/index.html

日期：2026-10-27

## 静态检查

命令：`~/.venv-tm/bin/python tools/check_html.py modules/03-two-body/index.html`
结果：6/6 项通过，0 项失败，EXIT_CODE=0

## 运行时自测

命令：`google-chrome --headless=new --no-sandbox --disable-gpu --window-size=1440,900 --virtual-time-budget=5000 --dump-dom 'file:///home/wck/Theoretical-Mechanics/modules/03-two-body/index.html?selftest=1'`

结果：SELFTEST 5/5 PASS
- ST1 r1 Jupiter : r1=0.004956 ref=0.004956
- ST2 omega Kepler III : w=0.530129 ref=0.530129
- ST3 v1 Earth : v1=0.000019 ref=0.000019
- ST4 Doppler Jupiter : dl=0.00002075 ref~0.00002075
- ST5 period : P=11.852172 ref=11.852172

## 数值验证

命令：`~/.venv-tm/bin/python modules/03-two-body/qa/numeric_check.py`
结果：6/6 PASS
