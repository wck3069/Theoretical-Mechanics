# 双曲运动与恒固有加速度

> 模块代号：M30 · 23-hyperbolic-motion · 理论力学 · 交互讲义（ch07 狭义相对论）
>
> 恒定固有加速度 $a$（本页取 $c=1$）的质点从静止、位置 $x_0=1/a$ 出发，世界线是双曲线
> $x^2-t^2=1/a^2$：$t=\sinh(a\tau)/a$、$x=\cosh(a\tau)/a$、$v(t)=t/\sqrt{t^2+1/a^2}<1$、
> $\tau(t)=\operatorname{arsinh}(at)/a$、快度 $\eta=a\tau$。$t=0$ 从原点发出的光子沿 $x=t$
> 追逐，间距 $\sqrt{t^2+1/a^2}-t=e^{-a\tau}/a\to0$ 却永不归零——$x=t$ 正是 Rindler 视界。
> 坐标加速度 $dv/dt=a/\gamma^3$，恒固有加速度 $\ne$ 恒坐标加速度。

## 书稿映射

| 来源 | 主题 | 核心知识点 | 手稿章节 |
|---|---|---|---|
| ch07 | 闵可夫斯基时空与固有时 · 不变间隔与因果分类 | $(x,ct)$ 等尺度图上光锥 $45^\circ$、类时世界线在光锥内、$(+,-,-,-)$ 号差 | manuscript/chapters/ch07.tex §闵可夫斯基时空与固有时（191 行起） |
| ch07 | 变速世界线与双生子 | $\tau=\int\sqrt{1-u^2/c^2}\,dt$、直线世界线固有时最大（数学注记 307 行）、快度 modernbox（317 行） | ch07.tex §变速世界线与双生子（265 行起） |
| ch07 | 恒力运动与固有加速度 | $p=Ft$、$u(t)=\frac{Ft/m}{\sqrt{1+(Ft/mc)^2}}$、$\dd u/\dd t=(F/m)[1+(Ft/mc)^2]^{-3/2}$、$\chi=\alpha\tau/c$、$(x+c^2/\alpha)^2-c^2t^2=(c^2/\alpha)^2$、恒力例 $\alpha=F/m$ | ch07.tex §恒力运动与固有加速度（523 行起） |
| ch07 | 计算与模拟：沿世界线积累固有时 | 逐片积分 $\tau$、加密时间片收敛检验（860 行起） | ch07.tex §计算与模拟（860 行起） |

注：手稿把恒力例子画成 $x(t)=\frac{mc^2}{F}[\sqrt{1+(Ft/mc)^2}-1]$（原点出发）；本页把起点平移为
$x_0=1/a$，使双曲线恰为 $x^2-t^2=1/a^2$，与 $t=\sinh(a\tau)/a,\ x=\cosh(a\tau)/a$ 完全一致。
本模块的固有加速度即手稿的 $\alpha$（一维、恒质量时 $\alpha=F/m$）。

## 物理模型

- 状态 $(v,x,\tau)$ 对坐标时 $t$ 联立积分：$\dot v=a(1-v^2)^{3/2}=a/\gamma^3$、$\dot x=v$、
  $\dot\tau=\sqrt{1-v^2}=1/\gamma$，RK4 定步长 $h=0.001$；解析基准 $x=\sqrt{t^2+1/a^2}$、
  $v=t/\sqrt{t^2+1/a^2}$、$\tau=\operatorname{arsinh}(at)/a$、$\gamma=\sqrt{1+a^2t^2}=\cosh\eta$。
- 场景1（`?scene=worldline`）：闵氏图，$ct$ 竖直、$x$ 水平、两轴等尺度（光锥严格 $45^\circ$，
  与模块 13 约定一致）。双曲世界线（数值实线 + 解析虚线）、观察者和惯性对照（$x=v_i t$）动点、
  从原点的光子 $x=t$（与视界母线重合）与其间间距高亮；区域 $x<t$（任何信号追不上加速者）
  用淡青色阴影标出，$x=t$ 以金色长虚线标为 Rindler 视界。视图随 $t$ 自适应放大。
- 场景2（`?scene=velocity`）：$v(t)$ 数值 vs 解析 vs 牛顿线 $v=at$，在 $t=1/a$ 处红叉标出
  牛顿越界点，$v=1$ 金色渐近线；右上角内嵌 $\eta=a\tau$ 线性图；HUD 给 $dv/dt=a/\gamma^3$。
- 场景3（`?scene=clock`）：固有时逐段累积曲线 $\tau(t)$（数值）vs $\tau=t$（惯性留守），
  加底部两根钟面进度条；HUD 给 $\tau$、$t$、$\tau/t$、年龄差 $t-\tau$。

## 参数说明

| 参数 | 物理含义 | 默认值 | 范围 | 单位/说明 |
|---|---|---|---|---|
| a | 固有加速度（固有时测得的加速度；恒力例 $a=F/m$） | 1.00 | 0.2–3 | $c=1$ 制；自然长度/时间单位即 $1/a$ |
| vi | 场景1 惯性对照世界线 $x=v_i t$ 的速度（从原点） | 0.60 | 0.05–0.95 | $c=1$ 制 |
| photon | 场景1 是否从原点（t=0）发射追逐光子 $x=t$ | 1（开） | 0/1 | 该光子线恰是 Rindler 视界母线 |
| tend | 场景3 旅程总坐标时 $t_{\rm end}$ | 10.0 | 2–30 | $c=1$ 制 |
| speed | 动画时间倍率（RK4 $h=0.001$ 上的累加器） | 0.50 | 0.05–3 | × |

场景：`?scene=worldline|velocity|clock`；自测：`?selftest=1`（不启动动画）。
URL 完整示例：`index.html?scene=worldline&a=1&vi=0.6&photon=1&tend=10&speed=0.5`；
非法参数自动回退默认值。预设按钮：标准双曲（a=1）、高加速度（a=2.5）、光子追逐（a=0.5）、
牛顿对照（场景2）、双生子（场景3，a=1，t_end=10）。

## 运行方式

- **交互页面**：浏览器直接打开 `index.html`——单文件、离线可用（星空背景依赖仓库内
  `../../assets/cosmos/`，需保持仓库目录结构）
- **HTML 检查**：`/home/wck/.venv-tm/bin/python tools/check_html.py modules/23-hyperbolic-motion/index.html`
- **自测**：`index.html?selftest=1`，或
  `/home/wck/.venv-tm/bin/python tools/verify_selftest.py modules/23-hyperbolic-motion/index.html`
- **渲染冒烟**：`google-chrome --headless=new --dump-dom …/index.html | grep -c canvas`

## 验收记录

| 日期 | 项目 | 命令 | 结果 |
|---|---|---|---|
| 2026-11-23 | HTML 检查 | `/home/wck/.venv-tm/bin/python tools/check_html.py modules/23-hyperbolic-motion/index.html` | 6/6 项通过，0 项失败（EXIT_CODE=0，1 个内联 script 块 esprima 4.0.1 解析通过） |
| 2026-11-23 | selftest | `/home/wck/.venv-tm/bin/python tools/verify_selftest.py modules/23-hyperbolic-motion/index.html` | `PASS 23-hyperbolic-motion pass=20 fail=0`（面板末行 `SELFTEST 19/19 PASS`） |
| 2026-11-23 | 渲染冒烟 | `google-chrome --headless=new --dump-dom …/index.html \| grep -c canvas` | `3`（场景 canvas + 星空背景；无 JS 异常） |
| 2026-11-23 | 三场景截图 | `google-chrome --headless=new --window-size=1280,820 --virtual-time-budget=9000 --screenshot` | /tmp/opencode/shot-hyp-worldline.png、shot-hyp-velocity.png、shot-hyp-clock.png |
| 2026-11-23 | 运行时错误探测 | headless `--enable-logging=stderr`（三场景各 9s 虚拟时间） | 0 errors；HUD 与解析值一致（worldline t=0.583：γ=1.158=cosh(aτ)、间距 0.57454=√(t²+1)−t；velocity η=0.625、γ=cosh η=1.201、dv/dt=a/γ³=0.577；clock τ=0.481=asinh(0.5)、终点 τ/t=0.2998、年龄差 7.002） |

selftest 断言明细（19 条，均 PASS；RK4 h=1e-3，a=1）：

1. ST1 状态有界：x=20.024984 > t=20.000000，v=0.998752339 < 1
2. ST1 双曲不变量 max|x²−t²−1/a²| = 1.0874e-10 < 1e-8（t 积到 20）
3. ST2 v<1 全程：max v = 0.998752338878
4. ST2 v(t) t=1：7.071068e-1，relerr 1.99e-14
5. ST2 v(t) t=5：9.805807e-1，relerr 6.79e-16
6. ST2 v(t) t=20：9.987523e-1，relerr 3.00e-15
7. ST3 τ(t) t=1：8.813736e-1，relerr 1.30e-14
8. ST3 τ(t) t=5：2.312438e+0，relerr 9.60e-16
9. ST3 τ(t) t=20：3.689504e+0，relerr 9.00e-14
10. ST4 快度相加 η=0.5+0.9：tanh(η₁+η₂) vs (v₁+v₂)/(1+v₁v₂)，relerr 0
11. ST4 快度相加 η=1.2+2.1：relerr 0
12. ST4 快度相加 η=0.3+3.0：relerr 0
13. ST5 t=100 光子未追上：gap = 4.999875e-3 > 0
14. ST5 数值间距 vs √(t²+1/a²)−t：relerr 2.27e-8
15. ST5 间距 vs e^(−aτ)/a：relerr 2.27e-8
16. ST6 牛顿位置 x(t)（a=1, at=0.1）：1.004988 vs 1.005，relerr 1.24e-5
17. ST6 牛顿速度 v(t)（a=1, at=0.1）：0.099504 vs 0.1，relerr 4.96e-3
18. ST6 牛顿位置 x(t)（a=0.5, at=0.1）：2.009975 vs 2.01，relerr 1.24e-5
19. ST6 牛顿速度 v(t)（a=0.5, at=0.1）：0.099504 vs 0.1，relerr 4.96e-3

## 已知限制

- 演示取 $c=1$ 的无量纲制：$x$、$t$、$1/a$ 同一单位；换实数场景（如 $a=1\,$ly/y²≈9.7e-8 ly/y²
  量级）只需把长度单位取 $c^2/a$、时间单位取 $c/a$。
- RK4 定步长 h=0.001、无自适应；$v$ 达到 $1-10^{-12}$ 后截断（HUD 提示「已触发」），
  不加防护时 $1-v^2$ 可能因舍入变负使 $\sqrt{1-v^2}$ 出 NaN——这是页面对 $v\to1$ 的显式钳制。
- 场景1 的追光光子恰从原点发出，其轨迹与 Rindler 视界母线重合：这是特例（一般 $t_0>0$
  从 $x=0$ 发出的光子会更早且同样追不上）；页面按手稿图景取 $t_0=0$。
- 场景1 惯性对照从原点出发（$x=v_i t$），不与加速者同起点；它只用于对比直线 vs 双曲线
  世界线，不比较两者钟速（钟速比较在场景3）。
- 场景3 的加速者沿单一双曲线无限远离，不是「掉头重逢」版双生子（手稿 §双生子的瞬时掉头
  折线模型在模块 13 的场景里已有）；这里演示的是视界意义下的单向旅程：$t\to\infty$
  时留守者年龄 $\to\infty$ 而飞船钟 $\sim\ln t/a$。
- 视图随 $t$ 自适应缩小比例：$t$ 很大时双曲线与 $x=t$ 在图上几乎重合——这正是
  「间距指数消失」的几何真相，具体数值以 HUD（间距解析值）为准。
