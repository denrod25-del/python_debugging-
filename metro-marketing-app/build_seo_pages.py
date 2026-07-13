#!/usr/bin/env python3
"""Generate the programmatic SEO layer: one landing page per metro x channel.

The Media Ant playbook: publish free, genuinely useful rate/contact pages that
rank for long-tail searches ("billboard advertising tampa"), tease the data,
and convert to the app. Reads data.json; writes seo/ (301 pages + index +
sitemap.xml + robots.txt). Server mounts this at /rates.

    python3 build_seo_pages.py [--base https://adatlas.example]
"""
from __future__ import annotations

import argparse
import json
import os
import re
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "seo")

# channel key -> (slug prefix, page H1 template, category in contacts, blurb)
CHANNELS = {
    "billboard": ("billboard-advertising", "Billboard & Outdoor Advertising in {city}",
                  "Outdoor / OOH",
                  "Static and digital billboards, posters, wallscapes and transit media."),
    "tv": ("tv-advertising", "TV & Cable Advertising in {city}",
           "Broadcast",
           "Big-4 network affiliates plus zoned cable - local TV is more affordable than most owners think."),
    "radio": ("radio-advertising", "Radio Advertising in {city}",
              None,  # built from metro fields, not the contacts table
              "The major radio ownership groups and Spanish-language stations serving the market."),
    "newspaper": ("newspaper-advertising", "Newspaper & Print Advertising in {city}",
                  "Print",
                  "The dominant daily, the business journal, and where print still earns its keep."),
    "events": ("event-sponsorship", "Event Sponsorships in {city}",
               "Experiential & Event",
               "Fairs, festivals, home shows and pro-sports sponsorship properties."),
    "pr": ("local-pr", "Local PR & Media Coverage in {city}",
           "PR & Earned",
           "The newsrooms and pitch targets that put a local business in the news for free."),
    "partnerships": ("business-partnerships", "Business Partnerships & Networking in {city}",
                     "Partnership & Channel",
                     "Chambers, referral networks and the partnership channels that compound."),
}

CSS = """
:root{--ground:#F1F4F3;--card:#fff;--ink:#16292B;--muted:#5C6F6D;--brand:#1E5E58;
--brand-soft:#E1ECEA;--accent:#D9631E;--accent-soft:#F8E8DC;--line:#D7E0DE;
--display:Futura,'Avenir Next','Century Gothic','Trebuchet MS',sans-serif;
--serif:Charter,'Bitstream Charter',Georgia,serif;
--ui:system-ui,-apple-system,'Segoe UI',Roboto,sans-serif}
@media (prefers-color-scheme:dark){:root{--ground:#0E1B1C;--card:#152627;--ink:#E5ECEA;
--muted:#94A8A5;--brand:#53ADA4;--brand-soft:#1C3B39;--accent:#E8834A;--accent-soft:#3A2416;--line:#274241}}
*{box-sizing:border-box}body{margin:0;background:var(--ground);color:var(--ink);
font-family:var(--ui);line-height:1.55}
header{display:flex;align-items:center;gap:.5rem;padding:.7rem 1.2rem;border-bottom:1px solid var(--line)}
.wordmark{font-family:var(--display);font-weight:700;letter-spacing:.14em;text-transform:uppercase;text-decoration:none;color:var(--ink)}
.wordmark span{color:var(--accent)}
header a.cta{margin-left:auto;background:var(--brand);color:#fff;text-decoration:none;
padding:.5rem 1rem;border-radius:8px;font-weight:700;font-size:.88rem}
main{max-width:820px;margin:0 auto;padding:1.4rem 1.2rem 4rem}
.crumbs{font-size:.8rem;color:var(--muted)}.crumbs a{color:var(--brand)}
h1{font-family:var(--display);text-transform:uppercase;letter-spacing:.02em;
font-size:clamp(1.5rem,4vw,2.2rem);line-height:1.1;margin:.6rem 0;text-wrap:balance}
.lede{font-family:var(--serif);color:var(--muted);font-size:1.05rem;margin:0 0 1.4rem}
.facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:.6rem;margin:1rem 0 1.4rem}
.fact{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:.65rem .8rem}
.fact b{display:block;font-variant-numeric:tabular-nums}
.fact span{font-size:.7rem;color:var(--muted);letter-spacing:.07em;text-transform:uppercase}
.panel{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:1.1rem 1.2rem;margin:1rem 0}
.panel h2{font-family:var(--display);font-size:1.02rem;letter-spacing:.04em;text-transform:uppercase;margin:0 0 .5rem}
.gate{border:1.5px dashed var(--accent);background:var(--accent-soft);text-align:center}
.gate a{display:inline-block;background:var(--accent);color:#fff;text-decoration:none;
padding:.6rem 1.3rem;border-radius:8px;font-weight:700;margin-top:.5rem}
.faq h3{font-size:.98rem;margin:1rem 0 .2rem}.faq p{margin:.2rem 0;color:var(--muted)}
.links{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:.4rem;margin:.6rem 0}
.links a{font-size:.86rem;color:var(--brand)}
footer{border-top:1px dashed var(--line);margin-top:2.5rem;padding:1.2rem;text-align:center;color:var(--muted);font-size:.78rem}
"""


def slugify(s):
    s = s.replace("★", "").strip()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")


def esc(s):
    return str(s or "").replace("&", "&amp;").replace("<", "&lt;")


def page_shell(title, desc, canonical, body, jsonld=""):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canonical}">
<style>{CSS}</style>
{jsonld}
</head>
<body>
<header>
  <a class="wordmark" href="index.html"><span>&#9670;</span>AdAtlas</a>
  <a class="cta" href="/">Open the app &rarr;</a>
</header>
<main>
{body}
</main>
<footer>Rates are market reference bands compiled from public sources and operator data;
always confirm a live quote. &copy; AdAtlas.</footer>
</body>
</html>"""


def faq_jsonld(qas):
    items = [{"@type": "Question", "name": q,
              "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qas]
    return ('<script type="application/ld+json">'
            + json.dumps({"@context": "https://schema.org", "@type": "FAQPage",
                          "mainEntity": items}) + "</script>")


def build_channel_page(base, key, metro, contacts_by_cat, all_metros):
    slug_prefix, h1_t, cat, blurb = CHANNELS[key]
    city = metro["metro"].replace("★", "").strip()
    st = metro["state"]
    cityst = f"{city}, {st}" if st else city
    slug = f"{slug_prefix}-{slugify(city)}-{slugify(st) if st else 'us'}.html"
    h1 = h1_t.format(city=cityst)
    title = f"{h1} — Rates, Contacts & Operators (2026) | AdAtlas"

    # channel-specific content
    if key == "radio":
        teaser = f"Major radio groups: {metro['radio']}. Spanish-language: {metro['spanish']}."
        rate_line = "Local radio flights typically run $1,000–$8,000+/month depending on daypart and station reach; sponsorships (traffic/weather) price higher for frequency."
    else:
        row = contacts_by_cat.get(cat, {})
        teaser = row.get("contacts", "")
        if key == "billboard":
            rate_line = (f"Standard billboards in {city} run about {metro['oohRate']} per month "
                         f"per face; premium corridors and digital run higher. "
                         f"{metro['oohOps']} operators/brokers serve the market.")
        elif key == "tv":
            rate_line = ("Local TV is quote-based, but zoned cable (Spectrum Reach / Comcast "
                         "Effectv) lets small businesses buy specific neighborhoods at a "
                         "fraction of broadcast cost.")
        elif key == "newspaper":
            rate_line = (f"Print in {city} centers on {metro['paper']} and {metro['bizj']}; "
                         "rates are quote-based by size and section.")
        elif key == "events":
            rate_line = ("Sponsorships range from a few hundred dollars (youth sports, "
                         "community events) to five figures for marquee properties.")
        elif key == "pr":
            rate_line = "Earned coverage is free - the cost is a good story and a well-aimed pitch."
        else:
            rate_line = ("Most partnership channels cost time, not money - chamber dues are "
                         "typically a few hundred dollars a year.")

    # teaser: show first ~140 chars, gate the rest
    teaser_short = (teaser[:140] + "…") if teaser and len(teaser) > 140 else (teaser or "")

    qas = [
        (f"How much does {h1.split(' in ')[0].lower()} cost in {city}?", rate_line),
        (f"Who sells {h1.split(' in ')[0].lower()} in {city}?",
         f"{teaser_short} The full who-to-call card (all providers, verified dates) is in the AdAtlas app."),
        (f"What's the fastest way to start marketing in {city}?",
         "Foundation first: Google Business Profile + Local Services Ads + a review engine, "
         "then city landing pages, then paid local media like this channel."),
    ]

    # internal links: other channels same metro + same channel nearby metros
    other_ch = [f'<a href="{CHANNELS[k][0]}-{slugify(city)}-{slugify(st) if st else "us"}.html">'
                f'{esc(CHANNELS[k][1].format(city=city))}</a>'
                for k in CHANNELS if k != key]
    idx = [m["metro"] for m in all_metros].index(metro["metro"])
    nearby = [m for m in all_metros[max(0, idx - 3): idx + 4] if m["metro"] != metro["metro"]][:6]
    same_ch = [f'<a href="{slug_prefix}-{slugify(m["metro"])}-{slugify(m["state"]) if m["state"] else "us"}.html">'
               f'{esc(CHANNELS[key][1].format(city=m["metro"].replace("★","").strip()))}</a>'
               for m in nearby]

    body = f"""
<p class="crumbs"><a href="index.html">All markets</a> &rsaquo; {esc(cityst)} &rsaquo; {esc(h1.split(' in ')[0])}</p>
<h1>{esc(h1)}</h1>
<p class="lede">{esc(blurb)}</p>
<div class="facts">
  <div class="fact"><b>{esc(metro['pop'])}</b><span>Metro population</span></div>
  <div class="fact"><b>#{esc(metro['dma'])}</b><span>Nielsen DMA (approx)</span></div>
  <div class="fact"><b>{esc(metro['oohRate'])}</b><span>Billboard band /mo</span></div>
  <div class="fact"><b>{esc(metro['paper']).split('/')[0]}</b><span>Major newspaper</span></div>
</div>
<div class="panel">
  <h2>What it costs</h2>
  <p>{esc(rate_line)}</p>
</div>
<div class="panel">
  <h2>Who to contact</h2>
  <p>{esc(teaser_short)}</p>
</div>
<div class="panel gate">
  <h2>The full contact card is free to unlock</h2>
  <p>Every provider for {esc(cityst)} across 13 channel categories - with verified dates,
  rate bands, and a 1,100-tactic playbook.</p>
  <a href="/">Create a free AdAtlas account &rarr;</a>
  <p style="font-size:.85rem;margin:.7rem 0 0"><a style="background:none;color:var(--brand);padding:0"
     href="/plan?metro={quote(metro['metro'])}&amp;utm_source=rates">
     or build a free 1-page marketing plan for {esc(city)} &rarr;</a></p>
</div>
<div class="panel faq">
  <h2>Frequently asked</h2>
  {''.join(f'<h3>{esc(q)}</h3><p>{esc(a)}</p>' for q, a in qas)}
</div>
<div class="panel">
  <h2>More in {esc(city)}</h2>
  <div class="links">{''.join(other_ch)}</div>
  <h2>Same channel, nearby markets</h2>
  <div class="links">{''.join(same_ch)}</div>
</div>"""
    html = page_shell(title, f"{rate_line} Contacts, rates and operators for {cityst}.",
                      f"{base}/rates/{slug}", body, faq_jsonld(qas))
    return slug, html


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="https://adatlas.example")
    args = ap.parse_args()
    base = args.base.rstrip("/")

    with open(os.path.join(HERE, "data.json")) as fh:
        data = json.load(fh)
    os.makedirs(OUT, exist_ok=True)

    metros = data["metros"]
    contacts = data["contacts"]
    by_metro = {}
    for c in contacts:
        by_metro.setdefault(c["metro"], {})[c["category"]] = c

    slugs = []
    for m in metros:
        cbc = by_metro.get(m["metro"], {})
        for key in CHANNELS:
            slug, html = build_channel_page(base, key, m, cbc, metros)
            with open(os.path.join(OUT, slug), "w") as fh:
                fh.write(html)
            slugs.append(slug)

    # index page
    groups = []
    for m in metros:
        city = m["metro"].replace("★", "").strip()
        st = m["state"]
        links = "".join(
            f'<a href="{CHANNELS[k][0]}-{slugify(city)}-{slugify(st) if st else "us"}.html">'
            f'{esc(CHANNELS[k][1].format(city="").replace(" in ",""))}</a>'
            for k in CHANNELS)
        home = " ★ home market" if m["metro"].startswith("Palm Beach") else ""
        groups.append(f'<div class="panel"><h2>{esc(city)}{", "+esc(st) if st else ""}'
                      f'{home}</h2><div class="links">{links}</div></div>')
    idx_body = f"""
<h1>Local Advertising Rates &amp; Contacts by Metro</h1>
<p class="lede">Free reference pages for {len(metros)} US markets x {len(CHANNELS)} channels:
what it costs, who sells it, and how to start. Built from the AdAtlas dataset.</p>
{''.join(groups)}"""
    with open(os.path.join(OUT, "index.html"), "w") as fh:
        fh.write(page_shell("Local Advertising Rates & Contacts by Metro | AdAtlas",
                            f"Advertising rates and media contacts for {len(metros)} US metros "
                            f"across billboards, TV, radio, print, events, PR and partnerships.",
                            f"{base}/rates/", idx_body))

    # sitemap + robots
    urls = [f"{base}/rates/"] + [f"{base}/rates/{s}" for s in slugs]
    sm = ('<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + "\n".join(f"  <url><loc>{u}</loc></url>" for u in urls)
          + "\n</urlset>\n")
    with open(os.path.join(OUT, "sitemap.xml"), "w") as fh:
        fh.write(sm)
    with open(os.path.join(OUT, "robots.txt"), "w") as fh:
        fh.write(f"User-agent: *\nAllow: /\nSitemap: {base}/rates/sitemap.xml\n")

    print(f"seo/: {len(slugs)} channel pages + index + sitemap ({len(urls)} URLs)")


if __name__ == "__main__":
    main()
