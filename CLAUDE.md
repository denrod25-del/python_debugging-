# Python Debug Dojo — deploy kit

You (Claude Code) are being asked to deploy three related Vercel projects that make up the Python Debug Dojo. This file is your source of truth. Read it end-to-end before running anything.

## What you're deploying

Three separate Vercel projects, each from its own subfolder in this monorepo:

| Folder            | Purpose                                             | Vercel project name |
|-------------------|-----------------------------------------------------|---------------------|
| `pydojo-landing/` | Marketing landing page (static HTML)                | `pydojo-landing`    |
| `pydojo-app/`     | The dojo app (single-file static HTML)              | `pydojo-app`        |
| `pydojo-proxy/`   | AI proxy — Vercel Edge Function at `/api/ai`        | `pydojo-proxy`      |

The three are wired: landing links to app; app calls proxy for AI features. The wiring step (`scripts/50-wire.sh`) handles it.

## Prerequisites

Verify these CLIs are installed and authenticated before you start. If any are missing, **stop and tell the user** which to install — do not attempt to install them yourself.

- `git` — any recent version
- `gh` — GitHub CLI, authenticated (`gh auth status` must succeed)
- `vercel` — Vercel CLI, authenticated (`vercel whoami` must succeed)
- `jq` — for parsing JSON output

The user runs on Windows PowerShell with WSL/Git Bash; scripts are POSIX bash and should be invoked via `bash scripts/…` or `./deploy.sh` from a bash-capable shell.

## Configuration

Configuration lives in `.env` at the repo root. If it doesn't exist:

1. `cp .env.example .env`
2. Ask the user to fill in the required values, or ask them explicitly for each. Never guess `ANTHROPIC_API_KEY`.

Required:
- `GITHUB_USER` — GitHub owner for the repos (e.g. `denrod25-del`)
- `ANTHROPIC_API_KEY` — Anthropic API key. Sensitive.

Optional (leave blank for auto):
- `ALLOWED_ORIGIN` — restrict proxy to a specific origin. If blank, the wire step will set it to the app's deployed URL automatically.
- `VERCEL_SCOPE` — pass to `vercel --scope` for teams. Blank = personal account.
- `APP_REPO_NAME`, `LANDING_REPO_NAME`, `PROXY_REPO_NAME` — override the default GitHub repo names.

Load config with `set -a; . .env; set +a` — every script does this automatically via `scripts/lib.sh`.

## Deploy in one command

```bash
bash deploy.sh
```

This runs each phase in order. Each phase is idempotent — safe to re-run if a step fails.

## Deploy step-by-step

If you'd rather run phases individually or a phase fails:

```bash
bash scripts/00-preflight.sh       # verify CLIs, config, subfolders
bash scripts/10-github.sh          # create/push 3 GitHub repos
bash scripts/20-vercel-deploy.sh   # first-time deploy to Vercel (creates 3 projects)
bash scripts/30-vercel-env.sh      # set proxy env vars (ANTHROPIC_API_KEY etc.)
bash scripts/40-vercel-redeploy.sh # redeploy proxy so env vars take effect
bash scripts/50-wire.sh            # update landing HTML with deployed app URL, push, redeploy landing
bash scripts/99-status.sh          # print all URLs + user's remaining manual step
```

Each script writes deployed URLs to `.deploy-state` (git-ignored), so later scripts read from there and don't need arguments.

## Handling failures

- If a Vercel CLI command prompts interactively (team selection, project creation confirmation), respond with the appropriate answer. `VERCEL_SCOPE` in `.env` avoids team prompts.
- If `gh repo create` fails because the repo exists, that's fine — the script handles this and pushes to the existing repo.
- If a Vercel deploy fails mid-flight, re-run just that phase. State from previous successful phases persists in `.deploy-state`.
- If `.deploy-state` gets corrupted, delete it and re-run from `scripts/20-vercel-deploy.sh` — deploys will re-derive URLs.

If you hit an error you can't resolve, print the exact error message and stop. Ask the user before making assumptions about how to fix it.

## The one manual step

`scripts/50-wire.sh` cannot automate one thing: setting the AI endpoint inside the deployed dojo app. It lives in the user's browser (IndexedDB / window.storage), not server config.

`scripts/99-status.sh` prints exactly what the user needs to paste:

> Open **[app URL]** → **Stats → AI endpoint** → paste **[proxy URL]/api/ai** → Save → Test connection.

Include this in your final message to the user.

## Non-goals

Do **not**:
- Attempt to install missing CLIs
- Guess or fabricate the `ANTHROPIC_API_KEY`
- Auto-select a Vercel team without user input
- Configure DNS or custom domains — the user does this in the Vercel dashboard after deploy
- Delete `.vercel/` folders inside the sub-projects (they hold the project link)
- Deploy anything from `alternatives/` — that folder is reference-only. The deployable projects are `pydojo-landing/`, `pydojo-app/`, `pydojo-proxy/`.

## Layout

```
CLAUDE.md              this file
README.md              human-readable overview
DEPLOY-VERCEL.md       human walkthrough (backup reference)
.env.example           config template
.env                   your config (git-ignored, you create this)
.deploy-state          auto-populated with deployed URLs (git-ignored)
deploy.sh              orchestrator: runs all scripts in order
scripts/
  lib.sh               shared helpers (loaded by every script)
  00-preflight.sh      verify prereqs + config
  10-github.sh         create + push 3 GitHub repos
  20-vercel-deploy.sh  first deploy of each project
  30-vercel-env.sh     set proxy env vars
  40-vercel-redeploy.sh redeploy proxy after env vars
  50-wire.sh           patch landing URL, redeploy landing
  99-status.sh         print URLs + manual step
pydojo-landing/        landing page source          ← DEPLOYED
pydojo-app/            dojo app source              ← DEPLOYED
pydojo-proxy/          AI proxy source              ← DEPLOYED
alternatives/          non-Vercel proxy options     ← reference only, do NOT deploy
  proxy-cloudflare-worker/
  proxy-express-docker/
```
