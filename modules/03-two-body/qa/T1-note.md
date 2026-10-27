# M3-T1 验证记录 — modules/03-two-body/note.tex

日期：2026-10-27

## 构建与 §7.1 验收

命令：`bash tools/build_note.sh modules/03-two-body`
退出码：0

PDF 信息：
- 页数：6（≥6 ✓）
- 未解析引用 `??`：0 ✓
- TODO/TBD/待补：0 ✓
- 编号公式：≥8 ✓
- 参考文献 bibitem：3（≥2 ✓）

## 数值验证

命令：`~/.venv-tm/bin/python modules/03-two-body/qa/numeric_check.py`
结果：
- r1 (Jupiter) = 7.417e8 m, r1/Rsun = 1.066 ✓
- v1 (Jupiter) = 12.45 m/s ✓
- delta_lambda (Jupiter) = 2.075e-5 nm ✓
- r1 (Earth) = 4.490e5 m, v1 = 0.0894 m/s ✓
- omega Kepler III 与 2pi/P 一致 ✓
- 验收汇总：6/6 PASS ✓

## 作业映射

覆盖：两体专题（作业-4 第 5 题）— 质心、约化质量、两体 Kepler、RV、多普勒、系外行星。
