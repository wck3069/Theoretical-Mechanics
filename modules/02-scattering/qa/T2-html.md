# M2-T2 验证证据 — modules/02-scattering/index.html

日期：2026-10-27

## 静态检查

命令：`~/.venv-tm/bin/python tools/check_html.py modules/02-scattering/index.html`
结果：6/6 项通过，0 项失败，EXIT_CODE=0

## 运行时自测

命令：`google-chrome --headless=new --no-sandbox --disable-gpu --window-size=1440,900 --virtual-time-budget=5000 --dump-dom 'file:///home/wck/Theoretical-Mechanics/modules/02-scattering/index.html?selftest=1'`

结果：SELFTEST 5/5 PASS
- ST1 scatter angle formula : theta=0.920151 ref=0.920151
- ST2 dSigma/dOmega at pi/2 : ds=0.282942 ref=0.282942
- ST3 b_c formula : bc=1.414214 ref=1.414214
- ST4 sigma capture : sigma=6.283185 ref=6.283185
- ST5 trajectory theta vs formula : num=... ref=...

## 数值验证

命令：`~/.venv-tm/bin/python modules/02-scattering/qa/numeric_check.py`
结果：4/4 PASS
