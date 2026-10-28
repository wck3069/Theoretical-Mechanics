# P10 art M8 — 圆柱脱离 / 单摆 / 双摆动画

- 圆柱：小球从顶端沿圆柱下滑到 48.19° 脱离，之后抛体运动，循环；3D 球体 + 拖尾 + 脱离点标记。
- 单摆：RK4 积分 θ''=-(g/L)sinθ，固定步长 1/120s 累积，P.speed 缩放；摆锤 3D 球体 + 拖尾 + 周期读数。
- 双摆：保留原 RK4，两个摆锤改为 3D 球体视觉，拖尾保留。
- `prefers-reduced-motion` 时静态示意；`window.TMART.sphere` 优先，缺失时本地径向渐变兜底。
- 验证：check_html 6/6；selftest 5/5 PASS。
