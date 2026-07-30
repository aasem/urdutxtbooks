# Urdu textbook pipeline — reproducible toolchain.
# Build:  docker build -t urdu-pipeline .
# Run:    see run.sh / README.md
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# --- system packages ---
# texlive-xetex        : XeLaTeX engine
# texlive-lang-arabic  : bidi + polyglossia Urdu support
# texlive-latex-extra  : titlesec, caption, standalone, etc.
# fonts-noto-*         : Nastaliq (body) + Naskh/math coverage
# pandoc               : Markdown -> HTML/LaTeX
# python3 + pymupdf    : SVG/PDF conversion
RUN apt-get update && apt-get install -y --no-install-recommends \
      texlive-xetex \
      texlive-lang-arabic \
      texlive-latex-extra \
      texlive-fonts-recommended \
      fonts-noto-core \
      fonts-noto-extra \
      fonts-noto-ui-core \
      fontconfig \
      pandoc \
      python3 \
      python3-pip \
      ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# PyMuPDF for SVG<->PDF conversion (pinned)
RUN pip3 install --no-cache-dir --break-system-packages pymupdf==1.28.0

# Confirm Nastaliq is available from fonts-noto-core
RUN mkdir -p /usr/share/fonts/urdu \
    && (fc-list | grep -qi "Noto Nastaliq Urdu" \
        || echo "note: install Noto Nastaliq Urdu if missing") \
    && fc-cache -f

WORKDIR /work
COPY . /work

# Sanity: fail the build early if a core tool is missing
RUN xelatex --version >/dev/null \
    && pandoc --version >/dev/null \
    && python3 -c "import fitz" \
    && echo "toolchain OK"

CMD ["bash"]
