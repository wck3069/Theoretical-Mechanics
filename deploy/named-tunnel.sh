#!/usr/bin/env bash
# 一条命令建立固定网址：命名隧道 -> 登录门(8090) = 网站 + 本地 AI。
#
# 用法：bash deploy/named-tunnel.sh tm.你的域名.com
# 前提：Cloudflare 账号里已添加该域名（任意注册商购买后转入 CF  nameservers）。
# 人工步骤仅一处：脚本会调用 cloudflared tunnel login，打印授权 URL，
# 你在浏览器打开并选择该域名所在 zone；其余全自动。
#
# 完成后：https://tm.你的域名.com 固定不变（重启/掉线自动重连，URL 不再漂移），
# 原临时 tm-tunnel 自动停用，URL 写入 ~/.local/state/tm/login-url。
set -euo pipefail

HOST="${1:-}"
if [ -z "$HOST" ]; then
  echo "用法: bash deploy/named-tunnel.sh <主机名, 如 tm.example.com>" >&2
  exit 2
fi
CF_BIN="${CLOUDFLARED_BIN:-$(command -v cloudflared || echo "$HOME/.local/bin/cloudflared")}"
if [ ! -x "$CF_BIN" ]; then
  echo "cloudflared 未找到（设 CLOUDFLARED_BIN）" >&2
  exit 127
fi

TUNNEL_NAME="tm-site"
CF_DIR="$HOME/.cloudflared"
CONFIG="$CF_DIR/tm-site.yml"
STATE="${XDG_STATE_HOME:-$HOME/.local/state}/tm"

echo "==> 1/5 Cloudflare 授权（cert.pem 缺失时触发浏览器登录）"
if [ ! -f "$CF_DIR/cert.pem" ]; then
  "$CF_BIN" tunnel login
fi
[ -f "$CF_DIR/cert.pem" ] || { echo "授权未完成，退出" >&2; exit 1; }

echo "==> 2/5 创建隧道 $TUNNEL_NAME（幂等）"
if ! "$CF_BIN" tunnel list 2>/dev/null | awk '{print $2}' | grep -qx "$TUNNEL_NAME"; then
  "$CF_BIN" tunnel create "$TUNNEL_NAME"
fi
TUNNEL_ID="$("$CF_BIN" tunnel list 2>/dev/null | awk -v n="$TUNNEL_NAME" '$2==n{print $1; exit}')"
[ -n "$TUNNEL_ID" ] || { echo "取不到隧道 ID" >&2; exit 1; }
CRED="$CF_DIR/$TUNNEL_ID.json"
[ -f "$CRED" ] || { echo "凭证文件缺失: $CRED" >&2; exit 1; }

echo "==> 3/5 DNS 路由 $HOST -> $TUNNEL_NAME"
"$CF_BIN" tunnel route dns "$TUNNEL_NAME" "$HOST" || echo "（DNS 记录可能已存在，继续）"

echo "==> 4/5 写配置 + systemd 单元"
cat > "$CONFIG" <<EOF
tunnel: $TUNNEL_ID
credentials-file: $CRED
ingress:
  - hostname: $HOST
    service: http://127.0.0.1:8090
  - service: http_status:404
EOF

UNIT_DIR="$HOME/.config/systemd/user"
mkdir -p "$UNIT_DIR"
cat > "$UNIT_DIR/tm-named-tunnel.service" <<EOF
[Unit]
Description=TM Cloudflare named tunnel (fixed https://$HOST -> login gate)
After=network-online.target tm-login.service
Wants=network-online.target

[Service]
Environment="PATH=$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/bin"
ExecStart=$CF_BIN tunnel --config $CONFIG --no-autoupdate run
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user disable --now tm-tunnel.service 2>/dev/null || true
systemctl --user enable --now tm-named-tunnel.service

echo "==> 5/5 验证 https://$HOST/health"
mkdir -p "$STATE"
ok=""
for _ in $(seq 1 12); do
  sleep 3
  code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 "https://$HOST/health" || true)"
  if [ "$code" = "200" ]; then ok=1; break; fi
done
if [ -n "$ok" ]; then
  printf 'https://%s\n' "$HOST" > "$STATE/login-url"
  ln -sfn "$STATE/login-url" /tmp/tm-login-url
  echo "完成：https://$HOST （网站+本地AI，登录门保护；URL 已写入 state）"
else
  echo "警告：/health 未返回 200。检查: systemctl --user status tm-named-tunnel; journalctl --user -u tm-named-tunnel -n 30" >&2
  exit 1
fi
