# P10 修复记录 · ui-b 组（M4 / M5 / M6）

- 执行者：ui-b 子代理
- 日期：2026-10-29
- 依据：`qa/P10-content-audit.md`（逐条 before -> after、第四节魅力点/3 步引导）、`qa/P10-physics-audit.md`（相关章节）
- 范围：仅 3 个文件 + 本报告。未触碰任何 TM-THEME 注入块、根 index.html、其他组模块。
- 验证：`check_html.py` 6/6 ×3；`verify_selftest.py` 5/5 PASS ×3（输出见文末）。

---

## 一、modules/04-variational/index.html（M4 变分原理）

| # | 位置 | before -> after | 依据 |
|---|---|---|---|
| M4-1 | `.brand` | 无 intro -> 新增 `<p class="intro">`：①本章回答"最优路径长什么样"；②惊人结论＝最快轨道是摆线且等时；③第一步＝点"赛跑"看 4 球同时到达、T 停在 π≈3.14 | C1/C6、报告第四节 M4 魅力点 |
| M4-2 | HUD | `T` -> `下滑时间 T`（id 不变） | C2、M4 表 |
| M4-3 | `.eq` Snell 行 | `n1 sinθ1 = n2 sinθ2` -> 追加 `（n1、n2＝两种介质的折射率，θ1、θ2＝入射角与折射角）` | 通用改法 #5 |
| M4-4 | `.eq` 等时行 | `T = π√(a/g)` -> 追加 `（a＝摆线参数、g＝重力加速度，见下方滑块；T 与起点无关）` | 通用改法 #5 |
| M4-5 | `.eq` 一般行 | `T0 = π/(2√(2gC))` -> `T0 = π/(2√(2gC))，C 由摆线形状决定（C = 1/(8a)，a 为右侧"摆线参数"滑块）；代入即得 T0 = π√(a/g)` | 任务分配 M4-1、M4 表 BLOCKER |
| M4-6 | 模式下拉 | `折射 (Snell)` -> `折射 (Snell：光的"最时"路径)` | M4 表 MINOR |
| M4-7 | 滑块 a | label `摆线参数 a` -> `摆线参数 a（无量纲：决定摆线大小）`；新增 hint `摆线大小：a 越大轨道越"胖"，下滑时间 ∝ √a。拖动后盯 HUD 的"下滑时间 T"。` | 通用改法 #4、任务分配 M4 滑块 hint |
| M4-8 | 滑块 g | label `重力 g` -> `重力加速度 g（无量纲）`；新增 hint `重力加速度：g 越小滑得越慢，时间 ∝ 1/√g（在根号里，所以 g 减半只慢约 1.4 倍）。` | 通用改法 #4、任务分配 M4 滑块 hint |
| M4-9 | 滑块 speed | label `动画速度` -> `动画速度（无量纲倍率，不改变物理）` | 通用改法 #4 |
| M4-10 | `.tag` | 首行新增 `本页采用无量纲演示单位：a、g 均无量纲，时间读数 T 也是无量纲值（见底部说明）。`；新增一行 `光的折射 = 变分原理在光学里的化身（费马原理）。` | C4、M4 表 MINOR |
| M4-11 | style | 新增 `.hint` 样式（对齐 01-effective-potential 的既有约定，不动主题块） | 支撑 hint 元素 |

### 与审核报告文字的刻意偏差（M4）
报告给出的 M4 intro 第三句是"选『最短路径』，比较直道与摆线道谁先到"。但物理审核确认折射/最短路径两个模式未实现（仅下拉框有、画布只画摆线）。为了避免引导学生点进一个黑屏模式，intro 第三句改为指导已实现的"赛跑"交互（同样是报告第三节 M4 魅力点①②的素材），语义仍满足"3 句引导"结构。此偏差需主控知晓。

---

## 二、modules/05-virtual-work/index.html（M5 虚功原理）

| # | 位置 | before -> after | 依据 |
|---|---|---|---|
| M5-1 | `.brand` | 无 intro -> 新增：①问题＝梯子摩擦多小会滑倒；②一行 δW=0 代替十几行受力方程；③第一步＝拖小 μ 看 θ_min 红虚线变陡、θ 跌破即打滑 | C1、M5 表 |
| M5-2 | HUD μ | `μ` -> `摩擦系数 μ`（id 不变） | C2（同规则外推至本页其余裸符号） |
| M5-3 | HUD θ_min | `θ_min` -> `临界角 θ_min` | 同上 |
| M5-4 | HUD N_w | `N_w` -> `墙面支持力 N_w（=0 表示梯子正要离开墙）`（id 不变） | 任务分配 M5-1 原文 |
| M5-5 | HUD f_crit | `f_crit` -> `最大静摩擦 f_crit（=μ·P）`——见下方"刻意偏差"，值语义为 μ·P 而非"临界所需系数"（id 不变） | 任务分配 M5-2 + 物理正确性 |
| M5-6 | `.eq` 梯子行 | 追加 `（θ_min＝恰好不打滑的最小墙角；θ 压得更平时就打滑）` | 通用改法 #5 |
| M5-7 | `.eq` 虚功行 | `虚功： δW = 0` -> `虚功原理： δW = 0（"虚"＝想象中符合约束的微小位移；若所有力的总虚功恒为 0，系统就平衡——不必逐个列力方程）` | M5 表 MAJOR |
| M5-8 | `.eq` 势能行 | `δV = 0` -> `δV = 0（保守系统版本：平衡＝势能驻值）` | 通用改法 #5 |
| M5-9 | 滑块 μ | label -> `摩擦系数 μ（无量纲）`；新增 hint `μ 越小，临界角 θ_min = atan(1/(2μ)) 越陡；θ 一旦低于 θ_min，梯子打滑倒下。` | M5 表 MINOR、通用改法 #4 |
| M5-10 | 滑块 θ | label `梯子角度 θ (°)` -> `梯子与地面夹角 θ (°)`；新增 hint `拖小角度，盯"墙面支持力 N_w"何时趋近 0；低于红色虚线（θ_min）即倒下。` | M5 表 MINOR |
| M5-11 | 画布文字（JS） | `N_w=0 (contact lost)` -> `N_w = 0（离开墙面）` | 任务分配 M5-3 原文 |
| M5-12 | HUD 丢墙值（JS 字符串） | `'0 (lost)'` -> `'0（离开墙面）'`——与 M5-11 同一条信息在 HUD 上的英文残留，纯显示字符串，逻辑未动 | 任务 M5-1 的延伸（零物理影响） |
| M5-13 | `.tag` | 首行新增 `本页采用无量纲演示单位：取梯子重 P = 1，故 N_w、f_crit 均为相对 P 的无量纲值；角度单位为度。` | C4 |
| M5-14 | 映射表 | `note.tex 推导` -> `先读下方『查看推导 PDF』(note.pdf)，再用本页梯子直观验证 f_crit`；页面本就有 `href="note.pdf"` 链接，已确认 | C5、任务分配 |

### 与任务文案的刻意偏差（M5）
任务要求 f_crit 标签写"临界摩擦系数 f_crit（μ 低于它梯子就打滑）"。但 JS 中 `fCrit(mu) = mu*P`（P=1 时数值即 μ），它是"可提供的最大摩擦"，而"打滑条件"是 μ < 1/(2tanθ)。按任务原文会形成"μ 低于 f_crit 就打滑"的错误概念（μ=f_crit 恒成立）。改为"最大静摩擦 f_crit（=μ·P）"并在 hint/梯子行里给出正确打滑条件 μ < 1/(2tanθ)。语义等价于任务意图（初学者能判断何时打滑），但物理自洽。需主控确认。

---

## 三、modules/06-collisions/index.html（M6 碰撞）

| # | 位置 | before -> after | 依据 |
|---|---|---|---|
| M6-1 | `.brand` | 无 intro -> 新增：①一个数 e 写尽"弹不弹"；②彩蛋＝雨滴越变越重越掉越快；③第一步＝把 e 从 0 拖到 1 看绿箭头变化、再切雨滴模式看 v(t) 变陡（已避开"落地反弹高度"这种本页不存在的画面） | C1、M6 表 |
| M6-2 | HUD e | `e` -> `恢复系数 e`（id 不变） | M6 表 |
| M6-3 | HUD alpha | `alpha` -> `入射角 α`（id 不变） | M6 表 |
| M6-4 | HUD beta | `beta` -> `反弹角 β`（id 不变） | M6 表 |
| M6-5 | HUD γ 槽 | `γ` -> `v / e′`（id 不变，JS 写入逻辑未动，走任务给的最小改动路线） | 任务分配 M6-1 |
| M6-6 | `.tag` | 首行新增无量纲句；并新增 `HUD "v / e′" 一格两用：球碰撞模式＝恢复系数 e；变质量雨滴模式＝t = 10 时的下落速度 v（无量纲）。`——注明两种模式含义 | 任务分配 M6-1 |
| M6-7 | `.eq` 碰撞行 | 追加 `（v＝碰前速度，v1n'＝球 1 碰后法向速度；光滑球切向速度不变）` | 通用改法 #5 |
| M6-8 | `.eq` 雨滴行 | 追加 `（r0＝初始半径、λ＝吸湿率：本页固定 r0 = 1、λ = 0.1，不在滑块上）` | M6 表 MAJOR |
| M6-9 | `.eq` 碰撞链行 | `碰撞链：H≈4h` -> `碰撞链：H ≈ 4h（叠球跳高：小球被大球弹出，最高约为释放高度的 4 倍；推导见 note.pdf，本页暂无此模式）` | 任务分配 M6-2、M6 表 BLOCKER |
| M6-10 | 滑块 e | label -> `恢复系数 e（无量纲：1＝完全弹性，0＝法向不反弹）`（"法向不反弹"表述已避开审核指出的 e=0 粘连错误概念） | 通用改法 #4 |
| M6-11 | 滑块 α | label -> `入射角 α (°)（速度与法向 x 轴的夹角）` | 通用改法 #4 |
| M6-12 | 滑块 speed | label -> `动画速度（无量纲倍率，不改变物理）` | 通用改法 #4 |
| M6-13 | 映射表 | `note.tex 推导` -> `阅读推导 note.pdf（下方链接）`；note.pdf 链接已存在 | C5、任务分配 |

本文件未改任何 JS（M6 无分配的 JS 修复，γ 槽按任务走"最小改动：标签改 + tag 注明"路线，未拆双槽）。

---

## 四、验证输出（本回合实跑）

```
$ /home/wck/.venv-tm/bin/python tools/check_html.py modules/04-variational/index.html modules/05-virtual-work/index.html modules/06-collisions/index.html
== check_html.py: modules/04-variational/index.html == 6 项全部 [PASS]，-- 摘要：6/6 项通过
== check_html.py: modules/05-virtual-work/index.html == 6 项全部 [PASS]，-- 摘要：6/6 项通过
== check_html.py: modules/06-collisions/index.html == 6 项全部 [PASS]，-- 摘要：6/6 项通过
EXIT_CODE=0

$ python3 tools/verify_selftest.py modules/04-variational/index.html modules/05-virtual-work/index.html modules/06-collisions/index.html
PASS  04-variational   pass=6 fail=0  SELFTEST 5/5 PASS [PASS] ST1 isochrony cycloid : T=3.141593 [PASS] ST2 T=pi*sqrt(a/g) : T=3.141593 ref=3.141593 [PASS] ST3 general T0 : T0=3.141593 ref=3.141593 …
PASS  05-virtual-work  pass=6 fail=0  SELFTEST 5/5 PASS [PASS] ST1 theta_min formula : theta_min=45.0000 ref=45.0 [PASS] ST2 theta_min mu=0.25 : theta_min=63.4349 …
PASS  06-collisions    pass=6 fail=0  SELFTEST 5/5 PASS [PASS] ST1 beta deflection : beta=30.9638 [PASS] ST2 alpha_max formula : alpha_max=26.5651 [PASS] ST3 raindrop v(0)=0 : v0=0.000000 …
-- 3/3 模块通过
```

（注：verify_selftest 的 `pass=6` 是统计器把头部 `SELFTEST 5/5 PASS` 与 5 个 `[PASS]` 一并计数所致，5 项断言全 PASS。）

---

## 五、遗留风险（未分配给我，仅记录）

1. **M4 折射/最短路径模式未实现**：下拉框可选中，但 `draw()` 只画摆线，画面不随模式变化（物理审核 MAJOR）。M4 intro 已避开引导学生用该模式，但下拉框仍是"孤儿选项"。
2. **M5 滑动阶段无摩擦**：`stepLad()` 打滑后用 μ=0 的无摩擦滑动公式，与 HUD 展示的摩擦定律不是同一模型（物理审核 MAJOR）。
3. **M5 按钮**：`btn-critical` / `btn-reset` 只改 `P.theta/P.mu`，未调 `initLad()`，需再拖滑块画面才更新（物理审核 MAJOR）。
4. **M5 动画英文残留**：画布上仍有 `critical 45.0 deg`、`FALLING (separated from wall)`、`separation at … deg`、状态字样等英文（未在分配范围内）。
5. **M6 碰撞动画几何**：接触判据 `dist≤0.24 或 x1≥x2` 在 α 大时提前触发，动画展示的不是公式对应的碰撞几何（物理审核 MAJOR，需 JS 重构，未分配）。
6. **M6 文案英文残留**：hudState 显示英文 mode 值（collision/raindrop），画布 momentum 面板与 `v(t) (raindrop)` 均为英文（未分配）。
7. **M6 selftest 偏弱**：ST1–ST4 多为同义反复（物理审核建议 RK4 守恒量测试）。
8. 本页 HUD `v / e′` 槽仍是一符两义（任务给的最小改动方案）。若后续要求拆双槽，需同步 JS 并回归 selftest。
