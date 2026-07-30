# University Physics (Urdu)

Urdu translation of selected chapters from **Halliday / Resnick / Walker**, course **PHYS-101**.
This repo is **one book only**.

- **Translators** edit Markdown under `content/` (no Docker, no TeX).
- **Admins** review PRs, compile HTML/PDF with Docker, then merge and publish.

Book metadata lives in `book.yaml`.

---

## Who does what

| Role | You do | You do not |
|------|--------|------------|
| **Translator** | Copy the project → edit a section/chapter → ask to merge your changes | Run Docker, commit `output/`, change `scripts/` |
| **Admin** | Review that request, optionally build with Docker, approve & merge, publish HTML/PDF | Expect translators to ship PDF/HTML themselves |

---

## GitHub in plain language (read this first)

You do **not** need to be a programmer. You need these ideas:

| Word | Meaning |
|------|---------|
| **Repository (repo)** | The project folder on GitHub — all book files live here: https://github.com/aasem/urdutxtbooks |
| **Clone** | Download a copy of the repo to your computer |
| **Fork** | Your own copy of the repo **under your GitHub account**. You push to *your* copy, then ask the original project to take your changes |
| **Branch** | A named line of work (e.g. `translate/ch01-time`) so you do not edit `main` directly. Think of it as a draft notebook |
| **Commit** | A saved snapshot of your edits with a short message |
| **Push** | Upload your commits from your computer to GitHub |
| **Pull Request (PR)** | A formal request: “Please review my branch and merge it into `main`.” Discussion and review happen on the PR page |
| **Merge** | Admin accepts the PR; your text becomes part of the official book on `main` |
| **`main`** | The official, up-to-date branch of the book. Always start new work from a fresh `main` |

**Typical student path:** Fork → Clone your fork → New branch → Edit in Obsidian → Commit → Push → Open PR → Fix review comments → Admin merges.

Install once on your machine:

1. A free [GitHub account](https://github.com/join)
2. [Git for Windows](https://git-scm.com/download/win) (or Git on Linux/macOS)
3. [Obsidian](https://obsidian.md) (recommended) or VS Code / Cursor

On Windows you can use **Git Bash** (comes with Git) or PowerShell for the commands below.

---

## For translators

You only need **Git** + **Obsidian** (or VS Code). You do **not** need Docker or LaTeX.

### 1) Get the repo onto your computer

**Option A — fork (usual for students)**

1. Sign in to GitHub.
2. Open https://github.com/aasem/urdutxtbooks
3. Click **Fork** (top right). GitHub creates `https://github.com/<your-username>/urdutxtbooks`
4. On **your** fork page, click the green **Code** button, copy the HTTPS URL, then in a terminal:

```bash
git clone https://github.com/<your-username>/urdutxtbooks.git
cd urdutxtbooks
```

Replace `<your-username>` with your GitHub username.

5. Link the original project as `upstream` (do this once), so you can later download updates:

```bash
git remote add upstream https://github.com/aasem/urdutxtbooks.git
git remote -v
```

You should see `origin` (your fork) and `upstream` (aasem’s repo).

**Option B — clone without forking**  
Only if an admin already gave you write access to `aasem/urdutxtbooks`:

```bash
git clone https://github.com/aasem/urdutxtbooks.git
cd urdutxtbooks
```

Then use `origin` instead of `upstream` in the pull commands below.

### 2) Update `main` and create a branch

Every time you start new work:

```bash
git checkout main
git pull upstream main
git checkout -b translate/ch01-time
```

If Option B (no fork): use `git pull origin main` instead of `upstream`.

- `checkout main` — go to the official branch  
- `pull` — download the latest book text  
- `checkout -b …` — create and switch to your draft branch  

Branch name ideas: `translate/ch01-measuring`, `translate/ch10-torque`. One PR ≈ one clear piece of work.

If `git pull upstream main` says it does not know `upstream`, redo step 1.5.

### 3) What files you may edit

**Only** files under `content/`.

Good PR sizes:

- **One section:** e.g. `content/ch01/sections/02-time.md`
- **One chapter:** everything under `content/ch01/`
- **More than one chapter:** only if an admin asked you to

```
content/
  ch01/
    chapter.yaml      # chapter number, Urdu title, status, contributors
    sections/
      00-intro.md     # optional intro (no # heading)
      01-….md         # one section file; starts with # Title
      99-summary.md   # often # خلاصہ {.unnumbered}
    figures/          # figures (usually leave alone unless asked)
book.yaml             # book info — do not change unless asked
```

When you edit a chapter, add your name to `contributors` inside that chapter’s `chapter.yaml`.

Do **not** edit `scripts/`, `Dockerfile`, or anything under `output/`.

### 4) Write Urdu + math in Obsidian

1. Install Obsidian → **Open folder as vault** → select the `urdutxtbooks` folder (the one you cloned).
2. In the file list, open e.g. `content/ch01/sections/02-time.md`.
3. Turn on **Live Preview** or **Reading** view so math shows correctly.
4. Write Urdu as normal. For equations use:
   - Inline: `$E = mc^2$`
   - Display: `$$ \rho = \frac{m}{V} $$`
5. English technical terms: `**صلب جسم** (rigid body)` — Urdu bold, English in parentheses.

If the editor feels left-to-right only: Obsidian settings → enable RTL for the note or editor.

**Allowed:** Urdu, `(english)`, `$math$`, Markdown tables, `![caption](figures/fig-1.svg)`, one `#` heading per section file.

**Not allowed:** HTML tags, random LaTeX document code, changing build scripts.

What you see in Obsidian = text + equations. It is **not** the final printed book (admins build that).

Save files in Obsidian (normal save). Then go back to the terminal for Git.

### 5) Save to GitHub and open a Pull Request

In the terminal, from the `urdutxtbooks` folder, on your branch:

```bash
git status
git add content/
git status
git commit -m "Translate ch01 section on time"
git push -u origin translate/ch01-time
```

- First `status` — see what changed  
- `git add content/` — stage only translation files  
- Second `status` — confirm `scripts/` and `output/` are **not** listed  
- `commit` — save a snapshot (use your own clear message)  
- `push` — upload the branch to **your fork** on GitHub  

**Open the Pull Request (on the website):**

1. Open https://github.com/aasem/urdutxtbooks (or your fork — GitHub often shows a yellow banner **Compare & pull request** after a push).
2. Click **Pull requests** → **New pull request**.
3. Set base repository: `aasem/urdutxtbooks`, base branch: **`main`**.  
   Set compare: **your fork** and **your branch** (e.g. `translate/ch01-time`).
4. Title example: `ch01: translate time section`.
5. In the description, write what you translated and any doubts.
6. Click **Create pull request**.

You are done for now. An admin will review.

**If they ask for changes:** edit the same files in Obsidian, then:

```bash
git add content/
git commit -m "Fix review comments on time section"
git push
```

The same PR updates automatically. Do **not** open a second PR for the same work.

### 6) After your PR is merged

On GitHub the PR will show **Merged**. On your computer:

```bash
git checkout main
git pull upstream main
git branch -d translate/ch01-time
```

For the next section, create a **new** branch from updated `main` (repeat from step 2). Do not keep using an old merged branch.

### Translator troubleshooting

| Problem | What to try |
|---------|-------------|
| `git` not found | Install Git and reopen the terminal |
| Permission denied / login failed when pushing | Use GitHub login/token; or GitHub Desktop if the terminal is hard |
| Merge conflicts | Ask an admin; do not panic. Often fixed by updating `main` first |
| I edited the wrong file | Say so on the PR; admins can help revert |
| Math looks wrong in Obsidian | Check you used `$...$` not missing dollars; try Live Preview |

---

## For admins

### Review and approve a PR

1. Open the PR → **Files changed**. Prefer diffs only under `content/`.
2. Check Urdu, math, and `(english terms)`.
3. Optional: check out the PR branch and run Docker (below); skim HTML/PDF for □, broken figures, tables.
4. **Request changes** or **Approve**.
5. **Merge** into `main`.
6. Delete the branch when GitHub offers it.
7. Publish new HTML/PDF (Pages, host, or release). Do not ask students to commit `output/`.

Explain review comments in simple language on the PR so students learn.

### Compile with Docker

| Command | Meaning | When |
|---------|---------|------|
| `docker build -t urdu-pipeline .` | Build the toolchain **image** | Once; again only if `Dockerfile` changes |
| `docker run … ./build.sh …` | Compile chapter or whole book | Whenever you need fresh HTML/PDF |

#### Setup

1. [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows/macOS) or Docker Engine (Linux).
2. Windows: start Docker Desktop and wait until it is running.
3. Open a terminal in the repo root (folder that contains `Dockerfile`).

#### Image (rare)

```bash
docker build -t urdu-pipeline .
```

#### Build a PR branch before merging

```bash
git fetch origin
gh pr checkout <number>
# or: git checkout <pr-branch-name>
```

**Windows (PowerShell):**

```powershell
docker run --rm -v "${PWD}:/work" urdu-pipeline ./build.sh book
docker run --rm -v "${PWD}:/work" urdu-pipeline ./build.sh content/ch01
```

**Linux / macOS:**

```bash
docker run --rm -v "$PWD:/work" urdu-pipeline ./build.sh book
docker run --rm -v "$PWD:/work" urdu-pipeline ./build.sh content/ch01
```

| Target | Command | Output |
|--------|---------|--------|
| One chapter | `./build.sh content/ch01` | `content/ch01/output/` |
| Whole book | `./build.sh book` | `output/` — HTML (desktop: TOC on the right) + PDF |

Then merge on GitHub. If you publish from `main`, check out `main`, pull, and run `./build.sh book` again.

Close `print.pdf` before rebuilding if the file is locked.

### Admin end-to-end

1. Student opens PR.  
2. Check out the branch → `docker run … ./build.sh book`.  
3. Open `output/index.html` and/or `output/print.pdf`.  
4. Approve + merge.  
5. Publish HTML (e.g. GitHub Pages) and/or distribute the PDF.

---

## Repo map

```
book.yaml          # book title / course / language
content/           # ← translators work only here
output/            # whole-book build (admins; usually gitignored)
scripts/           # build tools (admins)
build.sh
Dockerfile
```

## More books

One **GitHub repo per book**. Clone this repo as a template. Duplicating Docker/scripts is fine for now.

## Notes

- TikZ figure labels become outlines in SVG (not selectable text).
- HTML math uses the KaTeX CDN unless templates are changed to local files.
- PDF uses Noto Nastaliq Urdu; spot-check for □ after large edits.
