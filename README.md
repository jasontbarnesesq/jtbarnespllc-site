# jtbarnespllc.com

Website of **J.T. Barnes & Associates, PLLC**: a client-facing law firm site (the Firm) with a gateway to insights, the newsletter, and practice tools (the Lab).

- Hosting: GitHub Pages, published from the `docs/` folder of the `main` branch
- Domain: `jtbarnespllc.com` (set by `docs/CNAME`)
- No frameworks, no build service, no cookies, no third-party requests. Fonts are self-hosted.
- Design: Barnes Brand v1 (November 2026). Libre Franklin, Ink / White / Rust, the closing corner. See `brand/barnes-brand-web.json`.

## Repository layout

```
build/build.py            Site generator: firm data, page copy, shared header and footer
brand/                    Barnes Brand web tokens (barnes-brand-web.json), Timekeeper logo
docs/                     Published website (GitHub Pages serves this folder)
  index.html              Home (client landing)
  practice/               Practice overview + six practice-area pages
  approach/  about/  contact/
  insights/  newsletter/  lab/ (timekeeper/, minder/)   The Lab zone
  legal/ (privacy/)       Disclaimer, attorney advertising notice, privacy
  404.html  sitemap.xml  robots.txt  CNAME  .nojekyll
  assets/css/site.css     Design tokens and all styles
  assets/js/site.js       Menu, forms, and the CONFIG block
  assets/fonts/            Libre Franklin (woff2) and its license
  assets/img/brand/        Logo and icon SVGs (supplied artwork; never retype the logo)
```

## Everyday edits

All page HTML is generated. Edit `build/build.py`, then run:

```bash
python3 build/build.py
```

Commit both `build/build.py` and the regenerated `docs/` files.

| To change | Edit |
|---|---|
| Phone, email, LinkedIn, Timekeeper URL, booking link | `SITE` in `build/build.py` |
| Headline figures and the results note | `FACTS` and `RESULTS_NOTE` |
| Practice-area pages | `PRACTICE` (one dict per page) |
| Publish an article | Add a dict to `ARTICLES` (slug, title, date, category, summary, body) |
| Contact form or newsletter provider | `CONFIG` at the top of `docs/assets/js/site.js` |
| Colors and type | Tokens at the top of `docs/assets/css/site.css` (keep `brand/barnes-brand-web.json` in step) |
| The corner after each page headline | `closing()` in `build/build.py` |

### Forms

The site has no server, so by default the contact and newsletter forms open the visitor's email app with a pre-filled message to `jtbarnes@jtbarnespllc.com`. To collect submissions directly instead, create a form with a provider that accepts a standard POST (Formspree, Jotform, Basin) or a newsletter service (Buttondown, Mailchimp), paste its endpoint into `contactEndpoint` or `newsletterEndpoint` in `site.js`, and add that provider's domain to the `connect-src` and `form-action` entries of the Content Security Policy in `head()` within `build/build.py`.

### Online booking

Set `SITE["scheduling_url"]` to a Calendly or Microsoft Bookings link and rebuild. Every "Schedule a Consultation" button will then open it.

## Building for a different domain

The default build targets jtbarnespllc.com. The interim copy running on jasontbarnes.com (repository `jasontbarnesesq.github.io`, since October 17, 2026) was built with:

```bash
python3 build/build.py --domain jasontbarnes.com \
  --out ../jasontbarnesesq.github.io --legacy-stubs --no-nojekyll
cp -r docs/assets docs/favicon.ico ../jasontbarnesesq.github.io/
```

`--legacy-stubs` adds forwarding pages at the old jasontbarnes.com addresses; `--no-nojekyll` keeps GitHub's normal processing for the Timekeeper and start-page folders in that repository. Never overwrite its `CNAME`, `MyLegalTimekeeper/`, `startpage/`, `MyLegalWidget_A1`, or `widgets`.

## Preview locally

```bash
cd docs && python3 -m http.server 8000
# open http://localhost:8000
```

## Launch

Follow `JTB_PLLC_Website_Launch_Workbook.xlsx` (Launch Plan tab), which covers DNS, GitHub Pages, the jasontbarnes.com redirect, compliance review, and QA.

Contact: Jason T. Barnes, jtbarnes@jtbarnespllc.com, +1.469.304.6366
