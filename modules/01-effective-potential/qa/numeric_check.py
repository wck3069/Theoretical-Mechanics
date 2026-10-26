#!/home/wck/.venv-tm/bin/python
# -*- coding: utf-8 -*-
"""numeric_check.py —— M1《有效势与轨道稳定性》讲义数值验证脚本

对应 PLAN.md §5.3（物理与数值规范）与 §7.1（讲义验收）。
讲义 note.tex“数值验证”一节表格中的每一个数字都来自本脚本的实际输出，
脚本输出同时粘贴于 qa/T1-note.md。

单位制（与讲义“模型与假设”一致）：
  - 质量 m = 1（无量纲化约定，讲义 §模型与假设）；
  - Kepler 势   V = -alpha/r，取 alpha = 1；
  - 幂律势      V = beta * r**k；
  - 高斯势      V = -V0 * exp(-lam**2 * r**2)，取 V0 = lam = 1；
  - 微扰        dV = beta/r**2 或 gamma/r**3（作业-2 Q7 记号）。

数值方法（仅用 Python 标准库 + numpy，不依赖 scipy）：
  - 四阶 Runge--Kutta（定步长，步长按周期归一化，§5.3）；
  - 二分法（bisection）与牛顿法（Newton）求根；
  - 三点抛物线顶点细化用于周期/拱点定位。

运行：/home/wck/.venv-tm/bin/python modules/01-effective-potential/qa/numeric_check.py
"""
from __future__ import annotations

import sys
from math import sqrt, exp, pi, floor, log10

import numpy as np

TWO_PI = 2.0 * pi
RESULTS = []          # (标签, 解析值, 数值值, 相对误差) —— 末尾打印 LaTeX 表格
PASSFAIL = []         # (验收项, 目标, 实际, 是否通过)


# ----------------------------------------------------------------------
# 通用数值工具
# ----------------------------------------------------------------------
def rk4(f, t0, y0, h, n):
    """定步长四阶 Runge--Kutta：f(t, y) -> y'（list），返回 (ts, ys)。"""
    d = len(y0)
    ts = [float(t0)]
    ys = [tuple(float(v) for v in y0)]
    t = float(t0)
    y = [float(v) for v in y0]
    for _ in range(n):
        k1 = f(t, y)
        y2 = [y[i] + 0.5 * h * k1[i] for i in range(d)]
        k2 = f(t + 0.5 * h, y2)
        y3 = [y[i] + 0.5 * h * k2[i] for i in range(d)]
        k3 = f(t + 0.5 * h, y3)
        y4 = [y[i] + h * k3[i] for i in range(d)]
        k4 = f(t + h, y4)
        y = [y[i] + (h / 6.0) * (k1[i] + 2.0 * k2[i] + 2.0 * k3[i] + k4[i])
              for i in range(d)]
        t += h
        ts.append(t)
        ys.append(tuple(y))
    return ts, ys


def bisect(f, a, b, tol=1e-13, maxiter=200):
    """二分法求根：要求 f(a)*f(b) < 0，否则抛 ValueError。"""
    fa, fb = f(a), f(b)
    if fa == 0.0:
        return a
    if fb == 0.0:
        return b
    if fa * fb > 0.0:
        raise ValueError("bisect: 端点同号 f(%g)=%g, f(%g)=%g" % (a, fa, b, fb))
    for _ in range(maxiter):
        m = 0.5 * (a + b)
        fm = f(m)
        if fm == 0.0 or (b - a) < tol:
            return m
        if fa * fm < 0.0:
            b, fb = m, fm
        else:
            a, fa = m, fm
    return 0.5 * (a + b)


def newton(f, df, x0, tol=1e-14, maxiter=100):
    """牛顿法求根，返回 (根, 迭代次数)。"""
    x = float(x0)
    for i in range(1, maxiter + 1):
        fx = f(x)
        if abs(fx) < tol:
            return x, i - 1
        x -= fx / df(x)
    return x, maxiter


def vertex_t(i, h):
    """等步长三点 (i-1, i, i+1) 抛物线顶点（极大值时刻）。

    t* = t_i + h*(y_{i-1} - y_{i+1}) / (2*(y_{i-1} - 2 y_i + y_{i+1}))
    调用方保证三点括住极大值（v 从 + 变 -）。
    """
    return lambda ys: h * (ys[i - 1] - ys[i + 1]) / (2.0 * (ys[i - 1] - 2.0 * ys[i] + ys[i + 1]))


def relerr(num, ana):
    return abs(num - ana) / abs(ana)


def fmt(x, sig=6):
    """表格就绪字符串：6 位有效数字（%g 自动切换科学计数法）。"""
    return "%.6g" % x


def add_row(label, ana, num, re):
    RESULTS.append((label, ana, num, re))


def check(name, target, actual, ok):
    PASSFAIL.append((name, target, actual, ok))
    print("  [验收] %-42s 目标 %-14s 实际 %-14s %s"
          % (name, target, actual, "PASS" if ok else "FAIL"))


# ----------------------------------------------------------------------
# 物理模型（m = 1）
# ----------------------------------------------------------------------
def radial_system(L, dVdr):
    """约化径向系统 y = (r, v_r, theta)：

    r'' = L^2/r^3 - V'(r)   （m=1，角动量守恒代入横向运动）
    theta' = L / r^2        （角动量守恒：L = m r^2 theta'）
    """
    def f(t, y):
        r, vr, _th = y
        return [vr, L * L / (r * r * r) - dVdr(r), L / (r * r)]
    return f


def find_maxima(ts, ys, ivmax=1):
    """返回 (极大值时刻列表, 对应索引列表)。

    ivmax = 1：用 y[1]（v_r）从 + 变 - 检测 y[0]（r）的极大；
    起点若 v_r(0)=0 且 r 递减（远拱点），t=0 本身是精确极大，一并收录。
    抛物线顶点细化：三点 (i-1, i, i+1)。
    """
    n = len(ts)
    tmax = []
    idx = []
    v0 = ys[0][ivmax]
    if v0 == 0.0:                      # 起点即极值（精确）
        tmax.append(0.0)
        idx.append(0)
    for i in range(1, n - 1):
        if ys[i][ivmax] > 0.0 and ys[i + 1][ivmax] <= 0.0:
            rs = [ys[j][0] for j in (i - 1, i, i + 1)]
            dt = vertex_t(1, ts[i + 1] - ts[i])(rs)   # 相对 t_i 的偏移
            tmax.append(ts[i] + dt)
            idx.append(i)
    return tmax, idx


def theta_at(ts, ys, idx, tstar):
    """由索引 i（跨步点）与细化时刻 t* 线性插值 theta(t*)。"""
    out = []
    for i, t in zip(idx, tstar):
        if i == 0:
            out.append(ys[0][2])
        else:
            h = ts[i + 1] - ts[i]
            w = (t - ts[i]) / h
            out.append(ys[i][2] + w * (ys[i + 1][2] - ys[i][2]))
    return out


# ======================================================================
# (a) Kepler 圆轨道半径 r0：牛顿法解 V_eff'(r0) = 0
# ======================================================================
def check_a():
    print("=" * 76)
    print("(a) Kepler 圆轨道：牛顿法解 V_eff'(r0)=0   [m=1, alpha=1, L=1.2]")
    print("-" * 76)
    alpha, L = 1.0, 1.2

    def dVeff(r):                      # V_eff' = alpha/r^2 - L^2/r^3
        return alpha / r**2 - L * L / r**3

    def ddVeff(r):                     # V_eff'' = -2 alpha/r^3 + 3 L^2/r^4
        return -2.0 * alpha / r**3 + 3.0 * L * L / r**4

    r0, it = newton(dVeff, ddVeff, 0.8)
    r0_ana = L * L / alpha
    res = abs(dVeff(r0))
    print("  牛顿迭代次数          : %d（初值 r=0.8）" % it)
    print("  r0 数值               : %.15g" % r0)
    print("  r0 解析 = L^2/alpha   : %.15g" % r0_ana)
    print("  |r0-r0_ana|/r0_ana    : %.3e" % relerr(r0, r0_ana))
    print("  残差 |V_eff'(r0)|     : %.3e" % res)
    check("(a) 残差 |V_eff'(r0)|", "< 1e-9", "%.3e" % res, res < 1e-9)
    add_row("$r_0$（Kepler，牛顿法，$L=1.2$）", r0_ana, r0, relerr(r0, r0_ana))
    return r0, res


# ======================================================================
# (b) 近圆轨道径向小振动频率 omega_r：RK4 测径向周期
# ======================================================================
def check_b():
    print("=" * 76)
    print("(b) 近圆轨道径向小振动频率 omega_r = 2pi/T_r（RK4，抛物线顶点测周期）")
    print("-" * 76)
    # ---- Kepler：r0=1, L=1, 扰动 delta=0.01 ----
    alpha, L, r0, delta = 1.0, 1.0, 1.0, 0.01
    dVdr = lambda r: alpha / r**2                      # V = -alpha/r
    f = radial_system(L, dVdr)
    T_guess = TWO_PI / sqrt(3 * L * L / r0**4 - 2 * alpha / r0**3)
    h = T_guess / 4000.0
    nsteps = int(20 * T_guess / h)                     # 约 20 个径向周期
    ts, ys = rk4(f, 0.0, [r0 + delta, 0.0, 0.0], h, nsteps)
    tmax, _ = find_maxima(ts, ys)
    per = [tmax[i + 1] - tmax[i] for i in range(len(tmax) - 1)]
    T_r = sum(per) / len(per)
    wr_num = TWO_PI / T_r
    wr_ana = sqrt(3 * L * L / r0**4 - 2 * alpha / r0**3)   # = sqrt(V_eff''(r0))
    e = relerr(wr_num, wr_ana)
    print("  [Kepler] r0=1, L=1, delta=0.01, 步长 h=%.3e, 极大点 %d 个"
          % (h, len(tmax)))
    print("    T_r 数值            : %.10g" % T_r)
    print("    omega_r 数值        : %.10g" % wr_num)
    print("    omega_r 解析=sqrt(V_eff''(r0)) : %.10g" % wr_ana)
    print("    相对误差           : %.3e" % e)
    check("(b) omega_r 相对误差（Kepler）", "< 1%", "%.3e" % e, e < 1e-2)
    add_row("$\\omega_r$（Kepler 近圆，$\\delta=0.01$）", wr_ana, wr_num, e)

    # ---- 高斯势：V=-V0 e^{-lam^2 r^2}, V0=lam=1, r0=1 ----
    V0, lam, r0g, delta = 1.0, 1.0, 1.0, 0.005
    Lg = sqrt(2.0 * V0 * lam**2 * r0g**4 * exp(-lam**2 * r0g**2))  # 圆轨道条件
    dVdr_g = lambda r: 2.0 * V0 * lam**2 * r * exp(-lam**2 * r * r)
    fg = radial_system(Lg, dVdr_g)
    # 圆轨道上 V_eff'' = 4 V0 lam^2 e^{-lam^2 r0^2} (2 - lam^2 r0^2)
    d2 = 4.0 * V0 * lam**2 * exp(-lam**2 * r0g**2) * (2.0 - lam**2 * r0g**2)
    wr_ana_g = sqrt(d2)
    T_guess = TWO_PI / wr_ana_g
    h = T_guess / 4000.0
    nsteps = int(20 * T_guess / h)
    ts, ys = rk4(fg, 0.0, [r0g + delta, 0.0, 0.0], h, nsteps)
    tmax, _ = find_maxima(ts, ys)
    per = [tmax[i + 1] - tmax[i] for i in range(len(tmax) - 1)]
    T_r = sum(per) / len(per)
    wr_num_g = TWO_PI / T_r
    e = relerr(wr_num_g, wr_ana_g)
    print("  [高斯势] V0=lam=1, r0=1, L=sqrt(2/e)=%.10g, delta=0.005" % Lg)
    print("    T_r 数值            : %.10g" % T_r)
    print("    omega_r 数值        : %.10g" % wr_num_g)
    print("    omega_r 解析        : %.10g  (=2/sqrt(e))" % wr_ana_g)
    print("    相对误差           : %.3e" % e)
    check("(b) omega_r 相对误差（高斯势）", "< 1%", "%.3e" % e, e < 1e-2)
    add_row("$\\omega_r$（高斯势近圆，$\\delta=0.005$）", wr_ana_g, wr_num_g, e)


# ======================================================================
# (c) 幂律势 V = beta r^k：频率比 a = omega_r/omega_theta = sqrt(k+2)
# ======================================================================
def check_c():
    print("=" * 76)
    print("(c) 幂律势 V=beta r^k 的频率比 a=omega_r/omega_theta（全轨道积分）")
    print("-" * 76)
    print("  参数：m=1, L=1, r0=1, beta=1/k（此时圆轨道恰在 r0=1, omega_theta=1）")
    for k in (-1.0, 1.0, 2.0):
        beta = 1.0 / k
        dVdr = lambda r, k=k, beta=beta: k * beta * r**(k - 1.0)   # = r^(k-1)
        f = radial_system(1.0, dVdr)
        wr_ana = sqrt(k + 2.0)
        T_guess = TWO_PI / wr_ana
        h = T_guess / 4000.0
        nsteps = int(10 * T_guess / h)                 # 约 10 个径向周期
        ts, ys = rk4(f, 0.0, [1.01, 0.0, 0.0], h, nsteps)
        tmax, idx = find_maxima(ts, ys)
        thmax = theta_at(ts, ys, idx, tmax)
        dth = [thmax[i + 1] - thmax[i] for i in range(len(thmax) - 1)]
        dth_mean = sum(dth) / len(dth)
        per = [tmax[i + 1] - tmax[i] for i in range(len(tmax) - 1)]
        T_r = sum(per) / len(per)
        a_num = TWO_PI / dth_mean                      # = omega_r/omega_theta
        a_ana = sqrt(k + 2.0)
        e = relerr(a_num, a_ana)
        print("  [k=%+g] beta=%g: T_r=%.10g, 相邻远拱点 Dtheta=%.10g"
              % (k, beta, T_r, dth_mean))
        print("    a 数值 = 2pi/Dtheta : %.10g" % a_num)
        print("    a 解析 = sqrt(k+2)  : %.10g" % a_ana)
        print("    相对误差           : %.3e" % e)
        check("(c) a=sqrt(k+2) 相对误差（k=%g）" % k, "< 1%", "%.3e" % e, e < 1e-2)
        add_row("$a=\\omega_r/\\omega_\\theta$（幂律 $k=%g$）" % k, a_ana, a_num, e)


# ======================================================================
# (d) 比奈方程进动：dV = beta/r^2（精确）与 dV = gamma/r^3（一阶）
# ======================================================================
def check_d():
    print("=" * 76)
    print("(d) 比奈方程微扰进动（m=alpha=L=p=1, e=0.3, u(0)=1.3, u'(0)=0）")
    print("-" * 76)
    h = TWO_PI / 5000.0

    def binet_precession(rhs, norb=12):
        """积分 u''=rhs(u)，返回相邻近心点（u 极大）间距的均值。"""
        def f(t, y):
            return [y[1], rhs(y[0])]
        nsteps = int(norb * TWO_PI / h)
        ts, ys = rk4(f, 0.0, [1.3, 0.0], h, nsteps)
        tmax, _ = find_maxima(ts, ys, ivmax=1)         # y=(u, u')：u' 变号检测
        # find_maxima 用 y[1] 检测、对 y[0] 拟合顶点，正好对应 (u, u')
        dth = [tmax[i + 1] - tmax[i] for i in range(len(tmax) - 1)]
        return sum(dth) / len(dth), len(tmax)

    # ---- (d1) dV = beta/r^2：方程线性，进动公式精确 ----
    beta = 0.004
    kappa = sqrt(1.0 + 2.0 * beta)                     # m=L=1
    dth_num, nmax = binet_precession(lambda u: 1.0 - (1.0 + 2.0 * beta) * u)
    dth_ana = TWO_PI / kappa                           # 精确拱点间距
    dpre_ana = dth_ana - TWO_PI                        # 每圈进动（精确）
    dpre_num = dth_num - TWO_PI
    e = relerr(dpre_num, dpre_ana)
    print("  [dV=beta/r^2] beta=0.004, kappa=sqrt(1+2beta)=%.10g" % kappa)
    print("    近心点间距 数值     : %.10g（近心点 %d 个）" % (dth_num, nmax))
    print("    每圈进动 数值      : %.10g" % dpre_num)
    print("    每圈进动 解析(精确): 2pi(1/kappa-1) = %.10g" % dpre_ana)
    print("    相对误差           : %.3e" % e)
    check("(d) beta/r^2 进动（对精确公式）", "< 1e-3", "%.3e" % e, e < 1e-3)
    add_row("$\\delta\\theta$（$\\delta V=\\beta/r^2$，$\\beta=0.004$，精确式）",
            dpre_ana, dpre_num, e)

    # ---- (d2) dV = gamma/r^3：一阶摄动公式 delta_theta = -6 pi m gamma/(L^2 p) ----
    devs = {}
    for gamma in (0.002, 0.001):
        dth_num, nmax = binet_precession(lambda u, g=gamma: 1.0 - u - 3.0 * g * u * u)
        dpre_num = dth_num - TWO_PI
        dpre_ana = -6.0 * pi * gamma                    # m=alpha=L=p=1 的一阶式
        e = relerr(dpre_num, dpre_ana)
        devs[gamma] = e
        print("  [dV=gamma/r^3] gamma=%g" % gamma)
        print("    近心点间距 数值     : %.10g（近心点 %d 个）" % (dth_num, nmax))
        print("    每圈进动 数值      : %.10g" % dpre_num)
        print("    每圈进动 一阶公式  : -6 pi gamma = %.10g" % dpre_ana)
        print("    相对偏差           : %.3e（O(gamma) 二阶修正，非数值误差）" % e)
        if gamma == 0.002:
            check("(d) gamma/r^3 进动（对一阶公式）", "< 2%", "%.3e" % e, e < 2e-2)
            add_row("$\\delta\\theta$（$\\delta V=\\gamma/r^3$，$\\gamma=0.002$，一阶式）",
                    dpre_ana, dpre_num, e)
    ratio = devs[0.002] / devs[0.001]
    print("  [阶次检验] gamma 减半（0.002->0.001），相对偏差之比 = %.3f"
          "（一阶摄动应接近 2）" % ratio)
    check("(d) 偏差随 gamma 线性（比值）", "1.5 ~ 2.5", "%.3f" % ratio,
          1.5 < ratio < 2.5)


# ======================================================================
# (e) RK4 能量漂移（20 个周期）+ 高斯势最大角动量 L_max（二分法）
# ======================================================================
def check_e():
    print("=" * 76)
    print("(e-1) 直角坐标全系统 RK4 能量/角动量漂移（Kepler，20 个周期）")
    print("-" * 76)
    L, x0 = 1.0, 1.01                                  # 近圆轨道 delta=0.01
    y0 = [x0, 0.0, 0.0, L / x0]                        # (x, y, vx, vy)

    def f(t, y):
        x, yv, vx, vy = y
        r2 = x * x + yv * yv
        r3 = r2 * sqrt(r2)
        return [vx, vy, -x / r3, -yv / r3]

    def energy(y):
        return 0.5 * (y[2]**2 + y[3]**2) - 1.0 / sqrt(y[0]**2 + y[1]**2)

    def angmom(y):
        return y[0] * y[3] - y[1] * y[2]

    E0, L0 = energy(y0), angmom(y0)
    h = TWO_PI / 5000.0
    nsteps = int(20 * TWO_PI / h)
    ts, ys = rk4(f, 0.0, y0, h, nsteps)
    dE = max(abs(energy(y) - E0) for y in ys) / abs(E0)
    dL = max(abs(angmom(y) - L0) for y in ys) / abs(L0)
    print("  初值 (x,y,vx,vy)=(%.4g,0,0,%.6g), E0=%.10g, L0=%.10g"
          % (x0, L / x0, E0, L0))
    print("  步长 h=%.3e, 步数 %d（t in [0, 40 pi]）" % (h, nsteps))
    print("  能量相对漂移 max|dE/E0|   : %.3e" % dE)
    print("  角动量相对漂移 max|dL/L0| : %.3e" % dL)
    check("(e) 能量相对漂移（20 周期）", "< 1e-6", "%.3e" % dE, dE < 1e-6)
    add_row("能量相对漂移（20 周期）", 0.0, dE, None)

    print("-" * 76)
    print("(e-2) 高斯势 V=-V0 e^{-lam^2 r^2}（V0=lam=1）：最大角动量 L_max（二分法）")
    V0, lam = 1.0, 1.0

    def dVeff(r, L):                    # V_eff' = 2 V0 lam^2 r e^{-lam^2 r^2} - L^2/r^3
        return 2.0 * V0 * lam**2 * r * exp(-lam**2 * r * r) - L * L / r**3

    def d2Veff(r, L):                   # V_eff'' = 2 V0 lam^2 e^{-..}(1-2 lam^2 r^2)+3L^2/r^4
        return (2.0 * V0 * lam**2 * exp(-lam**2 * r * r) * (1.0 - 2.0 * lam**2 * r * r)
                + 3.0 * L * L / r**4)

    def stable_root(L):
        """稳定支圆轨道半径 r0(L)：二分 (0.05, sqrt(2)/lam)；无根则 None。"""
        try:
            return bisect(lambda r: dVeff(r, L), 0.05, sqrt(2.0) / lam,
                          tol=1e-14, maxiter=300)
        except ValueError:
            return None

    def marginal(L):
        """V_eff''(r0(L))：稳定为正；无圆轨道（L 过大）返回 -1。"""
        r0 = stable_root(L)
        return -1.0 if r0 is None else d2Veff(r0, L)

    lo, hi = 0.5, 1.5                   # marginal(lo)>0, marginal(hi)=-1
    for _ in range(120):
        mid = 0.5 * (lo + hi)
        if marginal(mid) > 0.0:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-13:
            break
    Lmax_num = 0.5 * (lo + hi)
    Lmax_ana = 2.0 * sqrt(2.0 * V0) / (lam * exp(1.0))   # = 2 sqrt(2 V0)/(lam e)
    e = relerr(Lmax_num, Lmax_ana)
    # 临界半径 r*：沿圆轨道族 L=L(r)（圆轨道条件），对 V_eff''(r, L(r)) 二分求零点。
    # （不用 stable_root(Lmax_num)：L 恰在临界值处是双重根，数值上不可分辨；
    #   直接对 r 二分边际条件 V_eff''=0 是单根，可达机器精度。）
    def d2_on_family(r):
        Lr = sqrt(2.0 * V0 * lam**2 * r**4 * exp(-lam**2 * r * r))
        return d2Veff(r, Lr)
    rstar = bisect(d2_on_family, 1.0, 1.5, tol=1e-13, maxiter=300)
    print("  外层二分 L in [0.5,1.5]，内层二分 r in [0.05, sqrt(2)]")
    print("  L_max 数值           : %.12g" % Lmax_num)
    print("  L_max 解析 = 2 sqrt(2 V0)/(lam e) : %.12g" % Lmax_ana)
    print("  临界半径 r* 数值     : %.12g（解析 sqrt(2)/lam = %.12g）"
          % (rstar, sqrt(2.0) / lam))
    print("  相对误差             : %.3e" % e)
    check("(e) L_max 相对误差（二分法）", "< 1e-6", "%.3e" % e, e < 1e-6)
    add_row("$L_{\\max}$（高斯势，二分法）", Lmax_ana, Lmax_num, e)

    # 稳定窗口两侧验证（§6 必做验收 5：稳定/不稳定判定与 V_eff'' 符号一致）
    for fac in (0.999, 1.001):
        Lt = fac * Lmax_ana
        r0 = stable_root(Lt)
        if r0 is None:
            print("  L=%.6g*L_max：无圆轨道（V_eff' 在稳定窗口内无零点）" % fac)
            check("(e) L=%.3f L_max 无圆轨道" % fac, "无根", "无根", True)
        else:
            s = d2Veff(r0, Lt)
            print("  L=%.6g*L_max：r0=%.8g, V_eff''(r0)=%+.6g -> %s"
                  % (fac, r0, s, "稳定" if s > 0 else "不稳定"))
            check("(e) L=%.3f L_max 稳定支 V_eff''>0" % fac, "V_eff''>0", "%+.3g" % s,
                  s > 0)


# ======================================================================
# (f) 抛物线彗星在地球轨道内的停留时间（作业-2 Q5）
# ======================================================================
def check_f():
    print("=" * 76)
    print("(f) 抛物线彗星停留时间（mu=R=1，近日点 q=R/n，从近日点积分到 r=R）")
    print("-" * 76)
    mu, R = 1.0, 1.0
    TE = TWO_PI * sqrt(R**3 / mu)                     # 地球公转周期（圆轨道）
    for n in (2.0, 4.0):
        q = R / n
        L = sqrt(2.0 * mu * q)                          # 抛物线（E=0）角动量
        f = radial_system(L, lambda r: mu / r**2)

        # 事件积分：从近日点出发，直到 r >= R（线性插值定位穿越时刻）
        h = 1.0e-4
        t, y = 0.0, [q, 0.0, 0.0]
        tprev, rprev = 0.0, q
        while True:
            k1 = f(t, y)
            k2 = f(t + 0.5 * h, [y[i] + 0.5 * h * k1[i] for i in range(3)])
            k3 = f(t + 0.5 * h, [y[i] + 0.5 * h * k2[i] for i in range(3)])
            k4 = f(t + h, [y[i] + h * k3[i] for i in range(3)])
            y = [y[i] + (h / 6.0) * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i])
                  for i in range(3)]
            t += h
            if y[0] >= R:
                t_out = tprev + (R - rprev) / (y[0] - rprev) * h
                break
            tprev, rprev = t, y[0]
        t_num = 2.0 * t_out                             # 对称性：总停留 = 2 t_out

        # 解析式 1（径向积分闭式）与解析式 2（作业题公式）
        t_ana1 = (1.0 / sqrt(2.0 * mu)) * ((4.0 / 3.0) * (R - q)**1.5
                                          + 4.0 * q * sqrt(R - q))
        t_ana2 = TE * (2.0 * (n + 2.0) / (3.0 * pi * n)) * sqrt((n - 1.0) / (2.0 * n))
        e = relerr(t_num, t_ana2)
        print("  [n=%g] q=%.6g, L=sqrt(2 q)=%.6g, h=1e-4" % (n, q, L))
        print("    停留时间 数值          : %.10g" % t_num)
        print("    解析式1（径向积分）    : %.10g" % t_ana1)
        print("    解析式2（作业公式）    : %.10g  (= T_E*(2(n+2)/(3 pi n))*sqrt((n-1)/(2n)))"
              % t_ana2)
        print("    相对误差（对解析式2） : %.3e" % e)
        check("(f) 停留时间相对误差（n=%g）" % n, "< 1e-4", "%.3e" % e, e < 1e-4)
        add_row("彗星停留时间 $t$（$n=%g$，$T_E=2\\pi$）" % n, t_ana2, t_num, e)
    print("  （n=2 时公式取最大值：t/T_E = 2/(3 pi) = %.10g）"
          % (2.0 / (3.0 * pi)))


# ======================================================================
# (g) 椭圆轨道时间平均与位力定理（作业-5 Q4）
# ======================================================================
def check_g():
    print("=" * 76)
    print("(g) Kepler 椭圆时间平均（alpha=1, a=1, e=0.5, T=2 pi）")
    print("-" * 76)
    a, e = 1.0, 0.5
    L = sqrt(1.0 * a * (1.0 - e * e))                  # L = sqrt(alpha a (1-e^2))
    rp = a * (1.0 - e)
    y0 = [rp, 0.0, 0.0, L / rp]                        # 近日点直角坐标初值

    def f(t, y):
        x, yv, vx, vy = y
        r2 = x * x + yv * yv
        r3 = r2 * sqrt(r2)
        return [vx, vy, -x / r3, -yv / r3]

    T = TWO_PI * sqrt(a**3 / 1.0)                      # 开普勒第三定律
    h = T / 20000.0
    nsteps = int(T / h)
    ts, ys = rk4(f, 0.0, y0, h, nsteps)
    # 周期函数在全周期上梯形积分（Euler--Maclaurin：谱精度）
    s_inv_r = 0.0
    s_kin = 0.0
    for i in range(nsteps):
        r_i = sqrt(ys[i][0]**2 + ys[i][1]**2)
        r_j = sqrt(ys[i + 1][0]**2 + ys[i + 1][1]**2)
        k_i = 0.5 * (ys[i][2]**2 + ys[i][3]**2)
        k_j = 0.5 * (ys[i + 1][2]**2 + ys[i + 1][3]**2)
        s_inv_r += 0.5 * (1.0 / r_i + 1.0 / r_j) * h
        s_kin += 0.5 * (k_i + k_j) * h
    inv_r_num = s_inv_r / T
    kin_num = s_kin / T
    pot_num = -1.0 * inv_r_num                         # <V> = -alpha <1/r>
    vir = 2.0 * kin_num / abs(pot_num)                 # 位力比 2<T>/|<V>|
    e1 = relerr(inv_r_num, 1.0 / a)
    e2 = relerr(kin_num, 1.0 / (2.0 * a))
    e3 = abs(vir - 1.0)
    print("  初值 (x,y,vx,vy)=(%.6g,0,0,%.6g), L=%.6g, T=2 pi" % (rp, L / rp, L))
    print("  <1/r> 数值 : %.10g   解析 1/a = 1        相对误差 %.3e" % (inv_r_num, e1))
    print("  <T>  数值 : %.10g   解析 alpha/(2a)=0.5   相对误差 %.3e" % (kin_num, e2))
    print("  <V>  数值 : %.10g   解析 -alpha/a = -1" % pot_num)
    print("  位力比 2<T>/|<V>| : %.10g（位力定理要求 = 1，偏差 %.3e）" % (vir, e3))
    check("(g) <1/r>=1/a 相对误差", "< 1e-4", "%.3e" % e1, e1 < 1e-4)
    check("(g) <T>=alpha/(2a) 相对误差", "< 1e-4", "%.3e" % e2, e2 < 1e-4)
    check("(g) 位力比 2<T>/|<V>| 偏离 1", "< 1e-4", "%.3e" % e3, e3 < 1e-4)
    add_row("$\\langle 1/r\\rangle$（$a=1$，$e=0.5$）", 1.0 / a, inv_r_num, e1)
    add_row("$\\langle T\\rangle$（$a=1$，$e=0.5$）", 1.0 / (2.0 * a), kin_num, e2)


# ======================================================================
# 主程序
# ======================================================================
def main():
    print("M1 数值验证 numeric_check.py")
    print("Python %s / numpy %s" % (sys.version.split()[0], np.__version__))
    print("单位制：m=1（无量纲）；RK4 定步长；二分法/牛顿法求根")
    print()
    check_a()
    print()
    check_b()
    print()
    check_c()
    print()
    check_d()
    print()
    check_e()
    print()
    check_f()
    print()
    check_g()
    print()
    print("=" * 76)
    print("数值验证表（LaTeX 数据，与 note.tex 表格逐行对应，勿手改）")
    print("-" * 76)
    for label, ana, num, re in RESULTS:
        if re is None:                                  # 能量漂移行：解析值为 0
            print("  %s & $0$ & $%s$ & 目标 $<10^{-6}$ \\\\" % (label, fmt(num)))
        else:
            print("  %s & $%s$ & $%s$ & $%s$ \\\\"
                  % (label, fmt(ana), fmt(num), fmt(re)))
    print()
    npass = sum(1 for _, _, _, ok in PASSFAIL if ok)
    print("验收汇总：%d/%d PASS" % (npass, len(PASSFAIL)))
    for name, target, actual, ok in PASSFAIL:
        if not ok:
            print("  FAIL: %s（目标 %s，实际 %s）" % (name, target, actual))
    return 0 if npass == len(PASSFAIL) else 1


if __name__ == "__main__":
    sys.exit(main())
