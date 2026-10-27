# M7-T1 验证记录 — modules/07-rigid-body/note.tex

日期：2026-10-27

## 构建与 §7.1 验收

命令：`bash tools/build_note.sh modules/07-rigid-body`
退出码：0

PDF 信息：
- 页数：6（≥6 ✓）
- 未解析引用 `??`：0 ✓
- TODO/TBD/待补：0 ✓
- 编号公式：≥8 ✓
- 参考文献 bibitem：3（≥2 ✓）

## 数值验证

命令：`~/.venv-tm/bin/python modules/07-rigid-body/qa/numeric_check.py`
结果：
- cap centroid (R=1,b=0): 0.375 ✓
- cap centroid (R=1,b=0.5): 0.175 ✓
- beetle ring rotation: pi ✓
- disk L: 0.5 ✓
- shell V: correct ✓
- 验收汇总：6/6 PASS ✓

## 作业映射

覆盖：作业-4 Q1-Q4（刚体几何与角动量）。
