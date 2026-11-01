# 理论力学交互讲义 · 交接记录

日期：2026-11-01  
项目：`/home/wck/Theoretical-Mechanics`  
标题：**理论力学：从质点到哈密顿**

## 1. 当前状态

站点结构：**七章 + 9 个可交互模块 + 1 个氢原子独立专题**。

七章与模块映射：

| 章 | 名称 | 模块 |
|---|---|---|
| 1 | 质点力学 | M0 比奈、M1 有效势、M2 散射 |
| 2 | 质点系力学 | M3 两体、M6 碰撞/变质量 |
| 3 | 变分法 | M4 变分原理 |
| 4 | 拉格朗日力学 | M5 虚功/拉格朗日 |
| 5 | 小振动 | M8 运动学/非线性振动 |
| 6 | 刚体力学 | M7 刚体 |
| 7 | 哈密顿力学 | 暂无模块，章节页为导读/建设中 |

- 首页星图有 **7 颗行星**，点击进入 `chapters/01-particle` … `chapters/07-hamiltonian`。
- 氢原子**不占 C1–C7 编号**，已拆为顶层独立目录 `hydrogen/`；首页 topbar「氢原子」进入 `hydrogen/index.html`。
- 旧路径 `modules/09-hydrogen/index.html` 保留为轻量重定向页（meta refresh + JS），指向 `../../hydrogen/sim.html`，避免旧链接与模块页上一章/下一章断裂。
- 原有 M0–M8 模块页保留，作为章节下的子模块。

## 2. 氢原子独立专题 `hydrogen/`

```text
hydrogen/
  index.html   专题导读（标题、两张入口卡、公式与说明）
  sim.html     交互实验：3D 电子云 + 径向波函数/能级图
```

### 2.1 3D 电子云（沿用原 M9）

- 量子数 n = 1…3，l = 0…n−1，m = −l…l。
- 两种模式：透明等值面（marching tetrahedra，|ψ| 等值面）与点状图（按 r²R² 与角向概率拒绝采样）。
- 多个 (n,l,m) 轨道可叠加；颜色由 `orbColor(n,l,m)` 决定，n 定主色相（1 青 / 2 金 / 3 紫），l、m 微调。
- 拖动旋转、滚轮/双指缩放、自动自转；`prefers-reduced-motion` 下停止自转。
- HUD 增加**能级 E = −13.60/n² eV**。

### 2.2 径向波函数图（新增）

- 面板按钮「径向波函数与能级」打开全屏 sheet；也可用 `hydrogen/sim.html?radial=1` 直接打开。
- 布局按 **(n,l) 多子图**：n=1、n=2、n=3 各一个子图，子图内画 l=0…n−1 的 R_nl(r) 曲线。
- 颜色与 3D 轨道列表完全一致：`orbColor(n,l,0)`，同一 (n,l) 在两个视图同色。
- 横轴 r/a₀ 自适应：扫描所有 l，取 |R| 衰减到峰值 1% 以下的外缘，再吸附到整齐刻度 `[6,8,10,12,16,20,24,28,32,40,48]`；纵轴按该 n 下所有 l 的峰值对称展开。
- 径向节点用空心圆标在 R=0 轴线上，数量 n−l−1。
- 右侧能级阶梯：E_n = −13.6/n² eV，线性坐标（−14.6…1.6），n=1/2/3 按 n 着色，当前 n 加粗发光；0 eV 为电离线。
- 交互：
  - 悬停子图显示 `r/a₀` 与 `R_nl(r)` 读数；
  - 点击曲线选最近的 (n,l)，同步 n/l/m 下拉框与 HUD；
  - 点击能级选最近的 n；
  - Esc 或「关闭」收起。
- **节点检测细节**：判符号时跳过恰好为 0 的样本，用“最后一个非零符号”判翻转。否则 R_3_1 在 r=6 被采样到 0 时会漏掉节点（已由自检抓到并修复）。

### 2.3 自检契约

`hydrogen/sim.html?selftest=1` 输出 `#selftestPanel`，包含 14 条断言：

- 对全部 6 条 R_nl（n≤3）验证 ∫₀^∞ r²R²dr = 1（阈值 2×10⁻³）；
- 验证径向节点数 = n−l−1；
- 验证 R_10(0) = 2。

`tools/verify_selftest.py` 默认目标已加入 `hydrogen/sim.html`。

### 2.4 限制

- 只实现 n ≤ 3 的解析径向函数；n=4 需要补 R_40…R_43，并检查归一化。
- 能级图只用线性刻度；不显示精细结构、自旋或塞曼分裂。

## 3. 首页 / 星图

### 3.1 数据

- `window.TM_MODULES`：7 个章节对象（C1–C7），`sim` 指向章节页。
- `window.TM_SUBMODULES`：9 个 M0–M8 模块数据，用于兼容/来源链接。
- 星图、星表、筛选、搜索围绕 7 个章节；行星点击直接进入章节页。
- 顶栏「氢原子」→ `hydrogen/index.html`；hero 计数为 7 章 / 8 次作业 / 1 个独立专题 / 9 个模块。
- `showDetail()` 仍存在但星图基本不用；`TM_SUBMODULES` 保留。

### 3.2 行星纹理

来源：Solar System Scope 2K 纹理，本地 `assets/textures/`，CC BY 4.0。现已全部转为 **WebP (quality 82)**。

映射：

- C1 质点力学 → 水星 `2k_mercury.webp`
- C2 质点系力学 → 金星 `2k_venus_surface.webp`
- C3 变分法 → 地球 `2k_earth_daymap.webp`
- C4 拉格朗日力学 → 火星 `2k_mars.webp`
- C5 小振动 → 木星 `2k_jupiter.webp`
- C6 刚体力学 → 土星 `2k_saturn.webp`（保留光环）
- C7 哈密顿力学 → 天王星 `2k_uranus.webp`
- 太阳 → `2k_sun.webp`

渲染：

- `drawTexturedSphere(...)`：纹理 + 太阳方向光照 + 赤道参考线 + 自转偏移。
- 行星不自发光，只有太阳发光；土星环用 `o.tilt`；地球保留月球。

### 3.3 太阳

- 直径 **4.87956 cm**，按 96 dpi 为 `R = 92.21 px`，随 `systemZoom` 缩放。
- 无中心白点、无十字坐标轴、无呼吸效果。
- 自转 `sunSpin += dt * speed * 0.05`。

### 3.4 行星自转与倾角

```js
o.spin += 0.1 * (orbitalDays[i] / spinDays[i]) * dθ;
```

`0.1` 是整体放慢 10 倍的视觉系数。真实每公转自转圈数：水星 1.50、金星 −0.925、地球 366.25、火星 669.6、木星 10477、土星 24232、天王星 −42722。

轴倾角：水星 0.034°、金星 177.4°、地球 23.44°、火星 25.19°、木星 3.13°、土星 26.73°、天王星 97.77°。

### 3.5 遮挡与轨道

- `planetPos()` 返回 `z = r * sin(θ)`。
- `drawOrbits()` 分三层：背面行星（z≤0）→ 太阳 → 前景行星（z>0）。
- 轨道长轴固定 `rot = −14°`，不随时间进动。

### 3.6 缩放与拖动

- `systemZoom` 默认 1；滚轮范围 0.45–2.6，**只在鼠标位于太阳圆盘内生效**。
- 拖动太阳移动整个系统：更新 `starCenter`，行星、轨道、月球、土星环、星尘与星空同步平移；拖动时清空旧轨迹，拖动结束抑制误点击行星。

### 3.7 星空

- 背景星云静止；300 颗星逐点独立闪烁（窄屏 170）。
- 星空缓慢定向流动（约 4 px/s 向右、1.2 px/s 向下），边缘无缝回环。
- 背景层随太阳拖动平移；`prefers-reduced-motion` 关闭流动/闪烁。

### 3.8 性能

- 首页 canvas DPR 上限 1.25，动画限 30fps，后台标签页暂停 rAF。
- 尘埃 68（窄屏 48），`bursts` 上限 720。
- 已去掉大块 `backdrop-filter` 模糊。

## 4. 纹理与许可

- 8 张 Solar System Scope 2K 纹理（2048×1024），JPEG → WebP：quality 82、method 6，尺寸与内容不变。
- 总体积 **4.4M → 1.4M**（约 −68%）。单张最大为水星 406K。
- 原始 JPEG 备份在仓库外：`/home/wck/.cache/tm-textures-jpg/`（不提交）。
- `assets/textures/LICENSE.txt` 已更新：列出 `.webp` 文件名，并注明 2026-11-01 的 WebP 重编码属于修改（CC BY 4.0 要求）。
- `tools/ai_server.py` 的 MIME 表新增 `.webp: image/webp`。

## 5. 其他提交的修复

### M1 有效势

`modules/01-effective-potential/index.html`：

- 轨迹尾迹按**实测轨道周期**衰减（当前周期的 3.5 倍），不再固定长度。
- 通过 θ 穿越 2π 的间隔测量周期；未测到前用线性化频率或 L/r² 估计。
- `initState()` / `placeAt()` 重置 `orbitTMeasured`、`lastThCross`、`lastThT`。

### M5 虚功/梯子

`modules/05-virtual-work/index.html`：

- 鼠标/触控可直接拖动梯子改变 θ；拖动时暂停模拟，松手后按新角度重新判断打滑。
- 落地终态改为 θ=0 水平，删除落地前 0.03/0.003 rad 的提前吸附和回弹。
- 慢速动画按 `dt*speed` 拆小步 RK4，避免低速抖动。

## 6. 运行与部署

### 本地服务

```bash
cd /home/wck/Theoretical-Mechanics
TM_STATIC_ROOT="$PWD/dist" bash tools/serve.sh
```

进程 PID 易失效，现场查询：

```bash
pgrep -af 'tools/serve.sh'
pgrep -af cloudflared
```

重启 AI/静态服务：

```bash
TM_STATIC_ROOT="$PWD/dist" nohup bash tools/serve.sh > /tmp/tm-serve.log 2>&1 &
```

### 入口

- 本地：`http://127.0.0.1:8765/`
- 公网 Quick Tunnel：地址不固定，`pgrep -af cloudflared` 后从日志读取；重启 cloudflared 会换地址。
- GitHub Pages：`https://wck3069.github.io/Theoretical-Mechanics/`

Basic Auth、AI key、模型配置在 `~/.config/tm-ai.env`，**不要提交到仓库**。

### 静态导出 / Pages

```bash
bash tools/export_static.sh          # 输出 dist/
bash tools/publish_pages.sh          # 强制更新 gh-pages
```

`export_static.sh` 现在复制：

```bash
cp -r "$ROOT/chapters" "$OUT/chapters"
cp -r "$ROOT/hydrogen" "$OUT/hydrogen"
mkdir -p "$OUT/assets"
cp -r "$ROOT/assets/textures" "$OUT/assets/textures"
```

导出目录约 4.5M，不含任何 `.jpg`。

## 7. 验证命令与结果

```bash
cd /home/wck/Theoretical-Mechanics
/home/wck/.venv-tm/bin/python tools/check_html.py index.html modules/*/index.html chapters/*/index.html hydrogen/*.html
python3 tools/verify_selftest.py
python3 tools/layout_qa.py --viewport 1440x900 --viewport 390x844 index.html hydrogen/index.html hydrogen/sim.html
```

本轮结果：

- `check_html`：20 个页面（首页 + 9 模块 + 7 章节 + 2 氢原子页）全部 6/6 通过。
- `verify_selftest`：11/11 通过。9 个模块中 `00-binet` 无自检契约 SKIP；氢原子 14/14 PASS（归一化 + 节点数）。
- `layout_qa`：6/6 通过（1440×900 与 390×844）。
- 本地链接/资源检查（一次性脚本）：155 个相对引用，0 缺失。
- 无头截图：`/tmp/tm-shots/radial-1440b.png`、`radial-390b.png`、`hydro-1440.png`、`home-webp.png`（临时文件，不提交）。

## 8. 本轮提交

```text
d991979 feat(home): rebuild the star map around seven chapters with textured planets
9dde09d feat(hydrogen): split hydrogen into a standalone topic with radial wavefunction plots
09b0c09 fix(M5): drag the ladder to set theta and land at theta=0
a7e1a59 fix(M1): fade orbit trail over the measured orbital period
83392f6 fix(M7): compare shell and solid potentials; clean up beetle angle overlays
```

## 9. 已知问题 / 下一步建议

1. **AI 仍按 9 个模块工作**
   - `tools/ai_server.py` 与离线 KB 仍是 M0–M8 说法；氢原子未进入检索索引。
   - 首页/星表已是七章 + 独立专题；AI 的泛问题菜单可能仍列 9 个模块。
   - 若要统一：把 AI 章节索引改成七章 + 氢原子专题，同时保留 `[M#]` 引用到子模块。

2. **章节页是手写 HTML**
   - 7 个 `chapters/*/index.html` 直接写入，没有生成器；修改需直接改 HTML。
   - 后续可补 `tools/build_chapters.py` 统一导航与卡片。

3. **模块页导航仍走 M0–M8 链**
   - 9 个模块页内的 `CHAPTERS` 数组仍以 `09-hydrogen` 结尾，指向重定向页；`08-kinematics` 的“下一章”会跳到氢原子 sim。
   - 若要与七章统一，需要改所有模块页的 `CHAPTERS`，或引入章节级导航。

4. **氢原子只覆盖 n ≤ 3**
   - 径向图与 3D 电子云都只有 1s…3d。
   - 加 n=4 需补 R_40/R_41/R_42/R_43 并跑归一化自检。

5. **行星自转比例很快**
   - 已整体放慢 10 倍，木星/土星/天王星仍很快，这是真实自转/公转比导致的；只改 `updatePlanets()` 里的 `0.1` 即可。

6. **性能**
   - 首页 30fps / DPR 1.25；低端机可再降到 20fps，或行星纹理只在 hover 时绘制。
   - 2500 帧检查中 `sprites/bursts/trails/stars` 稳定，无 JS 内存泄漏迹象。

7. **太阳拖动与缩放的交互**
   - `resize` 会把 `starCenter` 重置到初始位置；若希望拖动后不回弹，需要保留拖动位置。

8. **Pages 与 Quick Tunnel**
   - Quick Tunnel 地址临时；GitHub Pages 是静态站，AI 只有离线检索；完整 AI 在本地/公网隧道。
   - 氢原子页在 Pages 上是纯静态交互，不依赖 AI 端点。

9. **氢原子不在星图**
   - 这是有意设计（独立专题，不占 C1–C7）。若想变成第 8 颗行星，需要新增海王星纹理并重排星图数组。

## 10. 关键文件

- `index.html`：首页、七章星图、行星纹理、太阳、缩放、拖动、星空。
- `chapters/01-particle/index.html` … `chapters/07-hamiltonian/index.html`：七章总览。
- `hydrogen/index.html`：氢原子专题导读。
- `hydrogen/sim.html`：3D 电子云 + 径向波函数/能级图 + 自检。
- `modules/09-hydrogen/index.html`：旧路径重定向到 `hydrogen/sim.html`。
- `modules/00-binet` … `modules/08-kinematics`：M0–M8 子模块。
- `modules/01-effective-potential/index.html`：M1 周期尾迹。
- `modules/05-virtual-work/index.html`：M5 梯子拖动/落地。
- `assets/textures/`：8 张 WebP 纹理 + `LICENSE.txt`。
- `tools/export_static.sh`、`tools/publish_pages.sh`、`tools/check_html.py`、`tools/verify_selftest.py`、`tools/layout_qa.py`、`tools/ai_server.py`。
- `~/.config/tm-ai.env`：AI key、Basic Auth、模型配置（不提交）。

## 11. 新对话建议开场

> 读取 `/home/wck/Theoretical-Mechanics/HANDOFF.md`，先检查 `git status` 和最近提交。当前站点为七章 + 9 模块 + 氢原子独立专题 `hydrogen/`，纹理已转 WebP 并提交。先不要改代码，告诉我你看到的未提交文件、Pages 部署状态，以及氢原子自检是否仍然通过。
