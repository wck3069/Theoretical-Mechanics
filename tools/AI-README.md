# 理论力学交互讲义 · 本地 AI 助手

## 启动

```bash
bash tools/serve.sh
```

默认监听 `http://127.0.0.1:8765/`，同时提供静态站点与 `/api/ask`。

## Strata 模式（默认）

Strata 在 `http://127.0.0.1:8080/v1` 提供 `qwen3.8-flash-next-iq3_s`，默认即可：

```bash
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

## 隐私

仅本地运行，请求仅发往 `127.0.0.1`，不上传任何数据。

## 学生怎么访问（三种方式）

### 方式一：静态部署（推荐给全班，人人可开）

```bash
bash tools/export_static.sh
```

把生成的 `dist/` 上传到 GitHub Pages、Netlify、学校静态空间或任意 nginx。
学生直接打开网址即可：9 章讲义、交互模拟、PDF、星图导航全部可用。
此模式下方 AI 面板自动降级为**离线本地检索**（在 9 章元数据里按关键词找相关章节与 PDF），不需要任何服务器。

### 方式二：教室局域网（要完整体验本地 AI）

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
