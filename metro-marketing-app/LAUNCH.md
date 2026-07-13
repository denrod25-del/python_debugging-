# AdAtlas — from this repo to launched

Everything in this guide assumes the repo as it stands: the code is done and
tested; every step below is accounts, keys, and configuration. Budget roughly
**$30–60/month** in infrastructure and **one weekend** of setup.

---

## Step 1 — Name & domain (~$12/yr, 30 min)

"AdAtlas" is a working title — check the trademark/domain landscape before
printing shirts. Buy the domain at any registrar. You'll need it in Steps 3–5.

## Step 2 — Host the app (~$7–25/mo, 1–2 hrs)

Any host that runs a Python process works. Easiest paths, in order:

- **Render.com** — create a "Web Service" from the GitHub repo,
  root dir `metro-marketing-app`, build `pip install -r requirements.txt`,
  start `uvicorn server:app --host 0.0.0.0 --port $PORT`.
- **Railway / Fly.io** — same shape.

Pre-deploy, run locally and commit the artifacts the server needs:

```bash
python3 export_data.py                                # workbook -> data.json
python3 init_db.py                                    # -> adatlas.db
python3 build_seo_pages.py --base https://YOURDOMAIN  # -> seo/ with real canonicals
```

**SQLite caveat:** on most PaaS hosts the filesystem is ephemeral — attach a
persistent disk (Render: "Disk", $1/mo) or you'll lose signups on redeploy.
Swap to Postgres when you outgrow it; the SQL in `server.py` ports directly.

Point your domain's DNS at the host (they all walk you through it).

## Step 3 — Secrets (30 min)

Set these environment variables on the host:

| Var | What |
|---|---|
| `ADMIN_TOKEN` | A long random string — protects `/admin` |
| `STRIPE_SECRET_KEY` | From dashboard.stripe.com → Developers → API keys |
| `STRIPE_PRICE_ID` | Create a Product "AdAtlas Pro" @ $49/mo recurring; copy its price id |
| `STRIPE_WEBHOOK_SECRET` | Add endpoint `https://YOURDOMAIN/api/stripe-webhook` in Stripe → Webhooks; **then add signature verification** in `stripe_webhook()` (the TODO is marked) |
| `SMTP_HOST` (+ creds) | Any provider (Resend, Postmark, SES). Wire `send_reset_email()` — the function is the single integration point |

Test the money path once with Stripe's test card (4242 4242 4242 4242)
before flipping to live keys.

## Step 4 — Turn on the acquisition engine (1 hr)

1. Verify the domain in **Google Search Console**.
2. Submit `https://YOURDOMAIN/rates/sitemap.xml` (302 URLs).
3. Expect indexing over 2–8 weeks; long-tail queries ("billboard advertising
   tampa cost") are the target. Watch Search Console → Performance.
4. Add a free analytics tag (GA4 or Plausible) to `page_shell()` in
   `build_seo_pages.py` and `web/index.html` so you can see page → signup flow.

## Step 5 — First customers (the real work)

You already own the perfect beachhead: **Palm Beach County trades**.

1. Seed 10 free accounts with PBC contractors you know; watch what they click.
2. Post the free `/rates/` pages where owners hang out (trade Facebook groups,
   Nextdoor, r/smallbusiness — as answers, not ads).
3. First 25 Pro subscribers: founder-price them at $29/mo lifetime in exchange
   for a monthly 15-minute call. Those calls are your roadmap.
4. Charge from day one. Free users validate interest; only payers validate a
   business.

## Step 6 — Spin the flywheel (ongoing, this is the moat)

- **Quarterly re-verification:** run `verify_contacts.py` (Apify or
  Firecrawl - set the API key as an env var, never on the command line).
  It writes findings to a review queue at `/admin` - approve/reject each
  one; approving bumps `last_verified`. Nothing auto-overwrites contacts.
- **Capture quote data:** add a "What did they quote you?" prompt after a user
  views a contact card. Real quote benchmarks are the dataset nobody — not
  SRDS, not AdMall — has. That's what an acquirer eventually buys.
- **Log everything:** verification history and quote counts are diligence
  assets. A spreadsheet is fine; just never skip a quarter.

## Milestones that matter

| Milestone | Signal |
|---|---|
| First stranger pays $49 | The idea survives contact with reality |
| 100 Pro subs (~$5k MRR) | Quit-your-job territory; SEO flywheel usually visible |
| 1,000+ user-reported quotes | The proprietary dataset exists |
| Vendor claims arriving unprompted | The second side of the market found you |

Acquirers to keep warm once there's traction: Semrush, Yelp, Vendasta,
SalesFuel (AdMall), Clutch. The pitch: "the buyer-side local media
intelligence layer, with N quarters of verification history and the only
SMB quote-benchmark dataset in the US."
