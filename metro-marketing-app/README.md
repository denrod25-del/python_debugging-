# MetroStack — prototype + production-shaped backend

Subscription "one-stop shop" for local marketing intelligence: who to call in
each major US metro (billboard operators + rate bands, TV/radio ad desks,
newspapers, event sponsorships, chambers) plus a 1,116-tactic library rated by
cost, relevance, and time-to-impact. Fed by the master dataset in
`../marketing-repository/`.

Two ways to run it:

## A. Full app (API server — auth, real gating, Stripe-ready)

```bash
pip install -r requirements.txt
python3 export_data.py   # workbook -> data.json
python3 init_db.py       # data.json -> metrostack.db (SQLite, last_verified on every row)
python3 server.py        # http://localhost:8000
```

What the backend does (all verified end-to-end):

- **Auth** — signup/login/logout, PBKDF2-hashed passwords, httponly session cookies
- **Server-side gating** (not client tricks): free accounts get 5 of 13 categories
  per market, 25 tactics per query, 10 quick wins; the API simply doesn't send
  locked data. Playbook returns 402 for free users.
- **Subscription** — `POST /api/subscribe`. With `STRIPE_SECRET_KEY` +
  `STRIPE_PRICE_ID` set it creates a real Stripe Checkout session and
  `/api/stripe-webhook` flips the plan on completion; without keys it runs in
  mock mode for demos.
- **Trust signal** — every contact row carries `last_verified` / `verified_by`,
  surfaced in the UI as "✓ verified 2026-07-08".
- **Vendor side** — `POST /api/claim` files a listing claim (the second revenue
  side); `GET /api/claims` lists them.

## B. Static demo (no server)

```bash
python3 build_site.py    # template.html + data.json -> dist/index.html
```

Open `dist/index.html` anywhere — same UI with a localStorage-mock subscription.

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
init_db.py       data.json -> metrostack.db (adds last_verified, users, claims)
server.py        FastAPI backend: auth, gated data API, subscribe, claims
web/index.html   API-driven frontend (auth modal, claim modal, verified chips)
template.html    static-demo variant (data injected at /*__DATA__*/)
build_site.py    inlines data.json -> dist/index.html
data.json        generated (306 KB)
dist/index.html  generated static demo, deployable anywhere
```

## Still to do before charging real money

- Set `STRIPE_SECRET_KEY` / `STRIPE_PRICE_ID` and verify the webhook signature
  (`STRIPE_WEBHOOK_SECRET`) — the endpoints are wired, keys are not
- Deploy: any host that runs uvicorn (Fly/Render/Railway); swap SQLite for
  Postgres when concurrent writes matter
- Password reset + email verification (needs an email provider)
- Quarterly re-verification pipeline + user-reported quote benchmarks (the moat)
- Claim review admin (approve -> verified badge on the listing)
