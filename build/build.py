#!/usr/bin/env python3
"""
jtbarnespllc.com static site generator.

Every page shares one header, one footer, and one set of facts, so a change made
here appears everywhere. No dependencies beyond Python 3.8+.

    python3 build/build.py          # regenerates every page into docs/

Edit SITE and FACTS for contact details and published figures, PRACTICE for
practice-area pages, and ARTICLES to publish an Insights article.
Static assets (CSS, JS, fonts, images) live in docs/assets and are not generated.
"""
import argparse
import json
import os
from datetime import date
from html import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs")

# ---------------------------------------------------------------------------
# 1. Firm data (single source of truth)
# ---------------------------------------------------------------------------
SITE = {
    "firm": "J.T. Barnes & Associates, PLLC",
    "short": "J.T. Barnes & Associates",
    "domain": "jtbarnespllc.com",
    "url": "https://jtbarnespllc.com",
    "attorney": "Jason T. Barnes",
    "title": "Managing Partner",
    "office_phone": "+1.469.304.6366",
    "office_tel": "+14693046366",
    "mobile_phone": "+1.214.450.4400",
    "mobile_tel": "+12144504400",
    "email": "jtbarnes@jtbarnespllc.com",
    "city": "Dallas, Texas",
    "locality": "Dallas",
    "region": "TX",
    "linkedin": "https://www.linkedin.com/in/jasontbarnes/",
    "timekeeper_url": "https://jasontbarnes.com/mylegaltimekeeper/",
    # Optional booking link (Calendly, Microsoft Bookings, etc.). Blank = route to /contact/
    "scheduling_url": "",
    "updated": "2026-10-15",
}

# ---------------------------------------------------------------------------
# Build target. Default is the permanent home, jtbarnespllc.com.
#   python3 build/build.py                                   -> docs/ for jtbarnespllc.com
#   python3 build/build.py --domain jasontbarnes.com \
#       --out ../jasontbarnesesq.github.io --legacy-stubs --no-nojekyll
#                                                            -> interim build into the
#                                                               jasontbarnes.com repository
# ---------------------------------------------------------------------------
_ap = argparse.ArgumentParser(description="Build jtbarnespllc.com")
_ap.add_argument("--domain", default="jtbarnespllc.com", help="Domain the site is served from")
_ap.add_argument("--out", default=None, help="Output folder (default: docs/)")
_ap.add_argument("--legacy-stubs", action="store_true",
                 help="Also write redirect pages for old jasontbarnes.com paths (interim build only)")
_ap.add_argument("--no-nojekyll", action="store_true",
                 help="Do not write .nojekyll (keeps Jekyll processing for other folders in a shared repo)")
ARGS, _ = _ap.parse_known_args()
SITE["domain"] = ARGS.domain
SITE["url"] = "https://" + ARGS.domain
if ARGS.out:
    OUT = os.path.abspath(ARGS.out)

# Old jasontbarnes.com paths -> new paths (used with --legacy-stubs)
LEGACY = {
    "/legal-services/": "/practice/",
    "/practice-tools/": "/lab/",
    "/privacy/": "/legal/privacy/",
    "/insights/jpmorgan-2026-family-office-report/": "/insights/",
    "/insights/eb5-2026-dhs-updates/": "/insights/",
    "/insights/why-time-tracking-fails-lawyers/": "/insights/",
}

# Published figures. Confirm each before launch (see workbook, Compliance tab).
FACTS = [
    ("Nearly 30", "Years in practice"),
    ("750+", "Transactions &amp; fund formations"),
    ("51", "Countries"),
    ("Nearly 20", "Years in EB-5 finance"),
]
RESULTS_NOTE = ("Figures describe Mr. Barnes&rsquo;s career experience, including work at prior firms. "
                "Prior results do not guarantee a similar outcome.")

# ---------------------------------------------------------------------------
# 2. Practice areas
# ---------------------------------------------------------------------------
PRACTICE = [
    {
        "slug": "fund-formation",
        "title": "Fund Formation &amp; Alternative Investments",
        "nav": "Fund Formation",
        "summary": "Structuring and documenting private investment funds and co-investment vehicles for sponsors, managers, and the families and institutions that invest alongside them.",
        "overview": [
            "Jason has advised on fund formations across private equity, venture capital, real estate, credit, and impact strategies, representing both the sponsors raising capital and the investors committing it.",
            "That two-sided perspective shapes how terms get drafted: anticipating what sophisticated limited partners will negotiate, and protecting sponsors from provisions that look standard but carry real cost over the life of a fund.",
        ],
        "work": [
            "Fund structuring, including master-feeder, parallel, and blocker structures",
            "Private placement memoranda, limited partnership agreements, and subscription documents",
            "General partner and management company formation, carried interest, and fee economics",
            "Side letters, most-favored-nation provisions, and investor negotiations",
            "Co-investment vehicles, special purpose vehicles, and single-asset funds",
            "Investment adviser registration and exempt reporting adviser questions",
            "Small Business Investment Company (SBIC) fund structures",
        ],
        "clients": "Emerging and established fund sponsors, investment managers and advisers, and family offices investing as limited partners.",
    },
    {
        "slug": "capital-markets",
        "title": "Capital Markets &amp; Securities Offerings",
        "nav": "Capital Markets",
        "summary": "Private placements and exempt offerings, structured to raise capital efficiently and to stay on the right side of federal and state securities law.",
        "overview": [
            "Most capital raised by private companies moves through exemptions from registration, and the details of each exemption matter: who may be solicited, what must be disclosed, and which filings are due and when.",
            "Jason advises issuers, sponsors, placement agents, and investors on offerings from early-stage rounds to institutional private placements, with close attention to the practical mechanics that decide whether a raise closes on schedule.",
        ],
        "work": [
            "Regulation D offerings under Rule 506(b) and Rule 506(c)",
            "Regulation S and other cross-border offerings",
            "Offering memoranda, risk factors, and investor communications",
            "Senior and subordinated debt financings and syndicated participations",
            "Form D and state notice filings",
            "Broker-dealer and finder questions in capital raising",
            "Venture capital and growth equity financings",
        ],
        "clients": "Private companies and their founders, sponsors and issuers, placement agents, and institutional and individual investors.",
    },
    {
        "slug": "family-office",
        "title": "Family Office Advisory",
        "nav": "Family Office",
        "summary": "Governance, structure, and investment infrastructure for families moving from an operating business to institutional-grade capital management.",
        "overview": [
            "When a family moves from running a business to managing its wealth, it inherits the legal architecture of an institution without the staff of one.",
            "Jason helps families and their advisors build that architecture deliberately: entity structure, governance and decision rights, investment vehicles, co-investment alongside outside sponsors, and the regulatory questions that come with managing capital across family members and generations.",
        ],
        "work": [
            "Single family office structuring and the family office exclusion under the Investment Advisers Act",
            "Investment entity and holding company design",
            "Governance frameworks, investment committees, and decision rights",
            "Direct investments and co-investments alongside institutional sponsors",
            "Commitments to third-party funds, including side letter negotiation",
            "Planning around liquidity events and business transitions",
        ],
        "clients": "Families and family offices, family-owned businesses, and the wealth, tax, and accounting advisors who serve them.",
    },
    {
        "slug": "eb5",
        "title": "EB-5 Finance",
        "nav": "EB-5 Finance",
        "summary": "Transactional and securities counsel for EB-5 regional centers, project developers, and the foreign investors who fund them.",
        "overview": [
            "EB-5 financing sits where securities law, project finance, and immigration objectives meet, and its participants often span several continents.",
            "For nearly two decades Jason has served as transactional and securities counsel in EB-5 capital raises, coordinating developers, regional centers, immigration counsel, overseas intermediaries, and escrow and fund administrators so that the investment structure supports both the project&rsquo;s capital needs and each investor&rsquo;s objectives.",
        ],
        "work": [
            "Offering structure and documents for new commercial enterprises",
            "Regional center and project developer engagement terms",
            "Loan and equity structures between the new commercial enterprise and the job-creating entity",
            "Securities compliance for offerings to non-U.S. investors",
            "Escrow, administration, and investor reporting frameworks",
            "Coordination with immigration counsel and overseas intermediaries",
        ],
        "clients": "Regional centers, project developers and sponsors, and investors and their advisors.",
        "note": "The firm provides transactional and securities counsel in EB-5 matters. Investors&rsquo; immigration petitions are prepared by their immigration counsel, with whom the firm coordinates closely.",
    },
    {
        "slug": "ma-structured-finance",
        "title": "M&amp;A, Joint Ventures &amp; Structured Finance",
        "nav": "M&amp;A &amp; Structured Finance",
        "summary": "Acquisitions, joint ventures, and financing structures for middle-market businesses and the investors who back them.",
        "overview": [
            "Middle-market transactions demand the same structural rigor as large deals, usually with leaner teams and tighter timelines.",
            "Jason represents buyers, sellers, sponsors, and capital providers in acquisitions, joint ventures, recapitalizations, and structured financings, including multi-tier holding structures and cross-border arrangements.",
        ],
        "work": [
            "Acquisitions and dispositions of private companies and business assets",
            "Holding company and acquisition vehicle structures",
            "Joint ventures between operators and capital partners",
            "Recapitalizations, restructurings, and growth financings",
            "Structured and alternative financing arrangements",
            "Inbound and cross-border investment",
        ],
        "clients": "Founders and owners of middle-market businesses, private equity sponsors, strategic buyers, and capital providers.",
    },
    {
        "slug": "real-estate",
        "title": "Real Estate Capital &amp; Transactions",
        "nav": "Real Estate",
        "summary": "Joint ventures, capital stacks, and investment structures for real estate sponsors and the capital partners who invest with them.",
        "overview": [
            "Real estate deals are capital structure problems as much as property problems.",
            "Jason represents sponsors, general partners, and investors in joint ventures, programmatic equity relationships, and private offerings across industrial, commercial, and development projects, focusing on the economics and governance that decide how a partnership performs when plans change.",
        ],
        "work": [
            "General partner and limited partner joint venture agreements and waterfall economics",
            "Programmatic and single-asset equity partnerships",
            "Syndications and private offerings of real estate interests",
            "Preferred equity and mezzanine structures",
            "Development and value-add project capitalization",
            "Foreign capital investment in U.S. real estate",
        ],
        "clients": "Real estate sponsors and developers, institutional and family office capital partners, and foreign investors.",
    },
]

# ---------------------------------------------------------------------------
# 3. Insights articles. Add a dict to publish; newest first.
#    body is HTML. Keep paragraphs in <p> tags; use <h2> for subheads.
# ---------------------------------------------------------------------------
ARTICLES = [
    # {
    #     "slug": "example-article",
    #     "title": "Article title",
    #     "date": "2026-11-03",
    #     "category": "Private Funds",
    #     "summary": "One or two sentences for the archive card and search results.",
    #     "body": "<p>First paragraph.</p><h2>Subhead</h2><p>More text.</p>",
    # },
]

# ---------------------------------------------------------------------------
# 4. Layout
# ---------------------------------------------------------------------------
PAGES = []  # (path, noindex) for sitemap

NAV = [("Practice", "/practice/"), ("Approach", "/approach/"), ("About", "/about/"),
       ("Insights", "/insights/"), ("Contact", "/contact/")]
UTIL = [("Newsletter", "/newsletter/"), ("The Lab", "/lab/")]


def fmt_date(iso):
    d = date.fromisoformat(iso)
    return f"{d:%B} {d.day}, {d.year}"


def schedule_href():
    return SITE["scheduling_url"] or "/contact/"


def schedule_attrs():
    return ' target="_blank" rel="noopener"' if SITE["scheduling_url"] else ""


def current(path, href):
    if href == "/":
        return path == "/"
    return path.startswith(href)


def header(path):
    def cur(h):
        return ' aria-current="page"' if current(path, h) else ""
    main = "".join(f'<li><a href="{h}"{cur(h)}>{t}</a></li>' for t, h in NAV)
    util = "".join(f'<a href="{h}"{cur(h)}>{t}</a>' for t, h in UTIL)
    return f'''<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
  <div class="utility">
    <div class="wrap">
      <span class="loc">{SITE["city"]}</span>
      <nav aria-label="Utility">{util}<a class="phone" href="tel:{SITE["office_tel"]}">{SITE["office_phone"]}</a></nav>
    </div>
  </div>
  <div class="mainbar">
    <div class="wrap">
      <a class="brand" href="/" aria-label="{SITE["firm"]}, home">
        <img src="/assets/img/barnes-logo-white.png" width="521" height="179" alt="Barnes">
        <span class="brand-name">J.T. Barnes<br>&amp; Associates, PLLC</span>
      </a>
      <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="primary-nav">Menu</button>
      <nav class="primary-nav" id="primary-nav" aria-label="Primary">
        <ul>{main}</ul>
        <a class="btn btn-gold" href="{schedule_href()}"{schedule_attrs()}>Schedule a Consultation</a>
      </nav>
    </div>
  </div>
</header>'''


def footer():
    practice_links = "".join(f'<li><a href="/practice/{p["slug"]}/">{p["nav"]}</a></li>' for p in PRACTICE)
    return f'''<footer class="site-footer">
  <div class="wrap">
    <div class="footer-top">
      <div class="footer-brand">
        <img src="/assets/img/barnes-logo-white.png" width="521" height="179" alt="Barnes" loading="lazy">
        <p><strong>{SITE["firm"]}</strong></p>
        <p>Corporate finance, securities, and private capital counsel.</p>
        <p>{SITE["city"]}</p>
      </div>
      <div>
        <h4>Practice</h4>
        <ul>{practice_links}</ul>
      </div>
      <div>
        <h4>Firm</h4>
        <ul>
          <li><a href="/approach/">Approach</a></li>
          <li><a href="/about/">About Jason</a></li>
          <li><a href="/contact/">Contact</a></li>
          <li><a href="{schedule_href()}"{schedule_attrs()}>Schedule a Consultation</a></li>
        </ul>
      </div>
      <div>
        <h4>The Lab</h4>
        <ul>
          <li><a href="/insights/">Insights</a></li>
          <li><a href="/newsletter/">Securities Compliance Weekly</a></li>
          <li><a href="/lab/">Practice Tools</a></li>
          <li><a href="/lab/timekeeper/">Legal Timekeeper</a></li>
          <li><a href="/lab/minder/">Legal Minder</a></li>
        </ul>
      </div>
      <div>
        <h4>Contact</h4>
        <ul>
          <li><a href="tel:{SITE["office_tel"]}">Office {SITE["office_phone"]}</a></li>
          <li><a href="tel:{SITE["mobile_tel"]}">Mobile {SITE["mobile_phone"]}</a></li>
          <li><a href="mailto:{SITE["email"]}">{SITE["email"]}</a></li>
          <li><a href="{SITE["linkedin"]}" rel="noopener">LinkedIn</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-legal">
      <div>
        <p>&copy; <span data-year>{date.today().year}</span> {SITE["firm"]}. All rights reserved.</p>
        <p><a href="/legal/">Legal Notices &amp; Disclaimer</a> &middot; <a href="/legal/privacy/">Privacy</a> &middot; <a href="/legal/#advertising">Attorney Advertising</a></p>
      </div>
      <div>
        <p><strong>Attorney Advertising.</strong> {SITE["attorney"]} is responsible for the content of this website. Principal office: {SITE["city"]}. This website provides general information, not legal advice. Contacting the firm does not create an attorney-client relationship. Not certified by the Texas Board of Legal Specialization.</p>
      </div>
    </div>
  </div>
</footer>'''


def head(path, title, description, noindex=False, jsonld=None):
    full_title = title if title.startswith(SITE["short"]) else f"{title} | {SITE['firm']}"
    canonical = SITE["url"] + path
    ld = ""
    if jsonld:
        ld = '\n<script type="application/ld+json">' + json.dumps(jsonld, ensure_ascii=False) + "</script>"
    robots = '\n<meta name="robots" content="noindex, follow">' if noindex else ""
    return f'''<!doctype html>
<html lang="en" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{full_title}</title>
<meta name="description" content="{escape(description, quote=True)}">
<link rel="canonical" href="{canonical}">{robots}
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; font-src 'self'; connect-src 'self' https:; form-action 'self' https: mailto:; base-uri 'self'; object-src 'none'">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta name="theme-color" content="#1C1C1C">
<meta property="og:site_name" content="{SITE["firm"]}">
<meta property="og:type" content="website">
<meta property="og:title" content="{full_title}">
<meta property="og:description" content="{escape(description, quote=True)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE["url"]}/assets/img/og-image.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/img/favicon-32.png">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<link rel="preload" href="/assets/fonts/dm-sans-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/playfair-display-latin-500-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/css/site.css">
<script src="/assets/js/site.js" defer></script>{ld}
</head>'''


def page(path, title, description, body, zone="firm", noindex=False, jsonld=None):
    html = (head(path, title, description, noindex, jsonld)
            + f'\n<body class="zone-{zone}">\n' + header(path)
            + f'\n<main id="main">\n{body}\n</main>\n' + footer() + "\n</body>\n</html>\n")
    rel = path.strip("/")
    target = os.path.join(OUT, rel, "index.html") if rel else os.path.join(OUT, "index.html")
    if path == "/404.html":
        target = os.path.join(OUT, "404.html")
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        f.write(html)
    PAGES.append((path, noindex))


def page_hero(crumbs, eyebrow, h1, lede):
    trail = " &rsaquo; ".join(f'<a href="{h}">{t}</a>' if h else t for t, h in crumbs)
    return f'''<section class="page-hero on-dark">
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb">{trail}</nav>
    <span class="eyebrow">{eyebrow}</span>
    <h1>{h1}</h1>
    <p class="lede">{lede}</p>
  </div>
</section>'''


def lab_hero(crumbs, badge, h1, lede):
    trail = " &rsaquo; ".join(f'<a href="{h}">{t}</a>' if h else t for t, h in crumbs)
    return f'''<section class="lab-hero">
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb">{trail}</nav>
    <span class="lab-badge">{badge}</span>
    <h1>{h1}</h1>
    <p class="lede">{lede}</p>
  </div>
</section>'''


def stats_block(extra_class=""):
    items = "".join(f'<div class="stat"><div class="num">{n}</div><div class="lbl">{l}</div></div>' for n, l in FACTS)
    return f'<div class="stats {extra_class}">{items}</div>\n<p class="footnote">{RESULTS_NOTE}</p>'


def cta_band(h2="Discuss a transaction or offering.",
             p="Start with a confidential conversation about where you are and what you need."):
    return f'''<section class="cta-band on-dark">
  <div class="wrap">
    <div>
      <h2>{h2}</h2>
      <p>{p}</p>
    </div>
    <div class="actions">
      <a class="btn btn-gold" href="{schedule_href()}"{schedule_attrs()}>Schedule a Consultation</a>
      <a class="btn btn-ghost" href="tel:{SITE["office_tel"]}">Call {SITE["office_phone"]}</a>
    </div>
  </div>
</section>'''


def newsletter_form(compact=False):
    name_field = "" if compact else '''<div><label for="nl-name">Name</label><input id="nl-name" name="name" type="text" autocomplete="name"></div>'''
    return f'''<form class="form newsletter-form" novalidate>
  {name_field}
  <div><label for="nl-email{'-c' if compact else ''}">Email</label><input id="nl-email{'-c' if compact else ''}" name="email" type="email" autocomplete="email" required></div>
  <div><button class="btn btn-teal" type="submit">Subscribe</button></div>
  <p class="form-status small" role="status" aria-live="polite"></p>
</form>'''


ORG_LD = {
    "@context": "https://schema.org",
    "@type": "LegalService",
    "@id": SITE["url"] + "/#firm",
    "name": SITE["firm"],
    "url": SITE["url"] + "/",
    "logo": SITE["url"] + "/assets/img/icon-512.png",
    "image": SITE["url"] + "/assets/img/og-image.jpg",
    "telephone": SITE["office_phone"].replace(".", "-"),
    "email": SITE["email"],
    "address": {"@type": "PostalAddress", "addressLocality": SITE["locality"],
                "addressRegion": SITE["region"], "addressCountry": "US"},
    "areaServed": ["United States", "International"],
    "knowsAbout": ["Securities law", "Private fund formation", "Private placements", "Family office structuring",
                   "EB-5 finance", "Mergers and acquisitions", "Real estate joint ventures"],
    "founder": {"@id": SITE["url"] + "/about/#jason"},
    "sameAs": [SITE["linkedin"]],
}
PERSON_LD = {
    "@context": "https://schema.org",
    "@type": "Person",
    "@id": SITE["url"] + "/about/#jason",
    "name": SITE["attorney"],
    "jobTitle": SITE["title"],
    "worksFor": {"@id": SITE["url"] + "/#firm", "@type": "LegalService", "name": SITE["firm"]},
    "image": SITE["url"] + "/assets/img/jason-barnes-headshot.webp",
    "alumniOf": [{"@type": "CollegeOrUniversity", "name": "Emory University School of Law"},
                 {"@type": "CollegeOrUniversity", "name": "Georgia Institute of Technology"}],
    "knowsAbout": ORG_LD["knowsAbout"],
    "sameAs": [SITE["linkedin"]],
}

# ---------------------------------------------------------------------------
# 5. Pages
# ---------------------------------------------------------------------------

def build_home():
    cards = "".join(f'''<a class="card card-top-rule" href="/practice/{p["slug"]}/">
  <span class="index">{i:02d}</span>
  <h3>{p["title"]}</h3>
  <p>{p["summary"]}</p>
  <span class="text-link">Learn more</span>
</a>''' for i, p in enumerate(PRACTICE, 1))
    body = f'''<section class="hero on-dark">
  <div class="wrap">
    <div>
      <span class="eyebrow">{SITE["firm"]}</span>
      <h1>Corporate finance and securities counsel for <em>families, funds,</em> and the middle market.</h1>
      <p class="lede">Nearly 30 years structuring, documenting, and negotiating the transactions that connect capital providers with the businesses and sponsors raising it. Institutional-quality work, delivered directly by the attorney you hire.</p>
      <div class="hero-actions">
        <a class="btn btn-gold" href="{schedule_href()}"{schedule_attrs()}>Schedule a Consultation</a>
        <a class="btn btn-ghost" href="/practice/">Practice Areas</a>
      </div>
    </div>
    <div class="hero-card">
      <img src="/assets/img/jason-barnes-headshot-280.webp" width="280" height="273" alt="Jason T. Barnes">
      <div>
        <div class="name">{SITE["attorney"]}</div>
        <div class="title">{SITE["title"]}</div>
      </div>
    </div>
  </div>
</section>

<section class="section-tight">
  <div class="wrap">
    {stats_block()}
  </div>
</section>

<section class="section section-stone">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">Practice</span>
      <h2>Counsel across the capital stack.</h2>
      <p class="lede">Having represented capital providers, investors, and those raising capital, Jason brings each side&rsquo;s view of the deal to the table, across the full life of an investment or a company.</p>
    </div>
    <div class="grid-3">{cards}</div>
  </div>
</section>

<section class="section">
  <div class="wrap split">
    <div>
      <span class="eyebrow">Who we serve</span>
      <h2>Institutional-quality counsel without institutional overhead.</h2>
      <p class="lede">The firm is built for clients who need sophisticated structuring and direct partner attention, not a large-firm staffing pyramid.</p>
      <a class="text-link" href="/approach/">How engagements work</a>
    </div>
    <div class="audience">
      <div><h4>Family offices &amp; private investors</h4><p>Governance, investment vehicles, and co-investments.</p></div>
      <div><h4>Fund sponsors &amp; managers</h4><p>Formation, offerings, and adviser questions.</p></div>
      <div><h4>Middle-market businesses</h4><p>Capital raises, acquisitions, and joint ventures.</p></div>
      <div><h4>Real estate sponsors</h4><p>Joint ventures, capital stacks, and syndications.</p></div>
      <div><h4>Cross-border investors</h4><p>Inbound capital, EB-5, and offshore offerings.</p></div>
      <div><h4>Capital providers</h4><p>Debt, preferred equity, and participations.</p></div>
    </div>
  </div>
</section>

<section class="section section-stone">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">Approach</span>
      <h2>Clear scope. Direct involvement. Systems that keep work moving.</h2>
    </div>
    <div class="grid-3">
      <div class="card"><h3>The attorney you hire does the work</h3><p>Jason leads every engagement personally, from structuring through closing, and brings in co-counsel and specialists where a matter calls for them.</p></div>
      <div class="card"><h3>Scope and fees agreed up front</h3><p>Engagements begin with a written scope and fee arrangement, including fixed or phased fees where the work allows, so there are no surprises at closing.</p></div>
      <div class="card"><h3>Technology-enabled delivery</h3><p>The practice runs on time, deadline, and document systems Jason built and uses every day. Some of them are shared in <a href="/lab/">the Lab</a>.</p></div>
    </div>
  </div>
</section>

<section class="section lab-band">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">From the Lab</span>
      <h2>Insights, research, and practice tools.</h2>
      <p class="lede">Writing and tools from an active securities practice, for clients, colleagues, and anyone who wants to work smarter.</p>
    </div>
    <div class="grid-3">
      <a class="card" href="/insights/"><span class="status status-soon">Insights</span><h3>Writing on private capital</h3><p>Analysis of private funds, securities offerings, family office trends, and the economics of professional work.</p><span class="text-link">Read</span></a>
      <a class="card" href="/newsletter/"><span class="status status-live">Weekly</span><h3>Securities Compliance Weekly</h3><p>Regulatory developments and market trends for fund managers, advisers, and family offices.</p><span class="text-link">Subscribe</span></a>
      <a class="card" href="/lab/"><span class="status status-dev">Tools</span><h3>Practice tools</h3><p>The Legal Timekeeper, Legal Minder, and the systems behind a technology-enabled practice.</p><span class="text-link">Explore the Lab</span></a>
    </div>
  </div>
</section>

{cta_band()}'''
    page("/", f"{SITE['short']} | Corporate Finance &amp; Securities Counsel, Dallas",
         "J.T. Barnes & Associates, PLLC: corporate finance, securities, fund formation, family office, EB-5, M&A, and real estate capital counsel for families, funds, and middle-market businesses. Dallas, Texas.",
         body, jsonld=ORG_LD)


def build_practice():
    cards = "".join(f'''<a class="card card-top-rule" href="/practice/{p["slug"]}/">
  <span class="index">{i:02d}</span>
  <h3>{p["title"]}</h3>
  <p>{p["summary"]}</p>
  <span class="text-link">Learn more</span>
</a>''' for i, p in enumerate(PRACTICE, 1))
    body = page_hero([("Home", "/"), ("Practice", None)], "Practice Areas",
                     "Structuring, documenting, and negotiating capital transactions.",
                     "The practice links capital providers with those seeking capital, across borders both physical and figurative, for clients ranging from early-stage sponsors to multi-generational family offices.")
    body += f'''
<section class="section">
  <div class="wrap">
    <div class="grid-3">{cards}</div>
  </div>
</section>
<section class="section section-stone">
  <div class="wrap">
    {stats_block()}
  </div>
</section>
{cta_band()}'''
    page("/practice/", "Practice Areas",
         "Fund formation, securities offerings, family office advisory, EB-5 finance, M&A and joint ventures, and real estate capital transactions.",
         body)

    for p in PRACTICE:
        work = "".join(f"<li>{w}</li>" for w in p["work"])
        overview = "".join(f"<p>{o}</p>" for o in p["overview"])
        note = f'<div class="note-box">{p["note"]}</div>' if p.get("note") else ""
        related = "".join(f'<a href="/practice/{q["slug"]}/">{q["title"]}</a>' for q in PRACTICE if q is not p)
        body = page_hero([("Home", "/"), ("Practice", "/practice/"), (p["nav"], None)], "Practice Area",
                         p["title"], p["summary"])
        body += f'''
<section class="section">
  <div class="wrap detail">
    <div>
      <h2>Overview</h2>
      {overview}
      <h2>Representative work</h2>
      <ul class="check-list">{work}</ul>
      <h2>Who we advise</h2>
      <p>{p["clients"]}</p>
      {note}
    </div>
    <aside>
      <div class="aside-card on-dark">
        <span class="eyebrow">Discuss a matter</span>
        <h3>Talk with Jason directly.</h3>
        <p>Initial conversations are confidential. Please share only general information until a conflicts check is complete.</p>
        <p class="contact-line"><a href="tel:{SITE["office_tel"]}">{SITE["office_phone"]}</a></p>
        <p class="contact-line"><a href="mailto:{SITE["email"]}">{SITE["email"]}</a></p>
        <a class="btn btn-gold" href="{schedule_href()}"{schedule_attrs()}>Schedule a Consultation</a>
      </div>
      <nav class="related" aria-label="Other practice areas">
        <span class="eyebrow">Other practice areas</span>
        {related}
      </nav>
    </aside>
  </div>
</section>
{cta_band()}'''
        plain = p["title"].replace("&amp;", "&")
        page(f"/practice/{p['slug']}/", p["title"], f"{plain}: {p['summary'].replace('&amp;', '&')}", body)


def build_approach():
    body = page_hero([("Home", "/"), ("Approach", None)], "Approach",
                     "How engagements work.",
                     "Sophisticated work should be easy to start, easy to understand, and easy to budget. Here is what working with the firm looks like.")
    body += f'''
<section class="section">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">The process</span>
      <h2>From first call to closing.</h2>
    </div>
    <div class="steps">
      <div class="step"><h3>Initial conversation</h3><p>A confidential call to understand the transaction, the parties, and the timeline. We run a conflicts check before you share details.</p></div>
      <div class="step"><h3>Scope and fee proposal</h3><p>A written engagement letter describing the work, the deliverables, and the fee arrangement: fixed, phased, or hourly, depending on the matter.</p></div>
      <div class="step"><h3>Execution</h3><p>Jason leads the work directly and coordinates with your accountants, administrators, co-counsel, and the other side&rsquo;s advisors.</p></div>
      <div class="step"><h3>Closing and handoff</h3><p>Organized closing sets, clear post-closing obligations, and calendared deadlines so nothing is missed after signing.</p></div>
    </div>
  </div>
</section>

<section class="section section-stone">
  <div class="wrap split">
    <div>
      <span class="eyebrow">Fees</span>
      <h2>Predictable where possible. Transparent always.</h2>
      <p>Many fund formations, offerings, and entity structuring projects have a well-defined scope, and for those the firm prefers fixed or phased fees. Where scope depends on negotiation or on the other side, work is billed hourly against an agreed estimate, with regular updates.</p>
      <p>Every arrangement is set out in writing before work begins.</p>
    </div>
    <div>
      <span class="eyebrow">Working with your advisors</span>
      <h2>One coordinated team.</h2>
      <p>Complex capital transactions involve tax advisors, accountants, fund administrators, lenders, immigration counsel, and local counsel in other jurisdictions. The firm works alongside the advisors you already trust, and can recommend specialists when a matter needs them.</p>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap split">
    <div>
      <span class="eyebrow">Technology-enabled delivery</span>
      <h2>A practice built on its own systems.</h2>
      <p>The firm runs on time-tracking, deadline-management, and document-standards systems that Jason designed for the way transactional work actually happens. The result is faster turnaround, consistent documents, and accurate, detailed invoices.</p>
      <p>Client information stays in secured, access-controlled systems. Tools demonstrated in the Lab use sample data only.</p>
      <a class="text-link" href="/lab/">Visit the Lab</a>
    </div>
    <div>
      <ul class="check-list">
        <li>Matter-level time capture with plain-language entries</li>
        <li>Deadline and filing calendars built from each transaction&rsquo;s documents</li>
        <li>Document templates governed by a single style and numbering standard</li>
        <li>Quality-control checks for defined terms, cross-references, and numbering</li>
        <li>Structured closing sets and post-closing obligation trackers</li>
      </ul>
    </div>
  </div>
</section>
{cta_band()}'''
    page("/approach/", "Approach",
         "How engagements with J.T. Barnes & Associates work: confidential first conversation, written scope and fees, direct partner involvement, and technology-enabled delivery.",
         body)


def build_about():
    body = page_hero([("Home", "/"), ("About", None)], "About",
                     "Jason T. Barnes", f"{SITE['title']}, {SITE['firm']}")
    body += f'''
<section class="section">
  <div class="wrap bio-grid">
    <div class="bio-photo">
      <img src="/assets/img/jason-barnes-headshot.webp" width="540" height="526" alt="Portrait of Jason T. Barnes">
      <dl class="facts">
        <dt>Education</dt>
        <dd>J.D., Emory University School of Law</dd>
        <dd>B.S., Georgia Institute of Technology</dd>
        <dt>Admission</dt>
        <dd>State Bar of Texas</dd>
        <dt>Recognition</dt>
        <dd>Texas Rising Stars, Super Lawyers, 2004 to 2012</dd>
        <dt>Bar leadership</dt>
        <dd>Dallas Bar Association, Securities Section</dd>
      </dl>
    </div>
    <div>
      <span class="eyebrow">Biography</span>
      <h2>Counsel to every side of the capital table.</h2>
      <p class="lede">Jason advises high-net-worth individuals, family offices, family-owned businesses, and private and public institutions on alternative investments, capital finance, and mergers and acquisitions.</p>
      <p>For nearly 30 years he has represented capital providers, investors, and those raising capital, which gives him an unusual view of the motivations and needs of every stakeholder across the full life cycle of an investment or a company. His technical work centers on structuring, documenting, and negotiating transactions across borders, both physical and figurative, linking capital with the people and projects that need it, from early-stage ventures to multi-lateral family offices.</p>
      <p>His experience includes work with members of the Forbes Global 50, some of the world&rsquo;s largest banks and financial institutions, private and public investment funds, investment managers and advisers, and high-net-worth individuals, on transactions inside and outside the United States. He has also served as a principal of registered investment advisers, giving him the client&rsquo;s view of the regulatory obligations he advises on.</p>
      <p>For nearly two decades he has served as transactional and securities counsel in the U.S. EB-5 program, coordinating developers, regional centers, immigration counsel, and investors around the world.</p>
      <p>Although deeply experienced with institutional capital, Jason focuses his practice on delivering institutional-quality solutions to families, middle-market businesses, and emerging sponsors. He leads {SITE["firm"]}, returning to independent practice after serving as a Shareholder at Munsch Hardt Kopf &amp; Harr, P.C. in Dallas.</p>
      <h3>Beyond the practice</h3>
      <p>Jason works on a pro bono basis to educate the investment community about investing in underserved and emerging markets, with a focus on double-bottom-line and impact-oriented strategies. He speaks and writes regularly on private funds, securities offerings, and the practical use of technology in legal work, and he builds the practice tools shared in <a href="/lab/">the Lab</a>.</p>
    </div>
  </div>
</section>
<section class="section section-stone">
  <div class="wrap">
    <div class="section-head"><span class="eyebrow">Experience at a glance</span></div>
    {stats_block()}
  </div>
</section>
{cta_band("Work with Jason.", "Start with a confidential conversation about your transaction, fund, or family office.")}'''
    page("/about/", "About Jason T. Barnes",
         "Jason T. Barnes, Managing Partner of J.T. Barnes & Associates, PLLC: nearly 30 years advising family offices, funds, and middle-market businesses on securities, fund formation, EB-5, and M&A.",
         body, jsonld=PERSON_LD)


def build_contact():
    options = "".join(f'<option>{p["nav"].replace("&amp;", "&")}</option>' for p in PRACTICE)
    sched = ""
    if SITE["scheduling_url"]:
        sched = f'<p><a class="btn btn-dark" href="{SITE["scheduling_url"]}" target="_blank" rel="noopener">Book a time online</a></p>'
    body = page_hero([("Home", "/"), ("Contact", None)], "Contact",
                     "Start a confidential conversation.",
                     "Tell us a little about your matter and how to reach you. Jason responds personally.")
    body += f'''
<section class="section">
  <div class="wrap split-wide split">
    <div>
      <form id="contact-form" class="form" novalidate>
        <div class="row-2">
          <div><label for="c-name">Name</label><input id="c-name" name="name" type="text" autocomplete="name" required></div>
          <div><label for="c-email">Email</label><input id="c-email" name="email" type="email" autocomplete="email" required></div>
        </div>
        <div class="row-2">
          <div><label for="c-phone">Phone (optional)</label><input id="c-phone" name="phone" type="tel" autocomplete="tel"></div>
          <div><label for="c-org">Organization (optional)</label><input id="c-org" name="organization" type="text" autocomplete="organization"></div>
        </div>
        <div>
          <label for="c-matter">Type of matter</label>
          <select id="c-matter" name="matter">
            <option value="">Select one</option>
            {options}
            <option>Other</option>
          </select>
        </div>
        <div>
          <label for="c-msg">How can we help?</label>
          <textarea id="c-msg" name="message" required></textarea>
          <p class="hint">Please describe your matter in general terms and include the names of the other parties involved so we can check for conflicts. Do not send confidential information until we confirm we can represent you.</p>
        </div>
        <label class="check"><input type="checkbox" name="ack" required> I understand that submitting this form does not create an attorney-client relationship and that information I send before an engagement is confirmed may not be treated as confidential.</label>
        <div><button class="btn btn-dark" type="submit">Send Inquiry</button></div>
        <p id="contact-status" class="form-status" role="status" aria-live="polite"></p>
      </form>
    </div>
    <aside class="contact-card">
      <dl>
        <dt>Office</dt><dd><a href="tel:{SITE["office_tel"]}">{SITE["office_phone"]}</a></dd>
        <dt>Mobile</dt><dd><a href="tel:{SITE["mobile_tel"]}">{SITE["mobile_phone"]}</a></dd>
        <dt>Email</dt><dd><a href="mailto:{SITE["email"]}">{SITE["email"]}</a></dd>
        <dt>Location</dt><dd>{SITE["city"]}<br><span class="small muted">Meetings in person, by phone, or by video.</span></dd>
      </dl>
      {sched}
    </aside>
  </div>
</section>'''
    page("/contact/", "Contact",
         "Contact J.T. Barnes & Associates, PLLC in Dallas, Texas for corporate finance, securities, fund formation, EB-5, and M&A counsel.",
         body)


def build_insights():
    if ARTICLES:
        items = "".join(f'''<a class="card" href="/insights/{a["slug"]}/">
  <span class="status status-soon">{a["category"]} &middot; {fmt_date(a["date"])}</span>
  <h3>{a["title"]}</h3><p>{a["summary"]}</p><span class="text-link">Read</span></a>''' for a in ARTICLES)
        archive = f'<div class="grid-3">{items}</div>'
    else:
        archive = '''<div class="grid-3">
  <div class="card"><span class="status status-dev">In preparation</span><h3>The Abundance Trap</h3><p>A long-form essay applying behavioral economics to professional identity and value in the age of AI.</p></div>
  <div class="card"><span class="status status-dev">In preparation</span><h3>Private funds, question by question</h3><p>A twice-weekly series working through the questions sponsors and investors actually ask about forming and investing in private funds.</p></div>
  <a class="card" href="/newsletter/"><span class="status status-live">Weekly</span><h3>Securities Compliance Weekly</h3><p>The week&rsquo;s regulatory developments and market trends for advisers, fund managers, and family offices.</p><span class="text-link">Subscribe</span></a>
</div>
<p class="small mt-sm">The first essays publish soon. Subscribe to the newsletter to receive them as they are released.</p>'''
    body = lab_hero([("Home", "/"), ("Insights", None)], "The Lab &middot; Insights",
                    "Writing on <em>private capital</em> and practice.",
                    "Analysis of private funds, securities offerings, family office trends, and the economics of professional work, written from an active transactional practice.")
    body += f'''
<section class="section">
  <div class="wrap">
    <div class="section-head"><span class="eyebrow">Series &amp; articles</span><h2>Latest writing</h2></div>
    {archive}
  </div>
</section>
<section class="section section-parchment">
  <div class="wrap split">
    <div>
      <span class="eyebrow">Speaking &amp; CLE</span>
      <h2>Programs for lawyers, advisers, and investors.</h2>
      <p>Jason speaks on private funds, securities offerings, EB-5 finance, and the practical use of technology in legal work, and is active in programming for the Dallas Bar Association Securities Section.</p>
      <p>To request a program or panel participation, <a href="/contact/">get in touch</a>.</p>
    </div>
    <div>
      <span class="eyebrow">Stay current</span>
      <h2>Securities Compliance Weekly</h2>
      <p>One email a week. No promotions.</p>
      {newsletter_form(compact=True)}
    </div>
  </div>
</section>'''
    page("/insights/", "Insights",
         "Insights from J.T. Barnes & Associates on private funds, securities offerings, family offices, EB-5 finance, and practice in the AI era.",
         body, zone="lab")

    for a in ARTICLES:
        d = date.fromisoformat(a["date"])
        body = lab_hero([("Home", "/"), ("Insights", "/insights/"), (a["category"], None)],
                        f'{a["category"]} &middot; {fmt_date(a["date"])}', a["title"], a["summary"])
        body += f'''
<section class="section">
  <div class="wrap"><article class="prose">{a["body"]}
    <p class="small muted">This article is general information, not legal advice, and does not create an attorney-client relationship.</p>
  </article></div>
</section>'''
        ld = {"@context": "https://schema.org", "@type": "Article", "headline": a["title"],
              "datePublished": a["date"], "author": {"@id": SITE["url"] + "/about/#jason"},
              "publisher": {"@id": SITE["url"] + "/#firm"}}
        page(f"/insights/{a['slug']}/", a["title"], a["summary"], body, zone="lab", jsonld=ld)


def build_newsletter():
    body = lab_hero([("Home", "/"), ("Newsletter", None)], "The Lab &middot; Newsletter",
                    "Securities <em>Compliance</em> Weekly",
                    "Regulatory developments, market trends, and practical guidance for investment advisers, fund managers, and family offices. Written from an active securities practice, not a content desk.")
    body += f'''
<section class="section">
  <div class="wrap split">
    <div>
      <span class="eyebrow">What each issue covers</span>
      <ul class="check-list">
        <li>SEC and state regulatory developments affecting private funds and advisers</li>
        <li>Alternative investment and fund formation trends</li>
        <li>EB-5 program updates and transactional guidance</li>
        <li>Family office and private capital market developments</li>
        <li>Practice and operations ideas for securities professionals</li>
      </ul>
      <p class="small muted mt-sm">The newsletter is general information, not legal advice. Subscribing does not create an attorney-client relationship.</p>
    </div>
    <div class="card">
      <span class="eyebrow">Subscribe</span>
      <h2>One email a week.</h2>
      <p>No promotions. Unsubscribe at any time.</p>
      {newsletter_form()}
    </div>
  </div>
</section>'''
    page("/newsletter/", "Securities Compliance Weekly",
         "Securities Compliance Weekly: regulatory developments and market trends for investment advisers, fund managers, and family offices.",
         body, zone="lab")


def build_lab():
    body = lab_hero([("Home", "/"), ("The Lab", None)], "The Lab",
                    "Practice tools, built in the <em>open</em>.",
                    "Generic productivity software assumes linear workflows. Transactional practice does not work that way. These are the tools I built to run my own practice, shared for anyone who wants to work the same way.")
    body += f'''
<section class="section">
  <div class="wrap">
    <div class="grid-3">
      <a class="card" href="/lab/timekeeper/"><span class="status status-live">In use</span><h3>Legal Timekeeper</h3><p>Matter-tagged time capture and reporting designed around how legal work is actually interrupted, resumed, and billed.</p><span class="text-link">Learn more</span></a>
      <a class="card" href="/lab/minder/"><span class="status status-dev">In development</span><h3>Legal Minder</h3><p>Natural-language scheduling that turns &ldquo;call the sponsor Tuesday at two&rdquo; into structured calendar entries for iOS and Outlook.</p><span class="text-link">Learn more</span></a>
      <a class="card" href="/newsletter/"><span class="status status-live">Weekly</span><h3>Intelligence pipeline</h3><p>An automated feed that gathers, scores, and summarizes regulatory and market news, and powers Securities Compliance Weekly.</p><span class="text-link">See the output</span></a>
    </div>
  </div>
</section>
<section class="section section-parchment">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">Working principles</span>
      <h2>AI is intake, not final output.</h2>
      <p class="lede">Every tool in the Lab follows the same workflow. Machines draft and organize; a lawyer reviews, decides, and signs.</p>
    </div>
    <div class="flow">
      <div><b>Generate</b><span>Drafts, extracts, and first passes produced quickly.</span></div>
      <div><b>Normalize</b><span>Output conformed to one style, numbering, and terminology standard.</span></div>
      <div><b>Validate</b><span>Defined terms, cross-references, and facts checked by a lawyer.</span></div>
      <div><b>Package</b><span>Clean deliverables in the format the reader needs.</span></div>
      <div><b>Preserve</b><span>Precedents and decisions captured for the next matter.</span></div>
    </div>
    <p class="small mt-sm">Tools in the Lab are shared for demonstration and general use. They are not legal services, and using them does not create an attorney-client relationship. Demonstrations use sample data only.</p>
  </div>
</section>'''
    page("/lab/", "The Lab: Practice Tools",
         "Practice tools built by a securities lawyer: the Legal Timekeeper, Legal Minder, and an automated regulatory intelligence pipeline.",
         body, zone="lab")

    # Timekeeper
    body = lab_hero([("Home", "/"), ("The Lab", "/lab/"), ("Legal Timekeeper", None)], "The Lab &middot; In use",
                    "Legal <em>Timekeeper</em>",
                    "Simple, accurate time tracking for legal work. No bloat and no learning curve, just a design built for the way a transactional practice actually operates.")
    body += f'''
<section class="section">
  <div class="wrap split">
    <div>
      <p>Most time-tracking software assumes you work on one thing at a time in neat blocks. Legal work does not fit that model: calls interrupt drafting, emails arrive mid-review, and deadlines move. The Timekeeper was built for that reality.</p>
      <ul class="check-list">
        <li>Fast time entry with matter tagging</li>
        <li>Daily, weekly, and monthly reporting</li>
        <li>Plain-language narratives ready for billing review</li>
        <li>Export for billing systems</li>
        <li>No subscription required</li>
      </ul>
      <p class="mt-sm"><a class="btn btn-teal" href="{SITE["timekeeper_url"]}" rel="noopener">Open the Timekeeper</a></p>
    </div>
    <div class="mock" role="img" aria-label="Sample Legal Timekeeper screen showing four time entries totaling 8.5 hours">
      <div class="mock-bar"><span></span><span></span><span></span><em>Legal Timekeeper &middot; sample data</em></div>
      <div class="mock-body">
        <div class="mock-row"><div>Sample Fund I, LP: LPA markup<small>Fund Formation</small></div><b>2.6h</b></div>
        <div class="mock-row"><div>Sample Holdings: term sheet review<small>M&amp;A &amp; Structured Finance</small></div><b>1.9h</b></div>
        <div class="mock-row"><div>Sample Regional Center: offering update<small>EB-5 Finance</small></div><b>3.2h</b></div>
        <div class="mock-row"><div>Newsletter: weekly issue<small>Practice Development</small></div><b>0.8h</b></div>
        <div class="mock-total">Today&rsquo;s total <b>8.5h</b></div>
      </div>
    </div>
  </div>
</section>'''
    page("/lab/timekeeper/", "Legal Timekeeper",
         "Legal Timekeeper: matter-tagged time tracking and reporting designed for transactional legal work.",
         body, zone="lab")

    # Minder
    body = lab_hero([("Home", "/"), ("The Lab", "/lab/"), ("Legal Minder", None)], "The Lab &middot; In development",
                    "Legal <em>Minder</em>",
                    "Calendar management, task tracking, and deadline awareness, built for the way a legal practice actually runs.")
    body += f'''
<section class="section">
  <div class="wrap split">
    <div>
      <p>Most calendar tools treat every appointment the same way. A client call, a filing deadline, a partner check-in, and a closing each carry different urgency, context, and follow-through. Legal Minder understands the difference.</p>
      <p>Describe what needs to happen and when, in plain language. Minder parses it, structures it, and pushes it into the calendar you already use (iOS, Outlook, or both) without adding another app to manage.</p>
      <p>Built as a companion to the Legal Timekeeper, Minder closes the loop between what you are tracking and what is actually scheduled.</p>
      <ul class="check-list">
        <li>Natural-language input</li>
        <li>Calendar export in standard ICS format for iOS and Outlook</li>
        <li>Matter and practice-area tagging</li>
        <li>Reminders for post-closing and filing obligations</li>
      </ul>
      <p class="mt-sm"><a class="btn btn-teal" href="/newsletter/">Follow development</a></p>
    </div>
    <div class="mock" role="img" aria-label="Sample Legal Minder conversation creating a calendar event from plain language">
      <div class="mock-bar"><span></span><span></span><span></span><em>Legal Minder &middot; sample data</em></div>
      <div class="mock-body">
        <div class="bubble user"><small>You</small>Schedule a call with the Sample Family Office Tuesday at 2pm, about an hour, fund structure review.</div>
        <div class="bubble"><small>Minder</small>Here is what I structured. Confirm to add it to your calendar.
          <div class="event">
            <div><span>Title</span>Sample Family Office: fund structure review</div>
            <div><span>When</span>Tuesday, 2:00 to 3:00 PM CT</div>
            <div><span>Tag</span>Family Office &middot; Client call</div>
            <div><span>Export</span>iOS Calendar and Outlook (ICS)</div>
          </div>
        </div>
        <div class="bubble user"><small>You</small>Confirmed. Remind me tomorrow morning to send the term sheet draft.</div>
        <div class="bubble"><small>Minder</small>Reminder set for 8:30 AM tomorrow: &ldquo;Send term sheet draft.&rdquo;</div>
      </div>
    </div>
  </div>
</section>'''
    page("/lab/minder/", "Legal Minder",
         "Legal Minder: natural-language calendar and deadline management for legal practices, exporting to iOS and Outlook.",
         body, zone="lab")


def build_legal():
    body = page_hero([("Home", "/"), ("Legal Notices", None)], "Legal",
                     "Legal notices and disclaimer.", "Please read these notices before relying on anything on this website.")
    body += f'''
<section class="section">
  <div class="wrap prose">
    <h2 id="advertising">Attorney advertising</h2>
    <p>This website is attorney advertising. {SITE["attorney"]} is the attorney responsible for its content. The firm&rsquo;s principal office is in {SITE["city"]}.</p>
    <p>{SITE["attorney"]} is licensed to practice law in Texas. The firm does not seek to represent anyone in a jurisdiction where this website does not comply with applicable rules. Not certified by the Texas Board of Legal Specialization.</p>

    <h2 id="no-advice">No legal advice</h2>
    <p>The content on this website, including articles, newsletters, and tools, is general information. It is not legal advice and should not be relied on for any specific matter. Laws change, and the application of law depends on particular facts.</p>

    <h2 id="no-relationship">No attorney-client relationship</h2>
    <p>Visiting this website, sending an email, completing the contact form, subscribing to the newsletter, or using any tool in the Lab does not create an attorney-client relationship. A relationship is formed only when the firm agrees to represent you in a signed engagement letter, after a conflicts check.</p>
    <p>Please do not send confidential or time-sensitive information until the firm has confirmed in writing that it can represent you. Information sent before then may not be treated as privileged or confidential.</p>

    <h2 id="results">Prior results and experience</h2>
    <p>Descriptions of experience, including transaction counts, countries, and years in practice, summarize Mr. Barnes&rsquo;s career, including work performed at prior firms. Every matter is different. Prior results do not guarantee a similar outcome.</p>

    <h2 id="eb5">EB-5 matters</h2>
    <p>The firm provides transactional and securities counsel in EB-5 matters. It does not prepare immigration petitions, which are handled by immigration counsel.</p>

    <h2 id="tools">Lab tools</h2>
    <p>Practice tools described or linked in the Lab are provided for demonstration and general use, as is, without warranty. They are not legal services. Demonstrations use sample data and do not depict client matters.</p>

    <h2 id="links">Third-party links</h2>
    <p>Links to other websites are provided for convenience. The firm is not responsible for their content or privacy practices.</p>

    <p class="small muted">Last updated {date.fromisoformat(SITE["updated"]).strftime("%B %Y")}.</p>
  </div>
</section>'''
    page("/legal/", "Legal Notices &amp; Disclaimer",
         f"Attorney advertising notice, disclaimer, and terms for {SITE['domain']}.", body)

    body = page_hero([("Home", "/"), ("Legal", "/legal/"), ("Privacy", None)], "Legal",
                     "Privacy policy.", "What this website collects, and what it does not.")
    body += f'''
<section class="section">
  <div class="wrap prose">
    <h2>Summary</h2>
    <p>This website does not use cookies, advertising trackers, or third-party analytics. Fonts and images are served from this website, so visiting a page does not send your information to font or image providers.</p>
    <h2>Information you send us</h2>
    <p>When you use the contact form or the newsletter form, your email program opens a pre-filled message to the firm, or the information is sent to a form or newsletter provider the firm uses for that purpose. The firm uses this information only to respond to you, check for conflicts, and send the newsletter if you asked for it. The firm does not sell personal information.</p>
    <h2>Server logs</h2>
    <p>Like all websites, this site&rsquo;s hosting provider automatically processes technical information such as IP addresses and browser type to deliver pages and keep the service secure. The firm does not use that information to identify visitors.</p>
    <h2>Newsletter</h2>
    <p>You can unsubscribe from Securities Compliance Weekly at any time using the link in any issue or by emailing <a href="mailto:{SITE["email"]}">{SITE["email"]}</a>.</p>
    <h2>Children</h2>
    <p>This website is intended for adults and is not directed to children under 13.</p>
    <h2>Changes and contact</h2>
    <p>The firm may update this policy and will post the revised version here. Questions can be sent to <a href="mailto:{SITE["email"]}">{SITE["email"]}</a>.</p>
    <p class="small muted">Last updated {date.fromisoformat(SITE["updated"]).strftime("%B %Y")}.</p>
  </div>
</section>'''
    page("/legal/privacy/", "Privacy Policy", f"Privacy policy for {SITE['domain']}.", body)


def build_404():
    body = page_hero([("Home", "/"), ("Not found", None)], "Page not found",
                     "That page has moved or no longer exists.",
                     ("If you followed a link from jasontbarnes.com, the content now lives on this site." if SITE["domain"] != "jasontbarnes.com" else "Try one of the pages below, or contact the firm directly."))
    body += '''
<section class="section">
  <div class="wrap">
    <div class="grid-3">
      <a class="card" href="/"><h3>Home</h3><p>Start from the firm home page.</p><span class="text-link">Go</span></a>
      <a class="card" href="/practice/"><h3>Practice areas</h3><p>Fund formation, securities offerings, family office, EB-5, M&amp;A, and real estate.</p><span class="text-link">Go</span></a>
      <a class="card" href="/contact/"><h3>Contact</h3><p>Reach Jason directly.</p><span class="text-link">Go</span></a>
    </div>
  </div>
</section>'''
    page("/404.html", "Page Not Found", "Page not found.", body, noindex=True)


def build_support_files():
    urls = []
    for path, noindex in PAGES:
        if noindex:
            continue
        pri = "1.0" if path == "/" else ("0.8" if path.count("/") <= 2 else "0.6")
        urls.append(f"  <url><loc>{SITE['url']}{path}</loc><lastmod>{SITE['updated']}</lastmod><priority>{pri}</priority></url>")
    with open(os.path.join(OUT, "sitemap.xml"), "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                + "\n".join(urls) + "\n</urlset>\n")
    with open(os.path.join(OUT, "robots.txt"), "w") as f:
        f.write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE['url']}/sitemap.xml\n")
    with open(os.path.join(OUT, "CNAME"), "w") as f:
        f.write(SITE["domain"] + "\n")
    if not ARGS.no_nojekyll:
        open(os.path.join(OUT, ".nojekyll"), "w").close()
    if ARGS.legacy_stubs:
        for old, new in LEGACY.items():
            target = SITE["url"] + new
            d = os.path.join(OUT, old.strip("/"))
            os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, "index.html"), "w") as f:
                f.write(f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Page moved</title>
<link rel="canonical" href="{target}"><meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url={new}">
</head><body><p>This page has moved to <a href="{new}">{target}</a>.</p></body></html>
''')


if __name__ == "__main__":
    build_home()
    build_practice()
    build_approach()
    build_about()
    build_contact()
    build_insights()
    build_newsletter()
    build_lab()
    build_legal()
    build_404()
    build_support_files()
    print(f"Built {len(PAGES)} pages into {OUT}")
