# 公网完整 AI：Cloudflare Tunnel + Access（推荐）

目标：学生从公网打开站点并用完整 AI；**SDU API key 只留在这台机器**，
前端/Pages 里没有 key；未登录 Cloudflare Access 的人连页面都打不开。

## 前提

- 一个托管在 Cloudflare 的域名（如 `mechanics.example.com`）。
- 这台机器能访问 `https://xplt.sdu.edu.cn:4000`（当前已通），并且能长期开机。
- `~/.config/tm-ai.env` 已配置 key（`chmod 600`）。
- 只暴露 `dist/`，不要把仓库根目录暴露出去（里面有 `作业/`、`tools/`、`qa/`）。

## 1. 构建静态站并启动服务（只监听本机）

```bash
cd /home/wck/Theoretical-Mechanics
bash tools/export_static.sh

TM_STATIC_ROOT="$PWD/dist" \
TM_MAX_CONCURRENT=2 TM_RATE_PER_MIN=15 \
bash tools/serve.sh
```

- `TM_STATIC_ROOT=dist` 让静态服务只读 `dist/`；`/作业/...`、`/tools/...` 会 404。
- 服务仍只监听 `127.0.0.1:8765`，公网无法直接连。
- AI 的 key 由 `tools/serve.sh` 从 `~/.config/tm-ai.env` 读取，前端只调用同源 `/api/ask`。

## 2. 创建命名隧道

```bash
# 安装 cloudflared（Debian/Ubuntu）
curl -L -o /tmp/cloudflared.deb \
  https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i /tmp/cloudflared.deb

cloudflared tunnel login          # 浏览器里选你的域名
cloudflared tunnel create mechanics-ai
cloudflared tunnel route dns mechanics-ai mechanics.example.com
```

把 `deploy/cloudflare/cloudflared.yml.example` 复制到 `~/.cloudflared/config.yml`，
替换 `<TUNNEL-UUID>`、`<user>`、域名。

```bash
cloudflared tunnel run mechanics-ai
```

常驻：

```bash
sudo cloudflared service install
sudo systemctl enable --now cloudflared
```


## Basic Auth（已内置，最省事）

服务端已支持 Basic Auth；在 `~/.config/tm-ai.env` 设置：

```bash
TM_AUTH_USER=理论力学
TM_AUTH_USER_ALT=lilun
TM_AUTH_PASS=<你自己的密码>
```

重启 `bash tools/serve.sh` 后：

- 浏览器打开站点会弹用户名/密码；输入后同源 `/api/ask` 自动带凭据。
- 未登录或密码错误返回 401；正确返回 200。
- 必须走 HTTPS（Cloudflare Tunnel 默认就是 HTTPS）；不要用明文 HTTP 公网。
- 用 `file://` 直接打开时浏览器不会带 Basic Auth，请用 `http(s)://` 地址。
- Cloudflare Access 可选：叠加邮箱/SSO 作为第二层；只用 Basic Auth 也够一个班使用。

验证：

```bash
curl -s -o /dev/null -w '%{http_code}\n' https://mechanics.example.com/          # 401
curl -s -u '理论力学:<密码>' -o /dev/null -w '%{http_code}\n' https://mechanics.example.com/  # 200
```

## 3. 加 Cloudflare Access（可选，第二层）

Cloudflare Zero Trust → **Access → Applications → Add an application → Self-hosted**：

- Application name：`理论力学 AI 助教`
- Public hostname：`mechanics.example.com`
- Session duration：8–24 小时
- Policy：
  - Action **Allow**
  - Include **Emails ending in** `@sdu.edu.cn`（或指定班级名单）
  - 需要更严格时用 **SDU SSO / OIDC**；没有就选 **One-time PIN**（邮箱收验证码）
- 保存后，未登录访问会先跳转 Access 登录页；登录后 Access cookie 会随同源
  `/api/ask` 一起发送，面板正常使用。

## 4. 限流与额度

- 应用层：`TM_MAX_CONCURRENT=2`、`TM_RATE_PER_MIN=15`（按 IP）。
- Cloudflare：Security → WAF → Rate limiting rules，对 `/api/ask` 加
  例如 `30 requests / 1 minute / IP`，超出返回 429。
- 学校网关本身可能也有配额；不要用 `reasoning_effort=high` 做全班并发。

## 5. 验证

```bash
# 未登录：应 302 到 Access 登录页
curl -sI https://mechanics.example.com/ | head

# 登录后（浏览器）：页面 + /api/ask 正常工作
# 确认页面源码里没有 key
curl -s https://mechanics.example.com/ | grep -c 'sk-'   # 应为 0
```

## 常见问题

- **Access 登录后仍 403**：检查 policy 的邮箱域、应用是否覆盖 `/api/*`；
  清 cookie 重试。
- **AI 返回 503**：本机到 `xplt.sdu.edu.cn:4000` 不通，或 key 过期/额度用尽；
  看 `tools/ai_server.py` 的 stderr 日志。
- **页面 502**：`tools/serve.sh` 没启动，或隧道指向的端口不对。
- **只想给校内/教室用**：不需要公网，直接
  `TM_HOST=0.0.0.0 TM_STATIC_ROOT="$PWD/dist" bash tools/serve.sh`，
  学生用 `http://<内网IP>:8765/`。
- **不想用 Cloudflare**：见 `deploy/Caddyfile` 的 Basic Auth 方案（需要公网 IP + 域名 + 证书）；
  应用同样用 `TM_STATIC_ROOT=dist` 启动。

## 为什么不在 Pages 里直接放 key

GitHub Pages / 纯静态站的所有代码都公开；把 key 写进前端等于把学校网关的额度公开。
Worker/Pages Functions 可以持有 key，但会丢失本项目的 149 段 RAG 与严格助教规则；
如果确实要用，建议 Function 只做“带 Access 的转发”，后端仍指向本隧道，而不是直接调 SDU API。
