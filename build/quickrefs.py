"""Render the two-page quick references in content/quickrefs/ to PDF.

Each content/quickrefs/<talk-slug>.html holds the body of a two-page reference
(two <section class="page"> blocks). This script wraps it in the shared template,
prints it to US Letter with headless Chrome, sets clean PDF metadata, and writes
docs/assets/speaking/<talk-slug>-quick-reference.pdf.

Usage:  python build/quickrefs.py            (all)
        python build/quickrefs.py <slug>     (one)
Requires: playwright (with a Chrome or Chromium install) and pikepdf.
"""
import os
import sys
import pathlib
import pikepdf
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "content" / "quickrefs"
OUT = ROOT / "docs" / "assets" / "speaking"
FONTS = (ROOT / "docs" / "assets" / "fonts").as_uri()
LOGO = (ROOT / "docs" / "assets" / "img" / "brand" / "barnes-logo-primary.svg").as_uri()
CHROME = os.environ.get("CHROME_PATH", "/usr/bin/google-chrome")

TEMPLATE = """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>{title}</title>
<style>
@font-face {{ font-family: "LF"; src: url("{fonts}/libre-franklin-latin-400-normal.woff2"); font-weight: 400; }}
@font-face {{ font-family: "LF"; src: url("{fonts}/libre-franklin-latin-400-italic.woff2"); font-weight: 400; font-style: italic; }}
@font-face {{ font-family: "LF"; src: url("{fonts}/libre-franklin-latin-500-normal.woff2"); font-weight: 500; }}
@font-face {{ font-family: "LF"; src: url("{fonts}/libre-franklin-latin-600-normal.woff2"); font-weight: 600; }}
@font-face {{ font-family: "LF"; src: url("{fonts}/libre-franklin-latin-700-normal.woff2"); font-weight: 700; }}
@font-face {{ font-family: "LF"; src: url("{fonts}/libre-franklin-latin-800-normal.woff2"); font-weight: 800; }}
@page {{ size: Letter; margin: 0; }}
:root {{ --ink:#1B1B1B; --muted:#5C5650; --rust:#A64B2A; --rule:#D9D5CE; --stone:#ECEAE6; --alt:#FAF9F6; }}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; padding: 0; }}
body {{ font-family: "LF", Arial, sans-serif; color: var(--ink); font-size: 8.4pt; line-height: 1.38; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
.page {{ width: 8.5in; height: 11in; padding: 0.5in 0.55in 0.45in; position: relative; page-break-after: always; overflow: hidden; display: flex; flex-direction: column; }}
.page:last-child {{ page-break-after: auto; }}
.qr-head {{ display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 1.5pt solid var(--ink); padding-bottom: 9pt; margin-bottom: 11pt; }}
.qr-head img {{ height: 20pt; }}
.eyebrow {{ font-size: 6.6pt; font-weight: 600; letter-spacing: .14em; text-transform: uppercase; color: var(--muted); }}
.eyebrow::before {{ content: ""; display: inline-block; width: 14pt; height: 1pt; background: var(--rust); vertical-align: middle; margin-right: 6pt; }}
h1 {{ font-size: 19pt; font-weight: 800; letter-spacing: -.02em; line-height: 1.05; margin: 5pt 0 3pt; }}
h1 .corner {{ display: inline-block; width: 6pt; height: 6pt; border-right: 2.4pt solid var(--rust); border-bottom: 2.4pt solid var(--rust); margin-left: 2pt; vertical-align: baseline; }}
.sub {{ font-size: 9.2pt; color: var(--muted); margin: 0; }}
.meta {{ font-size: 7pt; color: var(--muted); margin-top: 4pt; }}
h2 {{ font-size: 10.2pt; font-weight: 700; margin: 0 0 5pt; letter-spacing: -.005em; }}
h2 .n {{ color: var(--rust); margin-right: 4pt; }}
h3 {{ font-size: 8.4pt; font-weight: 700; margin: 0 0 2pt; }}
p {{ margin: 0 0 4pt; }}
ul, ol {{ margin: 0; padding-left: 12pt; }}
li {{ margin-bottom: 2.2pt; }}
.block {{ margin-bottom: 11pt; }}
.grid2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0 16pt; }}
.grid3 {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 7pt; }}
.card {{ border: .6pt solid var(--rule); border-top: 1.6pt solid var(--ink); padding: 6pt 7pt; background: #fff; }}
.card .num {{ font-weight: 800; color: var(--rust); font-size: 9pt; margin-right: 3pt; }}
.callout {{ background: var(--ink); color: #F5F3EE; padding: 9pt 12pt; margin-bottom: 11pt; display: flex; gap: 12pt; align-items: center; }}
.callout .q {{ font-size: 13pt; font-weight: 700; letter-spacing: -.01em; }}
.callout .lbl {{ font-size: 6.4pt; letter-spacing: .14em; text-transform: uppercase; color: #D9773F; font-weight: 600; white-space: nowrap; }}
.callout p {{ margin: 0; color: #B9B3AA; font-size: 7.6pt; }}
table {{ width: 100%; border-collapse: collapse; font-size: 7.7pt; }}
th {{ text-align: left; font-size: 6.4pt; letter-spacing: .1em; text-transform: uppercase; color: var(--muted); font-weight: 600; border-bottom: 1pt solid var(--ink); padding: 3pt 5pt 3pt 0; vertical-align: bottom; }}
td {{ border-bottom: .5pt solid var(--rule); padding: 4pt 6pt 4pt 0; vertical-align: top; }}
td:first-child {{ font-weight: 600; }}
.panel {{ background: var(--alt); border-left: 2pt solid var(--rust); padding: 7pt 9pt; }}
.small {{ font-size: 7pt; color: var(--muted); }}
.rule-tag {{ font-size: 6.6pt; color: var(--muted); white-space: nowrap; }}
.takeaways {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8pt; border-top: 1.5pt solid var(--ink); padding-top: 7pt; }}
.takeaways div {{ font-size: 7.7pt; }}
.takeaways b {{ display: block; font-size: 8.2pt; margin-bottom: 1pt; }}
.spacer {{ flex: 1; }}
.qr-foot {{ border-top: .6pt solid var(--rule); padding-top: 5pt; margin-top: 8pt; display: flex; justify-content: space-between; gap: 16pt; font-size: 6.3pt; color: var(--muted); }}
.qr-foot .disc {{ max-width: 5.2in; }}
</style></head><body>{body}</body></html>"""


def header(page_no, total=2):
    return ""  # header and footer are written into each page by the content file


def render(slug):
    body = (SRC / f"{slug}.html").read_text(encoding="utf8")
    title_line = body.split("<!--title:", 1)[1].split("-->", 1)[0].strip()
    html = TEMPLATE.format(title=title_line, fonts=FONTS, body=body.replace("{LOGO}", LOGO))
    tmp = SRC / f".{slug}.render.html"
    tmp.write_text(html, encoding="utf8")
    dst = OUT / f"{slug}-quick-reference.pdf"
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME)
        page = browser.new_page()
        page.goto(tmp.as_uri(), wait_until="networkidle")
        page.evaluate("document.fonts.ready")
        page.pdf(path=str(dst), format="Letter", print_background=True, prefer_css_page_size=True)
        browser.close()
    tmp.unlink()
    with pikepdf.open(dst, allow_overwriting_input=True) as pdf:
        n = len(pdf.pages)
        if pikepdf.Name.Metadata in pdf.Root:
            del pdf.Root[pikepdf.Name.Metadata]
        pdf.docinfo = pdf.make_indirect(pikepdf.Dictionary())
        pdf.docinfo[pikepdf.Name.Title] = title_line
        pdf.docinfo[pikepdf.Name.Author] = "Jason T. Barnes"
        pdf.docinfo[pikepdf.Name.Subject] = "Quick reference, Dallas Bar Association Securities Section program"
        pdf.save(dst, linearize=True)
    print(f"{dst.name}: {n} pages, {dst.stat().st_size // 1024} KB")
    if n != 2:
        raise SystemExit(f"{slug}: expected 2 pages, got {n}")


if __name__ == "__main__":
    slugs = sys.argv[1:] or sorted(f.stem for f in SRC.glob("*.html") if not f.name.startswith("."))
    for s in slugs:
        render(s)
