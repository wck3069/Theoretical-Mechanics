# 星图链接失效修复（2026-11-23 夜）

## 症状（用户报告）

"打开网页次数多后星图链接不可用"——首页星图行星点击逐渐失效。

## 根因（复现循环证实，非猜测）

`index.html` `startPlanetFly()` 的高清纹理等待路径存在**重入竞态**：

1. 纹理未加载时注册 3 个恢复触发器（load / error / 700ms 超时），每个都直接
   重入 `startPlanetFly`，而该函数**没有 `state.flying` 守卫**。
2. 慢纹理（CF 隧道/首访常见）→ 多代触发器先后触发 → 一次点击创建 **2–6 个
   飞行+iframe**（实测 max=6）；`state.flying` 指向最后一个，其余成孤儿。
3. 门户打开后按返回：`popstate` 只删 `querySelector('.tm-portal')`（**第一个**
   = 孤儿），真正盖屏的可见 iframe（opacity 1, pointer-events auto）留下；
   `portal-open` 类已移除 → 后续 popstate 早退守卫永不清理 →
   **星图被永久盖住，点击全部落在 iframe 上** = 用户症状。
4. 独立并发路径：iframe 预载 >2.5s 触发 `finishFlight` 整页跳转回退，
   跳转前不清理 `is-flying`（CSS 隐藏全部 UI）/iframe/飞行缩放 →
   真实浏览器 bfcache 返回时冻结脏状态（复现循环中 bfcacheMarker=42 存活 + dirty）。

## 复现循环（修复前 RED，修复后 GREEN）

`tools/qa-home/star_map_loop.py`（永久回归资产）：
- 本地服务器对 `Sec-Fetch-Dest: iframe` 的 neural 请求延迟 5s（强制回退路径）、
  对 `/textures/hi/` 图片延迟 1.2s（强制纹理等待竞态）——确定性触发，无需真实慢网。
- 合成 click 网格扫描启动飞行；断言：
  A2 bfcache 冻结（marker 存活+脏状态）、A3 iframe 计数 ≤1、A4 返回后残留=0。
- 修复前：fallback 模式 RED（A3 max=3、A2/A4 dirty），portal 模式 RED
  （4 iframe→返回剩 3，逐轮累积）。
- 修复后：两模式 ×3 轮 **GREEN**（返回后 iframes=0、UI 正常、可再次飞行）。

## 修复（index.html，四处最小改动）

1. `startPlanetFly` 顶部加 `if(state.flying) return;` —— 掐断重入竞态。
2. 创建新 iframe 前移除所有旧 `.tm-portal` —— 孤儿清零。
3. `popstate`：`querySelectorAll` 全量移除；守卫放宽为 `!portal-open && !pf`
   （飞行早期按返回也取消飞行并复位，用 `pf.pre*` 兜底恢复）。
4. `finishFlight`：跳转前全量清理（iframe/类/缩放/中心/标题/轨迹）——
   bfcache 冻结的文档是干净的。
5. 新增 `pageshow`（persisted）兜底：bfcache 返回时重置全部飞行/门户状态。

## 验证

- 回归循环两模式 GREEN（见上）。
- `check_html index.html` 6/6；dist 已同步（tm-static-sync）。
- 全量 `verify_selftest`：**23/23 模块通过**（含本轮新增 M27–M30）。

## 同轮完成：M29/M30 集成（第二波）

- M29 勒让德变换与罗斯约化（modules/22-legendre-routh，C6）：自测 **15/15**。
- M30 双曲运动与恒固有加速度（modules/23-hyperbolic-motion，C7）：自测 **20/20**。
- 注册表/章节卡/方程表/关键词/离线 FAQ 映射同步；首页计数 25→**27**。
- KB 合并（merge_kb_drafts.py）：**32 模块 / 329 chunks / 132,572 字**。
- 新边 L41–L47（含 Atwood 拉格朗日vs哈密顿 L44、恒加速度相对论vs牛顿 L46 等
  同题异法/极限对照）：**47 边 / 20 跨章**。
- 门禁：check_html 4×6/6；check_links **61 页 / 605 链 / 0 缺失**；
  tm-ai 重启 kb_chunks=329，M29/M30 检索命中；ch06/ch07 渲染探针吻合数据。
