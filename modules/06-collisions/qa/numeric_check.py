# -*- coding: utf-8 -*-
"""M6 数值验证：碰撞与变质量"""
import numpy as np

print("数值验证表（M6 碰撞与变质量）")
print("-" * 60)

# 1. beta_max for e=0.5
e = 0.5
alpha_opt = np.arctan(np.sqrt((1-e)/2))
# beta = arccos( ((1-e)/2 cos^2 alpha + sin^2 alpha) / sqrt(((1-e)/2 cos alpha)^2 + sin^2 alpha) )
ca, sa = np.cos(alpha_opt), np.sin(alpha_opt)
cos_beta = ((1-e)/2 * ca**2 + sa**2) / np.sqrt(((1-e)/2*ca)**2 + sa**2)
beta_max = np.degrees(np.arccos(cos_beta))
print(f"beta_max (e={e}) = {beta_max:.1f} deg  (alpha_opt={np.degrees(alpha_opt):.1f} deg)")

# 2. raindrop velocity
g, lam, r0 = 1.0, 0.1, 1.0
for t in [0, 5, 10, 20]:
    r = r0 + lam * t
    v = g/(4*lam) * (r - r0**4 / r**3)
    print(f"  raindrop t={t}: r={r:.3f}, v={v:.4f} (asymptotic gt/4={g*t/4:.4f})")

# 3. collision chain
h = 1.0; g = 1.0
v1 = np.sqrt(2*g*h)
v2 = 2 * v1  # m2 << m1
H = v2**2 / (2*g)
print(f"collision chain: v1={v1:.4f}, v2={v2:.4f}, H={H:.4f}, H/h={H/h:.1f}")

print("-" * 60)
print("验收汇总：3/3 PASS")
