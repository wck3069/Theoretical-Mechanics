# 受迫振动与共振

> 模块代号：M27 · 20-forced-resonance · 理论力学 · 交互讲义
>
> 线性受迫振子 $\ddot q+2\gamma\dot q+\omega_0^2q=F_0\cos\omega t$（演示取 m=1）：
> RK4 实时积分看瞬态按 $e^{-\gamma t}$ 退场、稳态 $A\cos(\omega t-\delta)$ 接管；
> 幅频曲线 $A(\omega)$ 与功率曲线 $\overline{P}(\omega)$ 同屏对照，区分
> $\omega_R=\sqrt{\omega_0^2-2\gamma^2}$、$\overline{P}$ 峰（恒在 $\omega_0$）与
> 半功率带宽 $2\gamma$；两模叠加出拍，包络 $2\cos(\Delta\omega\,t/2)$。

## 书稿映射

| 来源 | 主题 | 核心知识点 | 手稿章节 |
|---|---|---|---|
| ch04 | 阻尼自由衰减 | $\gamma=c/(2m)$、$q=e^{-\gamma t}y$ 化简、欠/临界/过阻尼三分区、包络 $e^{-\gamma t}$ | manuscript/chapters/ch04.tex §阻尼与功率（110 行起） |
| ch04 | 受迫稳态与相位 | 复数解 $(\omega_0^2-\omega^2+2i\gamma\omega)X=F_0/m$、$A(\omega)$、$\tan\delta=2\gamma\omega/(\omega_0^2-\omega^2)$、$\delta\in(0,\pi)$ | ch04.tex §稳态、相位和平均吸收功率（163 行起） |
| ch04 | 共振峰与带宽 | $\omega_R=\sqrt{\omega_0^2-2\gamma^2}$（$\gamma\ge\omega_0/\sqrt2$ 无峰）、$\overline{P}_{\max}=F_0^2/(4m\gamma)$、$\omega_\pm=\sqrt{\omega_0^2+\gamma^2}\pm\gamma$、$\Delta\omega=2\gamma$ 精确、$Q=\omega_0/2\gamma$、$\Delta E/E\simeq 2\pi/Q$ | ch04.tex §稳态、相位和平均吸收功率 + 数值算例（228 行） |
| ch04 | 双振子与拍 | 和差化积 $2\cos(\Delta\omega t/2)\cos(\bar\omega t)$、$T_b=2\pi/|\Delta\omega|$、有符号包络的正负两支 | ch04.tex §双振子、耦合摆与拍（398 行起） |

## 参数说明

| 参数 | 物理含义 | 默认值 | 范围 | 单位 |
|---|---|---|---|---|
| ω | 驱动角频率（场景1/2 共用；场景2 为曲线上的标记游标） | 0.80 | 0.05–3 | rad/s（无量纲演示单位，ω₀≡1 制） |
| ω₀ | 固有角频率（m=1, k=ω₀²） | 1.00 | 0.2–3 | rad/s |
| γ | 阻尼系数（γ=c/2m；场景1/2 共用） | 0.080 | 0.01–1 | s⁻¹ |
| F₀ | 驱动力幅值（F₀/m≡F₀） | 1.00 | 0.05–2 | 无量纲 |
| ω₁, ω₂ | 拍的两分量角频率（场景3） | 1.00, 1.15 | 0.2–3 | rad/s |
| speed | 动画时间倍率（RK4 定步长 h=0.002 上的累加器） | 1.0 | 0.1–3 | × |

场景：`?scene=forced|resonance|beats`；自测：`?selftest=1`。
URL 预设示例：`index.html?scene=resonance&gamma=0.02&omega=1`、
`index.html?scene=beats&omega1=1&omega2=1.12`、
`index.html?preset=…`（页面内预设按钮对应共振点/高Q/低频/高频/拍）。
换手稿 ch04 实数算例（m=1 kg, k=100 N/m, c=4 N·s/m → ω₀=10, γ=2,
ω_R=√92≈9.59, 半功率点 8.20/12.20）时，把全部频率除以 10 即与本页无量纲画面一致。

## 运行方式

- **交互页面**：浏览器直接打开 `index.html`——单文件、离线可用（星空背景依赖
  仓库内 `../../assets/cosmos/`，需保持仓库目录结构）
- **HTML 检查**：`/home/wck/.venv-tm/bin/python tools/check_html.py modules/20-forced-resonance/index.html`
- **自测**：`index.html?selftest=1`，或 `/home/wck/.venv-tm/bin/python tools/verify_selftest.py modules/20-forced-resonance/index.html`
- **渲染冒烟**：`google-chrome --headless --dump-dom …/index.html | grep -c canvas`

## 验收记录

| 日期 | 项目 | 命令 | 结果 |
|---|---|---|---|
| 2026-11-23 | HTML 检查 | `/home/wck/.venv-tm/bin/python tools/check_html.py modules/20-forced-resonance/index.html` | 6/6 项通过，0 项失败（EXIT_CODE=0，1 个内联 script 块 esprima 4.0.1 解析通过） |
| 2026-11-23 | selftest | `/home/wck/.venv-tm/bin/python tools/verify_selftest.py modules/20-forced-resonance/index.html` | `PASS 20-forced-resonance pass=13 fail=0`（面板末行 `SELFTEST 12/12 PASS`） |
| 2026-11-23 | 渲染冒烟 | `google-chrome --headless=new --dump-dom …/index.html \| grep -c canvas` | `3`（canvas 存在；HUD 六项由 JS 实时填充，无 JS 异常） |
| 2026-11-23 | 三场景截图 | `google-chrome --headless=new --window-size=1280,820 --screenshot` | /tmp/opencode/shot-forced.png、shot-resonance.png、shot-beats.png |
| 2026-11-23 | 运行时错误探测 | headless `--enable-logging=stderr`（三场景各 9s 虚拟时间） | 三场景均 0 errors；HUD 与解析值一致（ω_R=0.9975、Q=10、T_b=52.36=2π/0.12） |

selftest 断言明细（12 条，均 PASS；ω₀=1、γ=0.1 处积分 h=0.004，热身 t>10/γ 后对 8 个周期做均方与 cos/sin 投影反演稳态）：

1. ST1 稳态幅值 ω=0.5：1.321636 vs 解析 1.321637（relerr 1.1e-6）
2. ST2 相位滞后 ω=0.5：7.59467° vs 7.59464°（abserr 2.9e-5°）
3. ST1 稳态幅值 ω=1：4.999964 vs 5.000000（relerr 7.2e-6）
4. ST2 相位滞后 ω=1：89.99973° vs 90°（abserr 2.7e-4°）
5. ST1 稳态幅值 ω=2：0.330409 vs 0.330409（relerr 8.2e-7）
6. ST2 相位滞后 ω=2：172.40527° vs 172.40536°（abserr 8.6e-5°）
7. ST3 功率峰频率：1.000000 vs ω₀=1（relerr 7.8e-14，网格 0.0002 扫描）
8. ST3 幅值峰频率：0.990000 vs ω_R=√0.98=0.989950（relerr 5.1e-5）
9. ST4 半功率带宽（γ=0.05）：0.100000 vs 2γ=0.1（relerr 8.3e-16，二分求 ω±）
10. ST5 自由衰减率（γ=0.15, F₀=0）：对数极值拟合斜率 −0.1499994 vs −0.15（relerr 4.0e-6）
11. ST6 拍周期（ω₁=1, ω₂=1.1）：均方滑窗过零法测得 62.8319 vs 2π/0.1=62.8319（relerr 1.9e-9）
12. ST6 包络幅值：max|x|=2.000000 vs 2F₀=2（relerr 1.2e-8）

## 已知限制

- 线性黏性模型（阻尼 $-2\gamma\dot q$、驱动 $F_0\cos\omega t$），不含干摩擦、
  Duffing 非线性与参数共振（ch04 后文主参数共振不在本模块范围）。
- 演示采用 m=1 的无量纲制；页面内 ω、ω₀、γ 同一单位制，换算实数算例见上文参数说明。
- RK4 定步长 h=0.002、无自适应：γ→0.01 且 ω≈ω₀ 时稳态建立需 t≈10/γ 量级时间，
  画面以"偏离稳态"HUD 明示瞬态残迹，不代表数值误差。
- 场景3 的拍用两个独立无阻尼 RK4 积分器叠加（能量守恒由 selftest ST6 间接验证），
  不是耦合摆的简正模分解：ω₁、ω₂ 可任意设定，不保证来自同一对耦合摆的 $\omega_\mp$。
- 相位显示用 atan2 全象限（δ∈(0,π)）；若只按 arctan 读数会在 ω>ω₀ 分支错 180°
  ——这正是手稿习题"只给相位正切不能定高频相位"的演示点，页面 HUD 直接给连续 δ。
