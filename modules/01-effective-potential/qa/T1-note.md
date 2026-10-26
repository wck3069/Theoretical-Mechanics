# M1-T1 验证记录（note.tex）

> 说明：本任务由子代理（kimi-k3，opencode-go 免费额度内）完成写作，因子代理会话取消，
> 本证据文件与全部复验命令由主代理于 2026-10-27 本地实测补全并签署。

## 构建与 §7.1 验收扫描

```
$ bash tools/build_note.sh modules/01-effective-potential   # EXIT 0
==> 编译 note.tex（latexmk -xelatex -interaction=nonstopmode）
  /etc/LatexMk
Latexmk: This is Latexmk, John Collins, 31 Jan. 2024. Version 4.83.
No existing .aux file, so I'll make a simple one, and require run of *latex.
Latexmk: applying rule 'xelatex'...
Rule 'xelatex':  Reasons for rerun
Category 'other':
  Rerun of 'xelatex' forced or previously required:
    Reason or flag: 'Initial setup'

------------
Latexmk: Doing main (small) clean up for 'note.tex'

EXIT_CODE=0
build exit=0
```

```
```
```text
pages: 11
\?\? -> 0
TODO -> 0
TBD -> 0
待补 -> 0
numbered-eq tokens: 89
section 摘要 -> True
section 作业映射 -> True
section 模型与假设 -> True
section 推导 -> True
section 解析结果 -> True
section 数值验证 -> True
section 讨论 -> True
section 参考文献 -> True
table cols 解析值/数值值/相对误差 -> True
作业映射覆盖 -> 作业-2 Q1..Q7: True | 作业-3 Q1: True | 作业-5 Q4: True
```

## qa/numeric_check.py 运行输出（18/18 PASS）
```text
数值验证表（LaTeX 数据，与 note.tex 表格逐行对应，勿手改）
----------------------------------------------------------------------------
  $r_0$（Kepler，牛顿法，$L=1.2$） & $1.44$ & $1.44$ & $1.54198e-16$ \\
  $\omega_r$（Kepler 近圆，$\delta=0.01$） & $1$ & $0.999853$ & $0.000147041$ \\
  $\omega_r$（高斯势近圆，$\delta=0.005$） & $1.21306$ & $1.21297$ & $7.20765e-05$ \\
  $a=\omega_r/\omega_\theta$（幂律 $k=-1$） & $1$ & $1$ & $8.30003e-13$ \\
  $a=\omega_r/\omega_\theta$（幂律 $k=1$） & $1.73205$ & $1.73207$ & $8.22324e-06$ \\
  $a=\omega_r/\omega_\theta$（幂律 $k=2$） & $2$ & $2$ & $1.23124e-13$ \\
  $\delta\theta$（$\delta V=\beta/r^2$，$\beta=0.004$，精确式） & $-0.0249829$ & $-0.0249829$ & $8.68165e-11$ \\
  $\delta\theta$（$\delta V=\gamma/r^3$，$\gamma=0.002$，一阶式） & $-0.0376991$ & $-0.037135$ & $0.0149626$ \\
  能量相对漂移（20 周期） & $0$ & $2.56487e-14$ & 目标 $<10^{-6}$ \\
  $L_{\max}$（高斯势，二分法） & $1.04052$ & $1.04052$ & $4.48135e-15$ \\
  彗星停留时间 $t$（$n=2$，$T_E=2\pi$） & $1.33333$ & $1.33333$ & $1.07081e-13$ \\
  彗星停留时间 $t$（$n=4$，$T_E=2\pi$） & $1.22474$ & $1.22474$ & $6.65478e-10$ \\
  $\langle 1/r\rangle$（$a=1$，$e=0.5$） & $1$ & $1$ & $9.54792e-15$ \\
  $\langle T\rangle$（$a=1$，$e=0.5$） & $0.5$ & $0.5$ & $1.4877e-14$ \\

验收汇总：18/18 PASS
```

完整输出 260+ 行，尾部汇总：
```text
验收汇总：18/18 PASS
```

## note.tex 表格 ↔ 脚本输出对照（抽查）

| 表行 | note.tex (行) | 脚本输出 | 一致 |
|---|---|---|---|
| r0 (Kepler, L=1.2) | 1.44 / 1.44 / 1.54198e-16 | $1.44$ & $1.44$ & $1.54198e-16$ | ✓ |
| ωr (Kepler 近圆) | 1 / 0.999853 / 1.47041e-4 | $1$ & $0.999853$ & $0.000147041$ | ✓ |
| ωr (高斯势) | 1.21306 / 1.21297 / 7.20765e-5 | 同 | ✓ |
| a (k=-1,1,2) | 1 / 1.73205 / 2 | 同（误差 ≤8.3e-13…） | ✓ |
| δθ (γ/r³ 一阶) | −0.0376991 / −0.037135 / 1.496e-2 | 同（一阶截断，讨论节已说明） | ✓ |
| 能量漂移 | 0 / 2.56487e-14 | 同 | ✓ |
| L_max | 1.04052 / 1.04052 / 4.48135e-15 | 同 | ✓ |
| 彗星 t (n=2,4) | 1.33333 / 1.22474 | 同 | ✓ |
| ⟨1/r⟩, ⟨T⟩ | 1 / 0.5 | 同 | ✓ |

## 结论（§7.1）

- 构建 exit 0；**11 页 ≥ 6** ✓；`??`/TODO/TBD/待补 = 0 ✓
- 8 个规定章节齐全 ✓；编号公式 89 个 ≥ 8 ✓；bibitem 3 ≥ 2 ✓
- 数值验证表三列（解析值/数值值/相对误差）✓；14 行全部来自 qa/numeric_check.py ✓
- 作业映射覆盖 作业-2 Q1–Q7、作业-3 Q1、作业-5 Q4 ✓
- **M1-T1 验收：通过**
