# 有转动惯量的 Atwood 机

> 用拉格朗日量处理有转动惯量的定滑轮：加速度多出一个等效质量，绳两端张力不再相等。

> 模块代号：M9 · 09-atwood-pulley · 理论力学 · 交互讲义

## 作业映射

| 来源 | 题目 | 核心知识点 | 讲义章节 |
|---|---|---|---|
| 作业-8 Q1 | 定滑轮两端挂 $m_1,m_2$，绳不打滑，求 $a,T_1,T_2$ | 拉格朗日量、转动惯量、张力差 | note.tex §3–§4 |

## 物理模型

取 $m_2$ 向下的位移 $s$ 为广义坐标。绳不打滑，滑轮转角 $\varphi=s/R$。

$$L=\frac12\left(m_1+m_2+\frac{I}{R^2}\right)\dot s^2+(m_2-m_1)gs$$

$$a=\frac{(m_2-m_1)g}{m_1+m_2+I/R^2},\qquad
T_1=m_1(g+a),\qquad T_2=m_2(g-a)$$

$$T_2-T_1=\frac{Ia}{R^2}$$

$I=0$ 时 $T_1=T_2$，退化为理想滑轮。

## 参数说明

| 参数 | 物理含义 | 默认值 | 范围 | 单位 |
|---|---|---|---|---|
| $m_1$ | 左侧质量 | 1.00 | 0.2–5 | kg |
| $m_2$ | 右侧质量 | 2.00 | 0.2–8 | kg |
| $I$ | 滑轮转动惯量 | 0.50 | 0–4 | kg·m² |
| $R$ | 滑轮半径 | 0.20 | 0.05–0.5 | m |
| 速度 | 动画速度倍率 | 1.0 | 0.1–3 | × |

## 运行方式

- 讲义编译：`bash tools/build_note.sh modules/09-atwood-pulley`
- 交互页面：浏览器直接打开 `index.html`（单文件、离线可用）
- HTML 检查：`/home/wck/.venv-tm/bin/python tools/check_html.py modules/09-atwood-pulley/index.html`
- 自测：`index.html?selftest=1`
- 数值证据：`python3 qa/numeric_check.py`

## 验收记录

| 项目 | 结果 |
|---|---|
| note.tex 编译 | 退出码 0，`note.pdf` 4 页 |
| HTML 检查 | 6/6 通过 |
| 自测 | 10/10 PASS |
| 布局检查 | 1440×900、390×844 均通过 |
| 数值核对 | 3/3 PASS，RK4 相对误差 $1.4\times10^{-12}$、$1.5\times10^{-12}$ |

## 已知限制

- 绳不可伸长、不打滑；轮轴无摩擦；绳质量忽略。
- 动画在 $s>1.15\,\mathrm{m}$ 时自动回到起点，只影响演示，不影响公式。
- 重力取 $g=9.81\,\mathrm{m/s^2}$，不含空气阻力。

## 证据

- [qa/numeric_check.py](qa/numeric_check.py)
