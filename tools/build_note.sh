#!/usr/bin/env bash
# ============================================================
# build_note.sh —— 编译模块讲义 note.tex（PLAN.md §7.1，P0-T2）
#
# 用法：
#   bash tools/build_note.sh <module-dir>
#     <module-dir>  模块目录（含 note.tex），如 modules/01-effective-potential
#
# 流程：
#   1. cd <module-dir>
#   2. latexmk -xelatex -interaction=nonstopmode note.tex
#   3. 确认 note.pdf 已生成
#   4. latexmk -c 清理辅助文件（保留 note.pdf）
#   5. 传播 latexmk 退出码并清晰打印（EXIT_CODE=N）
#
# 退出码：latexmk 的退出码；latexmk 成功但 note.pdf 缺失时为 1；
#         用法/路径错误为 2。清理失败只告警，不改变退出码。
# ============================================================
set -o pipefail
set -u

usage() {
  sed -n '2,16p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
}

MODULE_DIR="${1:-}"
if [ -z "$MODULE_DIR" ]; then
  usage
  exit 2
fi
if [ ! -d "$MODULE_DIR" ]; then
  echo "ERROR: 目录不存在: $MODULE_DIR" >&2
  exit 2
fi
if [ ! -f "$MODULE_DIR/note.tex" ]; then
  echo "ERROR: 未找到 $MODULE_DIR/note.tex" >&2
  exit 2
fi

cd "$MODULE_DIR" || { echo "ERROR: 无法进入 $MODULE_DIR" >&2; exit 2; }

echo "==> 编译 note.tex（latexmk -xelatex -interaction=nonstopmode）"
latexmk -xelatex -interaction=nonstopmode note.tex
BUILD_RC=$?

if [ "$BUILD_RC" -ne 0 ]; then
  echo "EXIT_CODE=$BUILD_RC（latexmk 编译失败）"
  exit "$BUILD_RC"
fi

if [ ! -f note.pdf ]; then
  echo "EXIT_CODE=1（latexmk 退出码 0，但未生成 note.pdf）"
  exit 1
fi

PDF_BYTES=$(wc -c < note.pdf)
echo "==> note.pdf 已生成（${PDF_BYTES} bytes）"

echo "==> 清理辅助文件（latexmk -c，保留 note.pdf）"
latexmk -c
CLEAN_RC=$?
if [ "$CLEAN_RC" -ne 0 ]; then
  echo "WARN: latexmk -c 退出码 $CLEAN_RC（辅助文件可能未清理干净）" >&2
fi

echo "EXIT_CODE=$BUILD_RC"
exit "$BUILD_RC"
