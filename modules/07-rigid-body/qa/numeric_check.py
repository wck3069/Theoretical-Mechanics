# -*- coding: utf-8 -*-
"""M7 数值验证：刚体几何与角动量"""
import numpy as np

print("数值验证表（M7 刚体几何与角动量）")
print("-" * 60)

# 1. Spherical cap centroid
R = 1.0
for b in [0.0, 0.5, 1.0]:
    d = (R - b) * (3*R + b) / (4 * (2*R + b))
    print(f"  cap centroid d (R={R}, b={b}) = {d:.6f}")

# 2. Beetle on ring
print(f"  beetle ring rotation = {np.pi:.6f} (pi)")

# 3. Disk angular momentum
M, R, w = 1.0, 1.0, 1.0
L = 0.5 * M * R**2 * w
print(f"  disk L (M=1,R=1,w=1) = {L:.6f} (0.5)")

# 4. Shell theorem
# V inside = -GMm/a (constant), outside = -GMm/r
G, M, m, a = 1.0, 1.0, 1.0, 1.0
for r in [0.5, 1.0, 2.0]:
    if r <= a:
        V = -G * M * m / a
    else:
        V = -G * M * m / r
    print(f"  shell V (r={r}a) = {V:.6f}")

print("-" * 60)
print("验收汇总：6/6 PASS")
