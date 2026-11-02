# 虚功原理与静力学

> 用虚功原理与势能驻值法分析静力学平衡，计算梯子临界角，并以数值验证。

> 模块代号：05-virtual-work · 理论力学 · 交互讲义

## 作业映射

| 来源 | 核心知识点 | 页面对应 |
|---|---|---|
| 作业-7 Q1 | 半球碗中的均质棒 | note.tex 推导 |
| 作业-7 Q2 | 直角摆平衡角 | note.tex 推导 |
| 作业-7 Q3 | 圆槽中的两圆柱 | note.tex 推导 |
| 作业-7 Q4 | 梯子临界角 | HUD 显示 θ_min；滑块 μ/θ |
| 作业-7 Q5 | 弹簧杆平衡 | note.tex 推导 |

## 物理模型

虚功原理：平衡时 δW=0。保守系统 δV=0（势能驻值）。

梯子临界角：tan θ_min = 1/(2μ)。μ 增大时 θ_min 减小。

弹簧杆：势能 V(θ) = -Pl/2 sinθ + ½k(BC-l0)²，平衡 dV/dθ=0。

## 参数说明

| 参数 | 物理含义 | 默认值 | 范围 | 单位 |
|---|---|---|---|---|
| μ | 摩擦系数 | 0.5 | 0.05-2 | 无量纲 |
| θ | 梯子角度 | 45 | 5-85 | 度 |
| 速度 | 动画速度倍率 | 1.0 | 0.1-3 | 倍 |

## 运行方式

- 讲义编译：`bash tools/build_note.sh modules/05-virtual-work`
- 交互页面：浏览器直接打开 `modules/05-virtual-work/index.html`
- HTML 检查：`/home/wck/.venv-tm/bin/python tools/check_html.py modules/05-virtual-work/index.html`
- 自测：打开 `modules/05-virtual-work/index.html?selftest=1`

## 验收

- `check_html.py`：6/6 通过。
- 无头自测：`?selftest=1` 为 5/5 PASS。

## 已知限制

- 仅无量纲模型。
- 梯子为刚体，忽略变形。
- 不含相对论效应。
- RK4 固定步长。

## 证据

- [qa/T1-note.md](qa/T1-note.md)
- [qa/T2-html.md](qa/T2-html.md)
- [qa/T3-qa.md](qa/T3-qa.md)
