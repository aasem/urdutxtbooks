# Urdu Textbook Pipeline — local test build

This is the minimal, foolproof pipeline: Markdown sections per chapter,
standalone figure files, producing a **phone-first HTML** page and a
**print PDF**. No GitHub, no CI yet — everything runs on your machine.

## The authoring standard (what a contributor writes)

Each chapter is a folder under `content/`:

```
content/ch10/
  chapter.yaml       <- number, title, course, status, contributors
  sections/
    00-intro.md      <- optional lead-in (no numbered heading)
    01-….md          <- one file per section; starts with `# Title`
    02-….md
    99-summary.md    <- often `# خلاصہ {.unnumbered}`
  figures/
    fig-1.tex        <- one standalone TikZ figure per file
    …
  output/            <- generated; not authored
```

At build time the pipeline concatenates `sections/*.md` (sorted by
filename), prefixes a formal chapter opening from `chapter.yaml`, and
numbers sections as `10.1`, `10.2`, … (Western digits).

**`sections/*.md` may contain only:**

- Urdu prose (normal text, right-to-left handled automatically)
- English technical terms inline, as plain text: `... **صلب جسم** (rigid body) ...`
- Math: `$...$` inline and `$$...$$` display (standard LaTeX inside)
- Figures: `![caption text](figures/fig-N.svg)`
- One top-level `#` heading per section file (becomes e.g. `10.1`)

Nothing else — no raw LaTeX in prose, no custom macros, no HTML. That
constraint is what keeps the pipeline foolproof and lets anyone with good
Urdu + basic Markdown contribute. TikZ lives **only** in `figures/*.tex`.

**Each `figures/fig-N.tex`** is a complete standalone document: the fixed
preamble (do not edit) plus exactly one `tikzpicture`. Available colors:
`seccolor, accent, accent2, rulecolor, lightfill`.

**Layout / typography** live in `scripts/urdu-textbook.cls` (PDF) and
`scripts/template.html` (HTML) — not in chapter content. Extend the class
when you need a more formal textbook look (theorem environments, running
headers, etc.).

## How to run

### Option A — Docker (reproducible; recommended)

```bash
docker build -t urdu-pipeline .
docker run --rm -v "$PWD:/work" urdu-pipeline ./build.sh content/ch10
```

On PowerShell use `${PWD}` instead of `$PWD`.

Outputs land in `content/ch10/output/` on your host.

### Option B — directly on your machine

Requires: XeLaTeX (with `texlive-lang-arabic`), Pandoc, Python 3 with
`pymupdf`, and the **Noto Nastaliq Urdu** font installed.

```bash
pip3 install pymupdf==1.28.0
./build.sh content/ch10
```

## What each step does

1. **`scripts/build_figures.py`** — compiles every `figures/*.tex` with
   XeLaTeX and converts each to `figures/*.svg` (via PyMuPDF).

2. **`scripts/render.py`** — reads `chapter.yaml`, concatenates
   `sections/*.md`, then renders twice:
   - **HTML** (`index.html`): centered chapter opening; sections numbered
     `N.1`, `N.2`, …; math via **KaTeX**; figures as `<img>` to SVGs.
   - **PDF** (`print.pdf`): same structure via `urdu-textbook.cls`;
     Western page/section numbers; SVGs converted to PDF for include.

## Checking the output

- Open `content/ch10/output/index.html` in a browser, then narrow the
  window to a phone width. Chapter title should be centered at top;
  sections numbered `10.1` etc.; equations sit correctly in RTL text.
- Open `content/ch10/output/print.pdf`. Expect a formal chapter opening
  (باب 10 / گردش), Western page numbers, and sections `10.1`–`10.5`.

## Notes / known limits

- Text **inside** figures (axis labels etc.) is drawn as vector outlines in
  the SVG — not selectable or translatable through the pipeline. Keep
  figure labels to symbols/English where possible.
- HTML math needs the KaTeX CDN (internet) as written. For fully offline
  use, download KaTeX and point the two `<link>`/`<script>` tags in
  `scripts/template.html` at local copies.
- This is the ch10 physics chapter (rotation) as the worked test case.
  Add more chapters as sibling folders under `content/` using the same
  `chapter.yaml` + `sections/` layout.
