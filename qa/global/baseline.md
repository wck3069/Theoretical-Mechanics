# P0-T1 基线（资产盘点与基线固化）

日期：2026-10-26 ｜ 执行机：Linux ｜ 台账：P0-T1

## 1. 工具链事实（Linux）

| 项 | 事实 |
|---|---|
| LaTeX | TeX Live 2023/Debian：`XeTeX 3.141592653-2.6-0.999995`、`Latexmk 4.83`、`ctex`/`xeCJK`、Noto CJK 字体 |
| 编译验证 | `latexmk -xelatex -interaction=nonstopmode binet.tex` 退出码 0，PDF 5 页 |
| PDF 处理 | `~/.venv-tm/`：PyMuPDF（`import pymupdf`，`fitz` 别名已弃用）、numpy、git-filter-repo |
| 截图 | Google Chrome 154.0.8037.92，`--headless=new --screenshot` |
| Git | `git` + `gh`（已登录 `wck3069`），remote `origin` → `https://github.com/wck3069/Theoretical-Mechanics`（`main`） |
| Node.js | **不存在**（`node`/`npm`/`npx`/`bun` 均缺）；JS 语法检查替代方案在 P0-T2 决定，见 `qa/global/toolchain.md` |

## 2. 现有三件套（基线，只读至 P9）

| 文件 | SHA256 | 备注 |
|---|---|---|
| `binet.tex` | `23d46526181f9f09d0640bd33986fe94a7f75aec9053f7b02b515cdaab882cf3` | LaTeX 样板 |
| `binet.pdf` | `049b7773b81b69cc1b8a3c29cff1a8f15bce9ab9d20df7fe8f3b159f3038ac53` | 5 页 |
| `index.html` | `9c668494d3d8c001f8c647a86d67cf83ad026d8c878fa1ea60041f5268f1578b` | 交互模拟样板 |

## 3. 作业 PDF（知识点来源，仅本地，不入库）

| 文件 | 页数 | SHA256 |
|---|---|---|
| `作业/作业-1.pdf` | 2 | `de73cb2186dbe5ca312f2768e1a7a8068484d3b45f68854f4d3ad6032256e39b` |
| `作业/作业-2.pdf` | 2 | `c0585dd71aa48e395bddcdb260748b31cb7f1df68ca1850b6a8e09e60936034f` |
| `作业/作业-3.pdf` | 1 | `896dc19f10005de56469bbe6c9b34fd1f3fa2425b067531f975126f707847be2` |
| `作业/作业-4.pdf` | 1 | `747f159813733e4c66ef1fa413fb72d75a00d100b88ef084acc0a1e92aec24d3` |
| `作业/作业-5.pdf` | 1 | `045da3aaab37671c8532d0c4d4f87a6fd89a9a1b051f1893f3aec2210d44baad` |
| `作业/作业-6.pdf` | 1 | `44c1f0c17e42b377112135f934b3da1dc32ef79cc7dc3ec464eff1d18d09e355` |
| `作业/作业-7.pdf` | 2 | `6ba2908c42ada4874146e0ab764f21d88fe8e27a4d129ce7348371a6ea01c39e` |
| `作业/作业4-第5题-两体问题.pdf` | 1 | `1b914c40038e33cc0d87c113cd0327ea9eb0cf2c65a8b700a2634a46cf97555f` |

合计 8 份、11 页。仓库内 `作业/` 哈希与本地备份 `~/tm-assign-backup/` 逐一比对**完全一致**：只读边界成立，未被修改。

## 4. `index.html` 截图基线

截图命令：

```bash
google-chrome --headless=new --disable-gpu --no-sandbox --hide-scrollbars \
  --virtual-time-budget=6000 --window-size=<宽>,<高> \
  --screenshot=qa/global/<文件名> \
  'file:///home/wck/Theoretical-Mechanics/index.html'
```

| 文件 | 视口 | 结果 |
|---|---|---|
| `qa/global/baseline-index-1440.png` | 1440×900 | PNG 正常（7159 种颜色，非空白；深色主题正常渲染） |
| `qa/global/baseline-index-360.png` | 360×640 | PNG 正常（6970 种颜色，非空白） |

DOM 快检（`--dump-dom`）：23449 字符；`canvas` ×3、`requestAnimationFrame` ×2、`<h1>` ×1、"轨道" ×11。

## 5. 结论

- 三件套与 8 份作业的哈希/页数已固化；
- `作业/` 只读边界确认（哈希 == 备份）；
- 截图基线落盘于 `qa/global/`。
- 遗留：本机无 Node.js，P0-T2 决定 `node --check` 替代方案并记录到 `qa/global/toolchain.md`。
