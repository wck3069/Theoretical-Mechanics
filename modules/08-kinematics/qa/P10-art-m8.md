# P10-art-m8 — M8 运动学动画美术改造

任务文件：`/tmp/tmfix/art-m8.md`（3D 球体视觉 + 三模式流畅动画）
改动文件：**仅** `modules/08-kinematics/index.html`（未动 TM-THEME 注入块与 selftest 数学）

## 实现

- **圆柱脱离（cylinder）**：接触段 RK4 积分 θ″=g·sinθ（R=1，θ 从 0.057°≈顶端静止释放），脱离段由切向速度 v=√(2g(1−cosθd)) 分解为水平/竖直分量后解析抛体；落出视野后 0.45s 淡出重置，淡入无缝循环。画面：圆柱截面阴影渐变+高光弧+紫描边、3D 球体小球（径向渐变+高光+辉光）、拖尾、脱离点虚线半径+圆环标记、θ 角弧、实时读数。
- **单摆（pendulum）**：RK4 积分 θ″=−(g/L)sinθ，从 θ0 静止释放，真实摆动；摆线、3D 球体摆锤（solar）、teal 拖尾、θ0 振幅参考虚线、支架+斜纹、T/T0 读数。
- **双摆（double）**：RK4 与拖尾保留，两个摆锤改为 3D 球体（cyan / violet），摆线与配件统一新配色。
- **动画机制**：requestAnimationFrame + 固定步长累积器（1/120s），`P.speed` 缩放时间流，360 步掉帧保护；`prefers-reduced-motion` 时跳过推进、静态示意。
- **配色**：void `#03050c`、solar `#ffd27a`、cyan `#7fe0ff`、violet `#b79bff`、teal `#7ff0cf`、text `#e8eeff`。
- **球体工具**：`window.TMART.sphere` 存在时优先调用，否则本地径向渐变兜底（仓库内暂无 TMART，走本地路径）。
- HUD：cylinder 模式实时显示当前 θ 与状态（在轨/抛体）；detached 角恒显 48.19°。

## 验证（本回合实测）

1. `check_html.py`：**6/6 PASS**（内联 JS 语法 3 块、无外链/协议相对/外部资源/fetch/CDN）。
2. `verify_selftest.py modules/08-kinematics/index.html`：**SELFTEST 5/5 PASS**（ST1 detach 48.1897、ST2 cos=0.666667、ST3 corr=0.001904、ST4 T、ST5 双摆能量漂移）。
3. 物理动画确定性校验（/tmp 一次性 harness，直接驱动 simStep，虚时间 4000ms）：
   - cylinder：接触段 9.75s→(起点微扰调至 0.057° 后) **7.45s**，脱离角恰为 **48.19°**，脱离速度 **v=0.8165=√(2g/3)**，抛体 1.72s 后触发淡出→重置→第二周期接触段同为 7.45s（循环确定）。
   - pendulum：7s 摆动（T≈6.295s）振幅保持在 [−10.00°, +10.00°]，4s RK4 能量漂移 **3.8e-14**。
   - double：dpStep 拖尾正常增长（200→500 pts），ST5 能量守恒已在 selftest 覆盖。
4. 截图像素普查（`--headless --screenshot`，虚拟时间 800ms，canvas 区）：cylinder 含 cyan 球/teal 角弧、solar 标记；pendulum 含 solar 摆锤；double 含 cyan+solar+violet 三色。三模式画面均正常渲染。

说明：headless 虚拟时间不持续泵 rAF（raf 计数 0–1），故动画流畅性以「simStep 直驱 + 循环确定性」为证据；真实浏览器 rAF 按帧触发，逻辑为标准固定步长累积器。

## 残留风险

- 虚拟时间截屏无法直接目视动画过程（headless 限制），已在真实浏览器打开 `index.html?mode=…` 建议 QA 复看一遍。
- cylinder 接触段默认 ~7.45s（g=1、R=1 的真实物理），可用 speed 参数加速。
