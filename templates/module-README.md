<!-- 理论力学 · 交互讲义 —— README 模板（P0-T2）
     由 tools/new_module.py 复制为模块目录下的 README.md，
     并替换占位符 {{MODULE_TITLE}} / {{MODULE_SLUG}}。
     结构按 PLAN.md §4.2：作业映射、参数说明、运行方式、验收记录。 -->

# {{MODULE_TITLE}}

> 模块代号：{{MODULE_SLUG}} · 理论力学 · 交互讲义
>
> （模板占位：替换为本模块的一句话说明——讲义讲什么、交互页做什么）

## 作业映射

<!-- TODO：按 PLAN.md 第 3 节知识地图填写；来源写"作业-N QM"或"两体专题"。 -->

| 来源 | 题目 | 核心知识点 | 讲义章节 |
|---|---|---|---|
| 作业-N QM | （题面简述） | （知识点） | （note.tex 对应章节） |
| 作业-N QM | （题面简述） | （知识点） | （note.tex 对应章节） |

## 参数说明

<!-- TODO：与 index.html 的滑块一一对应；单位制在此写清（§5.3：默认无量纲化时给出有量纲示例）。 -->

| 参数 | 物理含义 | 默认值 | 范围 | 单位 |
|---|---|---|---|---|
| a | （占位：写明含义与对结果的影响） | 1.0 | 0.1–3 | （写明） |
| b | （占位） | 0.5 | 0–2 | （写明） |

URL 预设：`index.html?preset=default&a=1.0&b=0.5`（非法值自动回退默认，§5.2）。

## 运行方式

- **讲义编译**：`bash tools/build_note.sh <本模块目录>`（latexmk -xelatex，产物 note.pdf）
- **交互页面**：浏览器直接打开 `index.html`——单文件、离线可用，无需服务器
- **HTML 检查**：`/home/wck/.venv-tm/bin/python tools/check_html.py <本模块目录>/index.html`
- **自测**：`index.html?selftest=1`（§5.4：全部 PASS 才算通过，结果写入 `window.__selftest`）

## 验收记录

<!-- TODO：每条验收必须写实际命令 + 实际输出（§7.3：证据不能只写"已通过"）。 -->

| 日期 | 项目 | 命令 | 结果 |
|---|---|---|---|
| （日期） | note.tex 编译 | `bash tools/build_note.sh …` | （退出码 / PDF 页数） |
| （日期） | HTML 检查 | `/home/wck/.venv-tm/bin/python tools/check_html.py …` | （PASS/FAIL 摘要） |
| （日期） | selftest | `index.html?selftest=1` | （passed/failed 计数） |
| （日期） | 三档视口截图 | `google-chrome --headless=new …` | （截图路径） |

## 已知限制

<!-- TODO：写明模型适用范围、数值方法的已知问题（§7.4）。 -->

- （占位：如"奇点附近步长截断""小角度近似适用条件""参数超出范围时的行为"）
