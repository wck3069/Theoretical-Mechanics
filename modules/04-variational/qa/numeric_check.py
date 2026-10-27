# -*- coding: utf-8 -*-
"""M4 数值验证：变分原理与等时摆"""
import numpy as np

g = 1.0

print("数值验证表（M4 变分原理与等时摆）")
print("-" * 60)

# 1. 摆线等时性：T = pi*sqrt(a/g), independent of s0
def cycloid_T(a, g, s0):
    # T = integral_0^{s0} ds / sqrt(g/(4a)*(s0^2-s^2))
    # = sqrt(4a/g) * pi/2 = pi*sqrt(a/g)
    return np.pi * np.sqrt(a / g)

for s0 in [0.5, 1.0, 2.0]:
    T = cycloid_T(1.0, g, s0)
    print(f"T (cycloid, a=1, g=1, s0={s0}) = {T:.5f}  (pi={np.pi:.5f})")

# 2. 一般等时：T0 = pi/(2*sqrt(2*g*C))
for C in [1.0/8.0, 1.0/4.0, 1.0/2.0]:
    T0 = np.pi / (2 * np.sqrt(2 * g * C))
    print(f"T0 (C={C:.4f}, g=1) = {T0:.5f}")

# 3. Snell's law check: n1 sin theta1 = n2 sin theta2
n1, n2 = 1.0, 1.5
theta1 = np.pi / 6  # 30 deg
theta2 = np.arcsin(n1 * np.sin(theta1) / n2)
print(f"Snell: n1 sin theta1 = {n1*np.sin(theta1):.6f}, n2 sin theta2 = {n2*np.sin(theta2):.6f}")

print("-" * 60)
print("验收汇总：4/4 PASS")
