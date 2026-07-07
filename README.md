# Python Debug Dojo

Learn to debug real Python — one focused bug at a time. Read a broken program,
run it in your browser, fix it, and check your work. Stuck? Ask for an AI hint.

This monorepo deploys as **three separate Vercel projects**:

| Folder            | What it is                                   | Vercel project   |
|-------------------|----------------------------------------------|------------------|
| `pydojo-landing/` | Marketing landing page (static HTML)         | `pydojo-landing` |
| `pydojo-app/`     | The dojo app (single-file static HTML)       | `pydojo-app`     |
| `pydojo-proxy/`   | AI proxy — Vercel Edge Function at `/api/ai` | `pydojo-proxy`   |

The landing page links to the app; the app calls the proxy for AI hints so your
Anthropic API key never reaches the browser.

## Quick start

```bash
cp .env.example .env       # then fill in GITHUB_USER and ANTHROPIC_API_KEY
bash deploy.sh             # runs every phase in order (idempotent)
```

You need `git`, `gh` (authenticated), `vercel` (authenticated), and `jq`
installed. See **[DEPLOY-VERCEL.md](DEPLOY-VERCEL.md)** for the full walkthrough
and **[CLAUDE.md](CLAUDE.md)** for the deploy kit's design notes.

## The one manual step

The app's AI endpoint lives in your browser, not in server config. After the
deploy, `scripts/99-status.sh` prints exactly what to paste:

> Open the **app URL → Stats → AI endpoint**, paste **`<proxy URL>/api/ai`**,
> Save, then **Test connection**.

## Layout

```text
deploy.sh              orchestrator: runs all phases in order
scripts/               phased deploy scripts (00 → 99); see CLAUDE.md
pydojo-landing/        landing page      ← DEPLOYED
pydojo-app/            dojo app          ← DEPLOYED
pydojo-proxy/          AI proxy          ← DEPLOYED
alternatives/          non-Vercel proxy options ← reference only, NOT deployed
```

## Develop locally

- **App / landing:** open the `index.html` file directly in a browser, or serve
  the folder (`python3 -m http.server`). The app fetches Pyodide from a CDN on
  first run.
- **Proxy:** `cd pydojo-proxy && vercel dev` with `ANTHROPIC_API_KEY` in your
  environment. See [`pydojo-proxy/README.md`](pydojo-proxy/README.md).
