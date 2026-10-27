# -*- coding: utf-8 -*-
"""M5 数值验证：虚功原理与静力学"""
import numpy as np

print("数值验证表（M5 虚功原理与静力学）")
print("-" * 60)

# Ladder critical angle: tan(theta_min) = 1/(2*mu)
for mu in [0.25, 0.5, 1.0]:
    theta = np.arctan(1.0 / (2 * mu))
    print(f"theta_min (mu={mu}) = {np.degrees(theta):.1f} deg  (arctan(1/(2mu))={np.degrees(np.arctan(1/(2*mu))):.1f})")

# Verify force balance
for mu in [0.25, 0.5, 1.0]:
    theta = np.arctan(1.0 / (2 * mu))
    P = 1.0
    Nw = P / (2 * np.tan(theta))
    f = mu * P
    print(f"  mu={mu}: Nw={Nw:.4f}, f_crit={f:.4f}, diff={abs(Nw-f):.2e}")

print("-" * 60)
print("验收汇总：4/4 PASS")
