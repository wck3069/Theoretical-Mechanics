#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${1:-$ROOT/dist}"
rm -rf "$OUT"
mkdir -p "$OUT"
cp "$ROOT/index.html" "$ROOT/catalog.html" "$OUT/"
cp -r "$ROOT/modules" "$OUT/modules"
find "$OUT/modules" -type d -name qa -prune -exec rm -rf {} + 2>/dev/null || true
if grep -rIl --include='*.html' -e '127\.0\.0\.1' -e 'localhost' "$OUT"; then
  echo "WARNING: localhost reference found in exported HTML" >&2
fi
echo "Exported static site to: $OUT"
echo "Upload this folder to any static host (GitHub Pages, Netlify, nginx)."
echo "The AI panel will run in offline local-retrieval mode there."
du -sh "$OUT"
