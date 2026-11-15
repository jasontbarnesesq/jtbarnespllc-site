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
    "timekeeper_url": "/lab/timekeeper/app/",
    # Optional booking link (Calendly, Microsoft Bookings, etc.). Blank = route to /contact/
    "scheduling_url": "",
    "updated": "2026-11-06",
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
        "summary": "Structuring and documenting private equity, private credit, real estate, and venture funds and co-investment vehicles for sponsors, managers, and the families and institutions that invest alongside them.",
        "overview": [
            "Jason has advised on fund formations across private equity, private credit, venture capital, real estate, and impact strategies, representing both the sponsors raising capital and the investors committing it.",
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
        "slug": "private-equity-private-credit",
        "title": "Private Equity &amp; Private Credit",
        "nav": "Private Equity &amp; Credit",
        "summary": "Fund, deal, and financing counsel for middle-market private equity sponsors, private credit managers, and the family offices that invest alongside them.",
        "overview": [
            "Private equity and private credit now sit side by side in most middle-market transactions. A sponsor raises a fund, acquires a company, and finances the acquisition with a direct lender rather than a bank. Jason advises at each layer of that structure: the fund that raises the capital, the transaction it backs, and the credit that finances it.",
            "Having represented sponsors, investors, and capital providers, he drafts with the next negotiation in mind: the side letter a limited partner will request, the lender consent needed at exit, and the covenant that matters when performance slips.",
        ],
        "work": [
            "Buyout, growth, and independent-sponsor vehicles, including deal-by-deal funds and co-investment vehicles",
            "Platform and add-on acquisitions, recapitalizations, and management rollover",
            "Direct lending, mezzanine, and opportunistic credit funds",
            "Senior, unitranche, and subordinated loan documentation",
            "Preferred equity and other structured capital",
            "Fund-level financing, including subscription lines and NAV facilities",
            "Texas usury, licensing, and securities questions in privately originated loans",
            "Family office direct lending and co-lending alongside institutional managers",
        ],
        "clients": "Middle-market and independent sponsors, private credit managers and emerging lenders, family offices investing directly or alongside sponsors, and the companies they back.",
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
            "Direct lending and private credit allocations",
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
            "Sponsor-backed acquisitions and add-ons, financed by banks or direct lenders",
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
# 3. Insights content. Everything under /insights/ is built from these lists.
#    ARTICLES  articles, client alerts, and blog posts (newest first). body is HTML:
#              <p> paragraphs, <h2> subheads. kind is "Article", "Client Alert", or "Commentary".
#    TALKS     Speaking & CLE programs (below)
#    SERIES    named collections; an article or program joins one with "series": "<slug>"
#    TOPICS    the topic tags; practice-area topics share the practice slug
# ---------------------------------------------------------------------------
ARTICLES = [
    {"slug": "continuation-vehicles-defensible-process", "featured": True,
     "title": "Continuation Vehicles After the Vacatur: What a Defensible Process Looks Like",
     "date": "2026-11-15", "kind": "Article",
     "topics": ["fund-formation", "private-equity-private-credit"],
     "program": "2026-11-02-private-market-liquidity",
     "summary": "The SEC rule that would have required a fairness opinion is gone. The sponsor's duty is not. What investors, advisory committees, and sponsors should expect from a continuation vehicle process now that ILPA has finalized its guidance."},
    {"slug": "is-your-loan-a-security", "featured": True,
     "title": "Is Your Loan a Security? Three Questions for Private Credit Lenders and Borrowers",
     "date": "2026-11-15", "kind": "Article",
     "topics": ["private-equity-private-credit", "real-estate", "capital-markets"],
     "program": "2026-08-24-securities-issues-in-private-credit",
     "summary": "A private credit deal is a lending transaction and, very often, three separate securities questions: the fund that raised the money, the loan itself, and whoever was paid to find the capital. Where each one bites, for corporate and real estate credit alike."},
    {"slug": "rolling-equity-in-a-private-equity-sale", "featured": True,
     "title": "Rolling Equity in a Private Equity Sale: The Securities Questions Sellers Should Ask",
     "date": "2026-11-15", "kind": "Article",
     "topics": ["ma-structured-finance", "family-office"],
     "program": "2026-02-securities-compliance-in-ma",
     "summary": "Rollover equity, seller notes, and earnouts are securities or may be. The rights founders and families most often leave on the table when selling to a private equity buyer, and how to protect the value that is not paid at closing."},
    # {
    #     "slug": "example-article",               # page: /insights/articles/example-article/
    #     "title": "Article title",
    #     "date": "2026-11-03",
    #     "kind": "Article",                       # Article, Client Alert, or Commentary
    #     "topics": ["fund-formation"],            # one or more TOPICS slugs
    #     "series": "",                            # optional SERIES slug
    #     "summary": "One or two sentences for cards and search results.",
    #     "body": "<p>First paragraph.</p>",      # or omit and put the HTML in content/articles/<slug>.html
    #     "featured": True,                        # shown in the Featured row on the Insights hub
    #     "program": "<TALKS slug>",               # related Speaking & CLE program, cross-linked both ways
    # },
]


# ---------------------------------------------------------------------------
# Speaking & CLE: Dallas Bar Association Securities Section programs.
# Slides live in docs/assets/speaking/<slug>.pdf with a title-slide thumbnail at <slug>.webp.
# To add a program: drop both files in that folder and add a dict here (newest first).
#   quickref   path to the two-page quick reference PDF once it exists ("" hides the link)
#   published  False keeps a program off the site (for example, until a co-panelist approves)
# ---------------------------------------------------------------------------
TALKS = [
    {"slug": "2026-11-02-private-market-liquidity", "topics": ["private-equity-private-credit", "fund-formation", "capital-markets"], "date": "2026-11-02", "date_label": "November 2, 2026",
     "title": "Private Market Liquidity in 2026",
     "subtitle": "Secondaries, Continuation Vehicles and Tender Offer Strategies",
     "pages": 24, "bytes": 217727, "thumb": (720, 405),
     "quickref": "/assets/speaking/2026-11-02-private-market-liquidity-quick-reference.pdf", "article": "continuation-vehicles-defensible-process", "published": True},
    {"slug": "2026-08-24-securities-issues-in-private-credit", "topics": ["private-equity-private-credit", "fund-formation"], "date": "2026-08-24", "date_label": "August 24, 2026",
     "title": "Securities Issues in Private Credit",
     "subtitle": "The Fastest-Growing Corner of Private Capital",
     "pages": 22, "bytes": 201782, "thumb": (932, 720),
     "quickref": "/assets/speaking/2026-08-24-securities-issues-in-private-credit-quick-reference.pdf", "article": "is-your-loan-a-security", "published": True},
    {"slug": "2026-07-27-enforcement-lessons-for-transactional-lawyers", "topics": ["enforcement-compliance", "capital-markets"], "date": "2026-07-27", "date_label": "July 27, 2026",
     "title": "Enforcement Lessons for Transactional Lawyers",
     "subtitle": "How Routine Transactions Become Regulatory Investigations",
     "pages": 18, "bytes": 180538, "thumb": (720, 557),
     "quickref": "", "published": True},
    {"slug": "2026-06-22-the-new-disclosure-landscape", "topics": ["capital-markets", "enforcement-compliance"], "date": "2026-06-22", "date_label": "June 22, 2026",
     "title": "The New Disclosure Landscape",
     "subtitle": "Tariffs, Foreign Capital, CFIUS and Private Offerings",
     "pages": 19, "bytes": 174672, "thumb": (720, 540),
     "quickref": "", "published": True},
    {"slug": "2026-05-04-before-they-call-you", "topics": ["enforcement-compliance", "fund-formation"], "date": "2026-05-04", "date_label": "May 4, 2026",
     "title": "Before They Call You",
     "subtitle": "Recordkeeping, Sweep Examinations, and the Case for Self-Reporting",
     "pages": 16, "bytes": 131430, "thumb": (720, 557),
     "quickref": "", "published": True},
    {"slug": "2026-03-30-finra-under-the-hood", "topics": ["capital-markets", "enforcement-compliance"], "date": "2026-03-30", "date_label": "March 30, 2026",
     "title": "FINRA Under the Hood",
     "subtitle": "Private Placements, Finders, and Alternatives",
     "pages": 15, "bytes": 344392, "thumb": (932, 720),
     "quickref": "", "published": False,
     "note": "Moderated panel with John F. Guild, Bell Nunnally (former FINRA examiner)"},
    {"slug": "2026-02-securities-compliance-in-ma", "topics": ["ma-structured-finance", "capital-markets"], "date": "2026-02-01", "date_label": "February 2026",
     "title": "Securities Compliance in M&amp;A: A Deal Lawyer&rsquo;s Playbook",
     "subtitle": "Navigating Securities Issues, Rollover Structures, and Seller Wealth Protection",
     "pages": 16, "bytes": 2178397, "thumb": (932, 720),
     "quickref": "/assets/speaking/2026-02-securities-compliance-in-ma-quick-reference.pdf", "article": "rolling-equity-in-a-private-equity-sale", "published": True},
    {"slug": "2025-11-24-foundations-of-fund-counsel-part-2", "topics": ["fund-formation", "private-equity-private-credit"], "series": "foundations-of-fund-counsel", "date": "2025-11-24", "date_label": "November 24, 2025",
     "title": "Foundations of Fund Counsel, Part 2",
     "subtitle": "Key Rules and Regulations for Counsel Advising Investment Funds and Advisers",
     "pages": 34, "bytes": 713752, "thumb": (720, 540),
     "quickref": "", "published": True},
    {"slug": "2025-10-27-foundations-of-fund-counsel-part-1", "topics": ["fund-formation", "private-equity-private-credit"], "series": "foundations-of-fund-counsel", "date": "2025-10-27", "date_label": "October 27, 2025",
     "title": "Foundations of Fund Counsel, Part 1",
     "subtitle": "Key Rules and Regulations for Counsel Advising Investment Funds and Advisers",
     "pages": 46, "bytes": 930653, "thumb": (720, 540),
     "quickref": "", "published": True},
    {"slug": "2025-09-29-real-estate-as-a-security", "topics": ["real-estate", "capital-markets"], "date": "2025-09-29", "date_label": "September 29, 2025",
     "title": "Real Estate as a Security",
     "subtitle": "From the Howey Test to the Advisers Act",
     "pages": 35, "bytes": 149357, "thumb": (720, 540),
     "quickref": "", "published": True},
    {"slug": "2025-08-25-managing-securities-risks-in-ma", "topics": ["ma-structured-finance", "capital-markets"], "date": "2025-08-25", "date_label": "August 25, 2025",
     "title": "Managing Securities Risks in M&amp;A Transactions",
     "subtitle": "From Due Diligence to Post-Closing Integration",
     "pages": 25, "bytes": 260998, "thumb": (720, 540),
     "quickref": "", "published": True},
    {"slug": "2025-06-23-rule-144-and-secondary-markets", "topics": ["capital-markets"], "date": "2025-06-23", "date_label": "June 23, 2025",
     "title": "From Restriction to Resale",
     "subtitle": "Practical Insights on Rule 144 and Secondary Markets",
     "pages": 26, "bytes": 398977, "thumb": (720, 540),
     "quickref": "", "published": True},
    {"slug": "2025-05-19-avoiding-pitfalls-in-private-offerings", "topics": ["capital-markets", "enforcement-compliance"], "date": "2025-05-19", "date_label": "May 19, 2025",
     "title": "Avoiding Pitfalls in Private Offerings",
     "subtitle": "",
     "pages": 26, "bytes": 711934, "thumb": (720, 540),
     "quickref": "", "published": True},
    {"slug": "2025-04-28-securities-compliance-in-eb5-offerings", "topics": ["eb5", "capital-markets"], "date": "2025-04-28", "date_label": "April 28, 2025",
     "title": "Securities Compliance and the U.S. EB-5 Program",
     "subtitle": "Understanding Best Practices for Stakeholders and Counsel",
     "pages": 35, "bytes": 321290, "thumb": (720, 540),
     "quickref": "", "published": True},
    {"slug": "2025-01-27-securities-compliance-town-hall", "topics": ["enforcement-compliance", "capital-markets"], "date": "2025-01-27", "date_label": "January 27, 2025",
     "title": "Securities Compliance Town Hall",
     "subtitle": "Lessons from 2024 and What to Expect in 2025",
     "pages": 46, "bytes": 533483, "thumb": (720, 540),
     "quickref": "", "published": True},
]

# Upcoming programs (shown at the top of Speaking & CLE until the date passes). Newest last.
# {"date": "2027-01-25", "title": "...", "subtitle": "...", "venue": "Dallas Bar Association Securities Section",
#  "credit": "1.0 hour CLE, including 0.5 ethics", "topics": ["capital-markets"]}
UPCOMING = []

TOPICS = [
    # (slug, label, practice-page slug or None)
    ("fund-formation", "Fund Formation", "fund-formation"),
    ("private-equity-private-credit", "Private Equity &amp; Private Credit", "private-equity-private-credit"),
    ("capital-markets", "Capital Markets &amp; Offerings", "capital-markets"),
    ("family-office", "Family Office", "family-office"),
    ("eb5", "EB-5 Finance", "eb5"),
    ("ma-structured-finance", "M&amp;A &amp; Structured Finance", "ma-structured-finance"),
    ("real-estate", "Real Estate", "real-estate"),
    ("enforcement-compliance", "Enforcement &amp; Compliance", None),
    ("practice-of-law", "Practice of Law", None),
]
TOPIC = {t[0]: {"slug": t[0], "label": t[1], "practice": t[2]} for t in TOPICS}
TOPIC_LEDE = {
    "enforcement-compliance": "SEC, FINRA, and state enforcement trends, examinations, and the compliance practices that keep routine transactions from becoming investigations.",
    "practice-of-law": "How legal work is organized, priced, and delivered, including the practical use of AI and technology in a transactional practice.",
}

SERIES = [
    {"slug": "foundations-of-fund-counsel", "title": "Foundations of Fund Counsel",
     "status": "Two-part program",
     "summary": "A two-part Dallas Bar Association Securities Section program on the key rules and regulations for counsel advising investment funds and advisers.",
     "topics": ["fund-formation", "private-equity-private-credit"]},
    {"slug": "private-funds-question-by-question", "title": "Private Funds, Question by Question",
     "status": "In preparation",
     "summary": "A twice-weekly series working through the questions sponsors and investors actually ask about forming and investing in private funds.",
     "topics": ["fund-formation", "private-equity-private-credit"]},
    {"slug": "the-abundance-trap", "title": "The Abundance Trap",
     "status": "In preparation",
     "summary": "A long-form essay applying behavioral economics to professional identity and value in the age of AI.",
     "topics": ["practice-of-law"]},
]

# ---------------------------------------------------------------------------
# 4. Layout
# ---------------------------------------------------------------------------
PAGES = []  # (path, noindex) for sitemap

NAV = [("Practice", "/practice/"), ("Approach", "/approach/"), ("About", "/about/"),
       ("Insights", "/insights/"), ("Contact", "/contact/")]
INSIGHTS_NAV = [("All insights", "/insights/"), ("Articles", "/insights/articles/"),
                ("Series", "/insights/series/"), ("Speaking &amp; CLE", "/insights/speaking/"),
                ("Topics", "/insights/topics/"),
                ("Newsletter", "/newsletter/")]
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
    def item(t, h):
        if h != "/insights/":
            return f'<li><a href="{h}"{cur(h)}>{t}</a></li>'
        on = current(path, h) or path.startswith("/newsletter/")
        sub = "".join(f'<li><a href="{sh}">{st}</a></li>' for st, sh in INSIGHTS_NAV[1:])
        return (f'<li class="has-sub"><a href="{h}"{' aria-current="page"' if on else ""}>{t}</a>'
                f'<ul class="subnav" aria-label="Insights">{sub}</ul></li>')
    main = "".join(item(t, h) for t, h in NAV)
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
        <img src="/assets/img/brand/barnes-logo-primary.svg" width="136" height="37" alt="Barnes">
        <span class="brand-name">J.T. Barnes<br>&amp; Associates, PLLC</span>
      </a>
      <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="primary-nav">Menu</button>
      <nav class="primary-nav" id="primary-nav" aria-label="Primary">
        <ul>{main}</ul>
        <a class="btn btn-primary" href="{schedule_href()}"{schedule_attrs()}>Schedule a consultation</a>
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
        <img src="/assets/img/brand/barnes-logo-reversed.svg" width="150" height="41" alt="Barnes">
        <p><strong>{SITE["firm"]}</strong></p>
        <p>Institutional-quality counsel for private capital.</p>
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
          <li><a href="{schedule_href()}"{schedule_attrs()}>Schedule a consultation</a></li>
        </ul>
      </div>
      <div>
        <h4>Insights</h4>
        <ul>
          <li><a href="/insights/">All insights</a></li>
          <li><a href="/insights/articles/">Articles</a></li>
          <li><a href="/insights/series/">Series</a></li>
          <li><a href="/insights/speaking/">Speaking &amp; CLE</a></li>
          <li><a href="/newsletter/">Signal (newsletter)</a></li>
        </ul>
      </div>
      <div>
        <h4>The Lab</h4>
        <ul>
          <li><a href="/lab/">Practice Tools</a></li>
          <li><a href="/lab/timekeeper/">Legal Timekeeper</a></li>
          <li><a href="/lab/minder/">Legal Minder</a></li>
          <li><a href="/lab/prompt-coach/">Legal Prompt Coach</a></li>
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
<meta name="theme-color" content="#FFFFFF">
<meta property="og:site_name" content="{SITE["firm"]}">
<meta property="og:type" content="website">
<meta property="og:title" content="{full_title}">
<meta property="og:description" content="{escape(description, quote=True)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE["url"]}/assets/img/og-image.jpg?v={ASSET_V["og"]}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/svg+xml" href="/assets/img/favicon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/img/favicon-32.png">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<link rel="preload" href="/assets/fonts/libre-franklin-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/libre-franklin-latin-800-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/css/site.css?v={ASSET_V["css"]}">
<script src="/assets/js/site.js?v={ASSET_V["js"]}" defer></script>{ld}
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


def _asset_version(rel):
    """Short content hash, appended to asset URLs so browsers fetch a fresh copy whenever the file changes."""
    import hashlib
    return hashlib.sha256(open(os.path.join(ROOT, "docs", rel), "rb").read()).hexdigest()[:10]


ASSET_V = {"css": _asset_version("assets/css/site.css"), "js": _asset_version("assets/js/site.js"),
           "og": _asset_version("assets/img/og-image.jpg")}


def closing(h1):
    """End the headline with the brand's closing corner in place of its period, keeping the corner
    on the same line as the last word."""
    head, _, last = h1.rstrip().rpartition(" ")
    # The corner closes the statement, as it does in the logo, so it replaces a final period.
    # Other end punctuation (a question mark, say) stays.
    if last.endswith(".") and not last.endswith(".."):
        last = last[:-1]
    corner = '<span class="corner" aria-hidden="true"></span>'
    if last.endswith("</em>") and "<em>" not in last:
        # The highlight spans several words: keep the corner inside it so the tags nest correctly.
        tail = f'<span class="close-word">{last[:-5]}{corner}</span></em>'
    else:
        tail = f'<span class="close-word">{last}{corner}</span>'
    return f"{head} {tail}" if head else tail


def page_hero(crumbs, eyebrow, h1, lede):
    trail = " &rsaquo; ".join(f'<a href="{h}">{t}</a>' if h else t for t, h in crumbs)
    return f'''<section class="page-hero">
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb">{trail}</nav>
    <span class="eyebrow">{eyebrow}</span>
    <h1>{closing(h1)}</h1>
    <p class="lede">{lede}</p>
  </div>
</section>'''


def lab_hero(crumbs, badge, h1, lede):
    trail = " &rsaquo; ".join(f'<a href="{h}">{t}</a>' if h else t for t, h in crumbs)
    return f'''<section class="lab-hero">
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb">{trail}</nav>
    <span class="lab-badge">{badge}</span>
    <h1>{closing(h1)}</h1>
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
      <a class="btn btn-primary" href="{schedule_href()}"{schedule_attrs()}>Schedule a consultation</a>
      <a class="btn btn-ghost" href="tel:{SITE["office_tel"]}">Call {SITE["office_phone"]}</a>
    </div>
  </div>
</section>'''


def newsletter_form(compact=False):
    name_field = "" if compact else '''<div><label for="nl-name">Name</label><input id="nl-name" name="name" type="text" autocomplete="name"></div>'''
    return f'''<form class="form newsletter-form" novalidate>
  {name_field}
  <div><label for="nl-email{'-c' if compact else ''}">Email</label><input id="nl-email{'-c' if compact else ''}" name="email" type="email" autocomplete="email" required></div>
  <div><button class="btn btn-primary" type="submit">Subscribe</button></div>
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
    "knowsAbout": ["Securities law", "Private fund formation", "Private equity", "Private credit", "Private placements",
                   "Family office structuring", "EB-5 finance", "Mergers and acquisitions", "Real estate joint ventures"],
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

    cards += f'''<a class="card card-cta on-dark" href="/contact/">
  <span class="index">Not sure?</span>
  <h3>Where does your matter fit?</h3>
  <p>Most transactions touch several of these areas. Describe yours in general terms and Jason will tell you how he can help.</p>
  <span class="text-link">Start a conversation</span>
</a>'''
    body = f'''<section class="hero on-dark">
  <div class="wrap">
    <div>
      <span class="eyebrow">{SITE["firm"]}</span>
      <h1>{closing("Corporate finance and securities counsel for <em>families, funds,</em> and the middle market.")}</h1>
      <p class="lede">Nearly 30 years structuring, documenting, and negotiating the transactions that connect capital providers with the businesses and sponsors raising it. Institutional-quality work, delivered directly by the attorney you hire.</p>
      <div class="hero-actions">
        <a class="btn btn-primary" href="{schedule_href()}"{schedule_attrs()}>Schedule a consultation</a>
        <a class="btn btn-ghost" href="/practice/">Practice areas</a>
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
    <div class="grid-4">{cards}</div>
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
      <div><h4>Private equity &amp; credit managers</h4><p>Funds, acquisitions, and financing.</p></div>
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
      <a class="card" href="/newsletter/"><span class="status status-live">Every other Tuesday</span><h3>Signal</h3><p>Private capital, read clearly: what changed for fund sponsors, private lenders, EB-5 projects, and family offices, and why it matters.</p><span class="text-link">Subscribe</span></a>
      <a class="card" href="/lab/"><span class="status status-dev">Tools</span><h3>Practice tools</h3><p>The Legal Timekeeper, Legal Minder, Legal Prompt Coach, and the systems behind a technology-enabled practice.</p><span class="text-link">Explore the Lab</span></a>
    </div>
  </div>
</section>

{cta_band()}'''
    page("/", f"{SITE['short']} | Corporate Finance &amp; Securities Counsel, Dallas",
         "J.T. Barnes & Associates, PLLC: corporate finance, securities, fund formation, private equity, private credit, family office, EB-5, M&A, and real estate capital counsel for families, funds, and middle-market businesses. Dallas, Texas.",
         body, jsonld=ORG_LD)


def build_practice():
    cards = "".join(f'''<a class="card card-top-rule" href="/practice/{p["slug"]}/">
  <span class="index">{i:02d}</span>
  <h3>{p["title"]}</h3>
  <p>{p["summary"]}</p>
  <span class="text-link">Learn more</span>
</a>''' for i, p in enumerate(PRACTICE, 1))

    cards += f'''<a class="card card-cta on-dark" href="/contact/">
  <span class="index">Not sure?</span>
  <h3>Where does your matter fit?</h3>
  <p>Most transactions touch several of these areas. Describe yours in general terms and Jason will tell you how he can help.</p>
  <span class="text-link">Start a conversation</span>
</a>'''
    body = page_hero([("Home", "/"), ("Practice", None)], "Practice Areas",
                     "Structuring, documenting, and negotiating capital transactions.",
                     "The practice links capital providers with those seeking capital, across borders both physical and figurative, for clients ranging from early-stage sponsors to multi-generational family offices.")
    body += f'''
<section class="section">
  <div class="wrap">
    <div class="grid-4">{cards}</div>
  </div>
</section>
<section class="section section-stone">
  <div class="wrap">
    {stats_block()}
  </div>
</section>
{cta_band()}'''
    page("/practice/", "Practice Areas",
         "Fund formation, private equity and private credit, securities offerings, family office advisory, EB-5 finance, M&A and joint ventures, and real estate capital transactions.",
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
        <a class="btn btn-primary" href="{schedule_href()}"{schedule_attrs()}>Schedule a consultation</a>
      </div>
      <nav class="related" aria-label="Other practice areas">
        <span class="eyebrow">Other practice areas</span>
        {related}
      </nav>
    </aside>
  </div>
</section>
{related_insights(p["slug"])}
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
        sched = f'<p><a class="btn btn-primary" href="{SITE["scheduling_url"]}" target="_blank" rel="noopener">Book a time online</a></p>'
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
        <div><button class="btn btn-primary" type="submit">Send inquiry</button></div>
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
         "Contact J.T. Barnes & Associates, PLLC in Dallas, Texas for corporate finance, securities, fund formation, private equity, private credit, EB-5, and M&A counsel.",
         body)


def build_insights_all():
    """Insights hub and every page under /insights/, all built from ARTICLES, TALKS, SERIES, TOPICS."""
    items = insight_items()
    build_insights_hub(items)
    build_articles(items)
    build_series(items)
    build_speaking()
    build_topics(items)


def article_body(a):
    if a.get("body"):
        return a["body"]
    with open(os.path.join(ROOT, "content", "articles", a["slug"] + ".html"), encoding="utf8") as f:
        return f.read()


def insight_items():
    out = []
    for a in ARTICLES:
        out.append({"type": "article", "label": a.get("kind", "Article"), "date": a["date"],
                    "date_label": fmt_date(a["date"]), "title": a["title"], "summary": a["summary"],
                    "url": f'/insights/articles/{a["slug"]}/', "pdf": False, "topics": a.get("topics", []),
                    "series": a.get("series", ""), "thumb": None})
    for t in TALKS:
        if not t["published"]:
            continue
        out.append({"type": "program", "label": "Program", "date": t["date"], "date_label": t["date_label"],
                    "title": t["title"], "summary": t["subtitle"],
                    "url": f'/assets/speaking/{t["slug"]}.pdf', "pdf": True, "topics": t.get("topics", []),
                    "series": t.get("series", ""),
                    "thumb": (f'/assets/speaking/{t["slug"]}.webp', *t["thumb"]),
                    "meta": f'Slides, {t["pages"]} pages'})
    return sorted(out, key=lambda i: i["date"], reverse=True)


def insights_subnav(path):
    links = "".join(
        f'<a href="{h}"{" aria-current=\"page\"" if (path == h or (h != "/insights/" and path.startswith(h))) else ""}>{t}</a>'
        for t, h in INSIGHTS_NAV)
    return f'<nav class="subnav-bar" aria-label="Insights sections"><div class="wrap">{links}</div></nav>'


def topic_tags(topics):
    if not topics:
        return ""
    links = "".join(f'<a href="/insights/topics/{t}/">{TOPIC[t]["label"]}</a>' for t in topics if t in TOPIC)
    return f'<p class="tags">{links}</p>'


def feed(items):
    rows = []
    for i in items:
        pdf = ' <span class="muted">(PDF)</span>' if i["pdf"] else ""
        summary = f'<p>{i["summary"]}</p>' if i["summary"] else ""
        rows.append(f'''<li class="feed-item">
  <p class="feed-meta"><span class="feed-type">{i["label"]}</span><span>{i["date_label"]}</span></p>
  <h3><a href="{i["url"]}">{i["title"]}</a>{pdf}</h3>
  {summary}{topic_tags(i["topics"])}
</li>''')
    return f'<ul class="feed">{"".join(rows)}</ul>'


def series_card(sr, items):
    parts = [i for i in items if i["series"] == sr["slug"]]
    status = f'{len(parts)} parts' if parts else sr["status"]
    cls = "status-live" if parts else "status-dev"
    return f'''<a class="card" href="/insights/series/{sr["slug"]}/">
  <span class="status {cls}">{status}</span>
  <h3>{sr["title"]}</h3><p>{sr["summary"]}</p><span class="text-link">View series</span></a>'''


def topic_grid(items):
    cells = []
    for slug, label, _ in TOPICS:
        n = sum(1 for i in items if slug in i["topics"])
        count = f'{n} item{"s" if n != 1 else ""}' if n else "Coming soon"
        cells.append(f'<a class="topic-link" href="/insights/topics/{slug}/"><span>{label}</span><span class="muted">{count}</span></a>')
    return f'<div class="topic-grid">{"".join(cells)}</div>'


def subscribe_band():
    return f'''<section class="section section-parchment">
  <div class="wrap split">
    <div>
      <span class="eyebrow">Programs and panels</span>
      <h2>Bring a program to your group.</h2>
      <p>Jason speaks on private funds, securities offerings, EB-5 finance, and the practical use of technology in legal work, and is active in programming for the Dallas Bar Association Securities Section.</p>
      <p>To request a program or invite Jason to join a panel, <a href="/contact/">get in touch</a>.</p>
    </div>
    <div>
      <span class="eyebrow">Stay current</span>
      <h2>Signal</h2>
      <p>Private capital, read clearly. Every other Tuesday; no promotions.</p>
      {newsletter_form(compact=True)}
    </div>
  </div>
</section>'''


def build_insights_hub(items):
    articles = [i for i in items if i["type"] == "article"]
    programs = [i for i in items if i["type"] == "program"]
    featured = [a for a in ARTICLES if a.get("featured")][:3]
    feature = ""
    if featured:
        talk_by = {t["slug"]: t for t in TALKS}
        cards = []
        for a in featured:
            t = talk_by.get(a.get("program", ""))
            rel = (f'<p class="related-program"><span class="muted">From the program</span> <a href="/insights/speaking/#{t["slug"]}">{t["title"]}</a></p>'
                   if t else "")
            cards.append(f'''<article class="card featured-card">
  <p class="feed-meta"><span class="feed-type">{a.get("kind", "Article")}</span><span>{fmt_date(a["date"])}</span></p>
  <h3><a href="/insights/articles/{a["slug"]}/">{a["title"]}</a></h3>
  <p>{a["summary"]}</p>
  {topic_tags(a.get("topics", []))}
  {rel}
  <a class="text-link" href="/insights/articles/{a["slug"]}/">Read the article</a>
</article>''')
        feature = f'''<section class="section">
  <div class="wrap">
    <div class="section-head"><span class="eyebrow">Featured</span><h2>New from the practice</h2></div>
    <div class="grid-3 featured-grid">{"".join(cards)}</div>
  </div>
</section>'''
    n_art = f'{len(articles)} published' if articles else "First pieces publishing soon"
    types = f'''<div class="grid-4 type-grid">
  <a class="card card-top-rule" href="/insights/articles/"><span class="index">{n_art}</span><h3>Articles</h3><p>Articles, client alerts, and commentary on private capital transactions and regulation.</p><span class="text-link">Browse articles</span></a>
  <a class="card card-top-rule" href="/insights/series/"><span class="index">{len(SERIES)} series</span><h3>Series</h3><p>Multi-part collections, from the Foundations of Fund Counsel program to a question-by-question guide to private funds.</p><span class="text-link">Browse series</span></a>
  <a class="card card-top-rule" href="/insights/speaking/"><span class="index">{len(programs)} programs</span><h3>Speaking &amp; CLE</h3><p>Slides from Dallas Bar Association Securities Section programs, with quick references to follow.</p><span class="text-link">Browse programs</span></a>
  <a class="card card-top-rule" href="/newsletter/"><span class="index">Every other Tuesday</span><h3>Signal</h3><p>The newsletter: what changed in private capital, and why it matters, in a five-minute read.</p><span class="text-link">Subscribe</span></a>
</div>'''
    body = page_hero([("Home", "/"), ("Insights", None)], "Insights",
                     "Writing and programs on <em>private capital</em>.",
                     "Articles, series, and CLE programs on private funds, securities offerings, family offices, EB-5 finance, and the practice of law, from an active transactional practice.")
    body += insights_subnav("/insights/")
    body += feature
    body += f'''
<section class="section section-stone">
  <div class="wrap">
    <div class="section-head"><span class="eyebrow">Browse by type</span><h2>Find what you need</h2></div>
    {types}
  </div>
</section>
<section class="section" id="topics">
  <div class="wrap">
    <div class="section-head"><span class="eyebrow">Browse by topic</span><h2>Topics</h2></div>
    {topic_grid(items)}
  </div>
</section>
<section class="section section-stone">
  <div class="wrap">
    <div class="section-head"><span class="eyebrow">Latest</span><h2>Recent insights</h2></div>
    {feed([i for i in items if not (i['type'] == 'article' and any(a['slug'] in i['url'] for a in featured))][:8])}
    <p class="mt-sm"><a class="text-link" href="/insights/speaking/">All programs and slides</a></p>
  </div>
</section>
{subscribe_band()}'''
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "Insights",
          "url": SITE["url"] + "/insights/", "publisher": {"@id": SITE["url"] + "/#firm"}}
    page("/insights/", "Insights",
         "Articles, series, and CLE programs from J.T. Barnes & Associates on private funds, securities offerings, family offices, EB-5 finance, and the practice of law.",
         body, jsonld=ld)


def build_articles(items):
    articles = [i for i in items if i["type"] == "article"]
    if articles:
        listing = feed(articles)
    else:
        upcoming = "".join(series_card(sr, items) for sr in SERIES if sr["status"] == "In preparation")
        listing = f'''<p>The first articles publish soon. Subscribe to <a href="/newsletter/">Signal</a> to receive them as they are released.</p>
<div class="grid-3 mt-sm">{upcoming}</div>'''
    body = page_hero([("Home", "/"), ("Insights", "/insights/"), ("Articles", None)], "Insights &middot; Articles",
                     "Articles and <em>alerts</em>.",
                     "Articles, client alerts, and commentary on private capital transactions, securities regulation, and the practice of law.")
    body += insights_subnav("/insights/articles/")
    body += f'''
<section class="section">
  <div class="wrap">{listing}</div>
</section>
{subscribe_band()}'''
    page("/insights/articles/", "Articles",
         "Articles, client alerts, and commentary from J.T. Barnes & Associates on private funds, securities offerings, and private capital.",
         body)

    for a in ARTICLES:
        crumbs = [("Home", "/"), ("Insights", "/insights/"), ("Articles", "/insights/articles/"), (a.get("kind", "Article"), None)]
        body = page_hero(crumbs, f'{a.get("kind", "Article")} &middot; {fmt_date(a["date"])} &middot; Jason T. Barnes', a["title"], a["summary"])
        body += insights_subnav("/insights/articles/")
        body += f'''
<section class="section">
  <div class="wrap"><article class="prose">{article_body(a)}
    {topic_tags(a.get("topics", []))}
    <p class="small muted">This article is general information, not legal advice, and does not create an attorney-client relationship.</p>
  </article></div>
</section>'''
        ld = {"@context": "https://schema.org", "@type": "Article", "headline": a["title"],
              "datePublished": a["date"], "author": {"@id": SITE["url"] + "/about/#jason"},
              "publisher": {"@id": SITE["url"] + "/#firm"}}
        page(f"/insights/articles/{a['slug']}/", a["title"], a["summary"], body, jsonld=ld)


def build_series(items):
    cards = "".join(series_card(sr, items) for sr in SERIES)
    body = page_hero([("Home", "/"), ("Insights", "/insights/"), ("Series", None)], "Insights &middot; Series",
                     "Series and <em>collections</em>.",
                     "Multi-part programs and writing projects that work through a subject in depth.")
    body += insights_subnav("/insights/series/")
    body += f'''
<section class="section">
  <div class="wrap"><div class="grid-3">{cards}</div></div>
</section>
{subscribe_band()}'''
    page("/insights/series/", "Series",
         "Multi-part programs and writing series from J.T. Barnes & Associates on private funds, fund counsel, and the practice of law.",
         body)

    for sr in SERIES:
        parts = sorted((i for i in items if i["series"] == sr["slug"]), key=lambda i: i["date"])
        if parts:
            content = feed(parts)
        else:
            content = f'''<div class="note-box"><strong>{sr["status"]}.</strong> The first installments publish soon. Subscribe to <a href="/newsletter/">Signal</a> to receive them as they are released.</div>'''
        body = page_hero([("Home", "/"), ("Insights", "/insights/"), ("Series", "/insights/series/"), (sr["title"], None)],
                         f'Series &middot; {sr["status"] if not parts else str(len(parts)) + " parts"}', sr["title"], sr["summary"])
        body += insights_subnav("/insights/series/")
        body += f'''
<section class="section">
  <div class="wrap">
    {content}
    {topic_tags(sr["topics"])}
  </div>
</section>
{subscribe_band()}'''
        page(f'/insights/series/{sr["slug"]}/', sr["title"], sr["summary"], body)


def build_topics(items):
    body = page_hero([("Home", "/"), ("Insights", "/insights/"), ("Topics", None)], "Insights &middot; Topics",
                     "Browse by <em>topic</em>.",
                     "Every article, series, and program, organized by the practice areas and subjects they address.")
    body += insights_subnav("/insights/topics/")
    body += f'''
<section class="section">
  <div class="wrap">{topic_grid(items)}</div>
</section>
{subscribe_band()}'''
    page("/insights/topics/", "Topics",
         "Insights from J.T. Barnes & Associates organized by topic: fund formation, private equity and private credit, capital markets, family office, EB-5, M&A, real estate, enforcement, and the practice of law.",
         body)

    for slug, label, practice in TOPICS:
        tagged = [i for i in items if slug in i["topics"]]
        series = [sr for sr in SERIES if slug in sr["topics"]]
        prac = next((p for p in PRACTICE if p["slug"] == practice), None)
        lede = prac["summary"] if prac else TOPIC_LEDE.get(slug, "")
        listing = feed(tagged) if tagged else '<p>New material on this topic is in preparation.</p>'
        series_html = ""
        if series:
            series_html = f'''<div class="section-head mt-sm"><span class="eyebrow">Series</span><h2>Related series</h2></div>
    <div class="grid-3">{"".join(series_card(sr, items) for sr in series)}</div>'''
        practice_link = (f'<p class="mt-sm"><a class="text-link" href="/practice/{prac["slug"]}/">About the {prac["nav"].replace("&amp;", "&amp;")} practice</a></p>'
                         if prac else "")
        body = page_hero([("Home", "/"), ("Insights", "/insights/"), ("Topics", "/insights/topics/"), (label, None)],
                         "Insights &middot; Topic", label, lede)
        body += insights_subnav("/insights/topics/")
        body += f'''
<section class="section">
  <div class="wrap">
    {listing}
    {practice_link}
  </div>
</section>'''
        if series_html:
            body += f'''
<section class="section section-stone">
  <div class="wrap">{series_html}</div>
</section>'''
        body += subscribe_band()
        plain = label.replace("&amp;", "&")
        page(f"/insights/topics/{slug}/", f"{plain} Insights",
             f"Articles, series, and CLE programs on {plain.lower() if slug != 'eb5' else 'EB-5 finance'} from J.T. Barnes & Associates.",
             body)


def related_insights(practice_slug):
    """Up to three recent items tagged with a practice area, for the bottom of its practice page."""
    tagged = [i for i in insight_items() if practice_slug in i["topics"]][:3]
    if not tagged:
        return ""
    cards = []
    for i in tagged:
        pdf = " (PDF)" if i["pdf"] else ""
        cards.append(f'''<a class="card" href="{i["url"]}">
  <span class="status status-live">{i["label"]} &middot; {i["date_label"]}</span>
  <h3>{i["title"]}</h3><p>{i["summary"]}</p><span class="text-link">{"View slides" if i["pdf"] else "Read"}{pdf}</span></a>''')
    label = TOPIC[practice_slug]["label"]
    return f'''<section class="section section-stone">
  <div class="wrap">
    <div class="section-head"><span class="eyebrow">Related insights</span><h2>Recent writing and programs</h2></div>
    <div class="grid-3">{"".join(cards)}</div>
    <p class="mt-sm"><a class="text-link" href="/insights/topics/{practice_slug}/">All {label} insights</a></p>
  </div>
</section>'''


def _filesize(n):
    return f"{n / 1048576:.1f} MB" if n >= 1048576 else f"{round(n / 1024)} KB"


def build_speaking():
    talks = [t for t in TALKS if t["published"]]
    years = []
    for t in talks:
        y = t["date"][:4]
        if not years or years[-1][0] != y:
            years.append((y, []))
        years[-1][1].append(t)

    def card(t):
        pdf = f'/assets/speaking/{t["slug"]}.pdf'
        w, h = t["thumb"]
        sub = f'<p>{t["subtitle"]}</p>' if t["subtitle"] else ""
        note = f'<p class="talk-note">{t["note"]}</p>' if t.get("note") else ""
        qr = (f'<a class="text-link" href="{t["quickref"]}">Quick reference <span class="muted">(PDF, 2 pages)</span></a>'
              if t["quickref"] else "")
        art = next((a for a in ARTICLES if a["slug"] == t.get("article")), None)
        if art:
            qr += f'<a class="text-link" href="/insights/articles/{art["slug"]}/">Read the article</a>'
        return f'''<article class="card talk" id="{t["slug"]}">
  <a class="talk-thumb" href="{pdf}" tabindex="-1" aria-hidden="true"><img src="/assets/speaking/{t["slug"]}.webp" width="{w}" height="{h}" alt="" loading="lazy" decoding="async"></a>
  <span class="status status-live">{t["date_label"]}</span>
  <h3>{t["title"]}</h3>
  {sub}{note}{topic_tags(t.get("topics", []))}
  <div class="talk-links">
    <a class="text-link" href="{pdf}">Slides <span class="muted">(PDF, {t["pages"]} slides, {_filesize(t["bytes"])})</span></a>
    {qr}
  </div>
</article>'''

    sections = "".join(f'''
<section class="section{" section-parchment" if i % 2 else ""}">
  <div class="wrap">
    <div class="section-head"><span class="eyebrow">Dallas Bar Association &middot; Securities Section</span><h2>{y} programs</h2></div>
    <div class="grid-3 talks">{"".join(card(t) for t in items)}</div>
  </div>
</section>''' for i, (y, items) in enumerate(years))

    body = page_hero([("Home", "/"), ("Insights", "/insights/"), ("Speaking &amp; CLE", None)],
                     "Insights &middot; Speaking &amp; CLE",
                     "Programs for the <em>Securities</em> Section.",
                     "Slides from Jason&rsquo;s programs for the Dallas Bar Association Securities Section, posted as presented. "
                     "Two-page quick references for each program are in preparation.")
    body += insights_subnav("/insights/speaking/")
    upcoming = [u for u in UPCOMING if u["date"] >= date.today().isoformat()]
    if upcoming:
        rows = "".join(f'''<li class="feed-item">
  <p class="feed-meta"><span class="feed-type">Upcoming</span><span>{fmt_date(u["date"])}</span></p>
  <h3>{u["title"]}</h3><p>{u.get("subtitle", "")}</p>
  <p class="small muted">{u.get("venue", "")}{" &middot; " + u["credit"] if u.get("credit") else ""}</p>
</li>''' for u in upcoming)
        body += f'''
<section class="section section-stone">
  <div class="wrap">
    <div class="section-head"><span class="eyebrow">Upcoming</span><h2>Upcoming programs</h2></div>
    <ul class="feed">{rows}</ul>
  </div>
</section>'''
    body += sections
    body += f'''
<section class="section section-tight">
  <div class="wrap split">
    <div>
      <span class="eyebrow">About these materials</span>
      <p class="small muted">Slides are posted as presented on the date shown and reflect the law and market practice at that time. Later developments are not reflected. Programs delivered before the founding of {SITE["firm"]} carry the name of Mr. Barnes&rsquo;s prior firm.</p>
      <p class="small muted">These materials are general information, not legal advice, and do not create an attorney-client relationship.</p>
    </div>
    <div>
      <span class="eyebrow">Programs and panels</span>
      <p>To request a program for your organization or invite Jason to join a panel, <a href="/contact/">get in touch</a>.</p>
    </div>
  </div>
</section>'''
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "Speaking & CLE",
          "url": SITE["url"] + "/insights/speaking/",
          "hasPart": [{"@type": "PresentationDigitalDocument", "name": t["title"].replace("&rsquo;", "\u2019").replace("&amp;", "&"),
                       "dateCreated": t["date"], "encodingFormat": "application/pdf",
                       "url": SITE["url"] + f'/assets/speaking/{t["slug"]}.pdf',
                       "author": {"@id": SITE["url"] + "/about/#jason"}} for t in talks]}
    page("/insights/speaking/", "Speaking & CLE",
         "Slides from Jason T. Barnes's Dallas Bar Association Securities Section programs on private offerings, M&A, private funds, private credit, EB-5, and enforcement.",
         body, jsonld=ld)


def build_newsletter():
    body = page_hero([("Home", "/"), ("Insights", "/insights/"), ("Newsletter", None)], "Insights &middot; Newsletter",
                     "<em>Signal</em>",
                     "Private capital, read clearly. Every other Tuesday, a five-minute read on what changed for fund sponsors, private lenders, EB-5 projects, family offices, and the businesses they back, and why it matters. Written from an active practice, not a content desk.")
    body += insights_subnav("/newsletter/")
    body += f'''
<section class="section">
  <div class="wrap split">
    <div>
      <span class="eyebrow">What each issue covers</span>
      <ul class="check-list">
        <li><b>The Signal:</b> a short column on the one pattern worth noticing</li>
        <li><b>Deal climate:</b> a three-sentence read on financing and deal conditions</li>
        <li><b>Five that matter:</b> private equity, private credit, EB-5, family office, and regulatory developments, weighted toward Texas and the middle market</li>
        <li><b>On the calendar:</b> deadlines and decisions in the weeks ahead</li>
        <li><b>From the practice:</b> new articles, programs, and quick references</li>
      </ul>
      <p class="small muted mt-sm">The newsletter is general information, not legal advice. Subscribing does not create an attorney-client relationship.</p>
    </div>
    <div class="card">
      <span class="eyebrow">Subscribe</span>
      <h2>Every other Tuesday.</h2>
      <p>No promotions. Unsubscribe at any time.</p>
      {newsletter_form()}
    </div>
  </div>
</section>'''
    page("/newsletter/", "Signal Newsletter",
         "Signal, from J.T. Barnes & Associates: private capital, read clearly. Every other Tuesday, what changed for fund sponsors, private lenders, EB-5 projects, and family offices, and why it matters.",
         body)


def build_lab():
    body = lab_hero([("Home", "/"), ("The Lab", None)], "The Lab",
                    "Practice tools, built in the <em>open</em>.",
                    "Generic productivity software assumes linear workflows. Transactional practice does not work that way. These are the tools I built to run my own practice, shared for anyone who wants to work the same way.")
    body += f'''
<section class="section">
  <div class="wrap">
    <div class="grid-2">
      <a class="card" href="/lab/timekeeper/"><span class="status status-live">In use</span><h3>Legal Timekeeper</h3><p>Matter-tagged time capture and reporting designed around how legal work is actually interrupted, resumed, and billed.</p><span class="text-link">Learn more</span></a>
      <a class="card" href="/lab/minder/"><span class="status status-dev">In development</span><h3>Legal Minder</h3><p>Natural-language scheduling that turns &ldquo;call the sponsor Tuesday at two&rdquo; into structured calendar entries for iOS and Outlook.</p><span class="text-link">Learn more</span></a>
      <a class="card" href="/lab/prompt-coach/"><span class="status status-live">In use</span><h3>Legal Prompt Coach</h3><p>A browser extension for Edge and Chrome that scores AI prompts as you type and builds them out into complete, lawyer-grade instructions for Claude, ChatGPT, Copilot, and more.</p><span class="text-link">Learn more</span></a>
      <a class="card" href="/newsletter/"><span class="status status-live">Daily</span><h3>Intelligence pipeline</h3><p>An automated feed that gathers, scores, and summarizes regulatory and market news, and feeds Signal, the firm newsletter.</p><span class="text-link">See the output</span></a>
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
         "Practice tools built by a securities lawyer: the Legal Timekeeper, Legal Minder, Legal Prompt Coach, and an automated regulatory intelligence pipeline.",
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
      <p>Say or type who the work was for, the matter, and what you did. The Timekeeper asks for anything missing, rounds the time to your billing increment, and keeps a running total for the day.</p>
      <ul class="check-list">
        <li>Speak an entry or type it, with clients and matters suggested from your past entries</li>
        <li>Time recorded in tenths of an hour or quarter hours, rounded the way you bill</li>
        <li>Browse any past day, then export a day, week, month, or custom period as CSV or text</li>
        <li>Optional Microsoft sign-in keeps entries in sync across your devices through your own OneDrive</li>
        <li>Works offline and installs to a phone home screen; no subscription required</li>
      </ul>
      <p class="mt-sm"><a class="btn btn-primary" href="{SITE["timekeeper_url"]}">Open the Timekeeper</a></p>
      <p class="small mt-sm">Entries stay on your device and, if you sign in, in a private folder of your own OneDrive. The firm does not receive or store them.</p>
    </div>
    <div class="mock" role="img" aria-label="Sample Legal Timekeeper screen showing four time entries totaling 8.5 hours">
      <div class="mock-bar"><span></span><span></span><span></span><em>Legal Timekeeper &middot; sample data</em></div>
      <div class="mock-body">
        <div class="mock-row"><div>Sample Fund I, LP: LPA markup<small>Fund Formation</small></div><b>2.6h</b></div>
        <div class="mock-row"><div>Sample Holdings: term sheet review<small>M&amp;A &amp; Structured Finance</small></div><b>1.9h</b></div>
        <div class="mock-row"><div>Sample Regional Center: offering update<small>EB-5 Finance</small></div><b>3.2h</b></div>
        <div class="mock-row"><div>Newsletter: Signal issue<small>Practice Development</small></div><b>0.8h</b></div>
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
      <p class="mt-sm"><a class="btn btn-primary" href="/newsletter/">Follow development</a></p>
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

    # Prompt Coach
    body = lab_hero([("Home", "/"), ("The Lab", "/lab/"), ("Legal Prompt Coach", None)], "The Lab &middot; In use",
                    "Legal Prompt <em>Coach</em>",
                    "A browser extension that coaches AI prompts for legal work as you write them, then builds them out into complete instructions before you press send.")
    body += f'''
<section class="section">
  <div class="wrap split">
    <div>
      <p>The quality of an AI answer depends on the quality of the request. Most prompts for legal work leave out the facts a lawyer would never leave out: whose side you represent, which document and sections are in scope, what standard applies, and what the output should look like. The Prompt Coach catches those gaps while you type.</p>
      <p>Draft in your own words in the AI tool you already use. A small score indicator sits beside the prompt box, rates the draft from 0 to 100, names the missing pieces, and with one click rebuilds the draft into a full prompt: the method for the task, your instructions, the missing parameters as fill-in fields, quality controls, and a place for your source material.</p>
      <ul class="check-list">
        <li>Works inside Claude, ChatGPT, Gemini, Microsoft Copilot, Microsoft 365 Copilot, Perplexity, and Meta AI</li>
        <li>Nine profiles and more than 100 task scenarios, from drafting and document review to regulatory filings, disputes, client letters, and practice operations</li>
        <li>Texas attorney advertising guardrails built into every marketing and business development prompt</li>
        <li>A side panel builder for longer prompts, plus right-click coaching for text on any page</li>
        <li>Scoring and building run locally in the browser; the optional Deep Coach sends a draft to Claude only when you click it, using your own API key</li>
      </ul>
      <p class="mt-sm"><a class="btn btn-primary" href="mailto:{SITE["email"]}?subject=Legal%20Prompt%20Coach">Request a copy</a></p>
      <p class="small mt-sm">For Microsoft Edge and Google Chrome. The Prompt Coach improves how a request is written; it does not review the answer, and every output still needs a lawyer&rsquo;s judgment. Do not enter confidential client information into an AI tool your engagement terms do not permit.</p>
    </div>
    <div class="mock" role="img" aria-label="Sample Legal Prompt Coach session scoring a short document review prompt at 58, listing three gaps, and rebuilding it to a score of 91">
      <div class="mock-bar"><span></span><span></span><span></span><em>Legal Prompt Coach &middot; sample data</em></div>
      <div class="mock-body">
        <div class="bubble user"><small>Your draft</small>Review the Sample Fund I LPA and flag missing LP protections.</div>
        <div class="bubble"><small>Coach &middot; Legal Review</small>
          <div class="mock-row"><div>Prompt score<small>Below the 70 threshold for legal work</small></div><b>58</b></div>
          <div class="event">
            <div><span>Gap</span>Whose side you represent</div>
            <div><span>Gap</span>Articles and sections in scope</div>
            <div><span>Gap</span>Output format for findings</div>
          </div>
        </div>
        <div class="bubble"><small>Build full prompt</small>Acting as counsel to [prospective limited partner], review Articles [__] of the Sample Fund I LPA against market LP protections. Report material gaps only, in a findings table with section, issue, risk, and proposed language. Do not speculate beyond the document.
          <div class="mock-total">Rebuilt score <b>91</b></div>
        </div>
      </div>
    </div>
  </div>
</section>'''
    page("/lab/prompt-coach/", "Legal Prompt Coach",
         "Legal Prompt Coach: a browser extension for Edge and Chrome that scores and builds AI prompts for legal drafting, review, research, and practice operations.",
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
    <h2>Legal Timekeeper</h2>
    <p>The Legal Timekeeper in the Lab stores time entries in your browser on your own device. If you choose to sign in with a Microsoft account, the app also saves your entries to a private app folder in your own OneDrive (inside the Apps folder) so they stay in sync across your devices. The app asks Microsoft only for permission to read and write that one folder. Sign-in and storage are handled by Microsoft under its own privacy terms. Your entries go directly between your browser and Microsoft; the firm does not receive, store, or have access to them. You can sign out at any time, and you can remove the app&rsquo;s access from your Microsoft account settings.</p>
    <p>Voice entry uses the speech recognition built into your browser. Depending on your browser, the audio may be processed by your browser&rsquo;s provider (for example, Google for Chrome, Microsoft for Edge, or Apple for Safari) under that provider&rsquo;s privacy terms. Typed entry involves no audio at all.</p>
    <h2>Newsletter</h2>
    <p>You can unsubscribe from Signal at any time using the link in any issue or by emailing <a href="mailto:{SITE["email"]}">{SITE["email"]}</a>.</p>
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
    build_insights_all()
    build_newsletter()
    build_lab()
    build_legal()
    build_404()
    build_support_files()
    print(f"Built {len(PAGES)} pages into {OUT}")
