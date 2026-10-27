# 运动学与非线性振动

> 用运动学与非线性振荡分析圆柱脱离、单摆周期修正、Lorentz 力与相对运动。

> 模块代号：08-kinematics · 理论力学 · 交互讲义

## 作业映射

| 来源 | 核心知识点 | 页面对应 |
|---|---|---|
| 作业-1 Q1 | 椭圆交点速度 | note.tex 推导 |
| 作业-1 Q2 | 圆周运动 v(t) | note.tex 推导 |
| 作业-1 Q3 | 相对运动、渡河 | note.tex 推导 |
| 作业-1 Q4 | Lorentz 力、回旋 | note.tex 推导 |
| 作业-1 Q5 | 单摆周期修正 | HUD 显示 T |
| 作业-1 Q6 | 圆柱脱离 | 模式=圆柱脱离；HUD 显示脱离角 |

## 物理模型

圆柱脱离：cos θ = 2/3，θ ≈ 48.19°。

单摆周期：T ≈ 2π√(L/g)(1 + θ0²/16)。

Lorentz 力：回旋半径 r = mv/(eB)，漂移 v_d = E×B/B²。

## 参数说明

| 参数 | 物理含义 | 默认值 | 范围 | 单位 |
|---|---|---|---|---|
| θ0 | 振幅 | 10 | 1-60 | 度 |
| L | 摆长 | 1.0 | 0.5-3 | 无量纲 |
| g | 重力加速度 | 1.0 | 0.5-3 | 无量纲 |

## 运行方式

- 讲义编译：`bash tools/build_note.sh modules/08-kinematics`
- 交互页面：浏览器直接打开 `modules/08-kinematics/index.html`
- HTML 检查：`/home/wck/.venv-tm/bin/python tools/check_html.py modules/08-kinematics/index.html`
- 自测：打开 `modules/08-kinematics/index.html?selftest=1`

## 验收

- `check_html.py`：6/6 通过。
- 无头自测：`?selftest=1` 为 5/5 PASS。

## 已知限制

- 仅无量纲模型。
- 单摆仅保留 θ0² 阶修正。
- 不含相对论效应。
- RK4 固定步长。

## 证据

- [qa/T1-note.md](qa/T1-note.md)
- [qa/T2-html.md](qa/T2-html.md)
- [qa/T3-qa.md](qa/T3-qa.md)
