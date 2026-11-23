# 重陀螺的进动与章动

> 模块代号：M28 · 21-heavy-top · 理论力学 · 交互讲义
>
> 重对称陀螺（支点在下方、质心高 l）：由循环动量 p_φ、p_ψ 约化出倾角一维有效势
> V_eff(θ)，RK4 积分演示稳恒进动的慢支与快支、玫瑰线章动、竖直睡眠陀螺的稳定
> 阈值 ω₃c=√(4I₁Mgl)/I₃，以及力矩自由极限下进动速率与角动量几何的一致性。

## 书稿映射

| 来源 | 主题 | 核心知识点 | 手稿章节 |
|---|---|---|---|
| ch05 | 约化方程与稳恒进动 | Routh 约化、有效势 V_eff、转折点、进动二次方程 | manuscript/chapters/ch05.tex §约化方程与稳恒进动（约 1497 行起） |
| ch05 | 慢支、快支及章动频率 | Ω_slow≈Mgl/(I₃ω₃)、Ω_fast≈I₃ω₃/(I₁cosθ₀)、ω_n=√(V″(θ*)/I₁) | ch05.tex §慢支、快支及章动频率（约 1532 行起） |
| ch05 | 竖直睡眠陀螺须单独线性化 | θ=0 欧拉角奇异、模式指数 σ±、判据 ω₃²>4I₁Mgl/I₃² | ch05.tex §竖直睡眠陀螺（约 1577 行起） |

## 参数说明

| 参数 | 物理含义 | 默认值 | 范围 | 单位 |
|---|---|---|---|---|
| ω₃ | 自转角速度（轴向 L₃=I₃ω₃） | 12.0 | 0–20 | rad/s（无量纲演示单位） |
| θ₀ | 初始倾角（睡眠场景为初始偏离角） | 45 | 5–80 | ° |
| I₃/I₁ | 惯量比（I₁≡1） | 0.60 | 0.2–2 | — |
| Mgl | 重力矩 | 0.50 | 0.1–2 | 无量纲 |
| δθ | 释放偏移（稳恒预设上叠小章动） | 0 | −10–10 | ° |
| 演示速度 | 动画时间倍率（RK4 子步 h=0.002） | 1.0 | 0.1–3 | × |

场景：`?scene=top|pot|sleep`；释放模式：`?steady=none|slow|fast`；
预设：`?preset=slow|fast|strong|sleep`；自测：`?selftest=1`。
示例：`index.html?preset=sleep&w3=2.1`（非法值自动回退默认）。

## 运行方式

- **交互页面**：浏览器直接打开 `index.html`——单文件、离线可用（星空背景依赖
  仓库内 `../../assets/cosmos/`，需保持仓库目录结构）
- **HTML 检查**：`/home/wck/.venv-tm/bin/python tools/check_html.py modules/21-heavy-top/index.html`
- **自测**：`index.html?selftest=1`，或 `/home/wck/.venv-tm/bin/python tools/verify_selftest.py modules/21-heavy-top/index.html`

## 验收记录

| 日期 | 项目 | 命令 | 结果 |
|---|---|---|---|
| 2026-11-23 | HTML 检查 | `tools/check_html.py modules/21-heavy-top/index.html` | 6/6 项通过，0 项失败（EXIT_CODE=0） |
| 2026-11-23 | selftest | `tools/verify_selftest.py modules/21-heavy-top/index.html` | PASS pass=8 fail=0，面板末行 `SELFTEST 7/7 PASS` |
| 2026-11-23 | 渲染冒烟 | headless chrome `--dump-dom`（非自测模式） | canvas 存在，HUD t 由 0 递增至 0.07s，无 JS 异常 |
| 2026-11-23 | 三档视口截图 | `google-chrome --headless=new --window-size=… --screenshot` | /tmp/tm21/top_1280,800.png、top_820,1180.png、top_390,844.png、pot.png、sleep.png |

selftest 断言明细（均 PASS）：

1. ST1 稳恒进动根回代残差 6e-16/0；稳定形式小根一致（1e-16）
2. ST1b 慢支极限 Ω≈Mgl/(I₃ω₃)：slow=0.041769 vs 0.041667（rel 0.25%）
3. ST2 V_eff 极小点 θ*=56.98°（p_φ=1.2, p_ψ=2, Mgl=0.3），回代 0
4. ST3 睡眠判据 ω₃c=2.357：0.9ω₃c 倾角 0.5°→51.68°（增长）；1.1ω₃c 保持 0.500°（有界）
5. ST4 守恒：E、L_z 相对漂移 ≤1.59e-16（10⁴ 步 RK4）
6. ST5 章动周期实测 1.1900 vs 闭式 2π/ω_n=1.1900
7. ST6 力矩自由极限 Ω̄=5.5426 vs L_z/I₁=5.5426（rel 2.9e-8）

## 已知限制

- 仅对称陀螺 I₁=I₂；不含摩擦/阻尼，章动不衰减。
- 欧拉角在 sinθ→0 奇异：p_φ=p_ψ 情形按恒等式
  V=h²(1−cosθ)/2I₁(1+cosθ)、φ̇=h/I₁(1+cosθ) 精确改写；其余按 |sinθ|≥10⁻³
  截断并在 HUD 提示"读数不可信"。
- 一维模型允许 θ 越过 0/π 的解析延拓，θ 超出 [0,π] 时 HUD 以 |θ| 读数。
- RK4 定步长（h≈0.002）无自适应；快支稳恒解本身动力学不稳定，长时间积分必然
  失稳（属物理事实，画面以提示说明）。
- 演示采用无量纲单位（I₁≡1）；实数量纲示例见书稿 ch05 数值算例。
