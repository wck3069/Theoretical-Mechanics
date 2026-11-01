# -*- coding: utf-8 -*-
"""M10 数值验证：耦合系统与小振动（作业-8 Q3/Q4/Q5）"""
import math
G = 9.81
print("M10 数值验证（作业-8 Q3/Q4/Q5）")
print("-" * 72)
ok = total = 0

def check(name, got, want, tol=1e-6):
    global ok, total
    total += 1
    good = abs(got - want) <= tol
    ok += good
    print(f"{name:44s} {got:14.6f}  expect {want:14.6f}  {'PASS' if good else 'FAIL'}")

# Q3
M_over_m, alpha = 2.0, math.radians(30)
den = M_over_m + math.sin(alpha) ** 2
a_rel = G * math.sin(alpha) * (M_over_m + 1) / den
a_X = -G * math.sin(alpha) * math.cos(alpha) / den
k = math.cos(alpha) / (M_over_m + 1)
eta = M_over_m * k * k / (M_over_m * k * k + 1 - 2 * k * math.cos(alpha) + k * k)
check("Q3 a_rel", a_rel, 6.54, 1e-3)
check("Q3 a_X", a_X, -1.88794, 1e-4)
check("Q3 eta", eta, 2 / 9, 1e-12)
total += 1
res = (1 + M_over_m) * a_X + a_rel * math.cos(alpha)
good = abs(res) < 1e-12
ok += good
print(f"{'Q3 水平动量残差':44s} {res:14.2e}  {'PASS' if good else 'FAIL'}")

# Q4
k_s, l0, m = 80.0, 0.5, 1.0
r0 = l0 + m * G / k_s
check("Q4 r0", r0, 0.622625, 1e-6)
check("Q4 omega_r", math.sqrt(k_s / m), 8.944272, 1e-6)
check("Q4 omega_theta", math.sqrt(G / r0), 3.96937, 1e-4)

# Q5
ratio, l = 3.0, 1.0
check("Q5 omega", math.sqrt(G * (ratio + 1) / (ratio * l)), 3.61663, 1e-4)
check("Q5 M->inf omega", math.sqrt(G / l), 3.13209, 1e-4)
th, om = 0.2, 0.7
vX = -l * math.cos(th) * om / (ratio + 1)
pX = (ratio + 1) * vX + l * math.cos(th) * om
total += 1
good = abs(pX) < 1e-12
ok += good
print(f"{'Q5 p_X':44s} {pX:14.2e}  {'PASS' if good else 'FAIL'}")
print("-" * 72)
print(f"验收汇总：{ok}/{total} PASS")
