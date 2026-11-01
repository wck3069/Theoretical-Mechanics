# -*- coding: utf-8 -*-
"""M11 数值验证：旋转圆环 + 磁场（作业-8 Q5/Q6）"""
import math
G = 9.81
print("M11 数值验证（作业-8 Q5 圆环 / Q6 磁场）")
print("-" * 72)
ok = total = 0

def check(name, got, want, tol=1e-6):
    global ok, total
    total += 1
    good = abs(got - want) <= tol
    ok += good
    print(f"{name:46s} {got:14.6f}  expect {want:14.6f}  {'PASS' if good else 'FAIL'}")

# Q5
R = 1.2
check("Q5 Omega_c", math.sqrt(G / R), 2.85920, 1e-4)
Om = 3.0
th_eq = math.acos(G / (Om * Om * R))
check("Q5 theta_eq (deg)", math.degrees(th_eq), 24.72, 2e-2)
V0 = (G / R - Om * Om) * R * R
total += 1
good = V0 < 0
ok += good
print(f"{'Q5 theta=0 不稳定 (Veff''<0)':46s} {V0:14.4f}  {'PASS' if good else 'FAIL'}")
Veq = R * R * Om * Om * math.sin(th_eq) ** 2
total += 1
good = Veq > 0
ok += good
print(f"{'Q5 theta_eq 稳定 (Veff''>0)':46s} {Veq:14.4f}  {'PASS' if good else 'FAIL'}")

# Q5 Jacobi integral via RK4
th, om, h, Emin, Emax = 0.3, 0.0, 1e-4, 1e9, -1e9
for _ in range(20000):
    d1th, d1om = om, (Om * Om * math.cos(th) - G / R) * math.sin(th)
    d2th, d2om = om + d1om * h / 2, (Om * Om * math.cos(th + d1th * h / 2) - G / R) * math.sin(th + d1th * h / 2)
    d3th, d3om = om + d2om * h / 2, (Om * Om * math.cos(th + d2th * h / 2) - G / R) * math.sin(th + d2th * h / 2)
    d4th, d4om = om + d3om * h, (Om * Om * math.cos(th + d3th * h) - G / R) * math.sin(th + d3th * h)
    th += (d1th + 2 * d2th + 2 * d3th + d4th) * h / 6
    om += (d1om + 2 * d2om + 2 * d3om + d4om) * h / 6
    E = 0.5 * R * R * om * om - 0.5 * R * R * Om * Om * math.sin(th) ** 2 - G * R * math.cos(th)
    Emin, Emax = min(Emin, E), max(Emax, E)
check("Q5 dE (2 s RK4)", Emax - Emin, 0.0, 1e-6)

# Q6
B, v0, q, m = 1.2, 1.0, 1.0, 1.0
w = q * B / m
check("Q6 r_c", v0 / abs(w), 0.833333, 1e-6)
Qx0 = Qy0 = None
pxs = []
for i in range(201):
    t = 2 * math.pi / abs(w) * i / 200
    x, y = (v0 / w) * math.sin(w * t), (v0 / w) * (math.cos(w * t) - 1)
    vx, vy = v0 * math.cos(w * t), -v0 * math.sin(w * t)
    Qx, Qy = m * vx - q * B * y, m * vy + q * B * x
    pxs.append(m * vx - 0.5 * q * B * y)
    Qx0 = Qx if Qx0 is None else Qx0
    Qy0 = Qy if Qy0 is None else Qy0
    assert abs(Qx - Qx0) < 1e-12 and abs(Qy - Qy0) < 1e-12
total += 2; ok += 2
print(f"{'Q6 Qx,Qy 守恒 (一个周期)':46s} {'max|dQ|=0':>14s}  PASS")
check("Q6 Qx", Qx0, 1.0, 1e-12)
check("Q6 Qy", Qy0, 0.0, 1e-12)
check("Q6 Delta p_x", max(pxs) - min(pxs), 1.0, 1e-4)

print("-" * 72)
print(f"验收汇总：{ok}/{total} PASS")
