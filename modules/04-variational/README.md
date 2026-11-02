# 变分原理与等时摆

> 用变分原理导出折射定律与最短路径，证明摆线的等时性，并以数值积分验证等时性离散度。

> 模块代号：04-variational · 理论力学 · 交互讲义

## 作业映射

| 来源 | 核心知识点 | 页面对应 |
|---|---|---|
| 作业-6 Q1 | 费马原理、折射定律 | 模式=折射 |
| 作业-6 Q2 | 最短路径、直线 | 模式=最短路径 |
| 作业-6 Q3 | 摆线等时性 | 模式=等时摆；赛跑动画 |
| 作业-6 Q3(d) | 一般等时条件 h=Cs² | 数值验证 |

## 物理模型

变分原理：物理路径使泛函 J[y]=∫L(x,y,y')dx 取驻值，Euler-Lagrange 方程 ∂L/∂y - d/dx(∂L/∂y')=0。

费马原理：光程时间 T=∫n(s)/c ds 取驻值 → Snell 定律 n1 sinθ1=n2 sinθ2。

最短路径：弧长 S=∫ds 取驻值 → 直线 y=kx+c。

等时摆：摆线 h=s²/(8a)，下滑时间 T=π√(a/g)，与释放位置无关。一般：h=Cs²，T0=π/(2√(2gC))。

## 参数说明

| 参数 | 物理含义 | 默认值 | 范围 | 单位 |
|---|---|---|---|---|
| a | 摆线参数 | 1.0 | 0.1-3 | 无量纲 |
| g | 重力加速度 | 1.0 | 0.1-3 | 无量纲 |
| 速度 | 动画速度倍率 | 1.0 | 0.1-3 | 倍 |

## 运行方式

- 讲义编译：`bash tools/build_note.sh modules/04-variational`
- 交互页面：浏览器直接打开 `modules/04-variational/index.html`
- HTML 检查：`/home/wck/.venv-tm/bin/python tools/check_html.py modules/04-variational/index.html`
- 自测：打开 `modules/04-variational/index.html?selftest=1`

## 验收

- `check_html.py`：6/6 通过。
- 无头自测：`?selftest=1` 为 5/5 PASS。

## 已知限制

- 仅无量纲模型。
- 等时摆为理想无摩擦。
- 不含相对论效应。
- RK4 固定步长。

## 证据

- [qa/T1-note.md](qa/T1-note.md)
- [qa/T2-html.md](qa/T2-html.md)
- [qa/T3-qa.md](qa/T3-qa.md)
