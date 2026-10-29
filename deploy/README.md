# 远程访问方案（让学生用上本地 AI）

单卡 GPU（RTX 5090，约 3 个并发槽）决定了：**页面可以无限人看，AI 必须限流**。
下面按场景选一种，不要直接把 8765 端口暴露到公网。

## 选型

| 场景 | 方案 | 学生怎么进 | 鉴权 | 成本 |
|---|---|---|---|---|
| 同一间教室/实验室 Wi-Fi | 局域网直连 | `http://<老师机内网IP>:8765/` | 无（可信网络） | 0 |
| 同校但跨网段 / 宿舍 | **Tailscale（推荐）** | 私有域名，需加入 tailnet | 设备/账号身份 | 0 |
| 校外公开、要账号 | **Caddy/Nginx + HTTPS + Basic Auth** | 公网域名 | 用户名+密码 | 域名 + 服务器 |
| 不想开端口 | **Cloudflare Tunnel + Access** | 公网域名 | Cloudflare 登录/邮箱验证 | 0 起 |

> 最省事且安全的组合：**Tailscale Serve**（私有、自带 HTTPS、无需公网 IP）。
> 要真正公开，至少加 Basic Auth + 限流，并接受“单卡并发有限”。

## 一、局域网

```bash
TM_HOST=0.0.0.0 TM_MAX_CONCURRENT=2 TM_RATE_PER_MIN=15 bash tools/serve.sh
```

终端会打印 `http://192.168.x.x:8765/`。只适合可信局域网。

## 二、Tailscale（推荐给班级）

老师机与学生机加入同一个 tailnet（免费版够用）：

```bash
# 老师机
tailscale up
tailscale serve --bg https / http://127.0.0.1:8765
tailscale serve status
```

学生打开 `https://<机器名>.<tailnet>.ts.net/` 即可。默认仅 tailnet 内可见；
不要用 `tailscale funnel` 除非你确实要公开。

## 三、Caddy 反向代理（公网 + Basic Auth）

```bash
# 1) 生成密码哈希
caddy hash-password --plaintext '给学生的密码'

# 2) 设置环境变量并启动
export TM_DOMAIN=mechanics.example.com
export TM_USER=class
export TM_HASH='<上一步输出的哈希>'
caddy run --config deploy/Caddyfile

# 3) 应用本体（只监听本机）
TM_MAX_CONCURRENT=2 TM_RATE_PER_MIN=15 bash tools/serve.sh
```

Caddy 自动申请 HTTPS。学生第一次打开会弹用户名/密码。

## 四、Nginx 反向代理

```bash
sudo cp deploy/nginx.conf /etc/nginx/conf.d/mechanics.conf
sudo htpasswd -c /etc/nginx/.htpasswd class
sudo nginx -t && sudo systemctl reload nginx
```

把 `server_name` 改成你的域名；证书用 certbot 配置。

## 五、Cloudflare Tunnel（不开端口）

```bash
cloudflared tunnel --url http://127.0.0.1:8765
```

快速隧道会给出临时公网 URL，但**没有鉴权**；正式使用请建命名隧道并在
Cloudflare Zero Trust → Access 里加邮箱/组织策略。详见 `deploy/cloudflared.md`。

## 容量与限流（重要）

单卡 5090、模型 27B 级、约 40 tok/s：

- `TM_MAX_CONCURRENT=2`：同时最多 2 个回答，超出的请求返回 429 并提示稍后再试。
- `TM_RATE_PER_MIN=15`：每 IP 每分钟最多 15 次，防止刷接口。
- “快速模式”（fast）约 6 段检索，适合课堂；“深空模式”（deep）可能发送数万字，
  一次要几十秒，建议只用于答疑/办公时间。
- 页面本身是静态的，几百人同时浏览没问题；压力只在 `/api/ask`。

## 安全清单

- 不要把 `8765` 直接映射到公网；必须经过带 TLS + 鉴权的反向代理。
- 代理层设置请求体上限（1 MB）与超时（>=300 s，deep 模式较慢）。
- 只信任代理写入的 `X-Forwarded-For`（本服务用它做限流）；不要允许客户端伪造。
- AI 输出可能有错：页面上保留“以讲义推导为准”的提示。
- 定期看服务端 stderr 日志（方法/路径/状态/耗时，不记录问题正文）。
- 作业 PDF 属于私有资料，`export_static.sh` 不会导出 `作业/`。

## GitHub Pages（已启用）

- 源：`gh-pages` 分支根目录（由 `dist/` 生成，不含 tools/qa/data）
- 地址：<https://wck3069.github.io/Theoretical-Mechanics/>
- 更新：`bash tools/publish_pages.sh`（自动导出 dist、重建 gh-pages、推送）
- 静态托管没有 `/api`，AI 面板会自动降级为离线检索

## 公网完整 AI（key 不暴露）

- **推荐**：Cloudflare Tunnel + Access + `TM_STATIC_ROOT=dist`，见 `deploy/cloudflare/README.md`。
- **备选**：公网服务器 + Caddy Basic Auth（`deploy/Caddyfile`）；应用同样以 `TM_STATIC_ROOT=dist` 启动。
- **不要**把 `TM_AI_KEY` 写进 `index.html`、Pages、Worker 的前端代码；key 只留在服务端环境变量。
- 静态 Pages 仍保持离线检索；它没有 `/api`，也不应该持有 key。
