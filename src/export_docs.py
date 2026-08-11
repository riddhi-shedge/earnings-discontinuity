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


def find_chrome() -> str:
    for path in CHROME_CANDIDATES:
        if Path(path).exists():
            return path
    found = shutil.which("chromium") or shutil.which("google-chrome")
    if found:
        return found
    raise RuntimeError("No Chrome/Chromium found; cannot render PDF.")


CODE_SPAN = re.compile(r"```.*?```|`[^`\n]+`", re.S)


def markdown_to_html(md_text: str, title: str) -> str:
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
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f"<title>{title}</title><style>{DOC_CSS}</style></head>"
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

    writeup_md = ROOT / "writeup" / "writeup.md"
    writeup_html = ROOT / "writeup" / "writeup.print.html"
    writeup_html.write_text(
        markdown_to_html(writeup_md.read_text(),
                         "Do companies bend earnings to avoid reporting a loss?"),
        encoding="utf-8")
    html_to_pdf(writeup_html, ROOT / "writeup" / "writeup.pdf", chrome)
    print("wrote writeup/writeup.pdf")

    html_to_pdf(ROOT / "slides" / "slides.html", ROOT / "slides" / "slides.pdf", chrome)
    print("wrote slides/slides.pdf")


if __name__ == "__main__":
    main()
