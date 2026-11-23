# 理论力学站 · 现状与重构交接文档

> 生成时间：2026-11-10 21:40（CST）  
> 下次开工先读本文件；结构与命令已按当前机器状态核对。
>
> **2026-11-11 通宵追加**：全站（除首页）星空化（`assets/cosmos/` 设计系统）、新增模块 M13–M16、手稿移入章节目录互联、知识库扩到 **7 章 / 18 模块 / 212 节点 / 219 chunks（91,994 字）**。全部改动未提交；验收详见 `MORNING-REVIEW.md`。

---

## 0. 一句话现状

首页星图（7 行星）→ 点击行星进入 **知识网络页**（贴图光球 + 模块玻璃卡 + 神经丝 + 粒子吞吐，无水母）→ 展开模块看节点扇形 → 右侧详情面板。书稿已入库但**章节结构与新书稿不一致**，下一步按第 7 节做重构。

---

## 1. 访问地址与服务

| 用途 | 地址 / 方式 |
|---|---|
| 主站（临时隧道） | `https://intended-chapters-deaf-cache.trycloudflare.com` |
| 主站本地 | `http://127.0.0.1:8081/`（dist） |
| 源码直服（调试用） | `http://127.0.0.1:8099/`（仓库根，手动 `python3 -m http.server 8099`） |
| 文件上传站 | `https://hook-libraries-ddr-firewall.trycloudflare.com`（本地 `127.0.0.1:8098`） |
| 隧道 URL 记录 | `~/.local/state/tm/demo-url`、`~/.local/state/upload-site/url` |

systemd 用户服务（均 active）：`tm-static-sync`（改文件自动重建 dist）、`tm-static-server`（8081 读 dist + 注入 live-reload）、`tm-demo-tunnel`（cloudflared → 8081）。

上传站进程：`python3 ~/upload-site/server.py --port 8098`，隧道脚本 `~/upload-site/start-tunnel.sh`。

---

## 2. 仓库关键文件

```
index.html                     首页星图（canvas 太阳系；太阳效果已定稿）
neural/index.html              知识网络页（单文件：路由 + 渲染 + 粒子；自带星场 canvas#bg 已删，星空由 cosmos 供）
assets/cosmos/                 星空设计系统（tm-cosmos.css/js + ESA 星云 5 张 + ATTRIBUTION.md + _demo.html）
neural/data.js                 生成物：chapters + modules + sections/chunks
neural/media/                  参考素材（orb.mp4 8.3MB / jellyfish.mp4 724KB）——当前已不使用
neural/NOTICE.md               素材署名（PolyForm Noncommercial）
manuscript/                    新书稿（main.tex/main.pdf/chapters/*.tex/figures）+ index.html
data/knowledge.json            18 模块 219 chunks 的原始知识库（构建数据源；M13–16 已合并）
tools/build_neural_data.py     由 knowledge.json + index.html 生成 neural/data.js
tools/apply_neural_entry.py    首页行星点击 → neural 页（幂等）
tools/export_static.sh         构建 dist（含 neural/、manuscript/）
tools/static_sync.py           dist 监听重建（WATCH_DIRS 含 neural）
tools/qa-neural/               CDP 审计脚本（cdp.py / audit_current.py / interaction_audit.py / pixel_audit.py）
~/upload-site/                 上传站（server.py / index.html / files/）
```

数据规模：**7 章 / 18 模块 / 212 个节点（section）/ 219 chunks**（neural/data.js ≈174.5KB）。

---

## 3. 知识网络页架构（neural/index.html）

- **路由**：hash。`#/<chapterSlug>` / `#/<chapterSlug>/<moduleId 小写>` / `#/<chapterSlug>/<moduleId>/<chunkId>`；`writeHash()` 内部 `pushState + applyRoute()`（`pushState` 不触发 `hashchange`，必须手动同步）。
- **状态**：`state = {chapter, module, node}`；`render()` 分派 `renderLanding / renderOverview / renderModule`。
- **光球**：`#orb`（CSS 光晕）+ `#orbTex`（canvas，按 `chapters[].texture` 滚动贴图 + 临边昏暗，`orbSpin` 自转）。reduced-motion 下不自转。
- **概览**：`moduleSpots(ch,s)` 计算落点（桌面环形 / 窄屏纵向一列）；每模块一张玻璃卡（`moduleCard`）+ 双描边神经丝（`threadPair`）。**水母已下线**（`buildJellyLayer()` 直接 return）。
- **模块展开**：`renderModule` 双弧扇形（桌面）/ 双列（窄屏）；`labelLines` + `resolveLabelBoxes`（避让其它标签与节点圆点，最多 ±2 行）；窄屏每节点额外透明命中矩形（≥44px）。
- **详情面板**：`renderPanel`；节点正文经 `formatChunkText → plainOf` 以**纯文本**呈现（见 6.1）；链接含“完整模块页 / PDF / 本章页”。
- **粒子吞吐**：`#fx` canvas（`initFx / bakeFx / fx 状态机`），吸入 + 爆发 + 路由火花；`reduce` 时不画。
- **键盘**：Esc 逐级（节点→模块→章节→回首页）、`/` 聚焦筛选、输入框内 Esc 先 blur。
- **地图/无障碍**：面包屑 4 级、`aria-label`、窄屏详情为底部抽屉。

---

## 4. 首页（index.html）现状

- 行星点击 → `neural/index.html#/<chapter-slug>`（`neuralHref()`，`tools/apply_neural_entry.py` 可重放）。
- 太阳：2k 贴图 + 表面米粒/亮丝层 + 白热芯 + 临边昏暗 + 约 2800 根向外毛刺（金→红径向渐变）+ 双帧差分可观测的呼吸。日珥已移除。
- 章节页入口保留：详情面板“本章页” → `chapters/<去 chapter- 前缀>/index.html`（`chapterDir()`）。

---

## 5. 本轮已修复并验证的交互（别再回退）

| # | 问题 | 修法 | 验证 |
|---|---|---|---|
| 1 | 点模块/节点只改 URL 不渲染 | `writeHash` 后调 `applyRoute()` | 点卡片后面包屑/标题/节点即时更新 |
| 2 | 光球进章节 404 | `chapterDir()`：`chapter-01-x` → `chapters/01-x/` | 200 |
| 3 | 模块面板 × 关不掉 | `closeDetail()` 兼容“只选模块” | 面板收起、回总览 |
| 4 | Esc 不能逐级 | keydown 改为 `if(state.chapter)` | 节点→模块→章节→首页 |
| 5 | 水母视频点不动 | 视频设 `pointer-events:auto` + click（现已整体下线） | — |
| 6 | 无效节点无反馈 | `applyRoute` 里 `showNotice` | 提示“找不到这个知识节点” |
| 7 | 移动端重叠 | 概览纵向栈；窄屏模块视图隐藏光球（`body.narrow-mod`） | 390×844 无重叠 |
| 8 | 桌面标签碰撞 | 避让含圆点、限幅 ±2 行、标签底板仅 hover 显示 | `labelLabelOverlaps=0` |
| 9 | `sec:derive` 占位正文 | 正则过滤内部标记，空则给友好提示 | 面板显示替代文案 |
| 10 | MathJax 报错块 | 正文改纯文本（见 6.1） | 无黄色错误块 |

复跑命令：

```bash
cd /home/wck/Theoretical-Mechanics
~/.venv-tm/bin/python tools/check_html.py neural/index.html        # 期望 6/6
python3 tools/qa-neural/audit_current.py                          # 截图 + 关键状态
BASE=http://127.0.0.1:8081 python3 tools/qa-neural/interaction_audit.py
```

---

## 6. 已知限制（新会话必须知道）

### 6.1 详情面板公式是纯文本
`data/knowledge.json` 的 chunk 是笔记片段，含 `sub:`/`eq:` 交叉引用标记与**无定界的行间公式**，直接喂 MathJax 会输出 “You can't use 'macro parameter character #'”。目前 `plainOf()` 去标记后按纯文本显示。
**根治方案**：在 `tools/build_neural_data.py` 里增加清洗（去标记行、给裸公式补 `$$…$$`、丢弃含 `#` 的非法片段），再恢复 MathJax。

### 6.2 环境没有可用视觉模型
- 主模型 `deepseek-flash` 无图像输入；`multimodal-looker` 被插件钉在 `strata/qwen3.8-flash-next-iq3_s`（该部署未启用图像投影）。
- 改 `~/.config/opencode/opencode.json` 的 `agent.multimodal-looker.model` **不生效**；`opencode run -m opencode-go/<vision>` CLI 会挂起/报错。
- 免费视觉模型（`opencode-go/*-free`）在目录里存在但**线上端点返回 server error**；`opencode-go/qwen3.8-max` 可用（付费）。
- 结论：视觉验收只能靠**截图 + 人眼**或像素/几何数值审计。

### 6.3 其他
- dist 22MB，其中 `neural/media` 8.8MB 已无引用（水母下线后）——可删，构建会更快。
- 隧道是临时的，重启换域名。
- GitHub Pages 未发布（`gh-pages` 仍是旧版）；发布用 `tools/publish_pages.sh`（force-push）。

---

## 7. 重构方案（已确认方向：按新书稿 7 章重构）

### 7.1 新书稿结构（`manuscript/chapters/*.tex`）

| # | 章节 | 主要小节（摘） |
|---|---|---|
| 1 | 牛顿力学 | 运动的描述、参考系、自然坐标、牛顿三定律、中心力 |
| 2 | 变分法 | 费马原理、泛函与一阶变分、欧拉–拉格朗日方程 |
| 3 | 拉格朗日力学 | 约束与广义坐标、虚功原理、达朗贝尔、拉格朗日方程 |
| 4 | 小振动 | 平衡与稳定、阻尼/受迫、简正坐标 |
| 5 | 刚体力学 | 刚体运动学、欧拉角、惯量张量、角动量 |
| 6 | 哈密顿力学 | 勒让德变换、正则方程、相空间、罗斯约化 |
| 7 | 狭义相对论 | 洛伦兹变换、同时性、时间膨胀、时空间隔 |

### 7.2 现有章节 vs 新书稿

| 现网站（7 章） | 新书稿（7 章） |
|---|---|
| 质点力学 | 牛顿力学 |
| 质点系力学 | 变分法 |
| 变分法 | 拉格朗日力学 |
| 拉格朗日力学 | 小振动 |
| 小振动 | 刚体力学 |
| 刚体力学 | 哈密顿力学 |
| 哈密顿力学（空） | **狭义相对论（新增内容）** |

### 7.3 建议的目标结构（含关键词证据）

关键词密度（`grep -c`，见下表）用于把 12 个现有模块重新分配到 7 章：

| 新章 | 行星贴图 | 模块 | 证据（该章关键词命中） |
|---|---|---|---|
| 1 牛顿力学 | 2k_mercury | M0 比奈方程、M1 有效势、M2 散射、M3 两体 | 有效势 11 / 散射 20 / 两体 10 / 运动学 11 |
| 2 变分法 | 2k_venus_surface | M4 变分原理与等时摆 | 变分 35 / 费马 4 / 拉格朗日方程 11 |
| 3 拉格朗日力学 | 2k_earth_daymap | M5 虚功原理、M9 Atwood、M6 碰撞与变质量 | 虚功 25 / 耦合 13 / 拉格朗日方程 10 |
| 4 小振动 | 2k_mars | M8 非线性振动、M10 耦合系统 | 简正 10 / 耦合 21 |
| 5 刚体力学 | 2k_jupiter | M7 刚体几何与角动量 | 刚体 128 / 转动惯量 25 |
| 6 哈密顿力学 | 2k_saturn | M11 旋转参考系与磁场 | 正则 72 / 哈密顿 18 |
| 7 狭义相对论 | 2k_uranus | **M12（新建，来自 ch07.tex）** | 相对论 13 / 洛伦兹 9 / 变质量 7 |

待核对项：M6 碰撞（ch01 19 次 / ch05 19 次）与 M8 的运动学部分（ch01 运动学 11）归属，需按 `ch0X.tex` 正文确认后再定。

### 7.4 执行步骤（建议在新会话按序做）

1. **改数据源**：`data/knowledge.json` 追加/改写章节元信息（7 章新标题、新 slug、texture），模块按 7.3 重新挂载；M12 由 `ch07.tex` 抽取 section→chunk。
2. **改生成器**：`tools/build_neural_data.py` 的章节来源仍是 `index.html` 内联 `TM_MODULES`/`TM_SUBMODULES` —— 需要新增/迁移到 `data/chapters.json`，避免继续从首页脚本刮。
3. **改首页**：`window.TM_MODULES`（7 章）标题/配色/贴图、`TM_SUBMODULES`（12+1 模块）与 `neuralHref` 保持一致；`radiiArr/baseAArr` 等 7 元素数组不变。
4. **改章节页**：`chapters/<slug>/index.html` 目录名按新 slug 重命名/新建（旧 `01-particle…07-hamiltonian` → 新 7 章），并更新其模块列表。
5. **M12 内容**：从 `ch07.tex` 拆分 section，补进 `data/knowledge.json`（或直接生成），确保每个 section 至少 1 段正文。
6. **跑验证**：
   ```bash
   ~/.venv-tm/bin/python tools/check_html.py index.html neural/index.html
   python3 tools/qa-neural/audit_current.py           # 7 章 × 3 层截图
   BASE=http://127.0.0.1:8081 python3 tools/qa-neural/interaction_audit.py
   ```
   验收标准：每章都能进入；面包屑 4 级；Esc 4 段返回；移动端无重叠；标签重叠 = 0；无 404；控制台无 Uncaught。
7. **清理**：删 `neural/media/orb.mp4`（8.3MB 无用）；`data/knowledge.json` 与 `data.js` 保持一致（重跑生成器）。

### 7.5 风险

- 章节重命名会打断**外部旧链接**（`#/chapter-01-particle`）。建议保留 `oldSlug → newSlug` 重定向表。
- 模块重分配会让部分模块“跨章”（如 M6 碰撞），需确认是拆模块还是归一章。
- M12 内容从 tex 抽取质量不稳定，可能需要人工校订 section 标题。

---

## 8. 上传站（`~/upload-site/`）

- 单文件上传（≤512MB），返回不可猜 token 链接：`/f/<token>/<name>`。
- 存储 `files/<token>/<文件名>` + `meta.json`（size / sha256 / 时间）。
- 已收：`书稿.zip`（46.1MB，21:23）→ 已解包同步到 `manuscript/`。
- 重启隧道：`~/upload-site/start-tunnel.sh`。

---

## 9. 下一步待办（按优先级）

1. 按 7.3 定稿映射（先核对 M6 / M8 归属）。
2. 迁移章节元信息到 `data/chapters.json`，改造生成器。
3. 新建 M12（狭义相对论）内容。
4. 重跑数据 + 首页/章节页重命名 + 旧链接重定向。
5. 详情面板公式排版（6.1）。
6. 删除无用 `neural/media/orb.mp4`；决定是否发布 GitHub Pages。
7. 视觉复核（需人眼或可用视觉模型）。
