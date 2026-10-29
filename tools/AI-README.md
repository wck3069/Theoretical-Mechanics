# 理论力学交互讲义 · AI 助教

## 启动

```bash
bash tools/serve.sh
```

默认监听 `http://127.0.0.1:8765/`，同时提供静态站点与 `/api/ask`。

## SDU 校内 API（默认）

服务端默认使用学校 OpenAI 兼容网关：

```bash
TM_AI_BASE=https://xplt.sdu.edu.cn:4000/v1
TM_AI_MODEL=SDU-AI/DeepSeek-V4-Flash
TM_AI_EFFORT_FAST=minimal     # 快速：最低档
TM_AI_EFFORT_DEEP=medium      # 深空：中等档
```

`TM_AI_KEY` 只放在本机 `~/.config/tm-ai.env`（chmod 600），由 `tools/serve.sh` 自动 source；
**不要写进前端、`index.html` 或提交到仓库**。`tools/ai.env.example` 是占位模板。

助教行为（system prompt 强制）：
- 只答本站 9 章覆盖的物理问题；
- 每次最多 3 句、120 字，不展开推导；
- 要详细推导时只给一句直觉 + “详见 [M#] 的 note.pdf”；
- 物理但不在本站范围 → “网站未收录这个问题。”；
- 非物理问题 → “同学请认真学习。”。

## 可选：本地 Strata / KVMem

```bash
# Strata
TM_AI_BASE=http://127.0.0.1:8080/v1 \
TM_AI_MODEL=qwen3.8-flash-next-iq3_s \
TM_AI_KEY=strata-local \
python3 tools/ai_server.py

# KVMem 长上下文
TM_AI_BASE=http://127.0.0.1:18200/v1 \
TM_AI_MODEL=<kvmem-model> \
TM_AI_TIMEOUT=300 \
python3 tools/ai_server.py
```

## KVMem 长上下文模式

KVMem 服务运行在 18200 端口时，切换环境变量：

```bash
TM_AI_BASE=http://127.0.0.1:18200/v1 \
TM_AI_MODEL=<kvmem-model> \
TM_AI_TIMEOUT=300 \
python3 tools/ai_server.py
```

深度模式（`mode=deep`）会发送更多文段，适合 KVMem。

## API

- `GET /api/health`：`{ok, upstream, base, model, kb_chunks, version, mode_hint}`
- `GET /api/modules`：9 条模块元数据（无文段）
- `POST /api/ask`：`{question, module, mode, history}` → `{answer, sources, mode, model, ms, upstream}`

`module` 可为 `M0`..`M8` 或 slug；`mode` 为 `fast` 或 `deep`。

## 离线回退

模型不可达时 `/api/ask` 返回 HTTP 503 JSON：`{error:"upstream_offline", detail, fallback:"local-retrieval"}`，前端可退回到本地检索。

## 隐私与 key

- 默认把问题发送到学校网关 `xplt.sdu.edu.cn:4000`；不再声称“只在 127.0.0.1”。
- `TM_AI_KEY` 仅存在于服务端环境变量/`~/.config/tm-ai.env`；前端只调用同源 `/api/ask`，看不到 key。
- **GitHub Pages 是纯静态站点，没有 key，也不会直接调用学校 API**；线上 AI 面板自动降级为离线检索。
  若要在公网使用完整 AI，必须部署一个持有 key 的反向代理/Worker，并加鉴权与限流；不要把 key 放进公开前端。

## 学生怎么访问（三种方式）

### 方式一：静态部署（推荐给全班，人人可开）

```bash
bash tools/export_static.sh
```

把生成的 `dist/` 上传到 GitHub Pages、Netlify、学校静态空间或任意 nginx。
学生直接打开网址即可：9 章讲义、交互模拟、PDF、星图导航全部可用。
此模式下方 AI 面板自动降级为**离线本地检索**（在 9 章元数据里按关键词找相关章节与 PDF），不需要任何服务器。

### 方式二：教室局域网（要完整体验校内 AI）

老师在教室或实验室的一台机器上运行：

```bash
TM_HOST=0.0.0.0 bash tools/serve.sh
```

终端会打印形如 `http://192.168.x.x:8765/` 的局域网地址，学生用同一 Wi-Fi 打开即可，
此时 AI 助教连接本机模型（Strata 或 KVMem），全班共享。

注意：该端口**没有鉴权**，只适合可信的教室局域网；不要直接映射到公网。

### 方式三：公网完整版（需额外的反向代理与鉴权，不推荐直接暴露）

若确实要让校外学生用 AI，应在前面加一层带登录/限流的反向代理（Caddy、Nginx、Cloudflare Tunnel + Access 等），
并且模型机需要有足够的 GPU 与并发能力。默认配置不提供公网鉴权，请勿直接开放 8765 端口。

## 三种模式的差别

| 模式 | 学生访问 | 9 章内容 | AI 助教 | 需要 GPU |
|---|---|---|---|---|
| 静态部署 | 任意网址 | 可用 | 离线检索 | 否 |
| 教室局域网 | 同一局域网 | 可用 | 完整本地模型 | 是（老师机器） |
| 公网完整版 | 任意网址 | 可用 | 完整本地模型 | 是 + 反代鉴权 |

## 远程访问与限流

- `TM_MAX_CONCURRENT`（默认 2）：同时回答上限，超出返回 429。
- `TM_RATE_PER_MIN`（默认 20）：每 IP 每分钟请求上限。
- 公网/跨网段部署见 `deploy/README.md`（Tailscale / Caddy / Nginx / Cloudflare Tunnel）。
- 不要把 8765 裸端口暴露公网；必须加 TLS 与鉴权。

## 离线知识库（无后端也聪明）

```bash
python3 tools/build_offline_kb.py     # 生成 assets/tm-offline-kb.js
python3 tools/apply_ai_panel.py --apply
```

离线面板不再只列章节：它带 49 条常见问题直答、12 个术语、63 段讲义原文摘录，
并做同义词扩展（拉格朗日/Euler、费马/Fermat、洛伦兹/Lorentz 等）与 LaTeX 清洗。
没有 `/api` 时（GitHub Pages 或直接双击 HTML）仍然可用；连接本地服务后自动切换为完整模型。

公网完整 AI 见 `deploy/cloudflare/README.md`；必须用 `TM_STATIC_ROOT=dist` 只暴露站点，key 留在服务端。

## Basic Auth（公网/学生访问）

```bash
TM_AUTH_USER=理论力学
TM_AUTH_USER_ALT=lilun
TM_AUTH_PASS=<密码>
```

`tools/serve.sh` 会从 `~/.config/tm-ai.env` 读取。启动后浏览器弹登录框；未登录 401。
公网必须走 HTTPS；`file://` 打开不会带 Basic Auth，请用 `http(s)://` 地址。

## 本地起草 + 学校 API 审核（默认）

`TM_PIPELINE=local_review` 时：

1. 本机 Strata（`qwen3.8-flash-next-iq3_s`，8080）根据 RAG 文段写草稿；
2. 学校 `SDU-AI/DeepSeek-V4-Flash` 以 `reasoning_effort=minimal` 审核：事实、范围、长度、引用；
3. 返回审核后的最终答案，面板标注「学校审核」。
4. 本地不可用 → 学校直答；审核不可用 → 返回本地草稿并标注「本地草稿（未审核）」。

```bash
TM_PIPELINE=local_review
TM_LOCAL_BASE=http://127.0.0.1:8080/v1
TM_LOCAL_MODEL=qwen3.8-flash-next-iq3_s
TM_LOCAL_KEY=strata-local
TM_REVIEW_EFFORT=minimal
TM_REVIEW_MAX_TOKENS=260
```

实测 fast 约 9–13s（本地草稿 5–9s + 审核 4s），deep 约 10–11s；非物理问题走规则 0ms。

Windows 部署见 `deploy/windows.md`（`tools/serve.ps1`）。

## 公式排版

面板内置零依赖 LaTeX 子集渲染器：分数、根号、上下标、希腊字母、向量/点/帽、`$...$` 与 `\(...\)` 等；服务端提示模型只用简单 LaTeX。

## 连续无关问题

- 第一次非物理问题：`同学请认真学习。`
- 历史里已有提醒后仍问无关问题：`你的胆子真是肥嘟嘟的，快回去学习。`
- 物理问题不受影响；`history` 由面板自动携带（最近 6 条）。

## 问候

纯打招呼（你好/您好/哈喽/嗨/hi/hello/在吗/老师好/同学好）直接回复：

```
你好同学，有什么问题？
```

不调用模型、不计入无关问题；离线模式同样生效。
