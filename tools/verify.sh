#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

if [ -x "$HOME/.venv-tm/bin/python" ]; then
  PY="$HOME/.venv-tm/bin/python"
else
  PY="python3"
fi

"$PY" tools/check_html.py index.html catalog.html binet.html \
  chapters/*/index.html chapters/*/manuscripts/*.html \
  modules/*/index.html
"$PY" tools/check_links.py --root .
"$PY" tools/build_kb.py --check
"$PY" tools/build_offline_kb.py
"$PY" tools/apply_seo.py
git diff --exit-code
"$PY" tools/verify_selftest.py

echo "verify: OK"
