# طبیعیات — University Physics (Urdu)

Urdu translation of selected chapters from **Halliday / Resnick / Walker**, course **PHYS-101**.
This repo is **one book only**. Translators edit Markdown under `content/`.
Admins compile HTML/PDF with Docker. You do **not** need TeX or Docker to contribute.

Book metadata lives in `book.yaml` (`title`, `title_en`, `course`, `source`).

## Who does what

| Role | You do | You do not |
|------|--------|------------|
| **Translator** | Fork → branch → edit a section/chapter → open a PR | Run Docker, commit `output/`, change `scripts/` |
| **Admin / maintainer** | Review PRs, run the Docker build, publish HTML/PDF | Expect translators to ship binaries |

## For translators

```bash
git clone https://github.com/aasem/urdutxtbooks.git
cd urdutxtbooks
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

Two different Docker commands:

| Command | What it does | When to run |
|---------|--------------|-------------|
| `docker build -t urdu-pipeline .` | Builds the **image** (TeX, Pandoc, fonts, Python) | **Once** the first time; again **only** if `Dockerfile` or toolchain deps change |
| `docker run … ./build.sh content/chNN` | Compiles a **chapter** into HTML/PDF | **Every time** you want fresh output after content/PR merges |

Editing Markdown or figures does **not** require `docker build` again — only `docker run`.

### Setup

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows/macOS) or Docker Engine (Linux).
2. On Windows: start **Docker Desktop** and wait until it shows running.
3. Open a terminal in the **repo root** (folder that contains `Dockerfile`).

### 1) Build the image (rare)

**Windows (PowerShell)** and **Linux / macOS**:

```bash
docker build -t urdu-pipeline .
```

First build can take several minutes. After that, reuse the `urdu-pipeline` image until the Dockerfile changes.

### 2) Compile a chapter (common)

**Windows (PowerShell)** — Docker Desktop:

```powershell
docker run --rm -v "${PWD}:/work" urdu-pipeline ./build.sh content/ch01
docker run --rm -v "${PWD}:/work" urdu-pipeline ./build.sh content/ch10
```

**Linux / macOS** (bash):

```bash
docker run --rm -v "$PWD:/work" urdu-pipeline ./build.sh content/ch01
docker run --rm -v "$PWD:/work" urdu-pipeline ./build.sh content/ch10
```

**All chapters**

PowerShell:

```powershell
foreach ($d in Get-ChildItem content -Directory -Filter "ch*") {
  docker run --rm -v "${PWD}:/work" urdu-pipeline ./build.sh ("content/" + $d.Name)
}
```

Linux / macOS:

```bash
for d in content/ch*; do
  docker run --rm -v "$PWD:/work" urdu-pipeline ./build.sh "$d"
done
```

Outputs land in `content/chNN/output/` (`index.html`, `print.pdf`). Those folders are gitignored — publish from CI or a release; do not ask translators to commit them.

Pipeline inside the container: `scripts/build_figures.py` (TikZ → SVG), then `scripts/render.py` (sections → HTML + PDF).

## Repo map

```
book.yaml          # this book’s title / course / language
content/           # ← translators work here
scripts/           # build toolchain (maintainers)
build.sh           # ./build.sh content/chNN
Dockerfile         # reproducible TeX + Pandoc + fonts
```

## More books

Use a **separate GitHub repo per book**. Clone **urdutxtbooks** (طبیعیات) as a template; keep the same `content/chNN` + `scripts` + `Dockerfile` shape. Shared pipeline updates can later move into a template repo or a small shared package — duplication is fine until then.

## Notes

- Figure labels drawn in TikZ become outlines in SVG (not selectable text).
- HTML math uses the KaTeX CDN unless you vendor it in `scripts/template.html`.
