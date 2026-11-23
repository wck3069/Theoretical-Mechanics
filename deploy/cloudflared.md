# Cloudflare Tunnel（不开公网端口）

> 当前生产使用 quick tunnel + systemd 单元 `tm-tunnel`；URL 每次重启会变，
> 写入 `~/.local/state/tm/login-url` 并镜像到 `/tmp/tm-login-url`。
> 要固定域名，必须完成下面的命名隧道步骤（需要 Cloudflare 账号与域名；
> 当前机器没有 `~/.cloudflared/cert.pem`）。

## 站点 + 本地 AI 的公网入口（登录门架构，2026-11-23 验证）

**`tm-tunnel`（登录门隧道）就是「网站 + 本地 AI」的完整入口**，不需要 Pages：

```
访客 → https://<login-url> (CF quick tunnel)
     → TM-Login 登录门 127.0.0.1:8090（姓名 + 访问码，会话保护）
        ├─ 静态页：SITE_ROOT=dist（tm-static-sync 自动同步最新站点）
        └─ /api/*：服务端注入 Basic Auth 代理到 127.0.0.1:8765（ai_server）
                   → 本地 strata/qwen3.8 RAG，kb_chunks=300
```

- 登录门与 AI 同源，`assets/tm-ai-panel.js` 的 `API_BASE=''` 直接工作，零改动。
- `/api/*` 同样受登录保护（`before_request` 不豁免），AI 不裸露公网。
- 访问码在 `~/.config/tm-login.env`（TM_LOGIN_CODE），AI 凭证在 `~/.config/tm-ai.env`。
- 开放演示隧道 `tm-demo-tunnel`（8081 纯静态，无 AI）URL 在 `~/.local/state/tm/demo-url`。

**故障模式与修复**：quick tunnel 注册会被 CF 侧回收，cloudflared 日志报
`Unauthorized: Tunnel not found` 并无限重试旧 ID——此时 URL 已死。
修复：`systemctl --user restart tm-tunnel.service`，新 URL 自动写入 state 文件。

**8765 归 systemd 管**（`tm-ai.service` = tools/serve.sh）。不要手动 nohup 抢占端口，
否则 systemd 进入 auto-restart 崩溃循环。重启 AI：`systemctl --user restart tm-ai`。

端到端自检（登录 → /api/health → /api/ask）见 `qa/global/kb-recovery-2026-11-23.md`
同日的 CF 链路验证；测试登录记录名「链路自检」。

## 快速试用（无鉴权，仅临时）

```bash
TM_MAX_CONCURRENT=2 TM_RATE_PER_MIN=10 bash tools/serve.sh
cloudflared tunnel --url http://127.0.0.1:8765
```

会打印一个 `https://xxxx.trycloudflare.com` 临时地址。**任何人都能访问**，只用于演示。

## 正式使用（命名隧道 + 固定域名，一条命令）

前提：Cloudflare 账号里已有你的域名。然后：

```bash
bash deploy/named-tunnel.sh tm.你的域名.com
```

脚本自动完成：`tunnel login`（唯一人工步骤：浏览器打开打印的 URL 并选择域名 zone）
→ 创建隧道 tm-site → DNS 路由 → 写 `~/.cloudflared/tm-site.yml`（ ingress 指向
登录门 8090 = 网站+本地AI）→ 安装并启用 `tm-named-tunnel.service`、停用临时
`tm-tunnel` → 验证 `https://主机名/health` → URL 写入 `~/.local/state/tm/login-url`。

此后网址固定，重启/掉线自动重连不再漂移。建议再在 Cloudflare Zero Trust →
Access → Applications 为该主机名加策略（邮箱验证 / OTP），并设
`TM_MAX_CONCURRENT=2 TM_RATE_PER_MIN=10`。

手动步骤（脚本的等价展开，供排查）：

```bash
cloudflared tunnel login
cloudflared tunnel create tm-site
cloudflared tunnel route dns tm-site tm.example.com
```

`~/.cloudflared/tm-site.yml`（脚本自动生成，此处供排查对照）：

```yaml
tunnel: <tunnel-id>
credentials-file: /home/wck/.cloudflared/<tunnel-id>.json
ingress:
  - hostname: tm.example.com
    service: http://127.0.0.1:8090
  - service: http_status:404
```

```bash
cloudflared tunnel --config ~/.cloudflared/tm-site.yml run
```

注意 ingress 指向 **8090 登录门**（网站+本地AI，会话保护），不是 8765；
8765 的 Basic Auth 由登录门服务端注入，访客无需知道。未登录者进不来。
