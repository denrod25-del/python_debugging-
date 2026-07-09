# Symbolic — AI Product Operating System

> The operating system that builds software companies.
> Type an idea → Symbolic guides you from **idea → research → validation → requirements → design → engineering → testing → launch → iteration** — in one calm, intelligent workspace.

This folder is **Milestone 1 (Symbolic Core)** of the vision laid out in [`ARCHITECTURE.md`](./ARCHITECTURE.md) — a working, self-contained reference implementation you can open right now.

## Run it

It's a single static file. Open it directly:

```bash
open symbolic/index.html      # macOS
# or just double-click index.html
```

No build, no server, no keys required. State persists in `localStorage`.

## Deploy (matches this monorepo's pattern)

Static, `cleanUrls`, Vercel-ready — the same shape as `pydojo-app`:

```bash
cd symbolic
vercel                # first deploy, creates the project
vercel --prod         # promote
```

## What's inside (v1)

| Area | What it does |
|------|--------------|
| **Workspace** | Every product you're building, with live pipeline progress + quality score. Type an idea to spin up a new project. |
| **AI Product Manager** | Interviews you, then synthesizes an executive summary, problem statement, personas, user stories, feature list, success metrics, risks, and an MVP definition. |
| **AI UX Designer** | User journeys, screen hierarchy, and empty / loading / error / success states with accessibility notes. |
| **AI Software Architect** | Stack, database schema, API structure, auth/authz, storage, deployment, scalability, and security. |
| **AI Engineering Planner** | Epics, stories, story points, and a 12-week milestone plan. |
| **AI Quality Auditor** | Honest scores across 11 categories + **actionable** recommendations. |
| **Knowledge Graph** | Interactive, force-directed map connecting idea → goal → feature → screen → data → API → analytics → revenue → feedback. |
| **Product Memory** | Append-only, traceable decision log — every generated artifact writes an entry. |
| **AI Team** | 13 specialists, each with a mission and decision boundaries. |
| **Design System** | Live token + component gallery (light/dark, WCAG AA). |

Plus: **⌘K command palette**, light / dark / auto theme, JSON export per project, mobile-first responsive layout.

**It works fully offline** — generation runs as deterministic, domain-aware synthesis (it detects inventory / marketplace / social / health / fintech / education / booking / commerce ideas and tailors the output).

## Real streaming AI (optional)

This project ships a streaming Edge Function at **`api/ai.js`** (`/api/ai`) that forwards to the Anthropic Messages API — your key stays server-side. Wire it up:

1. Deploy, then set `ANTHROPIC_API_KEY` in the Vercel project (optionally `SYMBOLIC_MODEL`, default `claude-opus-4-8`).
2. In the app: **Settings (⚙) → AI endpoint → `/api/ai` → Test connection.**

With it on:

- **AI Product Manager** runs a *live, adaptive interview* — Claude's questions stream in token-by-token and adapt to your answers.
- **Product Manager / UX / Architect / Engineering** stream structured JSON that's parsed into the rich views (you watch it generate).

Every AI call **falls back to local synthesis** if the endpoint is missing or a request fails — the app never breaks. Running locally without a server? Leave the endpoint blank and everything still works.

## Domain intelligence

Try these ideas to see how the output adapts:

- `a plumbing inventory app for field technicians` → inventory domain
- `a marketplace for freelance chefs` → two-sided marketplace
- `a habit tracker for therapy patients` → health domain
- `an invoicing tool for small agencies` → fintech domain

## Roadmap

See [`ARCHITECTURE.md` §9](./ARCHITECTURE.md#9-implementation-roadmap). Next up (Milestone 2): real streaming AI via the Edge proxy, Supabase/Postgres persistence, and multi-user workspaces.

— Built by [B.Symbolic](https://bsymbolic.com)
