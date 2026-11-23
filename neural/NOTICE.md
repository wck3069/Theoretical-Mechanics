# 第三方视觉语言说明 / Attribution

本目录（`neural/`）的页面为原创实现：路由、状态机、布局与渲染代码均由本项目自行编写，
未复制任何第三方项目的源代码或媒体素材。

视觉语言（中央光球 + 水母状模块 + 触须展开为内容节点 + 右侧详情面板）参考并致敬：

- **neural-creator-dashboard** — <https://github.com/luoluo-121/neural-creator-dashboard>
  - 作者：luoluo-121
  - 许可：PolyForm Noncommercial License 1.0.0（仅限非商业用途）
  - 本项目仅借鉴其**视觉与交互概念**（光球呼吸、水母模块、伞状触须展开、面板层级），
    配色改为本站深空蓝主题；未使用其代码或示例数据。

## 媒体素材说明 / Media note（2026-11-10 更新）

曾直接取自上述仓库的实拍素材（`orb.mp4/jpg`、`jellyfish.mp4/jpg`）已全部下线删除，
水母实拍层渲染代码同步移除（`buildJellyLayer` 保留为 no-op）。`neural/` 现不含任何
第三方媒体文件；历史素材可在 git 历史中找回（`git log -- neural/media`）。

本站点用于教学与非商业目的。若需将该视觉方案用于商业用途，请自行评估并取得相应授权。
