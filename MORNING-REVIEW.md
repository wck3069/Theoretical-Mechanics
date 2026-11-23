# 通宵美化 · 验收文档（2026-11-11 晨）

> 按昨晚指令执行：全站（除首页）星空化、手稿入库互联、从手稿挖掘新项目。
> 所有改动未提交（`git status` 约 140 条），等你验收后再提交。

---

## 0. 你昨晚指令的逐条完成对照

| 指令 | 结果 |
|---|---|
| 主页（太阳系）美术风格一定不改动 | ✅ `index.html` 未动一行。新模块 M13–16 数据已入库但**未注入主页星图数组**（见第 5 节，一条命令的事，留给你决定） |
| 主风格星空，优化其他画面 | ✅ 深空星空 + 梵高《星夜》元素（涡卷笔触、月晕、调色板）做成统一设计系统 `assets/cosmos/`，覆盖：知识网络页、16 个模块页、14 个章节页（含旧路径跳转壳）、5 个手稿页、手稿目录 |
| 多加入动态元素 | ✅ 视差星空层、流星、星云漂移、卡片玻璃悬浮、滚动渐显（`.cosmos-reveal`）、各新模块自带交互动画；`prefers-reduced-motion` 与后台页自动暂停 |
| 找网上素材 / GitHub UI 美化项目运用 | ⚠️ 网络受限：外网图片 CDN 被墙（梵高原图拿不到）。已落地：ESA/哈勃星云图 5 张（pillars/crab/xdf/omega/andromeda，见 `assets/cosmos/ATTRIBUTION.md`）；梵高笔触/月晕全部用代码生成（涡卷噪声 + 调色板 #0b1d51/#1a3a6e/#2c5aa0/#e8c15a/#f5e6b8）。星空玻璃卡片系统为自研（参照 glassmorphism 通行做法） |
| 手稿加入网页、对应部分链接到做好的项目 | ✅ 手稿 4 页移入章节目录并挂星空框：`chapters/01-newton/manuscripts/{intro,hw1,chapter2}.html`、`chapters/02-variational/manuscripts/variational.html`；旧路径留自动跳转壳（sitemap 保留旧 URL）；章节页新增手稿入口，手稿页反向链接对应模拟模块 |
| 从手稿找可做的项目并加进去 | ✅ 新增 4 个模拟模块（全部源自手稿推导，见第 2 节） |
| 子代理视觉检查 + 自我完善 | ✅ 每波都有 headless-Chrome 视觉审计（见第 4 节），最终 19/19 全绿 |

---

## 1. 星空设计系统（新）

`assets/cosmos/tm-cosmos.css`（8KB）+ `tm-cosmos.js`（22KB）+ `_demo.html`（合约演示页）。

接入合约（所有页面已按此接线）：

```html
<link rel="stylesheet" href="../../assets/cosmos/tm-cosmos.css">
<script defer src="../../assets/cosmos/tm-cosmos.js"></script>
<body data-cosmos="page" data-cosmos-accent="#7ec8ff" data-cosmos-nebula="pillars">
```

- 层全部 `position:fixed; z-index:-1`，不抢交互；`window.TMCosmos` 可编程。
- 去重：知识网络页原自带星场 `canvas#bg`（initBg/drawBg/bgStars）已删除，由 cosmos 统一供星。
- 手稿页特殊约束：纸张印刷底色 `#fff` 与墨迹完全未动（对 `manuscript.css` 的 diff 为**纯新增 0 删除**），星空只做页面外围框景 + 顶栏玻璃化（rgba(12,16,34,.62) 金边）。
- 章节旧路径壳页也星空化，跳转壳（meta-refresh + location.replace）保持字节不动的部分未动。

## 2. 新模块（手稿挖掘，4 个）

| 模块 | 里程碑 | 来源 | 行数 | 自测 |
|---|---|---|---|---|
| `modules/13-lightcone-worldlines/` 光锥与世界线 | M13 #7ec8ff | 相对论手稿 ch.7 | 492 | 9 |
| `modules/14-foucault-rose/` 傅科摆玫瑰 | M14 #ffd76e | 01-newton 手稿 hw1 | 580 | 6 |
| `modules/15-lagrange-points/` 拉格朗日点 | M15 #c678dd | 01-newton 手稿 ch.2 | 527 | 6 |
| `modules/16-doppler-beaming/` 多普勒与集束 | M16 #ff7a9e | 相对论手稿 ch.7 | 1045 | 8 |

- 每模块含 `knowledge.draft.json`，已合并进 `data/knowledge.json`：**18 模块 / 219 块 / 91,994 字**，完整性断言通过。
- `neural/data.js` 已重建：7 章 / 18 模块 / 212 节 / 174.5KB → 知识网络图里可直接点开 M13–16。
- 章节卡片：01-newton 加了 14/15 两张卡，07-relativity 加了 13/16 两张卡，每卡三链（进入模拟 / 手稿 PDF / 知识网络锚点，锚点已按 `toLowerCase` 惯例核验可解析）。
- 新模块暂无独立 PDF（卡链到 `manuscript/main.pdf`）。若要单模块 PDF：`tools/build_note.sh` 可用。

## 3. 手稿手术（M1）

- `chapter2.html` + figs → `chapters/01-newton/manuscripts/`；`variational.html` + figs → `chapters/02-variational/manuscripts/`。
- 旧路径 = 跳转壳（meta-refresh + `location.replace`），git 记录为 R（重命名）+ 壳。
- 手稿目录 hub、章节卡、TOC（`tools/build_manuscript_toc.py` 产物）全部重定向到新路径；墨迹锚点 #pN 数量核验不变（55/29/93/29）。
- `sitemap.xml`：新增 4 模块 + 6 手稿条目；旧 URL 保留（壳页有效）。

## 4. 门禁与视觉审计（全部对 dist :8081 实测）

| 门禁 | 结果 |
|---|---|
| `tools/check_html.py`（全部改动文件） | 通过，exit 0 |
| `tools/check_links.py` | **41 页 / 379 链 / 0 缺失** |
| `tools/qa-neural/pixel_audit.py`（全量 19 例） | **19/19 PASS**（唯一 warn：合法滚动容器 clipped） |
| `tools/qa-neural/interaction_audit.py` | exit 0（首页→章节跳转、面板交互 OK） |
| `tools/qa-neural/audit_current.py` | exit 0（移动端详情面板、节点数 OK） |

截图与汇总在 `/tmp/nqa/pixels/`。

## 5. 留给早上的决定

1. **主页是否上 M13–16**：数据已在 `data/modules.json`/`knowledge.json`，跑 `~/.venv-tm/bin/python tools/apply_home_data.py` 即可注入主页星图数组（会改 `index.html`，因"一定不改动"指令今晚未执行）。
2. **新模块 PDF**：要的话用 `tools/build_note.sh` 生成，再把卡片 PDF 链从 main.pdf 换成单模块。
3. **星云图是否保留**：5 张 ESA 图（有署名文件）只挂在新模块与部分页背景，不喜欢可去掉 `data-cosmos-nebula` 属性即可。
4. **提交**：全部未 commit，等你看过再打。

## 6. 已知偏差与备注

- C2 傅科摆：任务提示里"10 小时偏转 53.1°"是错的，正确 ≈106.1°（35°纬度），子代理已按物理事实修正。
- C3 拉格朗日：提示里 α=0/180 的期望值写反，按手稿约定保留正确版。
- `tools/export_static.sh:26` 的 localhost WARNING 是既有信息性提示（file:// 打开时 AI 面板才回落 8765 端口），非故障；已按"仅文档化"处理。
- W2b 遗留：旧 12 模块页基础 CSS 里原有背景规则仍在（cosmos 层在其之上），视觉无碍；如需彻底清理可单独一轮。
- `/tmp/tm-w2*/`、`/tmp/nqa/` 为今晚工作残留，可随手删。

---

## 7. 今晨精修（第二轮，按今晨逐条反馈）

| 反馈 | 结果 |
|---|---|
| 行星贴图旋转处有直缝 | ✅ `drawTexturedSphere` clip 后先铺 `color` 底再贴纹理；探针（自旋 1.7/3.2 两相位）接缝断口 **74/87→0**，最低 alpha→255。太阳贴图探针本就 gap=0，按"最小修复"未动 |
| 悬停/选中的 7 颗小球旋转特效换掉 | ✅ 删 `drawSparkles`（全站唯一调用点），新增 `drawHoverAura`：贴边双向彗尾弧（渐隐拖尾+头部光点）+ 金色虚线进动环 + 柔光；`if(sel)` 金色实心圆环一并移除，选中态由光环本身标示 |
| 点击跳转等待期特效要与行星"一起放大" | ✅ `drawFlightAura` 全部半径 ∝ r（金环 1.36r、彗尾弧 1.10r/1.24r、虚线间隔、头部光点均随 r）；仅弧在天球铺屏后钳到对角半径（只封顶、不缩回）。探针：r=100 环 136px、r=150 环 204px——严格等比 |
| 章节"书稿"补齐 | ✅ 02–06 每卡 actions 行插"书稿 PDF"（02×1、03×2、04×2、05×1、06×1，按 01-newton 惯例），全部解析到 `manuscript/pdf/chNN-*.pdf`；01/07 已有（核验 ch01×2、ch07×3 链）；`main.pdf` 全站清零；手写笔记卡内"手稿"字样保留 |
| 章节背景图 4K | ✅ 新 `assets/img/portal/`：earth/jupiter/mars/moon/sun/stars 4096×2048、pillars 3927×4096（0.2–2.4MB），7 个章节门户 `data-cosmos-nebula` 全部换挂 |
| 知识网络页 #orb 升级 | ✅ 真球体渲染：per-pixel 法线→经纬采样 equirect 纹理、固定光向量软明暗界线、limb darkening、明侧边缘辉光、外圈大气、12% 抗锯齿边；自转=每帧经度平移（~18fps 重绘，dt 驱动）；file:// 自动回退旧画法；hover 增亮+沿球轮廓的 accent 泛光。纹理由 8K 日面图 Lanczos 缩到 2048×1024（281KB），`assets/img/LICENSE.txt` 补 CC BY 4.0 署名 |
| 主页顶栏加书稿入口 | ✅ 关于按钮后 `<a href="manuscript/index.html">书稿</a>`；`.top-actions a` 现成规则覆盖样式，零 CSS 新增 |

### 今晨修的网站级 bug
- `tools/export_static.sh` 从不拷贝 `assets/img/` → dist 上 4K 背景与地球贴图全 404。已加一行 `cp -r "$ROOT/assets/img" "$OUT/assets/img"` 并重建：`moon.jpg`/`earth.jpg` 均 200。

### Kimi-K2.5 审查（Ali-dashscope/Kimi-K2.5，xplt 网关）
- **采纳 2**：飞行彗尾头部光点 `10` → `Math.max(10,r*0.09)`（大行星光点不再相对消失）；悬停彗尾弧最小线宽 1.1/0.8 → 1.5/1.2（高分屏不糊）。
- **驳回 3（附证据）**：`hexA`/`ORB_TAU` "未定义"是截取上下文导致的误报（`index.html:404`、`neural/index.html:907` 均有定义，且活体探针全程跑通）；"去掉 diag 钳制"不符合物理——`min(r·rad, diag)` 单调只封顶，行星铺屏后更大半径本就在屏幕外。

### 今晨门禁复跑
| 门禁 | 结果 |
|---|---|
| `check_html.py` × 45 个 HTML（全部非 dist） | **0 失败** |
| `check_links.py` | **41 页 / 382 链 / 0 缺失**（书稿新链全解析） |
| CDP 活体审计 :8081 | 悬停金色像素 39846、飞行中段金环 500px、neural `.orbtex.live` 着陆+章节路由均 true |
| 特效离屏探针 | hover gold 375/arc 1222 + 帧差 2459（在转）；flight gold 608/arc 2093/glow 15507；等比放大 goldB 600/arcB 3348 |

全部仍未提交，等你验收。旧 14 章节目录壳未动。

## 8. 追补：点击行星落地改造 + 知识网络美化 + 4K 去重（你反馈"点击星球后的界面还是没有美化"/"4K照片重复"）

- **落地改章节门户**：主页点击行星的飞行 iframe/回退跳转/pushState 共 4 处由 `neural/` 改挂 `m.sim`（数据里本就存着 `chapters/0X/index.html`，主页提示语"点击行星进入章节"从此名实相符）。实测：点击→iframe `chapters/06-hamiltonian/index.html` opacity 1、URL 与标题同步。知识网络仍从章节卡片「知识网络」链进入。
- **知识网络页美化**（`neural/index.html`，CSS+1 行 JS）：命中行星后 `body::before` 铺该章 4K 行星/星云图（portal 素材，双层压暗护图谱可读，opacity 交叉淡入），原生星空画布叠于图片之上；`html::after` 金线画框（随章节 accent 色）；检索框 focus 光晕。实测 computed-style：`data-chap` 正确、`::before` 三层背景 opacity 1、边框 `rgba(215,180,138,.16)` inset 12px。
- **4K 重复修复**：每章节页原本 body 铺 portal 4K + cosmos 星云层再叠一张 ESA 大图（同屏两张大星云），已删 7 个章节页的 `data-cosmos-nebula`；知识网络页的 7 幅映射与章节页严格一致（01→earth … 07→pillars），章节→网络同图无缝衔接，全站每张 4K 只出现一次。
- 门禁复跑：check_html 6/6、check_links 41 页 382 链 0 缺失、7 张 portal 图 8081 全 200。截图：`/tmp/tm-home/landing-new.png`、`/tmp/tm-home/neural-ch05.png`。

---

*执行方式：4 波子代理并行（V1 设计系统 / C1–C4 新模块 / M1 手稿手术 / W2a–W2d 全站接线）+ 今晨两波（章节书稿/4K、神经球）与主编排直接操刀的主页特效手术；逐项磁盘核验 + 门禁复跑 + Kimi-K2.5 外部审查。*

## 9. 落地回滚：星球点击恢复分支图（用户反馈"分支图怎么没有了"）
- 撤销 4 处 `m.sim || neuralHref(m)` 落地重定向，星球点击恢复知识网络分支图（图本身已带 4K 章景+金框，此前"两者都做"的美化诉求仍成立）。
- 章节门户可达性改由神经页面包屑提供：`太阳系 / 章名(图) / 章节门户`，链接由 slug 推导（`../chapters/<去前缀slug>/index.html`），不新增数据字段。
- CDP 复验：landing src=neural#/chapter-06-hamiltonian、data-chap 生效、crumb="太阳系/刚体力学/章节门户"；7 个 slug 推导路径全部存在；check_links 通过。

## 10. 分支图交互+美工升级（用户："不要只美化背景，交互体验和美工也要优化"）
- 委派单名 visual-engineering 代理完成 neural/index.html（+162 行）六项：
  1. 悬停/键盘聚焦邻域高亮：命中项+其连线全亮，其余压暗至 .3（SVG .focusing/.hot 类，沿用详情视图 .th 调光模式；中心球悬停点亮全部）。
  2. 搜索升级：同时过滤侧栏与图节点（非命中 opacity .18）、命中计数徽章「N 个节点」、✕清除按钮、「无匹配结果」提示、场内 Esc 清空不触发路由回退、rail 重建后恢复过滤。
  3. 图项键盘可达：行星/模块卡/知识节点 tabindex+role+中文 aria-label+Enter/Space（复制 orb 既有模式）；中心球无章节时清 role/tabindex（顺手修掉残留缺陷）。
  4. 面板焦点管理：开→焦点入 #pTitle，关→焦点回触发项（rail/图项重建后按 kind+idx 重定位）。
  5. :active 按压反馈 9 处（节点/卡/侧栏/链接/按钮）。
  6. 美工：搜索框放大镜 SVG+focus 展宽+金色光晕、面包屑当前项金色药丸、面板 pill 链接+排版节奏+滚动条、节点文字 paint-order 描边抗 4K 背景、notice 同语言、focus-visible 环全站、reduced-motion 补齐。
- 修复代理缺陷 1 处：applySearch 只查 gNodes 漏掉 gBells 里的总览卡片 → 改为 svg 根统一查（徽章 0→「2 个节点」）。
- CDP 复验（chapter-04）：kbd=2、总览邻域 dimmed2/bright1、模块邻域 dimmed4/bright1+focusing 类、搜索徽章/清除/Esc、光晕 shadow 生效、面板焦点 pTitle。check_html 6/6、check_links 382/0、dist 已同步。
