# 22 · 勒让德变换与罗斯约化（Legendre Transform & Routh Reduction）

里程碑 **M29** · 手稿 **ch06 哈密顿力学** · 单文件离线交互模块（index.html，约 51.5 KB）· 单位制 m = k = l = g = 1。

三个联动场景：
1. **勒让德变换的切线构造**：L(q̇;q) 与 H(p;q) 双抛物线，切线斜率互换（p ↔ q̇），纵轴公共截距 −H；
2. **正则方程 vs 拉格朗日方程**：同一初态 (q₀, q̇₀→p₀=m q̇₀) 两套方程独立 RK4 积分，叠印验证重合，HUD 实时给出两解偏差与能量漂移；
3. **罗斯约化**：平面中心力场 θ 循环 → p_θ = Lz 守恒，全 2D 极坐标轨道与约化径向 r(t) 双轨对照，V_eff(r) = V(r) + Lz²/(2mr²) 面板标出转折点、E 线与极小。

## 书稿映射（manuscript/chapters/ch06.tex）

| 手稿小节 | 对应可视化 |
|---|---|
| §勒让德变换与正则方程（"勒让德变换与正则方程"） | 场景1 切线构造（斜率 = p、截距 = −H；恒等 dH = q̇ dp − L_q dq）；场景2 q̇ = ∂H/∂p、ṗ = −∂H/∂q 与 EL 方程独立积分对照，单摆含分界线 E = +mgl |
| §从模型辨认正则动量（中心势球坐标） | 场景3 p_θ = mr²θ̇ 守恒（HUD 实时 Lz 漂移），径向方程逐项核验（ST6 力律残差） |
| §罗斯约化的符号与循环条件 | 场景3 拉格朗日型 Routhian R = L − Lzθ̇ = ½mṙ² − V_eff；eqBox 明确标注"另一些文献取相反号 R_H = −R，勿混用"以及"直接代回 L 会把离心项错号" |

## 物理模型

- **勒让德变换**：p = ∂L/∂q̇；H = p q̇ − L（速度经 p 消去）。谐振子 L = ½q̇² − ½q² ⟹ H = ½p² + ½q²；单摆 L = ½θ̇² + cosθ ⟹ H = ½p² − cosθ（默认制）。凸性 ∂²L/∂q̇² = m > 0 保证对合（L→H→L 复原）。
- **几何核心**：L 在 q̇ 处切线斜率 = p、截距 = −H；H 在 p 处切线斜率 = q̇、截距同为 −H —— 互为切线族包络。
- **正则方程**：q̇ = ∂H/∂p，ṗ = −∂H/∂q；与 EL 方程 d/dt(∂L/∂q̇) = ∂L/∂q 经 p = ∂L/∂q̇ 一一对应。
- **罗斯约化**：θ 循环 ⟹ Lz = mr²θ̇ 守恒为参数；R(x, ẋ, μ) = L − Σμαẏα；约化方程 m r̈ = Lz²/(mr³) − V′(r)；重构 θ̇ = −∂R/∂Lz = Lz/(mr²)。
- **势**：开普勒 V = −1/r，谐振 V = ½r²；转折点解析求根（Kepler：E r² + r − Lz²/2 = 0；Harm：r± = √(2(E ± √(E² − Lz²)))）。

## 场景与参数

- `?scene=legendre|canonical|routh` 选场景；`sys=osc|pend`（场景1/2 系统，URL 中合并为 `sys=a|b`）；`pot=kepler|harm`（场景3）。
- 场景1 滑杆：q（定坐标，抛物线平移）、q̇（切点）。预设 **谐振子勒让德**。
- 场景2 滑杆：q₀、q̇₀、轨迹长度（周期数）。预设 **单摆正则**（q₀=2.6, q̇₀=0.45，E<1 摆动区）。
- 场景3 滑杆：Lz、r₀（初始 θ̇₀ = Lz/r₀²）、ṙ₀。预设 **开普勒约化**（Lz=0.8）、**谐振约化**、**近圆轨道**（Kepler Lz=1，r₀=1.1，圆轨道 r=Lz²=1 附近）。
- 通用：时间流速滑杆、暂停/重置；全部参数持久化于 URL（history.replaceState）。

## 运行方式

浏览器直接打开 `index.html`（离线，无网络请求），或：

```bash
python3 -m http.server 8000   # 仓库根目录
# 打开 http://localhost:8000/modules/22-legendre-routh/
```

自检模式：`index.html?selftest=1`（不起动画循环，页面底部输出断言面板，`window.__selftest` 同步可见）。

## 验收命令与实际结果

```
$ ~/.venv-tm/bin/python tools/check_html.py modules/22-legendre-routh/index.html
== check_html.py: modules/22-legendre-routh/index.html ==
[PASS] 1. 内联 JS 语法（1 个 <script> 块，esprima (4, 0, 1)）
[PASS] 2a. 无 http 或 https 外链（全文未出现）
[PASS] 2b. 无协议相对地址（属性、CSS、字符串均未出现）
[PASS] 2c. 资源引用均为本地相对路径（无外部资源标签）
[PASS] 2d. 无网络请求或外部模块加载（未出现）
[PASS] 2e. 无 CDN 域名引用（未出现）
-- 摘要：6/6 项通过，0 项失败
EXIT_CODE=0
```

```
$ ~/.venv-tm/bin/python tools/verify_selftest.py modules/22-legendre-routh/index.html
PASS  22-legendre-routh                           pass=15 fail=0  [PASS] ST1a 谐振子 ∂L/∂q̇ 中心差分 vs 解析 (q̇=-1.7) : expected=-1.700000e+0 actual=-1.700000e+0 relerr=6.33e-13 tol=0.000001 [PASS] ST1a 谐振子 ∂L/∂q̇ 中心差分 vs 解析 (q̇=0.5)
-- 1/1 模块通过
```

完整自检面板（headless chrome dump-dom 抓取，14 条断言全过）：

```
[PASS] ST1a 谐振子 ∂L/∂q̇ 中心差分 vs 解析 (q̇=-1.7) : expected=-1.700000e+0 actual=-1.700000e+0 relerr=6.33e-13 tol=0.000001
[PASS] ST1a 谐振子 ∂L/∂q̇ 中心差分 vs 解析 (q̇=0.5) : expected=5.000000e-1 actual=5.000000e-1 relerr=1.10e-13 tol=0.000001
[PASS] ST1a 谐振子 ∂L/∂q̇ 中心差分 vs 解析 (q̇=2.3) : expected=2.300000e+0 actual=2.300000e+0 relerr=2.69e-12 tol=0.000001
[PASS] ST1b 勒让德恒等式 H = p q̇ − L : expected=1.225000e+0 actual=1.225000e+0 relerr=0.00e+0 tol=1e-9
[PASS] ST2 对合 (L 的变换的变换) q̇=-2.3 : expected=2.040000e+0 actual=2.040000e+0 relerr=2.18e-16 tol=1e-8
[PASS] ST2 对合 (L 的变换的变换) q̇=0 : expected=-6.050000e-1 actual=-6.050000e-1 relerr=0.00e+0 tol=1e-8
[PASS] ST2 对合 (L 的变换的变换) q̇=1.7 : expected=8.400000e-1 actual=8.400000e-1 relerr=1.19e-15 tol=1e-8
[PASS] ST3 10 周期 q_H vs q_EL（正则=EL 等价性） : expected=0.000000 actual=0.000000 abserr=0.00e+0 tol=0.000001
[PASS] ST3 p_H vs m q̇_EL 映射残差 : expected=0.000000 actual=0.000000 abserr=0.00e+0 tol=0.000001
[PASS] ST4 单摆 H(p,θ) 相对漂移（RK4 5000 步） : expected=0.000000 actual=0.000000 relerr=3.33e-12 tol=1e-8
[PASS] ST5 约化 r(t) vs 全 2D（5 个径向周期）最大相对偏差 : expected=0.000000 actual=0.000000 relerr=6.83e-11 tol=0.000001
[PASS] ST5b E_full vs E_reduced（末态能量一致） : expected=-7.290806e-1 actual=-7.290806e-1 relerr=1.42e-11 tol=1e-9
[PASS] ST6 力律残差 max|r̈_2D − (Lz²/r³ − V′)|（m=1） : expected=0.000000 actual=0.000000 abserr=4.94e-11 tol=1e-9
[PASS] ST6b Lz = mr²θ̇ 沿全 2D 轨迹守恒 : expected=0.000000 actual=0.000000 relerr=5.07e-12 tol=1e-9
SELFTEST 14/14 PASS
```

说明：ST3 偏差恰为 0 是诚实结果——谐振子情形 ∂H/∂q|_{p→mq̇} 与 EL 右端给出逐字相同的 ODE，两列 RK4 因此产生机器相同轨道，验证的是"变换后方程一致"这一构造性事实（单摆情形动画中同样重合但 ST 用解析一致的系统给硬数字）。ST5 的径向周期由 V_eff 转折点间求积（中点法）估计，h = T_r/1500。

三场景常规模式启动检查（dump-dom，HUD 实值）：legendre `L(q,q̇)=0.1838`、canonical `E(初值)=0.7200`、routh `Lz(设定)=0.800`，selftestPanel 在非自检模式下 hidden。

## 已知限制

- 非相对论点粒子、平面运动、无阻力无辐射；单摆精确分界线 E = +mgl 与 r→0 库仑奇点是理想模型极限（r 下限 1e-6 防溢出）。
- 场景2 单摆 q 不换模：转动区解绕行会越出 ±π 视窗（eqBox 已注明）。
- 场景1 的动画在单摆模式下数值积分推进，谐振子模式用解析稳态 q = A cos(t−φ)（切线构造与数值无关，HUD 恒等式残差仍为机器精度）。
- 径向周期 T_r 由数值求积估计（相对误差 ~1.6%，仅用于 HUD/视窗调度；断言 ST5 直接用 h = T_r/1500 的一致性而非绝对 T_r）。
- file:// 协议下部分浏览器禁止 history.replaceState，URL 持久化会静默降级（try/catch）。

## 数值方法

四阶 Runge-Kutta（RK4）：正则/EL 双列 h = T/1600（单摆周期用 AGM 估计）；全 2D 极坐标（4 维态 [r,θ,ṙ,θ̇]）与约化 1D 双轨 h = 0.0012；勒让德场景恒等式与对合用中心差分 h = 1e-4、嵌套三分搜索（凸对偶，140/80 次迭代）。
