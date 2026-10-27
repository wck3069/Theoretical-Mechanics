# 全站回归报告 — P9-T2

日期：2026-10-27 · 验证人：主代理

## 模块自测（?selftest=1）

| 模块 | SELFTEST | 结果 |
|---|---|---|
| 01-effective-potential | 5/5 PASS | ✓ |
| 02-scattering | 5/5 PASS | ✓ |
| 03-two-body | 5/5 PASS | ✓ |
| 04-variational | 5/5 PASS | ✓ |
| 05-virtual-work | 5/5 PASS | ✓ |
| 06-collisions | 5/5 PASS | ✓ |
| 07-rigid-body | 5/5 PASS | ✓ |
| 08-kinematics | 5/5 PASS | ✓ |

命令：`google-chrome --headless=new --no-sandbox --disable-gpu --window-size=1440,900 --virtual-time-budget=5000 --dump-dom 'file:///home/wck/Theoretical-Mechanics/modules/<slug>/index.html?selftest=1'`

## 静态检查（check_html.py）

| 文件 | 结果 |
|---|---|
| modules/01-effective-potential/index.html | 6/6 ✓ |
| modules/02-scattering/index.html | 6/6 ✓ |
| modules/03-two-body/index.html | 6/6 ✓ |
| modules/04-variational/index.html | 6/6 ✓ |
| modules/05-virtual-work/index.html | 6/6 ✓ |
| modules/06-collisions/index.html | 6/6 ✓ |
| modules/07-rigid-body/index.html | 6/6 ✓ |
| modules/08-kinematics/index.html | 6/6 ✓ |
| catalog.html (root index.html) | 6/6 ✓ |

命令：`~/.venv-tm/bin/python tools/check_html.py <file>`

## 链接检查

Python 片段检查所有 HTML 文件中的 href/src 及 catalog.js 中的 sim/note 字符串，解析相对路径并验证文件存在。

结果：LINKS: ALL OK

## note.tex 验收

| 模块 | 页数 (≥6) | 公式 (≥8) | 参考文献 (≥2) | TODO/TBD/?? |
|---|---|---|---|---|
| 01-effective-potential | 11 ✓ | 39 ✓ | 3 ✓ | 0 ✓ |
| 02-scattering | 6 ✓ | 21 ✓ | 3 ✓ | 0 ✓ |
| 03-two-body | 6 ✓ | 15 ✓ | 3 ✓ | 0 ✓ |
| 04-variational | 6 ✓ | 15 ✓ | 3 ✓ | 0 ✓ |
| 05-virtual-work | 7 ✓ | 9 ✓ | 3 ✓ | 0 ✓ |
| 06-collisions | 6 ✓ | 12 ✓ | 3 ✓ | 0 ✓ |
| 07-rigid-body | 6 ✓ | 10 ✓ | 3 ✓ | 0 ✓ |
| 08-kinematics | 6 ✓ | 11 ✓ | 3 ✓ | 0 ✓ |

## 数值验证

| 模块 | 结果 |
|---|---|
| 01-effective-potential | 18/18 PASS |
| 02-scattering | 4/4 PASS |
| 03-two-body | 6/6 PASS |
| 04-variational | 4/4 PASS |
| 05-virtual-work | 4/4 PASS |
| 06-collisions | 3/3 PASS |
| 07-rigid-body | 6/6 PASS |
| 08-kinematics | 4/4 PASS |

## 三档视口

所有模块在 1440×900、768×1024、360×640 三种视口下无横向溢出（scrollWidth==innerWidth）。
Chrome 无头模式将视口钳制到最小 500px，移动端截图使用 360 但 DOM 度量在 500。

## 结论

全站回归通过。8 个模块全部满足 §7.1/§7.2/§7.3/§7.4 验收标准。
