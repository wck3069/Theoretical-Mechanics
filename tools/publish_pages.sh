#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

bash tools/export_static.sh

INDEX="$(mktemp)"
trap 'rm -f "$INDEX"' EXIT
export GIT_INDEX_FILE="$INDEX"
rm -f "$INDEX"
git read-tree --empty
( cd dist && git --git-dir="$ROOT/.git" add -A . )
TREE="$(git write-tree)"
COMMIT="$(git commit-tree "$TREE" -m "deploy: static site $(date -u +%Y-%m-%dT%H:%MZ)")"
git update-ref refs/heads/gh-pages "$COMMIT"
unset GIT_INDEX_FILE

git push -f origin gh-pages
URL="$(git remote get-url origin | sed -E 's#git@github.com:#https://github.com/#; s#\.git$##')"
OWNER_REPO="${URL#https://github.com/}"
OWNER="${OWNER_REPO%%/*}"
REPO="${OWNER_REPO##*/}"
echo "Published: https://${OWNER}.github.io/${REPO}/"
