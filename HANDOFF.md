# 理论力学交互讲义 · 交接记录

日期：2026-11-01  
项目：`/home/wck/Theoretical-Mechanics`  
标题：**理论力学：从质点到哈密顿**

## 1. 当前状态

站点结构：**七章 + 12 个可交互模块（M0–M11）**，不含氢原子。

七章与模块映射：

| 章 | 名称 | 模块 |
|---|---|---|
| 1 | 质点力学 | M0 比奈、M1 有效势、M2 散射 |
| 2 | 质点系力学 | M3 两体、M6 碰撞/变质量 |
| 3 | 变分法 | M4 变分原理 |
| 4 | 拉格朗日力学 | M5 虚功、M9 Atwood、M10 耦合系统、M11 旋转/磁场 |
| 5 | 小振动 | M8 运动学/非线性振动 |
| 6 | 刚体力学 | M7 刚体 |
| 7 | 哈密顿力学 | 暂无模块，章节页为导读/建设中 |

- 首页星图有 **7 颗行星**，点击进入 `chapters/01-particle` … `chapters/07-hamiltonian`。
- M0–M11 模块页均保留，作为章节下的子模块。
- 氢原子**不属于本站**。它已拆为独立站点：
  - 目录：`/home/wck/Quantum-Mechanics`
  - 仓库：`wck3069/Quantum-Mechanics`
  - Pages：`https://wck3069.github.io/Quantum-Mechanics/`
  - 本站不再保留 `hydrogen/`、`modules/09-hydrogen` 或任何指向它的链接。

## 2. 最近提交

```text
1cac9e8 feat(chapters): add printable chapter books with cover, TOC and bookmarks
249e7b3 feat(manuscripts): add handwritten-note OCR versions to chapters 1-3
c64f428 feat(M9-M11): visualize the Lagrangian problems from assignment 8
a7f526e refactor: move hydrogen out of the theoretical-mechanics site
8236aaa docs: update handoff for the hydrogen topic, webp textures and new structure
d991979 feat(home): rebuild the star map around seven chapters with textured planets
9dde09d feat(hydrogen): split hydrogen into a standalone topic with radial wavefunction plots
09b0c09 fix(M5): drag the ladder to set theta and land at theta=0
a7e1a59 fix(M1): fade orbit trail over the measured orbital period
83392f6 fix(M7): compare shell and solid potentials; clean up beetle angle overlays
```

`9dde09d` 与 `8236aaa` 里的氢原子内容已在 `a7f526e` 移除，历史仍保留在 git 中。

## 3. 首页 / 星图

### 3.1 数据

- `window.TM_MODULES`：7 个章节对象（C1–C7），`sim` 指向章节页。
- `window.TM_SUBMODULES`：12 个 M0–M11 模块数据，用于兼容/来源链接。
- 星图、星表、筛选、搜索围绕 7 个章节；行星点击直接进入章节页。
- hero 计数：7 章 / 8 次作业 / 12 个模块。
- `showDetail()` 仍存在但星图基本不用；`TM_SUBMODULES` 保留。

### 3.2 行星纹理

来源：Solar System Scope 2K 纹理，本地 `assets/textures/`，CC BY 4.0。全部为 **WebP (quality 82)**。

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
- `tools/ai_server.py` 的 MIME 表含 `.webp: image/webp`。

## 5. 其他提交的修复

### M1 有效势

`modules/01-effective-potential/index.html`：

- 轨迹尾迹按**实测轨道周期**衰减（当前周期的 3.5 倍），不再固定长度。
- 通过 θ 穿越 2π 的间隔测量周期；未测到前用线性化频率或 L/r² 估计。
- `initState()` / `placeAt()` 重置 `orbitTMeasured`、`lastThCross`、`lastThT`。

### M5 虚功/梯子

`modules/05-virtual-work/index.html`：

- 鼠标/触控可直接拖动梯子改变 θ；拖动时暂停模拟，松手后按新角度重新判断打滑。
- 落地终态 θ=0 水平，删除落地前 0.03/0.003 rad 的提前吸附和回弹。
- 慢速动画按 `dt*speed` 拆小步 RK4，避免低速抖动。

### 作业-8 模块（M9–M11）

`modules/09-atwood-pulley`、`modules/10-coupled-systems`、`modules/11-rotation-and-field` 是作业-8 的可视化，全部挂在第 4 章：

- **M9 Atwood**：以 $m_2$ 向下位移为广义坐标，$a=(m_2-m_1)g/(m_1+m_2+I/R^2)$，
  $T_1=m_1(g+a)$、$T_2=m_2(g-a)$；HUD 同时给出张力差与滑轮角加速度。
- **M10 耦合系统**：页内切换三个场景——斜面滑块（$a_{\rm rel}$、$a_X$、$\eta=2/9$）、
  弹簧摆（$r_0$、$\omega_r$、$\omega_\theta$）、小车单摆（$p_X=0$、$\omega$）。
- **M11 旋转与磁场**：旋转圆环（$\Omega_c$、$\theta_{\rm eq}$、稳定性、雅可比积分 $\mathcal E$ 与 $E_{\rm mech}$），
  磁场回旋（$Q_x$、$Q_y$、规范动量、回旋圆心）。
- 每页都有 `?selftest=1` 硬断言；`?scene=...` 可直接打开指定场景（M10/M11）。
- 三份 `note.tex` 由 `tools/build_note.sh` 编译；`qa/numeric_check.py` 给出数值证据。

### 手写手稿（网页代码版）

四份扫描手稿已转为网站内的 HTML 正文，**不再以 PDF 形式呈现**；公式与图都是代码：

| 章节 | 页面 | 内容 |
|---|---|---|
| 第 1 章 | `chapters/01-particle/manuscripts/hw1.html` | 作业一·第一章 26 页；6 张图 TikZ→SVG |
| 第 1 章 | `chapters/01-particle/manuscripts/intro.html` | 绪论与第一章笔记 49 页 |
| 第 2 章 | `chapters/02-system/manuscripts/chapter2.html` | 第二章笔记 59 页 |
| 第 3 章 | `chapters/03-variational/manuscripts/variational.html` | 变分原理 27 页 |

- 公式：本地 `assets/mathjax/tex-svg.js`（离线，无 CDN）；正文里的 `$...$`、`\[...\]` 由 MathJax 直接渲染。
- 图：TikZ 图编译为 SVG；截图裁剪用 `vtracer` 转矢量 SVG。
- **图像审核与重绘**：72 张 SVG 逐张视觉审核；37 张失败图按上下文重新生成 TikZ 并复审通过，最终 50 张保留、22 张不可读/误检图移除；页面顶部有说明。
- 交互链接：按章节在顶部与相关小节插入 M0–M11 的「交互演示」入口。
- 样式：`assets/manuscript.css`。
- 物理修正：作业一 9 处、变分原理 4 处、第二章 8 处、绪论 2 处；记录在同目录 `CORRECTIONS.md` / `INTRO-CORRECTIONS.md`。

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

- 本地：`http://127.0.0.1:8765/`（Basic Auth）
- 公网 Quick Tunnel：地址不固定，重启 cloudflared 会变
- GitHub Pages：`https://wck3069.github.io/Theoretical-Mechanics/`

Basic Auth、AI key、模型配置在 `~/.config/tm-ai.env`，**不要提交到仓库**。

### 静态导出 / Pages

```bash
bash tools/export_static.sh          # 输出 dist/
bash tools/publish_pages.sh          # 强制更新 gh-pages
```

`export_static.sh` 复制：

```bash
cp -r "$ROOT/modules" "$OUT/modules"
cp -r "$ROOT/chapters" "$OUT/chapters"
mkdir -p "$OUT/assets"
cp -r "$ROOT/assets/textures" "$OUT/assets/textures"
```

导出目录约 5.0M，不含 `.jpg`，也不含氢原子。

## 7. 验证命令与结果

```bash
cd /home/wck/Theoretical-Mechanics
/home/wck/.venv-tm/bin/python tools/check_html.py index.html modules/*/index.html chapters/*/index.html
python3 tools/verify_selftest.py
python3 tools/layout_qa.py --viewport 1440x900 --viewport 390x844 index.html modules/08-kinematics/index.html chapters/01-particle/index.html
```

本轮结果：

- `check_html`：20 个页面（首页 + 12 模块 + 7 章节）全部 6/6 通过。
- `verify_selftest`：12/12 通过（`00-binet` 无自检契约 SKIP）。M9 10/10、M10 11/11、M11 12/12。
- `layout_qa`：10/10 通过（首页、第 4 章、M9–M11，各 1440×900 与 390×844）。
- 本地链接/资源检查（一次性脚本）：157 个相对引用，0 缺失。
- 三份 note.pdf：M9 4 页、M10 5 页、M11 4 页。

## 8. 已知问题 / 下一步建议

1. **AI 仍按 9 个模块工作**
   - `tools/ai_server.py` 与离线 KB 仍是 M0–M8 说法。
   - 首页/星表是七章；AI 的泛问题菜单可能仍列 9 个模块。
   - 若要统一：把 AI 章节索引改成七章，同时保留 `[M#]` 引用到子模块。

2. **章节页是手写 HTML**
   - 7 个 `chapters/*/index.html` 直接写入，没有生成器；修改需直接改 HTML。
   - 后续可补 `tools/build_chapters.py` 统一导航与卡片。

3. **模块页导航仍走 M0–M11 链**
   - 11 个模块页内的 `CHAPTERS` 数组已更新为 M0–M11；M11 的“下一章”回到星图。
   - 若要与七章统一，需要改所有模块页的 `CHAPTERS`，或引入章节级导航。

4. **行星自转比例很快**
   - 已整体放慢 10 倍，木星/土星/天王星仍很快，这是真实自转/公转比导致的；只改 `updatePlanets()` 里的 `0.1` 即可。

5. **性能**
   - 首页 30fps / DPR 1.25；低端机可再降到 20fps，或行星纹理只在 hover 时绘制。
   - 2500 帧检查中 `sprites/bursts/trails/stars` 稳定，无 JS 内存泄漏迹象。

6. **太阳拖动与缩放的交互**
   - `resize` 会把 `starCenter` 重置到初始位置；若希望拖动后不回弹，需要保留拖动位置。

7. **Pages 与 Quick Tunnel**
   - Quick Tunnel 地址临时；GitHub Pages 是静态站，AI 只有离线检索；完整 AI 在本地/公网隧道。

8. **氢原子在另一个仓库**
   - 本站不再维护氢原子。需要改电子云、径向波函数或光谱，请去 `/home/wck/Quantum-Mechanics`。
   - 两边视觉风格不同，且没有共享代码；有意为之，避免理论力学站被量子内容拖重。

## 9. 关键文件

- `index.html`：首页、七章星图、行星纹理、太阳、缩放、拖动、星空。
- `chapters/01-particle/index.html` … `chapters/07-hamiltonian/index.html`：七章总览。
- `chapters/0{1,2,3}-*/manuscripts/*.html`：四份手写手稿的网页代码版；`figs/` 为 SVG 图。
- `assets/manuscript.css`、`assets/mathjax/tex-svg.js`：手稿页样式与离线公式渲染。
- `modules/00-binet` … `modules/08-kinematics`：M0–M8 子模块。
- `modules/09-atwood-pulley`：M9 有转动惯量的 Atwood 机（作业-8 Q1）。
- `modules/10-coupled-systems`：M10 斜面滑块 + 弹簧摆 + 小车单摆（作业-8 Q3/Q4/Q5）。
- `modules/11-rotation-and-field`：M11 旋转圆环 + 磁场回旋（作业-8 Q5/Q6）。
- `modules/01-effective-potential/index.html`：M1 周期尾迹。
- `modules/05-virtual-work/index.html`：M5 梯子拖动/落地。
- `assets/textures/`：8 张 WebP 纹理 + `LICENSE.txt`。
- `tools/export_static.sh`、`tools/publish_pages.sh`、`tools/check_html.py`、`tools/verify_selftest.py`、`tools/layout_qa.py`、`tools/ai_server.py`。
- `~/.config/tm-ai.env`：AI key、Basic Auth、模型配置（不提交）。

## 10. 新对话建议开场

> 读取 `/home/wck/Theoretical-Mechanics/HANDOFF.md`，先检查 `git status` 和最近提交。当前站点为七章 + 12 模块，氢原子已独立到 `../Quantum-Mechanics`。先不要改代码，告诉我你看到的未提交文件、Pages 部署状态，以及 `verify_selftest` 是否仍然通过。
