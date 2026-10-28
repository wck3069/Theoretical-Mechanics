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

## AI 模型路由（长期平衡态，2026-10-28 定稿）

### 本地 Maya（强、慢、单并发）
- 端点 `http://127.0.0.1:8080/v1`，模型 id `deepseek-v4.1-flash`（DeepSeek-V4.1-Flash-1017，Maya-S IQ2_XXS，339.5GB）
- 实测：prefill **331 tok/s**，decode **3.6–6 tok/s**，24GB 显存（RTX 5090 D v2）+ 503GB RAM
- 固定参数（勿改）：`--context 32768 --drafting off --vram-reserve-mib 512`
  - 曾用 262144 上下文 → 显存被 KV 占满，专家只能读盘 → **0 tok/s**，已弃用
- **默认 `reasoning_effort` 必须是 `none`/`low`**：high 会吃掉全部 max_tokens 预算（实测 12000 token 全用于 thinking，无 HTML 输出）
- **单并发**：一个长生成会阻塞后续请求 → 长任务一律后台跑，交互问答走云端
- 启停/体检：`~/bin/maya-start`、`~/bin/maya-stop`、`~/bin/ai-health`

### 云端免费（快、但会时段性不可用）
- `opencode-go/beam-free`：唯一稳定可用的
- `opencode/deepseek-v4.1-flash-free`、`opencode/nemotron-3-ultra-free`：多次返回 `Model is unavailable`

### 分工表（omo.jsonc / opencode.json 已写入）
| 场景 | 模型 | 理由 |
|---|---|---|
| quick / unspecified-* / writing / artistry / deep-low | beam-free | 1–3s，成本零 |
| deep-high / ultrabrain / oracle / metis | **maya/deepseek-v4.1-flash** | 长上下文、强推理；慢，后台执行 |
| visual-engineering / multimodal-looker | **maya/deepseek-v4.1-flash** | 支持图像输入 |
| 所有角色的兜底 | beam-free（Maya 不可用）/ maya（云端不可用） | 双向前提 |

### 执行规则（避免再踩坑）
1. 需要长文本生成（>3k token）→ 交 Maya，`reasoning_effort:none`，`max_tokens≥12000`，后台运行并轮询日志。
2. 需要"边改边看"的小步迭代 → 交云端 beam-free，不占本地单槽。
3. 提交前一律跑 `tools/check_html.py` + `?selftest=1`，模型产出不作验收依据。
4. Maya 忙时 `~/bin/ai-health` 的 probe 会超时——这是正常排队，不是故障。

## 2026-10-28 本地模型更替（Maya → Ollama）

### 删除
- Maya / DeepSeek-V4.1-Flash-1017（Maya-S，339.5GB）：`~/maya-models`、`~/project-maya` 已删除，释放 325GB，显存释放
- 删除原因：24GB 显存跑 748B MoE 只能读盘 → 解码 3.6–6 tok/s、单并发阻塞、340GB 磁盘 + 160GB 常驻内存，性价比低

### strata / 千问 3.8 现状：**无法恢复**
- `~/.local/bin/strata` 为断链（指向已删除的 `~/.local/share/strata/terminal/current/bin/strata`）
- 无安装包、无 shell 历史安装命令、无备份；两者此前按指示删除
- 恢复需原始安装包/下载源（strata 账号或安装脚本）

### 当前本地替代：Ollama `qwen3:32b-ctx8k`
| 项 | 值 |
|---|---|
| 规格 | Qwen3-32B Q4_K_M，32.8B dense |
| 显存 | 22GB / **100% GPU** |
| 上下文 | 8192（Modelfile 固定） |
| 解码 | **55.6 tok/s**（实测 111 token / 2.0s） |
| 探针 | `OK` in 451ms |
| 关思考 | 客户端需带 `reasoning_effort:"none"`，否则 content 为空（只出 reasoning 字段） |

### 路由（opencode.json / omo.jsonc 已改）
- `deep-high` / `ultrabrain` / `oracle` / `metis` / `visual-engineering` / `multimodal-looker` → `ollama/qwen3:32b-ctx8k`（`reasoningEffort: none`）
- `quick` / `explore` / `librarian` / `general` / `writing` / `deep-low` → `opencode-go/beam-free`
- 双向兜底：本地/云端任一不可用即切换
- 运维：`~/bin/ai-health`（本地模型 + 路由自检）

## 2026-10-28 千问 3.8 恢复上线（strata 重装）

### 恢复方式（可复现）
```bash
curl -fsSL https://github.com/Niko1221/Strata/releases/latest/download/install.sh -o install.sh && sh install.sh   # 用户级，SHA+签名校验
strata launch --model iq3_s --family qwen --context 128k --vision gpu --tune skip --access local --port 8080 --no-tui --yes
```
- 模型源即 HuggingFace `ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF`（2 分片 83.6GB + MTP 5GB + mmproj 0.9GB）
- 下载支持分块续传（`.part.chunks` 记录），慢速时段可用 `hf-mirror` 加速
- 安装体积：`~/.local/share/strata` 约 90GB；引擎 `cuda13` 版

### 实测（RTX 5090 D v2 / 24GB，temp 0.2，reasoning_effort=low）
| 项 | 结果 |
|---|---|
| 模型 id | `qwen3.8-flash-next-iq3_s`，n_ctx **131072**，文本+图像 |
| 短答延迟 | **1.5 s** |
| 解码 | **20–36 tok/s**（对比 Maya-S 3.6–6、Ollama 32B 55） |
| 长上下文（18KB 源码定位） | **6.0 s**（Maya 93.6 s） |
| 功能基准 | 7/8（T3 为判定脚本未处理 `\frac{L}{g}`，答案正确 → 实质 8/8） |

### 路由（已写入，需重启 opencode）
- `oracle` / `metis` / `deep-high` / `ultrabrain` / `visual-engineering` / `multimodal-looker` → `strata/qwen3.8-flash-next-iq3_s`
- 兜底：`ollama/qwen3:32b-ctx8k` → `opencode-go/beam-free`
- `quick` 等快活仍走 `beam-free`

### KVMem（Linux sm120a 诊断包，已验证）
- `kvmem-v0.16.0-rc1-linux-x86_64-cuda13-sm120a.tar.gz`（440MB，sha 已校验）
- 解压至 `~/kvmem/`，`sha256sum -c SHA256SUMS` 全 OK，`bin/llama-kvmem-server --help` 正常
- 是 llama.cpp 系（`llama-kvmem-server` / `start-iq3.sh` / `start-iq4.sh`），自带 CUDA 运行时，无需 toolkit
- **与 strata 争用同一张 24GB 显卡**：实测需先停 strata 才能跑

## 2026-10-28 KVMem 实测结论：**不适用于 Qwen3.8-Flash-Next**

包：`kvmem-v0.16.0-rc1-linux-x86_64-cuda13-sm120a`（440MB，sha 校验通过），llama.cpp 系（`llama-kvmem-server`），自带 CUDA 运行时。

| 配置 | 结果 |
|---|---|
| `-ngl 12 --kvmem-budget 8192 --kvmem-cpu-gb 32` + 视觉 | 启动成功（显存 15.7GB），首个 `/chat/completions` 请求 **崩溃** |
| `-ngl 8 --kvmem-budget 4096 --no-mmproj` | **启动即 abort**（`llama_init_from_model`） |
| `--no-kvmem -ngl 0`（纯 CPU） | ✅ 可用，生成 3.2 tok/s |

**根因（引擎内断言原文）**：
```
llama.cpp/src/models/qwen4exp.cpp:357: GGML_ASSERT(
  mctx_idx->get_n_kv() == inp->mctx->get_attn()->get_n_kv()
  && "the indexer cache must track the attention cache cell for cell") failed
```
Qwen3.8-Flash-Next（`Qwen4Exp`）要求 **indexer cache 与 attention KV cache 逐 cell 对齐**，而 KVMem 的"GPU 工作集预算"会缩小 KV 池 → 断言失败。即 **KVMem 的 KV 分页机制与该架构不兼容**（其发布包面向 27B ternary 线）。

**结论**：KVMem 无法在 24GB 显存上为 Qwen3.8 提供 262K 上下文；strata（原生 131072 上下文、36 tok/s）仍是本机最优解。

## 2026-10-29 KVMem + Qwen3.8-**27B** 实测（成功）

前置：KVMem 仅支持 **Qwen Dense**（27B 线）；`qwen4_exp`（Flash-Next）被明确拒绝（`docs/multi-backend-differences.md`）。
模型：`ISTA-DASLab/Qwen3.8-27B-GSQ-RCO-GGUF` 的 `Qwen3.8-27B-GSQ-RCO-IQ3_S-mtp.gguf`（12.12GB，sha256 校验通过）+ `unsloth/Qwen3.8-27B-GGUF` 的 `mmproj-BF16.gguf`。

启动（配方 iq3：KV q8_0、GPU 工作集 36864、reserve 16384、逻辑上下文 262144）：
```bash
PORT=18200 CUDA_VISIBLE_DEVICES=0 \
  MODEL=~/kvmem-models/Qwen3.8-27B-GSQ-RCO-IQ3_S-mtp.gguf \
  MMPROJ=~/kvmem-models/mmproj-BF16.gguf \
  ~/kvmem/kvmem-v0.16.0-rc1-linux-x86_64-cuda13-sm120a/scripts/start-iq3.sh
```

### 实测（RTX 5090 24GB）
| 项 | 结果 |
|---|---|
| 显存 | **15.6–16.7 GB**（含视觉） |
| 解码 | **112.6 tok/s**（strata 36 tok/s 的 3 倍） |
| 短答 | 1.0 s |
| 长文召回（24,129 tok） | 12.4 s，答案正确 |
| 长文召回（75,504 tok，**超 GPU 工作集**） | 43.8 s，**答案正确**（KVMem 分页生效） |
| 长文召回（141,337 tok，**≈4× 超预算**） | 97.2 s，**答案正确**，显存仍 16.7 GB |

### 与 strata 的取舍
| | strata 千问 3.8 Flash-Next | KVMem Qwen3.8-27B |
|---|---|---|
| 模型规模 | 大 MoE（IQ3_S 79GB） | 27B Dense（IQ3_S 12GB） |
| 解码 | 36 tok/s | **112 tok/s** |
| 上下文 | 131,072（硬上限） | **262,144 逻辑**，实测 141K 正确 |
| 显存 | 23.6 GB | **16.7 GB** |
| 质量 | 更强（大模型） | 较弱（27B） |
| 并发 | 单槽 | 单槽 |

**两者不能同时驻留**（23.6 + 16.7 > 24GB）。切换脚本：
- `~/bin/ai-strata` → 8080，质量优先（默认）
- `~/bin/ai-kvmem` → 18200，速度/超长上下文优先
