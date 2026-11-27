# 理论力学交互讲义 · 交接记录

日期：2026-11-23（文档于 2026-11-26 按仓库与机器实况重写）  
项目：`/home/wck/Theoretical-Mechanics`  
标题：**理论力学：从质点到哈密顿**  
仓库：`https://github.com/wck3069/Theoretical-Mechanics`（`main` 与 `origin/main` 同步，工作区干净）

> 本文件取代 2026-11-01 版本。更早的重构背景见 `HANDOFF-NEURAL.md`（11-10）与
> `MORNING-REVIEW.md`（11-11）；11-23 各轮的原始证据在 `qa/global/*-2026-11-23.md`。

## 1. 当前状态（一句话）

**七章（牛顿 → 相对论）+ 31 个交互单元（M0–M30）+ 狭义相对论章节导读单元 S7**，
由 23 个模块目录承载（部分目录用 `?mode=` / `?scene=` 承载多个单元）。
首页星图 7 行星 → 章节页 / 知识网络（`neural/`）→ 模块；AI 助教（RAG）知识库 32 单元 / 329 chunks。

> [!NOTE]
> 首页 hero 与 `HOMEPAGE.md` 写的是“27 个交互模拟”，与注册表 31 个 M 单元不一致（计数口径历史上
> 23→25→27 逐轮累加）。如需统一，改 `index.html` hero 与 `HOMEPAGE.md`。

## 2. 最近提交

```text
ef5ffd7 2026-11-23 fix(neural): close button dead on desktop preview panel
1edce75 2026-11-23 feat(site): seven-chapter cosmos restructure, true knowledge network, recovered KB
a177fa5 2026-11-23 fix(home): star-map portal iframe race and bfcache freeze
57772e0 2026-11-23 feat(modules): add M27-M30 interactive modules mined from the manuscript
104b4a5 2026-11-06 docs(deploy): record measured campus egress facts and add Wi-Fi reachability self-test
1dad1eb 2026-11-06 docs(deploy): campus NAT mapping request for a fixed site address
17ffafe 2026-11-06 feat(home): panel exclusivity, planet flight and sun fling on the star map
64f7ae8 2026-11-06 feat(tools): add static preview server and dist rebuild watcher
```

共 125 次提交。`1edce75` 一次性收下 11-07 至 11-23 的大量未提交重构（403 文件，+65,925 / −8,052）。
`gh-pages` 最后发布：2026-11-23 22:46。

## 3. 七章与单元映射

数据源：`data/chapters.json`（章 → 单元）、`data/modules.json`（单元注册表，32 条）。

| 章 | 名称 | 行星纹理 | 单元 |
|---|---|---|---|
| C1 | 牛顿力学 `chapters/01-newton` | 水星 | M0–M7 |
| C2 | 变分法 `chapters/02-variational` | 金星 | M8–M10 |
| C3 | 拉格朗日力学 `chapters/03-lagrangian` | 地球 | M11–M12 |
| C4 | 小振动 `chapters/04-oscillations` | 火星 | M13–M17、M27 |
| C5 | 刚体力学 `chapters/05-rigid-body` | 木星 | M18、M19、M28 |
| C6 | 哈密顿力学 `chapters/06-hamiltonian` | 土星 | M20–M23、M29 |
| C7 | 狭义相对论 `chapters/07-relativity` | 天王星 | S7、M24–M26、M30 |

### 3.1 单元 ↔ 目录

| 单元 | 标题 | 目录 / 入口 |
|---|---|---|
| M0 | 比奈方程 | `00-binet` |
| M1 | 有效势与轨道稳定性 | `01-effective-potential` |
| M2 | 散射与俘获 | `02-scattering` |
| M3 | 两体问题与系外行星 | `03-two-body` |
| M4 | 碰撞与变质量 | `06-collisions` |
| M5 | 圆柱脱离与运动学 | `08-kinematics?mode=cylinder` |
| M6 | 傅科摆与玫瑰线 | `14-foucault-rose` |
| M7 | 拉格朗日点 | `15-lagrange-points` |
| M8 / M9 / M10 | 等时摆 / 折射定律 / 最短路径 | `04-variational?mode=cycloid|refraction|shortest` |
| M11 | 虚功原理与静力学 | `05-virtual-work` |
| M12 | 有转动惯量的 Atwood 机 | `09-atwood-pulley` |
| M13 / M14 / M15 | 斜面滑块 / 弹簧摆 / 小车单摆 | `10-coupled-systems?scene=wedge|spring|cart` |
| M16 / M17 | 单摆周期修正 / 双摆混沌 | `08-kinematics?mode=pendulum|double` |
| M18 | 刚体几何与角动量 | `07-rigid-body` |
| M19 | 自由刚体与网球拍效应 | `17-free-rigid-body` |
| M20 / M21 | 旋转圆环上的珠子 / 磁场中的带电粒子 | `11-rotation-and-field?scene=ring|cyclotron` |
| M22 / M23 | 相空间与刘维尔 / 辛积分器比较 | `18-phase-space?scene=phase|integrator` |
| M24 | 光锥与世界线 | `13-lightcone-worldlines` |
| M25 | 相对论多普勒与车头灯效应 | `16-doppler-beaming` |
| M26 | 相对论碰撞与不变质量 | `19-relativistic-collisions` |
| M27 | 受迫振动与共振 | `20-forced-resonance` |
| M28 | 重陀螺的进动与章动 | `21-heavy-top` |
| M29 | 勒让德变换与罗斯约化 | `22-legendre-routh` |
| M30 | 双曲运动与恒固有加速度 | `23-hyperbolic-motion` |
| S7 | 狭义相对论（章节导读） | `chapters/07-relativity` |

> [!IMPORTANT]
> **目录号 ≠ 单元号**（如 `20-forced-resonance` 是 M27，`06-collisions` 是 M4）。AI 引用、知识库、
> 章节卡一律以 `data/modules.json` 的 `milestone` 为准。目录 `12-*` 不存在（S7 的 slug 为 `12-relativity`，指向章节页）。

### 3.2 旧章节路径

旧七章（`01-particle` `02-system` `03-variational` `04-lagrangian` `05-oscillations` `06-rigid-body`
`07-hamiltonian`）保留为约 1.2 KB 的跳转壳（“本章已并入…”），映射见 `data/chapters.json` 的
`slug_redirects`。不要在其中写内容。

### 3.3 手稿

每章 `chapters/0N-*/manuscripts/book.html`（C1–C7 全有）+ `figs/`；C1–C3 另有 `CORRECTIONS.md`
（C1 还有 `INTRO-CORRECTIONS.md`）。由 `tools/build_web_reader.py` / `build_manuscript_toc.py` 生成。
公式用本地 `assets/mathjax/tex-svg.js`（离线）。
旧版 `hw1.html` / `intro.html` / `chapter2.html` / `variational.html` 已不存在。

## 4. 11-23 四轮工作摘要

### 4.1 KB 恢复（`qa/global/kb-recovery-2026-11-23.md`）

- 11-16 误跑遗留 `tools/build_kb.py`，把 `data/knowledge.json` 覆盖回 12 模块旧编号。
- 新工具 `tools/recover_kb.py`：用 `neural/data.js` 快照 × `modules.json` 反向重建，往返 diff 为空。
- `build_kb.py` 加防回退守卫（现有 KB 更大则拒绝，需 `--force`）。**不要再用它重建 KB。**
- `ai_server.py` 提示词按 KB 动态生成；`MODULE_EQUATIONS` / `CHAPTER_KEYWORDS` / 离线 FAQ 映射对齐新编号。

### 4.2 知识网络“真网化”+ M27/M28（`qa/global/network-upgrade-2026-11-23.md`）

- `data/links.json`：**47 条边 / 20 条跨章**，4 类：method 同题异法 / limit 极限对照 / tool 共用工具 / prereq 前置路径。
- `neural/index.html`：章内贝塞尔连线、跨章胶囊、详情面板“交融 · 同题异法”区块、landing 跨章曲线 + 图例。
- 修复：语言旗标 `#tm-lang` 盖住面板 ✕；审计脚本旧路由（m5→m11）。
- 新工具 `tools/merge_kb_drafts.py`：把模块目录下的 `knowledge.draft.json` 合并进 KB。

### 4.3 星图链接失效（`qa/global/starmap-fix-2026-11-23.md`）

- 根因：`startPlanetFly()` 无 `state.flying` 守卫，慢纹理时一次点击产生 2–6 个 portal iframe；
  `popstate` 只删第一个，可见 iframe 永久盖住星图；`finishFlight` 回退跳转前不清状态，bfcache 返回冻结。
- 修复：重入守卫、建新 iframe 前清旧、popstate 全量清理、跳转前复位、`pageshow(persisted)` 兜底。
- 回归资产：`tools/qa-home/star_map_loop.py`（两模式 GREEN）。

### 4.4 M29/M30 + 桌面预览面板 ✕

- M27 13/13、M28 8/8、M29 15/15、M30 20/20 自检通过；每个模块含 `index.html` + `knowledge.draft.json` + README。
- 桌面端预览态 `closeDetail()` / `goUp()` 缺 preview 分支 → 已补；回归 `tools/qa-neural/panel_close_audit.py`。

## 5. 首页 / 星图要点

- 数据：`index.html` 内联的 `window.TM_MODULES`（← `data/chapters.json`，7 行星 = C1–C7）与
  `window.TM_SUBMODULES`（← `data/modules.json`）由 `tools/apply_home_data.py` 幂等重写；改注册表后要重跑它。
- 纹理：`assets/textures/2k_*.webp`（Solar System Scope，CC BY 4.0，见 `LICENSE.txt`），另有
  `assets/textures/hi/`（飞行时加载的高清版）与 `sm/`；太阳 `2k_sun.webp`、`nasa_sun_cme.webp`。
- 点击行星：飞行动画 → 章节/知识网络 portal iframe（`startPlanetFly` / `finishFlight`，见 4.3）。
- 以下 11-01 记录的细节仍有效：太阳 R≈92 px 随 `systemZoom` 缩放；滚轮缩放 0.45–2.6 仅在太阳盘内生效；
  拖动太阳平移整个系统；行星自转系数 `0.1`（`updatePlanets()`）；三层遮挡绘制；30fps、DPR≤1.25、后台暂停。
- 全站（除首页）使用 `assets/cosmos/` 星空设计系统；中英双语层见 `tools/build_i18n.py` / `assets/i18n/`。

## 6. 运行与部署（systemd 用户服务，均 active）

| 服务 | 作用 | 端口 |
|---|---|---|
| `tm-static-sync` | 监视源码，自动重建 `dist/` | — |
| `tm-static-server` | `tools/static_server.py` 读 `dist/`，注入 live-reload | 127.0.0.1:8081 |
| `tm-demo-tunnel` | cloudflared quick tunnel → 8081（开放预览，无登录） | — |
| `tm-login` | `~/TM-Login/app.py` 姓名登记门禁（Flask/waitress） | 0.0.0.0:8090 |
| `tm-tunnel` | cloudflared quick tunnel → 8090（登录门 = 网站 + AI） | — |
| `tm-ai` | `tools/ai_server.py` RAG 助教（Basic Auth，由登录门注入） | 127.0.0.1:8765 |
| `tm-backup.timer` | 每日备份登录数据库 | — |

另有手动进程：`tools/static_server.py --port 8123`（源码根直服预览）及其 cloudflared 隧道（11-16 起）。

当前 quick tunnel 地址（**重启即变**，以文件为准）：

- 开放预览：`~/.local/state/tm/demo-url`（→ `/tmp/tm-demo-url`）
- 登录门：`~/.local/state/tm/login-url`（→ `/tmp/tm-login-url`）
- GitHub Pages（静态、AI 仅离线检索）：`https://wck3069.github.io/Theoretical-Mechanics/`

配置（不提交）：`~/.config/tm-ai.env`（AI key、Basic Auth、模型）、`~/.config/tm-login.env`。
AI 上游校园网关（xplt）DOWN，当前走本机 strata（127.0.0.1:8080），`pipeline: local_only`。

固定域名：`deploy/named-tunnel.sh tm.<域名>` 一键脚本已写好（见 `deploy/cloudflared.md`），**尚未安装**
（无 `tm-named-tunnel.service`）；需要一个 Cloudflare 托管域名。校园 NAT 映射申请见 `deploy/campus-mapping.md`。

常用：

```bash
systemctl --user status tm-ai tm-login tm-static-server tm-static-sync tm-tunnel tm-demo-tunnel
systemctl --user restart tm-ai           # 改了 ai_server.py / knowledge.json 后
bash tools/export_static.sh              # 手动导出 dist/（通常由 tm-static-sync 自动完成）
bash tools/publish_pages.sh              # 强制更新 gh-pages
```

## 7. 数据与构建管线

```text
data/modules.json + data/chapters.json + data/links.json
        │
        ├─ tools/merge_kb_drafts.py   ← modules/*/knowledge.draft.json
        ├─ tools/recover_kb.py        （灾备：从 neural/data.js 反建 KB，--check 校验）
        ▼
data/knowledge.json  ──► tools/build_neural_data.py ──► neural/data.js
        │                └─► tools/build_offline_kb.py（Pages 离线 KB / FAQ）
        └─► tools/ai_server.py（tm-ai，重启生效）
```

新增模块的集成流程（按 11-23 M27–M30 的做法）：注册 `modules.json` → 加入 `chapters.json` 对应章 →
`merge_kb_drafts.py` → `links.json` 加边 → 章节卡（进入模拟 / 阅读书稿 / 知识网络）→
`ai_server.py` 的 `MODULE_EQUATIONS` / `CHAPTER_KEYWORDS` → `build_offline_kb.py` FAQ 映射 →
`build_neural_data.py` → 首页 hero 与 `HOMEPAGE.md` 计数 → 重启 `tm-ai`。

## 8. 验证命令与 11-23 结果

```bash
cd /home/wck/Theoretical-Mechanics
~/.venv-tm/bin/python tools/check_html.py index.html modules/*/index.html chapters/*/index.html neural/index.html
python3 tools/check_links.py --root .      # 或 --root dist
python3 tools/verify_selftest.py
~/.venv-tm/bin/python tools/build_neural_data.py
python3 tools/qa-home/star_map_loop.py
python3 tools/qa-neural/interaction_audit.py; python3 tools/qa-neural/audit_current.py; python3 tools/qa-neural/panel_close_audit.py
~/.venv-tm/bin/python tools/ai_server.py --check
```

11-23 最后一轮记录的结果（本文件重写时未重跑）：

- `verify_selftest`：**23/23** 通过。
- `check_links`：**61 页 / 605 链 / 0 缺失**；`check_html` 抽查页 6/6。
- `build_neural_data`：7 章 / 32 单元 / 47 边（20 跨章）。
- `tm-ai`：`kb_chunks=329`，M29/M30 检索命中。
- 星图回归两模式 GREEN；neural 三项审计 exit 0。

## 9. 已知问题 / 下一步

1. **计数不一致**：hero/HOMEPAGE “27 个交互模拟” vs 注册表 31 个 M 单元 / 23 个目录。确定口径后统一。
2. **模块页内导航**：`00-binet`…`17-free-rigid-body` 的上一页/下一页数组 `CHAPTERS` 仍是 11-01 的 12 个旧目录
   （`00-binet`…`11-rotation-and-field`）；`18`–`23` 没有该数组。未与七章 / 新编号统一，需改模块页或引入章节级导航。
3. **章节页是手写 HTML**：7 个 `chapters/0N-*/index.html` 无生成器；新增单元要手动加卡片。可补 `tools/build_chapters.py`。
4. **i18n 覆盖不全**：`assets/i18n/reader-*` 只覆盖旧模块目录，M13 以后的新模块/场景未翻译。
5. **`16-doppler-beaming`（M25）** 自测面板不符合 `verify_selftest` 的 `#selftestPanel` 契约（被 SKIP）；`00-binet` 同样无自检契约。
6. **固定域名未落地**：仍依赖 quick tunnel，地址会变；`named-tunnel.sh` 待有域名后执行。
7. **AI 上游**：校园网关 DOWN，助教只用本机 strata；单卡并发有限，公开访问需限流（`deploy/README.md`）。
8. **遗留工具**：`build_kb.py` 硬编码旧 12 模块编号，仅保留作参考，已加守卫。
9. **氢原子**：不属于本站，在 `/home/wck/Quantum-Mechanics`（`https://wck3069.github.io/Quantum-Mechanics/`），自 11-01 无更新。
10. **流程注意**：11-23 有子代理违规自行 commit（已 `reset --soft` 撤回）；委派时需明确禁止提交，并在合并前检查 `git log`。

## 10. 关键文件

- `index.html`：首页星图（7 行星、飞行/portal、太阳缩放拖动、星空）。
- `chapters/0N-*/index.html`：七章总览；`chapters/0N-*/manuscripts/book.html`：网页版书稿。
- `neural/index.html` + `neural/data.js` + `neural/structure.js`：知识网络。
- `modules/*/index.html`：交互模块（单文件）；新模块附 `knowledge.draft.json`、README。
- `data/*.json`：注册表、章节、知识库、跨章关联、模式。
- `tools/ai_server.py`、`tools/static_server.py`、`tools/export_static.sh`、`tools/publish_pages.sh`。
- `tools/recover_kb.py`、`tools/merge_kb_drafts.py`、`tools/build_neural_data.py`、`tools/build_offline_kb.py`。
- `tools/qa-home/`、`tools/qa-neural/`、`tools/verify_selftest.py`、`tools/check_links.py`、`tools/check_html.py`。
- `deploy/`：systemd 单元、cloudflared / named tunnel、Caddy / nginx、Tailscale、校园网说明。
- `~/TM-Login/`：登录门（Flask + SQLite）。
- `qa/global/`：各轮验收证据。

## 11. 新对话建议开场

> 读取 `/home/wck/Theoretical-Mechanics/HANDOFF.md`，先检查 `git status`、最近提交与
> `systemctl --user status 'tm-*'`。当前为七章 + M0–M30 + S7（23 个模块目录），单元编号以
> `data/modules.json` 为准。先不要改代码，告诉我未提交文件、Pages 与隧道状态，以及 `verify_selftest` 是否仍为 23/23。
