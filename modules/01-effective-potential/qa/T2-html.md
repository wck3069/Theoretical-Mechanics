# M1-T2 验证证据 — modules/01-effective-potential/index.html

日期：2026-10-27 · 验证人：主代理（google-chrome headless）+ 免费模型独立复核（Sisyphus-Junior/quick，`task_id: bg_d74310a1`）

## 交付物概要

- 单文件、零外链、内联 JS（esprima 4.0.1 / ES2017 语法），约 700 行。
- 4 种势：`kepler`（作业-2）、`harm`（作业-3）、`gauss`（作业-5）、`pow`（Bertrand 一般幂律）。
- 左面板轨道视图（轨迹拖尾、中心力心、可拖拽设初态）+ 右面板 V_eff(r)（禁戒区底纹、E 水平线、平衡点/转折点标记、当前 r 游标）+ HUD（t、r、θ、E、ω_r、ω_θ、能量漂移、轨道状态）。
- 滑杆：L、E、r0、k、γ(γ/r³ 进动项)、速度；预设 6 个；URL 参数读写（`?pot=L=&E=&r0=&k=&gam=&speed=&selftest=1`）。
- 主循环：RK4，`V = V_base + gam/r³`，`V_eff = V + L²/2r²`，逃逸/奇异守卫。

## 静态检查（check_html.py）

命令：`~/.venv-tm/bin/python tools/check_html.py modules/01-effective-potential/index.html`

```
[PASS] 1. 内联 JS 语法（1 个 <script> 块，esprima (4, 0, 1)）
[PASS] 2a. 无 http 或 https 外链（全文未出现）
[PASS] 2b. 无协议相对地址（属性、CSS、字符串均未出现）
[PASS] 2c. 资源引用均为本地相对路径（无外部资源标签）
[PASS] 2d. 无网络请求或外部模块加载（未出现）
[PASS] 2e. 无 CDN 域名引用（未出现）
-- 摘要：6/6 项通过，0 项失败
EXIT_CODE=0
```

主代理与免费模型两次独立运行输出一致。

## 运行时自测（chrome headless, ?selftest=1）

命令：

```
google-chrome --headless=new --no-sandbox --disable-gpu --virtual-time-budget=5000 \
  --dump-dom 'file:///.../index.html?selftest=1'
```

提取 `div#selftestPanel`（同时 `window.__selftest = {passed, failed, details}`）：

```
SELFTEST 5/5 PASS
[PASS] ST1 kepler turning points : roots=[1.0520303695138074, 2.2813029638195257] err=4.4e-16
[PASS] ST2 RK4 drift+period : drift=3.1e-14 Tr=13.52000 Ta=13.51926 rel=5.5e-5
[PASS] ST3 Bertrand ratio (k=2:2, kepler:1) : ratio_harm=2.0000 ratio_kep=1.0000
[PASS] ST4 gauss Lmax=1.0405 : L=0.99: eq=2 stable=1; L=1.05: eq=0
[PASS] ST5 gamma/r3 precession = 6*pi*gam/L^4 : shift=0.0534 theo=0.0545
```

断言含义：
- ST1：E=-0.3, L=1.2 开普勒转折点 vs 解析 a(1∓e)，误差 4.4e-16（判据 <1e-6）。
- ST2：RK4 dt=0.002 积分 48 时间单位，相对能量漂移 3.1e-14（判据 <1e-8）；径向周期 vs T=2πa^{3/2} 相对误差 5.5e-5（判据 <1e-3）。
- ST3：ω_θ/ω_r 频率比：谐振子=2.0000、开普勒=1.0000（判据 ±0.02，Bertrand 定理）。
- ST4：高斯势 Lmax=2√2/e≈1.0405：L=0.99 时平衡点恰 2 个（1 稳定），L=1.05 时 0 个（作业-5）。
- ST5：γ/r³ 进动 ω 频率法测得拱点偏移 0.0534 vs 解析 6πγ/L⁴=0.0545（判据 <5%）。

## 修复记录

- 首版自测 3/5：ST2 积分时长 30 不足 3 个径向过零（Tr=NaN）→ 加长到 48；ST5 判据原为写死阈值 0.01–0.05 → 改为对比解析值 6πγ/L⁴（±5%）。修复后 5/5 PASS。
- 免费模型对修复前快照的独立验证与主代理结果逐位一致（3/5、同一数值），验证方法可信。
