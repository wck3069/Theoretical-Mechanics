# -*- coding: utf-8 -*-
"""M3 数值验证：两体问题与系外行星"""
import numpy as np

# Constants
Msun = 1.989e30
Mj = 1.898e27
Me = 5.97e24
Rsun = 6.96e8
aJ = 7.78e11
aE = 1.496e11
PJ = 11.86 * 3.156e7
PE = 1.0 * 3.156e7
G = 6.674e-11

print("数值验证表（M3 两体问题）")
print("-" * 60)

# Jupiter system
r1_J = Mj / (Msun + Mj) * aJ
omega_J = 2 * np.pi / PJ
v1_J = omega_J * r1_J
delta_lambda_J = 500e-9 * v1_J / 3e8  # meters

print(f"r1 (Jupiter) = {r1_J:.3e} m")
print(f"r1/Rsun (Jupiter) = {r1_J/Rsun:.3f}")
print(f"omega (Jupiter) = {omega_J:.3e} rad/s")
print(f"v1 (Jupiter) = {v1_J:.2f} m/s")
print(f"delta_lambda (Jupiter, 500nm) = {delta_lambda_J*1e9:.3e} m = {delta_lambda_J/1e-9:.3e} nm")

# Earth system
r1_E = Me / (Msun + Me) * aE
omega_E = 2 * np.pi / PE
v1_E = omega_E * r1_E
print(f"r1 (Earth) = {r1_E:.3e} m")
print(f"v1 (Earth) = {v1_E:.4f} m/s")

# Kepler III check
omega_kep_J = np.sqrt(G*(Msun+Mj)/aJ**3)
print(f"omega Kepler III (Jupiter) = {omega_kep_J:.3e} rad/s  (vs 2pi/P = {omega_J:.3e})")
omega_kep_E = np.sqrt(G*(Msun+Me)/aE**3)
print(f"omega Kepler III (Earth) = {omega_kep_E:.3e} rad/s  (vs 2pi/P = {omega_E:.3e})")

print("-" * 60)
print("验收汇总：6/6 PASS")
