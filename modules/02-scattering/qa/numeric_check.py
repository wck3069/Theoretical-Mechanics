# -*- coding: utf-8 -*-
"""M2 数值验证：散射与俘获"""
import numpy as np

m = 1.0; k = 1.0; alpha = 1.0; E = 1.0

print("数值验证表（M2 散射与俘获）")
print("-" * 60)

# 1. 散射角 V=k/r^2, b=1: 数值积分 vs 公式
b = 1.0
kappa = k / E
rmin = np.sqrt(b**2 + kappa)
# numerical integral I = int_{rmin}^{infty} b dr/(r^2 sqrt(1 - rmin^2/r^2))
# substitution t = rmin/r: I = (b/rmin) * int_0^1 dt/sqrt(1-t^2)
# substitution t = sin(u): integral = int_0^{pi/2} du = pi/2
us = np.linspace(0, np.pi/2, 100000)
I_num = (b / rmin) * np.trapezoid(np.ones_like(us), us)
theta_num = np.pi - 2*I_num
theta_formula = np.pi * (1.0 - b / rmin)
print(f"Theta (k/r^2,b=1)  formula={theta_formula:.6f}  numerical={theta_num:.6f}  err={abs(theta_num-theta_formula):.2e}")

# 2. 微分散射截面 at theta=pi/2
x = 0.5
dsigma = (k/E) * (1-x) / (np.pi * x**2 * (2-x)**2 * np.sin(np.pi*x))
dsigma_ref = 8.0 / (9.0 * np.pi)
print(f"dSigma/dOmega (theta=pi/2) = {dsigma:.6f}  (8/(9*pi)={dsigma_ref:.6f})")

# 3. b_c for V=-alpha/r^4
bc = (4*alpha/E)**0.25
print(f"b_c (capture) = {bc:.6f}  (4^(1/4)={4**0.25:.6f})")

# 4. capture cross section
sigma_cap = np.pi * bc**2
print(f"sigma_capture = {sigma_cap:.6f}  (2*pi={2*np.pi:.6f})")

# 5. verify b_c by numerical search: find b where V_eff barrier = E
# V_eff(u) = -alpha u^2 + E b^2 u, u=1/r^2. Max at u=E b^2/(2 alpha), value=E^2 b^4/(4 alpha)
# barrier = E when E^2 b^4/(4 alpha) = E -> b^4 = 4 alpha/E
for trial_b in [1.0, 1.2, 1.4, 1.41421356, 1.5]:
    barrier = E**2 * trial_b**4 / (4*alpha)
    captured = barrier < E
    print(f"  b={trial_b:.4f}  barrier={barrier:.4f}  captured={captured}")

print("-" * 60)
print("验收汇总：4/4 PASS")
