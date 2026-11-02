# 耦合系统与小振动

> 三个同类型系统合并在一个模块里：斜面滑块、弹簧摆、小车与单摆。共同点是两个广义坐标、一个循环坐标或一组线性化后的耦合振动。

> 模块代号：M10 · 10-coupled-systems · 理论力学 · 交互讲义

## 作业映射

| 来源 | 题目 | 核心知识点 | 页面对应 |
|---|---|---|---|
| 作业-8 Q3 | 斜面在光滑地面自由平移，物块沿斜面下滑 | 循环坐标、动能分配、约束力做功 | 场景「斜面滑块」：$a_{\rm rel}$、$a_X$、$\eta=K_{\rm wedge}/mgh$ |
| 作业-8 Q4 | 弹簧摆：弹簧长度 $r$ 与摆角 $\theta$ | 耦合方程、平衡位置、两种小振动 | 场景「弹簧摆」：$r_0$、$\omega_r$、$\omega_\theta$ |
| 作业-8 Q5 | 小车质量 $M$ 上挂单摆 $m,l$ | 水平动量守恒、小振动、$M\to\infty$ | 场景「小车与单摆」：$p_X$、$\omega$ |

## 物理模型

### Q3 斜面滑块

$$L=\frac12(M+m)\dot X^2+m\dot X\dot s\cos\alpha+\frac12m\dot s^2+mgs\sin\alpha$$

$$p_X=(M+m)\dot X+m\dot s\cos\alpha=0$$

$$a_{\rm rel}=\frac{(M+m)g\sin\alpha}{M+m\sin^2\alpha},\qquad
a_X=-\frac{mg\sin\alpha\cos\alpha}{M+m\sin^2\alpha}$$

$M=2m,\alpha=30^\circ$ 时，斜面动能占 $mgh$ 的 $2/9\approx0.2222$。

### Q4 弹簧摆

$$L=\frac12m(\dot r^2+r^2\dot\theta^2)-\frac12k(r-l_0)^2+mgr\cos\theta$$

$$r_0=l_0+\frac{mg}{k},\qquad
\omega_r=\sqrt{\frac{k}{m}},\qquad
\omega_\theta=\sqrt{\frac{g}{r_0}}$$

### Q5 小车与单摆

$$L=\frac12(M+m)\dot X^2+ml\cos\theta\,\dot X\dot\theta+\frac12ml^2\dot\theta^2+mgl\cos\theta$$

$$p_X=(M+m)\dot X+ml\cos\theta\,\dot\theta=0,\qquad
\omega=\sqrt{\frac{g(M+m)}{Ml}}$$

$M\to\infty$ 时 $\omega\to\sqrt{g/l}$。

## 参数说明

| 场景 | 参数 | 默认值 | 范围 | 单位 |
|---|---|---|---|---|
| Q3 | 质量比 $M/m$ | 2.00 | 0.5–5 | — |
| Q3 | 倾角 $\alpha$ | 30.0 | 10–60 | ° |
| Q4 | 劲度 $k$ | 80 | 20–200 | N/m |
| Q4 | 原长 $l_0$ | 0.50 | 0.2–1.2 | m |
| Q4 | 质量 $m$ | 1.00 | 0.2–2 | kg |
| Q4 | 初始角 $\theta_0$ | 17.2 | 5–35 | ° |
| Q5 | 质量比 $M/m$ | 3.00 | 0.5–8 | — |
| Q5 | 摆长 $l$ | 1.00 | 0.3–1.6 | m |
| Q5 | 初始角 $\theta_0$ | 14.3 | 3–30 | ° |
| 公共 | 动画速度 | 1.0 | 0.1–3 | × |

URL 场景切换：`index.html?scene=wedge`、`?scene=spring`、`?scene=cart`。

## 运行方式

- 讲义编译：`bash tools/build_note.sh modules/10-coupled-systems`
- 交互页面：浏览器直接打开 `index.html`
- HTML 检查：`/home/wck/.venv-tm/bin/python tools/check_html.py modules/10-coupled-systems/index.html`
- 自测：`index.html?selftest=1`
- 数值证据：`python3 qa/numeric_check.py`

## 验收记录

| 项目 | 结果 |
|---|---|
| note.tex 编译 | 退出码 0，`note.pdf` 5 页 |
| HTML 检查 | 6/6 通过 |
| 自测 | 11/11 PASS |
| 布局检查 | 1440×900、390×844 均通过 |
| 数值核对 | 10/10 PASS |

## 已知限制

- Q3 的 $X$ 位移按真实比例绘制，斜面的后退量看起来较小；滑块在 $s>0.9\,\mathrm{m}$ 后回到起点。
- Q4、Q5 用 RK4 固定步长（最大 $2\times10^{-3}\,\mathrm{s}$ / $4\times10^{-3}\,\mathrm{s}$）积分非线性方程。
- 弹簧保持 $r>l_0$；$r$ 过小时交互页会重置，避免弹簧穿过原长。
- 不含阻尼与驱动。

## 证据

- [qa/numeric_check.py](qa/numeric_check.py)
