# Deploying the Python Debug Dojo to Vercel

A human walkthrough that mirrors what `deploy.sh` automates. Use this if you'd
rather run each phase yourself, or when a phase fails and you need to understand
what it does. `CLAUDE.md` is the canonical spec; this is the friendly version.

## 0. Prerequisites

Install and authenticate:

| Tool     | Check                | Fix                        |
|----------|----------------------|----------------------------|
| `git`    | `git --version`      | https://git-scm.com/       |
| `gh`     | `gh auth status`     | `gh auth login`            |
| `vercel` | `vercel whoami`      | `npm i -g vercel` + `vercel login` |
| `jq`     | `jq --version`       | https://jqlang.github.io/jq/ |

> Windows: run these from WSL or Git Bash. The scripts are POSIX bash — invoke
> them with `bash scripts/…` or `./deploy.sh`.

## 1. Configure

```bash
cp .env.example .env
```

Fill in at least:

- `GITHUB_USER` — the GitHub owner for the three repos.
- `ANTHROPIC_API_KEY` — your Anthropic key (kept server-side by the proxy).

Optional: `ALLOWED_ORIGIN` (auto = app URL), `VERCEL_SCOPE` (for teams).

## 2. Deploy

One command:

```bash
bash deploy.sh
```

…or phase by phase (each is idempotent — safe to re-run):

| Phase | Script                        | Does                                             |
|-------|-------------------------------|--------------------------------------------------|
| 00    | `scripts/00-preflight.sh`     | verify CLIs, auth, `.env`, folders               |
| 10    | `scripts/10-github.sh`        | create + push 3 GitHub repos                      |
| 20    | `scripts/20-vercel-deploy.sh` | first deploy → creates 3 Vercel projects          |
| 30    | `scripts/30-vercel-env.sh`    | set proxy env vars (`ANTHROPIC_API_KEY`, origin)  |
| 40    | `scripts/40-vercel-redeploy.sh` | redeploy proxy so env vars take effect          |
| 50    | `scripts/50-wire.sh`          | patch landing with app URL, push, redeploy landing |
| 99    | `scripts/99-status.sh`        | print URLs + the one manual step                  |

Deployed URLs are written to `.deploy-state` (git-ignored) so later phases read
them without arguments.

## 3. The one manual step

The app stores its AI endpoint in the browser, not in server config. From the
output of phase 99:

1. Open the **app URL**.
2. Go to **Stats → AI endpoint**.
3. Paste **`<proxy URL>/api/ai`**.
4. **Save**, then **Test connection** — you should see a friendly "pong".

## Troubleshooting

- **Vercel prompts for a team** — set `VERCEL_SCOPE` in `.env`.
- **`gh repo create` says the repo exists** — fine; phase 10 pushes to it.
- **A deploy fails mid-way** — re-run just that phase; earlier state persists in
  `.deploy-state`.
- **`.deploy-state` looks wrong** — delete it and re-run from phase 20.
- **AI hint / Test connection fails** — confirm `ANTHROPIC_API_KEY` is set on the
  proxy (`cd pydojo-proxy && vercel env ls`) and that `ALLOWED_ORIGIN` matches the
  app's origin (or is blank/`*` while testing).

## Custom domains

Not automated. Add them in the Vercel dashboard per project after deploy, then
(optionally) set `ALLOWED_ORIGIN` to your custom app domain and re-run phases
30 → 40 so the proxy's CORS allow-list matches.
