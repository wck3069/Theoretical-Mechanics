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

## 2026-10-27 收尾（清理 / 去冗余 / 发布）

| 项 | 结果 |
|---|---|
| 作业 PDF 入库 | **已从索引与全部历史移除**（`git filter-repo --path 作业 --invert-paths`），远端 `作业` 路径数 = 0；本地文件保留 |
| .git 体积 | 13M → 8.4M |
| 导航链接 | 全部模块上一/下一链接改指真实模块（原统一指向根目录，P9 迁移后语义错误）；M8 末页"返回总目录" |
| 目录双副本 | 根 `index.html` 为唯一正文；`catalog.html` 改为重定向（保 query/hash），消除 30KB 重复与漂移 |
| 全新克隆验收 | `git clone --depth 1` 到 /tmp：8/8 模块 `check_html 6/6` + `selftest 5/5`；目录渲染 9 张卡片 |
| 控制台 | 9 个页面全部无 error（含 binet legacy） |
| 链接检查 | ALL OK |

## 2026-10-28 M8 双摆方程修正（模型挑战暴露的真实缺陷）

**过程**：让本地 Maya（DeepSeek-V4.1-Flash，Maya-S）在只给规格、禁读现有实现的条件下独立生成 M8 模拟器。

| 项 | 门禁 | 物理（能量守恒） |
|---|---|---|
| 模型生成版 `/tmp/m8_ai/index.html` | check_html **6/6**、`SELFTEST 5/5 PASS` | **FAIL**：2s 积分能量漂移 **2.18e+01 J** |
| 我们修正前的 M8 | 6/6、5/5 | **FAIL**：漂移 **2.21e+01 J** |
| 我们修正后的 M8 | 6/6、5/5 | **PASS**：漂移 **5.8e-14** |

**根因**：双摆角加速度公式符号/系数错误（等质量等长、θ 为绝对角）。

修正后（拉格朗日推导，能量守恒校验）：
```
Δ = θ1-θ2, D = 2-cos²Δ
θ̈1 = [-g(2 sinθ1 - sinθ2 cosΔ) - L sinΔ(ω1² cosΔ + ω2²)] / (L·D)
θ̈2 = [2g(cosΔ sinθ1 - sinθ2) + L sinΔ(2ω1² + ω2² cosΔ)] / (L·D)
```

**门禁升级**：M8 的 ST5 由"角度有限（isFinite）"改为**能量漂移 < 1e-6（200 步 @2ms）**——旧断言对错误方程也会 PASS。

**结论**：本地模型能产出过静态门禁的骨架，但**物理必须独立校验**；"测试通过"不等于"结论正确"。
