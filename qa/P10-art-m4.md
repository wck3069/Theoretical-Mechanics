# P10 art M4 — 变分页折射/最短路径模式

## 实现摘要
- `modules/04-variational/index.html`：下拉框 `refraction`、`shortest` 去掉 `disabled`。
- 新增折射率滑块 `param-n`（1.0–2.5，默认 1.5），接入 DEFAULTS/RANGE/loadFromURL/syncURL/slider 绑定。
- `refraction` 模式：水平界面在画布中线，上介质 n1=1、下介质 n2=P.n；Snell 数值求界面交点（三分搜索）；绘制入射/折射光线、法线虚线、θ1/θ2 角弧与数值；光脉冲沿折线循环前进，界面处高光。
- `shortest` 模式：A 左上、B 右下；直线轨道与下凹曲线轨道；两球同时出发，速度按 √(2gΔy) 变化，曲线球先到 B；显示计时与“更短 ≠ 更快”。
- `cycloid` 模式保留，小球改为 3D 球体视觉 + 拖尾，等时性演示不变。
- 预渲染球体 sprite，requestAnimationFrame 驱动，配色统一为 void/solar/cyan/violet/teal/text。

## 截图建议
- `?mode=refraction&n=1.5`：界面交点、双光线、角弧、脉冲。
- `?mode=shortest`：两球位置差、计时对比。
- `?mode=cycloid`：4 球拖尾与等时到达。

## 遗留风险
- 时间/速度为无量纲演示单位，不同模式时间尺度不统一。
- 角弧绘制方向为近似，极端 n 下 θ2 可能接近临界角。
- 曲线轨道为正弦下凹近似，非严格摆线/最速降线。
