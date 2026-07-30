# University Physics (Urdu)

One **book** = one GitHub repo. Translators edit Markdown under `content/`.
Admins compile HTML/PDF with Docker. You do **not** need TeX or Docker to contribute.

## Who does what

| Role | You do | You do not |
|------|--------|------------|
| **Translator** | Fork → branch → edit a section/chapter → open a PR | Run Docker, commit `output/`, change `scripts/` |
| **Admin / maintainer** | Review PRs, run the Docker build, publish HTML/PDF | Expect translators to ship binaries |

## For translators

```bash
git clone https://github.com/<org>/<this-book>.git
cd <this-book>
```

Edit only under `content/`. Typical PR scopes:

- one **section** file (`content/ch01/sections/02-time.md`)
- one **chapter** folder (`content/ch01/`)
- several chapters (whole-book pass)

### Chapter layout

```
content/
  ch01/
    chapter.yaml      # chapter number, Urdu title, status, contributors
    sections/
      00-intro.md     # optional lead-in (no # heading)
      01-….md         # one numbered section; starts with `# Title`
      99-summary.md   # `# خلاصہ {.unnumbered}`
    figures/          # optional TikZ sources (+ committed .svg)
book.yaml             # book-level metadata (this repo’s identity)
```

New chapter: copy `content/ch01/`, set `chapter.yaml`, use ids `ch01`…`ch09`, then `ch10`, ….

### What you may put in a section `.md`

- Urdu prose
- English terms inline: `**صلب جسم** (rigid body)`
- Math: `$...$` and `$$...$$`
- Figures: `![caption](figures/fig-N.svg)`
- Markdown tables
- One top-level `#` heading per numbered section file

No raw LaTeX in prose, no HTML, no edits under `scripts/` or `output/`.

Add yourself under `contributors` in that chapter’s `chapter.yaml` when you touch it.

Open a PR against `main`. Keep the diff to the chapter/section you own.

## For admins — compile with Docker

```bash
docker build -t urdu-pipeline .

# one chapter
docker run --rm -v "${PWD}:/work" urdu-pipeline ./build.sh content/ch01

# all chapters (bash)
for d in content/ch*; do
  docker run --rm -v "${PWD}:/work" urdu-pipeline ./build.sh "$d"
done
```

On PowerShell, use `${PWD}` the same way. Outputs appear in `content/chNN/output/` (`index.html`, `print.pdf`). Those folders are gitignored — publish them from CI or a release, do not ask translators to commit them.

Pipeline: `scripts/build_figures.py` (TikZ → SVG) then `scripts/render.py` (sections → HTML + PDF).

## Repo map

```
book.yaml          # this book’s title / course / language
content/           # ← translators work here
scripts/           # build toolchain (maintainers)
build.sh           # ./build.sh content/chNN
Dockerfile         # reproducible TeX + Pandoc + fonts
```

## More books

Use a **separate GitHub repo per book** (recommended). Clone this repo as a template; keep the same `content/chNN` + `scripts` + `Dockerfile` shape. Shared pipeline updates can later move into a template repo or a small shared package — duplication is fine until then.

## Notes

- Figure labels drawn in TikZ become outlines in SVG (not selectable text).
- HTML math uses the KaTeX CDN unless you vendor it in `scripts/template.html`.
