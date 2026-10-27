# M4-T1 验证记录 — modules/04-variational/note.tex

日期：2026-10-27

## 构建与 §7.1 验收

命令：`bash tools/build_note.sh modules/04-variational`
退出码：0

PDF 信息：
- 页数：6（≥6 ✓）
- 未解析引用 `??`：0 ✓
- TODO/TBD/待补：0 ✓
- 编号公式：15（≥8 ✓）
- 参考文献 bibitem：3（≥2 ✓）

## 数值验证

命令：`~/.venv-tm/bin/python modules/04-variational/qa/numeric_check.py`
结果：
- T (cycloid, a=1, g=1): 3.14159 = pi (independent of s0) ✓
- T0 (C=1/8): 3.14159 = pi ✓
- T0 (C=1/4): 2.22144 ✓
- T0 (C=1/2): 1.57080 ✓
- Snell: n1 sin theta1 = n2 sin theta2 ✓
- 验收汇总：4/4 PASS ✓

## 作业映射

覆盖：作业-6 Q1（折射定律）、Q2（最短路径）、Q3（等时摆）、Q3(d)（一般等时条件）。
