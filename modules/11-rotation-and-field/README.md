# 旋转参考系与磁场

> 两个单粒子问题合并在一个模块里：电机驱动的竖直圆环上的珠子（有效势、稳定性、雅可比积分），以及均匀磁场中的带电粒子（诺特荷、回旋圆心）。

> 模块代号：M11 · 11-rotation-and-field · 理论力学 · 交互讲义

## 作业映射

| 来源 | 题目 | 核心知识点 | 页面对应 |
|---|---|---|---|
| 作业-8 Q5 | 圆环绕竖直直径以 $\Omega$ 转动，珠子沿环滑动 | 有效势、相对平衡、稳定性、$\mathcal E$ | 场景「旋转圆环」：$\Omega/\Omega_c$、$\theta_{\rm eq}$、$\mathcal E$ 与 $E_{\rm mech}$ |
| 作业-8 Q6 | 带电粒子在均匀磁场中运动 | 诺特荷、回旋圆心、规范动量 | 场景「磁场」：$Q_x$、$Q_y$、$p_x$、圆心 |

## 物理模型

### Q5 旋转圆环

$$L=\frac12mR^2\dot\theta^2+\frac12mR^2\Omega^2\sin^2\theta+mgR\cos\theta$$

$$\ddot\theta=\left(\Omega^2\cos\theta-\frac{g}{R}\right)\sin\theta$$

平衡：$\theta=0,\ \pi$；当 $\Omega\ge\Omega_c=\sqrt{g/R}$ 时出现
$\theta_{\rm eq}=\arccos\!\left(g/\Omega^2R\right)$。

$$\mathcal E=\frac12mR^2\dot\theta^2-\frac12mR^2\Omega^2\sin^2\theta-mgR\cos\theta$$

$$E_{\rm mech}=\mathcal E+mR^2\Omega^2\sin^2\theta$$

$\mathcal E$ 守恒，但不是惯性系机械能；差值是电机维持 $\Omega$ 输入的方位动能。

### Q6 均匀磁场中的带电粒子

$$L=\frac12m(\dot x^2+\dot y^2)+\frac{qB}{2}(x\dot y-y\dot x)$$

$$m\ddot x=qB\dot y,\qquad m\ddot y=-qB\dot x,\qquad \omega_c=\frac{qB}{m}$$

机械动量与规范动量都不守恒；平移对称性给出守恒的诺特荷：

$$Q_x=m\dot x-qBy,\qquad Q_y=m\dot y+qBx$$

回旋圆心 $(X_c,Y_c)=(x+\dot y/\omega_c,\ y-\dot x/\omega_c)$，满足
$Q_y=m\omega_cX_c$、$Q_x=-m\omega_cY_c$。

## 参数说明

| 场景 | 参数 | 默认值 | 范围 | 单位 |
|---|---|---|---|---|
| 圆环 | 半径 $R$ | 1.20 | 0.5–2 | m |
| 圆环 | 角速度 $\Omega$ | 2.00 | 0–5 | rad/s |
| 圆环 | 初始角 $\theta_0$ | 8.6 | 1–45 | ° |
| 磁场 | 磁感应强度 $B$ | 1.20 | 0.4–3 | 任意一致单位 |
| 磁场 | 初速度 $v_0$ | 1.00 | 0.4–2.5 | 任意一致单位 |
| 磁场 | 电荷符号 $q$ | +1 | −1/+1 | — |
| 公共 | 动画速度 | 1.0 | 0.1–3 | × |

URL 场景切换：`index.html?scene=ring`、`?scene=cyclotron`。

## 运行方式

- 讲义编译：`bash tools/build_note.sh modules/11-rotation-and-field`
- 交互页面：浏览器直接打开 `index.html`
- HTML 检查：`/home/wck/.venv-tm/bin/python tools/check_html.py modules/11-rotation-and-field/index.html`
- 自测：`index.html?selftest=1`
- 数值证据：`python3 qa/numeric_check.py`

## 验收记录

| 项目 | 结果 |
|---|---|
| note.tex 编译 | 退出码 0，`note.pdf` 4 页 |
| HTML 检查 | 6/6 通过 |
| 自测 | 12/12 PASS |
| 布局检查 | 1440×900、390×844 均通过 |
| 数值核对 | 11/11 PASS |

## 已知限制

- 圆环场景取 $m=1$；磁场场景取 $m=1$、$q=\pm1$，$B$ 与 $v_0$ 为任意一致单位。
- 圆环投影是几何投影，不做真实 3D 渲染；环的横向宽度随 $\Omega t$ 变化是投影效应。
- 不含辐射反作用、重力之外的力、相对论效应。

## 证据

- [qa/numeric_check.py](qa/numeric_check.py)
