# Tailscale：给班级一个私有 HTTPS 地址（推荐）

优点：不用公网 IP、不用证书、学生必须加入你的 tailnet，天然有身份边界。

```bash
# 老师机
tailscale up
TM_MAX_CONCURRENT=2 TM_RATE_PER_MIN=15 bash tools/serve.sh   # 仅监听 127.0.0.1:8765
tailscale serve --bg https / http://127.0.0.1:8765
tailscale serve status
```

学生：

1. 安装 Tailscale，接受你的邀请加入 tailnet；
2. 打开 `https://<老师机名>.<tailnet>.ts.net/`。

注意：
- `tailscale funnel` 会把服务暴露到公网，默认不要用；
- 若只想让某些学生访问，用 tailnet ACL 限制；
- 单卡仍受 `TM_MAX_CONCURRENT` 限制。
