# 校园映射单：给网站一个固定地址（2026-11-06）

## 要请网络管理员做的事

新增一条 NAT 端口映射，与现有的 `913 -> 192.168.199.120:22` 同类：

```
TCP  58.194.171.148:8443  ->  192.168.199.120:8090
```

映射之后，学生的固定地址就是 **`http://58.194.171.148:8443/`**，不会再变。

## 为什么是 8090

`TM-Login/app.py` 用 waitress 监听 `0.0.0.0:8090`（`threads=8`），它是整站唯一入口，同时负责三件事：

1. 姓名登记门禁（未登录一律 302 到登录页，实测 `/`、`/index.html`、`/api/health` 都是 302）
2. 反向代理 `SITE_ROOT=~/Theoretical-Mechanics/dist` 的静态页
3. `api_proxy` 把 `/api/*` 转给 `ai_server.py`（`127.0.0.1:8765`，AI 侧限流 `max_concurrent=2`、`rate_per_min=20`）

所以只映射这一个端口，页面、门禁、AI 就都通了。heft 本机防火墙未启用（`ufw`、`nftables` 均 inactive），映射到位即可用，无需在机器上放行。

## 映射到位后怎么验

heft 上（映射前就应当通过）：

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8090/     # 期望 302
```

从校外机器：

```bash
curl -s http://58.194.171.148:8443/ | grep -o "<title>[^<]*"       # 期望 登录 · 理论力学
```

## 实测（2026-11-06，从校园网有线出口，即 heft 本机）

- 有线出口的公网 IP 就是 `58.194.171.148`（与 SSH 映射 `913` 同一个），说明这台机器确实在那台 NAT 后面。
- `Cloudflare:443` IPv4 → 200（44 ms）；Quick Tunnel 域名 → 302；GitHub Pages 镜像 → 200（`tm-i18n.js` 等资产已在线上）。
- **该出口的 IPv6 完全不通**：`www.cloudflare.com`、`1.1.1.1`、`wck3069.github.io` 的 `curl -6` 全是 `HTTP 000`。而 `trycloudflare.com` 域名同时返回 AAAA（`2606:4700::...`）和 A（`104.16.231.132`），客户端会先试 v6 再回落 IPv4，实测回落把连接时间从 0.04 s 拉到 0.25 s。所以 v6 优先会造成明显卡顿，但不足以解释彻底打不开。
- Wi-Fi 与有线实验网可能走不同出口，境外 IP 是否被过滤尚未测到。要在 Wi-Fi 机器上跑 `deploy/wifi-selftest.sh` 才能定论；不能用开发机代替：开发机所有出站被 mihomo TUN 送到境外节点（实测出口 `52.69.172.100`），测出来的可达性不代表校园路径。

## 已知代价

- **明文 HTTP**。裸 IP 签不到可信证书，自签证书会给学生浏览器警告，反而更糟。要真 HTTPS，需要管理员再给一条校园域名的 A 记录 + `80` 端口映射（ACME HTTP-01 只认 80），届时用 Caddy 或 nginx 终结 TLS，`8090` 收回 `127.0.0.1` 即可，站点代码不用改。
- 门禁只是姓名登记，不是凭据保护：它挡的是"随便用"，不是"有意的绕过"。建议在 NAT 设备侧对该端口再加一层连接速率限制（若设备支持）。
- AI 是单卡（RTX 5090 D，`--parallel 1`），同一时刻只跑一个推理。班级同时提问会排队，必要时调 `TM_MAX_CONCURRENT` / `TM_RATE_PER_MIN`。

## 过渡期

映射生效前，临时入口仍是 Cloudflare Quick Tunnel（`tm-tunnel.service`，地址存在 `~/.local/state/tm/login-url`，每次重启都会换域名）。映射生效后应 `systemctl --user stop disable tm-tunnel.service`。
