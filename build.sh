#!/usr/bin/env bash
# build.sh — compile one chapter, or the whole book.
#
# Usage:
#   ./build.sh content/ch01     # one chapter → content/ch01/output/
#   ./build.sh book             # all chapters → output/ (single HTML + PDF)
#   ./build.sh                  # same as: ./build.sh book
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
TARGET="${1:-book}"

build_chapter() {
  local CHAPTER="$1"
  echo "==> [1/2] building figures in ${CHAPTER}/figures"
  python3 "${HERE}/scripts/build_figures.py" "${CHAPTER}"

  echo "==> [2/2] assembling ${CHAPTER}/sections → HTML + PDF"
  python3 "${HERE}/scripts/render.py" "${CHAPTER}"

  echo
  echo "Done. Chapter outputs in ${CHAPTER}/output/:"
  echo "  index.html   (phone-first HTML)"
  echo "  print.pdf    (print/lab copy)"
}

build_book() {
  echo "==> building figures for every chapter"
  local d
  for d in "${HERE}"/content/ch*; do
    [ -d "$d" ] || continue
    [ -f "$d/chapter.yaml" ] || continue
    echo "---- figures: $d"
    python3 "${HERE}/scripts/build_figures.py" "$d"
  done

  echo "==> assembling whole book → output/"
  python3 "${HERE}/scripts/render_book.py" "${HERE}"

  echo
  echo "Done. Book outputs in output/:"
  echo "  index.html   (full book, phone-first HTML + TOC)"
  echo "  print.pdf    (full book, continuous page numbers)"
  echo "  figures/     (figures namespaced per chapter)"
}

case "$TARGET" in
  book|all|.)
    build_book
    ;;
  content/*|*/content/*)
    build_chapter "$TARGET"
    ;;
  *)
    if [ -d "$TARGET" ] && [ -f "$TARGET/chapter.yaml" ]; then
      build_chapter "$TARGET"
    else
      echo "usage: ./build.sh content/chNN   # one chapter" >&2
      echo "       ./build.sh book           # whole book" >&2
      exit 2
    fi
    ;;
esac
