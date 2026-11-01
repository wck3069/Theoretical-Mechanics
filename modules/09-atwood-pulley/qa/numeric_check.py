# -*- coding: utf-8 -*-
"""M9 数值验证：有转动惯量的 Atwood 机（作业-8 Q1）"""
G = 9.81

def rk4_s(a, T, dt=1e-5):
    s = v = t = 0.0
    while t < T - 1e-12:
        h = min(dt, T - t)
        s += v * h + 0.5 * a * h * h
        v += a * h
        t += h
    return s

print("M9 数值验证（作业-8 Q1）")
print("-" * 72)
ok = 0
cases = [(1, 2, 0.5, 0.2), (0.5, 4, 1.2, 0.3), (2, 2, 1.0, 0.25)]
for m1, m2, I, R in cases:
    Meff = m1 + m2 + I / R**2
    a = (m2 - m1) * G / Meff
    T1 = m1 * (G + a)
    T2 = m2 * (G - a)
    s_exact = 0.5 * a * 0.4**2
    s_num = rk4_s(a, 0.4)
    err = abs(s_num - s_exact) / max(1e-12, abs(s_exact))
    dT = T2 - T1
    dT_expected = I * a / R**2
    good = err < 1e-9 and abs(dT - dT_expected) < 1e-9
    ok += good
    print(f"m1={m1:<4} m2={m2:<4} I={I:<4} R={R:<4} "
          f"Meff={Meff:8.3f} a={a:9.6f} T1={T1:9.6f} T2={T2:9.6f} "
          f"s_num={s_num:.8f} err={err:.1e} {'PASS' if good else 'FAIL'}")
print("-" * 72)
print(f"验收汇总：{ok}/{len(cases)} PASS")
