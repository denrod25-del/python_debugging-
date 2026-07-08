# pydojo-proxy

AI proxy for the **Python Debug Dojo**, deployed as a single [Vercel Edge
Function](https://vercel.com/docs/functions/edge-functions) at `/api/ai`.

Its only job is to keep your `ANTHROPIC_API_KEY` server-side. The browser app
posts a prompt here; this function forwards it to the Anthropic Messages API and
returns the assistant text. The key never reaches the client.

## Endpoint

```
POST /api/ai
Content-Type: application/json
```

Request body — either shape works:

```jsonc
// simple
{ "prompt": "Why does this raise IndexError?", "system": "You are a Python tutor." }

// full control
{ "messages": [{ "role": "user", "content": "…" }], "max_tokens": 512 }
```

Response:

```json
{ "text": "…", "model": "…", "usage": { "input_tokens": 12, "output_tokens": 34 } }
```

## Environment variables

| Name                | Required | Purpose                                             |
|---------------------|----------|-----------------------------------------------------|
| `ANTHROPIC_API_KEY` | yes      | Anthropic API key                                   |
| `ALLOWED_ORIGIN`    | no       | CORS allow-list; blank ⇒ `*`                        |
| `ANTHROPIC_MODEL`   | no       | Model id; blank ⇒ a current default in `api/ai.js`  |

These are set automatically by `scripts/30-vercel-env.sh` in the deploy kit.

## Local test

```bash
npm i -g vercel
vercel dev
curl -s localhost:3000/api/ai \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Explain a Python IndexError in one sentence."}'
```

(Needs `ANTHROPIC_API_KEY` in your environment or a local `.env`.)
