#!/usr/bin/env bash
# build.sh — run the whole pipeline for one chapter.
# Usage:  ./build.sh content/ch10
set -euo pipefail

CHAPTER="${1:-content/ch10}"
HERE="$(cd "$(dirname "$0")" && pwd)"

echo "==> [1/2] building figures in ${CHAPTER}/figures"
python3 "${HERE}/scripts/build_figures.py" "${CHAPTER}"

echo "==> [2/2] assembling ${CHAPTER}/sections → HTML + PDF"
python3 "${HERE}/scripts/render.py" "${CHAPTER}"

echo
echo "Done. Outputs in ${CHAPTER}/output/:"
echo "  index.html   (open in a browser — phone-first, KaTeX math)"
echo "  print.pdf    (print/lab copy)"
echo "  figures/     (compiled SVGs)"
