#!/usr/bin/env bash
# Cloudflare quick tunnel for the open demo preview (no login), serving dist/ via tm-static-server.
# The URL is ephemeral; it is written to $XDG_STATE_HOME/tm/demo-url and
# mirrored to /tmp/tm-demo-url for convenience.
set -euo pipefail

# systemd user units run with a minimal PATH; make sure ~/.local/bin is searched.
export PATH="$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin:${PATH:-}"
CF_BIN="${CLOUDFLARED_BIN:-$(command -v cloudflared || true)}"
if [[ -z "$CF_BIN" ]]; then
  echo "cloudflared not found (set CLOUDFLARED_BIN)" >&2
  exit 127
fi

STATE="${XDG_STATE_HOME:-$HOME/.local/state}/tm"
mkdir -p "$STATE"
URL_FILE="$STATE/demo-url"
: > "$URL_FILE"
ln -sfn "$URL_FILE" /tmp/tm-demo-url

"$CF_BIN" tunnel --url http://127.0.0.1:8081 --protocol http2 --no-autoupdate 2>&1 |
while IFS= read -r line; do
  printf '%s\n' "$line"
  if [[ "$line" =~ (https://[a-z0-9-]+\.trycloudflare\.com) ]]; then
    printf '%s\n' "${BASH_REMATCH[1]}" > "$URL_FILE"
  fi
done
