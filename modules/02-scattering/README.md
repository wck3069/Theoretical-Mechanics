# 散射与俘获

> 用散射实验与有效势垒分析中心力场中的散射角、微分散射截面与俘获截面，并以 RK4 数值积分验证解析结论。

> 模块代号：02-scattering · 理论力学 · 交互讲义

## 作业映射

| 来源 | 核心知识点 | 页面对应 |
|---|---|---|
| 作业-3 Q2 | 排斥势 k/r² 散射：散射角、微分散射截面、总截面发散 | 模式=散射；HUD 显示 Θ |
| 作业-3 Q3 | 吸引势 -α/r⁴ 俘获：临界 b_c、俘获截面 σ | 模式=俘获；HUD 显示 b_c、σ |

## 物理模型

无量纲约定：m=1，散射能量 E>0。

- 排斥势：V(r)=k/r²（k>0）
- 吸引势：V(r)=-α/r⁴（α>0）

散射角：Θ = π(1 - 1/√(1+k/(Eb²)))

微分散射截面：dσ/dΩ = (k/E)·(1-x)/[π·x²·(2-x)²·sin(πx)]，x=Θ/π

俘获：b_c = (4α/E)^{1/4}，σ = 2π√(α/E)

## 参数说明

| 参数 | 物理含义 | 默认值 | 范围 |
|---|---|---|---|
| E | 入射能量 | 1.0 | 0.1-5 |
| k/α | 势强度 | 1.0 | 0.1-5 |
| b | 碰撞参数 | 1.0 | 0-5 |
| 速度 | 动画速度 | 1.0 | 0.1-3 |

## 运行方式

- 讲义编译：bash tools/build_note.sh modules/02-scattering
- 交互页面：浏览器直接打开 modules/02-scattering/index.html
- HTML 检查：/home/wck/.venv-tm/bin/python tools/check_html.py modules/02-scattering/index.html
- 自测：打开 modules/02-scattering/index.html?selftest=1

## 验收

- check_html.py：6/6 通过。
- 无头自测：?selftest=1 为 5/5 PASS。

## 已知限制

- 仅无量纲模型。
- 排斥势 k/r² 为长程势，总散射截面发散。
- 不含相对论效应。

## 证据

- [qa/T1-note.md](qa/T1-note.md)
- [qa/T2-html.md](qa/T2-html.md)
- [qa/T3-qa.md](qa/T3-qa.md)
