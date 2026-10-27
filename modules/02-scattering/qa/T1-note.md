# M2-T1 验证记录 — modules/02-scattering/note.tex

日期：2026-10-27

## 构建与 §7.1 验收

命令：`bash tools/build_note.sh modules/02-scattering`
退出码：0

PDF 信息：
- 页数：6（≥6 ✓）
- 未解析引用 `??`：0 ✓
- TODO/TBD/待补：0 ✓
- 编号公式：21（≥8 ✓）
- 参考文献 bibitem：3（≥2 ✓）
- 章节：摘要、作业映射、模型与假设、推导、解析结果、数值验证、讨论、参考文献 ✓
- 数值验证表：解析值/数值值/相对误差三列 ✓

## 数值验证

命令：`~/.venv-tm/bin/python modules/02-scattering/qa/numeric_check.py`
结果：
- Theta (k/r^2, b=1): formula=0.920151, numerical=0.920151, err=2.22e-16 ✓
- dSigma/dOmega (theta=pi/2): 0.282942 = 8/(9*pi) ✓
- b_c (capture): 1.414214 = 4^(1/4) ✓
- sigma_capture: 6.283185 = 2*pi ✓
- 验收汇总：4/4 PASS ✓

## 作业映射

覆盖：作业-3 Q2（散射）、作业-3 Q3（俘获）。
