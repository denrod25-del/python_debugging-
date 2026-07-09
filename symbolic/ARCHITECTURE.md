# Symbolic — Architecture & Foundations

> **Symbolic is the operating system for creating software companies.**
> One workspace that guides a founder from *idea → research → validation → requirements → design → engineering → testing → launch → iteration.*

This document is the design foundation the master prompt asked for, written **before** implementation and kept in sync with it. It covers product architecture, information architecture, the data model, the design system, navigation, and the AI workflows — then closes with a milestone roadmap.

The first vertical slice of this architecture ships as a working app in [`index.html`](./index.html) (Symbolic Core, Phase 1). It is a single self-contained file so it deploys the same way as the other apps in this monorepo (static, Vercel, `cleanUrls`).

---

## 1. Core philosophy

Every surface answers five questions within five seconds:

1. **What is this?**
2. **Why should I trust it?**
3. **What can I do?**
4. **Why is this better?**
5. **What should I do next?**

The interface *reduces* complexity. Motion explains state, never decorates. The product feels calm, intelligent, trustworthy, premium.

---

## 2. Product architecture

```
                          ┌────────────────────────────────────┐
                          │              Symbolic               │
                          │      AI Product Operating System    │
                          └────────────────────────────────────┘
                                          │
     ┌────────────────┬───────────────────┼───────────────────┬────────────────┐
     ▼                ▼                   ▼                   ▼                ▼
 Workspace        AI Team           Knowledge Graph      Product Memory    Design System
 (projects)   (13 specialists)   (everything connects)   (traceable        (living tokens
     │                │                   │               decisions)        + components)
     │                │                   │
     └──────┬─────────┴─────────┬─────────┘
            ▼                    ▼
     Product Factory        AI Workflows
     (pipeline stages)   PM · UX · Architect · Eng · Auditor
```

**Layers**

| Layer | Responsibility |
|-------|----------------|
| **Shell** | Theme, navigation, command palette, settings, persistence, export. |
| **Workspace** | Project lifecycle — create, list, open, delete, progress. |
| **Project** | The unit of work. Holds every artifact for one product. |
| **AI Workflows** | Specialists that generate artifacts (brief, UX, architecture, plan, audit). |
| **Knowledge Graph** | The relationships between every artifact, visualized. |
| **Product Memory** | Append-only decision log; every recommendation is traceable. |
| **Design System** | Tokens + components consumed by the whole shell. |

**Implementation stance.** The reference implementation is framework-free and client-only (localStorage) so it runs anywhere with zero backend. The *target* production stack is Next.js + React + TypeScript + Tailwind + shadcn/ui + Supabase/Postgres + React Query + Zustand + Framer Motion, with AI via an Edge Function proxy (the same `/api/ai` pattern `pydojo-proxy` already uses in this repo). The client speaks to that proxy; no key ever ships to the browser.

---

## 3. Information architecture

```
Symbolic
├─ Workspace (all projects)
│   └─ Project
│       ├─ Overview        vision · mission · users · competitors
│       ├─ Product Manager  brief · problem · personas · stories · MVP · risks · metrics
│       ├─ UX Designer      journeys · screen hierarchy · states · a11y
│       ├─ Architect        stack · schema · API · auth · deploy · scale · security
│       ├─ Engineering      epics · stories · tasks · milestones · release plan
│       ├─ Quality Auditor  11 category scores + recommendations
│       ├─ Knowledge Graph  interactive node-link map
│       ├─ Product Memory   decision log
│       └─ Roadmap          pipeline stage tracker
├─ AI Team          the 13 specialists and their charters
├─ Design System    tokens + component gallery
└─ Academy          learn-by-doing (roadmap item)
```

Navigation is a **persistent left rail** on desktop that collapses to a bottom tab bar on mobile (mobile-first). A **command palette (⌘K / Ctrl+K)** jumps to any project or section.

---

## 4. Data model

Everything is one JSON document per workspace, versioned and exportable. Shapes (TypeScript-ish):

```ts
type Workspace = {
  version: 1
  settings: { theme: 'light' | 'dark' | 'auto'; aiEndpoint?: string; aiKey?: string }
  projects: Record<ProjectId, Project>
  activeProjectId?: ProjectId
}

type Project = {
  id: string
  name: string
  idea: string                 // the founder's one-liner
  createdAt: number
  stage: Stage                 // pipeline position
  overview: { vision; mission; users; competitors }
  pm:   { interview: QA[]; brief?: Brief }
  ux:   Doc                    // journeys, hierarchy, states, a11y
  arch: Doc                    // stack, schema, api, auth, deploy, scale, security
  eng:  { epics: Epic[]; milestones: Milestone[] }
  audit:{ scores: Record<Category, number>; recs: Rec[]; scoredAt?: number }
  memory: Decision[]           // append-only
  graph: { nodes: Node[]; links: Link[] }
}

type Stage = 'idea'|'research'|'validation'|'requirements'|'design'
           |'engineering'|'testing'|'launch'|'iteration'
type Decision = { id; ts; title; why; who; refs?: string[] }   // traceable memory
type Node = { id; kind: NodeKind; label }
type NodeKind = 'idea'|'goal'|'feature'|'screen'|'component'
              |'data'|'api'|'analytics'|'business'|'revenue'|'feedback'
```

**Product Memory is append-only.** Decisions are never edited in place — a superseding decision references the one it replaces, so the *why* stays traceable over time.

**The Knowledge Graph is derived + curated.** Nodes are generated from artifacts (a feature becomes a `feature` node, a screen a `screen` node) and the founder can add relationships by hand. Canonical edge chain:

```
idea → goal → feature → screen → component → data → api → analytics → business → revenue → feedback → idea
```

The loop closes: feedback feeds new ideas.

---

## 5. Design system

Brand DNA is inherited from B.Symbolic's existing apps and elevated for light **and** dark.

**Tokens**

| Token | Light | Dark |
|-------|-------|------|
| `--bg` | `#FAF7F5` | `#0C0E0D` |
| `--surface` | `#FFFFFF` | `#131817` |
| `--ink` | `#1A1D1B` | `#E8EFE9` |
| `--muted` | `#6B7670` | `#7D8B82` |
| `--line` | `#E7E0DB` | `#222B27` |
| `--oxblood` (brand) | `#8F3437` | `#B0474B` |
| `--accent` (AI green) | `#1B9E5A` | `#69F0A5` |
| `--amber` | `#B7791F` | `#FFCC66` |

**Type** — Display: *Playfair Display*; Serif: *Fraunces*; Sans/UI: *Inter*; Mono: *JetBrains Mono*.
**Spacing** — 4px base scale. **Radius** — 8 / 12 / 16. **Shadow** — one soft elevation token, theme-aware.

**Components** (in the gallery): buttons, cards, inputs, badges, tabs, segmented controls, tables, progress, skeletons, dialogs, notifications, and **AI components** — chat, thinking indicator, confidence meter, reasoning timeline, evidence panel, recommendation cards, risk meter, action panel.

Every component supports light/dark, responsive layout, keyboard access, and reduced-motion.

**Accessibility target: WCAG AA+.** Semantic HTML, focus-visible rings, `aria-*` on interactive controls, `prefers-reduced-motion` respected, contrast checked against the tokens above.

---

## 6. AI workflows

Each specialist takes structured **inputs** and returns structured **outputs** with defined **decision boundaries**. In the reference app, generation runs locally (deterministic synthesis tailored to the idea via domain detection) and *optionally* calls a configured AI endpoint for higher-fidelity output — so the app is fully usable offline and better with a key.

| Specialist | Inputs | Outputs |
|-----------|--------|---------|
| **Product Manager** | idea, interview answers | executive summary, problem statement, target users, user stories, personas, feature list, success metrics, risks, MVP definition |
| **UX Designer** | brief, features | user journeys, navigation, screen hierarchy, empty/error/loading states, a11y notes |
| **Architect** | brief, features, scale needs | stack, DB schema, API structure, auth/authz, storage, deployment, scalability, security |
| **Engineering Planner** | features, architecture | epics, user stories, tasks, dependencies, milestones, release plan |
| **Quality Auditor** | all artifacts | scores across 11 categories + **actionable** recommendations |

**Interview loop.** The PM asks one thoughtful question at a time, adapting follow-ups to answers, until it has enough to generate a brief. Every generated artifact writes a **Product Memory** entry (what was generated, from what inputs, when) so recommendations are traceable.

**The 11 audit categories:** Visual Design · UX · Accessibility · Performance · Security · AI Explainability · Product Strategy · Conversion · Mobile Experience · Engineering · Production Readiness.

---

## 7. The AI Team (13 specialists)

CEO · Product Manager · UX Designer · UI Designer · Software Architect · Frontend Engineer · Backend Engineer · Security Engineer · QA Engineer · Marketing Strategist · Growth Strategist · Documentation Writer · Support Specialist.

Each has a **mission, responsibilities, inputs, outputs, decision boundaries, and collaboration rules** — rendered in the AI Team view so the founder understands *who* is making each recommendation and *where its authority ends*.

---

## 8. Product Factory (pipeline)

```
Idea → Validation → Requirements → Wireframes → Hi-fi UI →
Frontend → Backend → Testing → Security → Accessibility → Launch → Iteration
```

Each stage is reviewable and editable. A project's `stage` field tracks position; the Roadmap view renders it and lets the founder advance or revert.

---

## 9. Implementation roadmap

**Milestone 0 — Foundations (this doc).** Architecture, IA, data model, design system, navigation, AI workflow specs. ✅

**Milestone 1 — Symbolic Core (shipping in `index.html`).**
Workspace + projects, Overview, AI Product Manager (interview → brief), Architect, UX, Engineering Planner, Quality Auditor, Knowledge Graph, Product Memory, AI Team, Design System gallery, command palette, light/dark, localStorage, JSON export, optional AI endpoint. ✅ (v1)

**Milestone 2 — Real streaming AI.** ✅ (shipping in `api/ai.js` + client)
A streaming Edge Function at `/api/ai` forwards to the Anthropic Messages API (key stays server-side). The client streams tokens live: the Product Manager runs a **real, adaptive interview** with Claude (questions typed token-by-token), and the PM / UX / Architect / Engineering specialists stream **structured JSON** that's parsed into the existing rich views. Every AI call falls back to local synthesis on any error, so the app never breaks. Default model `claude-opus-4-8` (override with `SYMBOLIC_MODEL` or in Settings).
*Still ahead:* move storage from localStorage to Supabase/Postgres with auth; multi-user workspaces; surfaced confidence + reasoning.

**Milestone 3 — Product Factory & handoff.** ✅ (shipping in the Factory + Handoff tabs)
The pipeline is now **gated**: each stage has exit criteria derived from the artifacts (interview depth, brief, UX, architecture + plan, audit ≥ 70, exported kit), and you *approve* a gate to advance. The **Handoff** tab packages the accumulated work into a downloadable, dependency-free **`.zip`** — a Next.js scaffold (README, `package.json`, `.env.example`, `db/schema.sql`, domain-aware API + page stubs, feature list), plus **GitHub-ready `issues.json` + `ISSUES.md`** generated from the epics/stories/milestones, and the project JSON. Exporting satisfies the launch gate.
*Still ahead:* one-click GitHub issue/repo sync, artifact diffing, richer AI-generated starter code.

**Milestone 4 — Academy.** ✅ (shipping in the Academy view)
"Every action teaches" — XP, levels, achievements, and a live challenge checklist all track the *real* work you do (start a product, answer interview questions, generate each artifact, run an audit, approve a gate, export a kit). A six-lesson learning path explains the *why* behind the method (start with one wedge · interview first · states are the product · never trust the client · traceable decisions · score what you ship). Achievements reconcile with real progress; XP surfaces as your level in the sidebar.
*Still ahead:* interactive in-context walkthroughs, per-lesson challenges with checks, streaks.

**Milestone 5 — Marketplace.**
Plugins, AI agents, templates, component packs, workflow packs, design systems, prompt libraries, automation recipes.

---

## 10. Non-goals (for v1)

- No persistence backend or auth yet — client-only, localStorage. (Live model calls now work via `/api/ai`; storage is still local.)
- Not a code generator yet — it produces *plans and specs*, not shipping app code (Milestone 3).
