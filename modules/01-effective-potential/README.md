# 有效势与轨道稳定性

> 用有效势方法分析中心力场中的圆轨道、稳定性、径向振动与进动，并以 RK4 数值积分验证解析结论。

> 模块代号：01-effective-potential · 理论力学 · 交互讲义

## 作业映射

| 来源 | 核心知识点 | 页面对应 |
|---|---|---|
| 作业-2 Q3 | 高斯势稳定圆轨道存在条件、L_max | 势能=高斯；L 滑到 1.04 观察极小值消失 |
| 作业-2 Q4 | 幂律势 ω_r/ω_θ=√(k+2)，a=1/2 对应势 | 势能=幂律；HUD 直接显示频率比 |
| 作业-2 Q6 | 椭圆轨道近/远日点角速度比 | 开普勒椭圆预设；转折点标记 |
| 作业-2 Q7 | δV=γ/r³ 导致近心点进动、轨道不闭合 | γ/r³ 滑块；轨迹进动可视化 |
| 作业-3 Q1 | V=kr²/2 轨道为椭圆（中心在力心） | 势能=谐振子预设 |
| 作业-5 Q4 | 位力定理 ⟨T⟩、⟨V⟩ 验证 | HUD 能量漂移列佐证 T+V 守恒 |

## 物理模型

无量纲约定：m=1，Kepler 强度 α=1，高斯势 V0=λ=1。中心力 F=F(r)e_r 保守，存在 V(r)。有效势

V_eff(r)=V_base(r)+L²/(2r²)+γ/r³

其中 base 势与导数：

- 开普勒：V=-1/r，dV/dr=1/r²
- 谐振子：V=r²/2，dV/dr=r
- 高斯：V=-e^{-r²}，dV/dr=2r e^{-r²}
- 幂律：V=sgn(k) r^k，dV/dr=sgn(k) k r^{k-1}（β=sgn(k)）

导数与加速度：

dV_eff/dr = dV_base/dr - L²/r³ - 3γ/r⁴
r̈ = -dV_eff/dr
θ̇ = L/r²

积分：RK4，固定步长 DT=0.004（动画按速度缩放）。能量 E=½ṙ²+V_eff(r) 在 HUD 监控漂移。约束：扫描下限 R_MIN=0.05，扫描上限 R_SCAN=12；r>14 判逃逸，r<0.04 判奇异。

## 参数说明

| 参数 | 物理含义 | 默认值 | 范围 | 单位 |
|---|---|---|---|---|
| L | 角动量 | 1.2 | 0.05-3 | 无量纲 |
| E | 总能量 | -0.3 | -2-2 | 无量纲 |
| r0 | 初始半径 | 1.0 | 0.1-5 | 无量纲 |
| k | 幂律指数（仅幂律势） | 2 | -3-3 | 无量纲 |
| γ | γ/r³ 微扰强度 | 0 | 0-0.02 | 无量纲 |
| 速度 | 动画速度倍率 | 1 | 0.1-3 | 倍 |

### 有量纲示例

取谐振子势 V=r²/2（对应 m=1、ω=1 的无量纲约定）。若取质量单位 1 kg、长度单位 1 m、时间单位 1 s，则 ω=1 rad/s，r=1 无量纲对应 1 m，势能 V=½·1·1²=0.5 J；角动量 L=1 无量纲对应 1 kg·m²/s；能量 E=-0.3 无量纲对应 -0.3 J。

## 预设与 URL

预设（按钮）：

| 预设 | pot | L | E | r0 | k | γ | speed |
|---|---|---|---|---|---|---|---|
| kepler | kepler | 1.2 | -0.30 | 1.0 | - | 0 | 1 |
| circ | kepler | 1.2 | -0.3472 | 1.44 | - | 0 | 1 |
| gauss | gauss | 1.0 | -0.50 | 1.0 | - | 0 | 1 |
| precess | kepler | 1.2 | -0.30 | 1.0 | - | 0.006 | 1 |
| pow | pow | 1.0 | 0.60 | 1.0 | 2 | - | 1 |
| escape | kepler | 0.8 | 0.05 | 1.5 | - | 0 | 1 |

URL：`index.html?pot=kepler&L=1.2&E=-0.3&r0=1.0&k=2&gam=0&speed=1`，或 `index.html?preset=kepler`。非法值自动回退默认。自测：`index.html?selftest=1`。

## 运行方式

- 讲义编译：`bash tools/build_note.sh modules/01-effective-potential`
- 交互页面：浏览器直接打开 `modules/01-effective-potential/index.html`
- HTML 检查：`/home/wck/.venv-tm/bin/python tools/check_html.py modules/01-effective-potential/index.html`
- 自测：打开 `modules/01-effective-potential/index.html?selftest=1`

## 验收

- `check_html.py`：6/6 通过。
- 无头自测：`?selftest=1` 为 5/5 PASS。
- 三档视口无横向溢出：1440/768/500 下 `scrollWidth==innerWidth`；Chrome 将视口钳制到 500，因此移动端截图取 360，但 DOM 度量在 500。

## 已知限制

- 仅无量纲模型，m=1、α=1。
- γ/r³ 项为现象学微扰，非严格相对论修正。
- 绘图扫描范围 r∈[0.05,12]；r>14 判逃逸，r<0.04 判奇异并停止。
- 不含相对论效应。
- RK4 固定步长 DT=0.004。
- Chrome 无头模式视口最小约 500 px，移动端截图使用 360。

## 证据

- [qa/T1-note.md](qa/T1-note.md)
- [qa/T2-html.md](qa/T2-html.md)
- [qa/T3-qa.md](qa/T3-qa.md)
