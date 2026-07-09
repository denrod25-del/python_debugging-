# MetroStack — prototype

Subscription "one-stop shop" for local marketing intelligence: who to call in
each major US metro (billboard operators + rate bands, TV/radio ad desks,
newspapers, event sponsorships, chambers) plus a 1,116-tactic library rated by
cost, relevance, and time-to-impact.

Single-file web app fed by the master dataset in `../marketing-repository/`.

## Build

```bash
python3 export_data.py   # workbook -> data.json (43 metros, 559 contacts, 1,116 tactics)
python3 build_site.py    # template.html + data.json -> dist/index.html (self-contained)
```

Open `dist/index.html` in any browser. No server, no dependencies.

## What the prototype demonstrates

- **Markets** — pick any of 43 metros (Palm Beach County ★ is market #0), get the
  facts strip (population, DMA, OOH rate band, operator count) and the 13-category
  contact card. Free tier sees 5 categories; the rest blur behind a Pro lock.
- **Tactics** — live search + filters (category / cost / relevance / speed) over
  1,116 rated tactics; free tier capped at 25 results.
- **Quick Wins** — the High-relevance × $ × DIY list (free shows 10 of 224).
- **Playbook** — budget split models + seasonal calendar (Pro).
- **Pricing** — Free / Pro $49 / Team $149. The subscribe buttons simulate an
  account with localStorage; **no payments are wired** — this is a prototype.

## Files

```
export_data.py   reads the Excel master -> data.json
template.html    the app (HTML/CSS/JS, data injected at /*__DATA__*/)
build_site.py    inlines data.json -> dist/index.html
data.json        generated (306 KB)
dist/index.html  generated, deployable anywhere (Vercel/Netlify/S3)
```

## Productionizing checklist (beyond prototype)

- Real auth + Stripe subscriptions (the gate logic already models the tiers)
- Move data from embedded JSON to an API + database with per-record verification
  dates ("last verified" is the product's trust signal)
- Vendor-side claim/verify flow (second revenue side, Clutch-style)
- Quarterly re-verification pipeline + user-reported quote benchmarks (the moat)
