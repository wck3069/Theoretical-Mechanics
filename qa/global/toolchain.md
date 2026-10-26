# 全局工具链记录（qa/global/toolchain.md）

> P0-T2 产物（2026-10-26）。记录本机已实测验证的工具链、命令与替代方案决策。
> 后续所有任务的编译、检查、截图一律以本文为准；版本号均为实测输出。

## 1. TeX Live（讲义编译）

| 组件 | 版本（实测） |
|---|---|
| XeTeX | `XeTeX 3.141592653-2.6-0.999995 (TeX Live 2023/Debian)` |
| Latexmk | `Latexmk, John Collins, 31 Jan. 2024. Version 4.83` |
| ctex / xeCJK | 随 TeX Live 2023 提供，Noto CJK 字体可用（PLAN.md §2.2） |

已验证编译命令（P0-T1 基线 `binet.tex` 与 P0-T2 模板自测均通过，退出码 0）：

```bash
latexmk -xelatex -interaction=nonstopmode note.tex
```

统一入口：`bash tools/build_note.sh <module-dir>`——编译后自动 `latexmk -c`
清理辅助文件（保留 note.pdf），传播并打印退出码。

## 2. 浏览器（截图 / 交互 QA）

| 组件 | 版本（实测） |
|---|---|
| Google Chrome | `Google Chrome 154.0.8037.92` |

三档视口截图方法（§7.3：desktop 1440×900 / tablet 768×1024 / mobile 360×640）：

```bash
google-chrome --headless=new --disable-gpu --no-sandbox \
  --window-size=1440,900 --screenshot=<out.png> \
  "file:///<abs-path>/index.html?preset=..."
```

（需要等待渲染/自测时加 `--virtual-time-budget=2000`；DOM 检查用 `--dump-dom`。）

## 3. Python venv

| 项 | 值（实测） |
|---|---|
| 解释器 | `/home/wck/.venv-tm/bin/python`（Python 3.12.3） |
| 依赖 | pymupdf 2.0、numpy 2.5.4、esprima 4.0.1 |
| 说明 | 系统 pip 受 PEP 668 限制，一律用 venv（PLAN.md §2.1） |

## 4. 决策记录：JS 语法检查用 esprima（替代 node --check）

**实测**：本机 `node`、`npm`、`npx`、`bun` 均不存在（`which` 无输出），且按任务约束
不安装任何软件（PLAN.md §2.2、§11 风险表）。

**决策**：§7.2 的"内联 JavaScript 通过 `node --check`"与 §7.3 的
"JS 语法检查输出（`node --check` **或记录的替代方案**）"按后者执行——
统一改用 **esprima 4.0.1（~/.venv-tm）**，由 `tools/check_html.py` 对每个内联
`<script>` 块做 `esprima.parseScript` 语法检查，任何解析错误即 FAIL、退出码非 0。

- 依据：PLAN.md §5.5"Node 仅用于 node --check"+ §11"失败则用 Python esprima；
  结论记入 qa/global/toolchain.md"。
- 影响范围：所有模块 T2 证据（`qa/T2-sim.md`）记录 `check_html.py` 的实际输出，
  不再出现 `node --check`。
- 模板约束：模板与模块的内联 JS 限用 esprima 4.0.1 可解析的语法
  （ES2017 及以下；不用可选链 `?.`、空值合并 `??` 等 ES2020 语法）。

## 5. 命令速查

| 用途 | 命令 |
|---|---|
| 生成模块骨架 | `/home/wck/.venv-tm/bin/python tools/new_module.py <slug> --out <dir>` |
| 编译讲义 | `bash tools/build_note.sh <module-dir>` |
| HTML 检查 | `/home/wck/.venv-tm/bin/python tools/check_html.py <file.html>` |
| 截图 | `google-chrome --headless=new --window-size=W,H --screenshot=<png> file:///<abs-path>` |
| PDF 页数/文本 | `/home/wck/.venv-tm/bin/python -c "import pymupdf; ..."` |

## 6. P0-T2 自测记录（2026-10-26）

用模板生成自测模块并全流程验证（完整命令与输出见 P0-T2 任务报告）：

```text
/home/wck/.venv-tm/bin/python tools/new_module.py _t2-selftest --out /tmp/t2-selftest
bash tools/build_note.sh /tmp/t2-selftest          # latexmk 退出码 0，note.pdf 生成
/home/wck/.venv-tm/bin/python tools/check_html.py templates/index.html            # 6/6 PASS
/home/wck/.venv-tm/bin/python tools/check_html.py /tmp/t2-selftest/index.html     # 6/6 PASS
google-chrome --headless=new --screenshot ... "file:///tmp/t2-selftest/index.html?selftest=1"
```

结果：骨架生成 ✓、编译退出码 0 ✓、HTML 检查 6/6 PASS ✓、
`?selftest=1` 面板 3/3 PASS（占位断言）✓、截图方法可用 ✓。
