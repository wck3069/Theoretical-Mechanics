#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${1:-$ROOT/dist}"
rm -rf "$OUT"
mkdir -p "$OUT"
cp "$ROOT/index.html" "$ROOT/catalog.html" "$ROOT/binet.html" "$OUT/"
cp -r "$ROOT/modules" "$OUT/modules"
cp -r "$ROOT/chapters" "$OUT/chapters"
cp -r "$ROOT/neural" "$OUT/neural"
cp -r "$ROOT/manuscript" "$OUT/manuscript"
mkdir -p "$OUT/assets"
cp -r "$ROOT/assets/img" "$OUT/assets/img"
cp -r "$ROOT/assets/textures" "$OUT/assets/textures"
cp "$ROOT/assets/manuscript.css" "$OUT/assets/manuscript.css"
cp "$ROOT/assets/ui-liquid.css" "$OUT/assets/ui-liquid.css"
cp "$ROOT/assets/tm-atelier.css" "$OUT/assets/tm-atelier.css"
cp "$ROOT/assets/ui-motion.js" "$OUT/assets/ui-motion.js"
cp "$ROOT/assets/manuscript-nav.js" "$OUT/assets/manuscript-nav.js"
cp "$ROOT/assets/pdf-viewer.js" "$OUT/assets/pdf-viewer.js"
cp "$ROOT/assets/tm-seq.js" "$OUT/assets/tm-seq.js"
cp "$ROOT/assets/tm-i18n.js" "$OUT/assets/tm-i18n.js"
cp "$ROOT/assets/tm-modes.js" "$OUT/assets/tm-modes.js"
cp "$ROOT/assets/tm-ai-panel.js" "$OUT/assets/tm-ai-panel.js"
cp "$ROOT/assets/tm-offline-kb.js" "$OUT/assets/tm-offline-kb.js"
cp "$ROOT/assets/tm-i18n-data.js" "$OUT/assets/tm-i18n-data.js"
cp -r "$ROOT/assets/i18n" "$OUT/assets/i18n"
cp "$ROOT/assets/og-cover.png" "$OUT/assets/og-cover.png"
cp -r "$ROOT/assets/mathjax" "$OUT/assets/mathjax"
cp -r "$ROOT/assets/cosmos" "$OUT/assets/cosmos"
cp "$ROOT/sitemap.xml" "$ROOT/robots.txt" "$OUT/"
find "$OUT/modules" -type d -name qa -prune -exec rm -rf {} + 2>/dev/null || true
# 原尺寸 portal 图已无页面引用（各页改用 assets/img/portal/sm/*.webp），不随发布产物上线
find "$OUT/assets/img/portal" -maxdepth 1 -type f \( -name "*.jpg" -o -name "*.png" \) -delete 2>/dev/null || true
find "$OUT" -name "*.md" -delete
find "$OUT/modules" \( -name '*.aux' -o -name '*.log' -o -name '*.out' -o -name '*.toc' \
  -o -name '*.fls' -o -name '*.fdb_latexmk' -o -name '*.xdv' -o -name '*.synctex.gz' \) -delete
: > "$OUT/.nojekyll"
if grep -rIl --include='*.html' -e '127\.0\.0\.1' -e 'localhost' "$OUT"; then
  echo "WARNING: localhost reference found in exported HTML" >&2
fi
echo "Exported static site to: $OUT"
echo "Upload this folder to any static host (GitHub Pages, Netlify, nginx)."
echo "The AI panel will run in offline local-retrieval mode there."
du -sh "$OUT"
