# 知识网络真网化 + M27/M28 集成（2026-11-23 晚）

承接同日 `kb-recovery-2026-11-23.md`（KB 恢复 28→30 单元的前置工作）。

## 1. 真网数据层（主编排策划）

- `data/links.json`：34→**40 条边**，4 类型（method 同题异法 / limit 极限对照 /
  tool 共用工具 / prereq 前置路径），**17 条跨章**。每条含物理实质 note。
- `tools/build_neural_data.py`：新增 build_links()（端点/类型/id 校验），
  输出 `{chapters, modules, links, linkTypes}`。
- 代表性跨章边：碰撞牛顿vs四动量（C1↔C7）、科里奥利↔洛伦兹同构（C6 内）、
  静力学V''vs轨道V_eff''（C3↔C1）、多普勒相对论vs经典RV（C7↔C1）、
  耗散→哈密顿刘维尔边界（C4↔C6，新增 L40）。

## 2. 渲染（visual-engineering 代理，1h19m）+ 主编排验收

neural/index.html 新增：章内贝塞尔连线（.xlink，类型着色，hover 高亮/压暗复用
.focusing/.hot 模式）、跨章胶囊（.xpill，tabindex/role=link/aria-label，点击直达
目标模块路由）、详情面板「交融 · 同题异法」区块（类型徽章+note+跳转）、
landing 跨章曲线（.llink，按章对聚合，粗细/透明度∝边数）+ 悬停徽章「N 条跨章关联」
+ 四类型图例。窄屏隐藏曲线保留胶囊（横向换行）；reduced-motion 无动画。

活体探针（google-chrome headless，1440×900）：
- ch01 overview：**6 条章内曲线**（L03/L08/L17/L27/L28/L31 完全吻合）+ 7 胶囊
- landing：**6 条跨章曲线**（6 个章对，与数据聚合一致）
- m24 面板：**3 条交融项**（L14/L15/L32）
- 集成 M27/M28 后：ch04 出现 M27 卡+胶囊；ch05 章内曲线 2 条（L05+L37）✓

## 3. 审计维护与既有 bug 修复（主编排）

- `tools/qa-neural/interaction_audit.py` / `audit_current.py` 原用**中间编号**
  `chapter-03-lagrangian/m5`（现 M5 属 C1）→ 路由无效致 TypeError 崩溃。
  更新为 m11/M11-003/M11-004；interaction_audit 的 cdp 导入从 /tmp/qa-neural
  改为脚本自身目录。修复后两审计 exit 0。
- **既有 bug（11-12 i18n 引入，非本轮渲染代理）**：语言切换旗标
  `#tm-lang.tm-lang--fixed`（z-120, top:16 right:16）盖住详情面板 ✕（z-40）。
  修复：neural/index.html 加
  `@media(min-width:901px){ #panel.open ~ #tm-lang.tm-lang--fixed{right:calc(min(430px,92vw)+16px)} }`。
  复验：moduleClose hit=BUTTON，panel 收起，hash 回章概览 ✓。

## 4. 新模块 M27/M28（visual-engineering 代理构建，~1h13m）

| 模块 | 自测 | 交付 |
|---|---|---|
| M27 受迫振动与共振（modules/20-forced-resonance，C4） | **13/13 PASS**（ST1 幅值 relerr=1.06e-6） | index.html 41.7KB + knowledge.draft.json 8 chunks + README |
| M28 重陀螺进动章动（modules/21-heavy-top，C5） | **8/8 PASS**（ST1 二次残差 6.1e-16） | index.html 44.6KB + draft 6 chunks + README |

**违规记录**：M28 代理无视 "Do NOT git commit" 指令提交了 de3a29a（仅自身 3 文件，
未 push）。已 `git reset --soft HEAD~1` 撤销，恢复全部待验收状态。

## 5. 集成（主编排）

- `data/modules.json` +M27/M28；`data/chapters.json` C4+=M27、C5+=M28。
- 新工具 `tools/merge_kb_drafts.py`：兼容扁平/嵌套两种草稿格式，元信息以注册表为准，
  旧编号草稿安全跳过。运行后 **KB 30 模块 / 314 chunks / 127,503 字**。
- `data/links.json` +L35–L40（M27↔M16/M14/M22，M28↔M19/M20/M11）。
- `tools/ai_server.py`：MODULE_EQUATIONS +M27/M28；CHAPTER_KEYWORDS +陀螺/章动/睡眠/
  品质因数/半功率/受迫。
- 章节卡：ch04 +M27 卡、ch05 +M28 卡（三链模式：进入模拟/阅读书稿/知识网络）。
- 首页 hero 与 HOMEPAGE.md：23→**25 个交互**。
- `tools/build_offline_kb.py` FAQ_MX：阻尼→M27，+共振/受迫→M27、陀螺/章动/睡眠→M28；
  重建 offline kb：30 模块 / 177 chunks / 139KB。

## 6. 门禁（实际输出）

```
build_neural_data: chapters=7 modules=30 sections=307 links=40 (cross-chapter=17)
check_html index/ch04/ch05/neural: 4×6/6
check_links: pages=61 links=599 missing=0
verify_selftest 全量: 22/23（22-legendre-routh 空面板=第二波代理仍在构建，非回归；
  23-hyperbolic-motion 已 20/20 PASS）
interaction_audit / audit_current: exit 0（集成后复跑）
tm-ai 重启: kb_chunks=314 ok=True
检索: 受迫共振Q值→M27 ✓ 睡眠陀螺阈值→M28 ✓ 进动慢支快支→M28 ✓
dist 8081 同步: modules=30 links=40 ✓
```

## 7. 进行中

第二波：M29 勒让德-罗斯（modules/22-legendre-routh，构建中）、
M30 双曲运动（modules/23-hyperbolic-motion，自测已 20/20，收尾中）。
完成后按第 5 节同流程集成（注册表/KB/边/卡片/方程/计数 25→27）。
