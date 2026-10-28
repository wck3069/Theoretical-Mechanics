# Cloudflare Tunnel（不开公网端口）

## 快速试用（无鉴权，仅临时）

```bash
TM_MAX_CONCURRENT=2 TM_RATE_PER_MIN=10 bash tools/serve.sh
cloudflared tunnel --url http://127.0.0.1:8765
```

会打印一个 `https://xxxx.trycloudflare.com` 临时地址。**任何人都能访问**，只用于演示。

## 正式使用（命名隧道 + Access）

```bash
cloudflared tunnel login
cloudflared tunnel create mechanics
cloudflared tunnel route dns mechanics mechanics.example.com
```

`~/.cloudflared/config.yml`：

```yaml
tunnel: mechanics
credentials-file: /root/.cloudflared/<tunnel-id>.json
ingress:
  - hostname: mechanics.example.com
    service: http://127.0.0.1:8765
  - service: http_status:404
```

```bash
cloudflared tunnel run mechanics
```

然后在 Cloudflare Zero Trust → Access → Applications 里为
`mechanics.example.com` 加策略（邮箱验证 / 组织 / OTP）。这样未登录者进不来。

建议同时在服务端设 `TM_MAX_CONCURRENT=2 TM_RATE_PER_MIN=10`。
