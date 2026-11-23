# KB 恢复与新编号对齐（2026-11-23）

## 背景

- 11-16 遗留工具 `tools/build_kb.py`（硬编码 12 模块旧编号 MODULES_META）被运行，
  把 `data/knowledge.json` 从新编号策划版覆盖回 **12 模块 / 180 chunks**（built_at 2026-11-02）。
- 站点注册表 `data/modules.json` 已是新编号 **M0–M26 + S7（28 单元）**；
  `neural/data.js`（11-16 21:53）保留 **300 chunks** 完整快照（含 garble 修复）。
- 后果：AI 助教 `[M#]` 引用与站点内容错位；M12–M26/S7 全部检索不到；
  离线 KB 的 FAQ 映射层存在错位（旋转圆环/雅可比→M19 应为 M20 等）。
- /tmp 两个 11-16 备份（before-garble / before-tables）均为旧 12 模块版，不可用；
  11-13 备份为 18 模块中间版。唯一完整最新源 = neural/data.js。

## 恢复（命令与实际输出）

```bash
cp neural/data.js /tmp/data.js.before-recovery
~/.venv-tm/bin/python tools/recover_kb.py
# recovered: modules=28 chunks=300 chars=122709
~/.venv-tm/bin/python tools/recover_kb.py --check
# modules=28/28 chunks=300 missing=无
~/.venv-tm/bin/python tools/build_neural_data.py
# wrote neural/data.js  chapters=7 modules=28 sections=293 bytes=233372
diff -q /tmp/data.js.before-recovery neural/data.js
# ROUNDTRIP OK: data.js 逐字节一致（恢复 KB 与原快照互为源，证明无损）
```

新工具 `tools/recover_kb.py`：modules.json（元信息）× data.js（chunks）反向重建 KB；
注册表模块在快照中缺失时拒绝写出不完整 KB；带 --check 校验模式。

## 对齐修复

1. `tools/build_kb.py`：防回退守卫——现有 KB 更大时拒绝覆盖（需 --force），
   docstring 标注遗留工具。实测：
   ```
   REFUSED: 现有 KB 更大（modules=28 chunks=300），本遗留构建只有 modules=12 chunks=180（旧编号）。
   guard exit=1
   ```
2. `tools/ai_server.py`：
   - SYSTEM_PROMPT / REVIEW_PROMPT 模块数与清单改为按 KB 动态生成（5 处硬编码清除）；
   - MODULE_EQUATIONS 重映射为 28 条新编号（M6 傅科 T_F=2π/(Ω|sinλ|)、
     M7 CR3BP μc≈0.0385、M25 ω'=γω(1−βcosα) 均对照 data.js chunk 原文核实）；
   - chapter_menu 示例改为新编号（M12 Atwood）；
   - CHAPTER_KEYWORDS 扩充光锥/世界线/相空间/刘维尔/辛积分/傅科/拉格朗日点/
     网球拍/多普勒/集束/不变质量/共振/阻尼/简正/勒让德/罗斯/泊松等新主题。
3. `tools/build_offline_kb.py`：
   - FAQ_MX/GLOSS_MX 错位修复：旋转圆环/雅可比→M20，诺特荷/回旋圆心→M21，
     转动惯量→M18（滑轮→M12 先行匹配），新增圆柱→M5、单摆/阻尼→M16、
     恢复系数/雨滴/偏转→M4、甲虫/球壳/球冠/平行轴→M18、费马→M9、洛伦兹变换→S7 等；
   - FAQ 答案文本 11 处旧编号残留清理（M4 变分→M8–M10、M6 碰撞→M4、
     M7 刚体→M18、M8 双摆→M17 等）。
   - 重建输出：`offline kb: modules=28 faq=57 glossary=18 chunks=164 size=130KB`

## 验证（实际输出）

```bash
~/.venv-tm/bin/python -m py_compile tools/ai_server.py tools/build_offline_kb.py tools/build_kb.py tools/recover_kb.py
# SYNTAX OK
~/.venv-tm/bin/python tools/ai_server.py --check
# kb : OK (chunks=300)   upstream : DOWN（既有校园网关状况，AI 走本地 strata）
```

检索测试（进程内 retrieve，全部命中新编号）：

| 查询 | Top 命中 |
|---|---|
| 光锥和世界线是什么 | M24 固有时与双生子佯谬 / 时空间隔与光锥 |
| 自由刚体的网球拍效应 | M19 模块概览 / 中间轴稳定性 |
| 相对论碰撞的不变质量 | M26 模块概览 / 固定靶阈值 |
| 傅科摆进动周期 | M6 傅科摆方程与进动周期 |
| 拉格朗日点 L4 稳定性 | M7 L4/L5 稳定性、蝌蚪与马蹄 |

8765 服务重启（kill 3245 → nohup bash tools/serve.sh，新 pid 3612078）：

- `GET /api/health` → ok:true, **kb_chunks:300**, pipeline:local_only
- `GET /api/modules` → **28**，末条 S7 狭义相对论
- `POST /api/ask {"question":"你好"}` → 规则问候「你好同学，有什么问题？」
- `POST /api/ask {"question":"公式","module":"M24"}` →
  「你在 M24 · 光锥与世界线。主要方程：$s^2=c^2t^2-x^2$ 不变…」+ 正确来源链接

基线（本轮开始时）：`verify_selftest` **19/19 PASS**（00-binet、16-doppler-beaming
SKIP 无 selftestPanel 契约）；`check_links` **57 页 / 589 链 / 0 缺失**；
`check_html` 全部 6/6。

## 遗留（下一轮）

- i18n 翻译层（assets/i18n/reader-*）只覆盖旧模块目录，新模块/场景未翻译。
- 16-doppler-beaming 的自测面板格式与 verify_selftest 契约不符（MORNING-REVIEW
  记录其有 8 条自测），可补 #selftestPanel 契约。
- 上游 xplt 网关 DOWN 为既有网络状况，与本次改动无关。
