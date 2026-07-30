#!/usr/bin/env python3
r"""
render_book.py — assemble every content/ch* chapter into one book HTML + PDF.

Outputs (repo root):
  output/index.html
  output/print.pdf
  output/figures/chNN/…

Figure links are rewritten from figures/fig-N.svg → figures/chNN/fig-N.svg
so chapter figure names never collide.

Usage:
    python3 render_book.py [REPO_ROOT]
"""
import glob
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import render as R  # noqa: E402

BOOK_HTML_TEMPLATE = os.path.join(HERE, "template-book.html")


def discover_chapters(content_dir):
    """Return [(chapter_num, chapter_dir, meta), ...] sorted by chapter number."""
    found = []
    for path in glob.glob(os.path.join(content_dir, "ch*")):
        if not os.path.isdir(path):
            continue
        yaml_path = os.path.join(path, "chapter.yaml")
        if not os.path.isfile(yaml_path):
            continue
        meta = R.load_chapter_yaml(yaml_path)
        if "chapter" not in meta or "title" not in meta:
            raise ValueError("%s must set chapter: and title:" % yaml_path)
        found.append((int(meta["chapter"]), path, meta))
    if not found:
        raise FileNotFoundError("no chapters with chapter.yaml under %s" % content_dir)
    found.sort(key=lambda t: t[0])
    return found


def chapter_slug(chapter_dir):
    return os.path.basename(os.path.abspath(chapter_dir))


def assemble_chapter_body(chapter_dir):
    """Concatenate sections/*.md (no YAML front matter)."""
    sec_dir = os.path.join(chapter_dir, "sections")
    files = sorted(glob.glob(os.path.join(sec_dir, "*.md")))
    if not files:
        raise FileNotFoundError("no .md files in %s" % sec_dir)
    parts = []
    for path in files:
        with open(path, encoding="utf-8") as f:
            text = f.read().strip()
        if text:
            parts.append(text)
            parts.append("")
    return "\n".join(parts).strip() + "\n", files


def rewrite_figure_paths(md, slug):
    """figures/foo.svg → figures/<slug>/foo.svg (and .pdf)."""
    return md.replace("](figures/", "](figures/%s/" % slug)


def copy_chapter_figures(chapter_dir, slug, dest_figures_root):
    """Copy non-.tex figure assets into dest_figures_root/<slug>/."""
    src = os.path.join(chapter_dir, "figures")
    dst = os.path.join(dest_figures_root, slug)
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    os.makedirs(dst, exist_ok=True)
    if not os.path.isdir(src):
        return
    for fn in os.listdir(src):
        if fn.endswith(".tex") or fn.startswith("."):
            continue
        shutil.copy2(os.path.join(src, fn), os.path.join(dst, fn))


def svgs_to_pdf_book(chapters, workdir):
    """Convert each chapter's SVGs into workdir/figures/<slug>/*.pdf."""
    import fitz

    for _num, chapter_dir, _meta in chapters:
        slug = chapter_slug(chapter_dir)
        fig_src = os.path.join(chapter_dir, "figures")
        fig_out = os.path.join(workdir, "figures", slug)
        os.makedirs(fig_out, exist_ok=True)
        if not os.path.isdir(fig_src):
            continue
        for fn in os.listdir(fig_src):
            if not fn.endswith(".svg"):
                continue
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


def pandoc_fragment(md_text, to_format, extra_args=None):
    """Convert markdown string to a pandoc body fragment (no -s)."""
    cmd = [
        "pandoc",
        "-f", "markdown+tex_math_dollars",
        "-t", to_format,
        *(extra_args or []),
    ]
    proc = subprocess.run(
        cmd, input=md_text.encode("utf-8"),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr.decode("utf-8", "replace"))
        raise RuntimeError("pandoc failed (%s)" % to_format)
    return proc.stdout.decode("utf-8")


def build_book_html(chapters, book, out_dir):
    with open(BOOK_HTML_TEMPLATE, encoding="utf-8") as f:
        tpl = f.read()

    title = book.get("title", "")
    title_en = book.get("title_en", "")
    course = book.get("course", "")
    source = book.get("source", "")

    header = ['<header class="book-open">']
    header.append('<p class="book-title">%s</p>' % _esc(title))
    if title_en:
        header.append('<p class="book-title-en">%s</p>' % _esc(title_en))
    meta_bits = [x for x in (course, source) if x]
    if meta_bits:
        header.append('<p class="book-meta">%s</p>' % _esc(" · ".join(meta_bits)))
    header.append("</header>")

    toc = ['<nav class="toc"><h2>فہرست</h2><ol>']
    body_parts = []
    counter_css = []

    for num, chapter_dir, meta in chapters:
        slug = chapter_slug(chapter_dir)
        chap_title = meta.get("title", "")
        anchor = "ch-%s" % num
        toc.append(
            '<li><a href="#%s">باب <span class="toc-num">%s</span> — %s</a></li>'
            % (anchor, num, _esc(chap_title))
        )
        counter_css.append(
            '.chapter[data-n="%s"] .chapter-body h1:not(.unnumbered)::before '
            '{ content: "%s." counter(sec) "\\2009"; }' % (num, num)
        )

        md, _files = assemble_chapter_body(chapter_dir)
        md = rewrite_figure_paths(md, slug)
        frag = pandoc_fragment(md, "html5", extra_args=["--mathjax"])

        body_parts.append('<article class="chapter" id="%s" data-n="%s">' % (anchor, num))
        body_parts.append('<header class="chapter-open">')
        body_parts.append(
            '<div class="chap-label">باب <span class="chap-num">%s</span></div>' % num
        )
        body_parts.append('<p class="chapter-title">%s</p>' % _esc(chap_title))
        body_parts.append("</header>")
        body_parts.append('<div class="chapter-body">')
        body_parts.append(frag)
        body_parts.append("</div></article>")

        copy_chapter_figures(chapter_dir, slug, os.path.join(out_dir, "figures"))

    toc.append("</ol></nav>")

    html = tpl
    html = html.replace("$title$", _esc(title or title_en or "Book"))
    html = html.replace("$chapter-counters$", "\n".join(counter_css))
    html = html.replace("$header$", "\n".join(header))
    html = html.replace("$toc$", "\n".join(toc))
    html = html.replace("$body$", "\n".join(body_parts))

    out_html = os.path.join(out_dir, "index.html")
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(html)
    return out_html


def _esc(s):
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def build_book_pdf(chapters, book, out_dir):
    out_pdf = os.path.join(out_dir, "print.pdf")
    workdir = tempfile.mkdtemp()
    try:
        svgs_to_pdf_book(chapters, workdir)
        shutil.copy(R.CLS_FILE, os.path.join(workdir, "urdu-textbook.cls"))

        title = book.get("title", "")
        title_en = book.get("title_en", "")
        course = book.get("course", "")
        source = book.get("source", "")

        tex_parts = [
            "\\documentclass{urdu-textbook}",
            "\\begin{document}",
            "\\begin{center}",
            "{\\color{seccolor}\\Huge\\bfseries %s}\\\\[10pt]" % _tex_esc(title),
        ]
        if title_en:
            tex_parts.append(
                "{\\latinfont\\Large %s}\\\\[8pt]" % _tex_esc(title_en)
            )
        if course:
            tex_parts.append(
                "{\\latinfont\\large %s}\\\\[6pt]" % _tex_esc(course)
            )
        if source:
            tex_parts.append(
                "{\\latinfont\\small %s}" % _tex_esc(source)
            )
        tex_parts += [
            "\\end{center}",
            "{\\color{rulecolor}\\rule{\\linewidth}{1.2pt}}",
            "\\vspace{1.5em}",
            "\\clearpage",
        ]

        for num, chapter_dir, meta in chapters:
            slug = chapter_slug(chapter_dir)
            chap_title = meta.get("title", "")
            md, _files = assemble_chapter_body(chapter_dir)
            md = rewrite_figure_paths(md, slug).replace(".svg)", ".pdf)")
            body = pandoc_fragment(
                md, "latex",
                extra_args=["--top-level-division=section"],
            )
            body = R.fix_pdf_latex(body)
            tex_parts.append("\\TextbookChapter{%s}{%s}" % (num, _tex_esc(chap_title)))
            tex_parts.append(body)
            tex_parts.append("\\clearpage")

        tex_parts.append("\\end{document}")
        tex = "\n".join(tex_parts)

        tex_path = os.path.join(workdir, "book.tex")
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(tex)

        proc = None
        for _ in range(2):
            proc = subprocess.run(
                ["xelatex", "-interaction=nonstopmode", "-halt-on-error", "book.tex"],
                cwd=workdir, env=dict(os.environ),
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=600,
            )
        built = os.path.join(workdir, "book.pdf")
        if proc.returncode != 0 or not os.path.exists(built):
            sys.stderr.write(proc.stdout.decode("utf-8", "replace")[-4000:])
            # Keep failing sources for local debugging
            try:
                shutil.copy(tex_path, os.path.join(out_dir, "_book.tex"))
                log_path = os.path.join(workdir, "book.log")
                if os.path.exists(log_path):
                    shutil.copy(log_path, os.path.join(out_dir, "_book.log"))
            except OSError:
                pass
            raise RuntimeError("xelatex failed for book")
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

        # Keep assembled tex for debugging
        shutil.copy(tex_path, os.path.join(out_dir, "_book.tex"))
        return out_pdf
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def _tex_esc(s):
    """Escape LaTeX specials in plain prose (not math)."""
    s = str(s)
    repl = {
        "\\": "\\textbackslash{}",
        "&": "\\&",
        "%": "\\%",
        "$": "\\$",
        "#": "\\#",
        "_": "\\_",
        "{": "\\{",
        "}": "\\}",
        "~": "\\textasciitilde{}",
        "^": "\\textasciicircum{}",
    }
    return "".join(repl.get(c, c) for c in s)


def main():
    repo = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.getcwd())
    content_dir = os.path.join(repo, "content")
    book_yaml = os.path.join(repo, "book.yaml")
    if not os.path.isfile(book_yaml):
        sys.stderr.write("no book.yaml in %s\n" % repo)
        return 2

    book = R.load_chapter_yaml(book_yaml)
    chapters = discover_chapters(content_dir)
    print("book: %s" % book.get("title", book.get("title_en", "")))
    print("chapters (%d):" % len(chapters))
    for num, path, meta in chapters:
        print("  - %s  باب %s — %s" % (chapter_slug(path), num, meta.get("title", "")))

    out_dir = os.path.join(repo, "output")
    if os.path.isdir(os.path.join(out_dir, "figures")):
        shutil.rmtree(os.path.join(out_dir, "figures"))
    os.makedirs(out_dir, exist_ok=True)

    html = build_book_html(chapters, book, out_dir)
    print("HTML ->", html)
    pdf = build_book_pdf(chapters, book, out_dir)
    print("PDF  ->", pdf)
    return 0


if __name__ == "__main__":
    sys.exit(main())
