% urdu-textbook.cls — XeLaTeX class for Urdu scientific chapters.
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{urdu-textbook}[2026/07/27 Urdu scientific textbook chapter]

\LoadClass[12pt,a4paper]{report}

\RequirePackage{fontspec}
\RequirePackage{amsmath}
\RequirePackage{amssymb}
\RequirePackage{graphicx}
\RequirePackage{geometry}
\RequirePackage{xcolor}
\RequirePackage{titlesec}
\RequirePackage{fancyhdr}
\RequirePackage{caption}
\RequirePackage{booktabs}
\RequirePackage{longtable}
\RequirePackage{array}
\RequirePackage[hidelinks]{hyperref}

\geometry{a4paper, margin=2.2cm, top=2.4cm, bottom=2.6cm}

\definecolor{seccolor}{RGB}{30,90,140}
\definecolor{rulecolor}{RGB}{205,150,35}

\RequirePackage{polyglossia}
\setdefaultlanguage{urdu}
\setotherlanguage{english}

\newfontfamily\urdufont[Script=Arabic,Language=Urdu,%
  BoldFont={Noto Nastaliq Urdu},AutoFakeBold=2.5]{Noto Nastaliq Urdu}
\setmainfont[Script=Arabic,Language=Urdu,%
  BoldFont={Noto Nastaliq Urdu},AutoFakeBold=2.5]{Noto Nastaliq Urdu}
\newfontfamily\englishfont{Noto Sans}
\newfontfamily\latinfont{Noto Sans}

% Math on a real math font (not Nastaliq) — fixes \sin, Latin letters, etc.
\RequirePackage{unicode-math}
\setmathfont{Latin Modern Math}
\setmathrm{Noto Sans}
\setmathsf{Noto Sans}

% English / Latin island in RTL prose (polyglossia handles direction)
\newcommand{\en}[1]{\textenglish{#1}}

\renewcommand{\thepage}{\number\value{page}}
\renewcommand{\thechapter}{\number\value{chapter}}
\renewcommand{\thesection}{\thechapter.\number\value{section}}
\renewcommand{\thesubsection}{\thesection.\number\value{subsection}}
\renewcommand{\theequation}{\thechapter.\number\value{equation}}

\titleformat{\chapter}[display]
  {\normalfont\color{seccolor}\filcenter}
  {\large\bfseries باب~\latinfont\thechapter}
  {1.2ex}
  {\Huge\bfseries}
  [\vspace{0.6em}{\color{rulecolor}\titlerule[1.2pt]}\vspace{1.2em}]
\titlespacing*{\chapter}{0pt}{20pt}{28pt}

\titleformat{\section}
  {\color{seccolor}\Large\bfseries}
  {\latinfont\thesection}
  {0.6em}{}
\titleformat{\subsection}
  {\color{seccolor}\large\bfseries}
  {\latinfont\thesubsection}
  {0.5em}{}
\titleformat{\subsubsection}{\bfseries}{}{0pt}{}

\setcounter{secnumdepth}{2}

\pagestyle{fancy}
\fancyhf{}
\fancyfoot[C]{\latinfont\thepage}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}
\fancypagestyle{plain}{%
  \fancyhf{}%
  \fancyfoot[C]{\latinfont\thepage}%
  \renewcommand{\headrulewidth}{0pt}%
}

\captionsetup{font=small,labelformat=empty,textfont={color=seccolor}}

\linespread{1.55}
\setlength{\parskip}{6pt}
\setlength{\parindent}{0pt}

\newcommand{\TextbookChapter}[2]{%
  \setcounter{chapter}{\numexpr#1-1\relax}%
  \chapter{#2}%
}
