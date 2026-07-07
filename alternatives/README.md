# alternatives/ — reference only

**Do not deploy anything in this folder with the Python Debug Dojo deploy kit.**
The deployable proxy is `pydojo-proxy/` (a Vercel Edge Function). These are
drop-in replacements for hosts other than Vercel, kept here for reference.

Each exposes the **same contract** as `pydojo-proxy`:

```text
POST /api/ai   (or /  for the worker)
{ "prompt": "…", "system": "…" }   or   { "messages": [...] }
→ { "text": "…", "model": "…", "usage": {…} }
```

So the app's **Stats → AI endpoint** can point at any of them interchangeably.

| Option                     | Host                | Use when…                                  |
|----------------------------|---------------------|--------------------------------------------|
| `proxy-cloudflare-worker/` | Cloudflare Workers  | you already live in the Cloudflare ecosystem |
| `proxy-express-docker/`    | any Docker host     | you want to self-host / run on your own box  |

Both read the same env vars: `ANTHROPIC_API_KEY` (required), `ALLOWED_ORIGIN`
(optional CORS allow-list), `ANTHROPIC_MODEL` (optional).
