#!/usr/bin/env python3
"""
build_figures.py — compile every standalone figure .tex in a chapter's
figures/ folder to an .svg beside it.

In the pipeline standard, each figure is already its own standalone LaTeX
file (one tikzpicture, fixed preamble). So there is NOTHING to extract —
we just compile each file and convert its cropped PDF to SVG. This is the
whole point of authoring figures separately: the build step is trivial and
cannot be confused by prose.

Usage:
    python3 build_figures.py CHAPTER_DIR

    CHAPTER_DIR must contain a figures/ subfolder of *.tex files.
    Produces figures/<name>.svg for each figures/<name>.tex.

Exit code 0 only if every figure compiled; non-zero otherwise.
"""
import sys
import os
import glob
import subprocess
import tempfile
import shutil


def compile_figure(tex_path: str) -> bool:
    name = os.path.splitext(os.path.basename(tex_path))[0]
    fig_dir = os.path.dirname(tex_path)
    out_svg = os.path.join(fig_dir, name + ".svg")
    workdir = tempfile.mkdtemp()
    try:
        shutil.copy(tex_path, os.path.join(workdir, "fig.tex"))
        proc = subprocess.run(
            ["xelatex", "-interaction=nonstopmode", "-halt-on-error", "fig.tex"],
            cwd=workdir, env=dict(os.environ),
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=180,
        )
        pdf_path = os.path.join(workdir, "fig.pdf")
        if proc.returncode != 0 or not os.path.exists(pdf_path):
            sys.stderr.write("\n--- %s failed ---\n" % name)
            sys.stderr.write(proc.stdout.decode("utf-8", "replace")[-1500:])
            return False
        import fitz
        doc = fitz.open(pdf_path)
        svg = doc[0].get_svg_image()
        doc.close()
        with open(out_svg, "w", encoding="utf-8") as f:
            f.write(svg)
        return True
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def main():
    if len(sys.argv) != 2:
        sys.stderr.write("usage: build_figures.py CHAPTER_DIR\n")
        return 2
    fig_dir = os.path.join(sys.argv[1], "figures")
    if not os.path.isdir(fig_dir):
        print("no figures/ folder — nothing to build")
        return 0
    tex_files = sorted(glob.glob(os.path.join(fig_dir, "*.tex")))
    if not tex_files:
        print("no figure .tex files found")
        return 0
    failures = 0
    for tex in tex_files:
        ok = compile_figure(tex)
        print(f"{os.path.basename(tex)}: {'OK' if ok else 'FAILED'}")
        if not ok:
            failures += 1
    total = len(tex_files)
    print(f"\n{total - failures}/{total} figures compiled")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
