# 碰撞与变质量

> 用碰撞几何与变质量动力学分析光滑球碰撞、雨滴下落与弹性碰撞链，并以数值验证。

> 模块代号：06-collisions · 理论力学 · 交互讲义

## 作业映射

| 来源 | 核心知识点 | 页面对应 |
|---|---|---|
| 作业-5 Q1 | 光滑球碰撞、恢复系数、偏转角 | 模式=碰撞；HUD 显示 β |
| 作业-5 Q2 | 变质量雨滴、v(t) | 模式=雨滴；数值公式 |
| 作业-5 Q3 | 弹性碰撞链、反弹高度 | note.tex 推导 |

## 物理模型

光滑球碰撞：法向恢复系数 e，切向无摩擦。偏转角 β，最大偏转角条件 tan²α=(1-e)/2。

变质量雨滴：dr/dt=λ=const，v(t)=g/(4λ)[(r0+λt)-r0⁴/(r0+λt)³]，t→∞ 时 v~gt/4。

弹性碰撞链：m2≪m1 时，B2 反弹高度 H≈4h。

## 参数说明

| 参数 | 物理含义 | 默认值 | 范围 | 单位 |
|---|---|---|---|---|
| e | 恢复系数 | 0.5 | 0-1 | 无量纲 |
| α | 入射角 | 45 | 1-89 | 度 |
| 速度 | 动画速度倍率 | 1.0 | 0.1-3 | 倍 |

## 运行方式

- 讲义编译：`bash tools/build_note.sh modules/06-collisions`
- 交互页面：浏览器直接打开 `modules/06-collisions/index.html`
- HTML 检查：`/home/wck/.venv-tm/bin/python tools/check_html.py modules/06-collisions/index.html`
- 自测：打开 `modules/06-collisions/index.html?selftest=1`

## 验收

- `check_html.py`：6/6 通过。
- 无头自测：`?selftest=1` 为 5/5 PASS。

## 已知限制

- 仅无量纲模型。
- 雨滴为理想变质量（增加质量初速度为 0）。
- 不含相对论效应。
- RK4 固定步长。

## 证据

- [qa/T1-note.md](qa/T1-note.md)
- [qa/T2-html.md](qa/T2-html.md)
- [qa/T3-qa.md](qa/T3-qa.md)
