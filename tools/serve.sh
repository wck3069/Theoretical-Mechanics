#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
PORT="${TM_PORT:-8765}"
HOST="${TM_HOST:-127.0.0.1}"
for f in "$HOME/.config/tm-ai.env" "$ROOT/tools/ai.env"; do
  if [ -f "$f" ]; then
    set -a
    . "$f"
    set +a
  fi
done
echo "Serving at http://127.0.0.1:${PORT}/"
if [ "$HOST" != "127.0.0.1" ]; then
  echo "LAN mode (TM_HOST=${HOST}). Students on the same network use the URL printed by the server below."
  echo "Do not expose this port to the public internet without a reverse proxy and authentication."
fi
exec python3 tools/ai_server.py --host "$HOST" --port "$PORT" "$@"
