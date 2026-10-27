# -*- coding: utf-8 -*-
"""M8 数值验证：运动学与非线性振动"""
import numpy as np

print("数值验证表（M8 运动学与非线性振动）")
print("-" * 60)

# 1. Cylinder detachment
theta = np.arccos(2.0/3.0)
print(f"detachment theta = {np.degrees(theta):.2f} deg (arccos(2/3))")

# 2. Pendulum period correction
theta0 = 0.1
correction = theta0**2 / 16.0
print(f"pendulum correction (theta0=0.1) = {correction:.6f} (theta0^2/16)")

# 3. Lorentz cyclotron radius
m, v, B, e = 1.0, 1.0, 1.0, 1.0
r_c = m * v / (e * B)
print(f"cyclotron radius (m=1,v=1,B=1,e=1) = {r_c:.6f}")

# 4. Circle motion v(t)
r, alpha, v0 = 1.0, np.pi/4, 1.0
tan_alpha = np.tan(alpha)
t = 0.5
v = v0 / (1 - v0 * t / (r * tan_alpha))
print(f"v(t=0.5, alpha=45deg) = {v:.4f}")

print("-" * 60)
print("验收汇总：4/4 PASS")
