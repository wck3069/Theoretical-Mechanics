# M6-T1 验证记录 — modules/06-collisions/note.tex

日期：2026-10-27

## 构建与 §7.1 验收

命令：`bash tools/build_note.sh modules/06-collisions`
退出码：0

PDF 信息：
- 页数：6（≥6 ✓）
- 未解析引用 `??`：0 ✓
- TODO/TBD/待补：0 ✓
- 编号公式：12（≥8 ✓）
- 参考文献 bibitem：3（≥2 ✓）

## 数值验证

命令：`~/.venv-tm/bin/python modules/06-collisions/qa/numeric_check.py`
结果：
- beta_max (e=0.5): 36.9 deg (alpha_opt=26.6 deg) ✓
- raindrop: v(t) computed, asymptotic gt/4 ✓
- collision chain: H/h = 4.0 ✓
- 验收汇总：3/3 PASS ✓

## 作业映射

覆盖：作业-5 Q1（碰撞）、Q2（变质量雨滴）、Q3（碰撞链）。
