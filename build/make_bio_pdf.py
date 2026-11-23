"""Build Jason's downloadable bio: docs/assets/files/jason-t-barnes-bio.pdf

The text comes from build.py (ABOUT_LEDE, ABOUT_BIO, FACTS, SITE, PRACTICE), so the PDF
matches the About page. Run after changing the bio:

    pip install playwright && python -m playwright install chromium
    python3 build/make_bio_pdf.py
"""
import importlib.util
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DOCS = HERE.parent / "docs"

sys.argv = [str(HERE / "build.py")]
spec = importlib.util.spec_from_file_location("site_build", HERE / "build.py")
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
S = b.SITE

FONTS = "".join(
    f'@font-face{{font-family:"Libre Franklin";src:url("{(DOCS / "assets/fonts" / f"libre-franklin-latin-{w}-normal.woff2").as_uri()}");font-weight:{w}}}'
    for w in (400, 500, 600, 700, 800)
)

practice = "".join(f"<li>{p['title']}</li>" for p in b.PRACTICE)
stats = "".join(f'<div class="st"><b>{n}</b><span>{l}</span></div>' for n, l in b.FACTS)
bio = "".join(f"<p>{p}</p>" for p in b.ABOUT_BIO)

HTML = f"""<!doctype html><html><head><meta charset="utf-8"><style>
{FONTS}
@page {{ size: Letter; margin: 0.5in 0.6in 0.5in; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; font-family: "Libre Franklin", Arial, sans-serif; color: #1B1B1B; font-size: 9pt; line-height: 1.48; }}
.top {{ display: flex; justify-content: space-between; align-items: flex-end; padding-bottom: 12pt; border-bottom: 1.5pt solid #1B1B1B; }}
.top img {{ width: 1.35in; display: block; }}
.top .firm {{ font-size: 7pt; font-weight: 600; letter-spacing: .14em; text-transform: uppercase; color: #5C5650; text-align: right; line-height: 1.6; }}
.grid {{ display: grid; grid-template-columns: 2.05in 1fr; gap: 0.36in; margin-top: 18pt; }}
.side .photo {{ width: 1.45in; height: 1.45in; border-radius: 50%; object-fit: cover; border: .75pt solid #D9D5CE; display: block; margin-bottom: 14pt; }}
.lbl {{ display: flex; align-items: center; gap: 7pt; font-size: 6.6pt; font-weight: 600; letter-spacing: .14em; text-transform: uppercase; color: #5C5650; margin: 11pt 0 3pt; }}
.lbl::before {{ content: ""; width: 12pt; height: 1.5pt; background: #A64B2A; }}
.side p, .side li {{ margin: 0 0 1.5pt; font-size: 8.2pt; line-height: 1.4; }}
.side ul {{ list-style: none; padding: 0; margin: 0; }}
.side a {{ color: #1B1B1B; text-decoration: none; }}
h1 {{ font-size: 28pt; font-weight: 800; letter-spacing: -.02em; line-height: 1.05; margin: 0; }}
.title {{ font-size: 8pt; font-weight: 600; letter-spacing: .14em; text-transform: uppercase; color: #5C5650; margin: 5pt 0 14pt; }}
.lede {{ font-size: 11pt; line-height: 1.42; color: #1B1B1B; margin: 0 0 10pt; }}
.main p {{ margin: 0 0 7pt; color: #2E2A26; }}
h3 {{ font-size: 10.5pt; font-weight: 700; margin: 12pt 0 4pt; }}
.stats {{ display: grid; grid-template-columns: repeat(4, 1fr); border-top: 1.5pt solid #1B1B1B; border-bottom: .75pt solid #D9D5CE; margin-top: 14pt; }}
.st {{ padding: 8pt 8pt 8pt 0; border-right: .75pt solid #D9D5CE; }}
.st + .st {{ padding-left: 8pt; }}
.st:last-child {{ border-right: 0; }}
.st b {{ display: block; font-size: 15pt; font-weight: 800; letter-spacing: -.02em; line-height: 1.1; }}
.st span {{ display: block; font-size: 6.4pt; font-weight: 600; letter-spacing: .1em; text-transform: uppercase; color: #5C5650; margin-top: 3pt; line-height: 1.35; }}
.note {{ font-size: 7pt; color: #5C5650; margin-top: 5pt; }}
.legal {{ margin-top: 14pt; padding-top: 8pt; border-top: .75pt solid #D9D5CE; font-size: 6.8pt; color: #5C5650; line-height: 1.5; }}
.nw {{ white-space: nowrap; }}
</style></head><body>
<div class="top">
  <img src="{(DOCS / 'assets/img/brand/barnes-logo-primary.svg').as_uri()}" alt="Barnes">
  <div class="firm"><span class="nw">{S['firm']}</span><br>{S['city']} &middot; {S['domain']}</div>
</div>
<div class="grid">
  <aside class="side">
    <img class="photo" src="{(DOCS / 'assets/img/jason-barnes-headshot.webp').as_uri()}" alt="">
    <div class="lbl">Direct contact</div>
    <p><a href="mailto:{S['direct_email']}">{S['direct_email']}</a></p>
    <p>Office {S['office_phone']}</p>
    <p>Mobile {S['mobile_phone']}</p>
    <p><a href="{S['linkedin']}">linkedin.com/in/jasontbarnes</a></p>
    <div class="lbl">Practice</div>
    <ul>{practice}</ul>
    <div class="lbl">Education</div>
    <p>J.D., Emory University School of Law</p>
    <p>B.S., Georgia Institute of Technology</p>
    <div class="lbl">Admission</div>
    <p>State Bar of Texas</p>
    <div class="lbl">Recognition</div>
    <p>Texas Rising Stars, Super Lawyers, 2004 to 2012</p>
    <div class="lbl">Bar leadership</div>
    <p>Dallas Bar Association, Securities Section</p>
  </aside>
  <main class="main">
    <h1>{S['attorney']}</h1>
    <div class="title">{S['title']}</div>
    <p class="lede">{b.ABOUT_LEDE}</p>
    {bio}
    <h3>Beyond the practice</h3>
    <p>Jason works on a pro bono basis to educate the investment community about investing in underserved and emerging markets, with a focus on double-bottom-line and impact-oriented strategies. He speaks and writes regularly on private funds, securities offerings, and the practical use of technology in legal work, and he builds the practice tools shared at {S['domain']}/lab.</p>
    <div class="stats">{stats}</div>
    <div class="note">{b.RESULTS_NOTE}</div>
  </main>
</div>
<div class="legal"><b>Attorney Advertising.</b> {S['attorney']} is responsible for this content. Principal office: {S['city']}. This biography provides general information, not legal advice, and does not create an attorney-client relationship. Not certified by the Texas Board of Legal Specialization.</div>
</body></html>"""

HTML = b.keep_firm_name_together(HTML)

out = DOCS / "assets" / "files" / "jason-t-barnes-bio.pdf"
out.parent.mkdir(parents=True, exist_ok=True)
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    tmp = HERE / "_bio_tmp.html"   # loaded from disk so the local fonts and images resolve
    tmp.write_text(HTML, encoding="utf-8")
    try:
        page.goto(tmp.as_uri(), wait_until="load")
        page.evaluate("document.fonts.ready")
        page.wait_for_timeout(300)
        page.pdf(path=str(out), format="Letter", print_background=True, prefer_css_page_size=True)
    finally:
        tmp.unlink()
    browser.close()
print("Wrote", out.relative_to(DOCS.parent))
