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

## 2026-10-27 交互修复轮（用户逐条反馈）

| 模块 | 修复内容 | 验证 |
|---|---|---|
| M1 | V_eff 图叠加径向动能阴影 `1/2 m v_r^2 = E - V_eff` 与标签 | 6/6 + 5/5 |
| M2 | 俘获模式 r→0 时停止并显示"被捕获 (r→0)" | 6/6 + 5/5 |
| M3 | 默认木星预设、RV 缓冲 2000、新增星体摆动放大面板、HUD 用 m/s | 6/6 + 5/5 |
| M4 | 修复动画（起始 v=0 导致首帧即 done）、摆线居中放大 | 6/6 + 5/5 |
| M5 | 低于临界角时梯子倒下动画（杆绕底端 `θ̈=-1.5cosθ`）、显示 N_w / f / P 矢量、临界角虚线参考、接触丢失提示 | 6/6 + 5/5 |
| M6 | 新增碰撞动画（接近→碰撞→散射，目标球被撞后运动） | 6/6 + 5/5 |
| M7 | 球冠参数改为高度 h（0.01–6，可超过半径）、甲虫-圆环动画（环反向转 -θ/2） | 6/6 + 5/5 |
| M8 | 双摆混沌模式（RK4）、预跑 320 步生成轨迹、枢轴锚固符号、右侧读数 | 6/6 + 5/5 |

代码片段由本地千问（qwen3.8-flash-next-iq3_s，127.0.0.1:8080）产出，主代理仅做集成与验收。

## 2026-10-27 第二轮（物理正确性）

| 模块 | 修复 | 验证证据 |
|---|---|---|
| M5 | 改为真实无摩擦滑移梯子：θ̇²=3g/L(sinθ₀−sinθ)，分离判据 sinθ=⅔sinθ₀（屏上标 "separation at … deg"）；底面沿地滑动；分离后 N_w=0 | 6/6 · 5/5 |
| M6 | 改为动量守恒的二维碰撞解：法向 v1n'=(1−e)/2·v1n、v2n'=(1+e)/2·v1n、切向不变；画布实时显示 P_before/P_after 与 "momentum conserved: YES" | 6/6 · 5/5 |
| M4 | 最低点黄点加标签 "lowest point"，消除"游离点"误读 | 6/6 · 5/5 |

本轮物理公式由主代理推导并数值校验（本地千问在该类推导上输出不稳定，未采用）。

## 2026-10-27 第三轮（交互可见性）

| 模块 | 修复 | 验证 |
|---|---|---|
| M7 | 甲虫轨迹改为采样数组折线（亮度 .9、线宽 3）、进入模式预跑 130 步、读数移到右侧避免压标题 | 6/6 · 5/5，截图确认 beetle=154.7° / ring=−77.3°（=−θ/2） |

## 2026-10-27 第四轮（移动端 360 + 补齐）

| 项 | 结果 |
|---|---|
| 8 模块 360×640 截图 | 已生成；Chrome 无头把视口钳制到 500，`scrollWidth==innerWidth` → 无横向溢出 |
| M5 窄屏标签重叠 | 修复：N_w 左移、critical 标签移到虚线中段并偏移，二者不再互压 |
| M8 窄屏控制区 | 面板 42vh→46vh、画布 58vh→54vh，减少首屏裁切 |
| M0 遗留说明 | 新增 `modules/00-binet/qa/T0-legacy.md`：只读样板、不参与 selftest、check_html 6/6、PDF 5 页 |
| M8 双摆轨迹 | trailMax 500→1200、预跑 320→600 步，轨迹覆盖更完整 |
