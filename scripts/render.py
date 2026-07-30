#!/usr/bin/env python3
r"""
render.py — assemble a chapter's sections/ into phone-first HTML and print PDF.

Chapter layout (replicable for every chapter):
  CHAPTER_DIR/
    chapter.yaml          # number, title, course, …
    sections/
      00-intro.md         # optional lead-in (no # heading)
      01-….md             # each file is one numbered section (# …)
      99-summary.md       # often {.unnumbered}
    figures/
    output/

Usage:
    python3 render.py CHAPTER_DIR
"""
import sys
import os
import glob
import subprocess
import tempfile
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
HTML_TEMPLATE = os.path.join(HERE, "template.html")
TEX_TEMPLATE = os.path.join(HERE, "template.tex")
CLS_FILE = os.path.join(HERE, "urdu-textbook.cls")


def fix_pdf_latex(tex):
    """Post-process Pandoc LaTeX for RTL Urdu + Latin islands.

    Body font is Noto Nastaliq Urdu — it has almost no Latin glyphs.
    Anything left as bare ASCII (SI, GPS, 3.56E9, Halliday, …) becomes □.
    Wrap those islands in \\en{…} (Noto Sans via polyglossia).

    Tables/math/commands are protected first so ``&`` stays inside
    longtable/tabular (otherwise XeLaTeX: Misplaced alignment tab).
    """
    import re

    # Pandoc ``…'' / ''…`` quotes are ASCII; Nastaliq has no those glyphs.
    tex = re.sub(r"''([^`\n]+)``", r"”\1“", tex)
    tex = re.sub(r"``([^'\n]+)''", r"“\1”", tex)

    # Em/en dashes often missing from Nastaliq → LTR hyphen.
    tex = tex.replace("—", r"\en{--}")
    tex = tex.replace("–", r"\en{-}")

    # (english phrase) -> \en{(english phrase)}
    def wrap_paren(m):
        return r"\en{(%s)}" % m.group(1)

    tex = re.sub(
        r"(?<!\\)\((?!\\)([A-Za-z][A-Za-z0-9\s\-\.,;:\/+]*)\)",
        wrap_paren,
        tex,
    )
    # Latin \text{…} in math → \mathrm{…}
    tex = re.sub(
        r"\\text\{([A-Za-z][^}]*)\}",
        r"\\mathrm{\1}",
        tex,
    )

    def fix_caption(m):
        body = m.group(1)
        body = re.sub(r"\\\((.+?)\\\)", r"\\hbox{$\1$}", body)
        return "\\caption{" + body + "}"

    tex = re.sub(
        r"\\caption\{((?:[^{}]|\{[^}]*\})*)\}",
        fix_caption,
        tex,
        flags=re.DOTALL,
    )

    protected = []

    def _protect(m):
        protected.append(m.group(0))
        # One PUA char encodes the index — no digits/letters for the wrapper to eat.
        idx = len(protected) - 1
        return "\uE000%s\uE001" % chr(0xE100 + idx)

    # Whole environments first (column specs may contain @, &, nested braces).
    for env in ("longtable", "tabular", "tabular*", "table", "figure"):
        tex = re.sub(
            r"\\begin\{%s\}.*?\\end\{%s\}" % (re.escape(env), re.escape(env)),
            _protect,
            tex,
            flags=re.DOTALL,
        )

    # Math and already-wrapped islands.
    for pat in (
        r"\$\$[\s\S]*?\$\$",
        r"\$[^$\n]+\$",
        r"\\\([\s\S]*?\\\)",
        r"\\\[[\s\S]*?\\\]",
        r"\\en\{[^{}]*\}",
        r"\\(?:mathrm|mathbf|mathit|mathsf|hbox|text|textbf|textit|texttt|textsf)\{[^{}]*\}",
        r"\\(?:hypertarget|hyperlink|label|includegraphics|url|href|color|textcolor)\{[^{}]*\}(?:\{[^{}]*\})*",
        r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:\{[^{}]*\})*",
    ):
        tex = re.sub(pat, _protect, tex)

    def _wrap_latin(m):
        return r"\en{%s}" % m.group(0)

    tex = re.sub(
        r"[A-Za-z][A-Za-z0-9./+\-]*|(?<![0-9.])[0-9]+(?:\.[0-9]+)?",
        _wrap_latin,
        tex,
    )

    for i in range(len(protected) - 1, -1, -1):
        tex = tex.replace("\uE000%s\uE001" % chr(0xE100 + i), protected[i])
    return tex


def load_chapter_yaml(path):
    """Minimal flat-YAML reader (no PyYAML dependency)."""
    meta = {}
    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if ":" not in line:
                continue
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip()
            if val.startswith("[") and val.endswith("]"):
                inner = val[1:-1].strip()
                meta[key] = [
                    x.strip().strip('"').strip("'")
                    for x in inner.split(",") if x.strip()
                ]
            elif val in ("null", "Null", "~"):
                meta[key] = None
            else:
                meta[key] = val.strip('"').strip("'")
    return meta


def assemble_markdown(chapter_dir, meta):
    """Concatenate sections/*.md in sorted order into one Pandoc source."""
    sec_dir = os.path.join(chapter_dir, "sections")
    if not os.path.isdir(sec_dir):
        raise FileNotFoundError("no sections/ in %s" % chapter_dir)
    files = sorted(glob.glob(os.path.join(sec_dir, "*.md")))
    if not files:
        raise FileNotFoundError("no .md files in %s" % sec_dir)

    parts = []
    # YAML front matter for Pandoc variables
    parts.append("---")
    parts.append('title: "%s"' % meta.get("title", "").replace('"', '\\"'))
    parts.append("chapter: %s" % meta.get("chapter", ""))
    if meta.get("course"):
        parts.append('course: "%s"' % meta["course"])
    parts.append("---")
    parts.append("")

    for path in files:
        with open(path, encoding="utf-8") as f:
            text = f.read().strip()
        if text:
            parts.append(text)
            parts.append("")
    return "\n".join(parts), files


def pandoc_vars(meta):
    return [
        "-V", "title=%s" % meta.get("title", ""),
        "-V", "chapter=%s" % meta.get("chapter", ""),
    ]


def build_html(md_path, out_dir, meta):
    out_html = os.path.join(out_dir, "index.html")
    cmd = [
        "pandoc", md_path,
        "-s",
        "-f", "markdown+tex_math_dollars+yaml_metadata_block",
        "-t", "html5",
        "--mathjax",
        "--template", HTML_TEMPLATE,
        *pandoc_vars(meta),
        "-o", out_html,
    ]
    subprocess.run(cmd, check=True)
    return out_html


def svgs_to_pdf(chapter_dir, workdir):
    import fitz
    fig_src = os.path.join(chapter_dir, "figures")
    fig_out = os.path.join(workdir, "figures")
    os.makedirs(fig_out, exist_ok=True)
    if not os.path.isdir(fig_src):
        return
    for fn in os.listdir(fig_src):
        if fn.endswith(".svg"):
            svg_path = os.path.join(fig_src, fn)
            pdf_path = os.path.join(fig_out, fn[:-4] + ".pdf")
            doc = fitz.open()
            svgdoc = fitz.open(svg_path)
            pdfbytes = svgdoc.convert_to_pdf()
            svgdoc.close()
            src = fitz.open("pdf", pdfbytes)
            doc.insert_pdf(src)
            doc.save(pdf_path)
            doc.close()


def build_pdf(md_text, chapter_dir, out_dir, meta):
    out_pdf = os.path.join(out_dir, "print.pdf")
    workdir = tempfile.mkdtemp()
    try:
        md = md_text.replace(".svg)", ".pdf)")
        tmp_md = os.path.join(workdir, "chapter.md")
        with open(tmp_md, "w", encoding="utf-8") as f:
            f.write(md)
        svgs_to_pdf(chapter_dir, workdir)
        # Class file must be on TeX's search path
        shutil.copy(CLS_FILE, os.path.join(workdir, "urdu-textbook.cls"))

        tex_path = os.path.join(workdir, "chapter.tex")
        subprocess.run([
            "pandoc", tmp_md,
            "-s",
            "-f", "markdown+tex_math_dollars+yaml_metadata_block",
            "--template", TEX_TEMPLATE,
            "--top-level-division=section",
            "-t", "latex",
            *pandoc_vars(meta),
            "-o", tex_path,
        ], check=True)

        with open(tex_path, encoding="utf-8") as f:
            tex = f.read()
        tex = fix_pdf_latex(tex)
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(tex)

        proc = None
        for _ in range(2):
            proc = subprocess.run(
                ["xelatex", "-interaction=nonstopmode", "-halt-on-error",
                 "chapter.tex"],
                cwd=workdir, env=dict(os.environ),
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=240,
            )
        built = os.path.join(workdir, "chapter.pdf")
        if proc.returncode != 0 or not os.path.exists(built):
            sys.stderr.write(proc.stdout.decode("utf-8", "replace")[-3000:])
            raise RuntimeError("xelatex failed")
        try:
            shutil.copy(built, out_pdf)
        except PermissionError:
            alt = os.path.join(out_dir, "print-new.pdf")
            shutil.copy(built, alt)
            sys.stderr.write(
                "warning: could not overwrite print.pdf (file open?); "
                "wrote %s instead\n" % alt
            )
            return alt
        return out_pdf
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def main():
    if len(sys.argv) != 2:
        sys.stderr.write("usage: render.py CHAPTER_DIR\n")
        return 2
    chapter_dir = sys.argv[1]
    yaml_path = os.path.join(chapter_dir, "chapter.yaml")
    if not os.path.exists(yaml_path):
        sys.stderr.write("no chapter.yaml in %s\n" % chapter_dir)
        return 2

    meta = load_chapter_yaml(yaml_path)
    if "chapter" not in meta or "title" not in meta:
        sys.stderr.write("chapter.yaml must set chapter: and title:\n")
        return 2

    md_text, files = assemble_markdown(chapter_dir, meta)
    print("sections (%d):" % len(files))
    for p in files:
        print("  -", os.path.basename(p))

    out_dir = os.path.join(chapter_dir, "output")
    os.makedirs(out_dir, exist_ok=True)

    fig_src = os.path.join(chapter_dir, "figures")
    if os.path.isdir(fig_src):
        fig_dst = os.path.join(out_dir, "figures")
        if os.path.isdir(fig_dst):
            shutil.rmtree(fig_dst)
        shutil.copytree(fig_src, fig_dst,
                        ignore=shutil.ignore_patterns("*.tex"))

    # Write assembled source for debugging / HTML pandoc input
    assembled = os.path.join(out_dir, "_assembled.md")
    with open(assembled, "w", encoding="utf-8") as f:
        f.write(md_text)

    html = build_html(assembled, out_dir, meta)
    print("HTML ->", html)
    pdf = build_pdf(md_text, chapter_dir, out_dir, meta)
    print("PDF  ->", pdf)
    return 0


if __name__ == "__main__":
    sys.exit(main())
