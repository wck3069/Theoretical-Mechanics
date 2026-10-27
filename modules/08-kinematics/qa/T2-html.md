# M8-T2 验证证据 — modules/08-kinematics/index.html

日期：2026-10-27

## 静态检查

命令：`~/.venv-tm/bin/python tools/check_html.py modules/08-kinematics/index.html`
结果：6/6 项通过，0 项失败，EXIT_CODE=0

## 运行时自测

命令：`google-chrome --headless=new --no-sandbox --disable-gpu --window-size=1440,900 --virtual-time-budget=5000 --dump-dom 'file:///home/wck/Theoretical-Mechanics/modules/08-kinematics/index.html?selftest=1'`

结果：SELFTEST 5/5 PASS
- ST1 detach angle : detach=48.1897 ref=48.1897
- ST2 cos detach=2/3 : cos=0.666667
- ST3 pendulum correction : corr=0.001904 ref=0.001904
- ST4 pendulum period : T=6.295148 ref=6.295148
- ST5 cyclotron radius : rc=1.000000

## 数值验证

命令：`~/.venv-tm/bin/python modules/08-kinematics/qa/numeric_check.py`
结果：4/4 PASS
