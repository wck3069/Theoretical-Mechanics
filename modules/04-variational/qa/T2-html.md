# M4-T2 验证证据 — modules/04-variational/index.html

日期：2026-10-27

## 静态检查

命令：`~/.venv-tm/bin/python tools/check_html.py modules/04-variational/index.html`
结果：6/6 项通过，0 项失败，EXIT_CODE=0

## 运行时自测

命令：`google-chrome --headless=new --no-sandbox --disable-gpu --window-size=1440,900 --virtual-time-budget=5000 --dump-dom 'file:///home/wck/Theoretical-Mechanics/modules/04-variational/index.html?selftest=1'`

结果：SELFTEST 5/5 PASS
- ST1 isochrony cycloid : T=3.14159
- ST2 T=pi*sqrt(a/g) : T=3.14159 ref=3.14159
- ST3 general T0 : T0=3.14159 ref=3.14159
- ST4 Snell law : lhs=0.500000
- ST5 discretization isochrony : discr<0.5%

## 数值验证

命令：`~/.venv-tm/bin/python modules/04-variational/qa/numeric_check.py`
结果：4/4 PASS
