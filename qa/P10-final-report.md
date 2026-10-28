# P10 最终交付报告（星图改版 + 初学者内容 + 本地 AI + 远程访问）

生成时间：2026-10-29
验收人：明早/中午人工复核
执行方式：DeepSeek V4.1 Flash 编排；UI/文案由免费 AI（beam-free / deepseek-free / glm-free）执行；物理公式修复由 GPT-6 Astra 与主控完成；最终视觉验收由免费视觉模型 nemotron-3.5-super-vl-free 逐张看图完成。

---

## 1. 交付内容

### 1.1 首页：开普勒行星系统星图（原创）
- 中心恒星（质心）+ 9 条椭圆轨道 + 9 颗行星，行星按开普勒第二定律运动（掠面速度守恒）。
- 相关章节之间绘制星座连线；行星有环（M0）、卫星（M3）、彗尾（M8）等差异化细节。
- 右侧「星表 STAR CATALOG」、左侧导读、底部搜索/星等筛选/标签/速度控制、详情面板、学习路径抽屉、术语表。
- 顶部栏新增「术语」，内置 12 个初学者一句话定义。
- 深空星云 + 三层星空 + 流星；尊重 `prefers-reduced-motion`。
- 单文件、零外部依赖；ES2017；`check_html.py` 6/6。

### 1.2 9 章模块：深空主题 + 初学者改造
- 注入星空/玻璃主题与轨道章节导航（桌面右下、手机右下紧凑版），物理 JS 未被改动（主题为独立注入块，可 `--revert`）。
- 每章新增 `.intro`：这章回答什么 → 最惊人的结论 → 第一步拖哪个滑块、盯哪里。
- HUD 全部改为「中文 + 符号」；滑块补物理含义与单位；无量纲约定前移/说明。
- 映射表补「阅读推导 note.pdf」入口；M0 新增 README。
- 术语、误解和符号系统统一（M7 h、M8 Lorentz、M6 e=0、M2 截面等）。

### 1.3 本地 AI 助教「问星」
- 后端：`tools/ai_server.py`（同源静态服务 + `/api/health`、`/api/modules`、`/api/ask`）。
- 知识库：`tools/build_kb.py` 从 9 章 `note.tex`/README 抽取 **149 个文段 / 66,325 字符**。
- 前端：`assets/tm-ai-panel.html` 浮动面板，快速/深空两种模式；在线用本地模型，离线自动降级为 9 章元数据检索。
- 本地后端支持 Strata（默认 8080）与 KVMem 长上下文（18200，深空模式）。
- 安全：并发上限 `TM_MAX_CONCURRENT=2`、每 IP 限流 `TM_RATE_PER_MIN=20`，超出返回 429。

### 1.4 部署与远程访问
- `tools/export_static.sh` → `dist/`（2.8 MB，11 个 HTML，9 份 PDF，无 localhost 引用）。可直接上传 GitHub Pages / Netlify / nginx；AI 面板降级为离线检索。
- `TM_HOST=0.0.0.0 bash tools/serve.sh` → 教室局域网共享完整 AI（启动时打印真实内网地址）。
- `deploy/`：Tailscale（推荐）、Caddy（HTTPS + Basic Auth）、Nginx（auth_basic + limit_req）、Cloudflare Tunnel + Access 的现成配置与安全清单。
- 明确警告：8765 端口无内置鉴权，禁止裸暴露公网。

---

## 2. 物理审核修复（8 个 BLOCKER + 关键 MAJOR）

| 章 | 修复 |
|---|---|
| M0 | GR 修正改为 `u''+u=GM/h²+3GM u²/c²`（λ_GR=3GM/c²）；`μu³` 明确为唯象进动；量纲说明改为 `G=M=1、h=L/m=1 ⇒ C=1`；页面同名文案同步 |
| M2 | 数值表改为 `Θ=0.920151`、`dσ/dΩ=0.282942`；`b<b_c` 措辞改为“不受势垒阻挡而越过”；长程/短程归因修正 |
| M3 | `r1,max=M2 a(1+e)/(M1+M2)`；`K=(M2/(M1+M2))(2πa/P)/√(1−e²)·sin i`；页面标签改为 M☉ |
| M5 | 直角摆 `V=-2ρg[a²cosφ−b²sinφ]`、`tanφ=-b²/a²`；弹簧杆 `V=+Pl/2 sinθ+½k(L−l0)²`、`P/2=k(L−l0)h/L`；两圆柱 `sinφ=r/(R−r)` 并补压力；梯子临界改为摩擦饱和 |
| M6 | `e=0` 不再称“粘连/β=0”：切向速度保留，`β=arctan(2tanα)−α`，`β_max=19.471°`；`β_max(e=0.5)=36.8699°` |
| M7 | 删除“让我重新计算。”草稿句；球冠参数统一为 h（球冠高度）；`shellV` 单位 bug 修复；甲虫世界角修复；页面公式改为 `d=h(4R−h)/[4(3R−h)]` |
| M8 | Lorentz 力符号改为 `m v̇x=-eB vy`、`m v̇y=-eE+eB vx`（漂移 `E×B/B²` 方向正确）；相空间分界 `E=mgL`；渡河最小漂移 `√3 d≈1.732d`；清理推导草稿问句 |

7 份受影响的 PDF 已用 `latexmk -xelatex` 重编译，页数正常、无 `??`。

---

## 3. 验证结果（全部通过）

| 检查 | 结果 |
|---|---|
| `check_html.py`（10 个 HTML × 6 项） | **60/60 通过** |
| `verify_selftest.py` | **8/8 有 selftest 契约的模块全 PASS**；M0 为遗留模块，SKIP（无 selftest 契约） |
| `layout_qa.py`（10 页 × 1440/390） | **20/20 通过**（无横向溢出、无关键浮层遮挡、无 <11px 文本、画布非零） |
| 免费视觉模型逐张看图 | **12/12 页面 PASS**；手机详情页两按钮在 9s 加载后可见 |
| `/api/health` | OK，149 chunks，busy/max_concurrent/rate_per_min 正常 |
| `/api/ask` fast（M1 有效势） | 中文回答 + [M1] 引用 |
| `/api/ask` deep（M8 Lorentz） | 方程符号与漂移方向均与修正后的论文一致 |
| 503 离线降级 | 指向不可用上游时返回 `upstream_offline` + 前端离线检索 |
| 限流 | `TM_RATE_PER_MIN=3` 下第 4 次请求返回 429 |
| 静态导出 | 2.8 MB、11 HTML、9 PDF、无 localhost 引用 |

---

## 4. 已知限制（有意保留/未展开）

1. **M4**：折射/最短路径下拉项已禁用（页面仍演示等时摆），推导见 note.pdf，避免“死模式”。
2. **M5**：梯子打滑后的动画仍用无摩擦滑动近似；画布文字已中文化。
3. **M6**：二维碰撞动画的接触判据仍是近似；HUD 的 `v / e′` 槽仍为一符两义（已加注说明）。
4. **M8**：圆柱/单摆模式为静态示意图；双摆为真实积分。
5. **M0**：遗留模块，无 `?selftest=1` 契约。
6. **AI**：本地模型回答质量随模型/负载变化；离线模式只做元数据检索，不做公式推导。
7. **限流**：单卡 GPU 默认 2 并发；deep 模式较慢，适合答疑而非全班同时使用。

---

## 5. 明天怎么验收

```bash
cd /home/wck/Theoretical-Mechanics

# 1) 起服务（本机 + 完整 AI）
bash tools/serve.sh
# 打开 http://127.0.0.1:8765/

# 2) 只验收静态站
bash tools/export_static.sh
# 打开 dist/index.html，或把 dist/ 上传静态托管

# 3) 一键回归
/home/wck/.venv-tm/bin/python tools/check_html.py index.html modules/*/index.html
python3 tools/verify_selftest.py
python3 tools/layout_qa.py
```

重点看：
- 首页星图：悬停/点击行星、星表、详情、术语表、学习路径。
- `?ask=1`：问「什么是有效势」「Lorentz 力漂移方向」「e=0 会粘住吗」。
- 手机 390px：底部筛选、详情两个按钮、AI 面板。
- `deploy/README.md`：远程访问的三种方案与安全边界。

---

## 6. 变更文件一览

- 改：`index.html`、`modules/00-binet` … `modules/08-kinematics`（9 章 HTML）、`tools/check_html.py`、`PLAN.md`
- 新增：`assets/`（design-tokens、模块主题片段、AI 面板）、`data/knowledge.json`、`deploy/`、`dist/`
- 新增工具：`tools/build_kb.py`、`ai_server.py`、`serve.sh`、`apply_theme.py`、`apply_ai_panel.py`、`export_static.sh`、`layout_qa.py`、`verify_selftest.py`、`AI-README.md`
- 审核与修复报告：`qa/P10-content-audit.md`、`qa/P10-physics-audit.md`、`qa/P10-fixes-ui-*.md`、`qa/P10-physics-fixes.md`、本报告

> 未执行 `git commit` / `git push`（按规则需你明确指示）。`dist/`、`.omo/`、`tmp/`、`__pycache__/` 已加入 `.gitignore`。

---

# 第二轮：美术、动画与物理缺口修复（2026-10-29 凌晨）

## 参考研究（只学方法，不搬素材/代码）
细读 `luoluo-121/neural-creator-dashboard` 的 `NetworkCanvas.jsx`、`Home.jsx`、`neural.css` 后，提取的是动效原则：
弹簧/缓动驱动的位移、分层辉光与 additive 混合、入场错峰、悬停放大、深度与拖尾；
没有复制其水母/光球视频、银灰配色或任何代码。我们的实现全部是 Canvas 2D 的球体高光、3D 投影与轨道系统。

## 首页流畅度
- 星空/星云/暗角一次性预渲染到离屏画布，每帧只 blit + 一小部分闪烁星，消除每帧创建渐变。
- 行星/辉光改为预渲染 sprite（含高光与边缘光），不再每帧 `createRadialGradient`。
- 行星拖尾、悬停弹簧放大、选中环、入场错峰（easeOutCubic）。
- 顶部栏/目录/命令栏/AI 面板的毛玻璃模糊半径下调一档，降低低端机 GPU 压力。

## 模块级修复
- **M4**：折射与最短路径从“死模式”变为可用；新增折射率 n；Snell 数值求交、光脉冲、直线 vs 下凹轨道赛跑。
- **M5**：梯子打滑改为 3×3 牛顿–欧拉方程 + 库仑摩擦（static / slide / detached 三态）；3D 木梯、N_w/N_f/f/P 箭头、摩擦锥；移动端字号 ≥11px。
- **M6**：碰撞判定改用真实半径，二维法向冲量；球体 3D 高光/拖尾；0.5s 接触停顿 + 白色闪光；`?demo=contact` 可确定性展示接触瞬间。
- **M7**：球冠改为可拖拽旋转的 3D 球面 + 切割圆盘 + 质心标记；h 上限改为直径 2R；甲虫-圆环恢复为 3D 圆环 + 甲虫 + 拖尾，可拖拽旋转。
- **M8**：圆柱脱离、单摆、双摆全部动画化，3D 球体与拖尾。

## 本地 AI 接入修复（file:// 也可用）
- 原因：面板原本在 `location.protocol === 'file:'` 时直接跳过健康检查，所以双击打开永远是“离线”。
- 修复：file:// 下自动请求 `http://127.0.0.1:8765/api/health` 与 `/api/ask`；服务端已有 CORS `*`。
- `tools/check_html.py` 仅放行本机环回 `http://127.0.0.1:8765` 与 `API_BASE + '/api/...'`，外部 URL 仍然 FAIL。
- 面板未连接时，关闭再打开会重新探测，不必刷新页面。
- 注意：GitHub Pages 没有 `/api`，线上 AI 面板仍按设计降级为离线检索。

## 第二轮的验收数字
- `check_html.py`：10 个 HTML × 6/6 = **60/60**
- `verify_selftest.py`：**9/9**（8 个有契约模块 + M0 SKIP）
- `layout_qa.py`：**20/20**
- 免费视觉模型逐张确认：M4 折射/最短路径、M6 接触闪光、M7 3D 球冠/甲虫、M8 三模式动画、首页构图
- AI：`file://` 与 `http://127.0.0.1:8765` 均显示“本地模型在线 · qwen3.8-flash-next-iq3_s”
