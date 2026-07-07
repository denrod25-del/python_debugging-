# proxy-express-docker (reference only)

The Python Debug Dojo AI proxy as a small Express server, containerised. Same
contract as `pydojo-proxy`, exposed at `POST /api/ai`. Self-host it anywhere
Docker runs.

## Run with Node

```bash
npm install
ANTHROPIC_API_KEY=sk-ant-... npm start
# → listening on :8080, endpoint at http://localhost:8080/api/ai
```

## Run with Docker

```bash
docker build -t pydojo-proxy .
docker run --rm -p 8080:8080 \
  -e ANTHROPIC_API_KEY=sk-ant-... \
  -e ALLOWED_ORIGIN=https://pydojo-app.vercel.app \
  pydojo-proxy
```

## Test

```bash
curl -s localhost:8080/api/ai \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Reply with the single word: pong"}'
```

Point the app's **Stats → AI endpoint** at `http(s)://<host>:8080/api/ai`.

> Requires Node 18+ (uses the built-in global `fetch`).
