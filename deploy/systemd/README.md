# systemd user units

安装：

```bash
mkdir -p ~/.config/systemd/user
cp deploy/systemd/tm-*.service deploy/systemd/tm-backup.timer ~/.config/systemd/user/
loginctl enable-linger "$USER"
systemctl --user daemon-reload
systemctl --user enable --now tm-login.service tm-ai.service tm-tunnel.service tm-backup.timer
```

检查：

```bash
systemctl --user status tm-login tm-ai tm-tunnel tm-backup.timer
journalctl --user -u tm-login -u tm-ai -u tm-tunnel -n 50
curl -s http://127.0.0.1:8090/health
```

说明：

- `tm-login` 运行 `/home/wck/TM-Login/app.py`（waitress，127.0.0.1:8090）
- `tm-ai` 运行 `tools/serve.sh`（本地 AI，127.0.0.1:8765）
- `tm-tunnel` 运行 `TM-Login/tunnel.sh`，quick tunnel 的 URL 写入
  `~/.local/state/tm/login-url`，并镜像到 `/tmp/tm-login-url`
- `tm-backup.timer` 每天 03:30 备份 `TM-Login/data/login.db`，保留 14 份
- 日志进 journald，不再写 `/tmp`
- **quick tunnel 的 URL 在进程重启后会变化**；固定域名需要 Cloudflare
  命名隧道，步骤见 `deploy/cloudflared.md`（需要账号与域名，当前机器没有 cert）
