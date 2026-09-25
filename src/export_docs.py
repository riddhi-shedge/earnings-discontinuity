"""Render the writeup and the slide deck to PDF via headless Chrome.

    python -m src.export_docs

Chrome is used rather than a Python HTML engine because the deck's print stylesheet
(one 16:9 page per section) is written against a real browser's pagination. Figures
are exported separately as vector PDFs by ``src/export_pdf.py``.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
]

# The writeup keeps LaTeX in the markdown (GitHub renders it); for print it is
# rewritten into plain notation, since no math engine is bundled here.
# Order matters: the innermost braces must be consumed first, otherwise the
# [^{}]* groups in \frac cannot match across a nested subscript.
MATH_REPLACEMENTS = [
    (r"\\text\{([^{}]*)\}", r"\1"),
    (r"\\tfrac\{1\}\{4\}", r"1/4"),
    (r"_\{([^{}]*)\}", r"<sub>\1</sub>"),
    (r"\^\{([^{}]*)\}", r"<sup>\1</sup>"),
    (r"\\sqrt\{([^{}]*)\}", r"sqrt(\1)"),
    (r"\\frac\{([^{}]*)\}\{([^{}]*)\}", r"\1 / \2"),
    (r"\\cdot", r"·"),
    (r"\\,", r" "),
]

DOC_CSS = """
@page { size: letter; margin: 0.85in 0.9in; }
* { box-sizing: border-box; }
body {
  font: 10.5pt/1.55 "Georgia", "Times New Roman", serif;
  color: #14140f; margin: 0; -webkit-print-color-adjust: exact; print-color-adjust: exact;
}
h1 { font: 700 21pt/1.18 "Helvetica Neue", Helvetica, Arial, sans-serif;
     margin: 0 0 .18em; letter-spacing: -.01em; }
h3 { font: 400 12pt/1.35 "Helvetica Neue", Helvetica, Arial, sans-serif;
     color: #52514e; margin: 0 0 1.5em; }
h2 { font: 700 13pt/1.3 "Helvetica Neue", Helvetica, Arial, sans-serif;
     margin: 1.7em 0 .5em; border-bottom: 1px solid #e3e2dd; padding-bottom: .28em;
     break-after: avoid; page-break-after: avoid; }
p, li { margin: 0 0 .62em; }
ul { padding-left: 1.15em; }
strong { color: #000; }
em { color: #2f2f2b; }
hr { border: 0; border-top: 1px solid #e3e2dd; margin: 1.6em 0; }
table { border-collapse: collapse; width: 100%; margin: .9em 0 1.1em;
        font: 9.5pt/1.4 "Helvetica Neue", Helvetica, Arial, sans-serif;
        font-variant-numeric: tabular-nums; break-inside: avoid; page-break-inside: avoid; }
th { text-align: left; border-bottom: 1.2px solid #0b0b0b; padding: .35em .5em; font-weight: 700; }
td { border-bottom: 1px solid #eceae4; padding: .32em .5em; }
tr td:not(:first-child), tr th:not(:first-child) { text-align: right; }
code { font: 9.5pt ui-monospace, "SF Mono", Menlo, monospace;
       background: #f3f2ee; padding: .08em .3em; border-radius: 2px; }
pre { background: #f7f6f2; border: 1px solid #e3e2dd; border-radius: 4px;
      padding: .7em .85em; overflow-x: auto; break-inside: avoid; }
pre code { background: none; padding: 0; font-size: 9pt; }
.formula { text-align: center; font: 11.5pt "Georgia", serif; margin: 1em 0 1.2em; }
a { color: #1f5fa8; text-decoration: none; word-break: break-word; }
"""


GUIDE_CSS = DOC_CSS + """
/* ---- reference guide: dense, no page breaks, strong visual hierarchy ------- */
@page { size: letter; margin: 0.78in 0.82in; }
body { font-size: 9.8pt; line-height: 1.52; }

h1 { font-size: 20pt; margin: 0 0 .1em; }
h1 + h3 { font-size: 11.5pt; font-style: italic; color: #52514e; font-weight: 400;
          margin: 0 0 1.4em; border: 0; padding: 0; }

/* PART banners: strong rule, no page break -- breaks left pages a fifth full */
h1.part { font: 700 12.5pt/1.3 "Helvetica Neue", Helvetica, Arial, sans-serif;
          letter-spacing: .10em; color: #2a78d6; text-transform: uppercase;
          border-top: 2.5px solid #2a78d6; padding: .45em 0 0; margin: 2.1em 0 1.1em;
          break-after: avoid; page-break-after: avoid; }

h2 { font-size: 12pt; border-bottom: 1px solid #e3e2dd; padding-bottom: .25em;
     margin: 1.7em 0 .7em; break-after: avoid; page-break-after: avoid; }
h1.part + h2 { margin-top: 0; }

h3 { font: 700 10pt/1.3 "Helvetica Neue", Helvetica, Arial, sans-serif; color: #14140f;
     margin: 1.4em 0 .4em; font-style: normal;
     break-after: avoid; page-break-after: avoid; }

h2 + p, h3 + p, h2 + table, h3 + table { break-before: avoid; page-break-before: avoid; }

/* definitions: compact, a thin accent rule rather than a filled box */
blockquote { margin: .7em 0; padding: .35em .6em .35em .75em; border-left: 3px solid #2a78d6;
             background: #f7f9fc; font-size: 9.4pt; line-height: 1.45;
             break-inside: avoid; page-break-inside: avoid; }
blockquote p { margin: 0 0 .3em; }
blockquote p:last-child { margin-bottom: 0; }
blockquote .term { font-weight: 700; }

/* Q&A: the question leads its answer paragraph; lift it onto its own line */
p .q { display: block; font-weight: 700; color: #14140f; margin-bottom: .12em; }
p:has(> .q) { margin-top: 1.15em; }
/* a question must not be the last thing on a page */
p .q { break-after: avoid; page-break-after: avoid; }

p, li { orphans: 2; widows: 2; margin: 0 0 .62em; }
ul, ol { margin: .3em 0 .7em; padding-left: 1.2em; }
li { margin: 0 0 .3em; }
table { font-size: 8.4pt; margin: .7em 0 .85em; }
th, td { padding: .26em .4em; }
/* Let the markdown column markers (|---:|) drive alignment rather than a blanket
   rule -- these tables mix prose columns with numeric ones. Must repeat the base
   selector exactly: `th, td` alone loses on specificity to `tr td:not(:first-child)`.
   Markdown emits inline styles for :-marked columns, which still win over this. */
tr td:not(:first-child), tr th:not(:first-child) { text-align: left; }
pre { margin: .7em 0; padding: .5em .7em; }
pre code { font-size: 8.4pt; }
hr { margin: 1.2em 0; }
"""


def find_chrome() -> str:
    for path in CHROME_CANDIDATES:
        if Path(path).exists():
            return path
    found = shutil.which("chromium") or shutil.which("google-chrome")
    if found:
        return found
    raise RuntimeError("No Chrome/Chromium found; cannot render PDF.")


CODE_SPAN = re.compile(r"```.*?```|`[^`\n]+`", re.S)


def _tag_structure(html: str) -> str:
    """Tag part banners, chapter openings and recap boxes for the print stylesheet.

    Also strips the horizontal rules that markdown emits either side of a PART
    banner, so the banner and the chapter beneath it are adjacent siblings and the
    "don't break between them" rule can match.
    """
    html = re.sub(r"<h1>(PART\b)", r'<h1 class="part">\1', html)
    # <hr> immediately before or after a part banner
    html = re.sub(r"<hr\s*/?>\s*(<h1 class=\"part\">)", r"\1", html)
    html = re.sub(r"(</h1>)\s*<hr\s*/?>", r"\1", html)

    def term_on_own_line(match: re.Match) -> str:
        # DOTALL on the italic gloss: it often wraps across source lines.
        inner = re.sub(r"<p>(<strong>.*?</strong>(?:\s*<em>.*?</em>)?)",
                       r'<p><span class="term">\1</span>', match.group(1), flags=re.S)
        return f"<blockquote>{inner}</blockquote>"

    html = re.sub(r"<blockquote>(.*?)</blockquote>", term_on_own_line, html, flags=re.S)
    # a Q&A question: a paragraph opening with a bold quoted string
    return re.sub(r'<p>(<strong>(?:&quot;|").*?(?:&quot;|")</strong>)',
                  r'<p><span class="q">\1</span>', html, flags=re.S)


def markdown_to_html(md_text: str, title: str, css: str = DOC_CSS) -> str:
    import markdown

    # Code blocks and inline code are literal text -- the math rewriting below must
    # not touch them, or `count_{i-1}` inside backticks renders as visible <sub> tags.
    stash: list[str] = []

    def park(match: re.Match) -> str:
        stash.append(match.group(0))
        return f"\x00CODE{len(stash) - 1}\x00"

    body = CODE_SPAN.sub(park, md_text)

    for pattern, repl in MATH_REPLACEMENTS:
        body = re.sub(pattern, repl, body)
    # display math -> centred formula block; inline $...$ -> plain text
    body = re.sub(r"\$\$(.+?)\$\$", r'<div class="formula">\1</div>', body, flags=re.S)
    body = re.sub(r"\$([^$\n]+)\$", r"\1", body)

    body = re.sub(r"\x00CODE(\d+)\x00", lambda m: stash[int(m.group(1))], body)

    html_body = markdown.markdown(body, extensions=["tables", "fenced_code", "sane_lists"])
    html_body = _tag_structure(html_body)
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f"<title>{title}</title><style>{css}</style></head>"
            f"<body>{html_body}</body></html>")


def html_to_pdf(html_path: Path, pdf_path: Path, chrome: str) -> None:
    subprocess.run(
        [chrome, "--headless", "--disable-gpu", "--no-pdf-header-footer",
         f"--print-to-pdf={pdf_path}", "--virtual-time-budget=8000",
         html_path.resolve().as_uri()],
        check=True, capture_output=True,
    )


def main() -> None:
    chrome = find_chrome()

    docs = [
        ("writeup/writeup.md", "writeup/writeup.pdf",
         "Do companies bend earnings to avoid reporting a loss?", DOC_CSS),
        ("writeup/project_guide.md", "writeup/project_guide.pdf",
         "Earnings Discontinuity Analysis — Complete Project Guide", GUIDE_CSS),
    ]
    for md_rel, pdf_rel, title, css in docs:
        md_path = ROOT / md_rel
        if not md_path.exists():
            print(f"skipped {md_rel} (not found)")
            continue
        html_path = md_path.with_suffix(".print.html")
        html_path.write_text(markdown_to_html(md_path.read_text(), title, css), encoding="utf-8")
        html_to_pdf(html_path, ROOT / pdf_rel, chrome)
        print(f"wrote {pdf_rel}")

    html_to_pdf(ROOT / "slides" / "slides.html", ROOT / "slides" / "slides.pdf", chrome)
    print("wrote slides/slides.pdf")


if __name__ == "__main__":
    main()
