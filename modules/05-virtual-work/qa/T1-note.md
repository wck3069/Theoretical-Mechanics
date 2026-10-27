# M5-T1 验证记录 — modules/05-virtual-work/note.tex

日期：2026-10-27

## 构建与 §7.1 验收

命令：`bash tools/build_note.sh modules/05-virtual-work`
退出码：0

PDF 信息：
- 页数：7（≥6 ✓）
- 未解析引用 `??`：0 ✓
- TODO/TBD/待补：0 ✓
- 编号公式：10 (≥8) ✓
- 参考文献 bibitem：3（≥2 ✓）

## 数值验证

命令：`~/.venv-tm/bin/python modules/05-virtual-work/qa/numeric_check.py`
结果：
- theta_min (mu=0.25): 63.4 deg ✓
- theta_min (mu=0.5): 45.0 deg ✓
- theta_min (mu=1.0): 26.6 deg ✓
- 力平衡验证：Nw = f_crit，diff < 1e-15 ✓
- 验收汇总：4/4 PASS ✓

## 作业映射

覆盖：作业-7 Q1-Q5（虚功原理与静力学）。
