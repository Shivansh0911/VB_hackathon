# CivicPulse — Autonomous Civic Intelligence Platform

> **AI discovers civic problems before citizens report them.**
> Citizens confirm. Agents escalate to the right authority. Automatically.

**Live Demo:** https://civicradar.netlify.app
**Backend API:** https://vb-hackathon.onrender.com
**API Docs:** https://vb-hackathon.onrender.com/docs
**Telegram Bot:** Search `@civicpulseai_bot` on Telegram

Built for **Vibe2Ship Hackathon — Problem 2: Community Hero (Hyperlocal Problem Solver)**

---

## The Problem

90% of civic issues — potholes, broken streetlights, water leaks — are never reported to authorities. Citizens complain on Twitter and WhatsApp but never fill government forms. Traditional civic apps just digitise the complaint form. Nobody uses them.

## The Inversion

**Every other civic app waits for you to report. CivicPulse already knows.**

An autonomous Discovery Agent scans Twitter, Reddit, and Google News RSS every 6 hours. It finds civic issues using Gemini AI, clusters them geospatially, and surfaces them on a live map. Citizens confirm what the AI found — no form filling, just a photo. Once 5 citizens confirm, the Resolution Agent identifies the exact government department and auto-generates a formal escalation letter.

---

## 3-Agent Autonomous Pipeline

```
┌──────────────────────────────────────────────────────────────────┐
│  AGENT 1 — DISCOVERY                  Runs every 6h (scheduled)  │
│                                                                   │
│  Sources: Twitter + Reddit + Google News RSS (parallel fetch)     │
│       ↓                                                           │
│  Gemini 2.5 Flash — batch classifies all signals into issues      │
│       ↓                                                           │
│  Haversine geospatial clustering (0.3km radius)                   │
│       ↓                                                           │
│  Neighbourhood geocoding — 60+ named areas mapped to real coords  │
│       ↓                                                           │
│  Deduplication against existing DB → new issues stored            │
│       ↓                                                           │
│  Issues appear on map as DISCOVERED                               │
└──────────────────────────────────────────────────────────────────┘
          ↓
┌──────────────────────────────────────────────────────────────────┐
│  AGENT 2 — CONFIRMATION          Triggered per citizen action     │
│                                                                   │
│  Via Web: citizen clicks issue → uploads photo                    │
│  Via Telegram: citizen sends /confirm <id> → sends photo          │
│       ↓                                                           │
│  Gemini 2.5 Flash (multimodal) validates photo matches issue      │
│       ↓                                                           │
│  Confidence score rises per confirmation                          │
│       ↓                                                           │
│  At 5 confirmations → status moves to CONFIRMED                   │
└──────────────────────────────────────────────────────────────────┘
          ↓
┌──────────────────────────────────────────────────────────────────┐
│  AGENT 3 — RESOLUTION            Triggered on CONFIRMED status    │
│                                                                   │
│  Authority lookup table → BBMP / BMC / GHMC / BESCOM / BWSSB     │
│  (department-level routing — BBMP Roads ≠ BBMP SWM ≠ BESCOM)     │
│       ↓                                                           │
│  Gemini 2.5 Flash drafts formal 250-word escalation letter        │
│       ↓                                                           │
│  Letter stored + shown in UI + logged for dispatch                │
│       ↓                                                           │
│  Issue moves to ESCALATED                                         │
└──────────────────────────────────────────────────────────────────┘
```

**Issue stages:** `DISCOVERED → CONFIRMED → ESCALATED → RESOLVED`

---

## Two Citizen Channels

### Web App — https://civicradar.netlify.app
- Live map with colour-coded issue pins (CartoDB Dark Matter tiles, free)
- Filter by status: All / Discovered / Confirmed / Escalated / Resolved
- Click any issue → see description, source signal, confidence bar
- Upload a photo to confirm → Gemini validates it live
- Impact dashboard showing pipeline stats
- "Run Discovery" button to manually trigger Agent 1
- Instant load — fallback issues shown at 0ms, live data loads in background

### Telegram Bot — @civicpulseai_bot
- `/start` — welcome and instructions
- `/issues` — lists top 8 active issues with status and confirmations needed
- `/confirm <id>` — starts photo confirmation flow for a specific issue
- Send a photo → Gemini Vision validates it → bot replies with confidence score and reasoning
- `/skip` — confirm without a photo
- Auto-notifies when 5-confirmation threshold is reached and escalation fires

**Citizens can participate without ever opening a browser.**

---

## Google AI Studio Usage

| Task | Model | Where |
|------|-------|-------|
| Classify signals into civic issues | Gemini 2.5 Flash | Discovery Agent (every 6h) |
| Validate citizen photos (web) | Gemini 2.5 Flash multimodal | Confirmation Agent |
| Validate citizen photos (Telegram) | Gemini 2.5 Flash multimodal | Telegram Bot |
| Draft formal escalation letter | Gemini 2.5 Flash | Resolution Agent |

All AI calls use the Gemini API via Google AI Studio. API key sourced from [aistudio.google.com](https://aistudio.google.com).

Additional Google source: **Google News RSS** — free real-time Indian civic news feed used as primary data source (no API key required).

---

## Data Sources

| Source | Status | Notes |
|--------|--------|-------|
| **Google News RSS** | Live, no auth | Primary real source — BBMP potholes, BMC waterlogging, GHMC drainage |
| **Twitter / X** | Mock fallback | Search API costs $100/month — city-specific realistic mock used |
| **Reddit** | Optional | r/bangalore, r/mumbai, r/hyderabad — add credentials to activate |
| **Google Maps Reviews** | Disabled | Places API is paid — excluded to keep project $0/month |

---

## Key Features

- **Inverted civic model** — AI proactively finds issues; citizens don't need to initiate
- **3 fully autonomous agents** running on APScheduler (discovery 6h, escalation 30min)
- **Dual channel** — web app + Telegram bot, both with live Gemini photo validation
- **Neighbourhood-level geocoding** — 60+ named areas (Indiranagar, Bandra, Gachibowli etc.) mapped to real coordinates
- **Department-level authority routing** — BBMP Roads ≠ BBMP SWM ≠ BESCOM ≠ BWSSB
- **Haversine geospatial clustering** — merges nearby same-category signals (0.3km radius)
- **Instant load** — fallback issues shown at 0ms, live data loads silently in background
- **Auto-refresh** — frontend silently refreshes at 35s to pick up new discovered issues
- **Uptime monitoring** — UptimeRobot pings every 5min, Render never cold-starts
- **$0/month total cost** — no paid APIs, all free tier

---

## Known Limitations & Why

### Twitter Search API — Paid Wall
Twitter's recent search API requires $100/month (Basic plan) as of 2023. CivicPulse has the full API integration — realistic city-specific mock tweets are used as fallback. The full Discovery pipeline (Gemini classification, clustering, geocoding) runs correctly on these + real Google News RSS.

### Email Dispatch — Intentionally Not Sent
SMTP email is fully coded. Not configured because sending AI-generated letters to real government officials based on hackathon demo data is inappropriate. In production: add Gmail SMTP credentials → letters reach real inboxes. The letter, authority, and escalation flow are all visible in the UI.

### DB Resets on Render Restart
Render free tier has no persistent disk. Mitigated by: instant seed data on startup + UptimeRobot keeping server warm. Data re-populates within seconds of any restart.

---

## Cities & Authorities

| City | Authorities Mapped |
|------|--------------------|
| **Bengaluru** | BBMP (Roads, SWM, Storm Water Drain, Horticulture), BESCOM, BWSSB |
| **Mumbai** | BMC (Roads, Hydraulic Engineering, SWM, Storm Water Drain), MSEDCL |
| **Hyderabad** | GHMC (Engineering, Sanitation), TSSPDCL, HMWSSB |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, Python 3.11, APScheduler, SQLite |
| AI | **Google AI Studio — Gemini 2.5 Flash** (classification, vision, letter drafting) |
| Telegram | python-telegram-bot 20.7 (async, runs inside FastAPI lifespan) |
| Frontend | React 18, Vite 5, Tailwind CSS 3, Leaflet.js |
| Map tiles | CartoDB Dark Matter (free, no API key) |
| Geospatial | Custom Haversine clustering (pure Python) |
| Data source | Google News RSS (live Indian civic news) |
| Hosting | Render (backend) + Netlify (frontend) |
| Uptime | UptimeRobot (free, 5-min ping) |
| **Total cost** | **$0/month** |

---

## Project Structure

```
civicpulse/
├── backend/
│   ├── main.py                    # FastAPI app, lifespan, Telegram bot startup
│   ├── database.py                # SQLite — parameterised queries throughout
│   ├── scheduler.py               # APScheduler — discovery 6h, escalation 30min
│   ├── seed_data.py               # Fallback data (only if Gemini quota exhausted)
│   ├── agents/
│   │   ├── discovery_agent.py     # Agent 1 — parallel fetch + Gemini + cluster
│   │   ├── confirmation_agent.py  # Agent 2 — Gemini Vision photo validation
│   │   └── resolution_agent.py    # Agent 3 — authority lookup + letter + email
│   └── services/
│       ├── gemini_service.py      # Gemini 2.5 Flash — all AI tasks + retry on 429
│       ├── telegram_bot.py        # Telegram bot — /issues, /confirm, photo handler
│       ├── geocoding_service.py   # 60+ neighbourhood coordinates
│       ├── clustering_service.py  # Haversine geospatial clustering
│       ├── authority_service.py   # BBMP/BMC/GHMC department-level lookup
│       ├── news_rss_service.py    # Google News RSS — live, no auth
│       ├── twitter_service.py     # Twitter v2 + city mock fallback
│       └── email_service.py       # SMTP dispatch (graceful skip if unconfigured)
└── frontend/
    └── src/
        ├── App.jsx                # Layout, filters, admin controls
        ├── components/
        │   ├── MapView.jsx        # Leaflet map, circle markers, fly-to, popup
        │   ├── IssueCard.jsx      # Confidence bar, expand, confirm button
        │   ├── ConfirmModal.jsx   # Photo upload + Gemini validation result
        │   ├── ImpactDashboard.jsx# Stats + pipeline visual
        │   └── EscalationLog.jsx  # Generated letter + authority shown
        └── hooks/
            └── useIssues.js       # Instant fallback + silent background load
```

---

## Local Development

```bash
# Backend
cd civicpulse
cp .env.example .env        # add GEMINI_API_KEY
pip install -r requirements.txt
cd backend && uvicorn main:app --reload
# API: http://localhost:8000
# Docs: http://localhost:8000/docs

# Frontend
cd civicpulse/frontend
npm install && npm run dev
# App: http://localhost:5173
```

---

## Future Improvements

| Feature | What it adds |
|---------|-------------|
| Live SMTP email | Letters actually reach government inboxes — code built, needs credentials |
| Twitter paid plan | Real tweet search ($100/month) — architecture fully ready |
| Reddit credentials | r/bangalore, r/mumbai, r/hyderabad signal — free OAuth2 |
| Telegram notifications | Notify citizen when their confirmed issue gets escalated |
| More cities | Delhi (MCD), Chennai (GCC), Pune (PMC) — lookup table extensible |
| PostgreSQL | Replace SQLite for concurrent writes at scale |
| Gamification | Points for confirmations, leaderboard per city |
