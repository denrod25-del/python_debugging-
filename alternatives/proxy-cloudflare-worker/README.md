# proxy-cloudflare-worker (reference only)

The Python Debug Dojo AI proxy as a Cloudflare Worker. Same contract as
`pydojo-proxy`, so the app's **Stats → AI endpoint** can point straight at the
worker's URL.

## Deploy

```bash
npm i -g wrangler
wrangler login
wrangler secret put ANTHROPIC_API_KEY      # paste your key when prompted
# optional: edit wrangler.toml [vars] to set ALLOWED_ORIGIN / ANTHROPIC_MODEL
wrangler deploy
```

The worker responds to `POST /` (there's no `/api/ai` path routing needed).
Set the app's AI endpoint to the worker URL, e.g.
`https://pydojo-proxy.<your-subdomain>.workers.dev`.

## Test

```bash
curl -s https://pydojo-proxy.<your-subdomain>.workers.dev \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Reply with the single word: pong"}'
```
