# 刚体几何与角动量

> 用质心积分、角动量守恒与 Newton 球壳定理分析刚体几何与引力势。

> 模块代号：07-rigid-body · 理论力学 · 交互讲义

## 作业映射

| 来源 | 核心知识点 | 页面对应 |
|---|---|---|
| 作业-4 Q1 | 球冠质心 | 模式=球冠质心；滑块 R/b |
| 作业-4 Q2 | 甲虫转环 | note.tex 推导 |
| 作业-4 Q3 | 圆盘角动量 | 模式=圆盘；HUD 显示 L |
| 作业-4 Q4 | 球壳势能 | 模式=球壳势能；HUD 显示 V |

## 物理模型

球冠质心：d=(R-b)(3R+b)/[4(2R+b)]。半球 (b=0): d=3R/8。

甲虫-圆环：角动量守恒，环转角 π (180°)。

圆盘角动量：L=½MR²ω。

Newton 球壳：r<R 时 V=-GMm/R（常数），r>R 时 V=-GMm/r。

## 参数说明

| 参数 | 物理含义 | 默认值 | 范围 | 单位 |
|---|---|---|---|---|
| R | 球/圆盘半径 | 1.0 | 0.5-3 | 无量纲 |
| b | 平面距离 | 0.0 | 0-3 | 无量纲 |
| M | 质量 | 1.0 | 0.1-5 | 无量纲 |
| ω | 角速度 | 1.0 | 0.1-5 | 无量纲 |

## 运行方式

- 讲义编译：`bash tools/build_note.sh modules/07-rigid-body`
- 交互页面：浏览器直接打开 `modules/07-rigid-body/index.html`
- HTML 检查：`/home/wck/.venv-tm/bin/python tools/check_html.py modules/07-rigid-body/index.html`
- 自测：打开 `modules/07-rigid-body/index.html?selftest=1`

## 验收

- `check_html.py`：6/6 通过。
- 无头自测：`?selftest=1` 为 5/5 PASS。

## 已知限制

- 仅无量纲模型。
- 不含相对论效应。
- RK4 固定步长。

## 证据

- [qa/T1-note.md](qa/T1-note.md)
- [qa/T2-html.md](qa/T2-html.md)
- [qa/T3-qa.md](qa/T3-qa.md)
